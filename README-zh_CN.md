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

## 🚀 为什么选择ModbusLink？

ModbusLink是专为**工业自动化**、**物联网应用**和**SCADA系统**设计的新一代Python Modbus库。采用现代化Python开发实践，在保持企业级可靠性的同时提供无与伦比的易用性。

### ✨ 核心特性

| 特性 | 描述 | 优势 |
|------|-----|------|
| 🏗️ **分层架构** | 关注点清晰分离 | 易于维护和扩展 |
| 🔌 **通用传输** | 支持TCP、RTU、ASCII | 兼容所有Modbus设备 |
| ⚡ **异步性能** | 原生asyncio支持 | 处理1000+并发连接 |
| 🛠️ **开发体验** | 直观API和完整类型提示 | 更快开发，更少bug |
| 📊 **丰富数据类型** | float32、int32、字符串等 | 处理复杂工业数据 |
| 🔍 **高级调试** | 协议级监控 | 快速故障排除 |
| 🖥️ **完整服务器** | 全功能服务器实现 | 构建自定义Modbus设备 |
| 🎯 **生产就绪** | 全面错误处理 | 放心部署 |

## 🚀 快速开始

### 安装

```bash
# 从 PyPI 安装
pip install modbuslink

# 或安装包含开发依赖的版本
pip install modbuslink[dev]
```

### 30秒快速体验

```python
from modbuslink import ModbusClient, TcpTransport

# 连接到Modbus TCP设备
transport = TcpTransport(host='192.168.1.100', port=502)
client = ModbusClient(transport)

with client:
    # 从保持寄存器读取温度
    temp = client.read_float32(slave_id=1, start_address=100)
    print(f"温度: {temp:.1f}°C")
    
    # 通过线圈控制水泵
    client.write_single_coil(slave_id=1, address=0, value=True)
    print("水泵已启动！")
```

## 📚 完整使用指南

### TCP客户端（以太网）

适用于**PLC**、**HMI**和**以太网设备**：

```python
from modbuslink import ModbusClient, TcpTransport

# 通过以太网连接PLC
transport = TcpTransport(
    host='192.168.1.10',
    port=502,
    timeout=5.0
)
client = ModbusClient(transport)

with client:
    # 读取生产计数器
    counter = client.read_int32(slave_id=1, start_address=1000)
    print(f"生产计数: {counter}")
    
    # 读取传感器数组
    sensors = client.read_holding_registers(slave_id=1, start_address=2000, quantity=10)
    print(f"传感器数值: {sensors}")
    
    # 更新设定值
    client.write_float32(slave_id=1, start_address=3000, value=75.5)
```

### RTU客户端（串口RS485/RS232）

适用于**现场仪表**、**传感器**和**传统设备**：

```python
from modbuslink import ModbusClient, RtuTransport

# 通过RS485连接现场设备
transport = RtuTransport(
    port='COM3',        # Linux: '/dev/ttyUSB0'
    baudrate=9600,
    parity='N',         # 无校验、偶校验、奇校验
    stopbits=1,
    timeout=2.0,
    rs485_mode=True     # 启用软件控制的RS485模式（RTS控制方向）
)
client = ModbusClient(transport)

with client:
    # 读取流量计
    flow_rate = client.read_float32(slave_id=5, start_address=0)
    print(f"流量: {flow_rate:.2f} L/min")
    
    # 读取压力变送器
    pressure_raw = client.read_input_registers(slave_id=6, start_address=0, quantity=1)[0]
    pressure_bar = pressure_raw / 100.0  # 转换为bar
    print(f"压力: {pressure_bar:.2f} bar")
```

### ASCII客户端（串口文本协议）

特殊应用和**调试**：

```python
from modbuslink import ModbusClient, AsciiTransport

# ASCII模式用于特殊设备
transport = AsciiTransport(
    port='COM1',
    baudrate=9600,
    bytesize=7,         # 7位ASCII
    parity='E',         # 偶校验
    timeout=3.0
)
client = ModbusClient(transport)

with client:
    # 读取实验室仪器
    temperature = client.read_float32(slave_id=2, start_address=100)
    print(f"实验室温度: {temperature:.3f}°C")
```

