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
from modbuslink import (
    AsyncModbusClient,
    AsyncTcpTransport,
    ConnectionError,
    TimeoutError,
    ModbusException,
)

# 配置日志 | Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


async def basic_operations_example():
    """基本操作示例 | Basic operations example"""
    print("\n=== 异步TCP基本操作示例 | Async TCP Basic Operations Example ===")

    # 创建异步TCP传输层 | Create async TCP transport
    transport = AsyncTcpTransport(
        host="127.0.0.1",  # Modbus TCP服务器地址 | Modbus TCP server address
        port=502,          # 标准Modbus TCP端口 | Standard Modbus TCP port
        timeout=5.0
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
    print("\n=== 异步TCP高级数据类型示例 | Async TCP Advanced Data Types Example ===")

    transport = AsyncTcpTransport(
        host="127.0.0.1",
        port=502,
        timeout=5.0
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

            # 写入64位浮点数 | Write 64-bit float
            print("\n3. 写入64位浮点数 | Writing 64-bit float...")
            precision_value = 3.141592653589793
            await client.write_float64(slave_id=1, start_address=24, value=precision_value)
            print(f"   写入高精度值 | Written precision value: {precision_value}")

            # 读取64位浮点数 | Read 64-bit float
            print("\n4. 读取64位浮点数 | Reading 64-bit float...")
            read_precision = await client.read_float64(slave_id=1, start_address=24)
            print(f"   读取高精度值 | Read precision value: {read_precision}")

            # 写入32位有符号整数 | Write 32-bit signed integer
            print("\n5. 写入32位有符号整数 | Writing 32-bit signed integer...")
            pressure = -12345
            await client.write_int32(slave_id=1, start_address=28, value=pressure)
            print(f"   写入压力值 | Written pressure: {pressure}")

            # 读取32位有符号整数 | Read 32-bit signed integer
            print("\n6. 读取32位有符号整数 | Reading 32-bit signed integer...")
            read_pressure = await client.read_int32(slave_id=1, start_address=28)
            print(f"   读取压力值 | Read pressure: {read_pressure}")

            # 写入32位无符号整数 | Write 32-bit unsigned integer
            print("\n7. 写入32位无符号整数 | Writing 32-bit unsigned integer...")
            counter = 4294967295  # 最大32位无符号整数 | Maximum 32-bit unsigned integer
            await client.write_uint32(slave_id=1, start_address=30, value=counter)
            print(f"   写入计数器值 | Written counter value: {counter}")

            # 读取32位无符号整数 | Read 32-bit unsigned integer
            print("\n8. 读取32位无符号整数 | Reading 32-bit unsigned integer...")
            read_counter = await client.read_uint32(slave_id=1, start_address=30)
            print(f"   读取计数器值 | Read counter value: {read_counter}")

            # 写入字符串 | Write string
            print("\n9. 写入字符串 | Writing string...")
            device_name = "AsyncTCP_Device_2024"
            await client.write_string(slave_id=1, start_address=40, value=device_name)
            print(f"   写入设备名称 | Written device name: '{device_name}'")

            # 读取字符串 | Read string
            print("\n10. 读取字符串 | Reading string...")
            read_name = await client.read_string(
                slave_id=1,
                start_address=40,
                length=len(device_name.encode("utf-8")),
            )
            print(f"   读取设备名称 | Read device name: '{read_name}'")

            # 测试不同的字节序和字序 | Test different byte and word orders
            print(
                "\n11. 测试不同的字节序和字序 | Testing different byte and word orders..."
            )
            test_value = 3.14159

            # Big endian, high word first (默认) | Big endian, high word first (default)
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
                f"   Big/High: 写入 {test_value}, 读取 {read_val1} | Written {test_value}, Read {read_val1}"
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
                f"   Little/Low: 写入 {test_value}, 读取 {read_val2} | Written {test_value}, Read {read_val2}"
            )

        except Exception as e:
            print(f"高级操作失败 | Advanced operation failed: {e}")


async def callback_example():
    """回调机制示例 | Callback mechanism example"""
    print("\n=== 异步TCP回调机制示例 | Async TCP Callback Mechanism Example ===")

    # 定义回调函数 | Define callback functions
    def on_register_read(registers):
        print(
            f"   [回调] 读取到寄存器值 | [Callback] Read register values: {registers}"
        )

    def on_register_write():
        print("   [回调] 寄存器写入完成 | [Callback] Register write completed")

    def on_float_read(value):
        print(f"   [回调] 读取到浮点数 | [Callback] Read float value: {value}")

    def on_coil_operation(result):
        print(f"   [回调] 线圈操作结果 | [Callback] Coil operation result: {result}")

    transport = AsyncTcpTransport(
        host="127.0.0.1",
        port=502,
        timeout=5.0
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

            print("\n4. 带回调的线圈操作 | Coil operation with callback...")
            coils = await client.read_coils(
                slave_id=1, start_address=0, quantity=8, callback=on_coil_operation
            )
            print(f"   主线程收到线圈状态 | Main thread received coil status: {coils}")

            # 等待一下让回调函数执行完成 | Wait a bit for callbacks to complete
            await asyncio.sleep(0.1)

        except Exception as e:
            print(f"回调示例失败 | Callback example failed: {e}")


async def concurrent_operations_example():
    """并发操作示例 | Concurrent operations example"""
    print("\n=== 异步TCP并发操作示例 | Async TCP Concurrent Operations Example ===")

    transport = AsyncTcpTransport(
        host="127.0.0.1",
        port=502,
        timeout=5.0
    )

    async with AsyncModbusClient(transport) as client:
        try:
            print(
                "\n并发执行多个读取操作 | Executing multiple read operations concurrently..."
            )

            # 创建多个并发任务 | Create multiple concurrent tasks
            tasks = [
                client.read_holding_registers(slave_id=1, start_address=0, quantity=4),
                client.read_holding_registers(slave_id=1, start_address=10, quantity=4),
                client.read_holding_registers(slave_id=1, start_address=20, quantity=4),
                client.read_coils(slave_id=1, start_address=0, quantity=16),
                client.read_input_registers(slave_id=1, start_address=0, quantity=8),
                client.read_discrete_inputs(slave_id=1, start_address=0, quantity=16),
            ]

            # 并发执行所有任务 | Execute all tasks concurrently
            start_time = asyncio.get_event_loop().time()
            results = await asyncio.gather(*tasks)
            end_time = asyncio.get_event_loop().time()

            print(
                f"   并发执行耗时 | Concurrent execution time: {end_time - start_time:.3f}秒"
            )
            print(f"   保持寄存器0-3 | Holding registers 0-3: {results[0]}")
            print(f"   保持寄存器10-13 | Holding registers 10-13: {results[1]}")
            print(f"   保持寄存器20-23 | Holding registers 20-23: {results[2]}")
            print(f"   线圈0-15 | Coils 0-15: {results[3]}")
            print(f"   输入寄存器0-7 | Input registers 0-7: {results[4]}")
            print(f"   离散输入0-15 | Discrete inputs 0-15: {results[5]}")

            print(
                "\n并发执行混合读写操作 | Executing mixed read/write operations concurrently..."
            )

            # 创建混合读写任务 | Create mixed read/write tasks
            mixed_tasks = [
                client.write_single_register(slave_id=1, address=100, value=1001),
                client.write_single_register(slave_id=1, address=101, value=1002),
                client.write_single_register(slave_id=1, address=102, value=1003),
                client.read_holding_registers(slave_id=1, start_address=100, quantity=3),
            ]

            # 并发执行混合任务 | Execute mixed tasks concurrently
            start_time = asyncio.get_event_loop().time()
            mixed_results = await asyncio.gather(*mixed_tasks)
            end_time = asyncio.get_event_loop().time()

            print(
                f"   混合操作耗时 | Mixed operations time: {end_time - start_time:.3f}秒"
            )
            print(f"   读取结果 | Read result: {mixed_results[3]}")

        except Exception as e:
            print(f"并发操作失败 | Concurrent operation failed: {e}")


async def industrial_monitoring_example():
    """异步工业监控示例 | Async industrial monitoring example"""
    print("\n=== 异步TCP工业监控示例 | Async TCP Industrial Monitoring Example ===")

    transport = AsyncTcpTransport(
        host="127.0.0.1",
        port=502,
        timeout=5.0
    )

    async with AsyncModbusClient(transport) as client:
        try:
            print("异步连续监控工业设备数据... | Async continuously monitoring industrial equipment data...")
            
            # 创建监控任务 | Create monitoring tasks
            async def monitor_temperature():
                """监控温度传感器 | Monitor temperature sensor"""
                for i in range(5):
                    temp = await client.read_float32(slave_id=1, start_address=100)
                    status = "正常" if 0 <= temp <= 100 else "异常"
                    print(f"   [温度监控] 第{i+1}次 | [Temperature Monitor] #{i+1}: {temp:.1f}°C ({status})")
                    await asyncio.sleep(1)

            async def monitor_pressure():
                """监控压力传感器 | Monitor pressure sensor"""
                for i in range(5):
                    pressure_raw = await client.read_holding_registers(slave_id=1, start_address=104, quantity=1)
                    pressure = pressure_raw[0] / 10.0
                    status = "正常" if 0 <= pressure <= 10 else "异常"
                    print(f"   [压力监控] 第{i+1}次 | [Pressure Monitor] #{i+1}: {pressure:.1f}bar ({status})")
                    await asyncio.sleep(1.2)

            async def monitor_motor_status():
                """监控电机状态 | Monitor motor status"""
                for i in range(5):
                    status_bits = await client.read_coils(slave_id=1, start_address=0, quantity=8)
                    motor_running = status_bits[0]
                    motor_fault = status_bits[1]
                    emergency_stop = status_bits[2]
                    
                    status_text = []
                    if motor_running:
                        status_text.append("运行中")
                    if motor_fault:
                        status_text.append("故障")
                    if emergency_stop:
                        status_text.append("急停")
                    
                    status_str = ", ".join(status_text) if status_text else "停止"
                    print(f"   [电机监控] 第{i+1}次 | [Motor Monitor] #{i+1}: {status_str}")
                    await asyncio.sleep(1.5)

            async def monitor_production_counter():
                """监控生产计数器 | Monitor production counter"""
                for i in range(5):
                    counter = await client.read_uint32(slave_id=1, start_address=200)
                    print(f"   [生产计数] 第{i+1}次 | [Production Counter] #{i+1}: {counter}件")
                    await asyncio.sleep(2)

            async def control_system_heartbeat():
                """控制系统心跳 | Control system heartbeat"""
                for i in range(5):
                    # 写入心跳信号 | Write heartbeat signal
                    await client.write_single_register(slave_id=1, address=999, value=i+1)
                    print(f"   [系统心跳] 第{i+1}次 | [System Heartbeat] #{i+1}: 心跳信号已发送")
                    await asyncio.sleep(1.8)

            # 并发执行所有监控任务 | Execute all monitoring tasks concurrently
            await asyncio.gather(
                monitor_temperature(),
                monitor_pressure(),
                monitor_motor_status(),
                monitor_production_counter(),
                control_system_heartbeat()
            )

        except Exception as e:
            print(f"异步工业监控失败 | Async industrial monitoring failed: {e}")


async def main():
    """主函数 | Main function"""
    print("ModbusLink 异步TCP客户端示例 | ModbusLink Async TCP Client Example")
    print("=" * 60)

    print("\n注意：此示例需要一个Modbus TCP服务器")
    print("Note: This example requires a Modbus TCP server")
    print("\n异步TCP的优势 | Async TCP Advantages:")
    print("  - 非阻塞网络I/O | Non-blocking network I/O")
    print("  - 支持高并发连接 | Supports high concurrent connections")
    print("  - 优秀的网络性能 | Excellent network performance")
    print("  - 适合分布式系统 | Suitable for distributed systems")
    print("\n推荐的Modbus TCP服务器 | Recommended Modbus TCP servers:")
    print("  - ModbusPal (免费模拟器) | ModbusPal (free simulator)")
    print("  - QModMaster (开源工具) | QModMaster (open source tool)")
    print("  - 工业PLC设备 | Industrial PLC devices")
    print("\n请修改连接参数以匹配您的服务器：")
    print("Please modify connection parameters to match your server:")
    print("  - host: 127.0.0.1")
    print("  - port: 502")
    print("  - slave_id: 1")

    try:
        # 依次执行各个示例 | Execute examples sequentially
        await basic_operations_example()
        await advanced_data_types_example()
        await callback_example()
        await concurrent_operations_example()
        await industrial_monitoring_example()

        print("\n=== 所有示例执行完成 | All Examples Completed ===")

    except KeyboardInterrupt:
        print("\n用户中断 | User interrupted")
    except ConnectionError as e:
        print(f"\n❌ 连接错误 | Connection error: {e}")
        print("请检查 | Please check:")
        print("  - Modbus TCP服务器是否正在运行 | Modbus TCP server is running")
        print("  - 服务器地址和端口是否正确 | Server address and port are correct")
        print("  - 网络连接是否正常 | Network connection is working")
        print("  - 防火墙是否阻止连接 | Firewall is not blocking the connection")
    except TimeoutError as e:
        print(f"\n❌ 超时错误 | Timeout error: {e}")
        print("请检查 | Please check:")
        print("  - 网络延迟是否过高 | Network latency is too high")
        print("  - 服务器是否响应正常 | Server is responding normally")
        print("  - 超时设置是否合理 | Timeout setting is reasonable")
    except ModbusException as e:
        print(f"\n❌ Modbus协议异常 | Modbus protocol exception: {e}")
        print("请检查 | Please check:")
        print("  - 从站地址是否正确 | Slave address is correct")
        print("  - 寄存器地址是否有效 | Register address is valid")
        print("  - 服务器是否支持请求的功能码 | Server supports the requested function code")
    except Exception as e:
        print(f"\n❌ 未知错误 | Unknown error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # 运行异步主函数 | Run async main function
    asyncio.run(main())
