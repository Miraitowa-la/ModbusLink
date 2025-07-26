User Guide
==========

This comprehensive guide covers all aspects of using ModbusLink.

Architecture Overview
---------------------

ModbusLink is built on a clean, layered architecture that separates concerns and promotes code reusability:

.. code-block:: text

   ┌─────────────────────────────────────┐
   │           Client Layer              │
   │  (ModbusClient, AsyncModbusClient)  │
   ├─────────────────────────────────────┤
   │          Transport Layer            │
   │   (TcpTransport, RtuTransport,      │
   │    AsyncTcpTransport)               │
   ├─────────────────────────────────────┤
   │           Utility Layer             │
   │  (CRC16, PayloadCoder, Logger)      │
   └─────────────────────────────────────┘

Transport Layer
---------------

The transport layer handles the low-level communication details.

TCP Transport
~~~~~~~~~~~~~

The TCP transport handles Modbus TCP communication with MBAP header management:

.. code-block:: python

   from modbuslink import TcpTransport

   transport = TcpTransport(
       host='192.168.1.100',
       port=502,
       timeout=10.0
   )

RTU Transport
~~~~~~~~~~~~~

The RTU transport handles Modbus RTU communication with CRC16 validation:

.. code-block:: python

   from modbuslink import RtuTransport

   transport = RtuTransport(
       port='/dev/ttyUSB0',  # or 'COM1' on Windows
       baudrate=9600,
       bytesize=8,
       parity='N',
       stopbits=1,
       timeout=1.0
   )

Async TCP Transport
~~~~~~~~~~~~~~~~~~~

For high-performance applications, use the async TCP transport:

.. code-block:: python

   from modbuslink import AsyncTcpTransport

   transport = AsyncTcpTransport(
       host='192.168.1.100',
       port=502,
       timeout=10.0
   )

Client Layer
------------

The client layer provides high-level Modbus operations.

Synchronous Client
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from modbuslink import ModbusClient, TcpTransport

   transport = TcpTransport(host='192.168.1.100', port=502)
   client = ModbusClient(transport)

   # Context manager (recommended)
   with client:
       registers = client.read_holding_registers(
           slave_id=1, start_address=0, quantity=10
       )

   # Manual connection management
   try:
       client.connect()
       registers = client.read_holding_registers(
           slave_id=1, start_address=0, quantity=10
       )
   finally:
       client.disconnect()

Asynchronous Client
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from modbuslink import AsyncModbusClient, AsyncTcpTransport
   import asyncio

   async def main():
       transport = AsyncTcpTransport(host='192.168.1.100', port=502)
       client = AsyncModbusClient(transport)

       # Context manager (recommended)
       async with client:
           registers = await client.read_holding_registers(
               slave_id=1, start_address=0, quantity=10
           )

   asyncio.run(main())

Supported Function Codes
------------------------

Read Operations
~~~~~~~~~~~~~~~

**Read Coils (0x01)**

.. code-block:: python

   coils = client.read_coils(
       slave_id=1,
       start_address=0,
       quantity=8
   )
   # Returns: [True, False, True, False, True, False, True, False]

**Read Discrete Inputs (0x02)**

.. code-block:: python

   inputs = client.read_discrete_inputs(
       slave_id=1,
       start_address=0,
       quantity=8
   )
   # Returns: [True, False, True, False, True, False, True, False]

**Read Holding Registers (0x03)**

.. code-block:: python

   registers = client.read_holding_registers(
       slave_id=1,
       start_address=0,
       quantity=10
   )
   # Returns: [1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000, 10000]

**Read Input Registers (0x04)**

.. code-block:: python

   registers = client.read_input_registers(
       slave_id=1,
       start_address=0,
       quantity=10
   )
   # Returns: [100, 200, 300, 400, 500, 600, 700, 800, 900, 1000]

Write Operations
~~~~~~~~~~~~~~~~

**Write Single Coil (0x05)**

.. code-block:: python

   client.write_single_coil(
       slave_id=1,
       address=0,
       value=True
   )

**Write Single Register (0x06)**

.. code-block:: python

   client.write_single_register(
       slave_id=1,
       address=0,
       value=1234
   )

**Write Multiple Coils (0x0F)**

.. code-block:: python

   client.write_multiple_coils(
       slave_id=1,
       start_address=0,
       values=[True, False, True, False, True]
   )

**Write Multiple Registers (0x10)**

.. code-block:: python

   client.write_multiple_registers(
       slave_id=1,
       start_address=0,
       values=[1000, 2000, 3000, 4000, 5000]
   )

Advanced Data Types
-------------------

ModbusLink provides built-in support for common data types:

32-bit Float
~~~~~~~~~~~~

.. code-block:: python

   # Write float32
   client.write_float32(
       slave_id=1,
       start_address=100,
       value=3.14159,
       byte_order='big',
       word_order='big'
   )

   # Read float32
   temperature = client.read_float32(
       slave_id=1,
       start_address=100,
       byte_order='big',
       word_order='big'
   )

32-bit Integer
~~~~~~~~~~~~~~

.. code-block:: python

   # Write int32
   client.write_int32(
       slave_id=1,
       start_address=102,
       value=-123456,
       byte_order='big',
       word_order='big'
   )

   # Read int32
   counter = client.read_int32(
       slave_id=1,
       start_address=102,
       byte_order='big',
       word_order='big'
   )