### 高性能异步操作

使用async/await**同时处理多个设备**：

```python
import asyncio
from modbuslink import AsyncModbusClient, AsyncTcpTransport

async def read_multiple_devices():
    """同时读取多个PLC数据"""
    
    # 创建到不同PLC的连接
    plc1 = AsyncModbusClient(AsyncTcpTransport('192.168.1.10', 502))
    plc2 = AsyncModbusClient(AsyncTcpTransport('192.168.1.11', 502))
    plc3 = AsyncModbusClient(AsyncTcpTransport('192.168.1.12', 502))
    
    async with plc1, plc2, plc3:
        # 同时读取所有PLC
        tasks = [
            plc1.read_holding_registers(1, 0, 10),    # 生产线1
            plc2.read_holding_registers(1, 0, 10),    # 生产线2
            plc3.read_holding_registers(1, 0, 10),    # 生产线3
        ]
        
        results = await asyncio.gather(*tasks)
        
        for i, data in enumerate(results, 1):
            print(f"PLC {i} 数据: {data}")

# 运行异步示例
asyncio.run(read_multiple_devices())
```

## 🖥️ Modbus服务器实现

使用ModbusLink强大的服务器功能**构建自己的Modbus设备**：

### TCP服务器（多客户端支持）

创建**HMI模拟器**、**设备仿真器**或**数据集中器**：

```python
from modbuslink import AsyncTcpModbusServer, ModbusDataStore
import asyncio

async def industrial_tcp_server():
    """模拟完整的工业控制系统"""
    
    # 为每种数据类型创建1000个点的数据存储
    data_store = ModbusDataStore(
        coils_size=1000,              # 数字输出（水泵、阀门）
        discrete_inputs_size=1000,    # 数字输入（传感器、开关）
        holding_registers_size=1000,  # 模拟输出（设定值）
        input_registers_size=1000     # 模拟输入（测量值）
    )
    
    # 初始化工业数据
    # 水泵和阀门控制
    data_store.write_coils(0, [True, False, True, False])
    
    # 过程设定值（温度、压力）
    data_store.write_holding_registers(0, [750, 1200, 850, 600])  # °C * 10
    
    # 传感器读数（模拟）
    data_store.write_input_registers(0, [748, 1195, 847, 598])   # 当前值
    
    # 安全联锁和限位开关
    data_store.write_discrete_inputs(0, [True, True, False, True])
    
    # 创建多客户端TCP服务器
    server = AsyncTcpModbusServer(
        host="0.0.0.0",          # 接受来自任何IP的连接
        port=502,                 # 标准Modbus端口
        data_store=data_store,
        slave_id=1,
        max_connections=50        # 支持多至50个HMI客户端
    )
    
    print("工业控制系统模拟器正在启动...")
    print("将您的HMI连接到: <您的IP>:502")
    print("从站地址: 1")
    
    try:
        await server.start()
        
        # 启动后台数据模拟
        simulation_task = asyncio.create_task(simulate_process_data(data_store))
        
        # 永久运行服务器
        await server.serve_forever()
        
    except KeyboardInterrupt:
        print("\n正在关闭服务器...")
        simulation_task.cancel()
    finally:
        await server.stop()

async def simulate_process_data(data_store):
    """模拟变化的过程数值"""
    import random
    
    while True:
        # 模拟温度波动
        temps = [random.randint(740, 760) for _ in range(4)]
        data_store.write_input_registers(0, temps)
        
        # 模拟压力变化
        pressures = [random.randint(1180, 1220) for _ in range(4)]
        data_store.write_input_registers(10, pressures)
        
        await asyncio.sleep(1.0)  # 每秒更新

# 运行服务器
asyncio.run(industrial_tcp_server())
```

### RTU服务器（串口现场设备）

仿真**现场仪表**和**智能传感器**：

