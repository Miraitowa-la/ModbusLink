"""
ModbusLink 异步RTU客户端示例
演示如何使用异步RTU传输层进行Modbus通信，
包括基本的读写操作、高级数据类型操作、并发操作和回调机制。

ModbusLink Async RTU Client Example
Demonstrates how to use async RTU transport for Modbus communication,
including basic read/write operations, advanced data type operations, concurrent operations and callback mechanisms.
"""

import asyncio
import logging
from modbuslink import (
    AsyncModbusClient,
    AsyncRtuTransport,
    ConnectionError,
    TimeoutError,
    CRCError,
    ModbusException,
)

# 配置日志 | Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


async def basic_operations_example():
    """基本操作示例 | Basic operations example"""
    print("\n=== 异步RTU基本操作示例 | Async RTU Basic Operations Example ===")

    # 创建异步RTU传输层 | Create async RTU transport
    transport = AsyncRtuTransport(
        port="COM1",  # Windows: COM1, Linux: /dev/ttyUSB0
        baudrate=9600,
        timeout=2.0
    )

    # 创建异步客户端 | Create async client
    async with AsyncModbusClient(transport) as client:
        try:
            # 读取保持寄存器 | Read holding registers
            print("\n1. 读取保持寄存器 | Reading holding registers...")
            registers = await client.read_holding_registers(
                slave_id=1, start_address=0, quantity=4
            )
            print(f"   寄存器值 | Register values: {registers}")

            # 写入单个寄存器 | Write single register
            print("\n2. 写入单个寄存器 | Writing single register...")
            await client.write_single_register(slave_id=1, address=0, value=1234)
            print("   写入完成 | Write completed")

            # 验证写入结果 | Verify write result
            print("\n3. 验证写入结果 | Verifying write result...")
            value = await client.read_holding_registers(
                slave_id=1, start_address=0, quantity=1
            )
            print(f"   寄存器0的值 | Register 0 value: {value[0]}")

            # 写入多个寄存器 | Write multiple registers
            print("\n4. 写入多个寄存器 | Writing multiple registers...")
            values = [1111, 2222, 3333, 4444]
            await client.write_multiple_registers(
                slave_id=1, start_address=10, values=values
            )
            print(f"   写入值 | Written values: {values}")

            # 读取多个寄存器 | Read multiple registers
            print("\n5. 读取多个寄存器 | Reading multiple registers...")
            read_values = await client.read_holding_registers(
                slave_id=1, start_address=10, quantity=4
            )
            print(f"   读取值 | Read values: {read_values}")

            # 线圈操作 | Coil operations
            print("\n6. 线圈操作 | Coil operations...")
            await client.write_single_coil(slave_id=1, address=0, value=True)
            coils = await client.read_coils(slave_id=1, start_address=0, quantity=8)
            print(f"   线圈状态 | Coil status: {coils}")

            # 写入多个线圈 | Write multiple coils
            coil_values = [True, False, True, False, True, False, True, False]
            await client.write_multiple_coils(
                slave_id=1, start_address=0, values=coil_values
            )
            coils = await client.read_coils(slave_id=1, start_address=0, quantity=8)
            print(f"   更新后的线圈状态 | Updated coil status: {coils}")

        except Exception as e:
            print(f"操作失败 | Operation failed: {e}")


async def advanced_data_types_example():
    """高级数据类型示例 | Advanced data types example"""
    print("\n=== 异步RTU高级数据类型示例 | Async RTU Advanced Data Types Example ===")

    transport = AsyncRtuTransport(
        port="COM1",
        baudrate=9600,
        timeout=2.0
    )

    async with AsyncModbusClient(transport) as client:
        try:
            # 写入32位浮点数 | Write 32-bit float
            print("\n1. 写入32位浮点数 | Writing 32-bit float...")
            temperature = 25.6
            await client.write_float32(slave_id=1, start_address=20, value=temperature)
            print(f"   写入温度值 | Written temperature: {temperature}°C")

            # 读取32位浮点数 | Read 32-bit float
            print("\n2. 读取32位浮点数 | Reading 32-bit float...")
            read_temp = await client.read_float32(slave_id=1, start_address=20)
            print(f"   读取温度值 | Read temperature: {read_temp}°C")

            # 写入32位有符号整数 | Write 32-bit signed integer
            print("\n3. 写入32位有符号整数 | Writing 32-bit signed integer...")
            pressure = -12345
            await client.write_int32(slave_id=1, start_address=22, value=pressure)
            print(f"   写入压力值 | Written pressure: {pressure}")

            # 读取32位有符号整数 | Read 32-bit signed integer
            print("\n4. 读取32位有符号整数 | Reading 32-bit signed integer...")
            read_pressure = await client.read_int32(slave_id=1, start_address=22)
            print(f"   读取压力值 | Read pressure: {read_pressure}")

            # 写入字符串 | Write string
            print("\n5. 写入字符串 | Writing string...")
            device_name = "AsyncRTU_Device"
            await client.write_string(slave_id=1, start_address=30, value=device_name)
            print(f"   写入设备名称 | Written device name: '{device_name}'")

            # 读取字符串 | Read string
            print("\n6. 读取字符串 | Reading string...")
            read_name = await client.read_string(
                slave_id=1,
                start_address=30,
                length=len(device_name.encode("utf-8")),
            )
            print(f"   读取设备名称 | Read device name: '{read_name}'")

            # 测试不同的字节序和字序 | Test different byte and word orders
            print(
                "\n7. 测试不同的字节序和字序 | Testing different byte and word orders..."
            )
            test_value = 3.14159

            # Big endian, high word first (默认) | Big endian, high word first (default)
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
                f"   Big/High: 写入 {test_value}, 读取 {read_val1} | Written {test_value}, Read {read_val1}"
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
                f"   Little/Low: 写入 {test_value}, 读取 {read_val2} | Written {test_value}, Read {read_val2}"
            )

        except Exception as e:
            print(f"高级操作失败 | Advanced operation failed: {e}")


