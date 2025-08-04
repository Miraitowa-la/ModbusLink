"""
ModbusLink 同步TCP客户端示例
演示如何使用同步TCP传输层进行Modbus通信，
包括基本的读写操作、高级数据类型操作和错误处理。

ModbusLink Sync TCP Client Example
Demonstrates how to use sync TCP transport for Modbus communication,
including basic read/write operations, advanced data type operations and error handling.
"""

import logging
import time
from modbuslink import (
    ModbusClient,
    TcpTransport,
    ConnectionError,
    TimeoutError,
    InvalidResponseError,
    ModbusException,
)

# 配置日志 | Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


def basic_operations_example():
    """基本操作示例 | Basic operations example"""
    print("\n=== 同步TCP基本操作示例 | Sync TCP Basic Operations Example ===")

    # 创建TCP传输层 | Create TCP transport
    transport = TcpTransport(host="127.0.0.1", port=502, timeout=5.0)

    # 创建客户端 | Create client
    client = ModbusClient(transport)

    try:
        with client:
            # 读取保持寄存器 | Read holding registers
            print("\n1. 读取保持寄存器 | Reading holding registers...")
            registers = client.read_holding_registers(
                slave_id=1, start_address=0, quantity=4
            )
            print(f"   寄存器值 | Register values: {registers}")

            # 写入单个寄存器 | Write single register
            print("\n2. 写入单个寄存器 | Writing single register...")
            client.write_single_register(slave_id=1, address=0, value=1234)
            print("   写入完成 | Write completed")

            # 验证写入结果 | Verify write result
            print("\n3. 验证写入结果 | Verifying write result...")
            value = client.read_holding_registers(
                slave_id=1, start_address=0, quantity=1
            )
            print(f"   寄存器0的值 | Register 0 value: {value[0]}")

            # 写入多个寄存器 | Write multiple registers
            print("\n4. 写入多个寄存器 | Writing multiple registers...")
            values = [1111, 2222, 3333, 4444]
            client.write_multiple_registers(
                slave_id=1, start_address=10, values=values
            )
            print(f"   写入值 | Written values: {values}")

            # 读取多个寄存器 | Read multiple registers
            print("\n5. 读取多个寄存器 | Reading multiple registers...")
            read_values = client.read_holding_registers(
                slave_id=1, start_address=10, quantity=4
            )
            print(f"   读取值 | Read values: {read_values}")

            # 线圈操作 | Coil operations
            print("\n6. 线圈操作 | Coil operations...")
            client.write_single_coil(slave_id=1, address=0, value=True)
            coils = client.read_coils(slave_id=1, start_address=0, quantity=8)
            print(f"   线圈状态 | Coil status: {coils}")

            # 写入多个线圈 | Write multiple coils
            coil_values = [True, False, True, False, True, False, True, False]
            client.write_multiple_coils(
                slave_id=1, start_address=0, values=coil_values
            )
            coils = client.read_coils(slave_id=1, start_address=0, quantity=8)
            print(f"   更新后的线圈状态 | Updated coil status: {coils}")

            # 读取输入寄存器 | Read input registers
            print("\n7. 读取输入寄存器 | Reading input registers...")
            input_registers = client.read_input_registers(
                slave_id=1, start_address=0, quantity=5
            )
            print(f"   输入寄存器值 | Input register values: {input_registers}")

            # 读取离散输入 | Read discrete inputs
            print("\n8. 读取离散输入 | Reading discrete inputs...")
            discrete_inputs = client.read_discrete_inputs(
                slave_id=1, start_address=0, quantity=8
            )
            print(f"   离散输入状态 | Discrete input status: {discrete_inputs}")

    except Exception as e:
        print(f"操作失败 | Operation failed: {e}")


def advanced_data_types_example():
    """高级数据类型示例 | Advanced data types example"""
    print("\n=== 同步TCP高级数据类型示例 | Sync TCP Advanced Data Types Example ===")

    transport = TcpTransport(host="127.0.0.1", port=502, timeout=5.0)
    client = ModbusClient(transport)

    try:
        with client:
            # 写入32位浮点数 | Write 32-bit float
            print("\n1. 写入32位浮点数 | Writing 32-bit float...")
            temperature = 25.6
            client.write_float32(slave_id=1, start_address=20, value=temperature)
            print(f"   写入温度值 | Written temperature: {temperature}°C")

            # 读取32位浮点数 | Read 32-bit float
            print("\n2. 读取32位浮点数 | Reading 32-bit float...")
            read_temp = client.read_float32(slave_id=1, start_address=20)
            print(f"   读取温度值 | Read temperature: {read_temp}°C")

            # 写入32位有符号整数 | Write 32-bit signed integer
            print("\n3. 写入32位有符号整数 | Writing 32-bit signed integer...")
            pressure = -12345
            client.write_int32(slave_id=1, start_address=22, value=pressure)
            print(f"   写入压力值 | Written pressure: {pressure}")

            # 读取32位有符号整数 | Read 32-bit signed integer
            print("\n4. 读取32位有符号整数 | Reading 32-bit signed integer...")
            read_pressure = client.read_int32(slave_id=1, start_address=22)
            print(f"   读取压力值 | Read pressure: {read_pressure}")

            # 写入字符串 | Write string
            print("\n5. 写入字符串 | Writing string...")
            device_name = "TCP_Device"
            client.write_string(slave_id=1, start_address=30, value=device_name)
            print(f"   写入设备名称 | Written device name: '{device_name}'")

            # 读取字符串 | Read string
            print("\n6. 读取字符串 | Reading string...")
            read_name = client.read_string(
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
                f"   Big/High: 写入 {test_value}, 读取 {read_val1} | Written {test_value}, Read {read_val1}"
            )

            # Little endian, low word first
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
                f"   Little/Low: 写入 {test_value}, 读取 {read_val2} | Written {test_value}, Read {read_val2}"
            )

    except Exception as e:
        print(f"高级操作失败 | Advanced operation failed: {e}")


