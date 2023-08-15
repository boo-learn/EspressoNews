import httpx
from httpx import Timeout


class ChatGPT:
    def __init__(self, api_key):
        self.api_key = api_key
        self.api_url = "https://api.openai.com/v1/chat/completions"

    async def generate_response(self, messages, user_id, model, **kwargs):
        # Prepare the data and headers for the API request
        headers, data = self._prepare_request_data(messages, user_id, model, **kwargs)

        # Make the API request
        response = await self._make_api_request(headers, data)

        # Handle the response
        return self._handle_response(response)

    def _prepare_request_data(self, messages, user_id, model, **kwargs):
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        data = {
            "model": model,
            "messages": messages,
        }

        data.update(kwargs)

        return headers, data

    async def _make_api_request(self, headers, data):
        async with httpx.AsyncClient(timeout=Timeout(60.0)) as client:
            response = await client.post(self.api_url, headers=headers, json=data)
        return response

    def _handle_response(self, response):
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Error: {response.status_code}, {response.text}")
