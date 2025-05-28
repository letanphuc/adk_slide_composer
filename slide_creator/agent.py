import os
import time

from google.adk.agents import LlmAgent
from google.adk.tools.agent_tool import AgentTool

from slide_creator.sub.compose_slides import compose_slides
from slide_creator.sub.outline_agent import outline_slide_agent
from slide_creator.sub.research_agent import research_agent


def write_tex_file(tex: str) -> str:
    """Writes LaTeX code to a file, tex shall be raw string, then return the file path."""
    p = 'tmp/output_{}.tex'.format(int(time.time()))
    # workaround
    tex = tex.replace('\\n', '\n')
    with open(p, 'w') as f:
        f.write(tex)
    return p


def compile_pdf(tex_path: str) -> str:
    """Compiles LaTeX code into a PDF document.

    Args:
        tex_path (str): Path to the LaTeX source file to compile.

    Returns:
        str: Path to the generated PDF file.
    """
    import subprocess
    import os

    pdf_path = os.path.splitext(tex_path)[0] + '.pdf'
    subprocess.run(['pdflatex', '-output-directory=tmp', tex_path], check=True)
    return pdf_path


slide_workflow_coordinator = LlmAgent(
    name="slide_workflow_coordinator",
    model=os.getenv('GOOGLE_GENAI_MODEL', 'gemini-2.0-flash'),
    description="Main agent that collects input from the user, clarifies it, then triggers the slide creation sequence",
    instruction="""
You are a user assistant helping to create presentation slides.
Start by asking the user what topic they want slides for.
Ask clarifying questions until you have enough detail (target audience, goal, number of slides, examples, etc).
Once ready, call:
 - research_agent to gather background information
 - outline_slide_agent to convert the background information into a structured outline
 - compose_pdf: to compose the slides from the outline
 
You have to provide both latex and pdf URL for user to download.
""",
    tools=[
        AgentTool(agent=research_agent),
        AgentTool(agent=outline_slide_agent),
        compose_slides
    ]
)

root_agent = slide_workflow_coordinator
