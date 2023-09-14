from bot_app.core.keyboards.creators import KeyboardType
from bot_app.core.tools.keyboards_tools import KeyboardsTools


class ChannelsKeyboards(KeyboardsTools):
    def __init__(self):
        super().__init__()
        self.init_keyboards()

    def init_keyboards(self):
        # self.register(
        #     'success_subscribe',
        #     KeyboardType.INLINE,
        #     lambda channel_username: [[('Отписаться', f'do not subscribe&slash&{channel_username}')]],
        # )
        #
        # self.register('sure_unsubscribe', KeyboardType.INLINE, [
        #     [('Да', 'unsubscribe')],
        #     [('Нет', 'do not unsubscribe')],
        # ])

        self.register(
            'channel_list',
            KeyboardType.INLINE,
            lambda channels: [
                [(channel[0].channel_name, f"choose_channel_{channel[0].channel_id}")]
                for channel in channels
            ]
        )
