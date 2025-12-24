# ModbusLink

<div align="center">

[![PyPI Downloads](https://static.pepy.tech/badge/modbuslink)](https://pepy.tech/projects/modbuslink)
[![PyPI version](https://badge.fury.io/py/modbuslink.svg)](https://badge.fury.io/py/modbuslink)
[![Python Version](https://img.shields.io/pypi/pyversions/modbuslink.svg)](https://pypi.org/project/modbuslink/)
[![License](https://img.shields.io/github/license/Miraitowa-la/ModbusLink)](LICENSE.txt)

**A Modern, High-Performance Python Modbus Library**

*Industrial-grade • Developer-friendly • Production-ready*

[English](#) | [中文版](README-zh_CN.md) | [Documentation](https://miraitowa-la.github.io/ModbusLink/en/index.html) | [Examples](#examples)

</div>

---

## 🚀 Why ModbusLink?

ModbusLink is a next-generation Python Modbus library designed for **industrial automation**, **IoT applications**, and **SCADA systems**. Built with modern Python practices, it provides unparalleled ease of use while maintaining enterprise-grade reliability.

### ✨ Key Features

| Feature | Description | Benefit |
|---------|-------------|----------|
| 🏗️ **Layered Architecture** | Clean separation of concerns | Easy maintenance & extension |
| 🔌 **Universal Transports** | TCP, RTU, ASCII support | Works with any Modbus device |
| ⚡ **Async Performance** | Native asyncio support | Handle 1000+ concurrent connections |
| 🛠️ **Developer Experience** | Intuitive APIs & full typing | Faster development & fewer bugs |
| 📊 **Rich Data Types** | float32, int32, strings & more | Handle complex industrial data |
| 🔍 **Advanced Debugging** | Protocol-level monitoring | Rapid troubleshooting |
| 🖥️ **Complete Server** | Full server implementation | Build custom Modbus devices |
| 🎯 **Production Ready** | Comprehensive error handling | Deploy with confidence |

## 🚀 Quick Start

### Installation

```bash
# Install from PyPI
pip install modbuslink

# Or install with development dependencies
pip install modbuslink[dev]
```

### 30-Second Demo

```python
from modbuslink import ModbusClient, TcpTransport

# Connect to Modbus TCP device
transport = TcpTransport(host='192.168.1.100', port=502)
client = ModbusClient(transport)

with client:
    # Read temperature from holding registers
    temp = client.read_float32(slave_id=1, start_address=100)
    print(f"Temperature: {temp:.1f}°C")
    
    # Control pump via coil
    client.write_single_coil(slave_id=1, address=0, value=True)
    print("Pump started!")
```

## 📚 Complete Usage Guide

### TCP Client (Ethernet)

Perfect for **PLCs**, **HMIs**, and **Ethernet-based devices**:

```python
from modbuslink import ModbusClient, TcpTransport

# Connect to PLC via Ethernet
transport = TcpTransport(
    host='192.168.1.10',
    port=502,
    timeout=5.0
)
client = ModbusClient(transport)

with client:
    # Read production counter
    counter = client.read_int32(slave_id=1, start_address=1000)
    print(f"Production count: {counter}")
    
    # Read sensor array
    sensors = client.read_holding_registers(slave_id=1, start_address=2000, quantity=10)
    print(f"Sensor values: {sensors}")
    
    # Update setpoint
    client.write_float32(slave_id=1, start_address=3000, value=75.5)
```

### RTU Client (Serial RS485/RS232)

Ideal for **field instruments**, **sensors**, and **legacy devices**:

```python
from modbuslink import ModbusClient, RtuTransport

# Connect to field device via RS485
transport = RtuTransport(
    port='COM3',        # Linux: '/dev/ttyUSB0'
    baudrate=9600,
    parity='N',         # None, Even, Odd
    stopbits=1,
    timeout=2.0,
    rs485_mode=True     # Enable software-controlled RS485 (RTS for direction)
)
client = ModbusClient(transport)

with client:
    # Read flow meter
    flow_rate = client.read_float32(slave_id=5, start_address=0)
    print(f"Flow rate: {flow_rate:.2f} L/min")
    
    # Read pressure transmitter
    pressure = client.read_input_registers(slave_id=6, start_address=0, quantity=1)[0]
    pressure_bar = pressure / 100.0  # Convert to bar
    print(f"Pressure: {pressure_bar:.2f} bar")
```

### ASCII Client (Serial Text Protocol)

Special applications and **debugging**:

```python
from modbuslink import ModbusClient, AsciiTransport

# ASCII mode for special devices
transport = AsciiTransport(
    port='COM1',
    baudrate=9600,
    bytesize=7,         # 7-bit ASCII
    parity='E',         # Even parity
    timeout=3.0
)
client = ModbusClient(transport)

with client:
    # Read laboratory instrument
    temperature = client.read_float32(slave_id=2, start_address=100)
    print(f"Lab temperature: {temperature:.3f}°C")
```

### High-Performance Async Operations

**Handle multiple devices simultaneously** with async/await:

```python
import asyncio
from modbuslink import AsyncModbusClient, AsyncTcpTransport

async def read_multiple_devices():
    """Read from multiple PLCs concurrently"""
    
    # Create connections to different PLCs
    plc1 = AsyncModbusClient(AsyncTcpTransport('192.168.1.10', 502))
    plc2 = AsyncModbusClient(AsyncTcpTransport('192.168.1.11', 502))
    plc3 = AsyncModbusClient(AsyncTcpTransport('192.168.1.12', 502))
    
    async with plc1, plc2, plc3:
        # Read all PLCs simultaneously
        tasks = [
            plc1.read_holding_registers(1, 0, 10),    # Production line 1
            plc2.read_holding_registers(1, 0, 10),    # Production line 2
            plc3.read_holding_registers(1, 0, 10),    # Production line 3
        ]
        
        results = await asyncio.gather(*tasks)
        
        for i, data in enumerate(results, 1):
            print(f"PLC {i} data: {data}")

# Run async example
asyncio.run(read_multiple_devices())
```

## 🖥️ Modbus Server Implementation

**Build your own Modbus devices** with ModbusLink's powerful server capabilities:

### TCP Server (Multi-Client Support)

Create **HMI simulators**, **device emulators**, or **data concentrators**:

```python
from modbuslink import AsyncTcpModbusServer, ModbusDataStore
import asyncio

async def industrial_tcp_server():
    """Simulate a complete industrial control system"""
    
    # Create data store for 1000 points each
    data_store = ModbusDataStore(
        coils_size=1000,              # Digital outputs (pumps, valves)
        discrete_inputs_size=1000,    # Digital inputs (sensors, switches)
        holding_registers_size=1000,  # Analog outputs (setpoints)
        input_registers_size=1000     # Analog inputs (measurements)
    )
    
    # Initialize industrial data
    # Pump and valve controls
    data_store.write_coils(0, [True, False, True, False])
    
    # Process setpoints (temperatures, pressures)
    data_store.write_holding_registers(0, [750, 1200, 850, 600])  # °C * 10
    
    # Sensor readings (simulated)
    data_store.write_input_registers(0, [748, 1195, 847, 598])   # Current values
    
    # Safety interlocks and limit switches
    data_store.write_discrete_inputs(0, [True, True, False, True])
    
    # Create multi-client TCP server
    server = AsyncTcpModbusServer(
        host="0.0.0.0",          # Accept connections from any IP
        port=502,                 # Standard Modbus port
        data_store=data_store,
        slave_id=1,
        max_connections=50        # Support up to 50 HMI clients
    )
    
    print("Starting Industrial Control System Simulator...")
    print("Connect your HMI to: <your_ip>:502")
    print("Slave ID: 1")
    
    try:
        await server.start()
        
        # Start background data simulation
        simulation_task = asyncio.create_task(simulate_process_data(data_store))
        
        # Run server forever
        await server.serve_forever()
        
    except KeyboardInterrupt:
        print("\nShutting down server...")
        simulation_task.cancel()
    finally:
        await server.stop()

async def simulate_process_data(data_store):
    """Simulate changing process values"""
    import random
    
    while True:
        # Simulate temperature fluctuations
        temps = [random.randint(740, 760) for _ in range(4)]
        data_store.write_input_registers(0, temps)
        
        # Simulate pressure changes
        pressures = [random.randint(1180, 1220) for _ in range(4)]
        data_store.write_input_registers(10, pressures)
        
        await asyncio.sleep(1.0)  # Update every second

# Run the server
asyncio.run(industrial_tcp_server())
```

### RTU Server (Serial Field Device)

Emulate **field instruments** and **smart sensors**:

```python
from modbuslink import AsyncRtuModbusServer, ModbusDataStore
import asyncio

async def smart_sensor_rtu():
    """Simulate a smart temperature/pressure sensor"""
    
    data_store = ModbusDataStore(
        holding_registers_size=100,   # Configuration registers
        input_registers_size=100      # Measurement data
    )
    
    # Device configuration
    data_store.write_holding_registers(0, [
        250,    # Temperature alarm high (°C * 10)
        -50,    # Temperature alarm low
        1500,   # Pressure alarm high (mbar)
        500     # Pressure alarm low
    ])
    
    # Create RTU field device
    server = AsyncRtuModbusServer(
        port="COM3",              # Serial port
        baudrate=9600,
        parity="N",
        data_store=data_store,
        slave_id=15,              # Field device address
        timeout=2.0
    )
    
    print("Smart Sensor RTU Device Starting...")
    print(f"Port: COM3, Baudrate: 9600, Slave ID: 15")
    
    try:
        await server.start()
        
        # Start sensor simulation
        sensor_task = asyncio.create_task(simulate_sensor_readings(data_store))
        
        await server.serve_forever()
        
    except KeyboardInterrupt:
        print("\nSensor offline")
        sensor_task.cancel()
    finally:
        await server.stop()

async def simulate_sensor_readings(data_store):
    """Simulate realistic sensor behavior"""
    import random, math, time
    
    start_time = time.time()
    
    while True:
        elapsed = time.time() - start_time
        
        # Simulate daily temperature variation
        base_temp = 200 + 50 * math.sin(elapsed / 3600)  # Hourly cycle
        temp = int(base_temp + random.uniform(-5, 5))     # Add noise
        
        # Simulate correlated pressure
        pressure = int(1000 + temp * 0.5 + random.uniform(-10, 10))
        
        # Update input registers
        data_store.write_input_registers(0, [temp, pressure])
        
        await asyncio.sleep(5.0)  # Update every 5 seconds

# Run the sensor
asyncio.run(smart_sensor_rtu())
```

### Multi-Server Deployment

**Run multiple servers simultaneously** for complex applications:

```python
from modbuslink import (
    AsyncTcpModbusServer,
    AsyncRtuModbusServer, 
    AsyncAsciiModbusServer,
    ModbusDataStore
)
import asyncio

async def multi_protocol_gateway():
    """Create a multi-protocol Modbus gateway"""
    
    # Shared data store for all protocols
    shared_data = ModbusDataStore(
        coils_size=1000,
        discrete_inputs_size=1000,
        holding_registers_size=1000,
        input_registers_size=1000
    )
    
    # Initialize gateway data
    shared_data.write_holding_registers(0, list(range(100, 200)))
    
    # Create multiple servers
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
    
    # Start all servers
    servers = [tcp_server, rtu_server, ascii_server]
    
    try:
        # Start servers concurrently
        await asyncio.gather(
            *[server.start() for server in servers]
        )
        
        print("Multi-Protocol Gateway Online:")
        print("  • TCP: 0.0.0.0:502")
        print("  • RTU: COM3@9600")
        print("  • ASCII: COM4@9600")
        
        # Run all servers
        await asyncio.gather(
            *[server.serve_forever() for server in servers]
        )
        
    except KeyboardInterrupt:
        print("\nShutting down gateway...")
    finally:
        await asyncio.gather(
            *[server.stop() for server in servers]
        )

# Run the gateway
asyncio.run(multi_protocol_gateway())
```

## 📊 Advanced Data Types & Industrial Applications

### Working with Industrial Data

ModbusLink provides **native support** for common industrial data formats:

```python
with client:
    # ✨ 32-bit IEEE 754 Floating Point
    # Perfect for: Temperature, Pressure, Flow rates, Analog measurements
    client.write_float32(slave_id=1, start_address=100, value=25.67)  # Temperature °C
    temperature = client.read_float32(slave_id=1, start_address=100)
    print(f"Process temperature: {temperature:.2f}°C")
    
    # 🔢 32-bit Signed Integer  
    # Perfect for: Counters, Production counts, Encoder positions
    client.write_int32(slave_id=1, start_address=102, value=-123456)
    position = client.read_int32(slave_id=1, start_address=102)
    print(f"Encoder position: {position} pulses")
    
    # 📝 String Data
    # Perfect for: Device names, Alarm messages, Part numbers
    client.write_string(slave_id=1, start_address=110, value="PUMP_001")
    device_name = client.read_string(slave_id=1, start_address=110, length=10)
    print(f"Device: {device_name}")
    
    # 🔄 Byte Order Control (Critical for multi-vendor compatibility)
    # Handle different PLC manufacturers
    
    # Siemens style: Big endian, high word first
    client.write_float32(
        slave_id=1, start_address=200, value=3.14159,
        byte_order="big", word_order="high"
    )
    
    # Schneider style: Little endian, low word first 
    client.write_float32(
        slave_id=1, start_address=202, value=3.14159,
        byte_order="little", word_order="low"
    )
```

### Real-World Industrial Example

```python
from modbuslink import ModbusClient, TcpTransport
import time

def monitor_production_line():
    """Complete production line monitoring system"""
    
    transport = TcpTransport(host='192.168.1.50', port=502, timeout=3.0)
    client = ModbusClient(transport)
    
    with client:
        print("🏭 Production Line Monitor Started")
        print("=" * 50)
        
        while True:
            try:
                # Read critical process parameters
                # Temperature control loop (PID setpoint & process value)
                temp_setpoint = client.read_float32(1, 1000)  # Setpoint
                temp_actual = client.read_float32(1, 1002)    # Process value
                
                # Production counter (32-bit integer)
                parts_produced = client.read_int32(1, 2000)
                
                # Quality metrics (holding registers)
                quality_data = client.read_holding_registers(1, 3000, 5)
                reject_count = quality_data[0]
                efficiency = quality_data[1] / 100.0  # Convert to percentage
                
                # System status (coils)
                status_coils = client.read_coils(1, 0, 8)
                line_running = status_coils[0]
                emergency_stop = status_coils[1]
                
                # Display real-time data
                print(f"\r🌡️  Temp: {temp_actual:6.1f}°C (SP: {temp_setpoint:.1f})  "
                      f"🔢 Parts: {parts_produced:6d}  "
                      f"🏆 Efficiency: {efficiency:5.1f}%  "
                      f"🚨 Status: {'RUN' if line_running else 'STOP'}", end="")
                
                # Automatic quality control
                if efficiency < 85.0:
                    print("\n⚠️  Low efficiency detected - adjusting parameters...")
                    # Adjust temperature setpoint
                    new_setpoint = temp_setpoint + 0.5
                    client.write_float32(1, 1000, new_setpoint)
                
                # Safety check
                if temp_actual > 85.0:
                    print("\n🔥 OVERTEMPERATURE ALARM!")
                    # Emergency shutdown
                    client.write_single_coil(1, 0, False)  # Stop line
                    break
                    
                time.sleep(1.0)
                
            except KeyboardInterrupt:
                print("\n🛱 Monitor stopped by user")
                break
            except Exception as e:
                print(f"\n❌ Communication error: {e}")
                time.sleep(5.0)  # Retry after 5 seconds

# Run the monitoring system
monitor_production_line()
```

## 🛡️ Production-Ready Features

### Comprehensive Error Handling

**Never lose production data** with robust error management:

```python
from modbuslink import (
    ModbusClient, TcpTransport,
    ConnectionError, TimeoutError, ModbusException, CRCError
)
import time

def resilient_data_collector():
    """Production-grade data collection with full error handling"""
    
    transport = TcpTransport(host='192.168.1.100', port=502)
    client = ModbusClient(transport)
    
    retry_count = 0
    max_retries = 3
    
    while retry_count < max_retries:
        try:
            with client:
                # Critical data collection
                production_data = client.read_holding_registers(1, 1000, 50)
                print(f"✅ Data collected successfully: {len(production_data)} points")
                return production_data
                
        except ConnectionError as e:
            print(f"🔌 Network connection failed: {e}")
            print("  • Check network cables")
            print("  • Verify device IP address")
            print("  • Check firewall settings")
            
        except TimeoutError as e:
            print(f"⏱️ Operation timed out: {e}")
            print("  • Network may be congested")
            print("  • Device may be overloaded")
            
        except CRCError as e:
            print(f"📊 Data corruption detected: {e}")
            print("  • Check serial cable integrity")
            print("  • Verify baud rate settings")
            
        except ModbusException as e:
            print(f"📝 Protocol error: {e}")
            print("  • Invalid slave address")
            print("  • Register address out of range")
            print("  • Function not supported")
            
        except Exception as e:
            print(f"❌ Unknown error: {e}")
            
        # Exponential backoff retry
        retry_count += 1
        wait_time = 2 ** retry_count
        print(f"🔄 Retrying in {wait_time} seconds... ({retry_count}/{max_retries})")
        time.sleep(wait_time)
    
    print("❌ Failed to collect data after all retries")
    return None

# Use in production
data = resilient_data_collector()
if data:
    print("Processing data...")
else:
    print("Activating backup data source...")
```

### Advanced Logging & Debugging

**Debug communication issues** with protocol-level monitoring:

```python
from modbuslink.common import Language, set_language
from modbuslink.utils import ModbusLogger
import logging

# Set global language (affects both logging and exception messages)
set_language(Language.EN)  # Use Language.CN for Chinese (default)

# Setup comprehensive logging
ModbusLogger.setup_logging(
    level=logging.DEBUG,
    enable_debug=True,
    log_file='modbus_debug.log',
    # language=Language.EN  # Use Language.CN for Chinese (default)
    # The original way of writing can still be used, but it is recommended to modify it using the method mentioned above(global).
)

# Enable packet-level debugging
ModbusLogger.enable_protocol_debug()

# Now all Modbus communications are logged:
# 2024-08-30 10:15:23 [DEBUG] Sending: 01 03 00 00 00 0A C5 CD
# 2024-08-30 10:15:23 [DEBUG] Received: 01 03 14 00 64 00 C8 01 2C 01 90 01 F4 02 58 02 BC 03 20 03 84 E5 C6
```

### Performance Monitoring

```python
import asyncio
import time
from modbuslink import AsyncModbusClient, AsyncTcpTransport

async def performance_benchmark():
    """Measure ModbusLink performance"""
    
    client = AsyncModbusClient(AsyncTcpTransport('192.168.1.100'))
    
    async with client:
        # Benchmark concurrent operations
        start_time = time.time()
        
        # 100 concurrent read operations
        tasks = [
            client.read_holding_registers(1, i*10, 10) 
            for i in range(100)
        ]
        
        results = await asyncio.gather(*tasks)
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"🚀 Performance Results:")
        print(f"  • Operations: {len(tasks)}")
        print(f"  • Total time: {duration:.2f} seconds")
        print(f"  • Operations/sec: {len(tasks)/duration:.1f}")
        print(f"  • Avg response time: {duration*1000/len(tasks):.1f} ms")

# Run benchmark
asyncio.run(performance_benchmark())
```

## 📈 Supported Modbus Functions

Complete **Modbus specification** implementation:

| Function Code | Name | Description | Use Case |
|---------------|------|-------------|----------|
| **0x01** | Read Coils | Read 1-2000 coil status | Digital outputs (pumps, valves, motors) |
| **0x02** | Read Discrete Inputs | Read 1-2000 input status | Digital sensors (limit switches, buttons) |
| **0x03** | Read Holding Registers | Read 1-125 register values | Analog outputs (setpoints, parameters) |
| **0x04** | Read Input Registers | Read 1-125 input values | Analog inputs (temperature, pressure) |
| **0x05** | Write Single Coil | Write one coil | Control single device (start pump) |
| **0x06** | Write Single Register | Write one register | Set single parameter (temperature setpoint) |
| **0x0F** | Write Multiple Coils | Write 1-1968 coils | Batch control (production sequence) |
| **0x10** | Write Multiple Registers | Write 1-123 registers | Batch parameters (recipe download) |

### Transport Layer Architecture

ModbusLink's **layered design** supports all major Modbus variants:

#### Synchronous Transports
- 🌐 **TcpTransport**: Ethernet Modbus TCP/IP (IEEE 802.3)
- 📞 **RtuTransport**: Serial Modbus RTU (RS232/RS485) with RS485 mode support
- 📜 **AsciiTransport**: Serial Modbus ASCII (7-bit text)

#### Asynchronous Transports  
- ⚡ **AsyncTcpTransport**: High-performance TCP (1000+ concurrent connections)
- ⚡ **AsyncRtuTransport**: Non-blocking serial RTU with RS485 mode support
- ⚡ **AsyncAsciiTransport**: Non-blocking serial ASCII

#### RS485 Mode Support

For adapters without automatic hardware flow control, ModbusLink supports **software-controlled RS485 mode** using RTS/DTR signals:

```python
from modbuslink import RtuTransport, RS485Settings

# Basic RS485 mode (RTS high for TX, low for RX)
transport = RtuTransport('/dev/ttyUSB0', baudrate=9600, rs485_mode=True)

# Custom RS485 settings for specific hardware
rs485_settings = RS485Settings(
    rts_level_for_tx=True,   # RTS high during transmission
    rts_level_for_rx=False,  # RTS low during reception
    delay_before_tx=0.001,   # 1ms delay before TX (for transceiver settling)
    delay_before_rx=0.001,   # 1ms delay before RX
)
transport = RtuTransport('/dev/ttyUSB0', rs485_mode=rs485_settings)
```

| RS485Settings Parameter | Type | Default | Description |
|------------------------|------|---------|-------------|
| `rts_level_for_tx` | bool | True | RTS pin level during transmission |
| `rts_level_for_rx` | bool | False | RTS pin level during reception |
| `delay_before_tx` | float | 0.0 | Delay in seconds before starting TX |
| `delay_before_rx` | float | 0.0 | Delay in seconds before starting RX |

### Key Performance Metrics

| Metric | Sync Client | Async Client | Async Server |
|--------|-------------|--------------|-------------|
| **Throughput** | 100 ops/sec | 1000+ ops/sec | 5000+ ops/sec |
| **Connections** | 1 | 1000+ | 1000+ |
| **Memory Usage** | Low | Medium | Medium |
| **CPU Usage** | Low | Very Low | Low |
| **Latency** | 10-50ms | 5-20ms | 1-10ms |

## 📁 Project Architecture

**Clean, maintainable, and extensible** codebase structure:

```
ModbusLink/
├── src/modbuslink/
│   ├── client/                    # 📱 Client Layer
│   │   ├── sync_client.py         # Synchronous Modbus client
│   │   └── async_client.py        # Asynchronous client with callbacks
│   │
│   ├── server/                    # 🖥️ Server Layer  
│   │   ├── data_store.py          # Thread-safe data storage
│   │   ├── async_base_server.py   # Server base class
│   │   ├── async_tcp_server.py    # Multi-client TCP server
│   │   ├── async_rtu_server.py    # Serial RTU server
│   │   └── async_ascii_server.py  # Serial ASCII server
│   │
│   ├── transport/                 # 🚚 Transport Layer
│   │   ├── base.py                # Sync transport interface
│   │   ├── async_base.py          # Async transport interface
│   │   ├── tcp.py                 # TCP/IP implementation
│   │   ├── rtu.py                 # RTU serial implementation
│   │   ├── ascii.py               # ASCII serial implementation
│   │   ├── async_tcp.py           # Async TCP with connection pooling
│   │   ├── async_rtu.py           # Async RTU with frame detection
│   │   └── async_ascii.py         # Async ASCII with message parsing
│   │
│   ├── utils/                     # 🔧 Utility Layer
│   │   ├── crc.py                 # CRC16 validation (RTU)
│   │   ├── coder.py               # Data type conversion
│   │   └── logging.py             # Advanced logging system
│   │
│   └── common/                    # 🛠️ Common Components
│       ├── language.py            # Unified language configuration
│       └── exceptions.py          # Custom exception hierarchy
│
├── examples/                      # 📚 Usage Examples
│   ├── sync_tcp_example.py        # Basic TCP client
│   ├── async_tcp_example.py       # High-performance async client
│   ├── sync_rtu_example.py        # Serial RTU communication  
│   ├── async_rtu_example.py       # Async RTU with error recovery
│   ├── sync_ascii_example.py      # ASCII mode debugging
│   ├── async_ascii_example.py     # Async ASCII communication
│   ├── async_tcp_server_example.py    # Multi-client TCP server
│   ├── async_rtu_server_example.py    # RTU field device simulator
│   ├── async_ascii_server_example.py  # ASCII device emulator
│   └── multi_server_example.py        # Multi-protocol gateway
│
└── docs/                          # 📜 Documentation
    ├── api/                       # API reference
    ├── guides/                    # User guides
    └── examples/                  # Advanced examples
```

## 📚 Examples

Explore **real-world scenarios** in the [examples](examples/) directory:

### 🔄 Synchronous Examples
- **Industrial Control**: Basic sync operations for PLCs and field devices
- **Data Acquisition**: Reliable data collection from sensors
- **Device Configuration**: Parameter setup and calibration

### ⚡ Asynchronous Examples  
- **SCADA Systems**: High-performance monitoring of multiple devices
- **IoT Gateways**: Concurrent communication with hundreds of sensors
- **Real-time Control**: Sub-millisecond response applications

### 🖥️ Server Examples
- **Device Simulators**: Test HMI applications without physical hardware
- **Protocol Gateways**: Bridge different Modbus variants
- **Training Systems**: Educational Modbus lab setups

### 🎆 Advanced Features
- **Multi-Protocol**: Run TCP, RTU, and ASCII servers simultaneously  
- **Error Recovery**: Automatic reconnection and retry logic
- **Performance Tuning**: Optimize for your specific use case
- **Production Deployment**: Best practices for 24/7 operation

## ⚙️ System Requirements

### Core Requirements
- **Python**: 3.8+ (3.9+ recommended for best performance)
- **Operating System**: Windows, Linux, macOS
- **Memory**: Minimum 64MB RAM
- **Network**: TCP/IP stack for Modbus TCP
- **Serial Ports**: RS232/RS485 for RTU/ASCII

### Dependencies
```bash
# Core dependencies (automatically installed)
pyserial >= 3.5          # Serial port communication
pyserial-asyncio >= 0.6   # Async serial support  
typing_extensions >= 4.0.0 # Enhanced type hints

# Development dependencies (optional)
pytest >= 7.0             # Unit testing
pytest-mock >= 3.0        # Test mocking
black >= 22.0             # Code formatting
ruff >= 0.1.0             # Code linting
mypy >= 1.0               # Type checking
```

### Performance Recommendations
- **CPU**: Multi-core recommended for async servers (2+ cores)
- **Network**: Gigabit Ethernet for high-throughput TCP applications
- **Serial**: USB-to-RS485 converters with FTDI chipsets
- **Python**: Use CPython for best performance (avoid PyPy for serial I/O)

## 📜 License & Contributing

**MIT License** - Free for commercial use. See [LICENSE.txt](LICENSE.txt) for details.

### Contributing Guidelines

**We welcome contributions!** Please:

1. 🍿 **Fork** the repository
2. 🌱 **Create** a feature branch
3. ✨ **Add** tests for new functionality
4. 📝 **Update** documentation
5. 🚀 **Submit** a pull request

**Areas where we need help:**
- Additional Modbus function codes (0x14, 0x15, 0x16, 0x17)
- Performance optimizations
- Additional transport protocols (Modbus Plus, etc.)
- Documentation improvements
- Real-world testing and bug reports

### Community & Support

- 💬 **GitHub Issues**: Bug reports and feature requests
- 📧 **Email Support**: Technical questions and consulting
- 📚 **Documentation**: Comprehensive guides and API reference
- 🎆 **Examples**: Production-ready code samples

---

<div align="center">

**Built with ❤️ for the Industrial Automation Community**

*ModbusLink - Connecting Industrial Systems with Modern Python*

</div>
