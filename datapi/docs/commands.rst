Commands
========

dataPi provides several commands to manage your data pods and documentation. Here's a list of available commands:

Initialize a New Project
------------------------

To create a new dataPi project:

.. code-block:: bash

   datapi init [PROJECT_NAME]

If no project name is specified, it defaults to 'datapi_project'.

Deploy Resources
----------------

Deploy all resources:

.. code-block:: bash

   datapi run --all

Deploy a single resource:

.. code-block:: bash

   datapi run --resource [RESOURCE_NAME]

List Resources
--------------

List all resources:

.. code-block:: bash

   datapi show --all

List a single resource:

.. code-block:: bash

   datapi show --resource [RESOURCE_NAME]

Generate Documentation
----------------------

Generate documentation for all resources:

.. code-block:: bash

   datapi docs generate --all

Generate documentation for a single resource:

.. code-block:: bash

   datapi docs generate --resource [RESOURCE_NAME]

Serve Documentation
-------------------

To serve the generated documentation:

.. code-block:: bash

   datapi docs serve
