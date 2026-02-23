快速开始
========

欢迎使用ModbusLink！本指南将带您在 **5分钟内** 掌握ModbusLink的核心功能。

.. tip::
   
   在开始之前，请确保ModbusLink已正确安装。如果没有，请参考 :doc:`installation` 。

1. 核心概念
--------

ModbusLink采用简洁的分层架构，只需两个步骤：

1. **创建传输层** - 处理底层通信（TCP、RTU、ASCII）
2. **创建客户端** - 提供高级Modbus操作

2. 30秒快速体验
------------

.. code-block:: python

   from modbuslink import SyncModbusClient, SyncTcpTransport

   # 连接到Modbus TCP设备
   transport = SyncTcpTransport(host='192.168.1.100', port=502)
   client = SyncModbusClient(transport)

   with client:
       # 读取温度传感器（float32格式）
       temp = client.read_float32(slave_id=1, start_address=100)
       print(f"当前温度: {temp:.1f}°C")
       
       # 控制水泵开关
       client.write_single_coil(slave_id=1, address=0, value=True)
       print("水泵已启动！")

3. 主流传输方式
------------

3.1 TCP传输（以太网）
~~~~~~~~~~~~~~~~~~

**适用场景**: PLC、HMI、以太网模块

.. code-block:: python

   from modbuslink import SyncModbusClient, SyncTcpTransport

   transport = SyncTcpTransport(
       host='192.168.1.10',    # PLC IP地址
       port=502,               # 标准Modbus TCP端口
       timeout=5.0             # 5秒超时
   )
   client = SyncModbusClient(transport)
   
   with client:
       # 读取生产计数器
       counter = client.read_int32(slave_id=1, start_address=1000)
       print(f"生产计数: {counter}")
       
       # 更新设定值
       client.write_float32(slave_id=1, start_address=3000, value=75.5)

3.2 RTU传输（串口）
~~~~~~~~~~~~~~~~~~

**适用场景**: 现场仪表、传感器、传统设备

.. code-block:: python

   from modbuslink import SyncModbusClient, SyncRtuTransport

   transport = SyncRtuTransport(
       port='COM3',            # Windows: COM3, Linux: /dev/ttyUSB0
       baudrate=9600,
       parity='N',
       stopbits=1,
       timeout=2.0
   )
   client = SyncModbusClient(transport)
   
   with client:
       # 读取流量计
       flow_rate = client.read_float32(slave_id=5, start_address=0)
       print(f"流量: {flow_rate:.2f} L/min")

4. 高级数据类型
------------

ModbusLink提供内置的高级数据类型支持：

.. code-block:: python

   with client:
       # 32位浮点数 (IEEE 754)
       temperature = client.read_float32(slave_id=1, start_address=100)
       client.write_float32(slave_id=1, start_address=100, value=25.6)
       
       # 32位整数
       counter = client.read_int32(slave_id=1, start_address=200)
       client.write_int32(slave_id=1, start_address=200, value=12345)
       
       # 字符串（UTF-8编码）
       device_name = client.read_string(slave_id=1, start_address=400, length=16)
       client.write_string(slave_id=1, start_address=400, value="PLC-001")

5. 高性能异步操作
--------------

对于需要处理多个设备的应用，使用异步操作：

.. code-block:: python

   import asyncio
   from modbuslink import AsyncModbusClient, AsyncTcpTransport

   async def read_multiple_plcs():
       # 创建到不同PLC的连接
       plc1 = AsyncModbusClient(AsyncTcpTransport('192.168.1.10', 502))
       plc2 = AsyncModbusClient(AsyncTcpTransport('192.168.1.11', 502))
       
       async with plc1, plc2:
           # 并发读取
           results = await asyncio.gather(
               plc1.read_holding_registers(1, 0, 10),
               plc2.read_holding_registers(1, 0, 10)
           )
           print(f"PLC1: {results[0]}, PLC2: {results[1]}")

   asyncio.run(read_multiple_plcs())

6. 本地测试环境
------------

如果您没有实际的Modbus设备，可以使用ModbusLink内置的服务器模拟器：

.. code-block:: python

   # 运行模拟服务器
   import asyncio
   from modbuslink import AsyncTcpModbusServer, ModbusDataStore

   async def run_test_server():
       data_store = ModbusDataStore()
       server = AsyncTcpModbusServer(
           data_store=data_store,
           host='127.0.0.1',
           port=5020
       )
       print("模拟服务器已启动，监听127.0.0.1:5020")
       await server.serve_forever()

   asyncio.run(run_test_server())

7. 错误处理
---------

.. code-block:: python

   from modbuslink import (
       SyncModbusClient, SyncTcpTransport,
       ConnectError, TimeOutError
   )

   try:
       with client:
           registers = client.read_holding_registers(1, 0, 10)
   except ConnectError:
       print("连接失败，检查网络和IP地址")
   except TimeOutError:
       print("超时，检查设备状态")

8. 下一步
------

武气学习完成！接下来您可以：

1. 📖 阅读 :doc:`user_guide` 全面了解所有功能
2. 🏗️ 了解 :doc:`architecture` 架构设计
3. 💡 查看 :doc:`examples` 更多实际示例
4. 📚 参考 :doc:`api_reference` 详细API文档

如遇到问题，请查看 :doc:`troubleshooting` 或在GitHub提交Issue。