```python
from modbuslink import AsyncRtuModbusServer, ModbusDataStore
import asyncio

async def smart_sensor_rtu():
    """模拟智能温度/压力传感器"""
    
    data_store = ModbusDataStore(
        holding_registers_size=100,   # 配置寄存器
        input_registers_size=100      # 测量数据
    )
    
    # 设备配置
    data_store.write_holding_registers(0, [
        250,    # 温度高报警 (°C * 10)
        -50,    # 温度低报警
        1500,   # 压力高报警 (mbar)
        500     # 压力低报警
    ])
    
    # 创建RTU现场设备
    server = AsyncRtuModbusServer(
        port="COM3",              # 串口
        baudrate=9600,
        parity="N",
        data_store=data_store,
        slave_id=15,              # 现场设备地址
        timeout=2.0
    )
    
    print("智能传感器RTU设备正在启动...")
    print(f"串口: COM3，波特率: 9600，从站地址: 15")
    
    try:
        await server.start()
        
        # 启动传感器模拟
        sensor_task = asyncio.create_task(simulate_sensor_readings(data_store))
        
        await server.serve_forever()
        
    except KeyboardInterrupt:
        print("\n传感器离线")
        sensor_task.cancel()
    finally:
        await server.stop()

async def simulate_sensor_readings(data_store):
    """模拟真实的传感器行为"""
    import random, math, time
    
    start_time = time.time()
    
    while True:
        elapsed = time.time() - start_time
        
        # 模拟日温度变化
        base_temp = 200 + 50 * math.sin(elapsed / 3600)  # 每小时周期
        temp = int(base_temp + random.uniform(-5, 5))     # 添加噪声
        
        # 模拟相关压力
        pressure = int(1000 + temp * 0.5 + random.uniform(-10, 10))
        
        # 更新输入寄存器
        data_store.write_input_registers(0, [temp, pressure])
        
        await asyncio.sleep(5.0)  # 每5秒更新

# 运行传感器
asyncio.run(smart_sensor_rtu())
```

### 多服务器部署

**同时运行多个服务器**实现复杂应用：

```python
from modbuslink import (
    AsyncTcpModbusServer,
    AsyncRtuModbusServer, 
    AsyncAsciiModbusServer,
    ModbusDataStore
)
import asyncio

async def multi_protocol_gateway():
    """创建多协议Modbus网关"""
    
    # 所有协议共享的数据存储
    shared_data = ModbusDataStore(
        coils_size=1000,
        discrete_inputs_size=1000,
        holding_registers_size=1000,
        input_registers_size=1000
    )
    
    # 初始化网关数据
    shared_data.write_holding_registers(0, list(range(100, 200)))
    
    # 创建多个服务器
    tcp_server = AsyncTcpModbusServer(
        host="0.0.0.0", port=502,
        data_store=shared_data, slave_id=1
    )
    
    rtu_server = AsyncRtuModbusServer(
        port="COM3", baudrate=9600,
        data_store=shared_data, slave_id=1
    )
    
    ascii_server = AsyncAsciiModbusServer(
        port="COM4", baudrate=9600,
        data_store=shared_data, slave_id=1
    )
    
    # 启动所有服务器
    servers = [tcp_server, rtu_server, ascii_server]
    
    try:
        # 并发启动服务器
        await asyncio.gather(
            *[server.start() for server in servers]
        )
        
        print("多协议网关已上线：")
        print("  • TCP: 0.0.0.0:502")
        print("  • RTU: COM3@9600")
        print("  • ASCII: COM4@9600")
        
        # 运行所有服务器
        await asyncio.gather(
            *[server.serve_forever() for server in servers]
        )
        
    except KeyboardInterrupt:
        print("\n正在关闭网关...")
    finally:
        await asyncio.gather(
            *[server.stop() for server in servers]
        )

# 运行网关
asyncio.run(multi_protocol_gateway())
```

## 📊 高级数据类型和工业应用

### 处理工业数据

ModbusLink为常见的工业数据格式提供**原生支持**：

