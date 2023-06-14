# EspressoNews

# Docker

### Запуск контейнеров
`docker compose up -d`

### Подключиться к контейнеру терминалом
`docker run -it --entrypoint bash <image id/name>`

### Подключение к запущенному контейнеру
`docker exec -it <image id/name> bash`

### Удаление контейнеров

To delete all containers including its volumes use:
`docker rm -vf $(docker ps -aq)`

To delete all the images:
`docker rmi -f $(docker images -aq)`

# Alembic(migrations)

### Генерация миграций из моделей
`alembic revision --autogenerate -m "init"`