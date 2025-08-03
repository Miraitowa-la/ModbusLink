用户指南
========

本综合指南涵盖了使用 ModbusLink 的所有方面。

架构概述
--------

ModbusLink 建立在清晰的分层架构之上，分离关注点并促进代码重用：

.. code-block:: text

   ┌─────────────────────────────────────┐
   │           客户端层                   │
   │  (ModbusClient, AsyncModbusClient)  │
   ├─────────────────────────────────────┤
   │           传输层                     │
   │   (TcpTransport, RtuTransport,      │
   │    AsyncTcpTransport)               │
   ├─────────────────────────────────────┤
   │           工具层                     │
   │  (CRC16, PayloadCoder, Logger)      │
   └─────────────────────────────────────┘

传输层
------

传输层处理底层通信细节。

TCP 传输
~~~~~~~~

TCP 传输处理带有 MBAP 头管理的 Modbus TCP 通信：

.. code-block:: python

   from modbuslink import TcpTransport

   transport = TcpTransport(
       host='192.168.1.100',
       port=502,
       timeout=10.0
   )

RTU 传输
~~~~~~~~

RTU 传输处理带有 CRC16 验证的 Modbus RTU 通信：

.. code-block:: python

   from modbuslink import RtuTransport

   transport = RtuTransport(
       port='/dev/ttyUSB0',  # Windows 上使用 'COM1'
       baudrate=9600,
       bytesize=8,
       parity='N',
       stopbits=1,
       timeout=1.0
   )

异步 TCP 传输
~~~~~~~~~~~~~

对于高性能应用，使用异步 TCP 传输：

.. code-block:: python

   from modbuslink import AsyncTcpTransport

   transport = AsyncTcpTransport(
       host='192.168.1.100',
       port=502,
       timeout=10.0
   )

客户端层
--------

客户端层提供高级 Modbus 操作。

同步客户端
~~~~~~~~~~

.. code-block:: python

   from modbuslink import ModbusClient, TcpTransport

   transport = TcpTransport(host='192.168.1.100', port=502)
   client = ModbusClient(transport)

   # 上下文管理器（推荐）
   with client:
       registers = client.read_holding_registers(
           slave_id=1, start_address=0, quantity=10
       )

   # 手动连接管理
   try:
       client.connect()
       registers = client.read_holding_registers(
           slave_id=1, start_address=0, quantity=10
       )
   finally:
       client.disconnect()

异步客户端
~~~~~~~~~~

.. code-block:: python

   from modbuslink import AsyncModbusClient, AsyncTcpTransport
   import asyncio

   async def main():
       transport = AsyncTcpTransport(host='192.168.1.100', port=502)
       client = AsyncModbusClient(transport)

       # 上下文管理器（推荐）
       async with client:
           registers = await client.read_holding_registers(
               slave_id=1, start_address=0, quantity=10
           )

   asyncio.run(main())

支持的功能码
------------

读取操作
~~~~~~~~

**读取线圈 (0x01)**

.. code-block:: python

   coils = client.read_coils(
       slave_id=1,
       start_address=0,
       quantity=8
   )
   # 返回: [True, False, True, False, True, False, True, False]

**读取离散输入 (0x02)**

.. code-block:: python

   inputs = client.read_discrete_inputs(
       slave_id=1,
       start_address=0,
       quantity=8
   )
   # 返回: [True, False, True, False, True, False, True, False]

**读取保持寄存器 (0x03)**

.. code-block:: python

   registers = client.read_holding_registers(
       slave_id=1,
       start_address=0,
       quantity=10
   )
   # 返回: [1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000, 10000]

**读取输入寄存器 (0x04)**

.. code-block:: python

   registers = client.read_input_registers(
       slave_id=1,
       start_address=0,
       quantity=10
   )
   # 返回: [100, 200, 300, 400, 500, 600, 700, 800, 900, 1000]

写入操作
~~~~~~~~

**写单个线圈 (0x05)**

.. code-block:: python

   client.write_single_coil(
       slave_id=1,
       address=0,
       value=True
   )

**写单个寄存器 (0x06)**

.. code-block:: python

   client.write_single_register(
       slave_id=1,
       address=0,
       value=1234
   )

**写多个线圈 (0x0F)**

.. code-block:: python

   client.write_multiple_coils(
       slave_id=1,
       start_address=0,
       values=[True, False, True, False, True]
   )

**写多个寄存器 (0x10)**

.. code-block:: python

   client.write_multiple_registers(
       slave_id=1,
       start_address=0,
       values=[1000, 2000, 3000, 4000, 5000]
   )

高级数据类型
------------

ModbusLink 提供常见数据类型的内置支持：

32位浮点数
~~~~~~~~~~

.. code-block:: python

   # 写入 float32
   client.write_float32(
       slave_id=1,
       start_address=100,
       value=3.14159,
       byte_order='big',
       word_order='big'
   )

   # 读取 float32
   temperature = client.read_float32(
       slave_id=1,
       start_address=100,
       byte_order='big',
       word_order='big'
   )

