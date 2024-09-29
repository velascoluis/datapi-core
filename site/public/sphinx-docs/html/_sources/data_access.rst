Data Access from Applications
=============================

Once you have deployed your dataPods, you can access the data they provide in two ways:

1. Directly through the REST API endpoint
2. Using the Python client SDK included in the dataPi package

REST API Endpoint
-----------------

Each deployed dataPod offers a ``get_data`` endpoint that you can query to retrieve the results. The specific URL for this endpoint will depend on your deployment configuration.

Python Client SDK
-----------------

dataPi provides a Python client SDK that simplifies the process of accessing data from your applications. Here's an example of how to use it:

.. code-block:: python

    from datapi import Client

    # Initialize the client
    client = Client(project_id=project_id, region=region, resource_name=resource_name)

    # List available services
    services = client.list_services()
    print("Available services:")
    for resource, url in services.items():
        print(f"- {resource}: {url}")

    # Get data from a specific resource
    data = client.get_data()
    print("Data from example_resource:", data)

Client Initialization
^^^^^^^^^^^^^^^^^^^^^

To initialize the client, you need to provide:

- ``project_id``: The ID of your Google Cloud project
- ``region``: The region where your dataPods are deployed
- ``resource_name``: The name of the specific resource you want to access

Available Methods
^^^^^^^^^^^^^^^^^

The Client class provides the following methods:

1. ``list_services()``: Returns a dictionary of available services and their URLs.
2. ``get_data()``: Retrieves the data from the specified resource.

Error Handling
--------------

When using the Python client SDK, make sure to implement proper error handling. The SDK may raise exceptions in case of network errors, authentication issues, or if the requested resource is not available.

Security Considerations
-----------------------

When accessing data from your applications, ensure that:

1. You're using secure communication protocols (HTTPS).
2. Your application has the necessary permissions to access the dataPod endpoints.
3. You're not exposing sensitive information (like project IDs or credentials) in client-side code.

Next Steps
----------

For more advanced usage and configuration options, refer to the detailed API documentation of the Python client SDK.
