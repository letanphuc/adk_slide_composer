import os

from google.adk.agents import LlmAgent
from google.adk.tools import google_search

research_agent = LlmAgent(
    name="research_agent",
    model=os.getenv('GOOGLE_GENAI_MODEL', 'gemini-2.0-flash'),
    description="Researches background material on the provided topic",
    instruction="""
You are a researcher. Given a topic, generate a concise background summary, key facts, and important references relevant to it.
Your output shall be enough to compose a presentation slide including references. Try to search the Internet for relevant information.
You need to search multiple times (up to 3 times) to get a comprehensive result.
""",
    tools=[google_search],
    output_key="research",
)
