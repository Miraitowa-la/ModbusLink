ModbusLink 文档
===============

.. image:: https://img.shields.io/pypi/v/modbuslink.svg
   :target: https://pypi.org/project/modbuslink/
   :alt: PyPI版本

.. image:: https://img.shields.io/pypi/pyversions/modbuslink.svg
   :target: https://pypi.org/project/modbuslink/
   :alt: Python版本

.. image:: https://img.shields.io/github/license/Miraitowa-la/ModbusLink
   :target: https://github.com/Miraitowa-la/ModbusLink/blob/main/LICENSE.txt
   :alt: 许可证

欢迎使用 ModbusLink 文档！

ModbusLink 是一个**现代化、高性能的Python Modbus库**，专为工业自动化、物联网应用和SCADA系统设计。采用现代化Python开发实践，在保持企业级可靠性的同时提供无与伦比的易用性。

.. toctree::
   :maxdepth: 2
   :caption: 快速入门
   :hidden:

   installation
   quickstart
   architecture

.. toctree::
   :maxdepth: 2
   :caption: 用户指南
   :hidden:

   user_guide
   advanced_guide
   performance
   production

.. toctree::
   :maxdepth: 2
   :caption: 示例和实践
   :hidden:

   examples
   best_practices
   troubleshooting

.. toctree::
   :maxdepth: 2
   :caption: API文档
   :hidden:

   api_reference

.. toctree::
   :maxdepth: 1
   :caption: 其他
   :hidden:

   changelog
   contributing

文档导航
========

新手入门
--------

.. grid:: 2
   :gutter: 3

   .. grid-item-card:: ⚡ 30秒快速体验
      :link: quickstart
      :link-type: doc
      :class-card: quickstart-card

      几分钟内开始使用ModbusLink。学习基础知识并实现您的第一次Modbus通信。

   .. grid-item-card:: 🛠️ 安装说明
      :link: installation
      :link-type: doc
      :class-card: install-card

      详细的安装指南，包括系统要求、依赖项和环境配置。

核心功能
--------

.. grid:: 3
   :gutter: 3

   .. grid-item-card:: 📖 用户指南
      :link: user_guide
      :link-type: doc
      :class-card: guide-card

      全面的使用指南，涵盖从基本操作到高级配置的所有功能。

   .. grid-item-card:: 🏗️ 架构设计
      :link: architecture
      :link-type: doc
      :class-card: arch-card

      深入了解ModbusLink的分层架构和设计原理。

   .. grid-item-card:: 📚 API参考
      :link: api_reference
      :link-type: doc
      :class-card: api-card

      完整的API文档，包含详细的类和方法描述。

实战应用
--------

.. grid:: 3
   :gutter: 3

   .. grid-item-card:: 💡 代码示例
      :link: examples
      :link-type: doc
      :class-card: example-card

      丰富的实际示例，涵盖各种工业应用场景。

   .. grid-item-card:: ⚡ 性能优化
      :link: performance
      :link-type: doc
      :class-card: perf-card

      性能调优技巧和并发处理最佳实践。

   .. grid-item-card:: 🔧 故障排除
      :link: troubleshooting
      :link-type: doc
      :class-card: trouble-card

      常见问题解决方案和调试技巧。

核心特性
========

.. list-table:: ModbusLink 核心特性
   :widths: 20 40 40
   :header-rows: 1

   * - 特性
     - 描述
     - 优势
   * - 🏗️ **分层架构**
     - 关注点清晰分离
     - 易于维护和扩展
   * - 🔌 **通用传输**
     - 支持TCP、RTU、ASCII
     - 兼容所有Modbus设备
   * - ⚡ **异步性能**
     - 原生asyncio支持
     - 处理1000+并发连接
   * - 🛠️ **开发体验**
     - 直观API和完整类型提示
     - 更快开发，更少bug
   * - 📊 **丰富数据类型**
     - float32、int32、字符串等
     - 处理复杂工业数据
   * - 🔍 **高级调试**
     - 协议级监控
     - 快速故障排除
   * - 🖥️ **完整服务器**
     - 全功能服务器实现
     - 构建自定义Modbus设备
   * - 🎯 **生产就绪**
     - 全面错误处理
     - 放心部署

支持的Modbus功能码
==================

.. list-table:: 
   :widths: 15 25 60
   :header-rows: 1

   * - 功能码
     - 功能名称
     - 描述
   * - **0x01**
     - 读取线圈
     - 读取一个或多个线圈的状态（布尔值）
   * - **0x02**
     - 读取离散输入
     - 读取一个或多个离散输入的状态（只读布尔值）
   * - **0x03**
     - 读取保持寄存器
     - 读取一个或多个保持寄存器的值（16位整数）
   * - **0x04**
     - 读取输入寄存器
     - 读取一个或多个输入寄存器的值（只读16位整数）
   * - **0x05**
     - 写单个线圈
     - 向指定地址写入单个线圈值
   * - **0x06**
     - 写单个寄存器
     - 向指定地址写入单个寄存器值
   * - **0x0F**
     - 写多个线圈
     - 向连续地址写入多个线圈值
   * - **0x10**
     - 写多个寄存器
     - 向连续地址写入多个寄存器值

30秒快速体验
============

安装ModbusLink
--------------

.. code-block:: bash

   # 从 PyPI 安装
   pip install modbuslink

简单示例
--------

**TCP客户端（以太网设备）**

.. code-block:: python

   from modbuslink import ModbusClient, TcpTransport

   # 连接到Modbus TCP设备
   transport = TcpTransport(host='192.168.1.100', port=502)
   client = ModbusClient(transport)

   with client:
       # 读取温度传感器
       temp = client.read_float32(slave_id=1, start_address=100)
       print(f"温度: {temp:.1f}°C")
       
       # 控制水泵开关
       client.write_single_coil(slave_id=1, address=0, value=True)
       print("水泵已启动！")

**串口客户端（RTU设备）**

.. code-block:: python

   from modbuslink import ModbusClient, RtuTransport

   # 连接到串口设备
   transport = RtuTransport(port='COM3', baudrate=9600)
   client = ModbusClient(transport)

   with client:
       # 读取流量计数据
       flow = client.read_float32(slave_id=5, start_address=0)
       print(f"流量: {flow:.2f} L/min")

**高性能异步操作**

.. code-block:: python

   import asyncio
   from modbuslink import AsyncModbusClient, AsyncTcpTransport

   async def read_multiple_plcs():
       """同时读取多个PLC数据"""
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

立即开始
--------

🚀 准备好了吗？前往 :doc:`installation` 安装ModbusLink，然后查看 :doc:`quickstart` 获取详细的入门教程！

社区和支持
==========

.. grid:: 2
   :gutter: 3

   .. grid-item-card:: 📖 GitHub项目
      :link: https://github.com/Miraitowa-la/ModbusLink
      :link-type: url

      源代码、问题报告和功能请求

   .. grid-item-card:: 📦 PyPI包
      :link: https://pypi.org/project/modbuslink/
      :link-type: url

      官方发布包和版本历史

版本信息
========

.. include:: ../CHANGELOG.md
   :parser: myst_parser.sphinx_

索引和表格
==========

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`