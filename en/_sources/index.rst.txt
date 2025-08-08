ModbusLink Documentation
========================

Welcome to ModbusLink's documentation!

ModbusLink is a modern, powerful, developer-friendly and highly extensible Python Modbus library that supports both synchronous and asynchronous operations with unparalleled ease of use and debugging experience.

.. toctree::
   :maxdepth: 2
   :caption: Contents:
   :hidden:

   installation
   quickstart
   user_guide
   api_reference
   examples

Documentation Sections
======================

.. grid:: 2
   :gutter: 3

   .. grid-item-card:: 🚀 Quick Start
      :link: quickstart
      :link-type: doc

      Get up and running with ModbusLink in minutes. Learn the basics and see your first Modbus communication.

   .. grid-item-card:: 📖 User Guide
      :link: user_guide
      :link-type: doc

      Comprehensive guide covering all features, from basic operations to advanced configurations.

   .. grid-item-card:: 📚 API Reference
      :link: api_reference
      :link-type: doc

      Complete API documentation with detailed class and method descriptions.

   .. grid-item-card:: 💡 Examples
      :link: examples
      :link-type: doc

      Real-world examples and integration patterns for various use cases.
   advanced_topics
   changelog

Key Features
============

* **Layered Architecture**: Strict separation of transport layer, client layer, and utility layer
* **Interface-Oriented Programming**: Using Abstract Base Classes (ABC) for unified interfaces
* **Dependency Injection**: Clients receive transport layer instances through constructors
* **User-Friendly API**: All external interfaces use Python native data types
* **Synchronous Support**: Complete synchronous Modbus client implementation
* **Multiple Transport Methods**: Support for RTU and TCP transport layers
* **Advanced Data Types**: Support for float32, int32, uint32, int64, and string operations
* **Unified Logging System**: Comprehensive logging for debugging and monitoring
* **Asynchronous Support**: Native async/await support for high-concurrency scenarios
* **Callback Mechanism**: Request completion notifications through callback functions
* **Modbus Slave Simulator**: Built-in slave simulator for testing client functionality

Supported Function Codes
========================

* **0x01**: Read Coils
* **0x02**: Read Discrete Inputs
* **0x03**: Read Holding Registers
* **0x04**: Read Input Registers
* **0x05**: Write Single Coil
* **0x06**: Write Single Register
* **0x0F**: Write Multiple Coils
* **0x10**: Write Multiple Registers

Quick Start
===========

Synchronous TCP Example
-----------------------

.. code-block:: python

   from modbuslink import ModbusClient, TcpTransport

   # Create TCP transport
   transport = TcpTransport(host='192.168.1.100', port=502, timeout=10.0)

   # Create client
   client = ModbusClient(transport)

   try:
       # Connect
       client.connect()
       
       # Read holding registers
       registers = client.read_holding_registers(
           slave_id=1,
           start_address=0,
           quantity=10
       )
       print(f"Registers: {registers}")
       
       # Write single register
       client.write_single_register(
           slave_id=1,
           address=0,
           value=1234
       )
       
   finally:
       client.disconnect()

Asynchronous TCP Example
------------------------

.. code-block:: python

   from modbuslink import AsyncModbusClient, AsyncTcpTransport
   import asyncio

   async def main():
       # Create async TCP transport
       transport = AsyncTcpTransport(
           host='192.168.1.100',
           port=502,
           timeout=10.0
       )

       # Create async client
       client = AsyncModbusClient(transport)

       async with client:
           # Read holding registers
           registers = await client.read_holding_registers(
               slave_id=1,
               start_address=0,
               quantity=10
           )
           print(f"Registers: {registers}")

   asyncio.run(main())

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`