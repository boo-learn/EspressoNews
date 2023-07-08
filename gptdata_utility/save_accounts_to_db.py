# Получаем список всех файлов с расширением .ini в папке accounts
import logging
import asyncio
import glob
import os

import configparser

from db_utils import save_gpt_account_to_db_sync
from shared.models import GPTAccount
from summary_service.chat_gpt import ChatGPT

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)


async def save_account(api_key):
    account = GPTAccount(
        api_key=str(api_key),
    )

    save_gpt_account_to_db_sync(account)


async def load_and_test_account(config_file):
    # Reading Configs
    config = configparser.ConfigParser()
    config.read(config_file)

    # Setting configuration values
    api_key = config['ChatGPT']['api_key']

    # Create the client and connect
    client = ChatGPT(api_key)

    logger.info("init gpt")

    try:
        response = await client.generate_response(
            messages=[{'role': 'system', 'content': 'Привет.'}],
            user_id=1,
            model="gpt-3.5-turbo-16k",
        )

        logger.info("Response sent")

        if response['choices'][0]['message']['content'] is not None:
            await save_account(api_key)
    except Exception as e:
        print(f"An error occurred: {e}")


accounts_path = os.path.join(os.path.dirname(__file__), 'accounts')
config_files = glob.glob(os.path.join(accounts_path, '*.ini'))

# Запускаем main функцию для каждого файла конфигурации
for config_file in config_files:
    logger.info("Starting cycle")
    asyncio.run(load_and_test_account(config_file))
