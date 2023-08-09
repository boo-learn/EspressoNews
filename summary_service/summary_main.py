import asyncio
import logging
import re
import itertools
from shared.config import RABBIT_HOST
from shared.db_utils import get_user_settings, get_digest_with_posts
from shared.models import Post, Role, Intonation
from shared.rabbitmq import Subscriber, QueuesType, Producer, MessageData
from summary_service.chat_gpt import ChatGPT
from db_utils import get_posts_without_summary_async, update_post_summary_async, get_active_gpt_accounts_async, \
    update_chatgpt_account_async, get_role_settings_options_for_gpt, get_intonation_settings_options_for_gpt, \
    get_summary_for_post_async, get_role_by_id, get_intonation_by_id

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


async def generate_summaries(data: dict):
    digest_obj = await get_digest_with_posts(data["digest_id"])
    role_obj = await get_role_by_id(digest_obj.role_id)
    intonation_obj = await get_intonation_by_id(digest_obj.intonation_id)
    posts = digest_obj.posts

    tasks = [update_post_and_generate_summary_async(i, post, role_obj, intonation_obj) for i, post in enumerate(posts)]

    results = await asyncio.gather(*tasks)

    if all(results):
        producer = Producer(host=RABBIT_HOST, queue=QueuesType.bot_service)
        logger.info(f"send_digest")
        message: MessageData = {
            "type": "send_digest",  # send_digest
            "data": {
                "user_id": data["user_id"],
                "digest_id": data["digest_id"],
            }
        }
        await producer.send_message(message_with_data=message, queue=QueuesType.bot_service)
    else:
        logger.info("Some posts failed to process."
                    " Not sending the message."
                    f" Userid: {data['user_id']}, Digestid: {data['digest_id']}")
        producer = Producer(host=RABBIT_HOST, queue=QueuesType.bot_service)
        logger.info(f"no digest")
        message: MessageData = {
            "type": "no_digest",
            "data": {
                "user_id": data["user_id"]
            }
        }
        await producer.send_message(message_with_data=message, queue=QueuesType.bot_service)


async def update_post_and_generate_summary_async(index, post, role_obj, intonation_obj):
    existing_summary = await get_summary_for_post_async(post.id, role_obj.id, intonation_obj.id)
    if existing_summary is None:
        chatgpt_accounts = await get_active_gpt_accounts_async()
        while len(chatgpt_accounts) > 0:
            num_accounts = len(chatgpt_accounts)
            # Попробуем каждый аккаунт, пока не удастся сгенерировать summary
            for i in range(num_accounts):
                chatgpt_account = chatgpt_accounts[(index + i) % num_accounts]  # Получаем аккаунт с учетом индекса
                chatgpt = ChatGPT(chatgpt_account.api_key)
                summary = await generate_summary(chatgpt, post, role_obj, intonation_obj)
                logger.info(f"Summary: {summary}")
                if summary:
                    await update_post_summary_async(post.id, summary, role_obj.id, intonation_obj.id)
                    return True  # Успешно сгенерировано summary
            # Обновляем список аккаунтов, если не удалось сгенерировать summary
            chatgpt_accounts = await get_active_gpt_accounts_async()
    else:
        logger.info(f"Summary already exists for post {post.id}.")
        return True
    logger.info('False')
    return False  # Не удалось сгенерировать summary



async def main():
    logger.info(f"Summary service run.")
    subscriber = Subscriber(host=RABBIT_HOST, queue=QueuesType.summary_service)
    subscriber.subscribe("summarize_digest", generate_summaries)
    await subscriber.run()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.create_task(main())
        loop.run_forever()
    finally:
        logger.info("Closing the event loop...")
        loop.close()
