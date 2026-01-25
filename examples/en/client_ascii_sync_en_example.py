"""
ModbusLink Sync ASCII Client Example
"""

import logging
import traceback

from src.modbuslink import (
    SyncModbusClient,
    SyncAsciiTransport,
    ConnectError,
    TimeOutError,
    LrcError,
    ModbusException,
    ModbusLogger,
    Language,
    set_language,
)


def basic_operation_example(client: SyncModbusClient):
    """Basic Operation Example"""
    print("\n=== Sync ASCII Basic Operation Example ===")

    try:
        with client:
            print("\n1. Read Coil Status (0x01)")
            coils = client.read_coils(
                slave_id=1, start_address=0, quantity=10
            )
            print(f"   Coil Status: {coils}")

            print("\n2. Read Discrete Input Status (0x02)")
            discrete_inputs = client.read_discrete_inputs(
                slave_id=1, start_address=0, quantity=10
            )
            print(f"   Discrete Input Status: {discrete_inputs}")

            print("\n3. Read Holding Registers (0x03)")
            holding_registers = client.read_holding_registers(
                slave_id=1, start_address=0, quantity=10
            )
            print(f"   Holding Registers: {holding_registers}")

            print("\n4. Read Input Registers (0x04)")
            input_registers = client.read_input_registers(
                slave_id=1, start_address=0, quantity=10
            )
            print(f"   Input Registers: {input_registers}")

            print("\n5. Write Single Coil (0x05)")
            client.write_single_coil(
                slave_id=1, address=0, value=True
            )
            coils = client.read_coils(
                slave_id=1, start_address=0, quantity=1
            )
            print(f"   Updated Coil Status: {coils[0]}")

            print("\n6. Write Single Register (0x06)")
            client.write_single_register(
                slave_id=1, address=0, value=1234
            )
            registers = client.read_holding_registers(
                slave_id=1, start_address=0, quantity=1
            )
            print(f"   Updated Register Value: {registers[0]}")

            print("\n7. Write Multiple Coils (0x0F)")
            client.write_multiple_coils(
                slave_id=1, start_address=5, values=[False, True, False, True, False]
            )
            coils = client.read_coils(
                slave_id=1, start_address=5, quantity=5
            )
            print(f"   Updated Coil Status: {coils}")

            print("\n8. Write Multiple Registers (0x10)")
            client.write_multiple_registers(
                slave_id=1, start_address=5, values=[1234, 5678, 51011, 31314, 4789]
            )
            registers = client.read_holding_registers(
                slave_id=1, start_address=5, quantity=5
            )
            print(f"   Updated Register Values: {registers}")

    except Exception as e:
        print(f"Operation failed: {e}")


