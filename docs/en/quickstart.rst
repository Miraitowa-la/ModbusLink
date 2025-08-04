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

ASCII Communication
-------------------

For Modbus ASCII communication over serial:

.. code-block:: python

   from modbuslink import ModbusClient, AsciiTransport

   # Create ASCII transport
   transport = AsciiTransport(
       port='COM1',
       baudrate=9600,
       bytesize=7,
       parity='E',
       stopbits=1,
       timeout=1.0
   )

   # Create client
   client = ModbusClient(transport)

   try:
       # Connect to the device
       client.connect()
       
       # Read holding registers
       registers = client.read_holding_registers(
           slave_id=1,
           start_address=0,
           quantity=4
       )
       print(f"Registers: {registers}")
       
       # Write a single register
       client.write_single_register(
           slave_id=1,
           address=0,
           value=1234
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

Error Handling
--------------

ModbusLink provides comprehensive error handling mechanisms:

.. code-block:: python

   from modbuslink import ModbusClient, TcpTransport
   from modbuslink.common.exceptions import (
       ConnectionError, TimeoutError, CRCError, 
       InvalidResponseError, ModbusException
   )

   transport = TcpTransport(host='192.168.1.100', port=502)
   client = ModbusClient(transport)

   try:
       client.connect()
       registers = client.read_holding_registers(
           slave_id=1, start_address=0, quantity=10
       )
       print(f"Registers: {registers}")
       
   except ConnectionError as e:
       print(f"Connection failed: {e}")
   except TimeoutError as e:
       print(f"Request timed out: {e}")
   except CRCError as e:
       print(f"CRC validation failed: {e}")
   except ModbusException as e:
       print(f"Modbus protocol error: {e}")
   except Exception as e:
       print(f"Unexpected error: {e}")
   finally:
       client.disconnect()

Next Steps
----------

Now that you understand the basics of ModbusLink, you can:

* Read the :doc:`user_guide` for more advanced features
* Check out the :doc:`examples` for more sample code
* Explore the :doc:`api_reference` for complete API documentation