```python
with client:
    # ✨ 32位 IEEE 754 浮点数
    # 适用于：温度、压力、流量、模拟测量
    client.write_float32(slave_id=1, start_address=100, value=25.67)  # 温度 °C
    temperature = client.read_float32(slave_id=1, start_address=100)
    print(f"过程温度: {temperature:.2f}°C")
    
    # 🔢 32位有符号整数
    # 适用于：计数器、生产计数、编码器位置
    client.write_int32(slave_id=1, start_address=102, value=-123456)
    position = client.read_int32(slave_id=1, start_address=102)
    print(f"编码器位置: {position} 脉冲")
    
    # 📝 字符串数据
    # 适用于：设备名称、报警消息、零件号
    client.write_string(slave_id=1, start_address=110, value="PUMP_001")
    device_name = client.read_string(slave_id=1, start_address=110, length=10)
    print(f"设备: {device_name}")
    
    # 🔄 字节序控制（对多供应商兼容性至关重要）
    # 处理不同PLC制造商
    
    # 西门子风格：大端序，高字在前
    client.write_float32(
        slave_id=1, start_address=200, value=3.14159,
        byte_order="big", word_order="high"
    )
    
    # 施耐德风格：小端序，低字在前
    client.write_float32(
        slave_id=1, start_address=202, value=3.14159,
        byte_order="little", word_order="low"
    )
```

### 真实的工业应用示例

```python
from modbuslink import ModbusClient, TcpTransport
import time

def monitor_production_line():
    """完整的生产线监控系统"""
    
    transport = TcpTransport(host='192.168.1.50', port=502, timeout=3.0)
    client = ModbusClient(transport)
    
    with client:
        print("🏭 生产线监控器已启动")
        print("=" * 50)
        
        while True:
            try:
                # 读取关键过程参数
                # 温度控制回路（PID设定值和过程值）
                temp_setpoint = client.read_float32(1, 1000)  # 设定值
                temp_actual = client.read_float32(1, 1002)    # 过程值
                
                # 生产计数器（32位整数）
                parts_produced = client.read_int32(1, 2000)
                
                # 质量指标（保持寄存器）
                quality_data = client.read_holding_registers(1, 3000, 5)
                reject_count = quality_data[0]
                efficiency = quality_data[1] / 100.0  # 转换为百分比
                
                # 系统状态（线圈）
                status_coils = client.read_coils(1, 0, 8)
                line_running = status_coils[0]
                emergency_stop = status_coils[1]
                
                # 显示实时数据
                print(f"\r🌡️  温度: {temp_actual:6.1f}°C (SP: {temp_setpoint:.1f})  "
                      f"🔢 产量: {parts_produced:6d}  "
                      f"🏆 效率: {efficiency:5.1f}%  "
                      f"🚨 状态: {'运行' if line_running else '停止'}", end="")
                
                # 自动质量控制
                if efficiency < 85.0:
                    print("\n⚠️  检测到低效率 - 正在调整参数...")
                    # 调整温度设定值
                    new_setpoint = temp_setpoint + 0.5
                    client.write_float32(1, 1000, new_setpoint)
                
                # 安全检查
                if temp_actual > 85.0:
                    print("\n🔥 超温报警！")
                    # 紧急停机
                    client.write_single_coil(1, 0, False)  # 停止生产线
                    break
                    
                time.sleep(1.0)
                
            except KeyboardInterrupt:
                print("\n🛱 用户停止监控")
                break
            except Exception as e:
                print(f"\n❌ 通信错误: {e}")
                time.sleep(5.0)  # 5秒后重试

# 运行监控系统
monitor_production_line()
```

## 🛡️ 生产级功能

### 全面的错误处理

**保障生产数据不丢失**，强大的错误管理：

