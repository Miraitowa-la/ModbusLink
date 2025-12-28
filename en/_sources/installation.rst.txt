Installation Guide
==================

.. contents:: Table of Contents
   :local:
   :depth: 2

System Requirements
-------------------

Basic Requirements
~~~~~~~~~~~~~~~~~

.. list-table:: 
   :widths: 20 80
   :header-rows: 1

   * - Component
     - Requirement
   * - **Python Version**
     - Python 3.9+ (Recommended 3.11+)
   * - **Operating System**
     - Windows 10+, Linux (Ubuntu 18.04+), macOS 10.15+
   * - **Memory**
     - Minimum 100MB RAM
   * - **Storage**
     - Approximately 10MB disk space

Dependencies
~~~~~~~~~~~~

**Required Dependencies**

- **Python Standard Library**: asyncio, threading, struct, socket
- **No External Dependencies**: Core functionality requires no additional packages

**Optional Dependencies**

.. code-block:: bash

   # Serial communication support (RTU/ASCII)
   pip install pyserial>=3.5
   
   # Async serial support
   pip install pyserial-asyncio>=0.6
   
   # Development tools
   pip install pytest>=7.0 black>=22.0 ruff>=0.1.0

Quick Installation
------------------

Install from PyPI (Recommended)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Basic installation
   pip install modbuslink
   
   # Include serial support
   pip install modbuslink[serial]
   
   # Include development dependencies
   pip install modbuslink[dev]
   
   # Complete installation (all features)
   pip install modbuslink[all]

.. note::
   
   If you only need TCP functionality, the basic installation is sufficient. Serial functionality requires the ``pyserial`` dependency.

Verify Installation
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import modbuslink
   print(f"ModbusLink version: {modbuslink.__version__}")
   
   # Check available components
   from modbuslink import ModbusClient, TcpTransport
   print("✅ TCP functionality available")
   
   try:
       from modbuslink import RtuTransport
       print("✅ RTU functionality available")
   except ImportError:
       print("❌ RTU functionality unavailable - need to install pyserial")

Advanced Installation
---------------------

Install from Source
~~~~~~~~~~~~~~~~~~

**Developer Installation**

.. code-block:: bash

   # Clone repository
   git clone https://github.com/Miraitowa-la/ModbusLink.git
   cd ModbusLink
   
   # Create virtual environment
   python -m venv venv
   
   # Activate virtual environment
   # Windows:
   venv\Scripts\activate
   # Linux/macOS:
   source venv/bin/activate
   
   # Install as editable package
   pip install -e ".[dev]"

**Specific Version Installation**

.. code-block:: bash

   # Install specific version
   pip install modbuslink==1.0.0
   
   # Install pre-release version
   pip install --pre modbuslink
   
   # Install latest from GitHub
   pip install git+https://github.com/Miraitowa-la/ModbusLink.git

Docker Installation
~~~~~~~~~~~~~~~~~~

.. code-block:: dockerfile

   # Dockerfile example
   FROM python:3.11-slim
   
   # Install ModbusLink
   RUN pip install modbuslink[all]
   
   # Copy application code
   COPY . /app
   WORKDIR /app
   
   # Run application
   CMD ["python", "your_modbus_app.py"]

Environment Configuration
-------------------------

Serial Port Permissions (Linux/macOS)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Ubuntu/Debian**

.. code-block:: bash

   # Add user to dialout group
   sudo usermod -a -G dialout $USER
   
   # Restart session to apply permissions
   # Or temporarily switch group
   newgrp dialout
   
   # View serial port devices
   ls -la /dev/ttyUSB* /dev/ttyACM*

**CentOS/RHEL**

.. code-block:: bash

   # Add user to uucp group
   sudo usermod -a -G uucp $USER
   
   # Restart session

**macOS**

.. code-block:: bash

   # View available serial ports
   ls /dev/cu.*
   
   # Usually no special permissions needed

