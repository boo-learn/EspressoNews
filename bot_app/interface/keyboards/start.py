from bot_app.core.keyboards.creators import KeyboardType
from bot_app.core.tools.keyboards_tools import KeyboardsTools


class StartKeyboards(KeyboardsTools):
    def __init__(self):
        super().__init__()
        self.init_keyboards()

    def init_keyboards(self):
        self.register('after_start_btn', KeyboardType.INLINE, [
            [('Животные', 'Животные')],
            [('Война', 'Война')],
            [('Ужасы', 'Ужасы')],
        ])