def industrial_monitoring_example():
    """工业监控示例 | Industrial monitoring example"""
    print("\n=== 同步TCP工业监控示例 | Sync TCP Industrial Monitoring Example ===")

    transport = TcpTransport(host="127.0.0.1", port=502, timeout=5.0)
    client = ModbusClient(transport)

    try:
        with client:
            print("连续监控工业设备数据... | Continuously monitoring industrial device data...")
            for i in range(3):
                # 读取温度传感器（浮点数）| Read temperature sensor (float)
                temp = client.read_float32(slave_id=1, start_address=100)

                # 读取压力传感器（整数，需要除以10）| Read pressure sensor (integer, divide by 10)
                pressure_raw = client.read_input_registers(slave_id=1, start_address=102, quantity=1)[0]
                pressure = pressure_raw / 10.0

                # 读取设备运行状态（线圈）| Read device running status (coil)
                running = client.read_coils(slave_id=1, start_address=0, quantity=1)[0]

                # 读取报警状态（离散输入）| Read alarm status (discrete input)
                alarm = client.read_discrete_inputs(slave_id=1, start_address=0, quantity=1)[0]

                # 读取生产计数器（32位整数）| Read production counter (32-bit integer)
                counter = client.read_int32(slave_id=1, start_address=110)

                print(
                    f"  第{i+1}次监控 | Monitoring #{i+1}: 温度={temp:.1f}°C, 压力={pressure:.1f}bar, "
                    f"运行={'是' if running else '否'}, 报警={'是' if alarm else '否'}, 计数器={counter}"
                )

                # 根据温度调整设定值 | Adjust setpoint based on temperature
                if temp > 30.0:
                    new_setpoint = 28.0
                    client.write_float32(slave_id=1, start_address=120, value=new_setpoint)
                    print(f"    温度过高，调整设定值为 {new_setpoint}°C | Temperature too high, adjusted setpoint to {new_setpoint}°C")

                if i < 2:  # 最后一次不等待 | Don't wait on last iteration
                    time.sleep(2)

    except Exception as e:
        print(f"工业监控失败 | Industrial monitoring failed: {e}")


def main():
    """主函数 | Main function"""
    print("ModbusLink 同步TCP客户端示例 | ModbusLink Sync TCP Client Example")
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
        basic_operations_example()
        advanced_data_types_example()
        industrial_monitoring_example()

        print("\n=== 所有示例执行完成 | All Examples Completed ===")

    except KeyboardInterrupt:
        print("\n用户中断 | User interrupted")
    except ConnectionError as e:
        print(f"\n❌ 连接错误 | Connection error: {e}")
        print("请检查 | Please check:")
        print(f"  - 目标设备 127.0.0.1:502 是否可达 | Target device 127.0.0.1:502 is reachable")
        print("  - 网络连接是否正常 | Network connection is normal")
        print("  - 防火墙是否阻止连接 | Firewall is blocking connection")
        print("  - 设备是否支持Modbus TCP协议 | Device supports Modbus TCP protocol")
    except TimeoutError as e:
        print(f"\n❌ 超时错误 | Timeout error: {e}")
        print("请检查 | Please check:")
        print("  - 网络延迟是否过高 | Network latency is too high")
        print("  - 设备响应是否正常 | Device response is normal")
        print("  - 超时设置是否合理 | Timeout setting is reasonable")
    except InvalidResponseError as e:
        print(f"\n❌ 响应格式错误 | Invalid response format: {e}")
        print("请检查 | Please check:")
        print("  - 设备是否正确实现Modbus TCP协议 | Device correctly implements Modbus TCP protocol")
        print("  - 网络传输是否有数据损坏 | Network transmission has data corruption")
    except ModbusException as e:
        print(f"\n❌ Modbus协议异常 | Modbus protocol exception: {e}")
        print("请检查 | Please check:")
        print("  - 单元标识符是否正确 | Unit identifier is correct")
        print("  - 寄存器地址是否有效 | Register address is valid")
        print("  - 设备是否支持请求的功能码 | Device supports the requested function code")
    except Exception as e:
        print(f"\n❌ 未知错误 | Unknown error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()