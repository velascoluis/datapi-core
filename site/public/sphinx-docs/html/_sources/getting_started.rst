Getting Started with dataPi
===========================

dataPi is a Python package that allows you to implement a distributed datalakehouse head made of data pods. This guide will help you get started with dataPi.

Installation
------------

To install dataPi from source:

1. Clone the repository
2. Run the following command:

   .. code-block:: bash

      pip install .

Initializing a New Project
--------------------------

To create a new dataPi project, run:

.. code-block:: bash

   datapi init [PROJECT_NAME]

If you don't specify a project name, it will default to 'datapi_project'.

This will create a project structure like this:

.. code-block:: bash

   datapi_project
      - config.yml
      - resources
      - - sample_resources.yml
      - deployments/
      - docs/

Configuration
-------------

The `config.yml` file should contain your dataPi general configuration. Here's an example:

.. code-block:: yaml

   # datapi configuration file

   metastore_type: POLARIS
   metastore_uri: 'METASTORE_URI/api/catalog'
   metastore_credentials: 'CLIENT_ID:CLIENT_SECRET'
   metastore_catalog: 'METASTORE_CATALOG_NAME'

   # datapi datapods - Deployment settings
   deployment:
     deployment_target: GCP_CLOUD_RUN
     build_service: GCP_CLOUD_BUILD
     project_id: GCP_PROJECT_ID
     registry_url: REGISTRY_URL
     region: GCP_REGION

Defining Resources
------------------

You can define your dataPods specs under the `resources` folder. Here are examples of reduction and projection resources:

Reduction Resource:

.. code-block:: yaml

   resource_name: RESOURCE_NAME
   type: REST
   depends_on:
       - namespace: METASTORE_NAMESPACE_NAME
         table: METASTORE_ICEBERG_TABLE_NAME
   local_engine: duckdb
   short_description: This a sample query
   long_description: long-desc.md
   operation_type: REDUCTION
   aggregate: sales.sum()
   group_by: quarter
   filters: region = 'EMEA'
   deploy: True 

Projection Resource:

.. code-block:: yaml

   resource_name: RESOURCE_NAME
   type: REST
   depends_on:
       - namespace: METASTORE_NAMESPACE_NAME
         table: METASTORE_ICEBERG_TABLE_NAME
   local_engine: duckdb
   short_description: This a sample query
   long_description: long-desc.md
   operation_type: PROJECTION
   select: sales quarter region
   filters: region = 'EMEA'
   deploy: True 

Resources can depend on Iceberg tables registered on the catalog, or on another existing (and deployed) data resources:

.. code-block:: yaml
    
   depends_on:
       - resource: RESOURCE_NAME
         

Basic Commands
--------------

Here are some basic commands to get you started:

- Deploy all resources:

  .. code-block:: bash

     datapi run --all

- Deploy a single resource:

  .. code-block:: bash

     datapi run --resource [RESOURCE_NAME]

- List all resources:

  .. code-block:: bash

     datapi show --all

- List one resource:

  .. code-block:: bash

     datapi show --resource [RESOURCE_NAME]

- Generate documentation for all resources:

  .. code-block:: bash

     datapi docs generate --all

- Serve documentation:

  .. code-block:: bash

     datapi docs serve

Using the Python Client SDK
---------------------------

You can use the included Python client SDK to access data from your application:

.. code-block:: python

   client = Client(project_id=project_id, region=region, resource_name=resource_name)
   services = client.list_services()
   print("Available services:")
   for resource, url in services.items():
       print(f"- {resource}: {url}")

   data = client.get_data()
   print("Data from example_resource:", data)

For more detailed information, please refer to the full documentation.