async def callback_example():
    """回调机制示例 | Callback mechanism example"""
    print("\n=== 异步RTU回调机制示例 | Async RTU Callback Mechanism Example ===")

    # 定义回调函数 | Define callback functions
    def on_register_read(registers):
        print(
            f"   [回调] 读取到寄存器值 | [Callback] Read register values: {registers}"
        )

    def on_register_write():
        print("   [回调] 寄存器写入完成 | [Callback] Register write completed")

    def on_float_read(value):
        print(f"   [回调] 读取到浮点数 | [Callback] Read float value: {value}")

    transport = AsyncRtuTransport(
        port="COM1",
        baudrate=9600,
        timeout=2.0
    )

    async with AsyncModbusClient(transport) as client:
        try:
            print("\n1. 带回调的寄存器读取 | Register read with callback...")
            registers = await client.read_holding_registers(
                slave_id=1, start_address=0, quantity=4, callback=on_register_read
            )
            print(f"   主线程收到结果 | Main thread received result: {registers}")

            print("\n2. 带回调的寄存器写入 | Register write with callback...")
            await client.write_single_register(
                slave_id=1, address=5, value=9999, callback=on_register_write
            )
            print("   主线程写入完成 | Main thread write completed")

            print("\n3. 带回调的浮点数读取 | Float read with callback...")
            float_val = await client.read_float32(
                slave_id=1, start_address=20, callback=on_float_read
            )
            print(f"   主线程收到浮点数 | Main thread received float: {float_val}")

            # 等待一下让回调函数执行完成 | Wait a bit for callbacks to complete
            await asyncio.sleep(0.1)

        except Exception as e:
            print(f"回调示例失败 | Callback example failed: {e}")


async def concurrent_operations_example():
    """并发操作示例 | Concurrent operations example"""
    print("\n=== 异步RTU并发操作示例 | Async RTU Concurrent Operations Example ===")

    transport = AsyncRtuTransport(
        port="COM1",
        baudrate=9600,
        timeout=2.0
    )

    async with AsyncModbusClient(transport) as client:
        try:
            print(
                "\n并发执行多个读取操作 | Executing multiple read operations concurrently..."
            )

            # 创建多个并发任务 | Create multiple concurrent tasks
            tasks = [
                client.read_holding_registers(slave_id=1, start_address=0, quantity=2),
                client.read_holding_registers(slave_id=1, start_address=10, quantity=2),
                client.read_holding_registers(slave_id=1, start_address=20, quantity=2),
                client.read_coils(slave_id=1, start_address=0, quantity=8),
                client.read_input_registers(slave_id=1, start_address=0, quantity=4),
            ]

            # 并发执行所有任务 | Execute all tasks concurrently
            start_time = asyncio.get_event_loop().time()
            results = await asyncio.gather(*tasks)
            end_time = asyncio.get_event_loop().time()

            print(
                f"   并发执行耗时 | Concurrent execution time: {end_time - start_time:.3f}秒"
            )
            print(f"   保持寄存器0-1 | Holding registers 0-1: {results[0]}")
            print(f"   保持寄存器10-11 | Holding registers 10-11: {results[1]}")
            print(f"   保持寄存器20-21 | Holding registers 20-21: {results[2]}")
            print(f"   线圈0-7 | Coils 0-7: {results[3]}")
            print(f"   输入寄存器0-3 | Input registers 0-3: {results[4]}")

        except Exception as e:
            print(f"并发操作失败 | Concurrent operation failed: {e}")


