import logging

from bot_app.core.keyboards.creators import KeyboardType
from bot_app.core.tools.keyboards_tools import KeyboardsTools


logger = logging.getLogger(__name__)


class MenuKeyboards(KeyboardsTools):
    def __init__(self):
        super().__init__()
        self.init_keyboards()

    def init_keyboards(self):
        self.register('thank_you', KeyboardType.INLINE, [
            [('Отблагодарить', None, 'https://t.me/espressonewsabout/7')]
        ])

        self.register('menu', KeyboardType.REPLY, [
            [('Донат',), ('Настройки',)],
            [('Мои каналы',)],
        ])
