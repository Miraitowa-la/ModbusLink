"""
ModbusLink Sync TCP Client Example
Demonstrates how to use sync TCP transport for Modbus communication,
including basic read/write operations, advanced data type operations and error handling.
"""

import logging
import time
from src.modbuslink import (
    ModbusClient,
    TcpTransport,
    ConnectionError,
    TimeoutError,
    InvalidResponseError,
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
    print("\n=== Sync TCP Basic Operations Example ===")

    # Create TCP transport
    transport = TcpTransport(host="127.0.0.1", port=502, timeout=5.0)

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

            # Read input registers
            print("\n7. Reading input registers...")
            input_registers = client.read_input_registers(
                slave_id=1, start_address=0, quantity=5
            )
            print(f"   Input register values: {input_registers}")

            # Read discrete inputs
            print("\n8. Reading discrete inputs...")
            discrete_inputs = client.read_discrete_inputs(
                slave_id=1, start_address=0, quantity=8
            )
            print(f"   Discrete input status: {discrete_inputs}")

    except Exception as e:
        print(f"Operation failed: {e}")


def advanced_data_types_example():
    """Advanced data types example"""
    print("\n=== Sync TCP Advanced Data Types Example ===")

    transport = TcpTransport(host="127.0.0.1", port=502, timeout=5.0)
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
            device_name = "TCP_Device"
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


def industrial_monitoring_example():
    """Industrial monitoring example"""
    print("\n=== Sync TCP Industrial Monitoring Example ===")

    transport = TcpTransport(host="127.0.0.1", port=502, timeout=5.0)
    client = ModbusClient(transport)

    try:
        with client:
            print("Continuously monitoring industrial device data...")
            for i in range(3):
                # Read temperature sensor (float)
                temp = client.read_float32(slave_id=1, start_address=100)

                # Read pressure sensor (integer, divide by 10)
                pressure_raw = client.read_input_registers(slave_id=1, start_address=102, quantity=1)[0]
                pressure = pressure_raw / 10.0

                # Read device running status (coil)
                running = client.read_coils(slave_id=1, start_address=0, quantity=1)[0]

                # Read alarm status (discrete input)
                alarm = client.read_discrete_inputs(slave_id=1, start_address=0, quantity=1)[0]

                # Read production counter (32-bit integer)
                counter = client.read_int32(slave_id=1, start_address=110)

                print(
                    f"  Monitoring #{i + 1} (Cycle {i + 1}): Temperature={temp:.1f}°C, Pressure={pressure:.1f}bar, "
                    f"Running={'Yes' if running else 'No'}, Alarm={'Yes' if alarm else 'No'}, Counter={counter}"
                )

                # Adjust setpoint based on temperature
                if temp > 30.0:
                    new_setpoint = 28.0
                    client.write_float32(slave_id=1, start_address=120, value=new_setpoint)
                    print(f"    Temperature too high, adjusted setpoint to {new_setpoint}°C")

                if i < 2:  # Don't wait on last iteration
                    time.sleep(2)

    except Exception as e:
        print(f"Industrial monitoring failed: {e}")


def main():
    """Main function"""
    print("ModbusLink Sync TCP Client Example")
    print("=" * 60)

    print("Note: This example requires a Modbus TCP server running on 127.0.0.1:502")
    print("You can use ModbusLink's slave simulator:")
    print("\n  from modbuslink import ModbusSlave")
    print("  slave = ModbusSlave(slave_id=1)")
    print("  slave.start_tcp_server('127.0.0.1', 502)")

    try:
        # Execute examples sequentially
        basic_operations_example()
        advanced_data_types_example()
        industrial_monitoring_example()

        print("\n=== All Examples Completed ===")

    except KeyboardInterrupt:
        print("\nUser interrupted")
    except ConnectionError as e:
        print(f"\nNO!!! Connection error: {e}")
        print("Please check:")
        print(f"  - Target device 127.0.0.1:502 is reachable")
        print("  - Network connection is normal")
        print("  - Firewall is blocking connection")
        print("  - Device supports Modbus TCP protocol")
    except TimeoutError as e:
        print(f"\nNO!!! Timeout error: {e}")
        print("Please check:")
        print("  - Network latency is too high")
        print("  - Device response is normal")
        print("  - Timeout setting is reasonable")
    except InvalidResponseError as e:
        print(f"\nNO!!! Invalid response format: {e}")
        print("Please check:")
        print("  - Device correctly implements Modbus TCP protocol")
        print("  - Network transmission has data corruption")
    except ModbusException as e:
        print(f"\nNO!!! Modbus protocol exception: {e}")
        print("Please check:")
        print("  - Unit identifier is correct")
        print("  - Register address is valid")
        print("  - Device supports the requested function code")
    except Exception as e:
        print(f"\nNO!!! Unknown error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()