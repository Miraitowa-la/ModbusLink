# ModbusLink

<div align="center">

[![PyPI 下载量](https://static.pepy.tech/badge/modbuslink)](https://pepy.tech/projects/modbuslink)
[![PyPI 版本](https://badge.fury.io/py/modbuslink.svg)](https://badge.fury.io/py/modbuslink)
[![Python 版本](https://img.shields.io/pypi/pyversions/modbuslink.svg)](https://pypi.org/project/modbuslink/)
[![许可证](https://img.shields.io/github/license/Miraitowa-la/ModbusLink)](LICENSE.txt)

**现代化、高性能的Python Modbus库**

*工业级 • 开发者友好 • 生产就绪*

[English](README.md) | [中文版](#) | [文档](https://miraitowa-la.github.io/ModbusLink/zh/index.html) | [示例](#examples)

</div>

---

## ✨ ModbusLink 简单介绍

**ModbusLink** 是一个专为现代工业自动化设计的 Python Modbus 协议库。它摒弃了传统库的复杂性，采用了清晰的分层架构（传输层与应用层分离）和现代化的
Python 特性（Type Hints, Asyncio）。

无论是构建高性能的 **TCP 服务器**，还是开发连接多个传感器的 **RTU 客户端**，ModbusLink 都能提供稳健、高效的支持。

### 核心特性

- **完全异步支持**：基于 Python 原生 `asyncio`，轻松处理高并发连接，同时也提供完善的**同步**接口。
- **架构解耦**：传输层（Transport）与协议层（Client/Server）分离，支持依赖注入，易于测试和扩展。
- **双语支持**：内置中/英双语日志和异常提示，通过 `language` 模块一键切换。
- **类型安全**：代码库全覆盖 Type Hints，配合 IDE 提供极佳的开发体验。
- **协议全面**：支持 Modbus TCP、RTU、ASCII 协议，覆盖客户端（Master）和服务器（Slave）模式。
- **高级编解码**：内置 `PayloadCoder`，轻松读写 Float32, Int64, String 等复杂数据类型。

---

## 📝 版本说明

- `1.2.x` 及其以前
    - 不建议使用
- `1.3.x`
    - [`1.3.0`](notes/1.3.0.md) RS485模式支持( #1 )
    - [`1.3.1`](notes/1.3.1.md) 日志语言切换支持( #2 )
    - [`1.3.2`](notes/1.3.2.md) 语言切换支持优化( #2 )
    - [`1.3.3`](notes/1.3.3.md) 异步客户端缺失函数添加( #3 )
    - [`1.3.4`](notes/1.3.4.md) 异步并发安全修复( #4 )
- `1.4.x`
    - [`1.4.0`](notes/1.4.0.md) 重构: 解决项目冗余问题，统一命名规范，并提升核心组件的性能与稳定性
    - [`1.4.1`](notes/1.4.1.md) RS485 模式支持恢复
    - [`1.4.2`](notes/1.4.2.md) TCP 传输层 flush() 方法 - 解决超时后事务ID不匹配问题
- `1.5.x` (根据 SemVer 规范进行了更新)
    - [`1.5.0`](notes/1.5.0.md) 增加 RTU/ASCII 传输层 flush() 方法
    - [`1.5.1`](notes/1.5.1.md) TCP 传输层增加 connection_timeout 参数
    - [`1.5.2`](notes/1.5.2.md) 修复传输层连接状态检查，并将生成的 egg-info 文件移出 Git
---

## 🚀 快速开始

### 软件包安装

使用 pip 安装最新版本：

```bash
pip install modbuslink
```

### 30秒快速体验

以下是一个简单的同步 TCP 客户端示例，读取保持寄存器：

```python
from modbuslink.client import SyncModbusClient
from modbuslink.transport import SyncTcpTransport

# 1. 创建传输层实例
transport = SyncTcpTransport(host='127.0.0.1', port=502)

# 2. 创建客户端实例（依赖注入）
with SyncModbusClient(transport) as client:
    # 3. 读取地址 0 开始的 10 个保持寄存器 (从站ID: 1)
    data = client.read_holding_registers(slave_id=1, start_address=0, quantity=10)
    print(f"读取结果: {data}")
```

---

## 📚 完整使用指南

ModbusLink 的设计核心是 **“解耦”**。客户端逻辑（`Client`）与通信方式（`Transport`）是分离的。这意味着您需要先实例化一个传输层对象，然后将其传递给客户端对象。

### 1.TCP客户端

适用于通过以太网（Modbus TCP）连接 PLC 或仪表。

**注意**：自 `v1.5.1` 起，TCP 传输层支持可选的 `connection_timeout` 参数，用于独立控制连接建立超时和数据操作超时。这在需要快速失败连接但允许较长时间数据操作的环境中非常有用。

```python
# 示例：快速连接，慢速数据操作
from modbuslink.transport import SyncTcpTransport

transport = SyncTcpTransport(
    host='192.168.1.10',
    port=502,
    timeout=10.0,              # 数据操作超时（发送/接收）
    connection_timeout=3.0      # 连接建立超时
)
```

#### TCP 同步客户端 (Sync)

最符合直觉的编程方式，适合简单的脚本或非高并发应用。

```python
from modbuslink.client import SyncModbusClient
from modbuslink.transport import SyncTcpTransport


def main():
    # 1. 配置传输层 (IP 和 端口)
    transport = SyncTcpTransport(host='192.168.1.10', port=502, timeout=2.0)

    # 2. 注入传输层创建客户端
    with SyncModbusClient(transport) as client:
        print("连接成功！")

        # 读取 10 个保持寄存器 (功能码 0x03)
        # slave_id: 从站单元ID (TCP中通常为1或255)
        regs = client.read_holding_registers(slave_id=1, start_address=100, quantity=10)
        print(f"寄存器值: {regs}")

        # 写入单个线圈 (功能码 0x05)
        client.write_single_coil(slave_id=1, address=0, value=True)
        print("线圈写入完成")


if __name__ == "__main__":
    main()
```

#### TCP 异步客户端 (Async)

基于 `asyncio`，适合需要高性能、高并发或集成到 FastAPI/GUI 应用的场景。

```python
import asyncio
from modbuslink.client import AsyncModbusClient
from modbuslink.transport import AsyncTcpTransport


async def main():
    # 1. 配置异步传输层
    transport = AsyncTcpTransport(host='192.168.1.10', port=502)

    # 2. 使用 async with 自动管理连接
    async with AsyncModbusClient(transport) as client:
        # 读取浮点数 (自动处理 2个寄存器的合并与解码)
        # 支持指定字节序，默认为 Big Endian
        temp = await client.read_float32(slave_id=1, start_address=200)
        print(f"当前温度: {temp:.2f}°C")

        # 写入多个寄存器
        await client.write_multiple_registers(slave_id=1, start_address=300, values=[10, 20, 30])


if __name__ == "__main__":
    asyncio.run(main())
```

### 2.RTU客户端

适用于通过 RS485/RS232 串口连接工业设备。

#### RTU 同步客户端 (Sync)

```python
from modbuslink.client import SyncModbusClient
from modbuslink.transport import SyncRtuTransport

# 1. 配置串口参数
transport = SyncRtuTransport(
    port='COM3',  # Windows: COMx, Linux: /dev/ttyUSBx
    baudrate=9600,
    bytesize=8,
    parity='N',
    stopbits=1,
    timeout=1.0
)

# 2. 创建客户端
with SyncModbusClient(transport) as client:
    # 读取输入寄存器 (功能码 0x04)
    data = client.read_input_registers(slave_id=1, start_address=0, quantity=5)
    print(f"传感器数据: {data}")
```

#### RTU 异步客户端 (Async)

在等待串口 IO 时不会阻塞主线程。

```python
import asyncio
from modbuslink.client import AsyncModbusClient
from modbuslink.transport import AsyncRtuTransport


async def main():
    # 异步串口传输层
    transport = AsyncRtuTransport(port='/dev/ttyUSB0', baudrate=115200)

    async with AsyncModbusClient(transport) as client:
        # 写入 32位 整数 (自动编码为 2 个寄存器)
        await client.write_int32(slave_id=2, start_address=10, value=50000)
        print("参数设置成功")


if __name__ == "__main__":
    asyncio.run(main())
```

### 3.ASCII 客户端

适用于某些老旧设备，数据以 ASCII 字符形式传输。

#### ASCII 同步客户端 (Sync)

```python
from modbuslink.client import SyncModbusClient
from modbuslink.transport import SyncAsciiTransport

# 配置为 ASCII 模式，通常数据位是 7 位
transport = SyncAsciiTransport(port='COM1', baudrate=9600, bytesize=7, parity='E', stopbits=1)

with SyncModbusClient(transport) as client:
    # 读线圈
    status = client.read_coils(slave_id=1, start_address=0, quantity=8)
    print(f"设备状态: {status}")
```

#### ASCII 异步客户端 (Async)

```python
import asyncio
from modbuslink.client import AsyncModbusClient
from modbuslink.transport import AsyncAsciiTransport


async def main():
    transport = AsyncAsciiTransport(port='/dev/ttyS0', baudrate=9600)

    async with AsyncModbusClient(transport) as client:
        # 写字符串 (ModbusLink 会自动将其编码并存入寄存器)
        await client.write_string(slave_id=1, start_address=100, value="HELLO")


if __name__ == "__main__":
    asyncio.run(main())
```

### 4. 客户端 RS485 模式

适用于 RS485 通信模式，通常需要配置额外的控制线（DE/RE）。
`SyncRtuTransport`/`AsyncRtuTransport`/`SyncAsciiTransport`/`AsyncAsciiTransport` 都可配置RS485模式

```python
# 同步RTU客户端为例（其他客户端只需要修改 "SyncRtuTransport" 即可）
from serial.rs485 import RS485Settings
from modbuslink import SyncRtuTransport

rs485_settings = RS485Settings(
    rts_level_for_tx=True,
    rts_level_for_rx=False,
    delay_before_tx=0.001,
    delay_before_rx=0.001,
)
transport = SyncRtuTransport('/dev/ttyUSB0', rs485_mode=rs485_settings)
```

### 5. 服务器示例

ModbusLink 的服务器实现均基于异步 IO，能够高效处理多客户端并发（TCP）或快速响应（RTU/ASCII）。

#### TCP 服务器

创建一个在本地 502 端口监听的服务器，带有数据回调功能。

```python
import asyncio
from modbuslink.server import AsyncTcpModbusServer, ModbusDataStore


async def run_server():
    # 1. 初始化数据存储 (定义寄存器大小)
    store = ModbusDataStore(
        coils_size=1000,
        holding_registers_size=1000
    )

    # 2. 设置初始数据
    store.write_holding_registers(address=0, values=[123, 456, 789])

    # 3. 添加回调：当客户端写入保持寄存器时触发
    def on_register_write(address, values):
        print(f"[回调] 客户端写入寄存器 @ {address}: {values}")

    store.add_callback('holding_registers', on_register_write)

    # 4. 启动服务器
    server = AsyncTcpModbusServer(host='0.0.0.0', port=502, data_store=store)

    print("TCP 服务器已启动，正在监听 502 端口...")
    try:
        await server.serve_forever()
    except asyncio.CancelledError:
        await server.stop()


if __name__ == "__main__":
    asyncio.run(run_server())
```

#### RTU 服务器

将计算机变成一个 Modbus RTU 从站设备。

```python
import asyncio
from modbuslink.server import AsyncRtuModbusServer, ModbusDataStore


async def run_server():
    store = ModbusDataStore()

    # 初始化串口服务器
    # slave_id: 本机作为从站的地址
    server = AsyncRtuModbusServer(
        port='COM4',
        baudrate=9600,
        slave_id=1,
        data_store=store
    )

    print("RTU 服务器运行中...")
    await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(run_server())
```

#### ASCII 服务器

```python
import asyncio
from modbuslink.server import AsyncAsciiModbusServer, ModbusDataStore


async def run_server():
    store = ModbusDataStore()

    server = AsyncAsciiModbusServer(
        port='/dev/ttyUSB0',
        baudrate=9600,
        slave_id=1,
        data_store=store
    )

    print("ASCII 服务器运行中...")
    await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(run_server())
```

### 高级技巧：并发采集多个设备

这是 ModbusLink 最强大的功能之一。使用 `asyncio`，您可以同时等待多个设备的 IO 响应，而不是一个接一个地串行等待，极大地缩短了总轮询时间。

```python
import asyncio
from modbuslink.client import AsyncModbusClient
from modbuslink.transport import AsyncTcpTransport


async def collect_data(device_ip, slave_id):
    """采集单个设备的逻辑"""
    transport = AsyncTcpTransport(host=device_ip, port=502)
    async with AsyncModbusClient(transport) as client:
        try:
            # 读取数据
            data = await client.read_holding_registers(slave_id, 0, 10)
            return {"ip": device_ip, "data": data, "status": "ok"}
        except Exception as e:
            return {"ip": device_ip, "error": str(e), "status": "error"}


async def main():
    # 假设有 3 台设备
    devices = ["192.168.1.101", "192.168.1.102", "192.168.1.103"]

    # 1. 创建任务列表
    tasks = [collect_data(ip, slave_id=1) for ip in devices]

    print("开始并发采集...")
    # 2. 并发执行 (gather)
    results = await asyncio.gather(*tasks)

    # 3. 处理结果
    for res in results:
        print(res)


if __name__ == "__main__":
    asyncio.run(main())
```

### 高级技巧：错误恢复与缓冲区清空

在不稳定的网络环境中，设备可能偶尔响应缓慢导致超时。ModbusLink 提供了 `flush()` 方法来清空接收缓冲区中的陈旧数据，防止"迟到"的响应影响后续请求。

#### 同步客户端错误恢复

```python
from modbuslink.client import SyncModbusClient
from modbuslink.transport import SyncTcpTransport
from modbuslink import TimeOutError, InvalidReplyError


def robust_read():
    """带错误恢复的稳健读取"""
    transport = SyncTcpTransport(host='192.168.1.100', port=502, timeout=2.0)
    client = SyncModbusClient(transport)

    with client:
        try:
            # 尝试读取数据
            data = client.read_holding_registers(slave_id=1, start_address=0, quantity=10)
            return data
        except (TimeOutError, InvalidReplyError) as e:
            print(f"错误: {e}")

            # 清空接收缓冲区，丢弃陈旧数据
            discarded = transport.flush()
            print(f"已清空 {discarded} 字节的陈旧数据")

            # 重试
            data = client.read_holding_registers(slave_id=1, start_address=0, quantity=10)
            return data
```

#### 异步客户端 - Home Assistant 集成模式

适用于需要长期稳定运行的场景，如 Home Assistant 集成：

```python
import asyncio
from modbuslink.client import AsyncModbusClient
from modbuslink.transport import AsyncTcpTransport
from modbuslink import TimeOutError, InvalidReplyError


async def home_assistant_polling():
    """Home Assistant 风格的设备轮询"""
    transport = AsyncTcpTransport(host='192.168.1.100', port=502, timeout=3.0)
    client = AsyncModbusClient(transport)

    poll_interval = 60  # 每60秒轮询一次
    max_consecutive_errors = 3
    consecutive_errors = 0

    async with client:
        while True:
            try:
                # 读取设备数据
                data = await client.read_holding_registers(
                    slave_id=1,
                    start_address=0,
                    quantity=10
                )

                print(f"设备数据: {data}")
                consecutive_errors = 0  # 成功后重置错误计数

            except TimeOutError:
                consecutive_errors += 1
                print(f"超时 (连续错误: {consecutive_errors}/{max_consecutive_errors})")

                # 清空缓冲区，防止陈旧响应影响下次请求
                discarded = await transport.flush()
                if discarded > 0:
                    print(f"清空了 {discarded} 字节的陈旧数据")

                # 连续错误过多时重新连接
                if consecutive_errors >= max_consecutive_errors:
                    print("连续错误过多，重新连接...")
                    await transport.close()
                    await asyncio.sleep(1)
                    await transport.open()
                    consecutive_errors = 0

            except InvalidReplyError as e:
                print(f"无效响应: {e}")
                # 事务ID不匹配时清空缓冲区
                await transport.flush()

            # 等待下次轮询
            await asyncio.sleep(poll_interval)


if __name__ == "__main__":
    asyncio.run(home_assistant_polling())
```

---

## 🛡️ 生产级功能

### 全面的错误处理

ModbusLink 定义了清晰的异常层级，方便在工业现场进行故障诊断：

- ConnectError: 连接失败（网络中断、串口被占用）。
- TimeOutError: 设备响应超时。
- CrcError / LrcError: 数据校验失败，自动过滤噪声。
- ModbusException: 设备返回的功能异常（如非法地址 0x02）。

### 高级日志和调试

内置双语日志系统，支持协议级 HEX 调试模式：

```python
from modbuslink.common.logging import ModbusLogger

# 启用调试模式，输出原始数据帧
ModbusLogger.setup_logging(enable_debug=True, language="CN")
ModbusLogger.enable_protocol_debug()
```

### 性能基准测试

ModbusLink 的异步核心设计使其能够轻松处理高并发场景。以下代码演示了如何利用 `asyncio` 在几秒钟内完成数百次 Modbus 请求：

```python
import asyncio
import time
from modbuslink.client import AsyncModbusClient
from modbuslink.transport import AsyncTcpTransport


async def performance_benchmark():
    """测量 ModbusLink 极限性能"""

    # 连接到高性能 Modbus 模拟器或服务器
    transport = AsyncTcpTransport(host='127.0.0.1', port=502)
    client = AsyncModbusClient(transport)

    async with client:
        print("开始基准测试...")
        start_time = time.time()

        # 创建 100 个并发读取任务 (非阻塞)
        # 这里的关键是：所有请求几乎同时发出，而不是一个接一个
        tasks = [
            client.read_holding_registers(slave_id=1, start_address=i, quantity=1)
            for i in range(100)
        ]

        # 等待所有任务完成
        results = await asyncio.gather(*tasks)

        end_time = time.time()
        duration = end_time - start_time

        # 统计结果
        print(f"性能结果：")
        print(f"  • 并发操作数: {len(tasks)}")
        print(f"  • 总耗时: {duration:.3f} 秒")
        print(f"  • 吞吐量: {len(tasks) / duration:.1f} Ops/s")
        print(f"  • 平均响应: {duration * 1000 / len(tasks):.2f} ms")


if __name__ == "__main__":
    asyncio.run(performance_benchmark())
```

---

---

## 📈 支持的Modbus功能

完整的**Modbus规范**实现：

| 功能码      | 名称      | 描述            | 使用场景           |
|----------|---------|---------------|----------------|
| **0x01** | 读取线圈    | 读取1-2000个线圈状态 | 数字输出（水泵、阀门、电机） |
| **0x02** | 读取离散输入  | 读取1-2000个输入状态 | 数字传感器（限位开关、按钮） |
| **0x03** | 读取保持寄存器 | 读取1-125个寄存器值  | 模拟输出（设定值、参数）   |
| **0x04** | 读取输入寄存器 | 读取1-125个输入值   | 模拟输入（温度、压力）    |
| **0x05** | 写单个线圈   | 写入一个线圈        | 控制单个设备（启动水泵）   |
| **0x06** | 写单个寄存器  | 写入一个寄存器       | 设置单个参数（温度设定值）  |
| **0x0F** | 写多个线圈   | 写入1-1968个线圈   | 批量控制（生产序列）     |
| **0x10** | 写多个寄存器  | 写入1-123个寄存器   | 批量参数（配方下载）     |

---

## 📁 项目架构

**简洁、可维护、可扩展**的代码库结构：

```
ModbusLink/
├── src/modbuslink/
│   ├── client/                    # 📱 客户端层
│   │   ├── sync_client.py         # 同步Modbus客户端
│   │   └── async_client.py        # 异步Modbus客户端
│   │
│   ├── server/                    # 🖥️ 服务器层
│   │   ├── data_store.py          # 数据存储类
│   │   ├── base_server.py         # 服务器基类
│   │   ├── tcp_server.py          # TCP服务器
│   │   ├── rtu_server.py          # RTU服务器
│   │   └── ascii_server.py        # ASCII服务器
│   │
│   ├── transport/                 # 🚚 传输层
│   │   ├── base_transport.py      # 同步/异步传输接口
│   │   ├── tcp_transport.py       # 同步/异步的TCP/实现
│   │   ├── rtu_transport.py       # 同步/异步的RTU实现
│   │   └── ascii_transport.py     # 同步/异步的ASCII实现
│   │
│   ├── utils/                     # 🔧 工具层
│   │   ├── crc.py                 # CRC16校验（RTU）
│   │   ├── lrc.py                 # LRC校验（ASCII）
│   │   └── coder.py               # 数据类型转换
│   │
│   └── common/                    # 🛠️ 通用组件
│       ├── language.py            # 统一语言配置
│       ├── exceptions.py          # 自定义异常体系
│       └── logging.py             # 高级日志系统
│
├── examples/                      # 📚 使用示例
│   ├── sync_tcp_example.py        # 同步TCP客户端示例
│   ├── async_tcp_example.py       # 异步TCP客户端示例
│   ├── sync_rtu_example.py        # 同步RTU客户端示例
│   ├── async_rtu_example.py       # 异步RTU客户端示例
│   ├── sync_ascii_example.py      # 同步ASCII客户端示例
│   ├── async_ascii_example.py     # 异步ASCII客户端示例
│   ├── async_tcp_server_example.py    # TCP服务器示例
│   ├── async_rtu_server_example.py    # RTU服务器示例
│   └── async_ascii_server_example.py  # ASCII服务器示例
│
└── docs/                          # 📜 文档
```

---

## 📚 示例

在[examples](examples/)目录中探索**真实世界的场景**：

---

## ⚙️ 系统要求

- Python: 3.9 或更高版本
- 依赖库:
    - `pyserial >= 3.5`: 串口通信基础
    - `pyserial-asyncio >= 0.6`: 异步串口支持
    - `typing_extensions`: 类型兼容性支持
- 操作系统: Windows, Linux, macOS (跨平台支持)

---

---

## 📜 许可证和贡献

**MIT许可证** - 可商用。详见[LICENSE.txt](LICENSE.txt)。

### 贡献指南

**欢迎贡献！**请：

1. 🍿 **Fork**仓库
2. 🌱 **创建**功能分支
3. ✨ **添加**新功能测试
4. 📝 **更新**文档
5. 🚀 **提交**拉取请求

### 社区和支持

- 💬 **GitHub Issues**: bug报告和功能请求
- 📧 **邮件支持**: 技术问题和咨询
- 📚 **文档**: 全面指南和API参考
- 🎆 **示例**: 生产就绪代码样本

---

<div align="center">

**为工业自动化社区精心打造 ❤️**

*ModbusLink - 用现代Python连接工业系统*

</div>