```python
from modbuslink import (
    ModbusClient, TcpTransport,
    ConnectionError, TimeoutError, ModbusException, CRCError
)
import time

def resilient_data_collector():
    """生产级数据采集，全面错误处理"""
    
    transport = TcpTransport(host='192.168.1.100', port=502)
    client = ModbusClient(transport)
    
    retry_count = 0
    max_retries = 3
    
    while retry_count < max_retries:
        try:
            with client:
                # 关键数据采集
                production_data = client.read_holding_registers(1, 1000, 50)
                print(f"✅ 数据采集成功: {len(production_data)} 个数据点")
                return production_data
                
        except ConnectionError as e:
            print(f"🔌 网络连接失败: {e}")
            print("  • 检查网络线缆")
            print("  • 验证设备IP地址")
            print("  • 检查防火墙设置")
            
        except TimeoutError as e:
            print(f"⏱️ 操作超时: {e}")
            print("  • 网络可能拥塞")
            print("  • 设备可能过载")
            
        except CRCError as e:
            print(f"📊 检测到数据损坏: {e}")
            print("  • 检查串口线缆完整性")
            print("  • 验证波特率设置")
            
        except ModbusException as e:
            print(f"📝 协议错误: {e}")
            print("  • 无效的从站地址")
            print("  • 寄存器地址超出范围")
            print("  • 不支持的功能")
            
        except Exception as e:
            print(f"❌ 未知错误: {e}")
            
        # 指数退避重试
        retry_count += 1
        wait_time = 2 ** retry_count
        print(f"🔄 {wait_time}秒后重试... ({retry_count}/{max_retries})")
        time.sleep(wait_time)
    
    print("❌ 所有重试后仍无法采集数据")
    return None

# 在生产中使用
data = resilient_data_collector()
if data:
    print("正在处理数据...")
else:
    print("正在激活备用数据源...")
```

### 高级日志和调试

**调试通信问题**，协议级监控：

```python
from modbuslink.utils import ModbusLogger
import logging

# 设置全面日志
ModbusLogger.setup_logging(
    level=logging.DEBUG,
    enable_debug=True,
    log_file='modbus_debug.log',
    console_output=True
)

# 启用数据包级调试
ModbusLogger.enable_protocol_debug()

# 现在所有Modbus通信都被记录：
# 2024-08-30 10:15:23 [DEBUG] 发送: 01 03 00 00 00 0A C5 CD
# 2024-08-30 10:15:23 [DEBUG] 接收: 01 03 14 00 64 00 C8 01 2C 01 90 01 F4 02 58 02 BC 03 20 03 84 E5 C6
```

### 性能监控

```python
import asyncio
import time
from modbuslink import AsyncModbusClient, AsyncTcpTransport

async def performance_benchmark():
    """测量ModbusLink性能"""
    
    client = AsyncModbusClient(AsyncTcpTransport('192.168.1.100'))
    
    async with client:
        # 并发操作基准测试
        start_time = time.time()
        
        # 100个并发读取操作
        tasks = [
            client.read_holding_registers(1, i*10, 10) 
            for i in range(100)
        ]
        
        results = await asyncio.gather(*tasks)
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"🚀 性能结果：")
        print(f"  • 操作数: {len(tasks)}")
        print(f"  • 总时间: {duration:.2f} 秒")
        print(f"  • 操作/秒: {len(tasks)/duration:.1f}")
        print(f"  • 平均响应时间: {duration*1000/len(tasks):.1f} ms")

# 运行基准测试
asyncio.run(performance_benchmark())
```

## 📈 支持的Modbus功能

完整的**Modbus规范**实现：

| 功能码 | 名称 | 描述 | 使用场景 |
|---------|------|-----|--------|
| **0x01** | 读取线圈 | 读取1-2000个线圈状态 | 数字输出（水泵、阀门、电机） |
| **0x02** | 读取离散输入 | 读取1-2000个输入状态 | 数字传感器（限位开关、按钮） |
| **0x03** | 读取保持寄存器 | 读取1-125个寄存器值 | 模拟输出（设定值、参数） |
| **0x04** | 读取输入寄存器 | 读取1-125个输入值 | 模拟输入（温度、压力） |
| **0x05** | 写单个线圈 | 写入一个线圈 | 控制单个设备（启动水泵） |
| **0x06** | 写单个寄存器 | 写入一个寄存器 | 设置单个参数（温度设定值） |
| **0x0F** | 写多个线圈 | 写入1-1968个线圈 | 批量控制（生产序列） |
| **0x10** | 写多个寄存器 | 写入1-123个寄存器 | 批量参数（配方下载） |

