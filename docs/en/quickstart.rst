Quick Start
===========

This guide will help you get started with ModbusLink quickly.

Basic Concepts
--------------

ModbusLink follows a layered architecture:

* **Transport Layer**: Handles the low-level communication (RTU, TCP)
* **Client Layer**: Provides high-level Modbus operations
* **Utility Layer**: Contains helper functions and data converters

Synchronous Operations
----------------------

TCP Connection
~~~~~~~~~~~~~~

.. code-block:: python

   from modbuslink import ModbusClient, TcpTransport

   # Create TCP transport
   transport = TcpTransport(
       host='192.168.1.100',
       port=502,
       timeout=10.0
   )

   # Create client
   client = ModbusClient(transport)

   try:
       # Connect to the device
       client.connect()
       
       # Read 10 holding registers starting from address 0
       registers = client.read_holding_registers(
           slave_id=1,
           start_address=0,
           quantity=10
       )
       print(f"Holding registers: {registers}")
       
       # Write a single register
       client.write_single_register(
           slave_id=1,
           address=0,
           value=1234
       )
       
       # Write multiple registers
       client.write_multiple_registers(
           slave_id=1,
           start_address=10,
           values=[100, 200, 300, 400]
       )
       
   except Exception as e:
       print(f"Error: {e}")
   finally:
       client.disconnect()

RTU Connection
~~~~~~~~~~~~~~

.. code-block:: python

   from modbuslink import ModbusClient, RtuTransport

   # Create RTU transport
   transport = RtuTransport(
       port='COM1',  # or '/dev/ttyUSB0' on Linux
       baudrate=9600,
       bytesize=8,
       parity='N',
       stopbits=1,
       timeout=1.0
   )

   # Create client
   client = ModbusClient(transport)

   try:
       # Connect to the device
       client.connect()
       
       # Read coils
       coils = client.read_coils(
           slave_id=1,
           start_address=0,
           quantity=8
       )
       print(f"Coils: {coils}")
       
       # Write a single coil
       client.write_single_coil(
           slave_id=1,
           address=0,
           value=True
       )
       
   except Exception as e:
       print(f"Error: {e}")
   finally:
       client.disconnect()

Asynchronous Operations
-----------------------

ModbusLink supports async/await for high-performance applications:

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
           
           # Write multiple registers concurrently
           tasks = [
               client.write_single_register(slave_id=1, address=i, value=i*10)
               for i in range(5)
           ]
           await asyncio.gather(*tasks)

   # Run the async function
   asyncio.run(main())

Advanced Data Types
-------------------

ModbusLink provides built-in support for advanced data types:

.. code-block:: python

   from modbuslink import ModbusClient, TcpTransport

   transport = TcpTransport(host='192.168.1.100', port=502)
   client = ModbusClient(transport)

   try:
       client.connect()
       
       # Read/write 32-bit float
       client.write_float32(slave_id=1, start_address=100, value=3.14159)
       temperature = client.read_float32(slave_id=1, start_address=100)
       print(f"Temperature: {temperature}°C")
       
       # Read/write 32-bit integer
       client.write_int32(slave_id=1, start_address=102, value=-123456)
       counter = client.read_int32(slave_id=1, start_address=102)
       print(f"Counter: {counter}")
       
   finally:
       client.disconnect()

Using the Slave Simulator
--------------------------

ModbusLink includes a built-in slave simulator for testing:

.. code-block:: python

   from modbuslink import ModbusSlave, DataStore
   import time

   # Create data store
   data_store = DataStore()
   
   # Initialize some data
   data_store.set_holding_registers(0, [1000, 2000, 3000, 4000, 5000])
   data_store.set_coils(0, [True, False, True, False, True, False, True, False])
   
   # Create slave
   slave = ModbusSlave(slave_id=1, data_store=data_store)
   
   # Start TCP server
   slave.start_tcp_server(host='127.0.0.1', port=5020)
   print("Slave simulator started on 127.0.0.1:5020")
   
   try:
       # Keep the simulator running
       time.sleep(60)  # Run for 60 seconds
   finally:
       slave.stop()

Error Handling
--------------

ModbusLink provides specific exceptions for different error conditions:

.. code-block:: python

   from modbuslink import (
       ModbusClient, TcpTransport,
       ConnectionError, TimeoutError, ModbusException
   )

   transport = TcpTransport(host='192.168.1.100', port=502)
   client = ModbusClient(transport)

   try:
       client.connect()
       registers = client.read_holding_registers(slave_id=1, start_address=0, quantity=10)
       
   except ConnectionError:
       print("Failed to connect to the device")
   except TimeoutError:
       print("Request timed out")
   except ModbusException as e:
       print(f"Modbus error: {e}")
   except Exception as e:
       print(f"Unexpected error: {e}")
   finally:
       client.disconnect()

Next Steps
----------

* Read the :doc:`user_guide` for detailed information
* Check out the :doc:`examples` for more use cases
* Explore the :doc:`api_reference` for complete API documentation
* Learn about :doc:`advanced_topics` for expert usage