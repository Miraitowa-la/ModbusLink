"""
ModbusLink Async RTU Client Example
Demonstrates how to use async RTU transport for Modbus communication,
including basic read/write operations, advanced data type operations, concurrent operations and callback mechanisms.
"""

import asyncio
import logging
from src.modbuslink import (
    AsyncModbusClient,
    AsyncRtuTransport,
    ConnectionError,
    TimeoutError,
    CRCError,
    ModbusException,
    ModbusLogger,
    Language,
    set_language,
)

set_language(Language.EN)

# Set logging
ModbusLogger.setup_logging(
    level=logging.INFO,
    enable_debug=True,
)


async def basic_operations_example():
    """Basic operations example"""
    print("\n=== Async RTU Basic Operations Example ===")

    # Create async RTU transport
    transport = AsyncRtuTransport(
        port="COM10",  # Windows: COM10, Linux: /dev/ttyUSB0
        baudrate=9600,
        timeout=2.0
    )

    # Create async client
    async with AsyncModbusClient(transport) as client:
        try:
            # Read holding registers
            print("\n1. Reading holding registers...")
            registers = await client.read_holding_registers(
                slave_id=1, start_address=0, quantity=4
            )
            print(f"   Register values: {registers}")

            # Write single register
            print("\n2. Writing single register...")
            await client.write_single_register(slave_id=1, address=0, value=1234)
            print("   Write completed")

            # Verify write result
            print("\n3. Verifying write result...")
            value = await client.read_holding_registers(
                slave_id=1, start_address=0, quantity=1
            )
            print(f"   Register 0 value: {value[0]}")

            # Write multiple registers
            print("\n4. Writing multiple registers...")
            values = [1111, 2222, 3333, 4444]
            await client.write_multiple_registers(
                slave_id=1, start_address=10, values=values
            )
            print(f"   Written values: {values}")

            # Read multiple registers
            print("\n5. Reading multiple registers...")
            read_values = await client.read_holding_registers(
                slave_id=1, start_address=10, quantity=4
            )
            print(f"   Read values: {read_values}")

            # Coil operations
            print("\n6. Coil operations...")
            await client.write_single_coil(slave_id=1, address=0, value=True)
            coils = await client.read_coils(slave_id=1, start_address=0, quantity=8)
            print(f"   Coil status: {coils}")

            # Write multiple coils
            coil_values = [True, False, True, False, True, False, True, False]
            await client.write_multiple_coils(
                slave_id=1, start_address=0, values=coil_values
            )
            coils = await client.read_coils(slave_id=1, start_address=0, quantity=8)
            print(f"   Updated coil status: {coils}")

        except Exception as e:
            print(f"Operation failed: {e}")


