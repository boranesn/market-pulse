from pathlib import Path

from market_pulse.export.markdown import render_markdown
from market_pulse.models.market import AnalysisReport


def render_pdf(report: AnalysisReport, output_path: Path) -> None:
    """Convert the report to PDF via weasyprint (Markdown → HTML → PDF)."""
    import markdown as md_lib
    from weasyprint import HTML

    md_text = render_markdown(report)
    html_content = f"""<!DOCTYPE html>
<html><head>
<meta charset="utf-8">
<style>
  body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
  h1 {{ color: #1a1a2e; border-bottom: 2px solid #16213e; }}
  h2 {{ color: #16213e; margin-top: 24px; }}
  li {{ margin: 4px 0; }}
</style>
</head><body>
{md_lib.markdown(md_text)}
</body></html>"""

    HTML(string=html_content).write_pdf(str(output_path))
