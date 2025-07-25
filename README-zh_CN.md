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
│   │   ├── sync_client.py   # 同步客户端实现
│   │   └── async_client.py  # 异步客户端实现
│   ├── transport/           # 传输层模块
│   │   ├── __init__.py
│   │   ├── base.py         # 传输层抽象基类
│   │   ├── async_base.py   # 异步传输层抽象基类
│   │   ├── rtu.py          # RTU传输层实现
│   │   ├── tcp.py          # TCP传输层实现
│   │   └── async_tcp.py    # 异步TCP传输层实现
│   ├── server/              # 服务器模块（第三阶段）
│   │   ├── __init__.py
│   │   └── slave.py        # Modbus从站模拟器
│   ├── utils/               # 工具模块
│   │   ├── __init__.py
│   │   ├── crc.py          # CRC16校验工具
│   │   ├── payload_coder.py # 数据编解码工具
│   │   └── logger.py       # 统一日志系统
│   └── common/              # 通用模块
│       ├── __init__.py
│       └── exceptions.py    # 异常定义
├── tests/                   # 测试模块
│   ├── __init__.py
│   ├── test_basic.py        # 基本功能测试
│   ├── test_crc.py          # CRC功能测试
│   ├── test_payload_coder.py # 数据编码测试
│   └── test_async_integration.py # 异步集成测试
├── examples/                # 使用示例
│   ├── __init__.py
│   ├── rtu_example.py       # RTU使用示例
│   ├── tcp_example.py       # TCP使用示例
│   ├── advanced_example.py  # 高级数据类型示例
│   ├── async_tcp_example.py # 异步TCP示例
│   ├── slave_simulator_example.py # 从站模拟器示例
│   └── stage3_complete_demo.py # 第三阶段完整演示
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

## 第二阶段功能

第二阶段主要提升了 ModbusLink 库的易用性和开发者体验，新增了高级数据类型支持和统一的日志系统。

### 高级数据类型支持

#### 数据编解码器

新增 `PayloadCoder` 类，提供了多种数据类型的编解码功能：

```python
from modbuslink.utils import PayloadCoder

# 32位浮点数
registers = PayloadCoder.encode_float32(3.14159, 'big', 'high')
value = PayloadCoder.decode_float32(registers, 'big', 'high')

# 32位整数
registers = PayloadCoder.encode_int32(123456789, 'big', 'high')
value = PayloadCoder.decode_int32(registers, 'big', 'high')

# 字符串
registers = PayloadCoder.encode_string("Hello ModbusLink")
value = PayloadCoder.decode_string(registers, 16)
```

#### 支持的数据类型

- **32位浮点数** `float32`: IEEE 754 单精度浮点数
- **32位有符号整数** `int32`: -2,147,483,648 到 2,147,483,647
- **32位无符号整数** `uint32`: 0 到 4,294,967,295
- **64位有符号整数** `int64`: -9,223,372,036,854,775,808 到 9,223,372,036,854,775,807
- **64位无符号整数** `uint64`: 0 到 18,446,744,073,709,551,615
- **字符串** `string`: UTF-8 编码的文本数据

#### 字节序和字序支持

支持不同的字节序（endianness）和字序（word order）：

- **字节序**: `'big'` (大端) 或 `'little'` (小端)
- **字序**: `'high'` (高字在前) 或 `'low'` (低字在前)

### 客户端高级API

为 `ModbusClient` 类新增了高级数据类型的读写方法：

```python
from modbuslink.client import ModbusClient
from modbuslink.transport import TcpTransport

client = ModbusClient(TcpTransport('192.168.1.100', 502))

with client:
    # 读写32位浮点数
    client.write_float32(slave_id=1, start_address=100, value=25.6)
    temperature = client.read_float32(slave_id=1, start_address=100)
    
    # 读写32位整数
    client.write_int32(slave_id=1, start_address=102, value=123456789)
    counter = client.read_int32(slave_id=1, start_address=102)
    
    # 读写字符串
    client.write_string(slave_id=1, start_address=110, value="ModbusLink")
    device_name = client.read_string(slave_id=1, start_address=110, length=10)
```

