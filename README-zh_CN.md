# ModbusLink

[English](README.md) | 中文版

[![PyPI Downloads](https://static.pepy.tech/badge/modbuslink)](https://pepy.tech/projects/modbuslink)
[![PyPI version](https://badge.fury.io/py/modbuslink.svg)](https://badge.fury.io/py/modbuslink)

一个现代化、强大且开发者友好的Python Modbus库，提供全面的传输层支持。

## 特性

- **🏗️ 分层架构**: 传输层、客户端和工具层的清晰分离
- **🔌 多种传输方式**: TCP、RTU和ASCII，支持同步和异步操作
- **⚡ 高性能**: 异步操作支持并发请求处理
- **🛠️ 开发者友好**: 直观的API和全面的错误处理
- **📊 高级数据类型**: 内置支持float32、int32、字符串等
- **🔍 调试支持**: 全面的日志记录和协议级调试
- **🎯 类型安全**: 完整的类型提示，更好的IDE支持

## 快速开始

### 安装

```bash
pip install modbuslink
```

### 基本用法

#### TCP客户端

```python
from modbuslink import ModbusClient, TcpTransport

# 创建TCP传输层
transport = TcpTransport(host='192.168.1.100', port=502)
client = ModbusClient(transport)

with client:
    # 读取保持寄存器
    registers = client.read_holding_registers(
        slave_id=1, start_address=0, quantity=10
    )
    print(f"寄存器值: {registers}")
    
    # 写入单个寄存器
    client.write_single_register(
        slave_id=1, address=0, value=1234
    )
```

#### RTU客户端

```python
from modbuslink import ModbusClient, RtuTransport

# 创建RTU传输层
transport = RtuTransport(
    port='COM1',  # Linux下使用 '/dev/ttyUSB0'
    baudrate=9600,
    timeout=1.0
)
client = ModbusClient(transport)

with client:
    # 读取线圈
    coils = client.read_coils(
        slave_id=1, start_address=0, quantity=8
    )
    print(f"线圈状态: {coils}")
```

#### ASCII客户端

```python
from modbuslink import ModbusClient, AsciiTransport

# 创建ASCII传输层
transport = AsciiTransport(
    port='COM1',
    baudrate=9600,
    bytesize=7,
    parity='E'
)
client = ModbusClient(transport)

with client:
    # 读取输入寄存器
    registers = client.read_input_registers(
        slave_id=1, start_address=0, quantity=5
    )
    print(f"输入寄存器: {registers}")
```

### 异步操作

```python
import asyncio
from modbuslink import AsyncModbusClient, AsyncTcpTransport

async def main():
    transport = AsyncTcpTransport(host='192.168.1.100', port=502)
    client = AsyncModbusClient(transport)
    
    async with client:
        # 并发操作
        tasks = [
            client.read_holding_registers(1, 0, 10),
            client.read_coils(1, 0, 8),
            client.write_single_register(1, 100, 9999)
        ]
        results = await asyncio.gather(*tasks)
        print(f"结果: {results}")

asyncio.run(main())
```

### 高级数据类型

```python
with client:
    # 32位浮点数
    client.write_float32(slave_id=1, start_address=100, value=3.14159)
    temperature = client.read_float32(slave_id=1, start_address=100)
    
    # 32位整数
    client.write_int32(slave_id=1, start_address=102, value=-123456)
    counter = client.read_int32(slave_id=1, start_address=102)
    
    # 字符串
    client.write_string(slave_id=1, start_address=110, value="Hello")
    message = client.read_string(slave_id=1, start_address=110, length=10)
```

## 支持的功能码

| 代码 | 功能 | 描述 |
|------|------|------|
| 0x01 | 读取线圈 | 读取线圈状态 |
| 0x02 | 读取离散输入 | 读取离散输入状态 |
| 0x03 | 读取保持寄存器 | 读取保持寄存器值 |
| 0x04 | 读取输入寄存器 | 读取输入寄存器值 |
| 0x05 | 写入单个线圈 | 写入单个线圈值 |
| 0x06 | 写入单个寄存器 | 写入单个寄存器值 |
| 0x0F | 写入多个线圈 | 写入多个线圈值 |
| 0x10 | 写入多个寄存器 | 写入多个寄存器值 |

## 传输层

### 同步传输层

- **TcpTransport**: 基于以太网的Modbus TCP
- **RtuTransport**: 基于串口的Modbus RTU
- **AsciiTransport**: 基于串口的Modbus ASCII

### 异步传输层

- **AsyncTcpTransport**: 高性能异步TCP
- **AsyncRtuTransport**: 高性能异步RTU
- **AsyncAsciiTransport**: 高性能异步ASCII

## 错误处理

```python
from modbuslink import (
    ModbusClient, TcpTransport,
    ConnectionError, TimeoutError, ModbusException
)

transport = TcpTransport(host='192.168.1.100', port=502)
client = ModbusClient(transport)

try:
    with client:
        registers = client.read_holding_registers(1, 0, 10)
except ConnectionError as e:
    print(f"连接失败: {e}")
except TimeoutError as e:
    print(f"操作超时: {e}")
except ModbusException as e:
    print(f"Modbus错误: {e}")
```

## 日志和调试

```python
from modbuslink.utils import ModbusLogger
import logging

# 设置日志
ModbusLogger.setup_logging(
    level=logging.DEBUG,
    enable_debug=True,
    log_file='modbus.log'
)

# 启用协议调试
ModbusLogger.enable_protocol_debug()
```

## 项目结构

```
ModbusLink/
├── src/modbuslink/
│   ├── client/              # 客户端实现
│   │   ├── sync_client.py   # 同步客户端
│   │   └── async_client.py  # 异步客户端
│   ├── transport/           # 传输层实现
│   │   ├── tcp.py          # TCP传输层
│   │   ├── rtu.py          # RTU传输层
│   │   ├── ascii.py        # ASCII传输层
│   │   ├── async_tcp.py    # 异步TCP传输层
│   │   ├── async_rtu.py    # 异步RTU传输层
│   │   └── async_ascii.py  # 异步ASCII传输层
│   ├── utils/              # 工具模块
│   │   ├── crc.py         # CRC校验
│   │   ├── payload_coder.py # 数据编码/解码
│   │   └── logger.py      # 日志系统
│   └── common/             # 通用模块
│       └── exceptions.py   # 异常定义
├── examples/               # 使用示例
│   ├── sync_tcp_example.py
│   ├── async_tcp_example.py
│   ├── sync_rtu_example.py
│   ├── async_rtu_example.py
│   ├── sync_ascii_example.py
│   └── async_ascii_example.py
└── docs/                   # 文档
```

## 示例

查看[examples](examples/)目录获取全面的使用示例：

- **同步示例**: TCP、RTU和ASCII的基本同步操作
- **异步示例**: 高性能异步操作和并发处理
- **高级功能**: 数据类型、错误处理和调试

## 系统要求

- Python 3.8+
- pyserial >= 3.5 (RTU/ASCII传输层需要)

## 许可证

MIT许可证 - 详见[LICENSE.txt](LICENSE.txt)。

## 贡献

欢迎贡献！请随时提交问题和拉取请求。
