import logging
import logging
import re

from db_utils import update_post_summary_async, get_active_gpt_accounts_async, \
    update_chatgpt_account_async

from shared.models import Post, Role, Intonation
from chat_gpt import ChatGPT

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def generate_summary(chatgpt: ChatGPT, post: Post, role_obj: Role, intonation_obj: Intonation):
    try:
        truncated_content = post.content[:10000]  # Truncate the content to 10,000 characters

        messages = [
            {"role": "system",
             "content": f"Ты программа для сокращения новостей. Используй тон: {intonation_obj.intonation}"},
            {"role": "user",
             "content": f"Ты программа для сокращения новостей. Используй тон: {intonation_obj.intonation}. Сделай текст максимально кратким и понятным, необходимо уложиться в 1-2 предложения.: {truncated_content}"}]

        logger.info(f"For post {post.id} summary is generating from {truncated_content[:50]}")
        response = await chatgpt.generate_response(messages=messages, user_id=post.id, model="gpt-3.5-turbo-16k")
        logger.info(f"For post {post.id} summary is {response['choices'][0]['message']['content'][:50]}")
        summary = response['choices'][0]['message']['content']

        logger.info(f"Summary {summary}")

        return summary
    except Exception as e:
        error_message = str(e)
        if "Error: 429" in error_message:
            message_match = re.search(r'rate_limit_exceeded', error_message)
            message_match2 = re.search(r'insufficient_quota', error_message)
            if message_match or message_match2:
                logger.info("Start disabling acc.")
                await update_chatgpt_account_async(chatgpt.api_key)
                logger.info("End disabling acc.")
        elif "Error: 401" in error_message:
            message_match = re.search(r'invalid_api_key', error_message)
            if message_match:
                logger.info("Start disabling acc.")
                await update_chatgpt_account_async(chatgpt.api_key)
                logger.info("End disabling acc.")
        elif "Invalid model" in error_message:  # Add this condition
            logger.info("Invalid model error occurred. Disabling account.")
            await update_chatgpt_account_async(chatgpt.api_key)
        else:
            logger.info("An error occurred, but the message could not be extracted.")
        logger.info(f"Error generating summary for post {post.id}: {e}")
        return None


async def update_post_and_generate_summary_async(session, index, post, role_obj, intonation_obj):
    chatgpt_accounts = await get_active_gpt_accounts_async(session)
    while len(chatgpt_accounts) > 0:
        num_accounts = len(chatgpt_accounts)
        # Попробуем каждый аккаунт, пока не удастся сгенерировать summary
        for i in range(num_accounts):
            chatgpt_account = chatgpt_accounts[(index + i) % num_accounts]  # Получаем аккаунт с учетом индекса
            chatgpt = ChatGPT(chatgpt_account.api_key)
            summary = await generate_summary(chatgpt, post, role_obj, intonation_obj)
            logger.info(f"Summary: {summary}")
            if summary:
                await update_post_summary_async(session, post.id, summary, role_obj.id, intonation_obj.id)
                return True  # Успешно сгенерировано summary
        # Обновляем список аккаунтов, если не удалось сгенерировать summary
        chatgpt_accounts = await get_active_gpt_accounts_async(session)
    logger.info('False')
    return False  # Не удалось сгенерировать summary
