import litellm
import instructor
from instructor.client import T


class LLM:
    def __init__(self, model) -> None:
        self.model = model
        if "groq" in model or "ollama_chat" in model:
            self.client = instructor.from_litellm(
                litellm.completion, mode=instructor.Mode.MD_JSON
            )
        else:
            self.client = instructor.from_litellm(litellm.completion)

    def structured_complete(self, prompt: str, response_model: type[T], **kwargs) -> T:
        return self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            response_model=response_model,
            **kwargs
        )
