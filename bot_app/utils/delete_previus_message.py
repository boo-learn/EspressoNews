from aiogram.utils.exceptions import MessageToDeleteNotFound

from bot_app.loader import bot


async def delete_previus_message_for_feedback(call):
    previous_message_id = call.message.message_id - 1

    try:
        await bot.delete_message(chat_id=call.message.chat.id, message_id=previous_message_id)
    except MessageToDeleteNotFound:
        print(f"Message with ID {previous_message_id} not found for deletion in chat {call.message.chat.id}")
        # Здесь можно добавить дополнительный код для логирования или других действий

    return True


async def delete_previus_previus_message_for_feedback(call):
    previous_message_id = call.message.message_id - 2

    try:
        await bot.delete_message(chat_id=call.message.chat.id, message_id=previous_message_id)
    except MessageToDeleteNotFound:
        print(f"Message with ID {previous_message_id} not found for deletion in chat {call.message.chat.id}")
        # Здесь можно добавить дополнительный код для логирования или других действий

    return True


async def delete_previus_message_for_default(message):
    previous_message_id = message.message_id - 1

    try:
        await bot.delete_message(chat_id=message.chat.id, message_id=previous_message_id)
    except MessageToDeleteNotFound:
        print(f"Message with ID {previous_message_id} not found for deletion in chat {message.chat.id}")
        # Здесь можно добавить дополнительный код для логирования или других действий

    return True