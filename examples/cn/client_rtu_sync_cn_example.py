"""
ModbusLink 同步RTU客户端示例
"""

import logging
import traceback

from src.modbuslink import (
    SyncModbusClient,
    SyncRtuTransport,
    ConnectError,
    TimeOutError,
    CrcError,
    ModbusException,
    ModbusLogger,
    Language,
    set_language,
)


def basic_operation_example(client: SyncModbusClient):
    """基本操作示例"""
    print("\n=== 同步RTU基本操作示例 ===")

    try:
        with client:
            print("\n1. 读取线圈状态 (0x01)")
            coils = client.read_coils(
                slave_id=1, start_address=0, quantity=10
            )
            print(f"   线圈状态: {coils}")

            print("\n2. 读取离散输入状态 (0x02)")
            discrete_inputs = client.read_discrete_inputs(
                slave_id=1, start_address=0, quantity=10
            )
            print(f"   离散输入状态: {discrete_inputs}")

            print("\n3. 读取保持寄存器 (0x03)")
            holding_registers = client.read_holding_registers(
                slave_id=1, start_address=0, quantity=10
            )
            print(f"   保持寄存器: {holding_registers}")

            print("\n4. 读取输入寄存器 (0x04)")
            input_registers = client.read_input_registers(
                slave_id=1, start_address=0, quantity=10
            )
            print(f"   输入寄存器: {input_registers}")

            print("\n5. 写单个线圈 (0x05)")
            client.write_single_coil(
                slave_id=1, address=0, value=True
            )
            coils = client.read_coils(
                slave_id=1, start_address=0, quantity=1
            )
            print(f"   更新后线圈状态: {coils[0]}")

            print("\n6. 写单个寄存器 (0x06)")
            client.write_single_register(
                slave_id=1, address=0, value=1234
            )
            registers = client.read_holding_registers(
                slave_id=1, start_address=0, quantity=1
            )
            print(f"   更新后寄存器值: {registers[0]}")

            print("\n7. 写多个线圈 (0x0F)")
            client.write_multiple_coils(
                slave_id=1, start_address=5, values=[False, True, False, True, False]
            )
            coils = client.read_coils(
                slave_id=1, start_address=5, quantity=5
            )
            print(f"   更新后线圈状态: {coils}")

            print("\n8. 写多个寄存器 (0x10)")
            client.write_multiple_registers(
                slave_id=1, start_address=5, values=[1234, 5678, 51011, 31314, 4789]
            )
            registers = client.read_holding_registers(
                slave_id=1, start_address=5, quantity=5
            )
            print(f"   更新后寄存器值: {registers}")

    except Exception as e:
        print(f"操作失败: {e}")