async def advanced_data_types_example():
    """Advanced data types example"""
    print("\n=== Async RTU Advanced Data Types Example ===")

    transport = AsyncRtuTransport(
        port="COM10",
        baudrate=9600,
        timeout=2.0
    )

    async with AsyncModbusClient(transport) as client:
        try:
            # Write 32-bit float
            print("\n1. Writing 32-bit float...")
            temperature = 25.6
            await client.write_float32(slave_id=1, start_address=20, value=temperature)
            print(f"   Written temperature: {temperature}°C")

            # Read 32-bit float
            print("\n2. Reading 32-bit float...")
            read_temp = await client.read_float32(slave_id=1, start_address=20)
            print(f"   Read temperature: {read_temp}°C")

            # Write 32-bit signed integer
            print("\n3. Writing 32-bit signed integer...")
            pressure = -12345
            await client.write_int32(slave_id=1, start_address=22, value=pressure)
            print(f"   Written pressure: {pressure}")

            # Read 32-bit signed integer
            print("\n4. Reading 32-bit signed integer...")
            read_pressure = await client.read_int32(slave_id=1, start_address=22)
            print(f"   Read pressure: {read_pressure}")

            # Write string
            print("\n5. Writing string...")
            device_name = "AsyncRTU_Device"
            await client.write_string(slave_id=1, start_address=30, value=device_name)
            print(f"   Written device name: '{device_name}'")

            # Read string
            print("\n6. Reading string...")
            read_name = await client.read_string(
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
            await client.write_float32(
                slave_id=1,
                start_address=40,
                value=test_value,
                byte_order="big",
                word_order="high",
            )
            read_val1 = await client.read_float32(
                slave_id=1, start_address=40, byte_order="big", word_order="high"
            )
            print(
                f"   Big/High: Written {test_value}, Read {read_val1}"
            )

            # Little endian, low word first
            await client.write_float32(
                slave_id=1,
                start_address=42,
                value=test_value,
                byte_order="little",
                word_order="low",
            )
            read_val2 = await client.read_float32(
                slave_id=1, start_address=42, byte_order="little", word_order="low"
            )
            print(
                f"   Little/Low: Written {test_value}, Read {read_val2}"
            )

        except Exception as e:
            print(f"Advanced operation failed: {e}")


async def callback_example():
    """Callback mechanism example"""
    print("\n=== Async RTU Callback Mechanism Example ===")

    # Define callback functions
    def on_register_read(registers):
        print(
            f"   [Callback] Read register values: {registers}"
        )

    def on_register_write():
        print("   [Callback] Register write completed")

    def on_float_read(value):
        print(f"   [Callback] Read float value: {value}")

    transport = AsyncRtuTransport(
        port="COM10",
        baudrate=9600,
        timeout=2.0
    )

    async with AsyncModbusClient(transport) as client:
        try:
            print("\n1. Register read with callback...")
            registers = await client.read_holding_registers(
                slave_id=1, start_address=0, quantity=4, callback=on_register_read
            )
            print(f"   Main thread received result: {registers}")

            print("\n2. Register write with callback...")
            await client.write_single_register(
                slave_id=1, address=5, value=9999, callback=on_register_write
            )
            print("   Main thread write completed")

            print("\n3. Float read with callback...")
            float_val = await client.read_float32(
                slave_id=1, start_address=20, callback=on_float_read
            )
            print(f"   Main thread received float: {float_val}")

            # Wait a bit for callbacks to complete
            await asyncio.sleep(0.1)

        except Exception as e:
            print(f"Callback example failed: {e}")


async def concurrent_operations_example():
    """Concurrent operations example"""
    print("\n=== Async RTU Concurrent Operations Example ===")

    transport = AsyncRtuTransport(
        port="COM10",
        baudrate=9600,
        timeout=2.0
    )

    async with AsyncModbusClient(transport) as client:
        try:
            print(
                "\nExecuting multiple read operations concurrently..."
            )

            # Create multiple concurrent tasks
            tasks = [
                client.read_holding_registers(slave_id=1, start_address=0, quantity=2),
                client.read_holding_registers(slave_id=1, start_address=10, quantity=2),
                client.read_holding_registers(slave_id=1, start_address=20, quantity=2),
                client.read_coils(slave_id=1, start_address=0, quantity=8),
                client.read_input_registers(slave_id=1, start_address=0, quantity=4),
            ]

            # Execute all tasks concurrently
            start_time = asyncio.get_event_loop().time()
            results = await asyncio.gather(*tasks)
            end_time = asyncio.get_event_loop().time()

            print(
                f"   Concurrent execution time: {end_time - start_time:.3f}秒"
            )
            print(f"   Holding registers 0-1: {results[0]}")
            print(f"   Holding registers 10-11: {results[1]}")
            print(f"   Holding registers 20-21: {results[2]}")
            print(f"   Coils 0-7: {results[3]}")
            print(f"   Input registers 0-3: {results[4]}")

        except Exception as e:
            print(f"Concurrent operation failed: {e}")


async def sensor_monitoring_example():
    """Async sensor monitoring example"""
    print("\n=== Async RTU Sensor Monitoring Example ===")

    transport = AsyncRtuTransport(
        port="COM10",
        baudrate=9600,
        timeout=2.0
    )

    async with AsyncModbusClient(transport) as client:
        try:
            print("Async continuously monitoring sensor data...")

            # Create monitoring tasks
            async def monitor_temperature():
                for i in range(3):
                    temp = await client.read_float32(slave_id=1, start_address=100)
                    print(f"   [Temperature Monitor] #{i + 1}: {temp:.1f}°C")
                    await asyncio.sleep(1)

            async def monitor_pressure():
                for i in range(3):
                    pressure_raw = await client.read_holding_registers(slave_id=1, start_address=104, quantity=1)
                    pressure = pressure_raw[0] / 10.0
                    print(f"   [Pressure Monitor] #{i + 1}: {pressure:.1f}bar")
                    await asyncio.sleep(1.5)

            async def monitor_status():
                for i in range(3):
                    status = await client.read_coils(slave_id=1, start_address=0, quantity=1)
                    print(f"   [Status Monitor] #{i + 1}: {'运行' if status[0] else '停止'}")
                    await asyncio.sleep(2)

            # Execute all monitoring tasks concurrently
            await asyncio.gather(
                monitor_temperature(),
                monitor_pressure(),
                monitor_status()
            )

        except Exception as e:
            print(f"Async sensor monitoring failed: {e}")


async def main():
    """Main function"""
    print("ModbusLink Async RTU Client Example")
    print("=" * 60)

    print("Note: This example requires a Modbus RTU device connected to serial port")
    print("\nAsync RTU Advantages:")
    print("  - Non-blocking I/O operations")
    print("  - Supports concurrent communication")
    print("  - Efficient resource utilization")
    print("  - Suitable for high-frequency data acquisition")
    print("Please modify serial port parameters to match your device:")
    print("  - port: COM10 (Windows) or /dev/ttyUSB0 (Linux)")
    print("  - baudrate: 9600")
    print("  - slave_id: 1")

    try:
        # Execute examples sequentially
        await basic_operations_example()
        await advanced_data_types_example()
        await callback_example()
        # await concurrent_operations_example() # 貌似有点问题后面在修复
        # await sensor_monitoring_example() # 貌似有点问题后面在修复

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
    # Run async main function
    asyncio.run(main())
