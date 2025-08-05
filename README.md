# ModbusLink

English | [中文版](README-zh_CN.md)

[![PyPI Downloads](https://static.pepy.tech/badge/modbuslink)](https://pepy.tech/projects/modbuslink)
[![PyPI version](https://badge.fury.io/py/modbuslink.svg)](https://badge.fury.io/py/modbuslink)

A modern, powerful, and developer-friendly Python Modbus library with comprehensive transport layer support.

## Features

- **🏗️ Layered Architecture**: Clean separation of transport, client, server, and utility layers
- **🔌 Multiple Transports**: TCP, RTU, and ASCII with both sync and async support
- **⚡ High Performance**: Asynchronous operations with concurrent request handling
- **🛠️ Developer Friendly**: Intuitive APIs with comprehensive error handling
- **📊 Advanced Data Types**: Built-in support for float32, int32, strings, and more
- **🔍 Debugging Support**: Comprehensive logging with protocol-level debugging
- **🎯 Type Safe**: Full type hints for better IDE support
- **🖥️ Server Support**: Complete Modbus server implementation with TCP, RTU, and ASCII support

## Quick Start

### Installation

```bash
pip install modbuslink
```

### Basic Usage

#### TCP Client

```python
from modbuslink import ModbusClient, TcpTransport

# Create TCP transport
transport = TcpTransport(host='192.168.1.100', port=502)
client = ModbusClient(transport)

with client:
    # Read holding registers
    registers = client.read_holding_registers(
        slave_id=1, start_address=0, quantity=10
    )
    print(f"Registers: {registers}")
    
    # Write single register
    client.write_single_register(
        slave_id=1, address=0, value=1234
    )
```

#### RTU Client

```python
from modbuslink import ModbusClient, RtuTransport

# Create RTU transport
transport = RtuTransport(
    port='COM1',  # or '/dev/ttyUSB0' on Linux
    baudrate=9600,
    timeout=1.0
)
client = ModbusClient(transport)

with client:
    # Read coils
    coils = client.read_coils(
        slave_id=1, start_address=0, quantity=8
    )
    print(f"Coils: {coils}")
```

#### ASCII Client

```python
from modbuslink import ModbusClient, AsciiTransport

# Create ASCII transport
transport = AsciiTransport(
    port='COM1',
    baudrate=9600,
    bytesize=7,
    parity='E'
)
client = ModbusClient(transport)

with client:
    # Read input registers
    registers = client.read_input_registers(
        slave_id=1, start_address=0, quantity=5
    )
    print(f"Input registers: {registers}")
```

### Asynchronous Operations

```python
import asyncio
from modbuslink import AsyncModbusClient, AsyncTcpTransport

async def main():
    transport = AsyncTcpTransport(host='192.168.1.100', port=502)
    client = AsyncModbusClient(transport)
    
    async with client:
        # Concurrent operations
        tasks = [
            client.read_holding_registers(1, 0, 10),
            client.read_coils(1, 0, 8),
            client.write_single_register(1, 100, 9999)
        ]
        results = await asyncio.gather(*tasks)
        print(f"Results: {results}")

asyncio.run(main())
```

### Modbus Servers

#### TCP Server

```python
from modbuslink import AsyncTcpModbusServer, ModbusDataStore
import asyncio

async def main():
    # Create data store
    data_store = ModbusDataStore(
        coils_size=1000,
        discrete_inputs_size=1000,
        holding_registers_size=1000,
        input_registers_size=1000
    )
    
    # Set initial data
    data_store.write_coils(0, [True, False, True, False])
    data_store.write_holding_registers(0, [100, 200, 300, 400])
    
    # Create TCP server
    server = AsyncTcpModbusServer(
        host="localhost",
        port=5020,
        data_store=data_store,
        slave_id=1
    )
    
    try:
        await server.start()
        print("TCP server started successfully!")
        await server.serve_forever()
    except KeyboardInterrupt:
        print("Stopping server...")
    finally:
        await server.stop()

asyncio.run(main())
```

#### RTU Server

```python
from modbuslink import AsyncRtuModbusServer, ModbusDataStore
import asyncio

async def main():
    # Create data store
    data_store = ModbusDataStore(
        coils_size=1000,
        discrete_inputs_size=1000,
        holding_registers_size=1000,
        input_registers_size=1000
    )
    
    # Create RTU server
    server = AsyncRtuModbusServer(
        port="COM3",  # or '/dev/ttyUSB0' on Linux
        baudrate=9600,
        data_store=data_store,
        slave_id=1
    )
    
    try:
        await server.start()
        print("RTU server started successfully!")
        await server.serve_forever()
    except KeyboardInterrupt:
        print("Stopping server...")
    finally:
        await server.stop()

asyncio.run(main())
```

#### ASCII Server

```python
from modbuslink import AsyncAsciiModbusServer, ModbusDataStore
import asyncio

async def main():
    # Create data store
    data_store = ModbusDataStore(
        coils_size=1000,
        discrete_inputs_size=1000,
        holding_registers_size=1000,
        input_registers_size=1000
    )
    
    # Create ASCII server
    server = AsyncAsciiModbusServer(
        port="COM4",
        baudrate=9600,
        data_store=data_store,
        slave_id=2,
        parity="E",
        bytesize=7
    )
    
    try:
        await server.start()
        print("ASCII server started successfully!")
        await server.serve_forever()
    except KeyboardInterrupt:
        print("Stopping server...")
    finally:
        await server.stop()

asyncio.run(main())
```

### Advanced Data Types

```python
with client:
    # 32-bit float
    client.write_float32(slave_id=1, start_address=100, value=3.14159)
    temperature = client.read_float32(slave_id=1, start_address=100)
    
    # 32-bit integer
    client.write_int32(slave_id=1, start_address=102, value=-123456)
    counter = client.read_int32(slave_id=1, start_address=102)
    
    # String
    client.write_string(slave_id=1, start_address=110, value="Hello")
    message = client.read_string(slave_id=1, start_address=110, length=10)
```

## Supported Function Codes

| Code | Function | Description |
|------|----------|-------------|
| 0x01 | Read Coils | Read coil status |
| 0x02 | Read Discrete Inputs | Read discrete input status |
| 0x03 | Read Holding Registers | Read holding register values |
| 0x04 | Read Input Registers | Read input register values |
| 0x05 | Write Single Coil | Write single coil value |
| 0x06 | Write Single Register | Write single register value |
| 0x0F | Write Multiple Coils | Write multiple coil values |
| 0x10 | Write Multiple Registers | Write multiple register values |

## Transport Layers

### Synchronous Transports

- **TcpTransport**: Modbus TCP over Ethernet
- **RtuTransport**: Modbus RTU over serial port
- **AsciiTransport**: Modbus ASCII over serial port

### Asynchronous Transports

- **AsyncTcpTransport**: High-performance async TCP
- **AsyncRtuTransport**: High-performance async RTU
- **AsyncAsciiTransport**: High-performance async ASCII

## Error Handling

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
    print(f"Connection failed: {e}")
except TimeoutError as e:
    print(f"Operation timed out: {e}")
except ModbusException as e:
    print(f"Modbus error: {e}")
```

## Logging and Debugging

```python
from modbuslink.utils import ModbusLogger
import logging

# Setup logging
ModbusLogger.setup_logging(
    level=logging.DEBUG,
    enable_debug=True,
    log_file='modbus.log'
)

# Enable protocol debugging
ModbusLogger.enable_protocol_debug()
```

## Project Structure

```
ModbusLink/
├── src/modbuslink/
│   ├── client/              # Client implementations
│   │   ├── sync_client.py   # Synchronous client
│   │   └── async_client.py  # Asynchronous client
│   ├── server/              # Server implementations
│   │   ├── data_store.py    # Data store
│   │   ├── async_base_server.py  # Async server base class
│   │   ├── async_tcp_server.py   # Async TCP server
│   │   ├── async_rtu_server.py   # Async RTU server
│   │   └── async_ascii_server.py # Async ASCII server
│   ├── transport/           # Transport layer implementations
│   │   ├── tcp.py          # TCP transport
│   │   ├── rtu.py          # RTU transport
│   │   ├── ascii.py        # ASCII transport
│   │   ├── async_tcp.py    # Async TCP transport
│   │   ├── async_rtu.py    # Async RTU transport
│   │   └── async_ascii.py  # Async ASCII transport
│   ├── utils/              # Utility modules
│   │   ├── crc.py         # CRC validation
│   │   ├── payload_coder.py # Data encoding/decoding
│   │   └── logger.py      # Logging system
│   └── common/             # Common modules
│       └── exceptions.py   # Exception definitions
├── examples/               # Usage examples
│   ├── sync_tcp_example.py
│   ├── async_tcp_example.py
│   ├── sync_rtu_example.py
│   ├── async_rtu_example.py
│   ├── sync_ascii_example.py
│   ├── async_ascii_example.py
│   ├── async_tcp_server_example.py    # TCP server example
│   ├── async_rtu_server_example.py    # RTU server example
│   ├── async_ascii_server_example.py  # ASCII server example
│   └── multi_server_example.py        # Multi-server example
└── docs/                   # Documentation
```

## Examples

Check out the [examples](examples/) directory for comprehensive usage examples:

- **Synchronous Examples**: Basic sync operations for TCP, RTU, and ASCII
- **Asynchronous Examples**: High-performance async operations with concurrency
- **Server Examples**: TCP, RTU, and ASCII server implementations
- **Advanced Features**: Data types, error handling, and debugging
- **Multi-Server**: Running multiple server types simultaneously

## Requirements

- Python 3.8+
- pyserial >= 3.5 (for RTU/ASCII transports)

## License

MIT License - see [LICENSE.txt](LICENSE.txt) for details.

## Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.
