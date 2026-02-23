Installation Guide
==================

1. System Requirements
----------------------

1.1 Basic Requirements
~~~~~~~~~~~~~~~~~~~~~~

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

1.2 Dependencies
~~~~~~~~~~~~~~~~

- **Python Standard Library**: asyncio, threading, struct, socket
- **External Dependencies**: pyserial, pyserial-asyncio, typing_extensions

2. Quick Installation
---------------------

2.1 Install from PyPI (Recommended)
~~~~~~~~~~~~~~~~~~

**Latest Version Installation**

.. code-block:: bash

   # Basic installation
   pip install modbuslink

**Specific Version Installation**

.. code-block:: bash

   # Install specific version
   pip install modbuslink==1.4.0

2.2 Install from Source
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Clone repository
   git clone https://github.com/Miraitowa-la/ModbusLink.git
   cd ModbusLink

   # Create virtual environment...

   # Install as editable package
   pip install -e .

2.3 Verify Installation
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import modbuslink
   print(f"ModbusLink version: {modbuslink.__version__}")

   from modbuslink import SyncTcpTransport
   print("✅ TCP functionality available")

   from modbuslink import SyncRtuTransport
   print("✅ RTU functionality available")

   from modbuslink import SyncAsciiTransport
   print("✅ ASCII functionality available")

3. Environment Configuration
----------------------------

3.1 Serial Port Permissions (Linux/macOS)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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

3.2 Windows Serial Port Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. **Check Device Manager** for port information
2. **Confirm COM port number** (e.g., COM1, COM3)
3. **Verify driver installation** is correct
4. **Firewall settings** Ensure Python applications have network permissions (for TCP functionality)

4. Troubleshooting
------------------

4.1 Common Installation Issues
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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

4.2 Serial Port Diagnostics
~~~~~~~~~~~~~~~~~~~~~~~~~~~

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

4.3 Network Diagnostics
~~~~~~~~~~~~~~~~~~~~~~~

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

5. Performance Tuning
---------------------

5.1 Timeout Settings
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from modbuslink import AsyncTcpTransport

   transport = AsyncTcpTransport(
       host='192.168.1.100',
       port=502,
       timeout=5.0  # Moderate timeout
   )

5.2 Memory Optimization
~~~~~~~~

.. code-block:: python

   # For large data reads, use batch operations
   registers = await client.read_holding_registers(
       slave_id=1, 
       start_address=0, 
       quantity=100  # Read multiple registers at once
   )

6. Upgrade Guide
--------

6.1 Upgrading from Older Versions
~~~~~~~~~~~~

.. code-block:: bash

   # Check current version
   pip show modbuslink
   
   # Upgrade to latest version
   pip install --upgrade modbuslink
   
   # Upgrade to specific version
   pip install --upgrade modbuslink==2.0.0

.. warning::
   
   Before upgrading, please check :doc:`changelog` for breaking changes.

7. Next Steps
-------------

After installation, we recommend:

1. 📖 Read :doc:`quickstart` for a quick start guide
2. 🏗️ Understand :doc:`architecture` design
3. 💡 Check :doc:`examples` for real examples
4. 📚 Reference :doc:`api_reference` for API documentation

If you encounter issues, please check :doc:`troubleshooting` or submit an issue on GitHub.