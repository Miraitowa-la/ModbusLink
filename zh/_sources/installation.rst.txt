安装指南
========

.. contents:: 本页内容
   :local:
   :depth: 2

系统要求
--------

基础要求
~~~~~~~~

.. list-table:: 
   :widths: 20 80
   :header-rows: 1

   * - 组件
     - 要求
   * - **Python版本**
     - Python 3.9+ （推荐 3.11+）
   * - **操作系统**
     - Windows 10+, Linux (Ubuntu 18.04+), macOS 10.15+
   * - **内存**
     - 最少 100MB RAM
   * - **存储空间**
     - 约 10MB 磁盘空间

依赖库
~~~~~~

**必需依赖**

- **Python标准库**: asyncio, threading, struct, socket
- **无外部依赖**: 核心功能无需额外安装包

**可选依赖**

.. code-block:: bash

   # 串口通信支持 (RTU/ASCII)
   pip install pyserial>=3.5
   
   # 异步串口支持
   pip install pyserial-asyncio>=0.6
   
   # 开发工具
   pip install pytest>=7.0 black>=22.0 ruff>=0.1.0

快速安装
--------

从PyPI安装 (推荐)
~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # 基础安装
   pip install modbuslink
   
   # 包含串口支持
   pip install modbuslink[serial]
   
   # 包含开发依赖
   pip install modbuslink[dev]
   
   # 完整安装（所有功能）
   pip install modbuslink[all]

.. note::
   
   如果您只需要TCP功能，基础安装即可。串口功能需要安装 ``pyserial`` 依赖。

验证安装
~~~~~~~~

.. code-block:: python

   import modbuslink
   print(f"ModbusLink版本: {modbuslink.__version__}")
   
   # 检查可用组件
   from modbuslink import ModbusClient, TcpTransport
   print("✅ TCP功能可用")
   
   try:
       from modbuslink import RtuTransport
       print("✅ RTU功能可用")
   except ImportError:
       print("❌ RTU功能不可用 - 需要安装pyserial")

高级安装
--------

从源码安装
~~~~~~~~~~

**开发者安装**

.. code-block:: bash

   # 克隆仓库
   git clone https://github.com/Miraitowa-la/ModbusLink.git
   cd ModbusLink
   
   # 创建虚拟环境
   python -m venv venv
   
   # 激活虚拟环境
   # Windows:
   venv\Scripts\activate
   # Linux/macOS:
   source venv/bin/activate
   
   # 安装为可编辑包
   pip install -e ".[dev]"

**特定版本安装**

.. code-block:: bash

   # 安装特定版本
   pip install modbuslink==1.0.0
   
   # 安装预发布版本
   pip install --pre modbuslink
   
   # 从GitHub安装最新版
   pip install git+https://github.com/Miraitowa-la/ModbusLink.git

Docker安装
~~~~~~~~~~

.. code-block:: dockerfile

   # Dockerfile示例
   FROM python:3.11-slim
   
   # 安装ModbusLink
   RUN pip install modbuslink[all]
   
   # 复制应用代码
   COPY . /app
   WORKDIR /app
   
   # 运行应用
   CMD ["python", "your_modbus_app.py"]

环境配置
--------

串口权限 (Linux/macOS)
~~~~~~~~~~~~~~~~~~~~~~~

**Ubuntu/Debian**

.. code-block:: bash

   # 添加用户到dialout组
   sudo usermod -a -G dialout $USER
   
   # 重新登录使权限生效
   # 或临时切换组
   newgrp dialout
   
   # 查看串口设备
   ls -la /dev/ttyUSB* /dev/ttyACM*

**CentOS/RHEL**

.. code-block:: bash

   # 添加用户到uucp组
   sudo usermod -a -G uucp $USER
   
   # 重新登录

**macOS**

.. code-block:: bash

   # 查看可用串口
   ls /dev/cu.*
   
   # 通常无需特殊权限配置

Windows串口配置
~~~~~~~~~~~~~~~