### 传输层架构

ModbusLink的**分层设计**支持所有主流Modbus变种：

#### 同步传输
- 🌐 **TcpTransport**: 以太网Modbus TCP/IP (IEEE 802.3)
- 📞 **RtuTransport**: 串口Modbus RTU (RS232/RS485)，支持RS485模式
- 📜 **AsciiTransport**: 串口Modbus ASCII (7位文本)

#### 异步传输
- ⚡ **AsyncTcpTransport**: 高性能TCP（1000+并发连接）
- ⚡ **AsyncRtuTransport**: 非阻塞串口RTU，支持RS485模式
- ⚡ **AsyncAsciiTransport**: 非阻塞串口ASCII

#### RS485模式支持

对于不支持自动硬件流控的适配器，ModbusLink支持使用RTS/DTR信号进行**软件控制的RS485模式**：

```python
from modbuslink import RtuTransport, RS485Settings

# 基本RS485模式（RTS高电平发送，低电平接收）
transport = RtuTransport('/dev/ttyUSB0', baudrate=9600, rs485_mode=True)

# 针对特定硬件的自定义RS485设置
rs485_settings = RS485Settings(
    rts_level_for_tx=True,   # 发送时RTS高电平
    rts_level_for_rx=False,  # 接收时RTS低电平
    delay_before_tx=0.001,   # 发送前延迟1ms（用于收发器稳定）
    delay_before_rx=0.001,   # 接收前延迟1ms
)
transport = RtuTransport('/dev/ttyUSB0', rs485_mode=rs485_settings)
```

| RS485Settings参数 | 类型 | 默认值 | 说明 |
|------------------------|------|---------|-------------|
| `rts_level_for_tx` | bool | True | 发送期间RTS引脚电平 |
| `rts_level_for_rx` | bool | False | 接收期间RTS引脚电平 |
| `delay_before_tx` | float | 0.0 | 开始发送前的延迟（秒） |
| `delay_before_rx` | float | 0.0 | 开始接收前的延迟（秒） |

### 关键性能指标

| 指标 | 同步客户端 | 异步客户端 | 异步服务器 |
|------|-----------|------------|-----------|
| **吞吐量** | 100 操作/秒 | 1000+ 操作/秒 | 5000+ 操作/秒 |
| **连接数** | 1 | 1000+ | 1000+ |
| **内存使用** | 低 | 中等 | 中等 |
| **CPU使用** | 低 | 非常低 | 低 |
| **延迟** | 10-50ms | 5-20ms | 1-10ms |

## 📁 项目架构

**简洁、可维护、可扩展**的代码库结构：

