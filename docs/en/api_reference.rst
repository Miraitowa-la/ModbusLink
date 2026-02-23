API Reference
=============

This section provides detailed API documentation for all ModbusLink classes and functions.

1. Client Module
----------------

1.1 SyncModbusClient
~~~~~~~~~~~~~~~~~~~~

.. autoclass:: modbuslink.client.sync_client.SyncModbusClient
   :members:
   :undoc-members:
   :show-inheritance:

1.2 AsyncModbusClient
~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: modbuslink.client.async_client.AsyncModbusClient
   :members:
   :undoc-members:
   :show-inheritance:

2. Transport Module
-------------------

2.1 SyncBaseTransport
~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: modbuslink.transport.base_transport.SyncBaseTransport
   :members:
   :undoc-members:
   :show-inheritance:

2.2 AsyncBaseTransport
~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: modbuslink.transport.base_transport.AsyncBaseTransport
   :members:
   :undoc-members:
   :show-inheritance:

2.3 SyncTcpTransport
~~~~~~~~~~~~~~~~~~~~

.. autoclass:: modbuslink.transport.tcp_transport.SyncTcpTransport
   :members:
   :undoc-members:
   :show-inheritance:

2.4 AsyncTcpTransport
~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: modbuslink.transport.tcp_transport.AsyncTcpTransport
   :members:
   :undoc-members:
   :show-inheritance:

2.5 SyncRtuTransport
~~~~~~~~~~~~~~~~~~~~

.. autoclass:: modbuslink.transport.rtu_transport.SyncRtuTransport
   :members:
   :undoc-members:
   :show-inheritance:

2.6 AsyncRtuTransport
~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: modbuslink.transport.rtu_transport.AsyncRtuTransport
   :members:
   :undoc-members:
   :show-inheritance:

2.7 SyncAsciiTransport
~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: modbuslink.transport.ascii_transport.SyncAsciiTransport
   :members:
   :undoc-members:
   :show-inheritance:

2.8 AsyncAsciiTransport
~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: modbuslink.transport.ascii_transport.AsyncAsciiTransport
   :members:
   :undoc-members:
   :show-inheritance:

3. Server Module
----------------

3.1 ModbusDataStore
~~~~~~~~~~~~~~~~~~~

.. autoclass:: modbuslink.server.data_store.ModbusDataStore
   :members:
   :undoc-members:
   :show-inheritance:

3.2 AsyncBaseModbusServer
~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: modbuslink.server.base_server.AsyncBaseModbusServer
   :members:
   :undoc-members:
   :show-inheritance:

3.3 AsyncTcpModbusServer
~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: modbuslink.server.tcp_server.AsyncTcpModbusServer
   :members:
   :undoc-members:
   :show-inheritance:

3.4 AsyncSerialModbusServer
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: modbuslink.server.serial_server.AsyncSerialModbusServer
   :members:
   :undoc-members:
   :show-inheritance:

3.5 AsyncRtuModbusServer
~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: modbuslink.server.rtu_server.AsyncRtuModbusServer
   :members:
   :undoc-members:
   :show-inheritance:

3.6 AsyncAsciiModbusServer
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: modbuslink.server.ascii_server.AsyncAsciiModbusServer
   :members:
   :undoc-members:
   :show-inheritance:

4. Utility Module
-----------------

4.1 PayloadCoder
~~~~~~~~~~~~~~~~

.. autoclass:: modbuslink.utils.coder.PayloadCoder
   :members:
   :undoc-members:
   :show-inheritance:

4.2 CRC16Modbus
~~~~~~~~~~~~~~~

.. autoclass:: modbuslink.utils.crc.CRC16Modbus
   :members:
   :undoc-members:
   :show-inheritance:

4.3 LRC16Modbus
~~~~~~~~~~~~~~~

.. autoclass:: modbuslink.utils.lrc.LRCModbus
   :members:
   :undoc-members:
   :show-inheritance:

5. Common Module
----------------

5.1 Logging Module
~~~~~~~~~~~~~~~~~~

.. automodule:: modbuslink.common.logging
   :members:
   :undoc-members:

5.2 Exception Module
~~~~~~~~~~~~~~~~~~~~

ModbusLinkError
***************

.. autoexception:: modbuslink.common.exceptions.ModbusLinkError
   :members:
   :undoc-members:
   :show-inheritance:

CommunicationError
******************

.. autoexception:: modbuslink.common.exceptions.CommunicationError
   :members:
   :undoc-members:
   :show-inheritance:

ValidationError
***************

.. autoexception:: modbuslink.common.exceptions.ValidationError
   :members:
   :undoc-members:
   :show-inheritance:

ConnectError
************

.. autoexception:: modbuslink.common.exceptions.ConnectError
   :members:
   :undoc-members:
   :show-inheritance:

TimeOutError
************

.. autoexception:: modbuslink.common.exceptions.TimeOutError
   :members:
   :undoc-members:
   :show-inheritance:

CrcError
********

.. autoexception:: modbuslink.common.exceptions.CrcError
   :members:
   :undoc-members:
   :show-inheritance:

LrcError
********

.. autoexception:: modbuslink.common.exceptions.LrcError
   :members:
   :undoc-members:
   :show-inheritance:

InvalidReplyError
*****************

.. autoexception:: modbuslink.common.exceptions.InvalidReplyError
   :members:
   :undoc-members:
   :show-inheritance:

ModbusException
***************

.. autoexception:: modbuslink.common.exceptions.ModbusException
   :members:
   :undoc-members:
   :show-inheritance:

5.3 Language Module
~~~~~~~~~~~~~~~~~~~

.. autoexception:: modbuslink.common.language
   :members:
   :undoc-members:
   :show-inheritance: