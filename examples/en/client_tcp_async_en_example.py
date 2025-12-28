"""
ModbusLink 异步TCP客户端示例
演示如何使用异步TCP传输层进行Modbus通信，
包括基本的读写操作、高级数据类型操作、并发操作和回调机制。

ModbusLink Async TCP Client Example
Demonstrates how to use async TCP transport for Modbus communication,
including basic read/write operations, advanced data type operations, concurrent operations and callback mechanisms.
"""

import asyncio
import logging
from src.modbuslink import (
    AsyncModbusClient,
    AsyncTcpTransport,
    ConnectionError,
    TimeoutError,
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
    print("\n=== Async TCP Basic Operations Example ===")

    # Create async TCP transport
    transport = AsyncTcpTransport(
        host="127.0.0.1",  # Modbus TCP server address
        port=502,  # Standard Modbus TCP port
        timeout=5.0
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
    print("\n=== Async TCP Advanced Data Types Example ===")

    transport = AsyncTcpTransport(
        host="127.0.0.1",
        port=502,
        timeout=5.0
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

            # Write 32-bit signed integer
            print("\n5. Writing 32-bit signed integer...")
            pressure = -12345
            await client.write_int32(slave_id=1, start_address=28, value=pressure)
            print(f"   Written pressure: {pressure}")

            # Read 32-bit signed integer
            print("\n6. Reading 32-bit signed integer...")
            read_pressure = await client.read_int32(slave_id=1, start_address=28)
            print(f"   Read pressure: {read_pressure}")

            # Write string
            print("\n9. Writing string...")
            device_name = "AsyncTCP_Device_2024"
            await client.write_string(slave_id=1, start_address=40, value=device_name)
            print(f"   Written device name: '{device_name}'")

            # Read string
            print("\n10. Reading string...")
            read_name = await client.read_string(
                slave_id=1,
                start_address=40,
                length=len(device_name.encode("utf-8")),
            )
            print(f"   Read device name: '{read_name}'")

            # Test different byte and word orders
            print(
                "\n11. Testing different byte and word orders..."
            )
            test_value = 3.14159

            # Big endian, high word first (default)
            await client.write_float32(
                slave_id=1,
                start_address=50,
                value=test_value,
                byte_order="big",
                word_order="high",
            )
            read_val1 = await client.read_float32(
                slave_id=1, start_address=50, byte_order="big", word_order="high"
            )
            print(
                f"   Big/High: Written {test_value}, Read {read_val1}"
            )

            # Little endian, low word first
            await client.write_float32(
                slave_id=1,
                start_address=52,
                value=test_value,
                byte_order="little",
                word_order="low",
            )
            read_val2 = await client.read_float32(
                slave_id=1, start_address=52, byte_order="little", word_order="low"
            )
            print(
                f"   Little/Low: Written {test_value}, Read {read_val2}"
            )

        except Exception as e:
            print(f"Advanced operation failed: {e}")


async def callback_example():
    """Callback mechanism example"""
    print("\n=== Async TCP Callback Mechanism Example ===")

    # Define callback functions
    def on_register_read(registers):
        print(
            f"   [Callback] Read register values: {registers}"
        )

    def on_register_write():
        print("   [Callback] Register write completed")

    def on_float_read(value):
        print(f"   [Callback] Read float value: {value}")

    def on_coil_operation(result):
        print(f"   [Callback] Coil operation result: {result}")

    transport = AsyncTcpTransport(
        host="127.0.0.1",
        port=502,
        timeout=5.0
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

            print("\n4. Coil operation with callback...")
            coils = await client.read_coils(
                slave_id=1, start_address=0, quantity=8, callback=on_coil_operation
            )
            print(f"   Main thread received coil status: {coils}")

            # Wait a bit for callbacks to complete
            await asyncio.sleep(0.1)

        except Exception as e:
            print(f"Callback example failed: {e}")


async def concurrent_operations_example():
    """Concurrent operations example"""
    print("\n=== Async TCP Concurrent Operations Example ===")

    transport = AsyncTcpTransport(
        host="127.0.0.1",
        port=502,
        timeout=5.0
    )

    async with AsyncModbusClient(transport) as client:
        try:
            print(
                "\nExecuting multiple read operations concurrently..."
            )

            # Create multiple concurrent tasks
            tasks = [
                client.read_holding_registers(slave_id=1, start_address=0, quantity=4),
                client.read_holding_registers(slave_id=1, start_address=10, quantity=4),
                client.read_holding_registers(slave_id=1, start_address=20, quantity=4),
                client.read_coils(slave_id=1, start_address=0, quantity=16),
                client.read_input_registers(slave_id=1, start_address=0, quantity=8),
                client.read_discrete_inputs(slave_id=1, start_address=0, quantity=16),
            ]

            # Execute all tasks concurrently
            start_time = asyncio.get_event_loop().time()
            results = await asyncio.gather(*tasks)
            end_time = asyncio.get_event_loop().time()

            print(
                f"   Concurrent execution time: {end_time - start_time:.3f}秒"
            )
            print(f"   Holding registers 0-3: {results[0]}")
            print(f"   Holding registers 10-13: {results[1]}")
            print(f"   Holding registers 20-23: {results[2]}")
            print(f"   Coils 0-15: {results[3]}")
            print(f"   Input registers 0-7: {results[4]}")
            print(f"   Discrete inputs 0-15: {results[5]}")

            print(
                "\nExecuting mixed read/write operations concurrently..."
            )

            # Create mixed read/write tasks
            mixed_tasks = [
                client.write_single_register(slave_id=1, address=100, value=1001),
                client.write_single_register(slave_id=1, address=101, value=1002),
                client.write_single_register(slave_id=1, address=102, value=1003),
                client.read_holding_registers(slave_id=1, start_address=100, quantity=3),
            ]

            # Execute mixed tasks concurrently
            start_time = asyncio.get_event_loop().time()
            mixed_results = await asyncio.gather(*mixed_tasks)
            end_time = asyncio.get_event_loop().time()

            print(
                f"   Mixed operations time: {end_time - start_time:.3f}秒"
            )
            print(f"   Read result: {mixed_results[3]}")

        except Exception as e:
            print(f"Concurrent operation failed: {e}")


async def industrial_monitoring_example():
    """Async industrial monitoring example"""
    print("\n=== Async TCP Industrial Monitoring Example ===")

    transport = AsyncTcpTransport(
        host="127.0.0.1",
        port=502,
        timeout=5.0
    )

    async with AsyncModbusClient(transport) as client:
        try:
            print("Async continuously monitoring industrial equipment data...")

            # Create monitoring tasks
            async def monitor_temperature():
                """Monitor temperature sensor"""
                for i in range(5):
                    temp = await client.read_float32(slave_id=1, start_address=100)
                    status = "Normal" if 0 <= temp <= 100 else "Abnormal"
                    print(f"   [Temperature Monitor] #{i + 1}: {temp:.1f}°C ({status})")
                    await asyncio.sleep(1)

            async def monitor_pressure():
                """Monitor pressure sensor"""
                for i in range(5):
                    pressure_raw = await client.read_holding_registers(slave_id=1, start_address=104, quantity=1)
                    pressure = pressure_raw[0] / 10.0
                    status = "Normal" if 0 <= pressure <= 10 else "Abnormal"
                    print(f"   [Pressure Monitor] #{i + 1}: {pressure:.1f}bar ({status})")
                    await asyncio.sleep(1.2)

            async def monitor_motor_status():
                """Monitor motor status"""
                for i in range(5):
                    status_bits = await client.read_coils(slave_id=1, start_address=0, quantity=8)
                    motor_running = status_bits[0]
                    motor_fault = status_bits[1]
                    emergency_stop = status_bits[2]

                    status_text = []
                    if motor_running:
                        status_text.append("Running")
                    if motor_fault:
                        status_text.append("Fault")
                    if emergency_stop:
                        status_text.append("Emergency Stop")

                    status_str = ", ".join(status_text) if status_text else "停止"
                    print(f"   [Motor Monitor] #{i + 1}: {status_str}")
                    await asyncio.sleep(1.5)

            async def monitor_production_counter():
                """Monitor production counter"""
                for i in range(5):
                    counter = await client.read_uint32(slave_id=1, start_address=200)
                    print(f"   [Production Counter] #{i + 1}: {counter}件")
                    await asyncio.sleep(2)

            async def control_system_heartbeat():
                """Control system heartbeat"""
                for i in range(5):
                    # Write heartbeat signal
                    await client.write_single_register(slave_id=1, address=999, value=i + 1)
                    print(f"   [System Heartbeat] #{i + 1}: Heartbeat signal has been sent")
                    await asyncio.sleep(1.8)

            # Execute all monitoring tasks concurrently
            await asyncio.gather(
                monitor_temperature(),
                monitor_pressure(),
                monitor_motor_status(),
                monitor_production_counter(),
                control_system_heartbeat()
            )

        except Exception as e:
            print(f"Async industrial monitoring failed: {e}")


async def main():
    """Main function"""
    print("ModbusLink Async TCP Client Example")
    print("=" * 60)

    print("Note: This example requires a Modbus TCP server")
    print("\nAsync TCP Advantages:")
    print("  - Non-blocking network I/O")
    print("  - Supports high concurrent connections")
    print("  - Excellent network performance")
    print("  - Suitable for distributed systems")
    print("\nRecommended Modbus TCP servers:")
    print("  - ModbusPal (free simulator)")
    print("  - QModMaster (open source tool)")
    print("  - Industrial PLC devices")
    print("Please modify connection parameters to match your server:")
    print("  - host: 127.0.0.1")
    print("  - port: 502")
    print("  - slave_id: 1")

    try:
        # Execute examples sequentially
        await basic_operations_example()
        await advanced_data_types_example()
        await callback_example()
        await concurrent_operations_example()
        await industrial_monitoring_example()

        print("\n=== All Examples Completed ===")

    except KeyboardInterrupt:
        print("\nUser interrupted")
    except ConnectionError as e:
        print(f"\nNO!!! Connection error: {e}")
        print("Please check:")
        print("  - Modbus TCP server is running")
        print("  - Server address and port are correct")
        print("  - Network connection is working")
        print("  - Firewall is not blocking the connection")
    except TimeoutError as e:
        print(f"\nNO!!! Timeout error: {e}")
        print("Please check:")
        print("  - Network latency is too high")
        print("  - Server is responding normally")
        print("  - Timeout setting is reasonable")
    except ModbusException as e:
        print(f"\nNO!!! Modbus protocol exception: {e}")
        print("Please check:")
        print("  - Slave address is correct")
        print("  - Register address is valid")
        print("  - Server supports the requested function code")
    except Exception as e:
        print(f"\nNO!!! Unknown error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Run async main function
    asyncio.run(main())
