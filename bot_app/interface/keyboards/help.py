from bot_app.core.keyboards.creators import KeyboardType
from bot_app.core.tools.keyboards_tools import KeyboardsTools


class HelpKeyboards(KeyboardsTools):
    def __init__(self):
        super().__init__()
        self.init_keyboards()

    def init_keyboards(self):
        self.register('frequent_questions', KeyboardType.INLINE, [
            [('Вопрос 1', 'question_1')],
            [('Вопрос 2', 'question_2')],
            [('Вопрос 3', 'question_3')],
            [('Вопрос 4', 'question_4')],
            [('Вопрос 5', 'question_5')],
        ])
        self.register(
            'help_main',
            KeyboardType.REPLY,
            [
                [
                    ('kb_reply_about', 'kb_reply_about'),
                    ('kb_reply_contact', 'kb_reply_contact')
                ],
                [
                    ('kb_reply_main_menu', 'kb_reply_main_menu')
                ]
            ]
        )
        self.register(
            'contact_text',
            KeyboardType.INLINE,
            [
                [
                    ('kb_inline_contact', None, 'https://t.me/nekone')
                ]
            ]
        )
        self.register(
            'to_main_menu',
            KeyboardType.REPLY,
            [
                [
                    ('kb_reply_search', 'kb_reply_search'),
                    ('kb_reply_lk', 'kb_reply_lk'),
                ],
                [
                    ('kb_reply_donate', 'kb_reply_donate'),
                    ('kb_reply_help', 'kb_reply_help'),
                ],
            ]

        )
