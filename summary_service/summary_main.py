import asyncio
import logging
import re
import itertools
from shared.config import RABBIT_HOST
from shared.models import Post, Role, Intonation
from shared.rabbitmq import Subscriber, QueuesType
from summary_service.chat_gpt import ChatGPT
from db_utils import get_posts_without_summary_async, update_post_summary_async, get_active_gpt_accounts_async, \
    update_chatgpt_account_async, get_role_settings_options_for_gpt, get_intonation_settings_options_for_gpt

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def generate_summary(chatgpt: ChatGPT, post: Post, role_obj: Role, intonation_obj: Intonation):
    try:
        truncated_content = post.content[:10000]  # Truncate the content to 10,000 characters

        messages = [
            {"role": "system", "content": f"You are {role_obj.role} and use intonation {intonation_obj.intonation}"},
            {"role": "user",
             "content": f"Сделай этот текст максимально кратким и понятным: {truncated_content}"}]

        response = await chatgpt.generate_response(messages=messages, user_id=post.post_id, model="gpt-3.5-turbo-16k")
        summary = response['choices'][0]['message']['content']
        summary += f'<a href="https://t.me/{post.channel.channel_username}/{post.post_id}"> #Источник </a>'

        logger.info(f"Summary {summary}")

        return summary, role.id, intonation.id
    except Exception as e:
        error_message = str(e)
        if "Error: 429" in error_message:
            message_match = re.search(r'rate_limit_exceeded', error_message)
            if message_match:
                logger.info("Start disabling acc.")
                await update_chatgpt_account_async(chatgpt.api_key)
                logger.info("End disabling acc.")
            else:
                logger.info("An error occurred, but the message could not be extracted.")
        logger.info(f"Error generating summary for post {post.post_id}: {e}")
        return None


async def generate_summaries():
    while True:
        posts = await get_posts_without_summary_async()
        roles_objects_list = await get_role_settings_options_for_gpt()
        intonation_objects_list = await get_intonation_settings_options_for_gpt()

        if not posts:
            break

        tasks = []
        chatgpt_accounts = await get_active_gpt_accounts_async()
        logger.info(f"GPT accounts {chatgpt_accounts}")

        for post in posts:
            if not chatgpt_accounts:
                break

            chatgpt_account = chatgpt_accounts.pop(0)
            chatgpt_accounts.append(chatgpt_account)
            gpt_instance = ChatGPT(chatgpt_account.api_key)

            tasks.extend(
                generate_summary(gpt_instance, post, role_obj, intonation_obj)
                for role_obj, intonation_obj in itertools.product(roles_objects_list, intonation_objects_list)
            )

        results = await asyncio.gather(*tasks)

        for post, (summary, role_id, intonation_id) in zip(posts, results):
            await update_post_summary_async(post.post_id, summary, role_id, intonation_id)


async def main():
    logger.info(f"Summary service run.")
    subscriber = Subscriber(host=RABBIT_HOST, queue=QueuesType.summary_service)
    subscriber.subscribe(message_type="summarize_news", callback=generate_summaries)
    await subscriber.run()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.create_task(main())
        loop.run_forever()
    finally:
        logger.info("Closing the event loop...")
        loop.close()
