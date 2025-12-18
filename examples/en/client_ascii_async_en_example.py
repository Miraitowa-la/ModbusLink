"""
ModbusLink Async ASCII Client Example
Demonstrates how to use async ASCII transport for Modbus communication,
including basic read/write operations, advanced data type operations, debugging features and error handling.
"""

import asyncio
import logging
from src.modbuslink import (
    AsyncModbusClient,
    AsyncAsciiTransport,
    ConnectionError,
    TimeoutError,
    CRCError,
    ModbusException,
    InvalidResponseError
)
from src.modbuslink.utils.logging import ModbusLogger, Language

# Set logging
ModbusLogger.setup_logging(
    level=logging.INFO,
    enable_debug=True,
    language=Language.EN,
)


async def basic_operations_example():
    """Basic operations example"""
    print("\n=== Async ASCII Basic Operations Example ===")

    # Create async ASCII transport
    transport = AsyncAsciiTransport(
        port="COM10",  # Windows: COM10, Linux: /dev/ttyUSB0
        baudrate=9600,
        timeout=3.0
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

            # Input registers and discrete inputs
            print("\n7. Reading input registers...")
            input_regs = await client.read_input_registers(
                slave_id=1, start_address=0, quantity=4
            )
            print(f"   Input register values: {input_regs}")

            print("\n8. Reading discrete inputs...")
            discrete_inputs = await client.read_discrete_inputs(
                slave_id=1, start_address=0, quantity=8
            )
            print(f"   Discrete input status: {discrete_inputs}")

        except Exception as e:
            print(f"Operation failed: {e}")


async def advanced_data_types_example():
    """Advanced data types example"""
    print("\n=== Async ASCII Advanced Data Types Example ===")

    transport = AsyncAsciiTransport(
        port="COM10",
        baudrate=9600,
        timeout=3.0
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

            # Write 32-bit unsigned integer(It seems there is a problem. It will be fixed later.)
            # print("\n5. Writing 32-bit unsigned integer...")
            # counter = 65535  # Smaller value suitable for ASCII transport
            # await client.write_uint32(slave_id=1, start_address=24, value=counter)
            # print(f"   Written counter value: {counter}")

            # Read 32-bit unsigned integer(It seems there is a problem. It will be fixed later.)
            # print("\n6. Reading 32-bit unsigned integer...")
            # read_counter = await client.read_uint32(slave_id=1, start_address=24)
            # print(f"   Read counter value: {read_counter}")

            # Write string(It seems there is a problem. It will be fixed later.)
            # print("\n7. Writing string...")
            # device_name = "AsyncASCII_Dev"
            # await client.write_string(slave_id=1, start_address=30, value=device_name)
            # print(f"   Written device name: '{device_name}'")

            # Read string(It seems there is a problem. It will be fixed later.)
            # print("\n8. Reading string...")
            # read_name = await client.read_string(
            #     slave_id=1,
            #     start_address=30,
            #     length=len(device_name.encode("utf-8")),
            # )
            # print(f"   Read device name: '{read_name}'")

            # Test different byte and word orders
            print(
                "\n9. Testing different byte and word orders..."
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


async def debugging_example():
    """Debugging features example"""
    print("\n=== Async ASCII Debugging Features Example ===")

    # Transport with debugging enabled
    transport = AsyncAsciiTransport(
        port="COM10",
        baudrate=9600,
        timeout=3.0
    )

    async with AsyncModbusClient(transport) as client:
        try:
            print("\n1. ASCII protocol features demonstration...")
            print("   ASCII protocol uses readable hexadecimal characters")
            print("   Each byte is represented by two ASCII characters")
            print("   Uses LRC checksum instead of CRC")

            # Demonstrate ASCII frame format
            print("\n2. ASCII frame format example:")
            print("   Start character: ':' (0x3A)")
            print("   Slave address: 01 (ASCII)")
            print("   Function code: 03 (ASCII)")
            print("   Data: 0000 0004 (ASCII)")
            print("   LRC checksum: F8 (ASCII)")
            print("   End characters: CR LF (0x0D 0x0A)")

            # Perform actual operations to observe ASCII communication
            print("\n3. Performing read operation to observe ASCII communication...")
            registers = await client.read_holding_registers(
                slave_id=1, start_address=0, quantity=4
            )
            print(f"   Read result: {registers}")

            print("\n4. Performing write operation to observe ASCII communication...")
            await client.write_single_register(slave_id=1, address=0, value=0x1234)
            print("   Write completed")

            # ASCII protocol advantages and disadvantages
            print("\n5. ASCII protocol characteristics analysis:")
            print("   Advantages:")
            print("     - High readability, easy to debug")
            print("     - Good compatibility")
            print("     - Easy error detection")
            print("   Disadvantages:")
            print("     - Low transmission efficiency")
            print("     - High bandwidth usage")
            print("     - Slow processing speed")

        except Exception as e:
            print(f"Debugging example failed: {e}")


async def error_handling_example():
    """Error handling example"""
    print("\n=== Async ASCII Error Handling Example ===")

    transport = AsyncAsciiTransport(
        port="COM10",
        baudrate=9600,
        timeout=3.0
    )

    async with AsyncModbusClient(transport) as client:
        try:
            print("\n1. Testing timeout handling...")
            try:
                # Try to read potentially non-existent registers
                registers = await client.read_holding_registers(
                    slave_id=99, start_address=0, quantity=1  # Use non-existent slave ID
                )
                print(f"   Unexpected success: {registers}")
            except TimeoutError as e:
                print(f"   Timeout error correctly caught: {e}")

            print("\n2. Testing LRC checksum error handling...")
            # 注意：Note: LRC errors are usually handled automatically by transport layer
            print("   LRC checksum is automatically handled at transport layer")

            print("\n3. Testing Modbus exception handling...")
            try:
                # Try to read invalid register address
                registers = await client.read_holding_registers(
                    slave_id=1, start_address=65535, quantity=1  # Invalid address
                )
                print(f"   Unexpected success: {registers}")
            except InvalidResponseError as e:
                print(f"   Modbus exception correctly caught: {e}")

            print("\n4. Testing connection error handling...")
            # This test may not trigger when actual device is connected
            print(
                "   Connection errors usually occur during transport initialization")

            print("\n5. Error recovery strategies:")
            print("   - Automatic retry mechanism")
            print("   - Connection status monitoring")
            print("   - Graceful degradation handling")
            print("   - Detailed error logging")

        except Exception as e:
            print(f"Error handling example failed: {e}")


async def performance_comparison_example():
    """Performance comparison example"""
    print("\n=== Async ASCII Performance Comparison Example ===")

    transport = AsyncAsciiTransport(
        port="COM10",
        baudrate=9600,
        timeout=3.0
    )

    async with AsyncModbusClient(transport) as client:
        try:
            print("\n1. Single operation performance test...")

            # Test read operation performance
            start_time = asyncio.get_event_loop().time()
            registers = await client.read_holding_registers(
                slave_id=1, start_address=0, quantity=10
            )
            end_time = asyncio.get_event_loop().time()
            read_time = end_time - start_time
            print(f"   Read 10 registers time: {read_time:.3f}秒")

            # Test write operation performance
            start_time = asyncio.get_event_loop().time()
            await client.write_multiple_registers(
                slave_id=1, start_address=10, values=[i for i in range(10)]
            )
            end_time = asyncio.get_event_loop().time()
            write_time = end_time - start_time
            print(f"   Write 10 registers time: {write_time:.3f}秒")

            print("\n2. Batch operation performance test...")

            # Batch read test
            start_time = asyncio.get_event_loop().time()
            tasks = [
                client.read_holding_registers(slave_id=1, start_address=i * 10, quantity=5)
                for i in range(5)
            ]
            results = await asyncio.gather(*tasks)
            end_time = asyncio.get_event_loop().time()
            batch_time = end_time - start_time
            print(f"   Concurrent read 5 groups time: {batch_time:.3f}秒")
            print(f"   Average time per group: {batch_time / 5:.3f}秒")

            print("\n3. ASCII vs RTU performance comparison analysis:")
            print("   ASCII protocol characteristics:")
            print(f"     - Single read time: ~{read_time:.3f}s")
            print(f"     - Single write time: ~{write_time:.3f}s")
            print("     - Data volume is 2x of RTU")
            print("     - Slower transmission speed")
            print("     - Debug-friendly")

            print("\n   Recommended use cases:")
            print("     - Debugging and development phase")
            print("     - Low-speed serial communication")
            print("     - Scenarios requiring manual monitoring")
            print("     - Compatibility with legacy devices")

        except Exception as e:
            print(f"Performance comparison example failed: {e}")


async def sensor_monitoring_example():
    """Async sensor monitoring example"""
    print("\n=== Async ASCII Sensor Monitoring Example ===")

    transport = AsyncAsciiTransport(
        port="COM10",
        baudrate=9600,
        timeout=3.0
    )

    async with AsyncModbusClient(transport) as client:
        try:
            print("Async continuously monitoring sensor data...")

            # Create monitoring tasks
            async def monitor_temperature():
                """Monitor temperature sensor"""
                for i in range(3):
                    temp = await client.read_float32(slave_id=1, start_address=100)
                    status = "Normal" if 0 <= temp <= 100 else "Abnormal"
                    print(f"   [Temperature Monitor] #{i + 1}: {temp:.1f}°C ({status})")
                    await asyncio.sleep(2)  # ASCII较慢，增加间隔 | ASCII is slower, increase interval

            async def monitor_humidity():
                """Monitor humidity sensor"""
                for i in range(3):
                    humidity_raw = await client.read_holding_registers(slave_id=1, start_address=102, quantity=1)
                    humidity = humidity_raw[0] / 10.0
                    status = "Normal" if 0 <= humidity <= 100 else "Abnormal"
                    print(f"   [Humidity Monitor] #{i + 1}: {humidity:.1f}% ({status})")
                    await asyncio.sleep(2.5)

            async def monitor_status():
                """Monitor device status"""
                for i in range(3):
                    status = await client.read_coils(slave_id=1, start_address=0, quantity=1)
                    print(f"   [Status Monitor] #{i + 1}: {'Start' if status[0] else 'Stop'}")
                    await asyncio.sleep(3)

            # Execute all monitoring tasks concurrently
            await asyncio.gather(
                monitor_temperature(),
                monitor_humidity(),
                monitor_status()
            )

        except Exception as e:
            print(f"Async sensor monitoring failed: {e}")


async def main():
    """Main function"""
    print("ModbusLink Async ASCII Client Example")
    print("=" * 60)

    print("Note: This example requires a Modbus ASCII device connected to serial port")
    print("\nAsync ASCII Characteristics:")
    print("  - Non-blocking serial I/O")
    print("  - Readable ASCII format")
    print("  - Easy to debug and monitor")
    print("  - Strong compatibility")
    print("  - Lower transmission efficiency")
    print("\nConfiguration notes:")
    print("  - ASCII protocol typically uses lower baud rates")
    print("  - Recommended baud rates: 1200, 2400, 4800, 9600")
    print("  - Data bits: 7 or 8 bits")
    print("  - Parity: even, odd, or none")
    print("  - Stop bits: 1 or 2 bits")
    print("Please modify serial port parameters to match your device:")
    print("  - port: COM10 (Windows) or /dev/ttyUSB0 (Linux)")
    print("  - baudrate: 9600")
    print("  - slave_id: 1")

    try:
        # Execute examples sequentially
        await basic_operations_example()
        await advanced_data_types_example()
        await debugging_example()
        await error_handling_example()
        # await performance_comparison_example()  # It seems there is a problem. It will be fixed later.
        # await sensor_monitoring_example()  # It seems there is a problem. It will be fixed later.

        print("\n=== All Examples Completed ===")

    except KeyboardInterrupt:
        print("\nUser interrupted")
    except ConnectionError as e:
        print(f"\nNO!!!Connection error: {e}")
        print("Please check:")
        print("  - Serial port exists and is available")
        print("  - Serial port is not occupied by other programs")
        print("  - Serial port parameters are correct")
        print("  - Device supports ASCII mode")
    except TimeoutError as e:
        print(f"\nNO!!! Timeout error: {e}")
        print("Please check:")
        print("  - Modbus device is connected and working properly")
        print("  - Serial cable is working properly")
        print("  - Baud rate and other parameters match the device")
        print("  - Device is configured for ASCII mode")
    except CRCError as e:
        print(f"\nNO!!! CRC verification error: {e}")
        print("Please check:")
        print("  - Serial cable has interference")
        print("  - Baud rate is correct")
        print("  - Device supports Modbus ASCII protocol")
        print("  - Data bits, parity, stop bits settings")
    except ModbusException as e:
        print(f"\nNO!!! Modbus protocol exception: {e}")
        print("Please check:")
        print("  - Slave address is correct")
        print("  - Register address is valid")
        print("  - Device supports the requested function code")
        print("  - Device is in ASCII mode")
    except Exception as e:
        print(f"\nNO!!! Unknown error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Run async main function
    asyncio.run(main())
