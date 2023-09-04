from aiogram.contrib.middlewares.i18n import I18nMiddleware

i18n = I18nMiddleware('messages', path='bot_app/data/locales', default='en')
