#!/usr/bin/env python3
"""ModbusLink 异步TCP客户端示例


ModbusLink Async TCP Client Example

演示如何使用异步TCP传输层和异步客户端进行Modbus通信，
包括基本的读写操作、高级数据类型操作和回调机制。


Demonstrates how to use async TCP transport and async client for Modbus communication,
including basic read/write operations, advanced data type operations and callback mechanisms.
"""

import asyncio
import logging
from modbuslink import AsyncModbusClient, AsyncTcpTransport

# 配置日志 | Configure logging
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


async def basic_operations_example():
    """基本操作示例 | Basic operations example"""
    print("\n=== 异步基本操作示例 | Async Basic Operations Example ===")

    # 创建异步TCP传输层 | Create async TCP transport
    transport = AsyncTcpTransport(host="127.0.0.1", port=502, timeout=5.0)

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
    print("\n=== 异步高级数据类型示例 | Async Advanced Data Types Example ===")

    transport = AsyncTcpTransport(host="127.0.0.1", port=502, timeout=5.0)

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

            # 测试不同的字节序和字序 | Test different byte and word orders
            print(
                "\n5. 测试不同的字节序和字序 | Testing different byte and word orders..."
            )
            test_value = 3.14159

            # Big endian, high word first (默认) | Big endian, high word first (default)
            await client.write_float32(
                slave_id=1,
                start_address=30,
                value=test_value,
                byte_order="big",
                word_order="high",
            )
            read_val1 = await client.read_float32(
                slave_id=1, start_address=30, byte_order="big", word_order="high"
            )
            print(
                f"   Big/High: 写入 {test_value}, 读取 {read_val1} | Written {test_value}, Read {read_val1}"
            )

            # Little endian, low word first
            await client.write_float32(
                slave_id=1,
                start_address=32,
                value=test_value,
                byte_order="little",
                word_order="low",
            )
            read_val2 = await client.read_float32(
                slave_id=1, start_address=32, byte_order="little", word_order="low"
            )
            print(
                f"   Little/Low: 写入 {test_value}, 读取 {read_val2} | Written {test_value}, Read {read_val2}"
            )

        except Exception as e:
            print(f"高级操作失败 | Advanced operation failed: {e}")


async def callback_example():
    """回调机制示例 | Callback mechanism example"""
    print("\n=== 异步回调机制示例 | Async Callback Mechanism Example ===")

    # 定义回调函数 | Define callback functions
    def on_register_read(registers):
        print(
            f"   [回调] 读取到寄存器值 | [Callback] Read register values: {registers}"
        )

    def on_register_write():
        print("   [回调] 寄存器写入完成 | [Callback] Register write completed")

    def on_float_read(value):
        print(f"   [回调] 读取到浮点数 | [Callback] Read float value: {value}")

    transport = AsyncTcpTransport(host="127.0.0.1", port=502, timeout=5.0)

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
    print("\n=== 异步并发操作示例 | Async Concurrent Operations Example ===")

    transport = AsyncTcpTransport(host="127.0.0.1", port=502, timeout=5.0)

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


async def main():
    """主函数 | Main function"""
    print("ModbusLink 异步TCP客户端示例 | ModbusLink Async TCP Client Example")
    print("=" * 60)

    print("\n注意：此示例需要一个运行在127.0.0.1:502的Modbus TCP服务器")
    print("Note: This example requires a Modbus TCP server running on 127.0.0.1:502")
    print("\n你可以使用ModbusLink的从站模拟器：")
    print("You can use ModbusLink's slave simulator:")
    print("\n  from modbuslink import ModbusSlave")
    print("  slave = ModbusSlave(slave_id=1)")
    print("  slave.start_tcp_server('127.0.0.1', 502)")

    try:
        # 依次执行各个示例 | Execute examples sequentially
        await basic_operations_example()
        await advanced_data_types_example()
        await callback_example()
        await concurrent_operations_example()

        print("\n=== 所有示例执行完成 | All Examples Completed ===")

    except KeyboardInterrupt:
        print("\n用户中断 | User interrupted")
    except Exception as e:
        print(f"\n示例执行失败 | Example execution failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    # 运行异步主函数 | Run async main function
    asyncio.run(main())