async def sensor_monitoring_example():
    """异步传感器监控示例 | Async sensor monitoring example"""
    print("\n=== 异步RTU传感器监控示例 | Async RTU Sensor Monitoring Example ===")

    transport = AsyncRtuTransport(
        port="COM1",
        baudrate=9600,
        timeout=2.0
    )

    async with AsyncModbusClient(transport) as client:
        try:
            print("异步连续监控传感器数据... | Async continuously monitoring sensor data...")
            
            # 创建监控任务 | Create monitoring tasks
            async def monitor_temperature():
                for i in range(3):
                    temp = await client.read_float32(slave_id=1, start_address=100)
                    print(f"   [温度监控] 第{i+1}次 | [Temperature Monitor] #{i+1}: {temp:.1f}°C")
                    await asyncio.sleep(1)

            async def monitor_pressure():
                for i in range(3):
                    pressure_raw = await client.read_holding_registers(slave_id=1, start_address=104, quantity=1)
                    pressure = pressure_raw[0] / 10.0
                    print(f"   [压力监控] 第{i+1}次 | [Pressure Monitor] #{i+1}: {pressure:.1f}bar")
                    await asyncio.sleep(1.5)

            async def monitor_status():
                for i in range(3):
                    status = await client.read_coils(slave_id=1, start_address=0, quantity=1)
                    print(f"   [状态监控] 第{i+1}次 | [Status Monitor] #{i+1}: {'运行' if status[0] else '停止'}")
                    await asyncio.sleep(2)

            # 并发执行所有监控任务 | Execute all monitoring tasks concurrently
            await asyncio.gather(
                monitor_temperature(),
                monitor_pressure(),
                monitor_status()
            )

        except Exception as e:
            print(f"异步传感器监控失败 | Async sensor monitoring failed: {e}")


async def main():
    """主函数 | Main function"""
    print("ModbusLink 异步RTU客户端示例 | ModbusLink Async RTU Client Example")
    print("=" * 60)

    print("\n注意：此示例需要一个连接到串口的Modbus RTU设备")
    print("Note: This example requires a Modbus RTU device connected to serial port")
    print("\n异步RTU的优势 | Async RTU Advantages:")
    print("  - 非阻塞I/O操作 | Non-blocking I/O operations")
    print("  - 支持并发通信 | Supports concurrent communication")
    print("  - 高效的资源利用 | Efficient resource utilization")
    print("  - 适合高频率数据采集 | Suitable for high-frequency data acquisition")
    print("\n请修改串口参数以匹配您的设备：")
    print("Please modify serial port parameters to match your device:")
    print("  - port: COM1 (Windows) 或 /dev/ttyUSB0 (Linux)")
    print("  - baudrate: 9600")
    print("  - slave_id: 1")

    try:
        # 依次执行各个示例 | Execute examples sequentially
        await basic_operations_example()
        await advanced_data_types_example()
        await callback_example()
        await concurrent_operations_example()
        await sensor_monitoring_example()

        print("\n=== 所有示例执行完成 | All Examples Completed ===")

    except KeyboardInterrupt:
        print("\n用户中断 | User interrupted")
    except ConnectionError as e:
        print(f"\n❌ 连接错误 | Connection error: {e}")
        print("请检查 | Please check:")
        print("  - 串口是否存在且可用 | Serial port exists and is available")
        print("  - 串口是否被其他程序占用 | Serial port is not occupied by other programs")
        print("  - 串口参数是否正确 | Serial port parameters are correct")
    except TimeoutError as e:
        print(f"\n❌ 超时错误 | Timeout error: {e}")
        print("请检查 | Please check:")
        print("  - Modbus设备是否已连接并正常工作 | Modbus device is connected and working properly")
        print("  - 串口线缆是否正常 | Serial cable is working properly")
        print("  - 波特率等参数是否与设备匹配 | Baud rate and other parameters match the device")
    except CRCError as e:
        print(f"\n❌ CRC校验错误 | CRC verification error: {e}")
        print("请检查 | Please check:")
        print("  - 串口线缆是否有干扰 | Serial cable has interference")
        print("  - 波特率是否正确 | Baud rate is correct")
        print("  - 设备是否支持Modbus RTU协议 | Device supports Modbus RTU protocol")
    except ModbusException as e:
        print(f"\n❌ Modbus协议异常 | Modbus protocol exception: {e}")
        print("请检查 | Please check:")
        print("  - 从站地址是否正确 | Slave address is correct")
        print("  - 寄存器地址是否有效 | Register address is valid")
        print("  - 设备是否支持请求的功能码 | Device supports the requested function code")
    except Exception as e:
        print(f"\n❌ 未知错误 | Unknown error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # 运行异步主函数 | Run async main function
    asyncio.run(main())