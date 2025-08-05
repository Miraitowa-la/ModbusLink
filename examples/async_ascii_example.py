"""
ModbusLink 异步ASCII客户端示例
演示如何使用异步ASCII传输层进行Modbus通信，
包括基本的读写操作、高级数据类型操作、调试功能和错误处理。

ModbusLink Async ASCII Client Example
Demonstrates how to use async ASCII transport for Modbus communication,
including basic read/write operations, advanced data type operations, debugging features and error handling.
"""

import asyncio
import logging
from modbuslink import (
    AsyncModbusClient,
    AsyncAsciiTransport,
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
    print("\n=== 异步ASCII基本操作示例 | Async ASCII Basic Operations Example ===")

    # 创建异步ASCII传输层 | Create async ASCII transport
    transport = AsyncAsciiTransport(
        port="COM1",  # Windows: COM1, Linux: /dev/ttyUSB0
        baudrate=9600,
        timeout=3.0
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

            # 输入寄存器和离散输入 | Input registers and discrete inputs
            print("\n7. 读取输入寄存器 | Reading input registers...")
            input_regs = await client.read_input_registers(
                slave_id=1, start_address=0, quantity=4
            )
            print(f"   输入寄存器值 | Input register values: {input_regs}")

            print("\n8. 读取离散输入 | Reading discrete inputs...")
            discrete_inputs = await client.read_discrete_inputs(
                slave_id=1, start_address=0, quantity=8
            )
            print(f"   离散输入状态 | Discrete input status: {discrete_inputs}")

        except Exception as e:
            print(f"操作失败 | Operation failed: {e}")


async def advanced_data_types_example():
    """高级数据类型示例 | Advanced data types example"""
    print("\n=== 异步ASCII高级数据类型示例 | Async ASCII Advanced Data Types Example ===")

    transport = AsyncAsciiTransport(
        port="COM1",
        baudrate=9600,
        timeout=3.0
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

            # 写入32位无符号整数 | Write 32-bit unsigned integer
            print("\n5. 写入32位无符号整数 | Writing 32-bit unsigned integer...")
            counter = 65535  # 适合ASCII传输的较小值 | Smaller value suitable for ASCII transport
            await client.write_uint32(slave_id=1, start_address=24, value=counter)
            print(f"   写入计数器值 | Written counter value: {counter}")

            # 读取32位无符号整数 | Read 32-bit unsigned integer
            print("\n6. 读取32位无符号整数 | Reading 32-bit unsigned integer...")
            read_counter = await client.read_uint32(slave_id=1, start_address=24)
            print(f"   读取计数器值 | Read counter value: {read_counter}")

            # 写入字符串 | Write string
            print("\n7. 写入字符串 | Writing string...")
            device_name = "AsyncASCII_Dev"
            await client.write_string(slave_id=1, start_address=30, value=device_name)
            print(f"   写入设备名称 | Written device name: '{device_name}'")

            # 读取字符串 | Read string
            print("\n8. 读取字符串 | Reading string...")
            read_name = await client.read_string(
                slave_id=1,
                start_address=30,
                length=len(device_name.encode("utf-8")),
            )
            print(f"   读取设备名称 | Read device name: '{read_name}'")

            # 测试不同的字节序和字序 | Test different byte and word orders
            print(
                "\n9. 测试不同的字节序和字序 | Testing different byte and word orders..."
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


async def debugging_example():
    """调试功能示例 | Debugging features example"""
    print("\n=== 异步ASCII调试功能示例 | Async ASCII Debugging Features Example ===")

    # 启用调试模式的传输层 | Transport with debugging enabled
    transport = AsyncAsciiTransport(
        port="COM1",
        baudrate=9600,
        timeout=3.0
    )

    async with AsyncModbusClient(transport) as client:
        try:
            print("\n1. ASCII协议特性演示 | ASCII protocol features demonstration...")
            print("   ASCII协议使用可读的十六进制字符 | ASCII protocol uses readable hexadecimal characters")
            print("   每个字节用两个ASCII字符表示 | Each byte is represented by two ASCII characters")
            print("   使用LRC校验而非CRC校验 | Uses LRC checksum instead of CRC")

            # 演示ASCII帧格式 | Demonstrate ASCII frame format
            print("\n2. ASCII帧格式示例 | ASCII frame format example:")
            print("   起始字符: ':' (0x3A) | Start character: ':' (0x3A)")
            print("   从站地址: 01 (ASCII) | Slave address: 01 (ASCII)")
            print("   功能码: 03 (ASCII) | Function code: 03 (ASCII)")
            print("   数据: 0000 0004 (ASCII) | Data: 0000 0004 (ASCII)")
            print("   LRC校验: F8 (ASCII) | LRC checksum: F8 (ASCII)")
            print("   结束字符: CR LF (0x0D 0x0A) | End characters: CR LF (0x0D 0x0A)")

            # 执行实际操作以观察ASCII通信 | Perform actual operations to observe ASCII communication
            print("\n3. 执行读取操作以观察ASCII通信 | Performing read operation to observe ASCII communication...")
            registers = await client.read_holding_registers(
                slave_id=1, start_address=0, quantity=4
            )
            print(f"   读取结果 | Read result: {registers}")

            print("\n4. 执行写入操作以观察ASCII通信 | Performing write operation to observe ASCII communication...")
            await client.write_single_register(slave_id=1, address=0, value=0x1234)
            print("   写入完成 | Write completed")

            # ASCII协议的优势和劣势 | ASCII protocol advantages and disadvantages
            print("\n5. ASCII协议特点分析 | ASCII protocol characteristics analysis:")
            print("   优势 | Advantages:")
            print("     - 可读性强，便于调试 | High readability, easy to debug")
            print("     - 兼容性好 | Good compatibility")
            print("     - 错误检测容易 | Easy error detection")
            print("   劣势 | Disadvantages:")
            print("     - 传输效率低 | Low transmission efficiency")
            print("     - 占用带宽大 | High bandwidth usage")
            print("     - 处理速度慢 | Slow processing speed")

        except Exception as e:
            print(f"调试示例失败 | Debugging example failed: {e}")


async def error_handling_example():
    """错误处理示例 | Error handling example"""
    print("\n=== 异步ASCII错误处理示例 | Async ASCII Error Handling Example ===")

    transport = AsyncAsciiTransport(
        port="COM1",
        baudrate=9600,
        timeout=3.0
    )

    async with AsyncModbusClient(transport) as client:
        try:
            print("\n1. 测试超时处理 | Testing timeout handling...")
            try:
                # 尝试读取可能不存在的寄存器 | Try to read potentially non-existent registers
                registers = await client.read_holding_registers(
                    slave_id=99, start_address=0, quantity=1  # 使用不存在的从站ID | Use non-existent slave ID
                )
                print(f"   意外成功 | Unexpected success: {registers}")
            except TimeoutError as e:
                print(f"   ✓ 超时错误正确捕获 | Timeout error correctly caught: {e}")

            print("\n2. 测试LRC校验错误处理 | Testing LRC checksum error handling...")
            # 注意：LRC错误通常由传输层自动处理 | Note: LRC errors are usually handled automatically by transport layer
            print("   LRC校验在传输层自动处理 | LRC checksum is automatically handled at transport layer")

            print("\n3. 测试Modbus异常处理 | Testing Modbus exception handling...")
            try:
                # 尝试读取无效的寄存器地址 | Try to read invalid register address
                registers = await client.read_holding_registers(
                    slave_id=1, start_address=65535, quantity=1  # 无效地址 | Invalid address
                )
                print(f"   意外成功 | Unexpected success: {registers}")
            except ModbusException as e:
                print(f"   ✓ Modbus异常正确捕获 | Modbus exception correctly caught: {e}")

            print("\n4. 测试连接错误处理 | Testing connection error handling...")
            # 这个测试在实际设备连接时可能不会触发 | This test may not trigger when actual device is connected
            print("   连接错误通常在传输层初始化时发生 | Connection errors usually occur during transport initialization")

            print("\n5. 错误恢复策略 | Error recovery strategies:")
            print("   - 自动重试机制 | Automatic retry mechanism")
            print("   - 连接状态监控 | Connection status monitoring")
            print("   - 优雅降级处理 | Graceful degradation handling")
            print("   - 详细错误日志 | Detailed error logging")

        except Exception as e:
            print(f"错误处理示例失败 | Error handling example failed: {e}")


async def performance_comparison_example():
    """性能对比示例 | Performance comparison example"""
    print("\n=== 异步ASCII性能对比示例 | Async ASCII Performance Comparison Example ===")

    transport = AsyncAsciiTransport(
        port="COM1",
        baudrate=9600,
        timeout=3.0
    )

    async with AsyncModbusClient(transport) as client:
        try:
            print("\n1. 单次操作性能测试 | Single operation performance test...")
            
            # 测试读取操作性能 | Test read operation performance
            start_time = asyncio.get_event_loop().time()
            registers = await client.read_holding_registers(
                slave_id=1, start_address=0, quantity=10
            )
            end_time = asyncio.get_event_loop().time()
            read_time = end_time - start_time
            print(f"   读取10个寄存器耗时 | Read 10 registers time: {read_time:.3f}秒")

            # 测试写入操作性能 | Test write operation performance
            start_time = asyncio.get_event_loop().time()
            await client.write_multiple_registers(
                slave_id=1, start_address=10, values=[i for i in range(10)]
            )
            end_time = asyncio.get_event_loop().time()
            write_time = end_time - start_time
            print(f"   写入10个寄存器耗时 | Write 10 registers time: {write_time:.3f}秒")

            print("\n2. 批量操作性能测试 | Batch operation performance test...")
            
            # 批量读取测试 | Batch read test
            start_time = asyncio.get_event_loop().time()
            tasks = [
                client.read_holding_registers(slave_id=1, start_address=i*10, quantity=5)
                for i in range(5)
            ]
            results = await asyncio.gather(*tasks)
            end_time = asyncio.get_event_loop().time()
            batch_time = end_time - start_time
            print(f"   并发读取5组寄存器耗时 | Concurrent read 5 groups time: {batch_time:.3f}秒")
            print(f"   平均每组耗时 | Average time per group: {batch_time/5:.3f}秒")

            print("\n3. ASCII vs RTU 性能对比分析 | ASCII vs RTU performance comparison analysis:")
            print("   ASCII协议特点 | ASCII protocol characteristics:")
            print(f"     - 单次读取耗时: ~{read_time:.3f}秒 | Single read time: ~{read_time:.3f}s")
            print(f"     - 单次写入耗时: ~{write_time:.3f}秒 | Single write time: ~{write_time:.3f}s")
            print("     - 数据量是RTU的2倍 | Data volume is 2x of RTU")
            print("     - 传输速度较慢 | Slower transmission speed")
            print("     - 调试友好 | Debug-friendly")
            
            print("\n   建议使用场景 | Recommended use cases:")
            print("     - 调试和开发阶段 | Debugging and development phase")
            print("     - 低速串口通信 | Low-speed serial communication")
            print("     - 需要人工监控的场合 | Scenarios requiring manual monitoring")
            print("     - 兼容老旧设备 | Compatibility with legacy devices")

        except Exception as e:
            print(f"性能对比示例失败 | Performance comparison example failed: {e}")


async def sensor_monitoring_example():
    """异步传感器监控示例 | Async sensor monitoring example"""
    print("\n=== 异步ASCII传感器监控示例 | Async ASCII Sensor Monitoring Example ===")

    transport = AsyncAsciiTransport(
        port="COM1",
        baudrate=9600,
        timeout=3.0
    )

    async with AsyncModbusClient(transport) as client:
        try:
            print("异步连续监控传感器数据... | Async continuously monitoring sensor data...")
            
            # 创建监控任务 | Create monitoring tasks
            async def monitor_temperature():
                """监控温度传感器 | Monitor temperature sensor"""
                for i in range(3):
                    temp = await client.read_float32(slave_id=1, start_address=100)
                    status = "正常" if 0 <= temp <= 100 else "异常"
                    print(f"   [温度监控] 第{i+1}次 | [Temperature Monitor] #{i+1}: {temp:.1f}°C ({status})")
                    await asyncio.sleep(2)  # ASCII较慢，增加间隔 | ASCII is slower, increase interval

            async def monitor_humidity():
                """监控湿度传感器 | Monitor humidity sensor"""
                for i in range(3):
                    humidity_raw = await client.read_holding_registers(slave_id=1, start_address=102, quantity=1)
                    humidity = humidity_raw[0] / 10.0
                    status = "正常" if 0 <= humidity <= 100 else "异常"
                    print(f"   [湿度监控] 第{i+1}次 | [Humidity Monitor] #{i+1}: {humidity:.1f}% ({status})")
                    await asyncio.sleep(2.5)

            async def monitor_status():
                """监控设备状态 | Monitor device status"""
                for i in range(3):
                    status = await client.read_coils(slave_id=1, start_address=0, quantity=1)
                    print(f"   [状态监控] 第{i+1}次 | [Status Monitor] #{i+1}: {'运行' if status[0] else '停止'}")
                    await asyncio.sleep(3)

            # 并发执行所有监控任务 | Execute all monitoring tasks concurrently
            await asyncio.gather(
                monitor_temperature(),
                monitor_humidity(),
                monitor_status()
            )

        except Exception as e:
            print(f"异步传感器监控失败 | Async sensor monitoring failed: {e}")


async def main():
    """主函数 | Main function"""
    print("ModbusLink 异步ASCII客户端示例 | ModbusLink Async ASCII Client Example")
    print("=" * 60)

    print("\n注意：此示例需要一个连接到串口的Modbus ASCII设备")
    print("Note: This example requires a Modbus ASCII device connected to serial port")
    print("\n异步ASCII的特点 | Async ASCII Characteristics:")
    print("  - 非阻塞串口I/O | Non-blocking serial I/O")
    print("  - 可读的ASCII格式 | Readable ASCII format")
    print("  - 便于调试和监控 | Easy to debug and monitor")
    print("  - 兼容性强 | Strong compatibility")
    print("  - 传输效率较低 | Lower transmission efficiency")
    print("\n配置说明 | Configuration notes:")
    print("  - ASCII协议通常使用较低的波特率 | ASCII protocol typically uses lower baud rates")
    print("  - 建议波特率: 1200, 2400, 4800, 9600 | Recommended baud rates: 1200, 2400, 4800, 9600")
    print("  - 数据位: 7或8位 | Data bits: 7 or 8 bits")
    print("  - 校验位: 偶校验、奇校验或无校验 | Parity: even, odd, or none")
    print("  - 停止位: 1或2位 | Stop bits: 1 or 2 bits")
    print("\n请修改串口参数以匹配您的设备：")
    print("Please modify serial port parameters to match your device:")
    print("  - port: COM1 (Windows) 或 /dev/ttyUSB0 (Linux)")
    print("  - baudrate: 9600")
    print("  - slave_id: 1")

    try:
        # 依次执行各个示例 | Execute examples sequentially
        await basic_operations_example()
        await advanced_data_types_example()
        await debugging_example()
        await error_handling_example()
        await performance_comparison_example()
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
        print("  - 设备是否支持ASCII模式 | Device supports ASCII mode")
    except TimeoutError as e:
        print(f"\n❌ 超时错误 | Timeout error: {e}")
        print("请检查 | Please check:")
        print("  - Modbus设备是否已连接并正常工作 | Modbus device is connected and working properly")
        print("  - 串口线缆是否正常 | Serial cable is working properly")
        print("  - 波特率等参数是否与设备匹配 | Baud rate and other parameters match the device")
        print("  - 设备是否配置为ASCII模式 | Device is configured for ASCII mode")
    except CRCError as e:
        print(f"\n❌ CRC校验错误 | CRC verification error: {e}")
        print("请检查 | Please check:")
        print("  - 串口线缆是否有干扰 | Serial cable has interference")
        print("  - 波特率是否正确 | Baud rate is correct")
        print("  - 设备是否支持Modbus ASCII协议 | Device supports Modbus ASCII protocol")
        print("  - 数据位、校验位、停止位设置 | Data bits, parity, stop bits settings")
    except ModbusException as e:
        print(f"\n❌ Modbus协议异常 | Modbus protocol exception: {e}")
        print("请检查 | Please check:")
        print("  - 从站地址是否正确 | Slave address is correct")
        print("  - 寄存器地址是否有效 | Register address is valid")
        print("  - 设备是否支持请求的功能码 | Device supports the requested function code")
        print("  - 设备是否处于ASCII模式 | Device is in ASCII mode")
    except Exception as e:
        print(f"\n❌ 未知错误 | Unknown error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # 运行异步主函数 | Run async main function
    asyncio.run(main())