def advanced_operation_example(client: SyncModbusClient):
    """高级操作示例"""
    print("\n=== 同步RTU高级操作示例 ===")

    try:
        with client:
            print("\n1. 写入32位浮点数")
            value = 25.6
            client.write_float32(
                slave_id=1, start_address=0, value=value
            )
            print(f"   写入值: {value}")

            print("\n2. 读取32位浮点数")
            read_value = client.read_float32(
                slave_id=1, start_address=0
            )
            print(f"   读取值: {read_value}")

            print("\n3. 写入32位有符号整数")
            value = -12345
            client.write_int32(
                slave_id=1, start_address=0, value=value
            )
            print(f"   写入值: {value}")

            print("\n4. 读取32位有符号整数")
            read_value = client.read_int32(
                slave_id=1, start_address=0
            )
            print(f"   读取值: {read_value}")

            print("\n5. 写入32位无符号整数")
            value = 12345
            client.write_uint32(
                slave_id=1, start_address=0, value=value
            )
            print(f"   写入值: {value}")

            print("\n6. 读取32位无符号整数")
            read_value = client.read_uint32(
                slave_id=1, start_address=0
            )
            print(f"   读取值: {read_value}")

            print("\n7. 写入64位有符号整数")
            value = -123
            client.write_int64(
                slave_id=1, start_address=0, value=value
            )
            print(f"   写入值: {value}")

            print("\n8. 读取64位有符号整数")
            read_value = client.read_int64(
                slave_id=1, start_address=0
            )
            print(f"   读取值: {read_value}")

            print("\n9. 写入64位无符号整数")
            value = 123
            client.write_uint64(
                slave_id=1, start_address=0, value=value
            )
            print(f"   写入值: {value}")

            print("\n10. 读取64位无符号整数")
            read_value = client.read_uint64(
                slave_id=1, start_address=0
            )
            print(f"   读取值: {read_value}")

            print("\n11. 写入字符串")
            value = "RTU Modbus"
            client.write_string(
                slave_id=1, start_address=0, value=value
            )
            print(f"   写入值: {value}")

            print("\n12. 读取字符串")
            read_value = client.read_string(
                slave_id=1, start_address=0, length=10
            )
            print(f"   读取值: {read_value}")

            print("\n13. 测试不同的字节序和字序(大端序，高位字)")
            value = 3.14159

            client.write_float32(
                slave_id=1,
                start_address=0,
                value=value,
                byte_order="big",
                word_order="high",
            )
            read_value = client.read_float32(
                slave_id=1,
                start_address=0,
                byte_order="big",
                word_order="high"
            )
            print(f"   Big/High: 写入 {value}, 读取 {read_value}")

            print("\n14. 测试不同的字节序和字序(小端序，低位字)")
            value = 3.14159

            client.write_float32(
                slave_id=1,
                start_address=0,
                value=value,
                byte_order="little",
                word_order="low",
            )
            read_value = client.read_float32(
                slave_id=1,
                start_address=0,
                byte_order="little",
                word_order="low"
            )
            print(f"   Little/Low: 写入 {value}, 读取 {read_value}")

    except Exception as e:
        print(f"高级操作失败: {e}")


def main():
    """主函数"""
    # 设置日志
    ModbusLogger.setup_logging(
        level=logging.INFO,
        enable_debug=True
    )

    set_language(Language.CN)

    print("=== ModbusLink 同步RTU客户端示例 ===")

    # RTU配置
    rtu_config = {
        "port": "COM10",  # Windows
        # "port": "/dev/ttyUSB0",   # Linux
        # "port": "/dev/tty.usbserial-0001",  # macOS
        "baudrate": 9600,
        "bytesize": 8,
        "parity": "N",
        "stopbits": 1,
        "timeout": 1,
    }

    # 创建RTU传输层
    transport = SyncRtuTransport(
        port=rtu_config["port"],
        baudrate=rtu_config["baudrate"],
        bytesize=rtu_config["bytesize"],
        parity=rtu_config["parity"],
        stopbits=rtu_config["stopbits"],
        timeout=rtu_config["timeout"]
    )

    # 创建RTU客户端
    client = SyncModbusClient(transport)

    print(f"RTU客户端配置:")
    print(f"  串口: {rtu_config['port']}")
    print(f"  波特率: {rtu_config['baudrate']}")
    print(f"  数据位: {rtu_config['bytesize']}")
    print(f"  停止位: {rtu_config['stopbits']}")
    print(f"  校验位: {rtu_config['parity']}")
    print(f"  注意: 需要一个Modbus RTU设备服务器\n")

    try:
        # 依次执行各个示例
        basic_operation_example(client)
        advanced_operation_example(client)

        print("\n=== 所有示例执行完成 ===")

    except KeyboardInterrupt:
        print("\n收到停止信号")
    except ConnectError as e:
        print(f"\n'ConnectError' 连接错误: {e}")
    except TimeOutError as e:
        print(f"\n'TimeOutError' 超时错误: {e}")
    except CrcError as e:
        print(f"\n'CrcError' CRC校验错误: {e}")
    except ModbusException as e:
        print(f"\n'ModbusException' Modbus协议异常: {e}")
    except Exception as e:
        print(f"\n其他错误错误: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    main()
