.. _ref_admin_install:

============
Installation
============

To install EdgeDB, first install EdgeDB's command line tool.

**Linux or macOS**

.. code-block:: bash

    $ curl --proto '=https' -sSf1 https://sh.edgedb.com | sh

**Windows Powershell**

.. code-block:: bash

    $ iwr https://ps1.edgedb.com -useb | iex

.. note::

    The `Install page <edgedb.com/install>`Alternatively, you can install ``edgedb-cli`` using a supported package
manager as described on the `Downloads <https://www.edgedb.com/download/>`_
page under the "Other Installation Options" section.


Server installation
===================

Once the ``edgedb`` command-line tool is installed, use the following command
to install the latest EdgeDB server release:

.. code-block:: bash

    $ edgedb server install

Refer to the command manual page for more information and installation options
(``edgedb server install --help``).
