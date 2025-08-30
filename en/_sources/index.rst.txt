ModbusLink Documentation
========================

.. image:: https://img.shields.io/pypi/v/modbuslink.svg
   :target: https://pypi.org/project/modbuslink/
   :alt: PyPI Version

.. image:: https://img.shields.io/pypi/pyversions/modbuslink.svg
   :target: https://pypi.org/project/modbuslink/
   :alt: Python Version

.. image:: https://img.shields.io/github/license/Miraitowa-la/ModbusLink
   :target: https://github.com/Miraitowa-la/ModbusLink/blob/main/LICENSE.txt
   :alt: License

Welcome to ModbusLink's documentation!

ModbusLink is a **modern, high-performance Python Modbus library** designed for industrial automation, IoT applications, and SCADA systems. Built with modern Python practices, it provides unparalleled ease of use while maintaining enterprise-grade reliability.

.. toctree::
   :maxdepth: 2
   :caption: Getting Started
   :hidden:

   installation
   quickstart
   architecture

.. toctree::
   :maxdepth: 2
   :caption: User Guide
   :hidden:

   user_guide
   advanced_guide
   performance
   production

.. toctree::
   :maxdepth: 2
   :caption: Examples & Practices
   :hidden:

   examples
   best_practices
   troubleshooting

.. toctree::
   :maxdepth: 2
   :caption: API Documentation
   :hidden:

   api_reference

.. toctree::
   :maxdepth: 1
   :caption: Others
   :hidden:

   changelog
   contributing

Documentation Sections
======================

New to ModbusLink?
------------------

.. grid:: 2
   :gutter: 3

   .. grid-item-card:: ⚡ 30-Second Demo
      :link: quickstart
      :link-type: doc
      :class-card: quickstart-card

      Get up and running with ModbusLink in minutes. Learn the basics and see your first Modbus communication.

   .. grid-item-card:: 🛠️ Installation Guide
      :link: installation
      :link-type: doc
      :class-card: install-card

      Detailed installation guide including system requirements, dependencies, and environment setup.

Core Features
-------------

.. grid:: 3
   :gutter: 3

   .. grid-item-card:: 📖 User Guide
      :link: user_guide
      :link-type: doc
      :class-card: guide-card

      Comprehensive guide covering all features, from basic operations to advanced configurations.

   .. grid-item-card:: 🏗️ Architecture Design
      :link: architecture
      :link-type: doc
      :class-card: arch-card

      Deep dive into ModbusLink's layered architecture and design principles.

   .. grid-item-card:: 📚 API Reference
      :link: api_reference
      :link-type: doc
      :class-card: api-card

      Complete API documentation with detailed class and method descriptions.

Real-World Applications
----------------------

.. grid:: 3
   :gutter: 3

   .. grid-item-card:: 💡 Code Examples
      :link: examples
      :link-type: doc
      :class-card: example-card

      Rich collection of real-world examples covering various industrial application scenarios.

   .. grid-item-card:: ⚡ Performance Tuning
      :link: performance
      :link-type: doc
      :class-card: perf-card

      Performance optimization techniques and concurrent processing best practices.

   .. grid-item-card:: 🔧 Troubleshooting
      :link: troubleshooting
      :link-type: doc
      :class-card: trouble-card

      Common issues solutions and debugging techniques.

Key Features
============

.. list-table:: ModbusLink Core Features
   :widths: 20 40 40
   :header-rows: 1

   * - Feature
     - Description
     - Benefit
   * - 🏗️ **Layered Architecture**
     - Clean separation of concerns
     - Easy maintenance & extension
   * - 🔌 **Universal Transports**
     - TCP, RTU, ASCII support
     - Works with any Modbus device
   * - ⚡ **Async Performance**
     - Native asyncio support
     - Handle 1000+ concurrent connections
   * - 🛠️ **Developer Experience**
     - Intuitive APIs & full typing
     - Faster development & fewer bugs
   * - 📊 **Rich Data Types**
     - float32, int32, strings & more
     - Handle complex industrial data
   * - 🔍 **Advanced Debugging**
     - Protocol-level monitoring
     - Rapid troubleshooting
   * - 🖥️ **Complete Server**
     - Full server implementation
     - Build custom Modbus devices
   * - 🎯 **Production Ready**
     - Comprehensive error handling
     - Deploy with confidence

