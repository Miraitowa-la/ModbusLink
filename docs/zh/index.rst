ModbusLink 文档
===============

欢迎使用 ModbusLink 文档！

ModbusLink 是一个现代化、功能强大、开发者友好且高度可扩展的 Python Modbus 库，同时支持同步和异步操作，并提供无与伦比的易用性和调试体验。

.. toctree::
   :maxdepth: 2
   :caption: 目录:
   :hidden:

   installation
   quickstart
   user_guide
   api_reference
   examples

文档导航
========

.. grid:: 2
   :gutter: 3

   .. grid-item-card:: 🚀 快速开始
      :link: quickstart
      :link-type: doc

      几分钟内开始使用ModbusLink。学习基础知识并实现您的第一次Modbus通信。

   .. grid-item-card:: 📖 用户指南
      :link: user_guide
      :link-type: doc

      全面的指南，涵盖从基本操作到高级配置的所有功能。

   .. grid-item-card:: 📚 API参考
      :link: api_reference
      :link-type: doc

      完整的API文档，包含详细的类和方法描述。

   .. grid-item-card:: 💡 示例
      :link: examples
      :link-type: doc

      各种用例的实际示例和集成模式。
   advanced_topics
   changelog

核心特性
========

* **分层架构**: 严格分离传输层、客户端层和工具层
* **面向接口编程**: 使用抽象基类 (ABC) 定义统一接口
* **依赖注入**: 客户端通过构造函数接收传输层实例
* **用户友好的API**: 对外接口全部使用 Python 原生数据类型
* **同步支持**: 完整的同步 Modbus 客户端实现
* **多传输方式**: 支持 RTU 和 TCP 传输层
* **高级数据类型**: 支持 float32、int32、uint32、int64 和字符串操作
* **统一日志系统**: 全面的日志记录用于调试和监控
* **异步支持**: 原生 async/await 支持，适用于高并发场景
* **回调机制**: 通过回调函数进行请求完成通知
* **Modbus 从站模拟器**: 内置从站模拟器用于测试客户端功能

支持的功能码
============

* **0x01**: 读取线圈
* **0x02**: 读取离散输入
* **0x03**: 读取保持寄存器
* **0x04**: 读取输入寄存器
* **0x05**: 写单个线圈
* **0x06**: 写单个寄存器
* **0x0F**: 写多个线圈
* **0x10**: 写多个寄存器

快速开始
========

同步 TCP 示例
-------------

.. code-block:: python

   from modbuslink import ModbusClient, TcpTransport

   # 创建 TCP 传输层
   transport = TcpTransport(host='192.168.1.100', port=502, timeout=10.0)

   # 创建客户端
   client = ModbusClient(transport)

   try:
       # 连接
       client.connect()
       
       # 读取保持寄存器
       registers = client.read_holding_registers(
           slave_id=1,
           start_address=0,
           quantity=10
       )
       print(f"寄存器: {registers}")
       
       # 写单个寄存器
       client.write_single_register(
           slave_id=1,
           address=0,
           value=1234
       )
       
   finally:
       client.disconnect()

异步 TCP 示例
-------------

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

   asyncio.run(main())

索引和表格
==========

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`