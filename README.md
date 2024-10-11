# AnthropicMockerClient

A lightweight wrapper around the Anthropic Python client for testing purposes.

Save money on your Anthropic API usage by mocking responses when your API key is prefixed with `TEST_`.

## Installation

You can install the AnthropicMockerClient package using pip:

```bash
pip install AnthropicMockerClient
```

```python
from anthropic_Mocker_client import AnthropicMockerClient
```

## Initialize the client

```python
client = AnthropicMockerClient(api_key="your_api_key_here")
```

## Use the client to interact with Anthropic's API

```python
response = client.complete(
prompt="Hello, world!",
model="claude-2",
max_tokens_to_sample=100
)
print(response)
```

```python
from anthropic_Mocker_client import AnthropicMockerClient
# Initialize the testable client
testable_client = AnthropicMockerClient(api_key="test_key")
#Set a mock response
testable_client.set_mock_response({
"completion": "This is a mock response",
"stop_reason": "stop_sequence",
"model": "claude-2"
})
# Use the client in your tests
response = testable_client.complete(
prompt="Test prompt",
model="claude-2",
max_tokens_to_sample=100
)
assert response["completion"] == "This is a mock response"
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This is an unofficial Mocker and is not affiliated with or endorsed by Anthropic. Use at your own risk.
