import lorem
from anthropic import Anthropic, AsyncAnthropic
from typing import Any, Dict, AsyncGenerator, Union

class AnthropicMockWrapper:
    def __init__(self, client: Union[Anthropic, AsyncAnthropic]):
        self.client = client
        self.is_test = isinstance(client, Anthropic) and client.api_key.startswith("TEST_")

    async def completion(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        if self.is_test:
            return self._get_mock_response(kwargs.get("max_tokens_to_sample", 100))
        
        if isinstance(self.client, AsyncAnthropic):
            return await self.client.completions.create(*args, **kwargs)
        else:
            return self.client.completions.create(*args, **kwargs)

    async def completion_stream(self, *args: Any, **kwargs: Any) -> AsyncGenerator[Dict[str, Any], None]:
        if self.is_test:
            yield self._get_mock_response(kwargs.get("max_tokens_to_sample", 100))
        else:
            if isinstance(self.client, AsyncAnthropic):
                async for chunk in self.client.completions.create(*args, **kwargs):
                    yield chunk
            else:
                for chunk in self.client.completions.create(*args, **kwargs):
                    yield chunk

    async def messages_create(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        if self.is_test:
            return self._get_mock_response(kwargs.get("max_tokens", 100))
        
        return await self.client.messages.create(*args, **kwargs)


    def _get_mock_response(self, max_tokens: int) -> Dict[str, Any]:
        return {
            "completion": self._generate_lorem_ipsum(max_tokens),
            "stop_reason": "length",
            "model": "claude-2"
        }
    def _generate_lorem_ipsum(self, max_tokens: int) -> str:
        words = lorem.text().split()
        return " ".join(words[:max_tokens])
