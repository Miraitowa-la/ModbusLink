安装指南
========

1. 系统要求
--------

1.1 基础要求
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

1.2 依赖库
~~~~~~

- **Python标准库**: asyncio, threading, struct, socket
- **外部依赖**: pyserial, pyserial-asyncio, typing_extensions

2. 快速安装
--------

2.1 从PyPI安装 (推荐)
~~~~~~~~~~~~~~~~~~

**最新版本安装**

.. code-block:: bash

   # 基础安装
   pip install modbuslink

**特定版本安装**

.. code-block:: bash

   # 安装特定版本
   pip install modbuslink==1.4.0

2.2 从源码安装
~~~~~~~~~~

.. code-block:: bash

   # 克隆仓库
   git clone https://github.com/Miraitowa-la/ModbusLink.git
   cd ModbusLink

   # 创建虚拟环境...

   # 安装为可编辑包
   pip install -e .

2.3 验证安装
~~~~~~~~

.. code-block:: python

   import modbuslink
   print(f"ModbusLink版本: {modbuslink.__version__}")

   from modbuslink import SyncTcpTransport
   print("✅ TCP功能可用")

   from modbuslink import SyncRtuTransport
   print("✅ RTU功能可用")

   from modbuslink import SyncAsciiTransport
   print("✅ ASCII功能可用")

3.  环境配置
--------

3.1 串口权限 (Linux/macOS)
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

3.2 Windows串口配置
~~~~~~~~~~~~~~~

1. **查看设备管理器** 中的端口信息
2. **确认COM端口号** （如 COM1, COM3）
3. **检查驱动程序** 是否正确安装
4. **防火墙设置** 确保Python应用有网络权限（TCP功能）

4. 故障排除
--------

4.1 常见安装问题
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

4.2 串口问题诊断
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

4.3 网络问题诊断
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

5. 性能调优
--------

5.1 超时时间
~~~~~~~~~~~~

.. code-block:: python

   from modbuslink import AsyncTcpTransport

   transport = AsyncTcpTransport(
       host='192.168.1.100',
       port=502,
       timeout=5.0  # 适中的超时时间
   )

5.2 内存优化
~~~~~~~~

.. code-block:: python

   # 对于大量数据读取，使用批量操作
   registers = await client.read_holding_registers(
       slave_id=1, 
       start_address=0, 
       quantity=100  # 一次读取多个寄存器
   )

6. 升级指南
--------

6.1 从旧版本升级
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

7. 下一步
------

安装完成后，建议您：

1. 📖 阅读 :doc:`quickstart` 快速入门指南
2. 🏗️ 了解 :doc:`architecture` 架构设计
3. 💡 查看 :doc:`examples` 实际示例
4. 📚 参考 :doc:`api_reference` API文档

如遇到问题，请查看 :doc:`troubleshooting` 或在GitHub提交Issue。