import asyncio

from shared.models import Post
from summary_service.chat_gpt import ChatGPT
from summary_service.db_utils import get_posts_without_summary, update_post_summary, get_active_gpt_accounts


async def generate_summary(chatgpt: ChatGPT, post: Post):
    try:
        messages = [{"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": f"Summarize this news article: {post.content}"}]

        response = await chatgpt.generate_response(messages=messages, user_id=post.post_id, model="text-davinci-002")
        summary = response['choices'][0]['message']['content']
        return summary
    except Exception as e:
        print(f"Error generating summary for post {post.post_id}: {e}")
        return None


async def generate_summaries(chatgpt_accounts):
    posts = get_posts_without_summary()
    tasks = []

    for post in posts:
        chatgpt_account = chatgpt_accounts.pop(0)
        chatgpt_accounts.append(chatgpt_account)

        tasks.append(generate_summary(chatgpt_account, post))

    summaries = await asyncio.gather(*tasks)

    for post, summary in zip(posts, summaries):
        update_post_summary(post.post_id, summary)


async def main():
    chatgpt_accounts = get_active_gpt_accounts()
    # Нужно добавить код, на запуск от RabbitMQ TODO
    # await generate_summaries(chatgpt_accounts)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    finally:
        loop.close()
