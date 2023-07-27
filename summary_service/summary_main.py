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
    get_summary_for_post_async

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def generate_summary(chatgpt: ChatGPT, post: Post, role_obj: Role, intonation_obj: Intonation):
    try:
        truncated_content = post.content[:10000]  # Truncate the content to 10,000 characters

        messages = [
            {"role": "system",
             "content": f"Твоя роль {role_obj.role} и используй интонацию {intonation_obj.intonation}"},
            {"role": "user",
             "content": f"Сделай этот текст максимально кратким и понятным, отвечай на русском языке: {truncated_content}"}]

        response = await chatgpt.generate_response(messages=messages, user_id=post.post_id, model="gpt-3.5-turbo-16k")
        summary = response['choices'][0]['message']['content']
        summary += f'<a href="https://t.me/{post.channel.channel_username}/{post.post_id}"> #Источник </a>'

        logger.info(f"Summary {summary}")

        return summary
    except Exception as e:
        error_message = str(e)
        if "Error: 429" in error_message:
            message_match = re.search(r'rate_limit_exceeded', error_message)
            if message_match:
                logger.info("Start disabling acc.")
                await update_chatgpt_account_async(chatgpt.api_key)
                logger.info("End disabling acc.")
        elif "Invalid model" in error_message:  # Add this condition
            logger.info("Invalid model error occurred. Disabling account.")
            await update_chatgpt_account_async(chatgpt.api_key)
        else:
            logger.info("An error occurred, but the message could not be extracted.")
        logger.info(f"Error generating summary for post {post.post_id}: {e}")
        return None


async def generate_summaries(data: dict):
    user_settings_obj = await get_user_settings(data["user_id"])
    role_obj = user_settings_obj.role
    intonation_obj = user_settings_obj.intonation

    digest_obj = await get_digest_with_posts(data["digest_id"])
    posts = digest_obj.posts

    chatgpt_accounts = await get_active_gpt_accounts_async()
    chatgpt_accounts_iter = itertools.cycle(chatgpt_accounts)

    tasks = []
    for post in posts:
        chatgpt_account = next(chatgpt_accounts_iter)
        chatgpt = ChatGPT(chatgpt_account.api_key)
        tasks.append(update_post_and_generate_summary_async(chatgpt, post, role_obj, intonation_obj))

    await asyncio.gather(*tasks)
    producer = Producer(host=RABBIT_HOST, queue=QueuesType.bot_service)
    logger.info(f"send_digest")
    message: MessageData = {
        "type": "send_digest",  # send_digest
        "data": {
            "user_id": data["user_id"],
            "digest_id": data["digest_id"],
        }
    }
    await producer.send_message(message_with_data=message, queue=QueuesType.summary_service)


async def update_post_and_generate_summary_async(chatgpt, post, role_obj, intonation_obj):
    existing_summary = await get_summary_for_post_async(post.post_id, role_obj.id, intonation_obj.id)
    if existing_summary is None:
        summary = await generate_summary(chatgpt, post, role_obj, intonation_obj)
        if summary:
            await update_post_summary_async(post.post_id, summary, role_obj.id, intonation_obj.id)


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
