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

        return summary, role_obj.id, intonation_obj.id
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


async def generate_summaries():
    logger = logging.getLogger('generate_summaries')

    roles_objects_list = await get_role_settings_options_for_gpt()
    logger.info(f"Fetched {len(roles_objects_list)} role settings options for GPT")

    intonation_objects_list = await get_intonation_settings_options_for_gpt()
    logger.info(f"Fetched {len(intonation_objects_list)} intonation settings options for GPT")

    for role_obj, intonation_obj in itertools.product(roles_objects_list, intonation_objects_list):
        logger.info(f"Processing for role {role_obj} and intonation {intonation_obj}")

        while True:
            logger.info("Starting new iteration of post summarization loop.")
            posts = await get_posts_without_summary_async(role_obj=role_obj, intonation_obj=intonation_obj)
            logger.info(f"Fetched {len(posts)} posts without summary")

            if not posts:
                logger.info("No posts without summaries found. Breaking loop.")
                break

            tasks = []
            chatgpt_accounts = await get_active_gpt_accounts_async()
            logger.info(f"Fetched {len(chatgpt_accounts)} active GPT accounts")

            for post in posts:
                if not chatgpt_accounts:
                    logger.warning("No active GPT accounts left. Breaking posts loop.")
                    break

                chatgpt_account = chatgpt_accounts.pop(0)
                chatgpt_accounts.append(chatgpt_account)
                gpt_instance = ChatGPT(chatgpt_account.api_key)
                logger.info(f"Processing post with id {post.post_id} using GPT account {chatgpt_account.api_key}")

                tasks.append(generate_summary(gpt_instance, post, role_obj, intonation_obj))
                logger.info(f"Created {len(tasks)} tasks to generate summaries")

            logger.info("Start gathering results from tasks.")
            results = await asyncio.gather(*tasks)
            results = [result for result in results if result is not None]
            for post, result in zip(posts, results):
                if result is not None:
                    summary, role_id, intonation_id = result
                    await update_post_summary_async(post.post_id, summary, role_id, intonation_id)
                    logger.info(f"Updated post with id {post.post_id} with new summary, role id, and intonation id")

        logger.info("Finished summarization process for role and intonation combination.")


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
