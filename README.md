# anthropic_mock_wrapper

A lightweight wrapper around the Anthropic Python client for testing purposes.

Save money on your Anthropic API usage by mocking responses when your API key is prefixed with `TEST_`.

## Installation

You can install the anthropic_mock_wrapper package using pip:

```bash
pip install anthropic_mock_wrapper
```

```python
from anthropic_mock_wrapper import AnthropicMockWrapper
```

## Initialize the client

```python
client = AnthropicMockWrapper(api_key="TEST_your_api_key_here")
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
from anthropic_mock_wrapper import AnthropicMockWrapper
# Initialize the testable client
testable_client = AnthropicMockWrapper(api_key="test_key")
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

## Build

```bash
python -m build
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This is an unofficial Mocker and is not affiliated with or endorsed by Anthropic. Use at your own risk.
