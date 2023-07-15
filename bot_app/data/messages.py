# ---------------------------------------------------------------------------------------------------------------------
# Manual message
# ---------------------------------------------------------------------------------------------------------------------
def gen_manual_mess():
    message = 'Быстренько оповещу тебя, чтобы ко мне не было вопросов сверху. \n \n'
    message += 'У нас есть офигенная фишка. Ты можешь переслать мне любое сообщение с открытого канала, и я добавлю '
    message += 'его в твои подписки.'

    return message


# ---------------------------------------------------------------------------------------------------------------------
# Start message
# ---------------------------------------------------------------------------------------------------------------------
def gen_start_mess(first_name):
    message = f'Привет, <b>{first_name}</b>! \n\n'
    message += 'Здесь самые актуальные новости из различных каналов. \n \n'
    message += 'Как на счёт того, чтобы выбрать каналы, из которых будет приходить сочный digest? \n \n'

    return message


def gen_mess_after_start_btn(first_name):
    message = f'<b>{first_name}</b>, смотри, сейчас нужно будет выбрать интересные тебе категории. \n\n'

    return message


# ---------------------------------------------------------------------------------------------------------------------
# help message
# ---------------------------------------------------------------------------------------------------------------------
def gen_help_mess(first_name):
    message = f'Привет, <b>{first_name}</b>! \n\n'
    message += 'Тебе нужна помощь? \n \n'

    return message


def gen_answer_to_question_mess(number=0):
    answer_messages = [
        'Ответ на вопрос 1',
        'Ответ на вопрос 2',
        'Ответ на вопрос 3',
        'Ответ на вопрос 4',
        'Ответ на вопрос 5'
    ]

    return answer_messages[int(number) - 1]


# ---------------------------------------------------------------------------------------------------------------------
# menu message
# ---------------------------------------------------------------------------------------------------------------------
def gen_menu_mess():
    message = 'Сезам, откройся!!!'

    return message


# ---------------------------------------------------------------------------------------------------------------------
# error message
# ---------------------------------------------------------------------------------------------------------------------
def gen_error_mess():
    message = 'Упс! Такой команды нет =)'

    return message


# ---------------------------------------------------------------------------------------------------------------------
# channels messages
# ---------------------------------------------------------------------------------------------------------------------
# add channel
def gen_adding_users_channels():
    message = 'Так, тут уже придётся немного подумать. \n \n'
    message += 'Каналы какой категории тебе интересны, говоришь?'

    return message


# unsubscribe from the channel
def gen_sure_unsubscribe_mess(channel_title):
    message = f'Вы уверены, что хотите удалить канал {channel_title}  \n \n'

    return message


# not subscribe, cause hidden channel
def gen_subscribe_failed_mess():
    message = f"К сожалению, вы не можете подписаться на закрытый канал!"

    return message


# subscribe success
def gen_success_subscribe_mess(channel_title):
    message = f"Вы подписались на канал {channel_title}"

    return message


# ---------------------------------------------------------------------------------------------------------------------
# Button "no, thanks"
# ---------------------------------------------------------------------------------------------------------------------
def gen_return_message():
    message = 'Для перехода в меню тыкни сюда -> /menu'

    return message


# ---------------------------------------------------------------------------------------------------------------------
# Digest not exist
# ---------------------------------------------------------------------------------------------------------------------
def gen_digest_not_exist_mess():
    message = 'К сожалению, новой информации по вашим каналам не появлялось.'

    return message


# ---------------------------------------------------------------------------------------------------------------------
# Thank you for donate
# ---------------------------------------------------------------------------------------------------------------------
def gen_thank_you_mess():
    message = 'Заранее благодарим вас, ведь уже через минуту наши разработчики станут чуточку счастливее.'

    return message
