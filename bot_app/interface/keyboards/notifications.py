import logging

from bot_app.core.keyboards.creators import KeyboardType
from bot_app.core.tools.keyboards_tools import KeyboardsTools


logger = logging.getLogger(__name__)


class MenuKeyboards(KeyboardsTools):
    def __init__(self):
        super().__init__()
        self.init_keyboards()

    def init_keyboards(self):
        self.register('suggestion_enter_mail', KeyboardType.INLINE, [
            [
                ('Нет, спасибо ❌', 'no_send_email'),
                ('Ввести почту✏️', 'enter_email'),
            ]
        ])