1. **查看设备管理器**中的端口信息
2. **确认COM端口号**（如 COM1, COM3）
3. **检查驱动程序**是否正确安装
4. **防火墙设置**：确保Python应用有网络权限（TCP功能）

故障排除
--------

常见安装问题
~~~~~~~~~~~~

**ImportError: No module named 'serial'**

.. code-block:: bash

   # 解决方案：安装pyserial
   pip install pyserial

**Permission denied on serial port**

.. code-block:: bash

   # Linux解决方案
   sudo chmod 666 /dev/ttyUSB0  # 临时解决
   sudo usermod -a -G dialout $USER  # 永久解决

**ModuleNotFoundError: No module named 'modbuslink'**

.. code-block:: bash

   # 检查安装状态
   pip list | grep modbuslink
   
   # 重新安装
   pip uninstall modbuslink
   pip install modbuslink

**版本冲突**

.. code-block:: bash

   # 创建干净的虚拟环境
   python -m venv clean_env
   source clean_env/bin/activate  # Linux/macOS
   clean_env\Scripts\activate     # Windows
   pip install modbuslink

串口问题诊断
~~~~~~~~~~~~

**检查串口可用性**

.. code-block:: python

   import serial.tools.list_ports
   
   # 列出所有串口
   ports = serial.tools.list_ports.comports()
   for port in ports:
       print(f"端口: {port.device}, 描述: {port.description}")

**测试串口连接**

.. code-block:: python

   import serial
   
   try:
       ser = serial.Serial('COM3', 9600, timeout=1)  # Windows
       # ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)  # Linux
       print("✅ 串口连接成功")
       ser.close()
   except Exception as e:
       print(f"❌ 串口连接失败: {e}")

网络问题诊断
~~~~~~~~~~~~

**测试TCP连接**

.. code-block:: python

   import socket
   
   def test_tcp_connection(host, port, timeout=5):
       try:
           sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
           sock.settimeout(timeout)
           result = sock.connect_ex((host, port))
           sock.close()
           return result == 0
       except Exception:
           return False
   
   if test_tcp_connection('192.168.1.100', 502):
       print("✅ TCP连接正常")
   else:
       print("❌ TCP连接失败")

性能调优
--------

生产环境配置
~~~~~~~~~~~~

.. code-block:: python

   # 推荐的生产环境配置
   import asyncio
   from modbuslink import AsyncModbusClient, AsyncTcpTransport
   
   # 连接池配置
   transport = AsyncTcpTransport(
       host='192.168.1.100',
       port=502,
       timeout=5.0,           # 适中的超时时间
       connect_timeout=3.0,   # 连接超时
       keepalive=True         # 保持连接活跃
   )
   
   # 异步事件循环优化
   if hasattr(asyncio, 'WindowsSelectorEventLoopPolicy'):
       # Windows优化
       asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

内存优化
~~~~~~~~

.. code-block:: python

   # 对于大量数据读取，使用批量操作
   registers = await client.read_holding_registers(
       slave_id=1, 
       start_address=0, 
       quantity=100  # 一次读取多个寄存器
   )
   
   # 避免频繁创建客户端对象
   # 使用连接池或长连接

升级指南
--------

从旧版本升级
~~~~~~~~~~~~

.. code-block:: bash

   # 查看当前版本
   pip show modbuslink
   
   # 升级到最新版本
   pip install --upgrade modbuslink
   
   # 升级到特定版本
   pip install --upgrade modbuslink==2.0.0

.. warning::
   
   升级前请查看 :doc:`changelog` 了解破坏性变更。

下一步
------

安装完成后，建议您：

1. 📖 阅读 :doc:`quickstart` 快速入门指南
2. 🏗️ 了解 :doc:`architecture` 架构设计
3. 💡 查看 :doc:`examples` 实际示例
4. 📚 参考 :doc:`api_reference` API文档

如遇到问题，请查看 :doc:`troubleshooting` 或在GitHub提交Issue。