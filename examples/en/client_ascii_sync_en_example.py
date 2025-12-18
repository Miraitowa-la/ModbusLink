"""
ModbusLink Sync ASCII Client Example
Demonstrates how to use sync ASCII transport for Modbus communication,
including basic read/write operations, advanced data type operations and error handling.
"""

import logging
import time
from src.modbuslink import (
    ModbusClient,
    AsciiTransport,
    ConnectionError,
    TimeoutError,
    ModbusException,
)
from src.modbuslink.utils.logging import ModbusLogger, Language

# Set logging
ModbusLogger.setup_logging(
    level=logging.INFO,
    enable_debug=True,
    language=Language.EN,
)


def basic_operations_example():
    """Basic operations example"""
    print("\n=== Sync ASCII Basic Operations Example ===")

    # Create ASCII transport
    transport = AsciiTransport(
        port="COM10",  # Windows: COM10, Linux: /dev/ttyUSB0
        baudrate=9600,
        bytesize=7,
        parity="E",  # Even parity
        timeout=2.0
    )

    # Create client
    client = ModbusClient(transport)

    try:
        with client:
            # Read holding registers
            print("\n1. Reading holding registers...")
            registers = client.read_holding_registers(
                slave_id=1, start_address=0, quantity=4
            )
            print(f"   Register values: {registers}")

            # Write single register
            print("\n2. Writing single register...")
            client.write_single_register(slave_id=1, address=0, value=1234)
            print("   Write completed")

            # Verify write result
            print("\n3. Verifying write result...")
            value = client.read_holding_registers(
                slave_id=1, start_address=0, quantity=1
            )
            print(f"   Register 0 value: {value[0]}")

            # Write multiple registers
            print("\n4. Writing multiple registers...")
            values = [1111, 2222, 3333, 4444]
            client.write_multiple_registers(
                slave_id=1, start_address=10, values=values
            )
            print(f"   Written values: {values}")

            # Read multiple registers
            print("\n5. Reading multiple registers...")
            read_values = client.read_holding_registers(
                slave_id=1, start_address=10, quantity=4
            )
            print(f"   Read values: {read_values}")

            # Coil operations
            print("\n6. Coil operations...")
            client.write_single_coil(slave_id=1, address=0, value=True)
            coils = client.read_coils(slave_id=1, start_address=0, quantity=8)
            print(f"   Coil status: {coils}")

            # Write multiple coils
            coil_values = [True, False, True, False, True, False, True, False]
            client.write_multiple_coils(
                slave_id=1, start_address=0, values=coil_values
            )
            coils = client.read_coils(slave_id=1, start_address=0, quantity=8)
            print(f"   Updated coil status: {coils}")

    except Exception as e:
        print(f"Operation failed: {e}")


def advanced_data_types_example():
    """Advanced data types example"""
    print("\n=== Sync ASCII Advanced Data Types Example ===")

    transport = AsciiTransport(
        port="COM10",
        baudrate=9600,
        bytesize=7,
        parity="E",
        timeout=2.0
    )

    client = ModbusClient(transport)

    try:
        with client:
            # Write 32-bit float
            print("\n1. Writing 32-bit float...")
            temperature = 25.6
            client.write_float32(slave_id=1, start_address=20, value=temperature)
            print(f"   Written temperature: {temperature}°C")

            # Read 32-bit float
            print("\n2. Reading 32-bit float...")
            read_temp = client.read_float32(slave_id=1, start_address=20)
            print(f"   Read temperature: {read_temp}°C")

            # Write 32-bit signed integer
            print("\n3. Writing 32-bit signed integer...")
            pressure = -12345
            client.write_int32(slave_id=1, start_address=22, value=pressure)
            print(f"   Written pressure: {pressure}")

            # Read 32-bit signed integer
            print("\n4. Reading 32-bit signed integer...")
            read_pressure = client.read_int32(slave_id=1, start_address=22)
            print(f"   Read pressure: {read_pressure}")

            # Write string
            print("\n5. Writing string...")
            device_name = "ASCII_Device"
            client.write_string(slave_id=1, start_address=30, value=device_name)
            print(f"   Written device name: '{device_name}'")

            # Read string
            print("\n6. Reading string...")
            read_name = client.read_string(
                slave_id=1,
                start_address=30,
                length=len(device_name.encode("utf-8")),
            )
            print(f"   Read device name: '{read_name}'")

            # Test different byte and word orders
            print(
                "\n7. Testing different byte and word orders..."
            )
            test_value = 3.14159

            # Big endian, high word first (default)
            client.write_float32(
                slave_id=1,
                start_address=40,
                value=test_value,
                byte_order="big",
                word_order="high",
            )
            read_val1 = client.read_float32(
                slave_id=1, start_address=40, byte_order="big", word_order="high"
            )
            print(
                f"   Big/High: Written {test_value}, Read {read_val1}"
            )

            # Little endian, low word first
            client.write_float32(
                slave_id=1,
                start_address=42,
                value=test_value,
                byte_order="little",
                word_order="low",
            )
            read_val2 = client.read_float32(
                slave_id=1, start_address=42, byte_order="little", word_order="low"
            )
            print(
                f"   Little/Low: Written {test_value}, Read {read_val2}"
            )

    except Exception as e:
        print(f"Advanced operation failed: {e}")


