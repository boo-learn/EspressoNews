import logging

from bot_app.core.keyboards.creators import KeyboardType
from bot_app.core.tools.keyboards_tools import KeyboardsTools


def build_channels_list(data):
    channels, limit, offset = data
    result = []
    if len(channels) <= limit:
        for channel in channels:
            btn_text = channel[0].channel_name + ' ❌'
            btn_cb = f"unsubscribe_{channel[0].channel_id}"
            result.append([(btn_text, btn_cb)])
    else:
        for channel in channels[offset:limit+offset]:
            btn_text = channel[0].channel_name + ' ❌'
            btn_cb = f"unsubscribe_{channel[0].channel_id}"
            result.append([(btn_text, btn_cb)])
        result.append([
            ('<', 'channels_prev'),
            (str(int(offset/limit + 1)), 'channels_current'),
            ('>', 'channels_next')
        ])

    return result


class AccountKeyboards(KeyboardsTools):
    def __init__(self):
        super().__init__()
        self.init_keyboards()

    def init_keyboards(self):
        self.register(
            'account_main', KeyboardType.REPLY, [
                [
                    ('kb_reply_my_channels', )
                ],
                [
                    ('kb_reply_change_intonation', ),
                    ('kb_reply_change_name', ),
                ],
                [
                    ('kb_reply_change_language', ),
                    ('kb_reply_to_main', ),
                ],
            ]
        )
        self.register(
            'account_ask_for_intonation', KeyboardType.INLINE, [
                [
                    ('list_official', 'cb_intonation_Official'),
                    ('list_sarcastic-joking', 'cb_intonation_Comedy_sarcastic'),
                ]
            ]
        )
        self.register(
            'account_ask_for_language', KeyboardType.INLINE, [
                [
                    ("🇷🇺 Русский", "cb_language_set_ru"),
                    ("🇺🇸 English", "cb_language_set_en"),
                    #("🇮🇳 हिन्दी", "cb_language_set_hi"),

                ],
                # [
                #     ("🇨🇳 中文", "cb_language_set_zh"),
                #     ("🇸🇦 العربية", "cb_language_set_ar"),
                #     ("🇧🇩 বাংলা", "cb_language_set_bn"),
                # ],
                # [
                #     ("🇪🇸 Español", "cb_language_set_es"),
                #     ("🇵🇹 Português", "cb_language_set_pt"),
                #     ("🇯🇵 日本語", "cb_language_set_ja"),
                # ],
            ]
        )
        self.register(
            'channel_list',
            KeyboardType.INLINE,
            build_channels_list
        )
        self.register(
            'language_updated', KeyboardType.REPLY, [
                [
                    ('kb_reply_my_channels', )
                ],
                [
                    ('kb_reply_change_intonation', ),
                    ('kb_reply_change_name', ),
                ],
                [
                    ('kb_reply_change_language', ),
                    ('kb_reply_to_main', ),
                ],
            ]
        )
