from jinja2 import Template
import imgkit
from typing import Dict, Optional
import os
from pathlib import Path

class TemplateService:
    def __init__(self):
        self.templates = {
            1: self._load_template("business_card"),
            2: self._load_template("product_ad"),
            3: self._load_template("event_invite")
        }

    def _load_template(self, template_name: str) -> str:
        """Load template content from file"""
        template_path = Path(__file__).parent.parent / "templates" / f"{template_name}.html"
        if not template_path.exists():
            raise FileNotFoundError(f"Template {template_name} not found")
        
        with open(template_path, "r", encoding="utf-8") as f:
            return f.read()

    def render_template(self, template_id: int, data: Dict) -> bytes:
        """Render template with data and convert to image"""
        if template_id not in self.templates:
            raise ValueError(f"Template ID {template_id} not found")

        # Get the template
        template_content = self.templates[template_id]
        template = Template(template_content)

        # Render the template with the provided data
        rendered_html = template.render(**data)

        # Convert HTML to image using imgkit
        options = {
            'format': 'png',
            'encoding': "UTF-8",
            'quality': 100
        }
        
        try:
            # Convert HTML to image
            image_data = imgkit.from_string(rendered_html, False, options=options)
            return image_data
        except Exception as e:
            raise Exception(f"Failed to generate image: {str(e)}")

# Create a singleton instance
template_service = TemplateService() 