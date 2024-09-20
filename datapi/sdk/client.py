import pandas as pd
import requests
from datapi.core.runner import Runner

class Client:
    def __init__(self, resource):
        self.runner = Runner()

    def _get_service_url(self, resource):
        runner = Runner()
        status = runner.show_all()
        resource_info = status['resources'].get(resource)
        
        if not resource_info:
            raise ValueError(f"Resource '{resource}' not found")
        
        service_status = resource_info['service_status']
        
        if isinstance(service_status, str) and service_status.startswith('http'):
            return service_status
        else:
            raise ValueError(f"Service URL not available for resource '{resource}'")
    
    def get_data(resource, self):
        try:
            url = self._get_service_url(resource)
            response = requests.get(f"{url}/get_data")
            response.raise_for_status()
            data = response.json()
            return pd.DataFrame(data)
        except requests.RequestException as e:
            raise Exception(f"Error fetching data: {str(e)}")

    def list_services(self):
        status = self.runner.show_all()
        services = {}
        for resource, info in status['resources'].items():
            service_status = info['service_status']
            if isinstance(service_status, str) and service_status.startswith('http'):
                services[resource] = service_status
        return services

from .client import Client
