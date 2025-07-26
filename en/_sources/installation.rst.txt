Installation
============

Requirements
------------

* Python 3.8 or higher
* pyserial >= 3.5 (for RTU transport)

Install from PyPI
-----------------

The easiest way to install ModbusLink is using pip:

.. code-block:: bash

   pip install modbuslink

Install from Source
-------------------

You can also install ModbusLink from the source code:

.. code-block:: bash

   git clone https://github.com/Miraitowa/ModbusLink.git
   cd ModbusLink
   pip install -e .

Development Installation
------------------------

For development, install with additional dependencies:

.. code-block:: bash

   git clone https://github.com/Miraitowa/ModbusLink.git
   cd ModbusLink
   pip install -e ".[dev]"

This will install additional packages for testing and documentation:

* pytest
* pytest-asyncio
* pytest-mock
* sphinx
* sphinx-rtd-theme
* black
* ruff
* mypy

Verify Installation
-------------------

To verify that ModbusLink is installed correctly, run:

.. code-block:: python

   import modbuslink
   print(modbuslink.__version__)

Optional Dependencies
---------------------

For RTU communication over serial ports:

.. code-block:: bash

   pip install pyserial

For documentation building:

.. code-block:: bash

   pip install sphinx sphinx-rtd-theme

For testing:

.. code-block:: bash

   pip install pytest pytest-asyncio pytest-mock

Troubleshooting
---------------

Common Issues
~~~~~~~~~~~~~

**ImportError: No module named 'serial'**

This error occurs when pyserial is not installed. Install it with:

.. code-block:: bash

   pip install pyserial

**Permission denied on serial port (Linux/macOS)**

Add your user to the dialout group:

.. code-block:: bash

   sudo usermod -a -G dialout $USER

Then log out and log back in.

**Windows serial port access issues**

Ensure the serial port is not being used by another application and that you have the correct drivers installed.