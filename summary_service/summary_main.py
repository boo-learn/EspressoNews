import asyncio

from shared.config import RABBIT_HOST
from shared.models import Post
from shared.rabbitmq import Subscriber, QueuesType
from summary_service.chat_gpt import ChatGPT
from db_utils import get_posts_without_summary_async, update_post_summary_async, get_active_gpt_accounts_async


async def generate_summary(chatgpt: ChatGPT, post: Post):
    try:
        truncated_content = post.content[:10000]  # Truncate the content to 10,000 characters

        messages = [{"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": f"Summarize this news article: {truncated_content}"}]

        response = await chatgpt.generate_response(messages=messages, user_id=post.post_id, model="gpt-3.5-turbo-16k")
        summary = response['choices'][0]['message']['content']
        return summary
    except Exception as e:
        print(f"Error generating summary for post {post.post_id}: {e}")
        return None


async def generate_summaries():
    chatgpt_accounts = await get_active_gpt_accounts_async()
    posts = await get_posts_without_summary_async()
    tasks = []

    for post in posts:
        chatgpt_account = chatgpt_accounts.pop(0)
        chatgpt_accounts.append(chatgpt_account)

        tasks.append(generate_summary(chatgpt_account, post))

    summaries = await asyncio.gather(*tasks)

    for post, summary in zip(posts, summaries):
        await update_post_summary_async(post.post_id, summary)


async def main():
    subscriber = Subscriber(host=RABBIT_HOST, queue=QueuesType.summary_service)
    subscriber.subscribe(message_type="summarize_news", callback=generate_summaries)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    finally:
        loop.close()
