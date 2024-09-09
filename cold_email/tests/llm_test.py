from unittest.mock import MagicMock
from llm import LLM


def test_structured_complete(mocker):
    mock_create = MagicMock(return_value="response")
    mocker.patch("instructor.from_litellm", return_value=MagicMock())
    response_model = MagicMock()

    llm = LLM("test_model")
    llm.client.chat.completions.create = mock_create

    response = llm.structured_complete("prompt", response_model)
    mock_create.assert_called_once_with(
        model="test_model",
        messages=[{"role": "user", "content": "prompt"}],
        response_model=response_model,
    )
    assert response == "response"