32位整数
~~~~~~~~

.. code-block:: python

   # 写入 int32
   client.write_int32(
       slave_id=1,
       start_address=102,
       value=-123456,
       byte_order='big',
       word_order='big'
   )

   # 读取 int32
   counter = client.read_int32(
       slave_id=1,
       start_address=102,
       byte_order='big',
       word_order='big'
   )

32位无符号整数
~~~~~~~~~~~~~~

.. code-block:: python

   # 写入 uint32
   client.write_uint32(
       slave_id=1,
       start_address=104,
       value=4294967295,
       byte_order='big',
       word_order='big'
   )

   # 读取 uint32
   value = client.read_uint32(
       slave_id=1,
       start_address=104,
       byte_order='big',
       word_order='big'
   )

字节序和字序
~~~~~~~~~~~~

ModbusLink 支持不同的字节序和字序：

* **字节序**: 'big'（大端序）或 'little'（小端序）
* **字序**: 'big'（高字在前）或 'little'（低字在前）

.. code-block:: python

   # 不同组合
   value1 = client.read_float32(1, 100, byte_order='big', word_order='big')      # >AB
   value2 = client.read_float32(1, 100, byte_order='big', word_order='little')   # >BA
   value3 = client.read_float32(1, 100, byte_order='little', word_order='big')   # <AB
   value4 = client.read_float32(1, 100, byte_order='little', word_order='little') # <BA

回调机制
--------

异步客户端支持操作完成通知的回调函数：

.. code-block:: python

   def on_read_complete(registers):
       print(f"读取完成: {registers}")

   def on_write_complete():
       print("写入完成")

   async def main():
       async with client:
           # 带回调的读取
           registers = await client.read_holding_registers(
               slave_id=1,
               start_address=0,
               quantity=5,
               callback=on_read_complete
           )
           
           # 带回调的写入
           await client.write_single_register(
               slave_id=1,
               address=0,
               value=1234,
               callback=on_write_complete
           )

并发操作
--------

异步客户端支持并发操作以提高性能：

.. code-block:: python

   async def concurrent_operations():
       async with client:
           # 创建多个任务
           tasks = [
               client.read_holding_registers(slave_id=1, start_address=0, quantity=5),
               client.read_coils(slave_id=1, start_address=0, quantity=8),
               client.read_input_registers(slave_id=1, start_address=0, quantity=5),
               client.write_single_register(slave_id=1, address=100, value=9999),
           ]
           
           # 并发执行所有任务
           results = await asyncio.gather(*tasks)
           print(f"并发结果: {results}")

性能优化
--------

为了获得最佳性能，请考虑以下建议：

1. **使用异步客户端**: 对于高并发应用，异步客户端提供更好的性能。

2. **批量操作**: 尽可能使用批量读写操作而不是单个操作。

3. **连接复用**: 保持连接打开并重复使用，而不是频繁连接/断开。

4. **合理设置超时**: 根据网络条件调整超时值。

错误处理
--------

ModbusLink 提供全面的错误处理：

异常类型
~~~~~~~~

.. code-block:: python

   from modbuslink import (
       ModbusLinkError,      # 基础异常
       ConnectionError,      # 连接问题
       TimeoutError,         # 请求超时
       CRCError,            # CRC 验证失败
       InvalidResponseError, # 无效响应格式
       ModbusException      # Modbus 协议错误
   )

错误处理示例
~~~~~~~~~~~~

.. code-block:: python

   try:
       client.connect()
       registers = client.read_holding_registers(slave_id=1, start_address=0, quantity=10)
       
   except ConnectionError as e:
       print(f"连接失败: {e}")
   except TimeoutError as e:
       print(f"请求超时: {e}")
   except CRCError as e:
       print(f"CRC 验证失败: {e}")
   except ModbusException as e:
       print(f"Modbus 错误码 {e.error_code}: {e}")
   except ModbusLinkError as e:
       print(f"ModbusLink 错误: {e}")
   except Exception as e:
       print(f"意外错误: {e}")
   finally:
       client.disconnect()

日志记录
--------

ModbusLink 包含全面的日志系统：

.. code-block:: python

   import logging
   from modbuslink.utils.logger import setup_logging

   # 启用调试日志
   setup_logging(level=logging.DEBUG)

   # 或手动配置
   logging.basicConfig(
       level=logging.DEBUG,
       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
   )

最佳实践
--------

1. **使用上下文管理器**: 始终使用 ``with`` 语句或 ``async with`` 进行自动资源管理。

2. **处理异常**: 为健壮的应用程序实现适当的异常处理。

3. **配置超时**: 根据网络条件设置适当的超时值。

4. **使用异步提高性能**: 对于需要高吞吐量的应用程序使用异步客户端。

5. **启用日志**: 在生产环境中使用日志进行调试和监控。

6. **验证数据**: 在写入设备之前始终验证数据范围和类型。

7. **连接管理**: 合理管理连接的生命周期，避免频繁连接断开。