def debugging_example():
    """Debugging example - ASCII protocol advantages"""
    print("\n=== Sync ASCII Debugging Example ===")
    print(
        "ASCII protocol advantages: High readability, easy debugging and monitoring")

    transport = AsciiTransport(
        port="COM10",
        baudrate=9600,
        bytesize=7,
        parity="E",
        timeout=2.0
    )

    client = ModbusClient(transport)

    try:
        with client:
            print("\nDemonstrating ASCII protocol readability...")

            # Enable protocol-level debugging (optional)
            # ModbusLogger.enable_protocol_debug()

            for i in range(3):
                # Read registers
                registers = client.read_holding_registers(
                    slave_id=1, start_address=i, quantity=1
                )
                print(f"   Read #{i + 1}: Reg {i} = {registers[0]}")

                # Write register
                test_value = 1000 + i * 100
                client.write_single_register(slave_id=1, address=i, value=test_value)
                print(f"   Writ #{i + 1}: Reg {i} = {test_value}")

                time.sleep(0.5)

            print("Note: In serial monitoring tools, you can see readable ASCII format data frames")
            print("Example read command might display as: :010300000001FA")

    except Exception as e:
        print(f"Debugging example failed: {e}")


def main():
    """Main function"""
    print("ModbusLink Sync ASCII Client Example")
    print("=" * 60)

    print("Note: This example requires a Modbus ASCII device connected to serial port")
    print("\nASCII Protocol Features:")
    print("  - Uses ASCII character encoding, easy to debug")
    print("  - LRC checksum, simple and reliable")
    print("  - Data frames are highly readable")
    print("  - Transmission efficiency is relatively low")
    print("Please modify serial port parameters to match your device:")
    print("  - port: COM10 (Windows) 或 /dev/ttyUSB0 (Linux)")
    print("  - baudrate: 9600")
    print("  - bytesize: 7")
    print("  - parity: E ")
    print("  - slave_id: 1")

    try:
        # Execute examples sequentially
        basic_operations_example()
        advanced_data_types_example()
        debugging_example()

        print("\n=== All Examples Completed ===")

    except KeyboardInterrupt:
        print("\nUser interrupted")
    except ConnectionError as e:
        print(f"\nNO!!! Connection error: {e}")
        print("Please check:")
        print("  - Serial port exists and is available")
        print("  - Serial port is not occupied by other programs")
        print("  - Serial port parameters are correct")
        print("  - Device supports ASCII protocol")
    except TimeoutError as e:
        print(f"\nNO!!! Timeout error: {e}")
        print("Please check:")
        print("  - Modbus device is connected and working properly")
        print("  - Serial cable is working properly")
        print("  - Baud rate and other parameters match the device")
        print("  - ASCII protocol parameters are correct")
    except ModbusException as e:
        print(f"\nNO!!! Modbus protocol exception: {e}")
        print("Please check:")
        print("  - Slave address is correct")
        print("  - Register address is valid")
        print("  - Device supports the requested function code")
        print("  - LRC checksum is correct")
    except Exception as e:
        print(f"\nNO!!! Unknown error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
