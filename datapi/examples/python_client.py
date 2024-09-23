from datapi.sdk.client import Client
import argparse


def main(project_id, region, resource_name):

    client = Client(project_id=project_id, region=region, resource_name=resource_name)

    services = client.list_services()

    print("Available services:")
    for resource, url in services.items():
        print(f"- {resource}: {url}")

    data = client.get_data()
    print("Data from example_resource:", data)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Python client for datapi")
    parser.add_argument("--project_id", required=True, help="Project ID")
    parser.add_argument("--region", required=True, help="Region")
    parser.add_argument("--resource_name", required=True, help="Resource name")

    args = parser.parse_args()
    main(args.project_id, args.region, args.resource_name)
