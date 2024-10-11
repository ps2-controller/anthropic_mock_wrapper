import asyncio
import random
import string
import lorem
from typing import Any, Dict, List, Union, Optional, AsyncIterator, Callable
from anthropic import Anthropic, AsyncAnthropic
from anthropic.types import (
    Message, MessageStreamEvent
)
from anthropic.types.beta import ( BetaMessageBatch,
    BetaMessageBatchIndividualResponse,
    BetaMessageBatchRequestCounts, BetaMessageBatchSucceededResult
)

class MockMessageStream:
    def __init__(self, content: str):
        self.content = content
        self.position = 0

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self.position >= len(self.content):
            raise StopAsyncIteration

        chunk = self.content[self.position:self.position + 10]
        self.position += 10

        return MessageStreamEvent(
            type="content_block_delta",
            index=0,
            delta={"type": "text", "text": chunk}
        )

class AnthropicMockWrapper:
    def __init__(self, client: Union[Anthropic, AsyncAnthropic]):
        self.client = client
        self.is_test = client.api_key.startswith("TEST_")
        self.is_async = isinstance(client, AsyncAnthropic)
        
        # Dynamically create wrapper methods for all client attributes
        for attr_name in dir(client):
            if not attr_name.startswith('_'):
                setattr(self, attr_name, self._create_wrapper(getattr(client, attr_name)))

        # Create nested structures
        self.messages = self.Messages(self)
        self.completions = self.Completions(self)
        self.beta = self.Beta(self)

    def _create_wrapper(self, attr: Any):
        if callable(attr):
            return self._create_method_wrapper(attr)
        elif isinstance(attr, property):
            return property(self._create_property_wrapper(attr))
        else:
            return attr

    def _create_method_wrapper(self, method):
        async def async_wrapper(*args, **kwargs):
            if self.is_test:
                return await self._mock_method(method.__name__, *args, **kwargs)
            return await method(*args, **kwargs)

        def sync_wrapper(*args, **kwargs):
            if self.is_test:
                return self._mock_method(method.__name__, *args, **kwargs)
            return method(*args, **kwargs)

        return async_wrapper if self.is_async else sync_wrapper

    def _create_property_wrapper(self, prop):
        def wrapper(self):
            if self.is_test:
                return self._mock_property(prop.__name__)
            return prop.__get__(self.client)
        return wrapper

    async def _mock_method(self, method_name: str, *args, **kwargs):
        if method_name == "create":
            return self._mock_create(*args, **kwargs)
        elif method_name == "stream":
            return self._mock_stream(*args, **kwargs)
        elif method_name == "retrieve":
            return self._mock_retrieve(*args, **kwargs)
        elif method_name == "list":
            return self._mock_list(*args, **kwargs)
        elif method_name == "cancel":
            return self._mock_cancel(*args, **kwargs)
        elif method_name == "results":
            return self._mock_results(*args, **kwargs)
        else:
            return self._mock_default_method(*args, **kwargs)

    def _mock_property(self, property_name: str):
        if property_name == "api_key":
            return "TEST_API_KEY"
        elif property_name == "base_url":
            return "https://api.anthropic.com"
        elif property_name == "timeout":
            return 600
        elif property_name == "max_retries":
            return 2
        else:
            return None

    def _mock_create(self, *args, **kwargs):
        content = lorem.paragraph()
        return Message(
            id=self._generate_id("msg"),
            type="message",
            role="assistant",
            content=[{"type": "text", "text": content}],
            model=kwargs.get("model", "claude-3-opus-20240229"),
            stop_reason="end_turn",
            usage={"input_tokens": 10, "output_tokens": len(content.split())}
        )

    def _mock_stream(self, *args, **kwargs):
        content = lorem.paragraph()
        return MockMessageStream(content)

    def _mock_retrieve(self, *args, **kwargs):
        return BetaMessageBatch(
            id=self._generate_id("batch"),
            processing_status="completed",
            created_at="2023-01-01T00:00:00Z",
            completed_at="2023-01-01T00:01:00Z",
            request_counts=BetaMessageBatchRequestCounts(
                succeeded=1,
                errored=0,
                canceled=0,
                completed=1,
                total=1
            )
        )

    def _mock_list(self, *args, **kwargs):
        batches = [
            BetaMessageBatch(
                id=self._generate_id("batch"),
                processing_status="completed",
                created_at="2023-01-01T00:00:00Z",
                completed_at="2023-01-01T00:01:00Z",
                request_counts=BetaMessageBatchRequestCounts(
                    succeeded=1,
                    errored=0,
                    canceled=0,
                    completed=1,
                    total=1
                )
            )
            for _ in range(5)
        ]
        return {"data": batches, "has_more": False}

    def _mock_cancel(self, *args, **kwargs):
        return BetaMessageBatch(
            id=self._generate_id("batch"),
            processing_status="canceled",
            created_at="2023-01-01T00:00:00Z",
            completed_at="2023-01-01T00:01:00Z",
            request_counts=BetaMessageBatchRequestCounts(
                succeeded=0,
                errored=0,
                canceled=1,
                completed=1,
                total=1
            )
        )

    def _mock_results(self, *args, **kwargs):
        for _ in range(5):
            yield BetaMessageBatchIndividualResponse(
                custom_id=self._generate_id("custom"),
                result=BetaMessageBatchSucceededResult(
                    type="succeeded",
                    message=self._mock_create()
                )
            )

    def _mock_default_method(self, *args, **kwargs):
        return None

    def _generate_id(self, prefix: str) -> str:
        random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=24))
        return f"{prefix}_{random_string}"

    class Messages:
        def __init__(self, wrapper):
            self.wrapper = wrapper
            self.create = wrapper._create_method_wrapper(wrapper.client.messages.create)
            self.stream = wrapper._create_method_wrapper(wrapper.client.messages.stream)

    class Completions:
        def __init__(self, wrapper):
            self.wrapper = wrapper
            self.create = wrapper._create_method_wrapper(wrapper.client.completions.create)

    class Beta:
        def __init__(self, wrapper):
            self.wrapper = wrapper
            self.messages = self.Messages(wrapper)

        class Messages:
            def __init__(self, wrapper):
                self.wrapper = wrapper
                self.create = wrapper._create_method_wrapper(wrapper.client.beta.messages.create)
                self.batches = self.Batches(wrapper)

            class Batches:
                def __init__(self, wrapper):
                    self.wrapper = wrapper
                    self.create = wrapper._create_method_wrapper(wrapper.client.beta.messages.batches.create)
                    self.retrieve = wrapper._create_method_wrapper(wrapper.client.beta.messages.batches.retrieve)
                    self.list = wrapper._create_method_wrapper(wrapper.client.beta.messages.batches.list)
                    self.cancel = wrapper._create_method_wrapper(wrapper.client.beta.messages.batches.cancel)
                    self.results = wrapper._create_method_wrapper(wrapper.client.beta.messages.batches.results)

    def with_options(self, **kwargs):
        if self.is_test:
            return self
        return self.client.with_options(**kwargs)

    def with_raw_response(self):
        if self.is_test:
            return self
        return self.client.with_raw_response()

    def with_streaming_response(self):
        if self.is_test:
            return self
        return self.client.with_streaming_response()