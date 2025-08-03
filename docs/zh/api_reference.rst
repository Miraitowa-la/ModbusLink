API 参考
========

本节提供ModbusLink所有类和函数的详细API文档。

客户端模块
----------

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

传输模块
--------

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



工具模块
--------

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

日志函数
~~~~~~~~

.. automodule:: modbuslink.utils.logger
   :members:
   :undoc-members:

异常模块
--------

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

功能码常量
----------

读取功能码
~~~~~~~~~~

* ``READ_COILS = 0x01`` - 读取线圈
* ``READ_DISCRETE_INPUTS = 0x02`` - 读取离散输入
* ``READ_HOLDING_REGISTERS = 0x03`` - 读取保持寄存器
* ``READ_INPUT_REGISTERS = 0x04`` - 读取输入寄存器

写入功能码
~~~~~~~~~~

* ``WRITE_SINGLE_COIL = 0x05`` - 写入单个线圈
* ``WRITE_SINGLE_REGISTER = 0x06`` - 写入单个寄存器
* ``WRITE_MULTIPLE_COILS = 0x0F`` - 写入多个线圈
* ``WRITE_MULTIPLE_REGISTERS = 0x10`` - 写入多个寄存器

异常码
~~~~~~

* ``ILLEGAL_FUNCTION = 0x01`` - 非法功能
* ``ILLEGAL_DATA_ADDRESS = 0x02`` - 非法数据地址
* ``ILLEGAL_DATA_VALUE = 0x03`` - 非法数据值
* ``SLAVE_DEVICE_FAILURE = 0x04`` - 从站设备故障
* ``ACKNOWLEDGE = 0x05`` - 确认
* ``SLAVE_DEVICE_BUSY = 0x06`` - 从站设备忙
* ``MEMORY_PARITY_ERROR = 0x08`` - 内存奇偶校验错误
* ``GATEWAY_PATH_UNAVAILABLE = 0x0A`` - 网关路径不可用
* ``GATEWAY_TARGET_DEVICE_FAILED_TO_RESPOND = 0x0B`` - 网关目标设备响应失败

数据类型格式
------------

字节序
~~~~~~

* ``'big'``: 大端序（最高有效字节在前）
* ``'little'``: 小端序（最低有效字节在前）

字序
~~~~

* ``'big'``: 高字在前
* ``'little'``: 低字在前

组合格式码
~~~~~~~~~~

* ``'>AB'``: 大端字节序，高字在前
* ``'>BA'``: 大端字节序，低字在前
* ``'<AB'``: 小端字节序，高字在前
* ``'<BA'``: 小端字节序，低字在前

类型别名
--------

.. code-block:: python

   from typing import List, Union, Optional, Callable, Any

   # 库中使用的常见类型别名
   RegisterList = List[int]
   CoilList = List[bool]
   ByteOrder = str  # 'big' 或 'little'
   WordOrder = str  # 'big' 或 'little'
   CallbackFunction = Optional[Callable[[Any], None]]

使用示例
--------

基本客户端使用
~~~~~~~~~~~~~~

.. code-block:: python

   from modbuslink import ModbusClient, TcpTransport

   # 创建传输层和客户端
   transport = TcpTransport(host='192.168.1.100', port=502)
   client = ModbusClient(transport)

   # 使用上下文管理器
   with client:
       # 读取操作
       coils = client.read_coils(slave_id=1, start_address=0, quantity=8)
       registers = client.read_holding_registers(slave_id=1, start_address=0, quantity=10)
       
       # 写入操作
       client.write_single_coil(slave_id=1, address=0, value=True)
       client.write_single_register(slave_id=1, address=0, value=1234)

异步客户端使用
~~~~~~~~~~~~~~

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

从站模拟器使用
~~~~~~~~~~~~~~

.. code-block:: python

   from modbuslink import ModbusSlave, DataStore

   # 创建和配置数据存储
   data_store = DataStore()
   data_store.set_holding_registers(0, [1000, 2000, 3000])
   data_store.set_coils(0, [True, False, True, False])

   # 创建和启动从站
   slave = ModbusSlave(slave_id=1, data_store=data_store)
   slave.start_tcp_server(host='127.0.0.1', port=5020)

   # 使用上下文管理器
   with slave:
       # 从站在后台运行
       pass

高级数据类型
~~~~~~~~~~~~

.. code-block:: python

   # Float32 操作
   client.write_float32(slave_id=1, start_address=100, value=3.14159)
   temperature = client.read_float32(slave_id=1, start_address=100)

   # Int32 操作，自定义字节/字序
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