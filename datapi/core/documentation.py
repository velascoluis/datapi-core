import os
import yaml
import glob
import markdown
from jinja2 import Environment, FileSystemLoader, ChoiceLoader, PackageLoader
import http.server
import socketserver
from typing import List, Optional, Dict
from pathlib import Path

RESOURCE_DOC_TEMPLATE_NAME = "resource_doc.html.jinja2"
INDEX_TEMPLATE_NAME = "index.html.jinja2"


class Documentation:
    def __init__(self, project_path: Optional[str] = None):
        self.project_path = Path(project_path or os.getcwd())
        self.resources_path = self.project_path / 'resources'
        self.docs_path = self.project_path / 'docs'

        package_loader = PackageLoader('datapi.core', 'templates')
        file_loader = FileSystemLoader(Path(__file__).parent / 'templates')
        self.jinja_env = Environment(loader=ChoiceLoader([package_loader, file_loader]))

    def generate(self, resource_name: Optional[str] = None) -> None:
        self.docs_path.mkdir(exist_ok=True)
        
        resource_files = [self.resources_path / f"{resource_name}.yml"] if resource_name else self._get_all_resources()
        
        for resource_file in resource_files:
            self._generate_resource_doc(resource_file)
        
        self._generate_index()
        print("Documentation generated successfully.")

    def _get_all_resources(self) -> List[Path]:
        return list(self.resources_path.glob('*.yml'))

    def _generate_resource_doc(self, resource_file: Path) -> None:
        data = self._load_yaml(resource_file)
        
        resource_name = data.get('resource_name', 'unknown_resource')
        short_description = data.get('short_description', '')
        long_description_file = data.get('long_description', '')
        
        # Load and render the long description from the markdown file
        long_description_html = self._render_long_description(resource_file.parent / long_description_file)
        
        template = self.jinja_env.get_template(RESOURCE_DOC_TEMPLATE_NAME)
        
        html_content = template.render(
            resource_name=resource_name,
            short_description=short_description,
            long_description_html=long_description_html
        )
        
        doc_file = self.docs_path / f"{resource_name}.html"
        doc_file.write_text(html_content)

    def _render_long_description(self, md_file_path: Path) -> str:
        try:
            with open(md_file_path, 'r') as md_file:
                md_content = md_file.read()
                return markdown.markdown(md_content)
        except FileNotFoundError:
            print(f"Warning: Long description file not found: {md_file_path}")
            return ""
        except Exception as e:
            print(f"Error rendering long description from {md_file_path}: {e}")
            return ""

    def _generate_index(self) -> None:
        resources = [
            {
                'name': data.get('resource_name', 'unknown_resource'),
                'short_description': data.get('short_description', '')
            }
            for resource_file in self._get_all_resources()
            if (data := self._load_yaml(resource_file))
        ]
        
        template = self.jinja_env.get_template(INDEX_TEMPLATE_NAME)
        html_content = template.render(resources=resources)
        
        index_file = self.docs_path / 'index.html'
        index_file.write_text(html_content)

    def serve(self, port: int = 8000) -> None:
        os.chdir(self.docs_path)
        handler = http.server.SimpleHTTPRequestHandler
        with socketserver.TCPServer(("", port), handler) as httpd:
            print(f"Serving documentation on http://localhost:{port}")
            httpd.serve_forever()

    def _load_yaml(self, file_path: Path) -> dict:
        try:
            with open(file_path, 'r') as file:
                data = yaml.safe_load(file) or {}
                return data
        except Exception as e:
            print(f"Error loading YAML file {file_path}: {e}")
            return {}
