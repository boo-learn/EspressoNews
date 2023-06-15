# Работа с переменными окружения

Все переменные окружения храним в .env файлах.

# Структура .env

* .env.local - Переменные для локальной разработки(вне docker контейнера)
* .env.test - Переменные для тестирования(
* .env.dev - Переменные для разработки(запуск в docker'ах)
* .env.prod - Переменные для продакшн сервера(на будущее)

# Шаблоны .env

Для каждого env файла храним шаблон c примером, пример формата имени: .env.local.example

# Автоматическая подгрузка из .env

`set -a && source <env_name> && set +a`

example: `set -a && source .env.local && set +a`

# Автоматическая подгрузка из .env

В `.bashrc` добавляем код:
```bash
# Auto load from .env
# Auto load from .env
load_env() {
  env_file=".env.$1"
  if [ -f "$env_file" ]; then
  # export $(cat "$env_file" | xargs)
      set -a
      source $env_file
      set +a
      echo "Автоматическая подгрузка переменных окружения из $env_file"
  fi
}
 
load_auto_env() {
  if [ -f .env.local ]; then
      load_env local;
  elif [ -f .env.test ]; then
      load_env test;
  elif [ -f .env.dev ]; then
      load_env dev;
  elif [ -f .env.prod ]; then
      load_env prod;
  fi
}
init_load () {
  if [[ "$LOAD_AUTO_ENV" == "$(pwd)" ]]; then
    # echo config from this directory already loaded, skipping
    return 0
  else
    # echo loading config from $(pwd)
    export LOAD_AUTO_ENV="$(pwd)"
    load_auto_env
  fi
}
 
export PROMPT_COMMAND="init_load; $PROMPT_COMMAND"
```

Примените изменения: `source .bashrc`

При заходе в директорию с .env файлами, их содержимое будет автоматически подгружаться