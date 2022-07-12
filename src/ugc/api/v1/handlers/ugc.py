from __future__ import annotations

from http import HTTPStatus
from typing import TYPE_CHECKING
from uuid import UUID

from aiohttp_apispec import docs, request_schema
from dependency_injector.wiring import Provide, inject

from aiohttp import web

from ugc.api.security import get_user_id_from_jwt
from ugc.api.utils import orjson_response
from ugc.api.v1 import openapi
from ugc.api.v1.serializers import FilmProgressCreate, FilmRatingCreate
from ugc.containers import Container
from ugc.domain.ratings.exceptions import NoFilmRatingError

if TYPE_CHECKING:
    from ugc.domain.bookmarks import BookmarkDispatcherService, BookmarkService
    from ugc.domain.progress import ProgressDispatcherService, ProgressService
    from ugc.domain.ratings import FilmRatingDispatcherService, FilmRatingService


@docs(**openapi.add_film_bookmark)
@inject
async def add_film_bookmark(
    request: web.Request, *,
    bookmark_dispatcher: BookmarkDispatcherService = Provide[Container.bookmark_dispatcher_service],
) -> web.Response:
    """Добавление фильма с `film_id` в закладки авторизованному пользователю."""
    await _handle_film_bookmark(request, bookmark_dispatcher, bookmarked=True)
    return orjson_response(status=HTTPStatus.ACCEPTED)


@docs(**openapi.delete_film_bookmark)
@inject
async def delete_film_bookmark(
    request: web.Request, *,
    bookmark_dispatcher: BookmarkDispatcherService = Provide[Container.bookmark_dispatcher_service],
) -> web.Response:
    """Удаление фильма с `film_id` из закладок авторизованного пользователя."""
    await _handle_film_bookmark(request, bookmark_dispatcher, bookmarked=False)
    return orjson_response(status=HTTPStatus.ACCEPTED)


@docs(**openapi.get_user_films_bookmarks)
@inject
async def get_user_films_bookmarks(
    request: web.Request, *,
    bookmark_service: BookmarkService = Provide[Container.bookmark_service],
) -> web.Response:
    """Получение списка фильмов в закладках авторизованного пользователя."""
    user_id = get_user_id_from_jwt(request.headers)
    bookmarks = await bookmark_service.get_user_bookmarks(user_id)
    return orjson_response(bookmarks, status=HTTPStatus.OK)


@docs(**openapi.track_film_progress)
@request_schema(FilmProgressCreate)
@inject
async def track_film_progress(
    request: web.Request, *,
    progress_dispatcher: ProgressDispatcherService = Provide[Container.progress_dispatcher_service],
) -> web.Response:
    """Сохранение прогресса фильма с `film_id` для авторизованного пользователя."""
    film_id: UUID = request.match_info["film_id"]
    user_id = get_user_id_from_jwt(request.headers)
    validated_data = request["data"]
    viewed_frame = validated_data["viewed_frame"]
    await progress_dispatcher.dispatch_progress_tracking(user_id=user_id, film_id=film_id, viewed_frame=viewed_frame)
    return orjson_response(status=HTTPStatus.ACCEPTED)


@docs(**openapi.get_film_progress)
@inject
async def get_film_progress(
    request: web.Request, *,
    progress_service: ProgressService = Provide[Container.progress_service],
) -> web.Response:
    """Получение прогресса фильма с `film_id` для авторизованного пользователя."""
    film_id: UUID = request.match_info["film_id"]
    user_id = get_user_id_from_jwt(request.headers)
    progress = await progress_service.get_user_film_progress(user_id=user_id, film_id=film_id)
    return orjson_response(progress, status=HTTPStatus.OK)


@docs(**openapi.get_film_rating)
@inject
async def get_film_rating(
    request: web.Request, *,
    film_rating_service: FilmRatingService = Provide[Container.film_rating_service],
) -> web.Response:
    """Получение рейтинга фильма."""
    film_id: UUID = request.match_info["film_id"]
    try:
        film_rating = await film_rating_service.get_film_rating(film_id)
    except NoFilmRatingError:
        return orjson_response(status=HTTPStatus.NO_CONTENT)
    return orjson_response(film_rating, status=HTTPStatus.OK)


@docs(**openapi.add_film_rating)
@request_schema(FilmRatingCreate)
@inject
async def add_film_rating(
    request: web.Request, *,
    film_rating_dispatcher: FilmRatingDispatcherService = Provide[Container.film_rating_dispatcher_service],
) -> web.Response:
    """Добавление пользовательского рейтинга фильму."""
    film_id: UUID = request.match_info["film_id"]
    validated_data = request["data"]
    rating = validated_data["rating"]
    user_id = get_user_id_from_jwt(request.headers)
    film_rating = await film_rating_dispatcher.dispatch_film_rating(film_id=film_id, user_id=user_id, rating=rating)
    return orjson_response(film_rating, status=HTTPStatus.ACCEPTED)


async def _handle_film_bookmark(
    request: web.Request,
    bookmark_dispatcher: BookmarkDispatcherService, *,
    bookmarked: bool,
) -> None:
    film_id: UUID = request.match_info["film_id"]
    user_id = get_user_id_from_jwt(request.headers)
    await bookmark_dispatcher.dispatch_bookmark_switch(user_id=user_id, film_id=film_id, bookmarked=bookmarked)
