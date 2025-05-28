import os
from pydantic import BaseModel, Field
from typing import List
from google.adk.agents import LlmAgent


class Chapter(BaseModel):
    title: str = Field(description="Title of the chapter/slide.")
    bullet_points: List[str] = Field(description="Bullet points for the chapter.")


class OutlineSlides(BaseModel):
    title: str = Field(description="Presentation title.")
    subtitle: str = Field(description="Presentation subtitle.")
    chapters: List[Chapter] = Field(description="List of chapters/slides in the presentation.")


outline_slide_agent = LlmAgent(
    name="outline_slide_agent",
    model=os.getenv('GOOGLE_GENAI_MODEL', 'gemini-2.0-flash'),
    description="Generates a structured slide deck from a given outline.",
    instruction="""
You are a slide formatter. Given detailed information, generate a structured presentation.
Ensure professional formatting with ~10 slides.
""",
    output_schema=OutlineSlides,
    output_key="slides_data",
)
