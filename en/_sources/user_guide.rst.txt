User Guide
==========

This comprehensive guide covers all aspects of using ModbusLink.

1. Architecture Overview
------------------------

ModbusLink is built on a clean, layered architecture that separates concerns and promotes code reusability:

.. code-block:: text

   ┌─────────────────────────────────────────┐
   │           Client Layer                   │
   │  (SyncModbusClient, AsyncModbusClient)  │
   ├─────────────────────────────────────────┤
   │           Transport Layer                │
   │ (SyncTcpTransport, SyncRtuTransport,    │
   │  SyncAsciiTransport, AsyncTcpTransport, │
   │  AsyncRtuTransport, AsyncAsciiTransport)│
   ├─────────────────────────────────────────┤
   │           Utility Layer                  │
   │      (CRC16, CRC16, PayloadCoder)       │
   └─────────────────────────────────────────┘

2. Transport Layer
------------------

The transport layer handles the low-level communication details.

2.1 TCP Transport
~~~~~~~~~~~~~~~~~

TCP transport handles Modbus TCP communication with MBAP header management:

.. code-block:: python

   from modbuslink import SyncTcpTransport

   transport = SyncTcpTransport(
       host='192.168.1.100',
       port=502,
       timeout=10.0
   )

2.2 RTU Transport
~~~~~~~~~~~~~~~~~

RTU transport handles Modbus RTU communication with CRC16 verification:

.. code-block:: python

   from modbuslink import SyncRtuTransport

   transport = SyncRtuTransport(
       port='/dev/ttyUSB0',  # Use 'COM1' on Windows
       baudrate=9600,
       bytesize=8,
       parity='N',
       stopbits=1,
       timeout=1.0
   )

2.3 Async TCP Transpor
~~~~~~~~~~~~~~~~~~~~~~

For high-performance applications, use the async TCP transport:

.. code-block:: python

   from modbuslink import AsyncTcpTransport

   transport = AsyncTcpTransport(
       host='192.168.1.100',
       port=502,
       timeout=10.0
   )

2.4 ASCII Transport
~~~~~~~~~~~~~~~~~~~

The ASCII transport handles Modbus ASCII communication with LRC validation:

.. code-block:: python

   from modbuslink import AsciiTransport

   transport = AsciiTransport(
       port='COM1',
       baudrate=9600,
       bytesize=7,
       parity='E',
       stopbits=1,
       timeout=1.0
   )

2.5 Async RTU Transport
~~~~~~~~~~~~~~~~~~~~~~~

For high-performance RTU applications, use the async RTU transport:

.. code-block:: python

   from modbuslink import AsyncRtuTransport

   transport = AsyncRtuTransport(
       port='COM1',
       baudrate=9600,
       timeout=3.0
   )

2.6 Async ASCII Transport
~~~~~~~~~~~~~~~~~~~~~~~~~

For high-performance ASCII applications, use the async ASCII transport:

.. code-block:: python

   from modbuslink import AsyncAsciiTransport

   transport = AsyncAsciiTransport(
       port='COM1',
       baudrate=9600,
       timeout=3.0
   )

3. Client Layer
---------------

The client layer provides high-level Modbus operations.

3.1 Synchronous Client
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from modbuslink import SyncModbusClient, SyncTcpTransport

   transport = SyncTcpTransport(host='192.168.1.100', port=502)
   client = SyncModbusClient(transport)

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

3.2 Asynchronous Client
~~~~~~~~~~~~~~~~~~~~~~~

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

4. Supported Function Codes
---------------------------

4.1 Read Operations
~~~~~~~~~~~~~~~~~~~

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

4.2 Write Operations
~~~~~~~~~~~~~~~~~~~~

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

5. Advanced Data Types
----------------------

ModbusLink provides built-in support for common data types, including "32-bit float/32-bit integer/32-bit unsigned integer", all including "32-bit float/32-bit integer/32-bit unsigned integer/64-bit integer/64-bit unsigned integer/string":

5.1 32-bit Float
~~~~~~~~~~~~~~~~

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

5.2 32-bit Integer
~~~~~~~~~~~~~~~~~~

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

5.3 32-bit Unsigned Integer
~~~~~~~~~~~~~~~~~~~~~~~~~~~

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

5.4 Byte and Word Order
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

ModbusLink supports different byte and word orders:

* **Byte Order**: 'big' (big-endian) or 'little' (little-endian)
* **Word Order**: 'big' (high word first) or 'little' (low word first)

.. code-block:: python

   # Different combinations
   value1 = client.read_float32(1, 100, byte_order='big', word_order='big')      # >AB
   value2 = client.read_float32(1, 100, byte_order='big', word_order='little')   # >BA
   value3 = client.read_float32(1, 100, byte_order='little', word_order='big')   # <AB
   value4 = client.read_float32(1, 100, byte_order='little', word_order='little') # <BA

6. Callback Mechanism
---------------------

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

7. Concurrent Operations
------------------------

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

8. Performance Optimization
---------------------------

For optimal performance, consider the following recommendations:

1. **Use Async Clients**: For high-concurrency applications, async clients provide better performance.

2. **Batch Operations**: Use batch read/write operations whenever possible instead of individual operations.

3. **Connection Reuse**: Keep connections open and reuse them rather than frequent connect/disconnect.

4. **Proper Timeouts**: Adjust timeout values based on network conditions.

9. Error Handling
-----------------

ModbusLink provides comprehensive error handling:

9.1 Exception Types
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from modbuslink import (
       ModbusLinkError      # Base exception class
       CommunicationError   # Communication error base class (broad scope)
       ConnectError         # Connection error exception
       TimeOutError         # Timeout error exception
       ValidationError      # Data validation error base class (broad scope)
       CrcError             # CRC verification error exception
       LrcError             # LRC verification error exception
       InvalidReplyError    # Invalid response error exception
       ModbusException      # Protocol error
   )

9.2 Error Handling Example
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   try:
       client.connect()
       registers = client.read_holding_registers(slave_id=1, start_address=0, quantity=10)
       
   except ConnectError as e:
       print(f"Connection failed: {e}")
   except TimeOutError as e:
       print(f"Request timeout: {e}")
   except CRCError as e:
       print(f"CRC verification failed: {e}")
   except LrcError as e:
       print(f"LRC verification failed: {e}")
   except InvalidReplyError as e:
       print(f"Invalid response failed: {e}")
   except ModbusException as e:
       print(f"Modbus error code {e.error_code}: {e}")
   except ModbusLinkError as e:
       print(f"ModbusLink error: {e}")
   except Exception as e:
       print(f"Unexpected error: {e}")
   finally:
       client.disconnect()

10. Logging
-----------

ModbusLink includes a comprehensive logging system:

.. code-block:: python

   import logging
   from modbuslink.logger import setup_logging

   # Enable debug logging
   setup_logging(level=logging.DEBUG)

   # Or configure manually
   logging.basicConfig(
       level=logging.DEBUG,
       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
   )

11. Best Practices
------------------

1. **Use Context Managers**: Always use ``with`` statements or ``async with`` for automatic resource management.

2. **Handle Exceptions**: Implement proper exception handling for robust applications.

3. **Configure Timeouts**: Set appropriate timeout values based on your network conditions.

4. **Use Async for High Performance**: Use async clients for applications requiring high throughput.

5. **Enable Logging**: Use logging for debugging and monitoring in production.

6. **Validate Data**: Always validate data ranges and types before writing to devices.

7. **Connection Management**: Properly manage connection lifecycle to avoid frequent connect/disconnect operations.