from bot_app.loader import bot


async def delete_previus_message_for_feedback(call):
    previous_message_id = call.message.message_id - 1

    await bot.delete_message(chat_id=call.message.chat.id, message_id=previous_message_id)

    return True


async def delete_previus_previus_message_for_feedback(call):
    previous_message_id = call.message.message_id - 2

    await bot.delete_message(chat_id=call.message.chat.id, message_id=previous_message_id)

    return True


async def delete_previus_message_for_default(message):
    previous_message_id = message.message_id - 1

    await bot.delete_message(chat_id=message.chat.id, message_id=previous_message_id)

    return True