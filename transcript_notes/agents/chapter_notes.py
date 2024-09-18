import instructor
from litellm import completion

from pydantic import BaseModel, Field
from typing import List

from llm import client, model


CHAPTER_PROMPT = """
Analyze the given YouTube transcript and extract chapters notes. For each chapter, provide a start timestamp, end timestamp, title, summary, main topics, and key takeaways.
Keep the information in same language.
"""

class ChapterNote(BaseModel):
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
    main_topics: List[str] = Field(
        ..., description="A list of main topics covered in the chapter"
    )
    key_points: List[str] = Field(
        ..., description="The most important points from the chapter"
    )

def extract_chapters_notes(transcript: str):
    return client.chat.completions.create_iterable(
        model=model,
        response_model=ChapterNote,
        messages=[
            {
                "role": "system",
                "content": CHAPTER_PROMPT,
            },
            {"role": "user", "content": transcript},
        ],
    )

def fmt_chapter_notes(chapter: ChapterNote):
    topics = "\n".join([f"* {t}" for t in chapter.main_topics])
    key_points = "\n".join([f"* {k}" for k in chapter.key_points])
    return f"## {chapter.title} [{chapter.start_ts}~{chapter.end_ts}]:  \n{chapter.summary}  \n### Topics:  \n{topics}  \n### Key Points:  \n{key_points}"