#### 可用的高级API方法

- `read_float32()` / `write_float32()`: 32位浮点数
- `read_int32()` / `write_int32()`: 32位有符号整数
- `read_uint32()` / `write_uint32()`: 32位无符号整数
- `read_int64()` / `write_int64()`: 64位有符号整数
- `read_uint64()` / `write_uint64()`: 64位无符号整数
- `read_string()` / `write_string()`: 字符串

### 统一日志系统

#### 日志配置

新增 `ModbusLogger` 类，提供统一的日志配置：

```python
from modbuslink.utils import ModbusLogger
import logging

# 配置日志系统
ModbusLogger.setup_logging(
    level=logging.INFO,     # 日志级别
    enable_debug=True,      # 启用调试模式
    log_file='modbus.log'   # 可选：输出到文件
)

# 启用协议级调试
ModbusLogger.enable_protocol_debug()

# 获取日志器
logger = ModbusLogger.get_logger('my_module')
logger.info("这是一条信息日志")
```

#### 日志级别

- `DEBUG`: 详细的调试信息，包括协议级别的原始数据
- `INFO`: 一般信息，如连接状态、操作结果
- `WARNING`: 警告信息，如超时重试
- `ERROR`: 错误信息，如连接失败、协议错误

#### 协议调试

启用协议调试后，可以查看原始的 Modbus 报文：

```
2024-01-15 10:30:15,123 - transport.tcp - DEBUG - 发送数据: 00 01 00 00 00 06 01 03 00 00 00 0A
2024-01-15 10:30:15,125 - transport.tcp - DEBUG - 接收数据: 00 01 00 00 00 17 01 03 14 00 01 00 02 00 03 00 04 00 05 00 06 00 07 00 08 00 09 00 0A
```

### 兼容性说明

- 所有新功能都向后兼容
- 现有的基础API保持不变
- 新的高级API是可选的
- 日志系统默认不启用

## 第三阶段功能

第三阶段引入了现代化的异步编程支持、回调机制和Modbus从站模拟功能。

### 异步传输层和客户端

#### 异步TCP传输

```python
from modbuslink import AsyncModbusClient, AsyncTcpTransport
import asyncio

# 创建异步TCP传输层
transport = AsyncTcpTransport(
    host='192.168.1.100',
    port=502,
    timeout=10.0
)

# 创建异步客户端
client = AsyncModbusClient(transport)

async def main():
    async with client:
        # 异步读取保持寄存器
        registers = await client.read_holding_registers(
            slave_id=1,
            start_address=0,
            quantity=10
        )
        print(f"寄存器: {registers}")
        
        # 异步写多个寄存器
        await client.write_multiple_registers(
            slave_id=1,
            start_address=0,
            values=[100, 200, 300, 400]
        )

asyncio.run(main())
```

#### 异步高级数据类型

```python
async def advanced_operations():
    async with client:
        # 异步32位浮点数操作
        await client.write_float32(slave_id=1, start_address=100, value=3.14159)
        temperature = await client.read_float32(slave_id=1, start_address=100)
        
        # 异步32位整数操作
        await client.write_int32(slave_id=1, start_address=102, value=-123456)
        counter = await client.read_int32(slave_id=1, start_address=102)
```

### 回调机制

异步客户端支持回调函数，用于操作完成通知：

```python
def on_registers_read(registers):
    print(f"回调: 读取了 {len(registers)} 个寄存器")

def on_write_completed():
    print("回调: 写入操作完成")

async def callback_demo():
    async with client:
        # 带回调的读取
        registers = await client.read_holding_registers(
            slave_id=1,
            start_address=0,
            quantity=5,
            callback=on_registers_read
        )
        
        # 带回调的写入
        await client.write_single_register(
            slave_id=1,
            address=0,
            value=1234,
            callback=on_write_completed
        )
```

