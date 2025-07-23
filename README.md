# ModbusLink

English [中文版](README-zh_CN.md)

A modern, powerful, developer-friendly and highly extensible Python Modbus library.

## Features

- **Layered Architecture**: Strict separation of transport layer, client and utility layers
- **Interface-Oriented Programming**: Use abstract base classes to define unified interfaces
- **Dependency Injection**: Client receives transport layer instances through constructor
- **User-Friendly**: All external interfaces use Python native data types
- **Synchronous Support**: Complete synchronous Modbus client implementation
- **Multiple Transport Methods**: Support RTU (serial port) and TCP transport

## Quick Start

### Installation

```bash
pip install modbuslink
```

### RTU Example

```python
from modbuslink import ModbusClient, RtuTransport

# Create RTU transport layer
transport = RtuTransport(
    port='COM1',        # Windows
    # port='/dev/ttyUSB0',  # Linux
    baudrate=9600,
    timeout=1.0
)

# Create client
client = ModbusClient(transport)

# Use context manager to automatically manage connections
with client:
    # Read holding registers
    registers = client.read_holding_registers(
        slave_id=1,
        start_address=0,
        quantity=4
    )
    print(f"Register values: {registers}")
    
    # Write single register
    client.write_single_register(
        slave_id=1,
        address=0,
        value=1234
    )
    
    # Read coil status
    coils = client.read_coils(
        slave_id=1,
        start_address=0,
        quantity=8
    )
    print(f"Coil status: {coils}")
```

### TCP Example

```python
from modbuslink import ModbusClient, TcpTransport

# Create TCP transport layer
transport = TcpTransport(
    host='192.168.1.100',
    port=502,
    timeout=10.0
)

# Create client
client = ModbusClient(transport)

# Use context manager to automatically manage connections
with client:
    # Read input registers
    registers = client.read_input_registers(
        slave_id=1,
        start_address=0,
        quantity=10
    )
    print(f"Input registers: {registers}")
    
    # Write multiple registers
    client.write_multiple_registers(
        slave_id=1,
        start_address=0,
        values=[100, 200, 300, 400]
    )
```

## Supported Function Codes

- **0x01**: Read Coil Status
- **0x02**: Read Discrete Input Status
- **0x03**: Read Holding Registers
- **0x04**: Read Input Registers
- **0x05**: Write Single Coil
- **0x06**: Write Single Register
- **0x0F**: Write Multiple Coils
- **0x10**: Write Multiple Registers

## Exception Handling

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
    print(f"Connection error: {e}")
except TimeoutError as e:
    print(f"Timeout error: {e}")
except CRCError as e:
    print(f"CRC validation error: {e}")
except ModbusException as e:
    print(f"Modbus protocol exception: {e}")
```

## Project Structure

```
ModbusLink/
├── src/modbuslink/          # Main source code
│   ├── __init__.py          # Main export interface
│   ├── client/              # Client module
│   │   ├── __init__.py
│   │   └── sync_client.py   # Synchronous client implementation
│   ├── transport/           # Transport layer module
│   │   ├── __init__.py
│   │   ├── base.py         # Transport layer abstract base class
│   │   ├── rtu.py          # RTU transport layer implementation
│   │   └── tcp.py          # TCP transport layer implementation
│   ├── utils/               # Utility module
│   │   ├── __init__.py
│   │   └── crc.py          # CRC16 validation tool
│   └── common/              # Common module
│       ├── __init__.py
│       └── exceptions.py    # Exception definitions
├── tests/                   # Test module
│   ├── __init__.py
│   ├── test_basic.py        # Basic functionality tests
│   └── test_crc.py          # CRC functionality tests
├── examples/                # Usage examples
│   ├── __init__.py
│   ├── rtu_example.py       # RTU usage example
│   └── tcp_example.py       # TCP usage example
├── pyproject.toml           # Project configuration
├── README.md                # Project documentation
└── LICENSE.txt              # License
```

## Testing

The project includes a complete test suite to verify the correctness of all functionality.

### Running Tests

```bash
# Run CRC functionality tests
python tests/test_crc.py

# Run basic functionality tests
python tests/test_basic.py
```

### Test Content

- **CRC Functionality Tests** (`tests/test_crc.py`): Verify the correctness of CRC16 validation algorithm
- **Basic Functionality Tests** (`tests/test_basic.py`): Verify module imports, transport layer creation, client functionality, etc.

All tests include detailed output information to help developers understand test progress and results.

## Development Plan

- [x] **Phase 1**: Build a solid and reliable core foundation (synchronous MVP)
- [ ] **Phase 2**: Improve usability and developer experience
- [ ] **Phase 3**: Embrace modernization: asynchronous, callbacks and extensions
- [ ] **Phase 4**: Release, testing and community ecosystem

## License

MIT License - See [LICENSE.txt](LICENSE.txt) for details

## Contributing

Issues and Pull Requests are welcome!