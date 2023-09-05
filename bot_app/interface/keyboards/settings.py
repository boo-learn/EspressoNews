from bot_app.core.keyboards.creators import KeyboardType
from bot_app.core.tools.keyboards_tools import KeyboardsTools


class SettingsKeyboards(KeyboardsTools):
    def __init__(self):
        super().__init__()
        self.init_keyboards()

    def init_keyboards(self):
        self.register('settings', KeyboardType.REPLY, [
            [('Язык',), ('Интонация',)],
            [('Периодичность',)],
            [('Главное меню',)],
        ])

        self.register('change_option_periodicity', KeyboardType.REPLY, [
            [('Каждый час',), ('Каждые 3 часа',)],
            [('Каждые 6 часов',)],
            [('Главное меню',)],
        ])

        self.register('change_option_intonation', KeyboardType.REPLY, [
            [('Официальная',)],
            [('Саркастично-шутливая',)],
            [('Главное меню',)],
        ])

        self.register('change_option_role', KeyboardType.REPLY, [
            [('Диктор',), ('Стандартная',)],
            [('Главное меню',)],
        ])

        self.register('change_option_language', KeyboardType.REPLY, [
            [('中文',), ('Español',), ('English',)],
            [('हिन्दी',), ('العربية',), ('বাংলা',)],
            [('পর্তুগিজ',), ('Русский',), ('日本語',)],
        ])
