import functools
from operator import and_
from typing import Any, Generic, Type, TypeVar

from aredis_om.model.model import NotFoundError, RedisModel
from bson import ObjectId
from pymongo import ASCENDING

from ugc.domain.factories import BaseModelFactory
from ugc.domain.types import BaseModel
from ugc.helpers import resolve_callables

from .clients import MongoCollectionClient, MongoDatabaseClient
from .types import PaginationCursor

_RM = TypeVar("_RM", bound=RedisModel)
_BM = TypeVar("_BM", bound=BaseModel)

MongoResult = dict[str, Any]


class RedisRepository(Generic[_RM]):
    """Репозиторий для работы с данными модели `RedisModel`."""

    def __init__(self, model: Type[_RM]) -> None:
        self.model = model

    # TODO: С релизом Python 3.11 добавится возможность делать generic named tuple
    # PR: https://github.com/python/cpython/pull/92027
    async def get_or_create(self, defaults: dict | None = None, **kwargs) -> tuple[_RM, bool]:
        """Получение объекта по `expressions`, создание нового при необходимости.

        Args:
            defaults: словарь с парами ключ-значение, который будет использоваться при создании объекта.
            **kwargs: поля для поиска.

        Returns:
            Кортеж с объектом и булевой переменной, показывающей был ли создан новый объект.
        """
        query = self._get_equal_query(**kwargs)
        try:
            obj = await self.model.find(query).first()
            return obj, False
        except NotFoundError:
            params = dict(resolve_callables(self._extract_model_params(defaults, **kwargs)))
            obj = self.model(**params)
            await obj.save()
            return obj, True

    async def update_or_create(self, defaults: dict | None = None, **kwargs) -> tuple[_RM, bool]:
        """Поиск объекта по заданным `kwargs` и обновление полей в соответствии с `defaults`.

        Если объект не был найден по `kwargs`, то будет создан новый.

        Args:
            defaults: словарь с парами ключ-значение, который будет использоваться при обновлении объекта.
            **kwargs: поля для поиска.

        Returns:
            Кортеж с объектом и булевой переменной, показывающей был ли создан новый объект.
        """
        defaults = defaults or {}
        obj, created = await self.get_or_create(defaults, **kwargs)
        if created:
            return obj, created
        for key, value in resolve_callables(defaults):
            setattr(obj, key, value)
        await obj.save()
        return obj, False

    def _get_equal_query(self, **kwargs) -> bool:
        expressions = (
            getattr(self.model, field) == value
            for field, value in kwargs.items()
        )
        query = functools.reduce(and_, expressions)
        return query

    @staticmethod
    def _extract_model_params(defaults: dict | None, **kwargs) -> dict:
        defaults = defaults or {}
        params = {key: value for key, value in kwargs.items()}
        params.update(defaults)
        return params


class MongoRepository(Generic[_BM]):
    """Репозиторий для работы с данными из MongoDB."""

    def __init__(self, db: MongoDatabaseClient, factory: BaseModelFactory, collection_name: str) -> None:
        assert isinstance(db, MongoDatabaseClient)
        self._db = db

        assert isinstance(factory, BaseModelFactory)
        self._factory = factory

        assert isinstance(collection_name, str)
        self._collection_name = collection_name

    @property
    def collection(self) -> MongoCollectionClient:
        return self._db[self._collection_name]

    def get_paginated_results_iter(
        self, *,
        limit: int,
        cursor: PaginationCursor = None,
        ordering: tuple[str, int] | None = None, filter_query: dict | None = None, pagination_query: dict | None = None,
    ):
        """Получение итератора по результатам с пагинацией."""
        if ordering is None:
            ordering = ("_id", ASCENDING)
        if pagination_query is None:
            pagination_query = {"_id": {"$gt": ObjectId(cursor)}}

        if cursor is None:
            return self.collection.find(filter_query).limit(limit).sort(*ordering)
        filter_query.update(pagination_query)
        return self.collection.find(filter_query).limit(limit).sort(*ordering)

    async def get_paginated_results(
        self, *,
        limit: int,
        cursor: PaginationCursor = None, cursor_field: str,
        ordering: tuple[str, int] | None = None, filter_query: dict | None = None, pagination_query: dict | None = None,
    ) -> tuple[list[_BM], PaginationCursor]:
        """Получение списка документов с использованием `cursor-based` пагинации."""
        raw_results = self.get_paginated_results_iter(
            limit=limit, cursor=cursor, ordering=ordering, filter_query=filter_query, pagination_query=pagination_query)
        results = [
            self._factory.create_from_serialized(self.fix_id_field(raw_result))
            async for raw_result in raw_results
        ]

        if not results:
            return [], None

        new_cursor = getattr(results[-1], cursor_field)
        return results, new_cursor

    @staticmethod
    def fix_id_field(data: MongoResult) -> MongoResult:
        """Переименование поля `_id`."""
        data["id"] = str(data.pop("_id"))
        return data
