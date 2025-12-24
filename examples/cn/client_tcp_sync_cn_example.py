"""
ModbusLink 同步TCP客户端示例
演示如何使用同步TCP传输层进行Modbus通信，
包括基本的读写操作、高级数据类型操作和错误处理。
"""

import logging
import time
from src.modbuslink import (
    ModbusClient,
    TcpTransport,
    ConnectionError,
    TimeoutError,
    InvalidResponseError,
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
    print("\n=== 同步TCP基本操作示例 ===")

    # 创建TCP传输层
    transport = TcpTransport(host="127.0.0.1", port=502, timeout=5.0)

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

            # 读取输入寄存器
            print("\n7. 读取输入寄存器...")
            input_registers = client.read_input_registers(
                slave_id=1, start_address=0, quantity=5
            )
            print(f"   输入寄存器值: {input_registers}")

            # 读取离散输入
            print("\n8. 读取离散输入...")
            discrete_inputs = client.read_discrete_inputs(
                slave_id=1, start_address=0, quantity=8
            )
            print(f"   离散输入状态: {discrete_inputs}")

    except Exception as e:
        print(f"操作失败: {e}")


def advanced_data_types_example():
    """高级数据类型示例"""
    print("\n=== 同步TCP高级数据类型示例 ===")

    transport = TcpTransport(host="127.0.0.1", port=502, timeout=5.0)
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

            # 写入字符串
            print("\n5. 写入字符串...")
            device_name = "TCP_Device"
            client.write_string(slave_id=1, start_address=30, value=device_name)
            print(f"   写入设备名称: '{device_name}'")

            # 读取字符串
            print("\n6. 读取字符串...")
            read_name = client.read_string(
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

            # 大端格式，高位字在前 (默认)
            client.write_float32(
                slave_id=1,
                start_address=40,
                value=test_value,
                byte_order="big",
                word_order="high",
            )
            read_val1 = client.read_float32(
                slave_id=1, start_address=40, byte_order="big", word_order="high"
            )
            print(
                f"   Big/High: 写入 {test_value}, 读取 {read_val1}"
            )

            # 小端格式，低字节在前          
            client.write_float32(
                slave_id=1,
                start_address=42,
                value=test_value,
                byte_order="little",
                word_order="low",
            )
            read_val2 = client.read_float32(
                slave_id=1, start_address=42, byte_order="little", word_order="low"
            )
            print(
                f"   Little/Low: 写入 {test_value}, 读取 {read_val2}"
            )

    except Exception as e:
        print(f"高级操作失败: {e}")


def industrial_monitoring_example():
    """工业监控示例"""
    print("\n=== 同步TCP工业监控示例 ===")

    transport = TcpTransport(host="127.0.0.1", port=502, timeout=5.0)
    client = ModbusClient(transport)

    try:
        with client:
            print("连续监控工业设备数据...")
            for i in range(3):
                # 读取温度传感器（浮点数）
                temp = client.read_float32(slave_id=1, start_address=100)

                # 读取压力传感器（整数，需要除以10）
                pressure_raw = client.read_input_registers(slave_id=1, start_address=102, quantity=1)[0]
                pressure = pressure_raw / 10.0

                # 读取设备运行状态（线圈）
                running = client.read_coils(slave_id=1, start_address=0, quantity=1)[0]

                # 读取报警状态（离散输入）
                alarm = client.read_discrete_inputs(slave_id=1, start_address=0, quantity=1)[0]

                # 读取生产计数器（32位整数）
                counter = client.read_int32(slave_id=1, start_address=110)

                print(
                    f"  第{i + 1}次监控  #{i + 1}: 温度={temp:.1f}°C, 压力={pressure:.1f}bar, "
                    f"运行={'是' if running else '否'}, 报警={'是' if alarm else '否'}, 计数器={counter}"
                )

                # 根据温度调整设定值
                if temp > 30.0:
                    new_setpoint = 28.0
                    client.write_float32(slave_id=1, start_address=120, value=new_setpoint)
                    print(
                        f"    温度过高，调整设定值为 {new_setpoint}°C")

                if i < 2:  # 最后一次不等待
                    time.sleep(2)

    except Exception as e:
        print(f"工业监控失败: {e}")


def main():
    """主函数"""
    print("ModbusLink 同步TCP客户端示例")
    print("=" * 60)

    print("\n注意：此示例需要一个运行在127.0.0.1:502的Modbus TCP服务器")
    print("\n你可以使用ModbusLink的从站模拟器：")
    print("\n  from modbuslink import ModbusSlave")
    print("  slave = ModbusSlave(slave_id=1)")
    print("  slave.start_tcp_server('127.0.0.1', 502)")

    try:
        # 依次执行各个示例
        basic_operations_example()
        advanced_data_types_example()
        industrial_monitoring_example()

        print("\n=== 所有示例执行完成 ===")

    except KeyboardInterrupt:
        print("\n用户中断")
    except ConnectionError as e:
        print(f"\nNO!!! 连接错误: {e}")
        print("请检查:")
        print(f"  - 目标设备 127.0.0.1:502 是否可达")
        print("  - 网络连接是否正常")
        print("  - 防火墙是否阻止连接")
        print("  - 设备是否支持Modbus TCP协议")
    except TimeoutError as e:
        print(f"\nNO!!! 超时错误: {e}")
        print("请检查:")
        print("  - 网络延迟是否过高")
        print("  - 设备响应是否正常")
        print("  - 超时设置是否合理")
    except InvalidResponseError as e:
        print(f"\nNO!!! 响应格式错误: {e}")
        print("请检查:")
        print("  - 设备是否正确实现Modbus TCP协议")
        print("  - 网络传输是否有数据损坏")
    except ModbusException as e:
        print(f"\nNO!!! Modbus协议异常: {e}")
        print("请检查:")
        print("  - 单元标识符是否正确")
        print("  - 寄存器地址是否有效")
        print("  - 设备是否支持请求的功能码")
    except Exception as e:
        print(f"\nNO!!! 未知错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
