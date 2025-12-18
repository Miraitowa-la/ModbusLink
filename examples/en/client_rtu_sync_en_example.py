"""
ModbusLink Sync RTU Client Example
Demonstrates how to use sync RTU transport for Modbus communication,
including basic read/write operations, advanced data type operations and error handling.
"""

import logging
import time
from src.modbuslink import (
    ModbusClient,
    RtuTransport,
    ConnectionError,
    TimeoutError,
    CRCError,
    ModbusException,
)
from src.modbuslink.utils.logging import ModbusLogger, Language

# Set logging
ModbusLogger.setup_logging(
    level=logging.INFO,
    enable_debug=True,
    language=Language.EN
)


def basic_operations_example():
    """Basic operations example"""
    print("\n=== Sync RTU Basic Operations Example ===")

    # Create RTU transport
    transport = RtuTransport(
        port="COM10",  # Windows: COM10, Linux: /dev/ttyUSB0
        baudrate=9600,
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
    print("\n=== Sync RTU Advanced Data Types Example ===")

    transport = RtuTransport(
        port="COM10",
        baudrate=9600,
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

            # Test different byte and word orders
            print(
                "\n5. Testing different byte and word orders..."
            )
            test_value = 3.14159

            # Big endian, high word first (default)
            client.write_float32(
                slave_id=1,
                start_address=30,
                value=test_value,
                byte_order="big",
                word_order="high",
            )
            read_val1 = client.read_float32(
                slave_id=1, start_address=30, byte_order="big", word_order="high"
            )
            print(
                f"   Big/High: Written {test_value}, Read {read_val1}"
            )

            # Little endian, low word first
            client.write_float32(
                slave_id=1,
                start_address=32,
                value=test_value,
                byte_order="little",
                word_order="low",
            )
            read_val2 = client.read_float32(
                slave_id=1, start_address=32, byte_order="little", word_order="low"
            )
            print(
                f"   Little/Low: Written {test_value}, Read {read_val2}"
            )

    except Exception as e:
        print(f"Advanced operation failed: {e}")


def sensor_monitoring_example():
    """Sensor monitoring example"""
    print("\n=== Sync RTU Sensor Monitoring Example ===")

    transport = RtuTransport(
        port="COM10",
        baudrate=9600,
        timeout=2.0
    )

    client = ModbusClient(transport)

    try:
        with client:
            print("Continuously reading sensor data...")
            for i in range(3):
                # Read temperature sensor (float)
                temp = client.read_float32(slave_id=1, start_address=100)

                # Read humidity sensor (integer, divide by 100)
                humidity_raw = client.read_holding_registers(slave_id=1, start_address=104, quantity=1)[0]
                humidity = humidity_raw / 100.0

                # Read device status (coil)
                status = client.read_coils(slave_id=1, start_address=0, quantity=1)[0]

                print(
                    f"  Read #{i + 1}: Temp={temp:.1f}°C, Hum={humidity:.1f}%, Status={'Run' if status else 'Stop'}"
                )

                if i < 2:  # 最后一次不等待 | Don't wait on last iteration
                    time.sleep(1)

    except Exception as e:
        print(f"Sensor data reading failed: {e}")


def main():
    """Main function"""
    print("ModbusLink Sync RTU Client Example")
    print("=" * 60)

    print("Note: This example requires a Modbus RTU device connected to serial port")
    print("Please modify serial port parameters to match your device:")
    print("  - port: COM10 (Windows) 或 /dev/ttyUSB0 (Linux)")
    print("  - baudrate: 9600")
    print("  - slave_id: 1")

    try:
        # Execute examples sequentially
        basic_operations_example()
        advanced_data_types_example()
        sensor_monitoring_example()

        print("\n=== All Examples Completed ===")

    except KeyboardInterrupt:
        print("\nUser interrupted")
    except ConnectionError as e:
        print(f"\nNO!!! Connection error: {e}")
        print("Please check:")
        print("  - Serial port exists and is available")
        print("  - Serial port is not occupied by other programs")
        print("  - Serial port parameters are correct")
    except TimeoutError as e:
        print(f"\nNO!!! Timeout error: {e}")
        print("Please check:")
        print("  - Modbus device is connected and working properly")
        print("  - Serial cable is working properly")
        print("  - Baud rate and other parameters match the device")
    except CRCError as e:
        print(f"\nNO!!! CRC verification error: {e}")
        print("Please check:")
        print("  - Serial cable has interference")
        print("  - Baud rate is correct")
        print("  - Device supports Modbus RTU protocol")
    except ModbusException as e:
        print(f"\nNO!!! Modbus protocol exception: {e}")
        print("Please check:")
        print("  - Slave address is correct")
        print("  - Register address is valid")
        print("  - Device supports the requested function code")
    except Exception as e:
        print(f"\nNO!!! Unknown error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
