import os
import yaml
import glob
import markdown
from jinja2 import Environment, FileSystemLoader, ChoiceLoader, PackageLoader
import http.server
import socketserver

RESOURCE_DOC_TEMPLATE_NAME = "resource_doc.html.jinja2"
INDEX_TEMPLATE_NAME = "index.html.jinja2"


class Documentation:
    def __init__(self, project_path=None):
        self.project_path = project_path or os.getcwd()
        self.resources_path = os.path.join(self.project_path, 'resources')
        self.docs_path = os.path.join(self.project_path, 'docs')

        package_loader = PackageLoader('datapi.core', 'templates')
        file_loader = FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates'))
        self.jinja_env = Environment(loader=ChoiceLoader([package_loader, file_loader]))

    def generate(self, resource_name=None):
        if not os.path.exists(self.docs_path):
            os.makedirs(self.docs_path)
        
        if resource_name:
            resource_files = [os.path.join(self.resources_path, f"{resource_name}.yml")]
        else:
            resource_files = self._get_all_resources()
        
        for resource_file in resource_files:
            self._generate_resource_doc(resource_file)
        
        self._generate_index()
        print("Documentation generated successfully.")

    def _get_all_resources(self):
        return glob.glob(os.path.join(self.resources_path, '*.yml'))

    def _generate_resource_doc(self, resource_file):
        with open(resource_file, 'r') as file:
            data = yaml.safe_load(file)
        
        resource_name = data.get('resource_name', 'unknown_resource')
        short_description = data.get('short_description', '')
        long_description = data.get('long_description', '')
        
        template = self.jinja_env.get_template(RESOURCE_DOC_TEMPLATE_NAME)
        
        html_content = template.render(
            resource_name=resource_name,
            short_description=short_description,
            long_description_html=markdown.markdown(long_description)
        )
        
        doc_file = os.path.join(self.docs_path, f"{resource_name}.html")
        with open(doc_file, 'w') as f:
            f.write(html_content)

    def _generate_index(self):
        resources = []
        for resource_file in self._get_all_resources():
            with open(resource_file, 'r') as file:
                data = yaml.safe_load(file)
            resources.append({
                'name': data.get('resource_name', 'unknown_resource'),
                'short_description': data.get('short_description', '')
            })
        
        template = self.jinja_env.get_template(INDEX_TEMPLATE_NAME)
        
        html_content = template.render(resources=resources)
        
        index_file = os.path.join(self.docs_path, 'index.html')
        with open(index_file, 'w') as f:
            f.write(html_content)

    def serve(self, port=8000):
        os.chdir(self.docs_path)
        handler = http.server.SimpleHTTPRequestHandler
        with socketserver.TCPServer(("", port), handler) as httpd:
            print(f"Serving documentation on http://localhost:{port}")
            httpd.serve_forever()
