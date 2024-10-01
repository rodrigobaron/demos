import instructor
from litellm import completion
from llama_index.llms.litellm import LiteLLM

model= "openrouter/nousresearch/hermes-3-llama-3.1-405b:free"

llm = LiteLLM(model=model)
client = instructor.from_litellm(
    completion, mode=instructor.Mode.MD_JSON
)