Windows Serial Port Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. **Check Device Manager** for port information
2. **Confirm COM port number** (e.g., COM1, COM3)
3. **Verify driver installation** is correct
4. **Firewall settings**: Ensure Python applications have network permissions (for TCP functionality)

Troubleshooting
---------------

Common Installation Issues
~~~~~~~~~~~~~~~~~~~~~~~~~

**ImportError: No module named 'serial'**

.. code-block:: bash

   # Solution: Install pyserial
   pip install pyserial

**Permission denied on serial port**

.. code-block:: bash

   # Linux solution
   sudo chmod 666 /dev/ttyUSB0  # Temporary solution
   sudo usermod -a -G dialout $USER  # Permanent solution

**ModuleNotFoundError: No module named 'modbuslink'**

.. code-block:: bash

   # Check installation status
   pip list | grep modbuslink
   
   # Reinstall
   pip uninstall modbuslink
   pip install modbuslink

**Version Conflicts**

.. code-block:: bash

   # Create clean virtual environment
   python -m venv clean_env
   source clean_env/bin/activate  # Linux/macOS
   clean_env\Scripts\activate     # Windows
   pip install modbuslink

Serial Port Diagnostics
~~~~~~~~~~~~~~~~~~~~~~~

**Check Serial Port Availability**

.. code-block:: python

   import serial.tools.list_ports
   
   # List all serial ports
   ports = serial.tools.list_ports.comports()
   for port in ports:
       print(f"Port: {port.device}, Description: {port.description}")

**Test Serial Port Connection**

.. code-block:: python

   import serial
   
   try:
       ser = serial.Serial('COM3', 9600, timeout=1)  # Windows
       # ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)  # Linux
       print("✅ Serial port connection successful")
       ser.close()
   except Exception as e:
       print(f"❌ Serial port connection failed: {e}")

Network Diagnostics
~~~~~~~~~~~~~~~~~~~

**Test TCP Connection**

.. code-block:: python

   import socket
   
   def test_tcp_connection(host, port, timeout=5):
       try:
           sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
           sock.settimeout(timeout)
           result = sock.connect_ex((host, port))
           sock.close()
           return result == 0
       except Exception:
           return False
   
   if test_tcp_connection('192.168.1.100', 502):
       print("✅ TCP connection normal")
   else:
       print("❌ TCP connection failed")

Performance Tuning
------------------

Production Environment Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Recommended production environment configuration
   import asyncio
   from modbuslink import AsyncModbusClient, AsyncTcpTransport
   
   # Connection pool configuration
   transport = AsyncTcpTransport(
       host='192.168.1.100',
       port=502,
       timeout=5.0,           # Moderate timeout
       connect_timeout=3.0,   # Connection timeout
       keepalive=True         # Keep connection alive
   )
   
   # Async event loop optimization
   if hasattr(asyncio, 'WindowsSelectorEventLoopPolicy'):
       # Windows optimization
       asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

Memory Optimization
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # For large data reads, use batch operations
   registers = await client.read_holding_registers(
       slave_id=1, 
       start_address=0, 
       quantity=100  # Read multiple registers at once
   )
   
   # Avoid frequent client object creation
   # Use connection pools or long connections

Upgrade Guide
-------------

Upgrading from Older Versions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Check current version
   pip show modbuslink
   
   # Upgrade to latest version
   pip install --upgrade modbuslink
   
   # Upgrade to specific version
   pip install --upgrade modbuslink==2.0.0

.. warning::
   
   Before upgrading, please check :doc:`changelog` for breaking changes.

Next Steps
----------

After installation, we recommend:

1. 📖 Read :doc:`quickstart` for a quick start guide
2. 🏗️ Understand :doc:`architecture` design
3. 💡 Check :doc:`examples` for real examples
4. 📚 Reference :doc:`api_reference` for API documentation

If you encounter issues, please check :doc:`troubleshooting` or submit an issue on GitHub.