import instructor
from litellm import completion

model= "openrouter/nousresearch/hermes-3-llama-3.1-405b"
client = instructor.from_litellm(
    completion, mode=instructor.Mode.MD_JSON
)