"""
ModbusLink 同步RTU客户端示例
演示如何使用同步RTU传输层进行Modbus通信，
包括基本的读写操作、高级数据类型操作和错误处理。
"""

import logging
import time
from src.modbuslink import (
    ModbusClient,
    RtuTransport,
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


def basic_operations_example():
    """基本操作示例"""
    print("\n=== 同步RTU基本操作示例 ===")

    # 创建RTU传输层
    transport = RtuTransport(
        port="COM10",  # Windows: COM10, Linux: /dev/ttyUSB0
        baudrate=9600,
        timeout=2.0
    )

    # 创建客户端
    client = ModbusClient(transport)

    try:
        with client:
            # 读取保持寄存器
            print("\n1. 读取保持寄存器...")
            registers = client.read_holding_registers(
                slave_id=1, start_address=0, quantity=4
            )
            print(f"   寄存器值: {registers}")

            # 写入单个寄存器
            print("\n2. 写入单个寄存器...")
            client.write_single_register(slave_id=1, address=0, value=1234)
            print("   写入完成")

            # 验证写入结果
            print("\n3. 验证写入结果...")
            value = client.read_holding_registers(
                slave_id=1, start_address=0, quantity=1
            )
            print(f"   寄存器0的值: {value[0]}")

            # 写入多个寄存器
            print("\n4. 写入多个寄存器...")
            values = [1111, 2222, 3333, 4444]
            client.write_multiple_registers(
                slave_id=1, start_address=10, values=values
            )
            print(f"   写入值: {values}")

            # 读取多个寄存器
            print("\n5. 读取多个寄存器...")
            read_values = client.read_holding_registers(
                slave_id=1, start_address=10, quantity=4
            )
            print(f"   读取值: {read_values}")

            # 线圈操作
            print("\n6. 线圈操作...")
            client.write_single_coil(slave_id=1, address=0, value=True)
            coils = client.read_coils(slave_id=1, start_address=0, quantity=8)
            print(f"   线圈状态: {coils}")

            # 写入多个线圈
            coil_values = [True, False, True, False, True, False, True, False]
            client.write_multiple_coils(
                slave_id=1, start_address=0, values=coil_values
            )
            coils = client.read_coils(slave_id=1, start_address=0, quantity=8)
            print(f"   更新后的线圈状态: {coils}")

    except Exception as e:
        print(f"操作失败: {e}")


def advanced_data_types_example():
    """高级数据类型示例"""
    print("\n=== 同步RTU高级数据类型示例 ===")

    transport = RtuTransport(
        port="COM10",
        baudrate=9600,
        timeout=2.0
    )

    client = ModbusClient(transport)

    try:
        with client:
            # 写入32位浮点数
            print("\n1. 写入32位浮点数...")
            temperature = 25.6
            client.write_float32(slave_id=1, start_address=20, value=temperature)
            print(f"   写入温度值: {temperature}°C")

            # 读取32位浮点数
            print("\n2. 读取32位浮点数...")
            read_temp = client.read_float32(slave_id=1, start_address=20)
            print(f"   读取温度值: {read_temp}°C")

            # 写入32位有符号整数
            print("\n3. 写入32位有符号整数...")
            pressure = -12345
            client.write_int32(slave_id=1, start_address=22, value=pressure)
            print(f"   写入压力值: {pressure}")

            # 读取32位有符号整数
            print("\n4. 读取32位有符号整数...")
            read_pressure = client.read_int32(slave_id=1, start_address=22)
            print(f"   读取压力值: {read_pressure}")

            # 测试不同的字节序和字序
            print(
                "\n5. 测试不同的字节序和字序..."
            )
            test_value = 3.14159

            # 大端序，高位字节在前 (默认)
            client.write_float32(
                slave_id=1,
                start_address=30,
                value=test_value,
                byte_order="big",
                word_order="high",
            )
            read_val1 = client.read_float32(
                slave_id=1, start_address=30, byte_order="big", word_order="high"
            )
            print(
                f"   Big/High: 写入 {test_value}, 读取 {read_val1}"
            )

            # 小端序，低位字节在前
            client.write_float32(
                slave_id=1,
                start_address=32,
                value=test_value,
                byte_order="little",
                word_order="low",
            )
            read_val2 = client.read_float32(
                slave_id=1, start_address=32, byte_order="little", word_order="low"
            )
            print(
                f"   Little/Low: 写入 {test_value}, 读取 {read_val2}"
            )

    except Exception as e:
        print(f"高级操作失败: {e}")


def sensor_monitoring_example():
    """传感器监控示例"""
    print("\n=== 同步RTU传感器监控示例 ===")

    transport = RtuTransport(
        port="COM10",
        baudrate=9600,
        timeout=2.0
    )

    client = ModbusClient(transport)

    try:
        with client:
            print("连续读取传感器数据...")
            for i in range(3):
                # 读取温度传感器（浮点数）
                temp = client.read_float32(slave_id=1, start_address=100)

                # 读取湿度传感器（整数，需要除以100）
                humidity_raw = client.read_holding_registers(slave_id=1, start_address=104, quantity=1)[0]
                humidity = humidity_raw / 100.0

                # 读取设备状态（线圈）
                status = client.read_coils(slave_id=1, start_address=0, quantity=1)[0]

                print(
                    f"  第{i + 1}次读取 #{i + 1}: 温度={temp:.1f}°C, 湿度={humidity:.1f}%, 状态={'运行' if status else '停止'}"
                )

                if i < 2:  # 最后一次不等待
                    time.sleep(1)

    except Exception as e:
        print(f"传感器数据读取失败: {e}")


def main():
    """主函数"""
    print("ModbusLink 同步RTU客户端示例")
    print("=" * 60)

    print("\n注意：此示例需要一个连接到串口的Modbus RTU设备")
    print("\n请修改串口参数以匹配您的设备：")
    print("  - port: COM10 (Windows) 或 /dev/ttyUSB0 (Linux)")
    print("  - baudrate: 9600")
    print("  - slave_id: 1")

    try:
        # 依次执行各个示例
        basic_operations_example()
        advanced_data_types_example()
        sensor_monitoring_example()

        print("\n=== 所有示例执行完成 ===")

    except KeyboardInterrupt:
        print("\n用户中断")
    except ConnectionError as e:
        print(f"\nNO!!! 连接错误: {e}")
        print("请检查:")
        print("  - 串口是否存在且可用")
        print("  - 串口是否被其他程序占用")
        print("  - 串口参数是否正确")
    except TimeoutError as e:
        print(f"\nNO!!! 超时错误: {e}")
        print("请检查:")
        print("  - Modbus设备是否已连接并正常工作")
        print("  - 串口线缆是否正常")
        print("  - 波特率等参数是否与设备匹配")
    except CRCError as e:
        print(f"\nNO!!! CRC校验错误: {e}")
        print("请检查:")
        print("  - 串口线缆是否有干扰")
        print("  - 波特率是否正确")
        print("  - 设备是否支持Modbus RTU协议")
    except ModbusException as e:
        print(f"\nNO!!! Modbus协议异常: {e}")
        print("请检查")
        print("  - 从站地址是否正确")
        print("  - 寄存器地址是否有效")
        print("  - 设备是否支持请求的功能码")
    except Exception as e:
        print(f"\nNO!!! 未知错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
