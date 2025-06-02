from jinja2 import Template
from typing import Dict
import os
from pathlib import Path
import tempfile
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

class TemplateService:
    def __init__(self):
        self.templates = self._load_all_templates()
        self.driver = None

    def _load_all_templates(self) -> Dict[str, str]:
        """Automatically load all templates from the templates directory"""
        templates = {}
        templates_dir = Path(__file__).parent.parent / "templates"
        
        if not templates_dir.exists():
            raise FileNotFoundError("Templates directory not found")
        
        # Load all HTML files from the templates directory
        for template_file in templates_dir.glob("*.html"):
            template_name = template_file.stem  # Get filename without extension
            with open(template_file, "r", encoding="utf-8") as f:
                templates[template_name] = f.read()
        
        if not templates:
            raise FileNotFoundError("No template files found in templates directory")
        
        return templates

    def get_available_templates(self) -> list[str]:
        """Return list of available template names"""
        return list(self.templates.keys())

    def _ensure_driver(self):
        """Ensure WebDriver is initialized"""
        if self.driver is None:
            chrome_options = Options()
            chrome_options.add_argument("--headless")  # Run in headless mode
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)

    async def render_template(self, template_name: str, data: Dict) -> bytes:
        """Render template with data and convert to image"""
        if template_name not in self.templates:
            raise ValueError(f"Template '{template_name}' not found. Available templates: {', '.join(self.get_available_templates())}")

        # Get the template
        template_content = self.templates[template_name]
        template = Template(template_content)

        # Render the template with the provided data
        rendered_html = template.render(**data)

        # Create a temporary HTML file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.html', mode='w', encoding='utf-8') as f:
            f.write("""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    body { margin: 0; padding: 0; }
                </style>
            </head>
            <body>
            """)
            f.write(rendered_html)
            f.write("</body></html>")
            temp_path = f.name

        try:
            # Ensure WebDriver is initialized
            self._ensure_driver()
            
            # Navigate to the temporary HTML file
            self.driver.get(f"file://{temp_path}")
            
            # Wait for the main div to be present
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "div"))
            )
            
            # Find the main div element
            element = self.driver.find_element(By.TAG_NAME, "div")
            
            # Take screenshot
            screenshot = element.screenshot_as_png
            
            return screenshot
        finally:
            # Cleanup temporary file
            os.unlink(temp_path)

    def cleanup(self):
        """Cleanup WebDriver resources"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
            finally:
                self.driver = None

# Create a singleton instance
template_service = TemplateService() 