def advanced_operation_example(client: SyncModbusClient):
    """Advanced Operation Example"""
    print("\n=== Sync ASCII Advanced Operation Example ===")

    try:
        with client:
            print("\n1. Write 32-bit Float")
            value = 25.6
            client.write_float32(
                slave_id=1, start_address=0, value=value
            )
            print(f"   Written Value: {value}")

            print("\n2. Read 32-bit Float")
            read_value = client.read_float32(
                slave_id=1, start_address=0
            )
            print(f"   Read Value: {read_value}")

            print("\n3. Write 32-bit Signed Integer")
            value = -12345
            client.write_int32(
                slave_id=1, start_address=0, value=value
            )
            print(f"   Written Value: {value}")

            print("\n4. Read 32-bit Signed Integer")
            read_value = client.read_int32(
                slave_id=1, start_address=0
            )
            print(f"   Read Value: {read_value}")

            print("\n5. Write 32-bit Unsigned Integer")
            value = 12345
            client.write_uint32(
                slave_id=1, start_address=0, value=value
            )
            print(f"   Written Value: {value}")

            print("\n6. Read 32-bit Unsigned Integer")
            read_value = client.read_uint32(
                slave_id=1, start_address=0
            )
            print(f"   Read Value: {read_value}")

            print("\n7. Write 64-bit Signed Integer")
            value = -123
            client.write_int64(
                slave_id=1, start_address=0, value=value
            )
            print(f"   Written Value: {value}")

            print("\n8. Read 64-bit Signed Integer")
            read_value = client.read_int64(
                slave_id=1, start_address=0
            )
            print(f"   Read Value: {read_value}")

            print("\n9. Write 64-bit Unsigned Integer")
            value = 123
            client.write_uint64(
                slave_id=1, start_address=0, value=value
            )
            print(f"   Written Value: {value}")

            print("\n10. Read 64-bit Unsigned Integer")
            read_value = client.read_uint64(
                slave_id=1, start_address=0
            )
            print(f"   Read Value: {read_value}")

            print("\n11. Write String")
            value = "ASC Modbus"
            client.write_string(
                slave_id=1, start_address=0, value=value
            )
            print(f"   Written Value: {value}")

            print("\n12. Read String")
            read_value = client.read_string(
                slave_id=1, start_address=0, length=10
            )
            print(f"   Read Value: {read_value}")

            print("\n13. Test different byte and word orders (Big Endian, High Word)")
            value = 3.14159

            client.write_float32(
                slave_id=1,
                start_address=0,
                value=value,
                byte_order="big",
                word_order="high",
            )
            read_value = client.read_float32(
                slave_id=1,
                start_address=0,
                byte_order="big",
                word_order="high"
            )
            print(f"   Big/High: Wrote {value}, Read {read_value}")

            print("\n14. Test different byte and word orders (Little Endian, Low Word)")
            value = 3.14159

            client.write_float32(
                slave_id=1,
                start_address=0,
                value=value,
                byte_order="little",
                word_order="low",
            )
            read_value = client.read_float32(
                slave_id=1,
                start_address=0,
                byte_order="little",
                word_order="low"
            )
            print(f"   Little/Low: Wrote {value}, Read {read_value}")

    except Exception as e:
        print(f"Advanced operation failed: {e}")


def main():
    """Main Function"""
    # Setup logging
    ModbusLogger.setup_logging(
        level=logging.INFO,
        enable_debug=True
    )

    set_language(Language.EN)

    print("=== ModbusLink Sync ASCII Client Example ===")

    # ASCII Configuration
    ascii_config = {
        "port": "COM10",  # Windows
        # "port": "/dev/ttyUSB0",   # Linux
        # "port": "/dev/tty.usbserial-0001",  # macOS
        "baudrate": 9600,
        "bytesize": 7,
        "parity": "E",
        "stopbits": 1,
        "timeout": 1,
    }

    # Create ASCII transport layer
    transport = SyncAsciiTransport(
        port=ascii_config["port"],
        baudrate=ascii_config["baudrate"],
        bytesize=ascii_config["bytesize"],
        parity=ascii_config["parity"],
        stopbits=ascii_config["stopbits"],
        timeout=ascii_config["timeout"]
    )

    # Create ASCII client
    client = SyncModbusClient(transport)

    print(f"ASCII Client Configuration:")
    print(f"  Port: {ascii_config['port']}")
    print(f"  Baudrate: {ascii_config['baudrate']}")
    print(f"  Data Bits: {ascii_config['bytesize']}")
    print(f"  Stop Bits: {ascii_config['stopbits']}")
    print(f"  Parity: {ascii_config['parity']}")
    print(f"  Note: Requires a Modbus ASCII device server\n")

    try:
        # Execute examples sequentially
        basic_operation_example(client)
        advanced_operation_example(client)

        print("\n=== All examples execution completed ===")

    except KeyboardInterrupt:
        print("\nStop signal received")
    except ConnectError as e:
        print(f"\n'ConnectError' Connection error: {e}")
    except TimeOutError as e:
        print(f"\n'TimeOutError' Timeout error: {e}")
    except LrcError as e:
        print(f"\n'LrcError' Checksum error: {e}")
    except ModbusException as e:
        print(f"\n'ModbusException' Modbus protocol exception: {e}")
    except Exception as e:
        print(f"\nOther error: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    main()
