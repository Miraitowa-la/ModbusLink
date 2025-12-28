"""
ModbusLink 异步RTU客户端示例
演示如何使用异步RTU传输层进行Modbus通信，
包括基本的读写操作、高级数据类型操作、并发操作和回调机制。
"""

import asyncio
import logging
from time import sleep

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

set_language(Language.CN)

# 设置日志
ModbusLogger.setup_logging(
    level=logging.INFO,
    enable_debug=True
)


async def basic_operations_example():
    """基本操作示例"""
    print("\n=== 异步RTU基本操作示例 ===")

    # 创建异步RTU传输层
    transport = AsyncRtuTransport(
        port="COM10",  # Windows: COM10, Linux: /dev/ttyUSB0
        baudrate=9600,
        timeout=2.0
    )

    # 创建异步客户端
    async with AsyncModbusClient(transport) as client:
        try:
            # 读取保持寄存器
            print("\n1. 读取保持寄存器...")
            registers = await client.read_holding_registers(
                slave_id=1, start_address=0, quantity=4
            )
            print(f"   寄存器值: {registers}")

            # 写入单个寄存器
            print("\n2. 写入单个寄存器...")
            await client.write_single_register(slave_id=1, address=0, value=1234)
            print("   写入完成")

            # 验证写入结果
            print("\n3. 验证写入结果...")
            value = await client.read_holding_registers(
                slave_id=1, start_address=0, quantity=1
            )
            print(f"   寄存器0的值: {value[0]}")

            # 写入多个寄存器
            print("\n4. 写入多个寄存器...")
            values = [1111, 2222, 3333, 4444]
            await client.write_multiple_registers(
                slave_id=1, start_address=10, values=values
            )
            print(f"   写入值: {values}")

            # 读取多个寄存器
            print("\n5. 读取多个寄存器...")
            read_values = await client.read_holding_registers(
                slave_id=1, start_address=10, quantity=4
            )
            print(f"   读取值: {read_values}")

            # 线圈操作
            print("\n6. 线圈操作...")
            await client.write_single_coil(slave_id=1, address=0, value=True)
            coils = await client.read_coils(slave_id=1, start_address=0, quantity=8)
            print(f"   线圈状态: {coils}")

            # 写入多个线圈
            coil_values = [True, False, True, False, True, False, True, False]
            await client.write_multiple_coils(
                slave_id=1, start_address=0, values=coil_values
            )
            coils = await client.read_coils(slave_id=1, start_address=0, quantity=8)
            print(f"   更新后的线圈状态: {coils}")

        except Exception as e:
            print(f"操作失败: {e}")


async def advanced_data_types_example():
    """高级数据类型示例"""
    print("\n=== 异步RTU高级数据类型示例 ===")

    transport = AsyncRtuTransport(
        port="COM10",
        baudrate=9600,
        timeout=2.0
    )

    async with AsyncModbusClient(transport) as client:
        try:
            # 写入32位浮点数
            print("\n1. 写入32位浮点数...")
            temperature = 25.6
            await client.write_float32(slave_id=1, start_address=20, value=temperature)
            print(f"   写入温度值: {temperature}°C")

            # 读取32位浮点数
            print("\n2. 读取32位浮点数...")
            read_temp = await client.read_float32(slave_id=1, start_address=20)
            print(f"   读取温度值: {read_temp}°C")

            # 写入32位有符号整数
            print("\n3. 写入32位有符号整数...")
            pressure = -12345
            await client.write_int32(slave_id=1, start_address=22, value=pressure)
            print(f"   写入压力值: {pressure}")

            # 读取32位有符号整数
            print("\n4. 读取32位有符号整数...")
            read_pressure = await client.read_int32(slave_id=1, start_address=22)
            print(f"   读取压力值: {read_pressure}")

            # 写入字符串
            print("\n5. 写入字符串...")
            device_name = "AsyncRTU_Device"
            await client.write_string(slave_id=1, start_address=30, value=device_name)
            print(f"   写入设备名称: '{device_name}'")

            # 读取字符串
            print("\n6. 读取字符串...")
            read_name = await client.read_string(
                slave_id=1,
                start_address=30,
                length=len(device_name.encode("utf-8")),
            )
            print(f"   读取设备名称: '{read_name}'")

            # 测试不同的字节序和字序
            print(
                "\n7. 测试不同的字节序和字序..."
            )
            test_value = 3.14159

            # 大端序，高位字节在前 (默认)
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
                f"   Big/High: 写入 {test_value}, 读取 {read_val1}"
            )

            # 小端序，低位字节在前
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
                f"   Little/Low: 写入 {test_value}, 读取 {read_val2}"
            )

        except Exception as e:
            print(f"高级操作失败: {e}")


async def callback_example():
    """回调机制示例"""
    print("\n=== 异步RTU回调机制示例 ===")

    # 定义回调函数
    def on_register_read(registers):
        print(
            f"   [回调] 读取到寄存器值: {registers}"
        )

    def on_register_write():
        print("   [回调] 寄存器写入完成")

    def on_float_read(value):
        print(f"   [回调] 读取到浮点数: {value}")

    transport = AsyncRtuTransport(
        port="COM10",
        baudrate=9600,
        timeout=2.0
    )

    async with AsyncModbusClient(transport) as client:
        try:
            print("\n1. 带回调的寄存器读取...")
            registers = await client.read_holding_registers(
                slave_id=1, start_address=0, quantity=4, callback=on_register_read
            )
            print(f"   主线程收到结果: {registers}")

            print("\n2. 带回调的寄存器写入...")
            await client.write_single_register(
                slave_id=1, address=5, value=9999, callback=on_register_write
            )
            print("   主线程写入完成")

            print("\n3. 带回调的浮点数读取...")
            float_val = await client.read_float32(
                slave_id=1, start_address=20, callback=on_float_read
            )
            print(f"   主线程收到浮点数: {float_val}")

            # 等待一下让回调函数执行完成
            await asyncio.sleep(0.1)

        except Exception as e:
            print(f"回调示例失败: {e}")


