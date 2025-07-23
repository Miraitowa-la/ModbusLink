# ModbusLink

[English](README.md) 中文版

现代化、功能强大、开发者友好且高度可扩展的Python Modbus库。

## 特性

- **分层架构**: 严格分离传输层、客户端和工具层
- **面向接口编程**: 使用抽象基类定义统一接口
- **依赖注入**: 客户端通过构造函数接收传输层实例
- **用户友好**: 对外接口全部使用Python原生数据类型
- **同步支持**: 完整的同步Modbus客户端实现
- **多传输方式**: 支持RTU（串口）和TCP传输

## 快速开始

### 安装

```bash
pip install modbuslink
```

### RTU示例

```python
from modbuslink import ModbusClient, RtuTransport

# 创建RTU传输层
transport = RtuTransport(
    port='COM1',        # Windows
    # port='/dev/ttyUSB0',  # Linux
    baudrate=9600,
    timeout=1.0
)

# 创建客户端
client = ModbusClient(transport)

# 使用上下文管理器自动管理连接
with client:
    # 读取保持寄存器
    registers = client.read_holding_registers(
        slave_id=1,
        start_address=0,
        quantity=4
    )
    print(f"寄存器值: {registers}")
    
    # 写单个寄存器
    client.write_single_register(
        slave_id=1,
        address=0,
        value=1234
    )
    
    # 读取线圈状态
    coils = client.read_coils(
        slave_id=1,
        start_address=0,
        quantity=8
    )
    print(f"线圈状态: {coils}")
```

### TCP示例

```python
from modbuslink import ModbusClient, TcpTransport

# 创建TCP传输层
transport = TcpTransport(
    host='192.168.1.100',
    port=502,
    timeout=10.0
)

# 创建客户端
client = ModbusClient(transport)

# 使用上下文管理器自动管理连接
with client:
    # 读取输入寄存器
    registers = client.read_input_registers(
        slave_id=1,
        start_address=0,
        quantity=10
    )
    print(f"输入寄存器: {registers}")
    
    # 写多个寄存器
    client.write_multiple_registers(
        slave_id=1,
        start_address=0,
        values=[100, 200, 300, 400]
    )
```

## 支持的功能码

- **0x01**: 读取线圈状态
- **0x02**: 读取离散输入状态
- **0x03**: 读取保持寄存器
- **0x04**: 读取输入寄存器
- **0x05**: 写单个线圈
- **0x06**: 写单个寄存器
- **0x0F**: 写多个线圈
- **0x10**: 写多个寄存器

## 异常处理

```python
from modbuslink import (
    ModbusClient, RtuTransport,
    ConnectionError, TimeoutError, CRCError, ModbusException
)

transport = RtuTransport('COM1')
client = ModbusClient(transport)

try:
    with client:
        registers = client.read_holding_registers(1, 0, 4)
except ConnectionError as e:
    print(f"连接错误: {e}")
except TimeoutError as e:
    print(f"超时错误: {e}")
except CRCError as e:
    print(f"CRC校验错误: {e}")
except ModbusException as e:
    print(f"Modbus协议异常: {e}")
```

## 项目结构

```
ModbusLink/
├── src/modbuslink/          # 主要源代码
│   ├── __init__.py          # 主要导出接口
│   ├── client/              # 客户端模块
│   │   ├── __init__.py
│   │   └── sync_client.py   # 同步客户端实现
│   ├── transport/           # 传输层模块
│   │   ├── __init__.py
│   │   ├── base.py         # 传输层抽象基类
│   │   ├── rtu.py          # RTU传输层实现
│   │   └── tcp.py          # TCP传输层实现
│   ├── utils/               # 工具模块
│   │   ├── __init__.py
│   │   └── crc.py          # CRC16校验工具
│   └── common/              # 通用模块
│       ├── __init__.py
│       └── exceptions.py    # 异常定义
├── tests/                   # 测试模块
│   ├── __init__.py
│   ├── test_basic.py        # 基本功能测试
│   └── test_crc.py          # CRC功能测试
├── examples/                # 使用示例
│   ├── __init__.py
│   ├── rtu_example.py       # RTU使用示例
│   └── tcp_example.py       # TCP使用示例
├── pyproject.toml           # 项目配置
├── README.md                # 项目说明
└── LICENSE.txt              # 许可证
```

## 测试

项目包含完整的测试套件，用于验证所有功能的正确性。

### 运行测试

```bash
# 运行CRC功能测试
python tests/test_crc.py

# 运行基本功能测试
python tests/test_basic.py
```

### 测试内容

- **CRC功能测试** (`tests/test_crc.py`): 验证CRC16校验算法的正确性
- **基本功能测试** (`tests/test_basic.py`): 验证模块导入、传输层创建、客户端功能等

所有测试都包含详细的输出信息，帮助开发者了解测试进度和结果。

## 开发计划

- [x] **第一阶段**: 构建坚实可靠的核心基础（同步MVP）
- [ ] **第二阶段**: 提升易用性与开发者体验
- [ ] **第三阶段**: 拥抱现代化：异步、回调与扩展
- [ ] **第四阶段**: 发布、测试与社区生态

## 许可证

MIT License - 详见 [LICENSE.txt](LICENSE.txt)

## 贡献

欢迎提交Issue和Pull Request！
