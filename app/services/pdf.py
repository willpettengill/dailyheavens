from pathlib import Path
from typing import Dict, Any
from weasyprint import HTML
from jinja2 import Environment, FileSystemLoader, select_autoescape

class PDFService:
    def __init__(self, templates_dir: str = "templates"):
        self.env = Environment(
            loader=FileSystemLoader(templates_dir),
            autoescape=select_autoescape(['html', 'xml'])
        )

    def generate_chart_pdf(
        self,
        chart_data: Dict[str, Any],
        template_name: str = "chart_template.html",
        output_path: Path = None
    ) -> Path:
        """Generate a PDF report from chart data."""
        # Get template
        template = self.env.get_template(template_name)
        
        # Render HTML
        html_content = template.render(
            chart=chart_data,
            interpretation=chart_data.get("interpretation", "")
        )
        
        # Create output path if not provided
        if output_path is None:
            output_path = Path("temp") / f"chart_{chart_data.get('id', 'report')}.pdf"
            output_path.parent.mkdir(exist_ok=True)
        
        # Generate PDF
        HTML(string=html_content).write_pdf(output_path)
        
        return output_path
