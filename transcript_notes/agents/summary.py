import instructor
from litellm import completion

from pydantic import BaseModel, Field
from typing import List

from llm import client, model


SUMMARY_PROMPT = """
Analyze the given YouTube transcript and summarize. Provide a title, main topics and key takeaways.
Keep the information in same language.
"""

class ContentSummary(BaseModel):
    title: str = Field(..., description="The title of the video")
    duration: float = Field(
        ..., description="The total duration of the video in seconds"
    )
    main_topics: List[str] = Field(
        ..., description="A list of main topics covered in the video"
    )
    key_takeaways: List[str] = Field(
        ..., description="The most important points from the entire video"
    )


def extract_summary(transcript: str):
    response = client.chat.completions.create(
        model=model,  # You can experiment with different models
        response_model=ContentSummary,
        messages=[
            {
                "role": "system",
                "content": SUMMARY_PROMPT,
            },
            {"role": "user", "content": transcript},
        ],
    )
    return [response]


def fmt_summary(content: ContentSummary):
    topics = "\n".join([f"* {t}" for t in content.main_topics])
    key_takeaways = "\n".join([f"* {k}" for k in content.key_takeaways])
    return f"# {content.title} [dutation:{content.duration}]  \n## Topics:  \n{topics}  \n## Key Takeaways:  \n{key_takeaways}"
