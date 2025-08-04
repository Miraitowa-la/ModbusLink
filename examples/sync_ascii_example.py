"""
ModbusLink 同步ASCII客户端示例
演示如何使用同步ASCII传输层进行Modbus通信，
包括基本的读写操作、高级数据类型操作和错误处理。

ModbusLink Sync ASCII Client Example
Demonstrates how to use sync ASCII transport for Modbus communication,
including basic read/write operations, advanced data type operations and error handling.
"""

import logging
import time
from modbuslink import (
    ModbusClient,
    AsciiTransport,
    ConnectionError,
    TimeoutError,
    ModbusException,
)

# 配置日志 | Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


def basic_operations_example():
    """基本操作示例 | Basic operations example"""
    print("\n=== 同步ASCII基本操作示例 | Sync ASCII Basic Operations Example ===")

    # 创建ASCII传输层 | Create ASCII transport
    transport = AsciiTransport(
        port="COM1",  # Windows: COM1, Linux: /dev/ttyUSB0
        baudrate=9600,
        bytesize=7,
        parity="E",  # 偶校验 | Even parity
        timeout=2.0
    )

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

    except Exception as e:
        print(f"操作失败 | Operation failed: {e}")


def advanced_data_types_example():
    """高级数据类型示例 | Advanced data types example"""
    print("\n=== 同步ASCII高级数据类型示例 | Sync ASCII Advanced Data Types Example ===")

    transport = AsciiTransport(
        port="COM1",
        baudrate=9600,
        bytesize=7,
        parity="E",
        timeout=2.0
    )

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
            device_name = "ASCII_Device"
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


def debugging_example():
    """调试示例 - ASCII协议的优势 | Debugging example - ASCII protocol advantages"""
    print("\n=== 同步ASCII调试示例 | Sync ASCII Debugging Example ===")
    print("ASCII协议的优势：可读性强，便于调试和监控 | ASCII protocol advantages: High readability, easy debugging and monitoring")

    transport = AsciiTransport(
        port="COM1",
        baudrate=9600,
        bytesize=7,
        parity="E",
        timeout=2.0
    )

    client = ModbusClient(transport)

    try:
        with client:
            print("\n演示ASCII协议的可读性... | Demonstrating ASCII protocol readability...")
            
            # 启用协议级调试（可选）| Enable protocol-level debugging (optional)
            # ModbusLogger.enable_protocol_debug()
            
            for i in range(3):
                # 读取寄存器 | Read registers
                registers = client.read_holding_registers(
                    slave_id=1, start_address=i, quantity=1
                )
                print(f"   第{i+1}次读取 | Reading #{i+1}: 寄存器{i} = {registers[0]}")
                
                # 写入寄存器 | Write register
                test_value = 1000 + i * 100
                client.write_single_register(slave_id=1, address=i, value=test_value)
                print(f"   第{i+1}次写入 | Writing #{i+1}: 寄存器{i} = {test_value}")
                
                time.sleep(0.5)

            print("\n注意：在串口监控工具中，你可以看到ASCII格式的可读数据帧")
            print("Note: In serial monitoring tools, you can see readable ASCII format data frames")
            print("例如读取命令可能显示为：:010300000001FA")
            print("Example read command might display as: :010300000001FA")

    except Exception as e:
        print(f"调试示例失败 | Debugging example failed: {e}")


def main():
    """主函数 | Main function"""
    print("ModbusLink 同步ASCII客户端示例 | ModbusLink Sync ASCII Client Example")
    print("=" * 60)

    print("\n注意：此示例需要一个连接到串口的Modbus ASCII设备")
    print("Note: This example requires a Modbus ASCII device connected to serial port")
    print("\nASCII协议特点 | ASCII Protocol Features:")
    print("  - 使用ASCII字符编码，便于调试 | Uses ASCII character encoding, easy to debug")
    print("  - LRC校验，简单可靠 | LRC checksum, simple and reliable")
    print("  - 数据帧可读性强 | Data frames are highly readable")
    print("  - 传输效率相对较低 | Transmission efficiency is relatively low")
    print("\n请修改串口参数以匹配您的设备：")
    print("Please modify serial port parameters to match your device:")
    print("  - port: COM1 (Windows) 或 /dev/ttyUSB0 (Linux)")
    print("  - baudrate: 9600")
    print("  - bytesize: 7")
    print("  - parity: E (偶校验)")
    print("  - slave_id: 1")

    try:
        # 依次执行各个示例 | Execute examples sequentially
        basic_operations_example()
        advanced_data_types_example()
        debugging_example()

        print("\n=== 所有示例执行完成 | All Examples Completed ===")

    except KeyboardInterrupt:
        print("\n用户中断 | User interrupted")
    except ConnectionError as e:
        print(f"\n❌ 连接错误 | Connection error: {e}")
        print("请检查 | Please check:")
        print("  - 串口是否存在且可用 | Serial port exists and is available")
        print("  - 串口是否被其他程序占用 | Serial port is not occupied by other programs")
        print("  - 串口参数是否正确 | Serial port parameters are correct")
        print("  - 设备是否支持ASCII协议 | Device supports ASCII protocol")
    except TimeoutError as e:
        print(f"\n❌ 超时错误 | Timeout error: {e}")
        print("请检查 | Please check:")
        print("  - Modbus设备是否已连接并正常工作 | Modbus device is connected and working properly")
        print("  - 串口线缆是否正常 | Serial cable is working properly")
        print("  - 波特率等参数是否与设备匹配 | Baud rate and other parameters match the device")
        print("  - ASCII协议参数是否正确 | ASCII protocol parameters are correct")
    except ModbusException as e:
        print(f"\n❌ Modbus协议异常 | Modbus protocol exception: {e}")
        print("请检查 | Please check:")
        print("  - 从站地址是否正确 | Slave address is correct")
        print("  - 寄存器地址是否有效 | Register address is valid")
        print("  - 设备是否支持请求的功能码 | Device supports the requested function code")
        print("  - LRC校验是否正确 | LRC checksum is correct")
    except Exception as e:
        print(f"\n❌ 未知错误 | Unknown error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()