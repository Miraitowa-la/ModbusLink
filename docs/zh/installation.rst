安装指南
========

系统要求
--------

* Python 3.9 或更高版本
* pyserial >= 3.5 (用于 RTU 传输)

从 PyPI 安装
------------

安装 ModbusLink 最简单的方法是使用 pip：

.. code-block:: bash

   pip install modbuslink

从源码安装
----------

您也可以从源代码安装 ModbusLink：

.. code-block:: bash

   git clone https://github.com/Miraitowa-la/ModbusLink.git
   cd ModbusLink
   pip install -e .

开发环境安装
------------

对于开发，请安装额外的依赖项：

.. code-block:: bash

   git clone https://github.com/Miraitowa-la/ModbusLink.git
   cd ModbusLink
   pip install -e ".[dev]"

这将安装用于测试和文档的额外包：

* pytest
* pytest-asyncio
* pytest-mock
* sphinx
* sphinx-rtd-theme
* black
* ruff
* mypy

验证安装
--------

要验证 ModbusLink 是否正确安装，请运行：

.. code-block:: python

   import modbuslink
   print(modbuslink.__version__)

可选依赖
--------

用于串口 RTU 通信：

.. code-block:: bash

   pip install pyserial

用于构建文档：

.. code-block:: bash

   pip install sphinx sphinx-rtd-theme

用于测试：

.. code-block:: bash

   pip install pytest pytest-asyncio pytest-mock

故障排除
--------

常见问题
~~~~~~~~

**ImportError: No module named 'serial'**

当 pyserial 未安装时会出现此错误。使用以下命令安装：

.. code-block:: bash

   pip install pyserial

**串口权限被拒绝 (Linux/macOS)**

将您的用户添加到 dialout 组：

.. code-block:: bash

   sudo usermod -a -G dialout $USER

然后注销并重新登录。

**Windows 串口访问问题**

确保串口未被其他应用程序使用，并且您已安装正确的驱动程序。