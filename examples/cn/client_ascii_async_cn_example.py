"""
ModbusLink 异步ASCII客户端示例
演示如何使用异步ASCII传输层进行Modbus通信，
包括基本的读写操作、高级数据类型操作、调试功能和错误处理。
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
from src.modbuslink.utils.logging import ModbusLogger

# 设置日志
ModbusLogger.setup_logging(
    level=logging.INFO,
    enable_debug=True,
)


async def basic_operations_example():
    """基本操作示例"""
    print("\n=== 异步ASCII基本操作示例 ===")

    # 创建异步ASCII传输层
    transport = AsyncAsciiTransport(
        port="COM10",  # Windows: COM10, Linux: /dev/ttyUSB0
        baudrate=9600,
        timeout=3.0
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

            # 写入多个寄存器 | Write multiple registers
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

            # 输入寄存器和离散输入
            print("\n7. 读取输入寄存器...")
            input_regs = await client.read_input_registers(
                slave_id=1, start_address=0, quantity=4
            )
            print(f"   输入寄存器值: {input_regs}")

            print("\n8. 读取离散输入...")
            discrete_inputs = await client.read_discrete_inputs(
                slave_id=1, start_address=0, quantity=8
            )
            print(f"   离散输入状态: {discrete_inputs}")

        except Exception as e:
            print(f"操作失败: {e}")


async def advanced_data_types_example():
    """高级数据类型示例"""
    print("\n=== 异步ASCII高级数据类型示例 ===")

    transport = AsyncAsciiTransport(
        port="COM10",
        baudrate=9600,
        timeout=3.0
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

            # 写入32位无符号整数(貌似有点问题后面在修复)
            # print("\n5. 写入32位无符号整数...")
            # counter = 65535  # 适合ASCII传输的较小值
            # await client.write_uint32(slave_id=1, start_address=24, value=counter)
            # print(f"   写入计数器值: {counter}")

            # 读取32位无符号整数(貌似有点问题后面在修复)
            # print("\n6. 读取32位无符号整数...")
            # read_counter = await client.read_uint32(slave_id=1, start_address=24)
            # print(f"   读取计数器值: {read_counter}")

            # 写入字符串(貌似有点问题后面在修复)
            # print("\n7. 写入字符串...")
            # device_name = "AsyncASCII_Dev"
            # await client.write_string(slave_id=1, start_address=30, value=device_name)
            # print(f"   写入设备名称: '{device_name}'")

            # 读取字符串(貌似有点问题后面在修复)
            # print("\n8. 读取字符串...")
            # read_name = await client.read_string(
            #     slave_id=1,
            #     start_address=30,
            #     length=len(device_name.encode("utf-8")),
            # )
            # print(f"   读取设备名称: '{read_name}'")

            # 测试不同的字节序和字序
            print(
                "\n9. 测试不同的字节序和字序..."
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
            print(f"高级操作失败")


async def debugging_example():
    """调试功能示例"""
    print("\n=== 异步ASCII调试功能示例 ===")

    # 启用调试模式的传输层
    transport = AsyncAsciiTransport(
        port="COM10",
        baudrate=9600,
        timeout=3.0
    )

    async with AsyncModbusClient(transport) as client:
        try:
            print("\n1. ASCII协议特性演示...")
            print("   ASCII协议使用可读的十六进制字符")
            print("   每个字节用两个ASCII字符表示")
            print("   使用LRC校验而非CRC校验")

            # 演示ASCII帧格式
            print("\n2. ASCII帧格式示例:")
            print("   起始字符: ':' (0x3A)")
            print("   从站地址: 01 (ASCII)")
            print("   功能码: 03 (ASCII)")
            print("   数据: 0000 0004 (ASCII)")
            print("   LRC校验: F8 (ASCII)")
            print("   结束字符: CR LF (0x0D 0x0A)")

            # 执行实际操作以观察ASCII通信
            print("\n3. 执行读取操作以观察ASCII通信...")
            registers = await client.read_holding_registers(
                slave_id=1, start_address=0, quantity=4
            )
            print(f"   读取结果: {registers}")

            print("\n4. 执行写入操作以观察ASCII通信...")
            await client.write_single_register(slave_id=1, address=0, value=0x1234)
            print("   写入完成")

            # ASCII协议的优势和劣势
            print("\n5. ASCII协议特点分析:")
            print("   优势:")
            print("     - 可读性强，便于调试")
            print("     - 兼容性好")
            print("     - 错误检测容易")
            print("   劣势:")
            print("     - 传输效率低")
            print("     - 占用带宽大")
            print("     - 处理速度慢")

        except Exception as e:
            print(f"调试示例失败: {e}")


async def error_handling_example():
    """错误处理示例"""
    print("\n=== 异步ASCII错误处理示例 ===")

    transport = AsyncAsciiTransport(
        port="COM10",
        baudrate=9600,
        timeout=3.0
    )

    async with AsyncModbusClient(transport) as client:
        try:
            print("\n1. 测试超时处理...")
            try:
                # 尝试读取可能不存在的寄存器
                registers = await client.read_holding_registers(
                    slave_id=99, start_address=0, quantity=1  # 使用不存在的从站ID
                )
                print(f"   意外成功: {registers}")
            except TimeoutError as e:
                print(f"   ✓ 超时错误正确捕获: {e}")

            print("\n2. 测试LRC校验错误处理...")
            # 注意：LRC错误通常由传输层自动处理
            print("   LRC校验在传输层自动处理")

            print("\n3. 测试Modbus异常处理...")
            try:
                # 尝试读取无效的寄存器地址
                registers = await client.read_holding_registers(
                    slave_id=1, start_address=65535, quantity=1  # 无效地址
                )
                print(f"   意外成功: {registers}")
            except InvalidResponseError as e:
                print(f"   ✓ Modbus异常正确捕获: {e}")

            print("\n4. 测试连接错误处理...")
            # 这个测试在实际设备连接时可能不会触发
            print(
                "   连接错误通常在传输层初始化时发生")

            print("\n5. 错误恢复策略:")
            print("   - 自动重试机制")
            print("   - 连接状态监控")
            print("   - 优雅降级处理")
            print("   - 详细错误日志")

        except Exception as e:
            print(f"错误处理示例失败: {e}")


async def performance_comparison_example():
    """性能对比示例"""
    print("\n=== 异步ASCII性能对比示例 ===")

    transport = AsyncAsciiTransport(
        port="COM10",
        baudrate=9600,
        timeout=3.0
    )

    async with AsyncModbusClient(transport) as client:
        try:
            print("\n1. 单次操作性能测试...")

            # 测试读取操作性能
            start_time = asyncio.get_event_loop().time()
            registers = await client.read_holding_registers(
                slave_id=1, start_address=0, quantity=10
            )
            end_time = asyncio.get_event_loop().time()
            read_time = end_time - start_time
            print(f"   读取10个寄存器耗时: {read_time:.3f}秒")

            # 测试写入操作性能
            start_time = asyncio.get_event_loop().time()
            await client.write_multiple_registers(
                slave_id=1, start_address=10, values=[i for i in range(10)]
            )
            end_time = asyncio.get_event_loop().time()
            write_time = end_time - start_time
            print(f"   写入10个寄存器耗时: {write_time:.3f}秒")

            print("\n2. 批量操作性能测试...")

            # 批量读取测试
            start_time = asyncio.get_event_loop().time()
            tasks = [
                client.read_holding_registers(slave_id=1, start_address=i * 10, quantity=5)
                for i in range(5)
            ]
            results = await asyncio.gather(*tasks)
            end_time = asyncio.get_event_loop().time()
            batch_time = end_time - start_time
            print(f"   并发读取5组寄存器耗时: {batch_time:.3f}秒")
            print(f"   平均每组耗时: {batch_time / 5:.3f}秒")

            print("\n3. ASCII vs RTU 性能对比分析:")
            print("   ASCII协议特点:")
            print(f"     - 单次读取耗时: ~{read_time:.3f}秒: ~{read_time:.3f}s")
            print(f"     - 单次写入耗时: ~{write_time:.3f}秒: ~{write_time:.3f}s")
            print("     - 数据量是RTU的2倍")
            print("     - 传输速度较慢")
            print("     - 调试友好")

            print("\n   建议使用场景:")
            print("     - 调试和开发阶段")
            print("     - 低速串口通信")
            print("     - 需要人工监控的场合")
            print("     - 兼容老旧设备")

        except Exception as e:
            print(f"性能对比示例失败: {e}")


async def sensor_monitoring_example():
    """异步传感器监控示例"""
    print("\n=== 异步ASCII传感器监控示例 ===")

    transport = AsyncAsciiTransport(
        port="COM10",
        baudrate=9600,
        timeout=3.0
    )

    async with AsyncModbusClient(transport) as client:
        try:
            print("异步连续监控传感器数据...")

            # 创建监控任务
            async def monitor_temperature():
                """监控温度传感器"""
                for i in range(3):
                    temp = await client.read_float32(slave_id=1, start_address=100)
                    status = "正常" if 0 <= temp <= 100 else "异常"
                    print(f"   [温度监控] 第{i + 1}次 #{i + 1}: {temp:.1f}°C ({status})")
                    await asyncio.sleep(2)  # ASCII较慢，增加间隔

            async def monitor_humidity():
                """监控湿度传感器"""
                for i in range(3):
                    humidity_raw = await client.read_holding_registers(slave_id=1, start_address=102, quantity=1)
                    humidity = humidity_raw[0] / 10.0
                    status = "正常" if 0 <= humidity <= 100 else "异常"
                    print(f"   [湿度监控] 第{i + 1}次 #{i + 1}: {humidity:.1f}% ({status})")
                    await asyncio.sleep(2.5)

            async def monitor_status():
                """监控设备状态"""
                for i in range(3):
                    status = await client.read_coils(slave_id=1, start_address=0, quantity=1)
                    print(f"   [状态监控] 第{i + 1}次 #{i + 1}: {'运行' if status[0] else '停止'}")
                    await asyncio.sleep(3)

            # 并发执行所有监控任务
            await asyncio.gather(
                monitor_temperature(),
                monitor_humidity(),
                monitor_status()
            )

        except Exception as e:
            print(f"异步传感器监控失败: {e}")


async def main():
    """主函数"""
    print("ModbusLink 异步ASCII客户端示例")
    print("=" * 60)

    print("\n注意：此示例需要一个连接到串口的Modbus ASCII设备")
    print("\n异步ASCII的特点:")
    print("  - 非阻塞串口I/O")
    print("  - 可读的ASCII格式")
    print("  - 便于调试和监控")
    print("  - 兼容性强")
    print("  - 传输效率较低")
    print("\n配置说明:")
    print("  - ASCII协议通常使用较低的波特率")
    print("  - 建议波特率: 1200, 2400, 4800, 9600")
    print("  - 数据位: 7或8位")
    print("  - 校验位: 偶校验、奇校验或无校验")
    print("  - 停止位: 1或2位")
    print("\n请修改串口参数以匹配您的设备：")
    print("Please modify serial port parameters to match your device:")
    print("  - port: COM10 (Windows) 或 /dev/ttyUSB0 (Linux)")
    print("  - baudrate: 9600")
    print("  - slave_id: 1")

    try:
        # 依次执行各个示例
        await basic_operations_example()
        await advanced_data_types_example()
        await debugging_example()
        await error_handling_example()
        # await performance_comparison_example()  # 貌似有点问题后面在修复
        # await sensor_monitoring_example()  # 貌似有点问题后面在修复

        print("\n=== 所有示例执行完成 ===")

    except KeyboardInterrupt:
        print("\n用户中断")
    except ConnectionError as e:
        print(f"\nNO!!! 连接错误: {e}")
        print("请检查:")
        print("  - 串口是否存在且可用")
        print("  - 串口是否被其他程序占用")
        print("  - 串口参数是否正确")
        print("  - 设备是否支持ASCII模式")
    except TimeoutError as e:
        print(f"\nNO!!! 超时错误: {e}")
        print("请检查:")
        print("  - Modbus设备是否已连接并正常工作")
        print("  - 串口线缆是否正常")
        print("  - 波特率等参数是否与设备匹配")
        print("  - 设备是否配置为ASCII模式")
    except CRCError as e:
        print(f"\nNO!!! CRC校验错误: {e}")
        print("请检查:")
        print("  - 串口线缆是否有干扰")
        print("  - 波特率是否正确")
        print("  - 设备是否支持Modbus ASCII协议")
        print("  - 数据位、校验位、停止位设置")
    except ModbusException as e:
        print(f"\nNO!!! Modbus协议异常: {e}")
        print("请检查:")
        print("  - 从站地址是否正确")
        print("  - 寄存器地址是否有效")
        print("  - 设备是否支持请求的功能码")
        print("  - 设备是否处于ASCII模式")
    except Exception as e:
        print(f"\nNO!!! 未知错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # 运行异步主函数
    asyncio.run(main())