Supported Modbus Function Codes
================================

.. list-table:: 
   :widths: 15 25 60
   :header-rows: 1

   * - Function Code
     - Function Name
     - Description
   * - **0x01**
     - Read Coils
     - Read status of one or more coils (boolean values)
   * - **0x02**
     - Read Discrete Inputs
     - Read status of one or more discrete inputs (read-only boolean values)
   * - **0x03**
     - Read Holding Registers
     - Read values of one or more holding registers (16-bit integers)
   * - **0x04**
     - Read Input Registers
     - Read values of one or more input registers (read-only 16-bit integers)
   * - **0x05**
     - Write Single Coil
     - Write a single coil value to specified address
   * - **0x06**
     - Write Single Register
     - Write a single register value to specified address
   * - **0x0F**
     - Write Multiple Coils
     - Write multiple coil values to consecutive addresses
   * - **0x10**
     - Write Multiple Registers
     - Write multiple register values to consecutive addresses

30-Second Demo
==============

Install ModbusLink
------------------

.. code-block:: bash

   # Install from PyPI
   pip install modbuslink

Simple Examples
---------------

**TCP Client (Ethernet Devices)**

.. code-block:: python

   from modbuslink import ModbusClient, TcpTransport

   # Connect to Modbus TCP device
   transport = TcpTransport(host='192.168.1.100', port=502)
   client = ModbusClient(transport)

   with client:
       # Read temperature sensor
       temp = client.read_float32(slave_id=1, start_address=100)
       print(f"Temperature: {temp:.1f}°C")
       
       # Control pump switch
       client.write_single_coil(slave_id=1, address=0, value=True)
       print("Pump started!")

**Serial Client (RTU Devices)**

.. code-block:: python

   from modbuslink import ModbusClient, RtuTransport

   # Connect to serial device
   transport = RtuTransport(port='COM3', baudrate=9600)
   client = ModbusClient(transport)

   with client:
       # Read flow meter data
       flow = client.read_float32(slave_id=5, start_address=0)
       print(f"Flow rate: {flow:.2f} L/min")

**High-Performance Async Operations**

.. code-block:: python

   import asyncio
   from modbuslink import AsyncModbusClient, AsyncTcpTransport

   async def read_multiple_plcs():
       """Read from multiple PLCs concurrently"""
       plc1 = AsyncModbusClient(AsyncTcpTransport('192.168.1.10', 502))
       plc2 = AsyncModbusClient(AsyncTcpTransport('192.168.1.11', 502))
       
       async with plc1, plc2:
           # Concurrent reading
           results = await asyncio.gather(
               plc1.read_holding_registers(1, 0, 10),
               plc2.read_holding_registers(1, 0, 10)
           )
           print(f"PLC1: {results[0]}, PLC2: {results[1]}")

   asyncio.run(read_multiple_plcs())

Get Started Now
---------------

🚀 Ready to dive in? Head to :doc:`installation` to install ModbusLink, then check out :doc:`quickstart` for a detailed tutorial!

Community and Support
=====================

.. grid:: 2
   :gutter: 3

   .. grid-item-card:: 📖 GitHub Project
      :link: https://github.com/Miraitowa-la/ModbusLink
      :link-type: url

      Source code, issue reports, and feature requests

   .. grid-item-card:: 📦 PyPI Package
      :link: https://pypi.org/project/modbuslink/
      :link-type: url

      Official releases and version history

Version Information
===================

.. include:: ../CHANGELOG.md
   :parser: myst_parser.sphinx_

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`