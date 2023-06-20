## Управление сервисами с использованием Docker Compose

### 1. Запуск всех сервисов

```bash
docker-compose up -d
```

Эта команда запустит все сервисы, описанные в файле docker-compose.yml, в фоновом режиме (флаг -d).

### 2. Остановка всех сервисов

```bash
docker-compose down
```

Эта команда остановит все сервисы и удалит контейнеры, сети и тома, определенные в docker-compose.yml.

### 3. Пересборка всех сервисов

```bash
docker-compose build
```

Эта команда пересоберет все образы для сервисов, указанных в файле docker-compose.yml.

### 4. Пересборка конкретного сервиса

```bash
docker-compose build <service_name>
```

Например, чтобы пересобрать сервис bot_app, выполните:

```bash
docker-compose build bot_app
```

### 5. Запуск конкретного сервиса

```bash
docker-compose up -d <service_name>
```

Например, чтобы запустить сервис bot_app, выполните:

```bash
docker-compose up -d bot_app
```

### 6. Остановка конкретного сервиса

```bash
docker-compose down <service_name>
```

Например, чтобы остановить сервис bot_app, выполните:

```bash
docker-compose down bot_app
```

### 7. Просмотр логов конкретного сервиса

```bash
docker-compose logs -f <service_name>
```

Например, чтобы просмотреть логи сервиса bot_app, выполните:

```bash
docker-compose logs -f bot_app
```

### 8. Выполнение команд внутри контейнера конкретного сервиса

```bash
docker-compose exec <service_name> <command>
```

Например, чтобы выполнить команду ls внутри контейнера сервиса bot_app, выполните:

```bash
docker-compose exec bot_app ls
```