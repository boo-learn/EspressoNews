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