32-bit Unsigned Integer
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Write uint32
   client.write_uint32(
       slave_id=1,
       start_address=104,
       value=4294967295,
       byte_order='big',
       word_order='big'
   )

   # Read uint32
   value = client.read_uint32(
       slave_id=1,
       start_address=104,
       byte_order='big',
       word_order='big'
   )

Byte and Word Order
~~~~~~~~~~~~~~~~~~~

ModbusLink supports different byte and word orders:

* **Byte Order**: 'big' (big-endian) or 'little' (little-endian)
* **Word Order**: 'big' (high word first) or 'little' (low word first)

.. code-block:: python

   # Different combinations
   value1 = client.read_float32(1, 100, byte_order='big', word_order='big')      # >AB
   value2 = client.read_float32(1, 100, byte_order='big', word_order='little')   # >BA
   value3 = client.read_float32(1, 100, byte_order='little', word_order='big')   # <AB
   value4 = client.read_float32(1, 100, byte_order='little', word_order='little') # <BA

Callback Mechanism
------------------

Async clients support callback functions for operation completion notifications:

.. code-block:: python

   def on_read_complete(registers):
       print(f"Read completed: {registers}")

   def on_write_complete():
       print("Write completed")

   async def main():
       async with client:
           # Read with callback
           registers = await client.read_holding_registers(
               slave_id=1,
               start_address=0,
               quantity=5,
               callback=on_read_complete
           )
           
           # Write with callback
           await client.write_single_register(
               slave_id=1,
               address=0,
               value=1234,
               callback=on_write_complete
           )

Concurrent Operations
---------------------

Async clients support concurrent operations for improved performance:

.. code-block:: python

   async def concurrent_operations():
       async with client:
           # Create multiple tasks
           tasks = [
               client.read_holding_registers(slave_id=1, start_address=0, quantity=5),
               client.read_coils(slave_id=1, start_address=0, quantity=8),
               client.read_input_registers(slave_id=1, start_address=0, quantity=5),
               client.write_single_register(slave_id=1, address=100, value=9999),
           ]
           
           # Execute all tasks concurrently
           results = await asyncio.gather(*tasks)
           print(f"Concurrent results: {results}")

Slave Simulator
---------------

ModbusLink includes a built-in slave simulator for testing:

Basic Setup
~~~~~~~~~~~

.. code-block:: python

   from modbuslink import ModbusSlave, DataStore

   # Create data store
   data_store = DataStore()
   
   # Initialize data
   data_store.set_holding_registers(0, [1000, 2000, 3000, 4000, 5000])
   data_store.set_coils(0, [True, False, True, False, True, False, True, False])
   data_store.set_input_registers(0, [100, 200, 300, 400, 500])
   data_store.set_discrete_inputs(0, [False, True, False, True, False, True])
   
   # Create slave
   slave = ModbusSlave(slave_id=1, data_store=data_store)
   
   # Start TCP server
   slave.start_tcp_server(host='127.0.0.1', port=5020)

Data Store Operations
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Direct data manipulation
   data_store = DataStore()
   
   # Set holding registers
   data_store.set_holding_registers(0, [1000, 2000, 3000])
   registers = data_store.get_holding_registers(0, 3)
   
   # Set coils
   data_store.set_coils(0, [True, False, True, False])
   coils = data_store.get_coils(0, 4)
   
   # Set input registers (read-only from client perspective)
   data_store.set_input_registers(0, [100, 200, 300])
   input_regs = data_store.get_input_registers(0, 3)
   
   # Set discrete inputs (read-only from client perspective)
   data_store.set_discrete_inputs(0, [True, False, True])
   inputs = data_store.get_discrete_inputs(0, 3)

Error Handling
--------------

ModbusLink provides comprehensive error handling:

Exception Types
~~~~~~~~~~~~~~~

.. code-block:: python

   from modbuslink import (
       ModbusLinkError,      # Base exception
       ConnectionError,      # Connection issues
       TimeoutError,         # Request timeout
       CRCError,            # CRC validation failure
       InvalidResponseError, # Invalid response format
       ModbusException      # Modbus protocol errors
   )

Error Handling Example
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   try:
       client.connect()
       registers = client.read_holding_registers(slave_id=1, start_address=0, quantity=10)
       
   except ConnectionError as e:
       print(f"Connection failed: {e}")
   except TimeoutError as e:
       print(f"Request timed out: {e}")
   except CRCError as e:
       print(f"CRC validation failed: {e}")
   except ModbusException as e:
       print(f"Modbus error code {e.error_code}: {e}")
   except ModbusLinkError as e:
       print(f"ModbusLink error: {e}")
   except Exception as e:
       print(f"Unexpected error: {e}")
   finally:
       client.disconnect()

Logging
-------

ModbusLink includes a comprehensive logging system:

.. code-block:: python

   import logging
   from modbuslink.utils.logger import setup_logging

   # Enable debug logging
   setup_logging(level=logging.DEBUG)

   # Or configure manually
   logging.basicConfig(
       level=logging.DEBUG,
       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
   )

Best Practices
--------------

1. **Use Context Managers**: Always use ``with`` statements or ``async with`` for automatic resource management.

2. **Handle Exceptions**: Implement proper exception handling for robust applications.

3. **Configure Timeouts**: Set appropriate timeout values based on your network conditions.

4. **Use Async for High Performance**: Use async clients for applications requiring high throughput.

5. **Test with Simulator**: Use the built-in slave simulator for development and testing.

6. **Enable Logging**: Use logging for debugging and monitoring in production.

7. **Validate Data**: Always validate data ranges and types before writing to devices.