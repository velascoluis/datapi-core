from datapi.sdk.client import Client

def main():
    # Create a Client instance
    client = Client(project_id="velascoluis-dev-sandbox", region="us-central1", resource_name="sample-resource")

    # List all available services
    services = client.list_services()
    
    print("Available services:")
    for resource, url in services.items():
        print(f"- {resource}: {url}")

    data = client.get_data()
    print("Data from example_resource:", data)

if __name__ == "__main__":
    main()
