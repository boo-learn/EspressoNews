from bot_app.core.keyboards.creators import KeyboardType
from bot_app.core.tools.keyboards_tools import KeyboardsTools


class StartKeyboards(KeyboardsTools):
    def __init__(self):
        super().__init__()
        self.init_keyboards()

    def init_keyboards(self):
        self.register(
            'after_start_btn', KeyboardType.INLINE, [
                [('Животные', 'Животные')],
                [('Война', 'Война')],
                [('Ужасы', 'Ужасы')],
            ]
        )
        self.register(
            'start',
            KeyboardType.REPLY,
            [
                [
                    ('Настроить сейчас ✅',),
                    ('Настроить позже ➡️',),
                ],
            ]
        )
        self.register(
            'ask_for_name',
            KeyboardType.INLINE,
            [[('Оставить имя', 'keep_name_cb')]]
        )
        self.register(
            'ask_for_intonation',
            KeyboardType.INLINE,
            [
                [
                    ('list_official', 'list_official'),
                    ('list_sarcastic-joking', 'list_sarcastic-joking'),
                ],
            ]
        )
