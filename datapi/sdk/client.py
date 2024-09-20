import pandas as pd
import requests
import os
import yaml
from google.cloud import run_v2
from google.auth import default

class Client:
    def __init__(self, project_id, region, resource_name):
        self.project_id = project_id
        self.region = region
        self.resource_name = resource_name
        self.service_url = self._get_service_url()

    def _get_service_url(self):
        # Use the list_services method to get the correct URL for the resource
        services = self.list_services()
        if self.resource_name in services:
            return services[self.resource_name]
        else:
            raise ValueError(f"Service URL for resource '{self.resource_name}' not found.")

    def get_data(self):
        try:
            response = requests.get(f"{self.service_url}/get_data")
            response.raise_for_status()
            data = response.json()
            return pd.DataFrame(data)
        except requests.RequestException as e:
            raise Exception(f"Error fetching data: {str(e)}")

    def list_services(self):
        # Authenticate and create a Cloud Run client
        credentials, project = default()
        client = run_v2.ServicesClient(credentials=credentials)

        # Get the parent resource name
        parent = f"projects/{self.project_id}/locations/{self.region}"

        try:
            # List services
            response = client.list_services(parent=parent)
            
            for service in response:
                # Extract the resource name (last part of the full name)
                resource_name = service.name.split('/')[-1]
                # Remove the '-service' suffix if present
                resource_name = resource_name[:-8] if resource_name.endswith('-service') else resource_name
                
                if resource_name == self.resource_name:
                    return {resource_name: service.uri}
            
            # If the resource is not found, return an empty dictionary
            return {}

        except Exception as e:
            raise Exception(f"Error listing Cloud Run services: {str(e)}")
