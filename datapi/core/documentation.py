import os
import yaml
import glob
import markdown
import jinja2
import http.server
import socketserver

class Documentation:
    def __init__(self, project_path=None):
        self.project_path = project_path or os.getcwd()
        self.resources_path = os.path.join(self.project_path, 'resources')
        self.docs_path = os.path.join(self.project_path, 'docs')

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
        
        template = jinja2.Template('''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{{ resource_name }}</title>
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/water.css@2/out/water.css">
        </head>
        <body>
            <h1>{{ resource_name }}</h1>
            <h2>Short Description</h2>
            <p>{{ short_description }}</p>
            <h2>Long Description</h2>
            {{ long_description_html | safe }}
        </body>
        </html>
        ''')
        
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
        
        template = jinja2.Template('''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Resource Documentation</title>
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/water.css@2/out/water.css">
        </head>
        <body>
            <h1>Resource Documentation</h1>
            <ul>
            {% for resource in resources %}
                <li>
                    <a href="{{ resource.name }}.html">{{ resource.name }}</a>
                    <p>{{ resource.short_description }}</p>
                </li>
            {% endfor %}
            </ul>
        </body>
        </html>
        ''')
        
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
