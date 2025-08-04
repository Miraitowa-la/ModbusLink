API Reference
=============

This section provides detailed API documentation for all ModbusLink classes and functions.

Client Module
-------------

ModbusClient
~~~~~~~~~~~~

.. autoclass:: modbuslink.client.sync_client.ModbusClient
   :members:
   :undoc-members:
   :show-inheritance:

AsyncModbusClient
~~~~~~~~~~~~~~~~~

.. autoclass:: modbuslink.client.async_client.AsyncModbusClient
   :members:
   :undoc-members:
   :show-inheritance:

Transport Module
----------------

BaseTransport
~~~~~~~~~~~~~

.. autoclass:: modbuslink.transport.base.BaseTransport
   :members:
   :undoc-members:
   :show-inheritance:

TcpTransport
~~~~~~~~~~~~

.. autoclass:: modbuslink.transport.tcp.TcpTransport
   :members:
   :undoc-members:
   :show-inheritance:

RtuTransport
~~~~~~~~~~~~

.. autoclass:: modbuslink.transport.rtu.RtuTransport
   :members:
   :undoc-members:
   :show-inheritance:

AsyncBaseTransport
~~~~~~~~~~~~~~~~~~

.. autoclass:: modbuslink.transport.async_base.AsyncBaseTransport
   :members:
   :undoc-members:
   :show-inheritance:

AsyncTcpTransport
~~~~~~~~~~~~~~~~~

.. autoclass:: modbuslink.transport.async_tcp.AsyncTcpTransport
   :members:
   :undoc-members:
   :show-inheritance:

AsciiTransport
~~~~~~~~~~~~~~

.. autoclass:: modbuslink.transport.ascii.AsciiTransport
   :members:
   :undoc-members:
   :show-inheritance:

AsyncRtuTransport
~~~~~~~~~~~~~~~~~

.. autoclass:: modbuslink.transport.async_rtu.AsyncRtuTransport
   :members:
   :undoc-members:
   :show-inheritance:

AsyncAsciiTransport
~~~~~~~~~~~~~~~~~~~

.. autoclass:: modbuslink.transport.async_ascii.AsyncAsciiTransport
   :members:
   :undoc-members:
   :show-inheritance:



Utility Module
--------------

CRC16Modbus
~~~~~~~~~~~

.. autoclass:: modbuslink.utils.crc.CRC16Modbus
   :members:
   :undoc-members:
   :show-inheritance:

PayloadCoder
~~~~~~~~~~~~

.. autoclass:: modbuslink.utils.payload_coder.PayloadCoder
   :members:
   :undoc-members:
   :show-inheritance:

Logger Functions
~~~~~~~~~~~~~~~~

.. automodule:: modbuslink.utils.logger
   :members:
   :undoc-members:

Exception Module
----------------

ModbusLinkError
~~~~~~~~~~~~~~~

.. autoexception:: modbuslink.common.exceptions.ModbusLinkError
   :members:
   :undoc-members:
   :show-inheritance:

ConnectionError
~~~~~~~~~~~~~~~

.. autoexception:: modbuslink.common.exceptions.ConnectionError
   :members:
   :undoc-members:
   :show-inheritance:

TimeoutError
~~~~~~~~~~~~

.. autoexception:: modbuslink.common.exceptions.TimeoutError
   :members:
   :undoc-members:
   :show-inheritance:

CRCError
~~~~~~~~

.. autoexception:: modbuslink.common.exceptions.CRCError
   :members:
   :undoc-members:
   :show-inheritance:

InvalidResponseError
~~~~~~~~~~~~~~~~~~~~

.. autoexception:: modbuslink.common.exceptions.InvalidResponseError
   :members:
   :undoc-members:
   :show-inheritance:

ModbusException
~~~~~~~~~~~~~~~

.. autoexception:: modbuslink.common.exceptions.ModbusException
   :members:
   :undoc-members:
   :show-inheritance:

Function Code Constants
-----------------------

Read Function Codes
~~~~~~~~~~~~~~~~~~~

* ``READ_COILS = 0x01``
* ``READ_DISCRETE_INPUTS = 0x02``
* ``READ_HOLDING_REGISTERS = 0x03``
* ``READ_INPUT_REGISTERS = 0x04``

