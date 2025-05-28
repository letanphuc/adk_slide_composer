import time
from typing import Optional

from google.adk.tools import ToolContext
from jinja2 import Environment, BaseLoader
import subprocess

from slide_creator.sub.outline_agent import OutlineSlides, Chapter
from slide_creator.sub.uploader import upload_file


def _compose_latex(slide: OutlineSlides, author: Optional[str] = "Your Name/Organization") -> str:
    latex_template = r"""
\documentclass[11pt]{beamer}

\usepackage{booktabs}
\usetheme{Madrid}
\usepackage{palatino}
\usepackage[default]{opensans}
\useinnertheme{circles}

\title{ {{- slide.title -}} }
\subtitle{ {{- slide.subtitle -}} }
\author{ {{- author -}} }
\institute{}
\date{}

\begin{document}

{# Title Page #}
\begin{frame}
\titlepage
\end{frame}

{# Slides #}
{% for chapter in slide.chapters %}
\section*{ {{- chapter.title -}} }
\begin{frame}
\frametitle{ {{- chapter.title -}} }
\begin{itemize}
{% for point in chapter.bullet_points %}
  \item {{ point }}
{% endfor %}
\end{itemize}
\end{frame}
{% endfor %}

\end{document}
"""
    env = Environment(
        loader=BaseLoader(),
        block_start_string='{%',
        block_end_string='%}',
        variable_start_string='{{',
        variable_end_string='}}',
        autoescape=False,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    template = env.from_string(latex_template)
    return template.render(slide=slide, author=author)


def compose_slides(tool_context: ToolContext) -> dict:
    """Composes LaTeX code and a PDF document, return the URL to the generated Latex, and PDF file."""

    slide_data = OutlineSlides(**tool_context.state.get('slides_data'))
    if not slide_data:
        raise ValueError("Missing slide data.")

    # escape `_` for latex
    def _escape_chars(s):
        replacements = {
            '\\': r'\textbackslash{}',
            '&': r'\&',
            '%': r'\%',
            '$': r'\$',
            '#': r'\#',
            '_': r'\_',
            '{': r'\{',
            '}': r'\}',
            '~': r'\textasciitilde{}',
            '^': r'\textasciicircum{}',
        }
        for char, escape in replacements.items():
            s = s.replace(char, escape)
        return s

    slide_data.title = _escape_chars(slide_data.title)
    slide_data.subtitle = _escape_chars(slide_data.subtitle)
    for chapter in slide_data.chapters:
        chapter.title = _escape_chars(chapter.title)
        chapter.bullet_points = [_escape_chars(s) for s in chapter.bullet_points]

    tex = _compose_latex(
        slide=slide_data,
        author=tool_context.state.get('author', 'Phuc')
    )
    latex_file = 'tmp/output{}.tex'.format(int(time.time()))
    pdf_file = latex_file.replace('.tex', '.pdf')
    with open(latex_file, 'w') as f:
        f.write(tex)
    subprocess.run(['pdflatex', '-output-directory=tmp', latex_file], check=True)

    urls = {
        'latex': upload_file(latex_file),
        'pdf': upload_file(pdf_file),
    }
    return urls


if __name__ == "__main__":
    from slide_creator.sub.outline_agent import OutlineSlides, Chapter
    from google.adk.tools import ToolContext

    sample_slide = OutlineSlides(
        title="C vs C++ for ARM Cortex-M Microcontrollers",
        subtitle="A Comparison for Embedded Systems Engineers",
        chapters=[
            Chapter(
                title="Introduction",
                bullet_points=[
                    "Overview of `ARM Cortex-M`",
                    "Importance in embedded systems"
                ]
            ),
            Chapter(
                title="C Programming",
                bullet_points=[
                    "Low-level access",
                    "Simple and efficient"
                ]
            ),
            Chapter(
                title="C++ Advantages",
                bullet_points=[
                    "Object-oriented features",
                    "Strong type checking _ and -"
                ]
            ),
        ]
    )


    class Context:
        pass


    context = Context()
    context.state = {'slides_data': sample_slide}
    pdf_path = compose_slides(context)
    print("PDF generated:", pdf_path)
