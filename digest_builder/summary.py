from db_utils import update_post_summary_async, get_active_gpt_accounts_async, \
    update_chatgpt_account_async
from shared.loggers import get_logger
from shared.models import Post, Role, Intonation, Language
from chat_gpt import ChatGPT, ChatGPTError

logger = get_logger('digest.summary')


async def generate_summary(
        chatgpt: ChatGPT,
        post: Post,
        role_obj: Role,
        intonation_obj: Intonation,
        language_obj: Language
):
    local_logger = logger.bind(post_id=post.id)
    try:
        truncated_content = post.content[:10000]

        messages = [
            {"role": "system",
             "content": f"Ты программа для сокращения новостей. Используй тон: {intonation_obj.intonation}. Используй {language_obj.name} язык."},
            {"role": "user",
             "content": f"Ты программа для сокращения новостей. Используй тон: {intonation_obj.intonation}. Используй {language_obj.name} язык.. Сделай текст максимально кратким и понятным, необходимо уложиться в 1-2 предложения.: {truncated_content}"}]

        local_logger.info("Generating summary", content=truncated_content[:50])
        response = await chatgpt.generate_response(messages=messages, user_id=post.id, model="gpt-3.5-turbo-16k")
        summary = response['choices'][0]['message']['content']
        local_logger.info('Summary generated', summary=summary[:50])

        return summary
    except ChatGPTError as e:
        if e.status_code == 429:
            if 'rate_limit_exceeded' in e.text:
                msg = 'rate_limit_exceeded'
            elif 'insufficient_quota' in e.text:
                msg = 'insufficient_quota'
            else:
                msg = None
            if msg:
                logger.error("Failed summary generation", reason=msg)
                logger.error("Start disabling account", api_key=chatgpt.api_key)
                await update_chatgpt_account_async(chatgpt.api_key)
                logger.info("Account disabled", api_key=chatgpt.api_key)
        elif e.status_code == 401:
            if 'invalid_api_key' in e.text:
                logger.error("Failed summary generation", reason='invalid_api_key')
                logger.error("Start disabling account", api_key=chatgpt.api_key)
                await update_chatgpt_account_async(chatgpt.api_key)
                logger.info("Account disabled", api_key=chatgpt.api_key)
        elif "Invalid model" in e.text:  # Add this condition
            logger.error("Failed summary generation", reason='invalid_model')
            logger.error("Start disabling account", api_key=chatgpt.api_key)
            await update_chatgpt_account_async(chatgpt.api_key)
            logger.info("Account disabled", api_key=chatgpt.api_key)
        else:
            logger.error("An error occurred, but the message could not be extracted.")
        local_logger.error(f"Failed summary generation", error=e)
        return None
    except Exception as e:
        logger.error('Unexpected exception', error=e)


async def update_post_and_generate_summary_async(session, index, post, role_obj, intonation_obj, language_obj):
    chatgpt_accounts = await get_active_gpt_accounts_async(session)
    while len(chatgpt_accounts) > 0:
        num_accounts = len(chatgpt_accounts)
        # Попробуем каждый аккаунт, пока не удастся сгенерировать summary
        for i in range(num_accounts):
            chatgpt_account = chatgpt_accounts[(index + i) % num_accounts]  # Получаем аккаунт с учетом индекса
            chatgpt = ChatGPT(chatgpt_account.api_key)
            summary = await generate_summary(chatgpt, post, role_obj, intonation_obj, language_obj)
            if summary:
                await update_post_summary_async(session, post.id, summary, role_obj.id, intonation_obj.id, language_obj.id)
                return True  # Успешно сгенерировано summary
        # Обновляем список аккаунтов, если не удалось сгенерировать summary
        chatgpt_accounts = await get_active_gpt_accounts_async(session)
    logger.info('Failed to generate summary')
    return False  # Не удалось сгенерировать summary
