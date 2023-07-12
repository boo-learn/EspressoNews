# Покрытие тестами

Чтобы получить покрытие тестами любого модуля
В терминале переходим в папку с модулем, например `$ cd digest_service/`
Запускаем: `$ pytest --cov=.`
Строим html отчет: `$ coverage html -i`
Смотрим получившуюся html'ку: `$ Wrote HTML report to htmlcov/index.html`


