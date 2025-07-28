快速开始
========

本指南将帮助您快速开始使用 ModbusLink。

基本概念
--------

ModbusLink 遵循分层架构：

* **传输层**: 处理底层通信 (RTU, TCP)
* **客户端层**: 提供高级 Modbus 操作
* **工具层**: 包含辅助函数和数据转换器

同步操作
--------

TCP 连接
~~~~~~~~

.. code-block:: python

   from modbuslink import ModbusClient, TcpTransport

   # 创建 TCP 传输层
   transport = TcpTransport(
       host='192.168.1.100',
       port=502,
       timeout=10.0
   )

   # 创建客户端
   client = ModbusClient(transport)

   try:
       # 连接到设备
       client.connect()
       
       # 从地址 0 开始读取 10 个保持寄存器
       registers = client.read_holding_registers(
           slave_id=1,
           start_address=0,
           quantity=10
       )
       print(f"保持寄存器: {registers}")
       
       # 写单个寄存器
       client.write_single_register(
           slave_id=1,
           address=0,
           value=1234
       )
       
       # 写多个寄存器
       client.write_multiple_registers(
           slave_id=1,
           start_address=10,
           values=[100, 200, 300, 400]
       )
       
   except Exception as e:
       print(f"错误: {e}")
   finally:
       client.disconnect()

RTU 连接
~~~~~~~~

.. code-block:: python

   from modbuslink import ModbusClient, RtuTransport

   # 创建 RTU 传输层
   transport = RtuTransport(
       port='COM1',  # Linux 上使用 '/dev/ttyUSB0'
       baudrate=9600,
       bytesize=8,
       parity='N',
       stopbits=1,
       timeout=1.0
   )

   # 创建客户端
   client = ModbusClient(transport)

   try:
       # 连接到设备
       client.connect()
       
       # 读取线圈
       coils = client.read_coils(
           slave_id=1,
           start_address=0,
           quantity=8
       )
       print(f"线圈: {coils}")
       
       # 写单个线圈
       client.write_single_coil(
           slave_id=1,
           address=0,
           value=True
       )
       
   except Exception as e:
       print(f"错误: {e}")
   finally:
       client.disconnect()

异步操作
--------

ModbusLink 支持 async/await 用于高性能应用：

.. code-block:: python

   from modbuslink import AsyncModbusClient, AsyncTcpTransport
   import asyncio

   async def main():
       # 创建异步 TCP 传输层
       transport = AsyncTcpTransport(
           host='192.168.1.100',
           port=502,
           timeout=10.0
       )

       # 创建异步客户端
       client = AsyncModbusClient(transport)

       async with client:
           # 读取保持寄存器
           registers = await client.read_holding_registers(
               slave_id=1,
               start_address=0,
               quantity=10
           )
           print(f"寄存器: {registers}")
           
           # 并发写多个寄存器
           tasks = [
               client.write_single_register(slave_id=1, address=i, value=i*10)
               for i in range(5)
           ]
           await asyncio.gather(*tasks)

   # 运行异步函数
   asyncio.run(main())

高级数据类型
------------

ModbusLink 提供内置的高级数据类型支持：

.. code-block:: python

   from modbuslink import ModbusClient, TcpTransport

   transport = TcpTransport(host='192.168.1.100', port=502)
   client = ModbusClient(transport)

   try:
       client.connect()
       
       # 读写 32 位浮点数
       client.write_float32(slave_id=1, start_address=100, value=3.14159)
       temperature = client.read_float32(slave_id=1, start_address=100)
       print(f"温度: {temperature}°C")
       
       # 读写 32 位整数
       client.write_int32(slave_id=1, start_address=102, value=-123456)
       counter = client.read_int32(slave_id=1, start_address=102)
       print(f"计数器: {counter}")
       
   finally:
       client.disconnect()

使用从站模拟器
--------------

ModbusLink 包含内置的从站模拟器用于测试：

.. code-block:: python

   from modbuslink import ModbusSlave, DataStore
   import time

   # 创建数据存储区
   data_store = DataStore()
   
   # 初始化一些数据
   data_store.set_holding_registers(0, [1000, 2000, 3000, 4000, 5000])
   data_store.set_coils(0, [True, False, True, False, True, False, True, False])
   
   # 创建从站
   slave = ModbusSlave(slave_id=1, data_store=data_store)
   
   # 启动 TCP 服务器
   slave.start_tcp_server(host='127.0.0.1', port=5020)
   print("从站模拟器已启动在 127.0.0.1:5020")
   
   try:
       # 保持模拟器运行
       time.sleep(60)  # 运行 60 秒
   finally:
       slave.stop()

错误处理
--------

ModbusLink 为不同的错误条件提供特定的异常：

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
       print("连接设备失败")
   except TimeoutError:
       print("请求超时")
   except ModbusException as e:
       print(f"Modbus 错误: {e}")
   except Exception as e:
       print(f"意外错误: {e}")
   finally:
       client.disconnect()

下一步
------

* 阅读 :doc:`user_guide` 获取详细信息
* 查看 :doc:`examples` 了解更多用例
* 探索 :doc:`api_reference` 获取完整的 API 文档
* 学习 :doc:`advanced_topics` 了解专家用法