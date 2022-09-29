# Netflix UGC
Сервис для работы с пользовательским контентом в онлайн-кинотеатре _Netflix_.

## Сервисы
- Netflix Admin:
  - Панель администратора для управления онлайн-кинотеатром (редактирование фильмов, жанров, актеров)
  - https://github.com/ReznikovRoman/netflix-admin
- Netflix ETL:
  - ETL пайплайн для синхронизации данных между БД сервиса Netflix Admin и Elasticsearch
  - https://github.com/ReznikovRoman/netflix-etl
- Netflix Movies API:
  - АПИ фильмов
  - https://github.com/ReznikovRoman/netflix-movies-api
    - Python клиент: https://github.com/ReznikovRoman/netflix-movies-client
- Netflix Auth API:
  - Сервис авторизации - управление пользователями и ролями
  - https://github.com/ReznikovRoman/netflix-auth-api
- Netflix UGC:
  - Сервис для работы с пользовательским контентом
  - https://github.com/ReznikovRoman/netflix-ugc
- Netflix Notifications:
  - Сервис для отправки уведомлений
  - https://github.com/ReznikovRoman/netflix-notifications
- Netflix Voice Assistant:
  - Голосовой ассистент Netflix
  - https://github.com/ReznikovRoman/netflix-voice-assistant

## Настройка и запуск
docker-compose содержат контейнеры:
 1. server
 2. redis
 3. traefik
 4. zookeeper-kafka
 5. zookeeper-clickhouse
 6. kafka
 7. init-kafka (создание топиков при запуске сервиса)
 8. clickhouse-server-0[1-4]

\* Нужно для полноценного веб-интерфейса Kafka

 9. schema-registry
 10. connect
 11. control-center
 12. ksqldb-server
 13. ksqldb-cli
 14. ksql-datagen
 15. rest-proxy

Файлы docker-compose:
 1. `docker-compose.yml` - для локальной разработки; используются стабы для работы с in-memory очередью.
 3. `docker-compose-dev.yml` - полный набор всех необходимых контейнеров (Kafka, ClickHouse cluster, Kafka UI).
 4. `tests/functional/docker-compose.yml` - для функциональных тестов.

Для запуска контейнеров нужно создать файл `.env` в корне проекта.

**Пример `.env`:**

```dotenv
ENV=.env

# Python
PYTHONUNBUFFERED=1

# Netflix UGC
# Project
NUGC_DEBUG=1
NUGC_PROJECT_BASE_URL=http://api-ugc.localhost:8010
NUGC_SERVER_PORT=8003
NUGC_PROJECT_NAME=netflix-ugc
NUGC_API_V1_STR=/api/v1
NUGC_SERVER_HOSTS=http://api-ugc.localhost:8010
# Auth
NAA_SECRET_KEY=changeme
# Redis
NUGC_REDIS_HOST=redis
NUGC_REDIS_PORT=6379
NUGC_REDIS_MAIN_DB=0
NUGC_REDIS_OM_URL=redis://@redis:6379
NUGC_REDIS_DEFAULT_CHARSET=utf-8
NUGC_REDIS_DECODE_RESPONSES=1
NUGC_REDIS_RETRY_ON_TIMEOUT=1
# MongoDB
NUGC_MONGODB_USER=yandex
NUGC_MONGODB_PASSWORD=netflix
NUGC_MONGODB_NAME=netflix_ugc
NUGC_MONGODB_HOST=mongodb
NUGC_MONGODB_PORT=27017
NUGC_MONGOEXPRESS_LOGIN=admin
NUGC_MONGOEXPRESS_PASSWORD=pass
# Queue
NUGC_QUEUE_PROGRESS_NAME=progress-topic
NUGC_QUEUE_PROGRESS_GROUP=progress-group
NUGC_QUEUE_PROGRESS_CONSUMERS=2
NUGC_QUEUE_BOOKMARKS_NAME=bookmarks-topic
NUGC_QUEUE_BOOKMARKS_GROUP=bookmarks-group
NUGC_QUEUE_BOOKMARKS_CONSUMERS=2
NUGC_QUEUE_FILM_RATING_NAME=film-rating-topic
NUGC_QUEUE_FILM_RATING_GROUP=film-rating-group
NUGC_FILM_RATING_CONSUMERS=2
# Kafka
NUGC_KAFKA_URL=kafka:9092
# ELK
NUGC_LOGSTASH_HOST=logstash
NUGC_LOGSTASH_PORT=5044
NUGC_LOGSTASH_LOGGER_VERSION=1
# Config
NUGC_USE_STUBS=0
NUGC_TESTING=0
NUGC_CI=0
```