### 并发操作

异步客户端支持并发操作，提升性能：

```python
async def concurrent_operations():
    async with client:
        # 创建多个并发任务
        tasks = [
            client.read_holding_registers(slave_id=1, start_address=0, quantity=5),
            client.read_coils(slave_id=1, start_address=0, quantity=8),
            client.read_input_registers(slave_id=1, start_address=0, quantity=5),
            client.write_single_register(slave_id=1, address=100, value=9999),
        ]
        
        # 并发执行所有任务
        results = await asyncio.gather(*tasks)
        print(f"并发结果: {results}")
```

### Modbus从站模拟器

#### 基本从站设置

```python
from modbuslink import ModbusSlave, DataStore

# 创建数据存储区
data_store = DataStore()

# 初始化数据
data_store.set_holding_registers(0, [1000, 2000, 3000, 4000, 5000])
data_store.set_coils(0, [True, False, True, False, True, False, True, False])
data_store.set_input_registers(0, [100, 200, 300, 400, 500])
data_store.set_discrete_inputs(0, [False, True, False, True, False, True])

# 创建从站
slave = ModbusSlave(slave_id=1, data_store=data_store)

# 启动TCP服务器
slave.start_tcp_server(host='127.0.0.1', port=5020)
print("从站模拟器已启动在 127.0.0.1:5020")

# 使用上下文管理器
with slave:
    # 从站在后台运行
    # 你的客户端代码在这里
    pass

# 或手动控制
slave.stop()
```

#### 数据存储区操作

```python
# 直接数据操作
data_store = DataStore()

# 设置保持寄存器
data_store.set_holding_registers(0, [1000, 2000, 3000])
registers = data_store.get_holding_registers(0, 3)

# 设置线圈
data_store.set_coils(0, [True, False, True, False])
coils = data_store.get_coils(0, 4)

# 设置输入寄存器（从客户端角度只读）
data_store.set_input_registers(0, [100, 200, 300])
input_regs = data_store.get_input_registers(0, 3)

# 设置离散输入（从客户端角度只读）
data_store.set_discrete_inputs(0, [True, False, True])
inputs = data_store.get_discrete_inputs(0, 3)
```

### 完整集成示例

```python
import asyncio
from modbuslink import (
    AsyncModbusClient, AsyncTcpTransport,
    ModbusSlave, DataStore
)

async def integration_demo():
    # 设置从站模拟器
    data_store = DataStore()
    data_store.set_holding_registers(0, [1000, 2000, 3000, 4000, 5000])
    
    slave = ModbusSlave(slave_id=1, data_store=data_store)
    slave.start_tcp_server(host='127.0.0.1', port=5020)
    
    # 设置异步客户端
    transport = AsyncTcpTransport(host='127.0.0.1', port=5020, timeout=5.0)
    client = AsyncModbusClient(transport)
    
    try:
        async with client:
            # 测试基本操作
            registers = await client.read_holding_registers(slave_id=1, start_address=0, quantity=5)
            print(f"读取寄存器: {registers}")
            
            # 测试写入操作
            await client.write_single_register(slave_id=1, address=0, value=9999)
            
            # 验证写入
            new_value = await client.read_holding_registers(slave_id=1, start_address=0, quantity=1)
            print(f"写入后: {new_value[0]}")
            
    finally:
        slave.stop()

asyncio.run(integration_demo())
```

## 开发计划

- [x] **第一阶段**: 构建坚实可靠的核心基础（同步MVP）
- [x] **第二阶段**: 提升易用性与开发者体验
- [x] **第三阶段**: 拥抱现代化：异步、回调与扩展
- [ ] **第四阶段**: 发布、测试与社区生态

## 许可证

MIT License - 详见 [LICENSE.txt](LICENSE.txt)

## 贡献

欢迎提交Issue和Pull Request！
