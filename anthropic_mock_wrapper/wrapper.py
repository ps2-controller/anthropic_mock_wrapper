import lorem
from anthropic import Anthropic, AsyncAnthropic
from typing import Any, Dict, List, AsyncGenerator, Union, Optional
import asyncio

class AnthropicMockWrapper:
    def __init__(self, client: Union[Anthropic, AsyncAnthropic]):
        self.client = client
        self.is_test = isinstance(client, Anthropic) and client.api_key.startswith("TEST_")
        self.messages = self.Messages(self)
        self.message_batches = self.MessageBatches(self)

    async def completion(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        if self.is_test:
            return self._get_mock_response(kwargs.get("max_tokens_to_sample", 100), "completion")
        
        if isinstance(self.client, AsyncAnthropic):
            return await self.client.completions.create(*args, **kwargs)
        else:
            return self.client.completions.create(*args, **kwargs)

    async def completion_stream(self, *args: Any, **kwargs: Any) -> AsyncGenerator[Dict[str, Any], None]:
        if self.is_test:
            yield self._get_mock_response(kwargs.get("max_tokens_to_sample", 100), "completion")
        else:
            if isinstance(self.client, AsyncAnthropic):
                async for chunk in self.client.completions.create(*args, **kwargs):
                    yield chunk
            else:
                for chunk in self.client.completions.create(*args, **kwargs):
                    yield chunk

    async def messages_create(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        if self.is_test:
            return self._get_mock_response(kwargs.get("max_tokens", 100), "message")
        
        if isinstance(self.client, AsyncAnthropic):
            return await self.client.messages.create(*args, **kwargs)
        else:
            return self.client.messages.create(*args, **kwargs)

    class Messages:
        def __init__(self, wrapper):
            self.wrapper = wrapper

        async def create(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
            return await self.wrapper.messages_create(*args, **kwargs)

    class MessageBatches:
        def __init__(self, wrapper):
            self.wrapper = wrapper

        async def create(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
            if self.wrapper.is_test:
                return self.wrapper._get_mock_response(kwargs.get("max_tokens", 100), "message_batch")
            
            if isinstance(self.wrapper.client, AsyncAnthropic):
                return await self.wrapper.client.message_batches.create(*args, **kwargs)
            else:
                return self.wrapper.client.message_batches.create(*args, **kwargs)

        async def retrieve(self, message_batch_id: str) -> Dict[str, Any]:
            if self.wrapper.is_test:
                return self.wrapper._get_mock_response(100, "message_batch")
            
            if isinstance(self.wrapper.client, AsyncAnthropic):
                return await self.wrapper.client.message_batches.retrieve(message_batch_id)
            else:
                return self.wrapper.client.message_batches.retrieve(message_batch_id)

        async def retrieve_results(self, message_batch_id: str) -> str:
            if self.wrapper.is_test:
                return self.wrapper._generate_lorem_ipsum(100)
            
            if isinstance(self.wrapper.client, AsyncAnthropic):
                return await self.wrapper.client.message_batches.retrieve_results(message_batch_id)
            else:
                return self.wrapper.client.message_batches.retrieve_results(message_batch_id)

        async def list(self, limit: int = 20, before_id: Optional[str] = None, after_id: Optional[str] = None) -> Dict[str, Any]:
            if self.wrapper.is_test:
                return {"data": [self.wrapper._get_mock_response(100, "message_batch") for _ in range(limit)]}
            
            if isinstance(self.wrapper.client, AsyncAnthropic):
                return await self.wrapper.client.message_batches.list(limit=limit, before_id=before_id, after_id=after_id)
            else:
                return self.wrapper.client.message_batches.list(limit=limit, before_id=before_id, after_id=after_id)

        async def cancel(self, message_batch_id: str) -> Dict[str, Any]:
            if self.wrapper.is_test:
                return self.wrapper._get_mock_response(100, "message_batch", processing_status="canceling")
            
            if isinstance(self.wrapper.client, AsyncAnthropic):
                return await self.wrapper.client.message_batches.cancel(message_batch_id)
            else:
                return self.wrapper.client.message_batches.cancel(message_batch_id)

    def _get_mock_response(self, max_tokens: int, response_type: str, processing_status: str = "in_progress") -> Dict[str, Any]:
        if response_type == "completion":
            return {
                "completion": self._generate_lorem_ipsum(max_tokens),
                "stop_reason": "length",
                "model": "claude-2"
            }
        elif response_type == "message":
            return {
                "id": "msg_" + self._generate_lorem_ipsum(8),
                "type": "message",
                "role": "assistant",
                "content": [{"type": "text", "text": self._generate_lorem_ipsum(max_tokens)}],
                "model": "claude-3-opus-20240229",
                "stop_reason": "end_turn",
                "usage": {"input_tokens": 10, "output_tokens": max_tokens}
            }
        elif response_type == "message_batch":
            return {
                "id": "msgbatch_" + self._generate_lorem_ipsum(8),
                "type": "message_batch",
                "processing_status": processing_status,
                "request_counts": {
                    "processing": 100,
                    "succeeded": 50,
                    "errored": 30,
                    "canceled": 10,
                    "expired": 10
                },
                "created_at": "2024-08-20T18:37:24.100435Z",
                "expires_at": "2024-08-21T18:37:24.100435Z",
                "results_url": f"https://api.anthropic.com/v1/messages/batches/msgbatch_{self._generate_lorem_ipsum(8)}/results"
            }

    def _generate_lorem_ipsum(self, max_tokens: int) -> str:
        words = lorem.text().split()
        return " ".join(words[:max_tokens])