### Запуск проекта:

Локально:
```shell
docker-compose build
docker-compose up
```

## Разработка
Синхронизировать окружение с `requirements.txt` / `requirements.dev.txt` (установит отсутствующие пакеты, удалит лишние, обновит несоответствующие версии):
```shell
make sync-requirements
```

Сгенерировать requirements.\*.txt files (нужно пере-генерировать после изменений в файлах requirements.\*.in):
```shell
make compile-requirements
```

Используем `requirements.local.in` для пакетов, которые нужно только разработчику. Обязательно нужно указывать _constraints files_ (-c ...)

Пример:
```shell
# requirements.local.txt

-c requirements.txt

ipython
```

### Тесты
Запуск тестов (всех, кроме функциональных) с экспортом переменных окружения из `.env` файла:
```shell
export $(echo $(cat .env | sed 's/#.*//g'| xargs) | envsubst) && make test
```

Для функциональных тестов нужно создать файл `.env` в папке ./tests/functional

**Пример `.env` (для корректной работы тестов надо подставить корректные значения для NAA):**
```dotenv
# Tests
ENV=.env

# Python
PYTHONUNBUFFERED=1

# Netflix UGC
# Project
NUGC_DEBUG=1
NUGC_PROJECT_BASE_URL=http://api-ugc.localhost:8010
NUGC_SERVER_PORT=8003
NUGC_PROJECT_NAME=netflix-ugc
NUGC_API_V1_STR=/api/v1
NUGC_SERVER_HOSTS=http://api-ugc.localhost:8010
# Auth
NAA_SECRET_KEY=changeme
# Redis
NUGC_REDIS_HOST=redis
NUGC_REDIS_PORT=6379
NUGC_REDIS_MAIN_DB=0
NUGC_REDIS_OM_URL=redis://@redis:6379
NUGC_REDIS_DEFAULT_CHARSET=utf-8
NUGC_REDIS_DECODE_RESPONSES=1
NUGC_REDIS_RETRY_ON_TIMEOUT=1
# MongoDB
NUGC_MONGODB_USER=yandex
NUGC_MONGODB_PASSWORD=netflix
NUGC_MONGODB_NAME=netflix_ugc
NUGC_MONGODB_HOST=mongodb
NUGC_MONGODB_PORT=27017
NUGC_MONGOEXPRESS_LOGIN=admin
NUGC_MONGOEXPRESS_PASSWORD=pass
# Queue
NUGC_QUEUE_PROGRESS_NAME=progress-topic
NUGC_QUEUE_PROGRESS_GROUP=progress-group
NUGC_QUEUE_PROGRESS_CONSUMERS=2
NUGC_QUEUE_BOOKMARKS_NAME=bookmarks-topic
NUGC_QUEUE_BOOKMARKS_GROUP=bookmarks-group
NUGC_QUEUE_BOOKMARKS_CONSUMERS=2
NUGC_QUEUE_FILM_RATING_NAME=film-rating-topic
NUGC_QUEUE_FILM_RATING_GROUP=film-rating-group
NUGC_FILM_RATING_CONSUMERS=2
# Kafka
NUGC_KAFKA_URL=kafka:9092
# Config
NUGC_USE_STUBS=1
NUGC_TESTING=1
NUGC_CI=0
# Tests
TEST_CLIENT_BASE_URL=http://traefik:80
TEST_SERVER_BASE_URL=http://server:8003
TEST_NETFLIX_AUTH_BASE_URL=http://traefik:81

# Netflix Auth API
FLASK_APP=auth.main
FLASK_DEBUG=1
FLASK_ENV=development
# Project
NAA_SQLALCHEMY_ECHO=0
NAA_PROJECT_BASE_URL=http://api-auth.localhost:8009
NAA_API_V1_STR=/api/v1
NAA_SERVER_HOSTS=http://api-auth.localhost:8009
NAA_SERVER_PORT=8002
NAA_PROJECT_NAME=netflix-auth
NAA_THROTTLE_KEY_PREFIX=limiter:
NAA_THROTTLE_USER_REGISTRATION_LIMITS=3/minute
NAA_THROTTLE_ENABLE_LIMITER=0
NAA_DEBUG=1
# Clients
NAA_CLIENT_USE_STUBS=1
# Tracing
NAA_OTEL_ENABLE_TRACING=0
# auth0
NAA_AUTH0_DOMAIN=dummy.com
NAA_AUTH0_API_AUDIENCE=https://dummy.com
NAA_AUTH0_ISSUER=https://dummy.com/
NAA_AUTH0_CLIENT_ID=secret
NAA_AUTH0_CLIENT_SECRET=secret
NAA_AUTH0_AUTHORIZATION_URL=https://dummy.com/oauth/token
# Social
NAA_SOCIAL_GOOGLE_CLIENT_ID=secret
NAA_SOCIAL_GOOGLE_CLIENT_SECRET=secret
NAA_SOCIAL_GOOGLE_METADATA_URL=https://accounts.google.com/.well-known/openid-configuration
NAA_SOCIAL_YANDEX_CLIENT_ID=secret
NAA_SOCIAL_YANDEX_CLIENT_SECRET=secret
NAA_SOCIAL_YANDEX_ACCESS_TOKEN_URL=https://oauth.yandex.ru/token
NAA_SOCIAL_YANDEX_USERINFO_ENDPOINT=https://login.yandex.ru/info
NAA_SOCIAL_YANDEX_AUTHORIZE_URL=https://oauth.yandex.ru/authorize
NAA_SOCIAL_USE_STUBS=1
# Postgres
NAA_DB_HOST=db-auth
NAA_DB_PORT=5432
NAA_DB_NAME=netflix_auth
NAA_DB_USER=test
NAA_DB_PASSWORD=yandex
NAA_DB_DEFAULT_SCHEMA=public
# Redis
NAA_REDIS_HOST=redis-auth
NAA_REDIS_PORT=6379
NAA_REDIS_THROTTLE_STORAGE_DB=2
NAA_REDIS_DEFAULT_CHARSET=utf-8
NAA_REDIS_DECODE_RESPONSES=1
NAA_REDIS_RETRY_ON_TIMEOUT=1
```

Запуск функциональных тестов:
```shell
cd ./tests/functional && docker-compose up test
```

Или через рецепт Makefile:
```shell
make dtf
```

### Code style:
Перед коммитом проверяем, что код соответствует всем требованиям:

```shell
make lint
```

### pre-commit:
Для настройки pre-commit:
```shell
pre-commit install
```

## Redis
Redis используется в качестве основной БД (Redis Stack on Redis Enterprise).
Веб-интерфейс RedisInsight доступен по адресу:
- `localhost:13333`

## Kafka
В качестве брокера сообщений используется Kafka.
Веб-интерфейс доступен по адресу (может настраиваться до 5-10 минут):
- `${PROJECT_BASE_URL}:9021/`

## Документация
Документация в формате OpenAPI 3 доступна по адресам:
- `${PROJECT_BASE_URL}/api/v1/docs` - Swagger