```
ModbusLink/
├── src/modbuslink/
│   ├── client/                    # 📱 客户端层
│   │   ├── sync_client.py         # 同步Modbus客户端
│   │   └── async_client.py        # 带回调的异步客户端
│   │
│   ├── server/                    # 🖥️ 服务器层
│   │   ├── data_store.py          # 线程安全数据存储
│   │   ├── async_base_server.py   # 服务器基类
│   │   ├── async_tcp_server.py    # 多客户端TCP服务器
│   │   ├── async_rtu_server.py    # 串口RTU服务器
│   │   └── async_ascii_server.py  # 串口ASCII服务器
│   │
│   ├── transport/                 # 🚚 传输层
│   │   ├── base.py                # 同步传输接口
│   │   ├── async_base.py          # 异步传输接口
│   │   ├── tcp.py                 # TCP/IP实现
│   │   ├── rtu.py                 # RTU串口实现
│   │   ├── ascii.py               # ASCII串口实现
│   │   ├── async_tcp.py           # 带连接池的异步TCP
│   │   ├── async_rtu.py           # 带帧检测的异步RTU
│   │   └── async_ascii.py         # 带消息解析的异步ASCII
│   │
│   ├── utils/                     # 🔧 工具层
│   │   ├── crc.py                 # CRC16校验（RTU）
│   │   ├── coder.py               # 数据类型转换
│   │   └── logging.py             # 高级日志系统
│   │
│   └── common/                    # 🛠️ 通用组件
│       └── exceptions.py          # 自定义异常体系
│
├── examples/                      # 📚 使用示例
│   ├── sync_tcp_example.py        # 基本TCP客户端
│   ├── async_tcp_example.py       # 高性能异步客户端
│   ├── sync_rtu_example.py        # 串口RTU通信
│   ├── async_rtu_example.py       # 带错误恢复的异步RTU
│   ├── sync_ascii_example.py      # ASCII模式调试
│   ├── async_ascii_example.py     # 异步ASCII通信
│   ├── async_tcp_server_example.py    # 多客户端TCP服务器
│   ├── async_rtu_server_example.py    # RTU现场设备模拟器
│   ├── async_ascii_server_example.py  # ASCII设备仿真器
│   └── multi_server_example.py        # 多协议网关
│
└── docs/                          # 📜 文档
    ├── api/                       # API参考
    ├── guides/                    # 用户指南
    └── examples/                  # 高级示例
```

## 📚 示例

在[examples](examples/)目录中探索**真实世界的场景**：

### 🔄 同步示例
- **工业控制**: PLC和现场设备的基本同步操作
- **数据采集**: 从传感器可靠采集数据
- **设备配置**: 参数设置和校准

### ⚡ 异步示例
- **SCADA系统**: 多个设备的高性能监控
- **物联网网关**: 与数百个传感器的并发通信
- **实时控制**: 亚毫秒响应应用

### 🖥️ 服务器示例
- **设备模拟器**: 无需物理硬件测试HMI应用
- **协议网关**: 桥接不同Modbus变种
- **培训系统**: 教育用Modbus实验室搭建

### 🎆 高级功能
- **多协议**: 同时运行TCP、RTU和ASCII服务器
- **错误恢复**: 自动重连和重试逻辑
- **性能调优**: 针对特定用例的优化
- **生产部署**: 24/7运行的最佳实践

## ⚙️ 系统要求

### 核心要求
- **Python**: 3.8+（建议3.9+以获得最佳性能）
- **操作系统**: Windows、Linux、macOS
- **内存**: 最低64MB RAM
- **网络**: Modbus TCP需要TCP/IP协议栈
- **串口**: RTU/ASCII需要RS232/RS485

### 依赖
```bash
# 核心依赖（自动安装）
pyserial >= 3.5          # 串口通信
pyserial-asyncio >= 0.6   # 异步串口支持
typing_extensions >= 4.0.0 # 增强类型提示

# 开发依赖（可选）
pytest >= 7.0             # 单元测试
pytest-mock >= 3.0        # 测试模拟
black >= 22.0             # 代码格式化
ruff >= 0.1.0             # 代码检查
mypy >= 1.0               # 类型检查
```

### 性能建议
- **CPU**: 异步服务器建议多核（2核+）
- **网络**: 高吞吐量TCP应用建议千兆以太网
- **串口**: 使用FTDI芯片的USB转RS485转换器
- **Python**: 使用CPython获得最佳性能（串口I/O避免PyPy）

## 📜 许可证和贡献

**MIT许可证** - 可商用。详见[LICENSE.txt](LICENSE.txt)。

### 贡献指南

**欢迎贡献！**请：

1. 🍿 **Fork**仓库
2. 🌱 **创建**功能分支
3. ✨ **添加**新功能测试
4. 📝 **更新**文档
5. 🚀 **提交**拉取请求

**我们需要帮助的领域：**
- 额外的Modbus功能码（0x14, 0x15, 0x16, 0x17）
- 性能优化
- 额外的传输协议（Modbus Plus等）
- 文档改进
- 真实世界测试和bug报告

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
