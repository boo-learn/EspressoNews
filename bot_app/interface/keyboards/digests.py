from bot_app.core.keyboards.creators import KeyboardType
from bot_app.core.tools.keyboards_tools import KeyboardsTools


class DigestsKeyboards(KeyboardsTools):
    def __init__(self):
        super().__init__()
        self.init_keyboards()

    def init_keyboards(self):
        self.register(
            'digest_load_more',
            KeyboardType.INLINE,
            lambda params: [[('Далее', f'send_summaries_with_offset_{params["offset"]}_for_{params["digest_id"]}')]]
        )