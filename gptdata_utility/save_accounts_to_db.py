# Now we get all api_keys from a single txt file
import logging
import asyncio
import os

from db_utils import save_gpt_account_to_db_sync
from shared.loggers import get_logger
from shared.models import GPTAccount
from chat_gpt import ChatGPT

# logging.basicConfig(level=logging.INFO,
#                     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
#
# logger = logging.getLogger(__name__)
logger = get_logger('gptdata.main')


async def save_account(api_key):
    account = GPTAccount(
        api_key=str(api_key),
    )

    save_gpt_account_to_db_sync(account)


async def load_and_test_account(api_key):
    # Create the client and connect
    client = ChatGPT(api_key)

    logger.info("Initialize new ChatGPT account")

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
        logger.error("Error initializing account", error=e)


api_keys_file = os.path.join(os.path.dirname(__file__), 'api_keys.txt')

# Read the api_keys from the txt file
with open(api_keys_file, 'r') as file:
    api_keys = [line.strip() for line in file]

# Run the main function for each api_key
for api_key in api_keys:
    logger.info("Starting cycle")
    asyncio.run(load_and_test_account(api_key))
