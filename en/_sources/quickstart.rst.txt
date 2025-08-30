Quick Start
===========

.. contents:: Table of Contents
   :local:
   :depth: 2

Welcome to ModbusLink! This guide will help you master ModbusLink's core features in **5 minutes**.

.. tip::
   
   Before starting, ensure ModbusLink is properly installed. If not, please refer to :doc:`installation`.

Basic Concepts
--------------

ModbusLink uses a simple layered architecture with just two steps:

1. **Create Transport Layer** - Handle low-level communication (TCP, RTU, ASCII)
2. **Create Client** - Provide high-level Modbus operations

30-Second Demo
==============

.. code-block:: python

   from modbuslink import ModbusClient, TcpTransport

   # Connect to Modbus TCP device
   transport = TcpTransport(host='192.168.1.100', port=502)
   client = ModbusClient(transport)

   with client:
       # Read temperature sensor (float32 format)
       temp = client.read_float32(slave_id=1, start_address=100)
       print(f"Current temperature: {temp:.1f}°C")
       
       # Control pump switch
       client.write_single_coil(slave_id=1, address=0, value=True)
       print("Pump started!")

Main Transport Methods
======================

TCP Transport (Ethernet)
------------------------

**Use Cases**: PLCs, HMIs, Ethernet modules

.. code-block:: python

   from modbuslink import ModbusClient, TcpTransport

   transport = TcpTransport(
       host='192.168.1.10',    # PLC IP address
       port=502,               # Standard Modbus TCP port
       timeout=5.0             # 5-second timeout
   )
   client = ModbusClient(transport)
   
   with client:
       # Read production counter
       counter = client.read_int32(slave_id=1, start_address=1000)
       print(f"Production count: {counter}")
       
       # Update setpoint
       client.write_float32(slave_id=1, start_address=3000, value=75.5)

RTU Transport (Serial)
----------------------

**Use Cases**: Field instruments, sensors, legacy devices

.. code-block:: python

   from modbuslink import ModbusClient, RtuTransport

   transport = RtuTransport(
       port='COM3',            # Windows: COM3, Linux: /dev/ttyUSB0
       baudrate=9600,
       parity='N',
       stopbits=1,
       timeout=2.0
   )
   client = ModbusClient(transport)
   
   with client:
       # Read flow meter
       flow_rate = client.read_float32(slave_id=5, start_address=0)
       print(f"Flow rate: {flow_rate:.2f} L/min")

Advanced Data Types
===================

ModbusLink provides built-in support for advanced data types:

.. code-block:: python

   with client:
       # 32-bit floating point (IEEE 754)
       temperature = client.read_float32(slave_id=1, start_address=100)
       client.write_float32(slave_id=1, start_address=100, value=25.6)
       
       # 32-bit integers
       counter = client.read_int32(slave_id=1, start_address=200)
       client.write_int32(slave_id=1, start_address=200, value=12345)
       
       # Strings (UTF-8 encoding)
       device_name = client.read_string(slave_id=1, start_address=400, length=16)
       client.write_string(slave_id=1, start_address=400, value="PLC-001")

High-Performance Async Operations
=================================

For applications handling multiple devices, use async operations:

.. code-block:: python

   import asyncio
   from modbuslink import AsyncModbusClient, AsyncTcpTransport

   async def read_multiple_plcs():
       # Create connections to different PLCs
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

Local Testing Environment
=========================

If you don't have actual Modbus devices, you can use ModbusLink's built-in server simulator:

.. code-block:: python

   # Run simulation server
   import asyncio
   from modbuslink import AsyncTcpModbusServer, ModbusDataStore

   async def run_test_server():
       data_store = ModbusDataStore()
       server = AsyncTcpModbusServer(
           data_store=data_store,
           host='127.0.0.1',
           port=5020
       )
       print("Simulation server started, listening on 127.0.0.1:5020")
       await server.serve_forever()

   asyncio.run(run_test_server())

Error Handling
==============

.. code-block:: python

   from modbuslink import (
       ModbusClient, TcpTransport,
       ConnectionError, TimeoutError
   )

   try:
       with client:
           registers = client.read_holding_registers(1, 0, 10)
   except ConnectionError:
       print("Connection failed, check network and IP address")
   except TimeoutError:
       print("Timeout, check device status")

Next Steps
==========

Congratulations on completing the tutorial! Next you can:

1. 📖 Read :doc:`user_guide` to understand all features comprehensively
2. 🏗️ Learn :doc:`architecture` design
3. 💡 Check :doc:`examples` for more real examples
4. 📚 Reference :doc:`api_reference` for detailed API documentation
5. ⚡ Study :doc:`performance` optimization techniques

If you encounter issues, please check :doc:`troubleshooting` or submit an issue on GitHub.