async def concurrent_operations_example():
    """并发操作示例"""
    print("\n=== 异步RTU并发操作示例 ===")

    transport = AsyncRtuTransport(
        port="COM10",
        baudrate=9600,
        timeout=2.0
    )

    async with AsyncModbusClient(transport) as client:
        try:
            print(
                "\n并发执行多个读取操作..."
            )

            # 创建多个并发任务
            tasks = [
                client.read_holding_registers(slave_id=1, start_address=0, quantity=2),
                client.read_holding_registers(slave_id=1, start_address=10, quantity=2),
                client.read_holding_registers(slave_id=1, start_address=20, quantity=2),
                client.read_coils(slave_id=1, start_address=0, quantity=8),
                client.read_input_registers(slave_id=1, start_address=0, quantity=4),
            ]

            # 并发执行所有任务
            start_time = asyncio.get_event_loop().time()
            results = await asyncio.gather(*tasks)
            end_time = asyncio.get_event_loop().time()

            print(
                f"   并发执行耗时: {end_time - start_time:.3f}秒"
            )
            print(f"   保持寄存器0-1: {results[0]}")
            print(f"   保持寄存器10-11: {results[1]}")
            print(f"   保持寄存器20-21: {results[2]}")
            print(f"   线圈0-7: {results[3]}")
            print(f"   输入寄存器0-3: {results[4]}")

        except Exception as e:
            print(f"并发操作失败: {e}")


async def sensor_monitoring_example():
    """异步传感器监控示例"""
    print("\n=== 异步RTU传感器监控示例 ===")

    transport = AsyncRtuTransport(
        port="COM10",
        baudrate=9600,
        timeout=2.0
    )

    async with AsyncModbusClient(transport) as client:
        try:
            print("异步连续监控传感器数据......")

            # 创建监控任务
            async def monitor_temperature():
                for i in range(3):
                    temp = await client.read_float32(slave_id=1, start_address=100)
                    print(f"   [温度监控] 第{i + 1}次 #{i + 1}: {temp:.1f}°C")
                    await asyncio.sleep(1)

            async def monitor_pressure():
                for i in range(3):
                    pressure_raw = await client.read_holding_registers(slave_id=1, start_address=104, quantity=1)
                    pressure = pressure_raw[0] / 10.0
                    print(f"   [压力监控] 第{i + 1}次 #{i + 1}: {pressure:.1f}bar")
                    await asyncio.sleep(1.5)

            async def monitor_status():
                for i in range(3):
                    status = await client.read_coils(slave_id=1, start_address=0, quantity=1)
                    print(f"   [状态监控] 第{i + 1}次 #{i + 1}: {'运行' if status[0] else '停止'}")
                    await asyncio.sleep(2)

            # 并发执行所有监控任务
            await asyncio.gather(
                monitor_temperature(),
                monitor_pressure(),
                monitor_status()
            )

        except Exception as e:
            print(f"异步传感器监控失败: {e}")


async def main():
    """主函数"""
    print("ModbusLink 异步RTU客户端示例")
    print("=" * 60)

    print("\n注意：此示例需要一个连接到串口的Modbus RTU设备")
    print("\n异步RTU的优势:")
    print("  - 非阻塞I/O操作")
    print("  - 支持并发通信")
    print("  - 高效的资源利用")
    print("  - 适合高频率数据采集")
    print("\n请修改串口参数以匹配您的设备：")
    print("  - port: COM10 (Windows) 或 /dev/ttyUSB0 (Linux)")
    print("  - baudrate: 9600")
    print("  - slave_id: 1")

    try:
        # 依次执行各个示例
        await basic_operations_example()
        await advanced_data_types_example()
        await callback_example()
        await concurrent_operations_example()
        await sensor_monitoring_example()

        print("\n=== 所有示例执行完成 ===")

    except KeyboardInterrupt:
        print("\n用户中断")
    except ConnectionError as e:
        print(f"\n❌ 连接错误: {e}")
        print("请检查:")
        print("  - 串口是否存在且可用")
        print("  - 串口是否被其他程序占用")
        print("  - 串口参数是否正确")
    except TimeoutError as e:
        print(f"\n❌ 超时错误: {e}")
        print("请检查:")
        print("  - Modbus设备是否已连接并正常工作")
        print("  - 串口线缆是否正常")
        print("  - 波特率等参数是否与设备匹配")
    except CRCError as e:
        print(f"\n❌ CRC校验错误: {e}")
        print("请检查:")
        print("  - 串口线缆是否有干扰")
        print("  - 波特率是否正确")
        print("  - 设备是否支持Modbus RTU协议")
    except ModbusException as e:
        print(f"\n❌ Modbus协议异常: {e}")
        print("请检查:")
        print("  - 从站地址是否正确")
        print("  - 寄存器地址是否有效")
        print("  - 设备是否支持请求的功能码")
    except Exception as e:
        print(f"\n❌ 未知错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # 运行异步主函数
    asyncio.run(main())
