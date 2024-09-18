import instructor
from litellm import completion

from pydantic import BaseModel, Field
from typing import List

from llm import client, model


CHAPTER_PROMPT = """
Analyze the given YouTube transcript and extract chapters. For each chapter, provide a start timestamp, end timestamp, title, and summary.
Keep the information in same language.
"""

class Chapter(BaseModel):
    start_ts: float = Field(
        ...,
        description="The start timestamp indicating when the chapter starts in the video.",
    )
    end_ts: float = Field(
        ...,
        description="The end timestamp indicating when the chapter ends in the video.",
    )
    title: str = Field(
        ..., description="A concise and descriptive title for the chapter."
    )
    summary: str = Field(
        ...,
        description="A brief summary of the chapter's content, don't use words like 'the speaker'",
    )

def extract_chapters(transcript: str):
    return client.chat.completions.create_iterable(
        model=model,  # You can experiment with different models
        response_model=Chapter,
        messages=[
            {
                "role": "system",
                "content": CHAPTER_PROMPT,
            },
            {"role": "user", "content": transcript},
        ],
    )

def fmt_chapter(chapter: Chapter):
    return f"## {chapter.title} [{chapter.start_ts}~{chapter.end_ts}]:  \n{chapter.summary}"