# EspressoNews

# Docker

### Запуск контейнеров
`docker compose up -d`

### Подключиться к контейнеру терминалом
`docker run -it <image id> bash`
С подключение переменных окружения:
`docker run --env-file .env -it [image id] bash`

### Подключение к запущенному контейнеру
`docker exec -it <image id/name> bash`

### Пересобрать контейнер
`docker-compose up -d --no-deps --build [service_name]`

### Удаление контейнеров

To delete all containers including its volumes use:
`docker rm -vf $(docker ps -aq)`

To delete all the images:
`docker rmi -f $(docker images -aq)`

# Alembic(migrations)

### Генерация миграций из моделей
`alembic revision --autogenerate -m "init"`

### Применение миграции