Write Function Codes
~~~~~~~~~~~~~~~~~~~~

* ``WRITE_SINGLE_COIL = 0x05``
* ``WRITE_SINGLE_REGISTER = 0x06``
* ``WRITE_MULTIPLE_COILS = 0x0F``
* ``WRITE_MULTIPLE_REGISTERS = 0x10``

Exception Codes
~~~~~~~~~~~~~~~

* ``ILLEGAL_FUNCTION = 0x01``
* ``ILLEGAL_DATA_ADDRESS = 0x02``
* ``ILLEGAL_DATA_VALUE = 0x03``
* ``SLAVE_DEVICE_FAILURE = 0x04``
* ``ACKNOWLEDGE = 0x05``
* ``SLAVE_DEVICE_BUSY = 0x06``
* ``MEMORY_PARITY_ERROR = 0x08``
* ``GATEWAY_PATH_UNAVAILABLE = 0x0A``
* ``GATEWAY_TARGET_DEVICE_FAILED_TO_RESPOND = 0x0B``

Data Type Formats
-----------------

Byte Order
~~~~~~~~~~

* ``'big'``: Big-endian (most significant byte first)
* ``'little'``: Little-endian (least significant byte first)

Word Order
~~~~~~~~~~

* ``'big'``: High word first
* ``'little'``: Low word first

Combined Format Codes
~~~~~~~~~~~~~~~~~~~~~

* ``'>AB'``: Big-endian bytes, high word first
* ``'>BA'``: Big-endian bytes, low word first
* ``'<AB'``: Little-endian bytes, high word first
* ``'<BA'``: Little-endian bytes, low word first

Type Aliases
------------

.. code-block:: python

   from typing import List, Union, Optional, Callable, Any

   # Common type aliases used throughout the library
   RegisterList = List[int]
   CoilList = List[bool]
   ByteOrder = str  # 'big' or 'little'
   WordOrder = str  # 'big' or 'little'
   CallbackFunction = Optional[Callable[[Any], None]]

Usage Examples
--------------

Basic Client Usage
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from modbuslink import ModbusClient, TcpTransport

   # Create transport and client
   transport = TcpTransport(host='192.168.1.100', port=502)
   client = ModbusClient(transport)

   # Use context manager
   with client:
       # Read operations
       coils = client.read_coils(slave_id=1, start_address=0, quantity=8)
       registers = client.read_holding_registers(slave_id=1, start_address=0, quantity=10)
       
       # Write operations
       client.write_single_coil(slave_id=1, address=0, value=True)
       client.write_single_register(slave_id=1, address=0, value=1234)

Async Client Usage
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from modbuslink import AsyncModbusClient, AsyncTcpTransport
   import asyncio

   async def main():
       transport = AsyncTcpTransport(host='192.168.1.100', port=502)
       client = AsyncModbusClient(transport)

       async with client:
           registers = await client.read_holding_registers(
               slave_id=1, start_address=0, quantity=10
           )
           await client.write_single_register(
               slave_id=1, address=0, value=1234
           )

   asyncio.run(main())

Slave Simulator Usage
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from modbuslink import ModbusSlave, DataStore

   # Create and configure data store
   data_store = DataStore()
   data_store.set_holding_registers(0, [1000, 2000, 3000])
   data_store.set_coils(0, [True, False, True, False])

   # Create and start slave
   slave = ModbusSlave(slave_id=1, data_store=data_store)
   slave.start_tcp_server(host='127.0.0.1', port=5020)

   # Use context manager
   with slave:
       # Slave runs in background
       pass

Advanced Data Types
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Float32 operations
   client.write_float32(slave_id=1, start_address=100, value=3.14159)
   temperature = client.read_float32(slave_id=1, start_address=100)

   # Int32 operations with custom byte/word order
   client.write_int32(
       slave_id=1, 
       start_address=102, 
       value=-123456,
       byte_order='little',
       word_order='big'
   )
   counter = client.read_int32(
       slave_id=1, 
       start_address=102,
       byte_order='little',
       word_order='big'
   )