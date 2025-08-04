#!/usr/bin/env python3
"""ModbusLink RTU使用示例 - 展示高级数据类型和日志功能 | ModbusLink RTU usage example - Demonstrating advanced data types and logging features

演示如何使用ModbusLink库进行RTU通信，包括：
Demonstrates how to use the ModbusLink library for RTU communication, including:
- 基本的 Modbus RTU 操作 | Basic Modbus RTU operations
- 高级数据类型（浮点数、整数、字符串）| Advanced data types (float, integer, string)
- 日志系统的使用 | Logging system usage
- 错误处理和异常管理 | Error handling and exception management
"""

import sys
import os
import logging
import time

# 添加src目录到Python路径，以便导入modbuslink模块 | Add src directory to Python path to import modbuslink module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from modbuslink import (
    ModbusClient,
    RtuTransport,
    ConnectionError,
    TimeoutError,
    CRCError,
    ModbusException,
)
from modbuslink.utils import ModbusLogger


def main():
    """RTU通信示例主函数 | RTU communication example main function"""
    # 配置日志系统 | Configure logging system
    ModbusLogger.setup_logging(
        level=logging.INFO,  # 设置日志级别 | Set log level
        enable_debug=True,  # 启用调试模式 | Enable debug mode
    )

    # 启用协议级调试（可选） | Enable protocol-level debugging (optional)
    # ModbusLogger.enable_protocol_debug()

    print(
        "=== ModbusLink RTU示例 - 高级数据类型和日志功能 | ModbusLink RTU Example - Advanced Data Types and Logging ==="
    )
    print("注意：请确保有可用的 Modbus RTU 设备连接到串口")
    print("Note: Please ensure a Modbus RTU device is connected to the serial port")

    # 配置串口参数 | Configure serial port parameters
    port = "COM1"  # Windows下的串口，Linux下可能是 '/dev/ttyUSB0' | Serial port on Windows, might be '/dev/ttyUSB0' on Linux
    baudrate = 9600
    timeout = 2.0
    slave_id = 1

    print(
        f"\n串口配置 | Serial port configuration: {port} @ {baudrate}bps, 超时 | timeout: {timeout}秒 | seconds"
    )
    print(f"从站地址 | Slave address: {slave_id}")
    print()

    # 创建RTU传输层 | Create RTU transport layer
    transport = RtuTransport(port=port, baudrate=baudrate, timeout=timeout)

    # 创建Modbus客户端 | Create Modbus client
    client = ModbusClient(transport)

    try:
        # 使用上下文管理器自动管理连接 | Use context manager to automatically manage connections
        with client:
            print("✓ RTU连接已建立 | RTU connection established")

            # 示例1: 读取保持寄存器 | Example 1: Read holding registers
            print("\n--- 示例1: 读取保持寄存器 | Example 1: Read Holding Registers ---")
            try:
                registers = client.read_holding_registers(
                    slave_id=slave_id, start_address=0, quantity=4
                )
                print(f"保持寄存器 | Holding registers [0-3]: {registers}")
                for i, value in enumerate(registers):
                    print(f"  寄存器 | Register {i}: {value} (0x{value:04X})")
            except Exception as e:
                print(f"读取保持寄存器失败 | Failed to read holding registers: {e}")

            # 示例2: 写单个寄存器 | Example 2: Write single register
            print("\n--- 示例2: 写单个寄存器 | Example 2: Write Single Register ---")
            try:
                test_value = 1234
                client.write_single_register(
                    slave_id=slave_id, address=0, value=test_value
                )
                print(
                    f"✓ 成功写入寄存器0 | Successfully wrote to register 0: {test_value}"
                )

                # 读回验证 | Read back for verification
                registers = client.read_holding_registers(
                    slave_id=slave_id, start_address=0, quantity=1
                )
                print(f"验证读取 | Verification read: {registers[0]}")
            except Exception as e:
                print(f"写单个寄存器失败 | Failed to write single register: {e}")

            # 示例3: 读取线圈状态 | Example 3: Read coil status
            print("\n--- 示例3: 读取线圈状态 | Example 3: Read Coil Status ---")
            try:
                coils = client.read_coils(
                    slave_id=slave_id, start_address=0, quantity=8
                )
                print(f"线圈状态 | Coil status [0-7]: {coils}")
                for i, state in enumerate(coils):
                    status = "ON" if state else "OFF"
                    print(f"  线圈 | Coil {i}: {status}")
            except Exception as e:
                print(f"读取线圈状态失败 | Failed to read coil status: {e}")

            # 示例4: 写单个线圈 | Example 4: Write single coil
            print("\n--- 示例4: 写单个线圈 | Example 4: Write Single Coil ---")
            try:
                client.write_single_coil(slave_id=slave_id, address=0, value=True)
                print("✓ 成功设置线圈0为ON | Successfully set coil 0 to ON")

                # 读回验证 | Read back for verification
                coils = client.read_coils(
                    slave_id=slave_id, start_address=0, quantity=1
                )
                status = "ON" if coils[0] else "OFF"
                print(f"验证读取 | Verification read: 线圈 | Coil 0 = {status}")
            except Exception as e:
                print(f"写单个线圈失败 | Failed to write single coil: {e}")

            # 示例5: 写多个寄存器 | Example 5: Write multiple registers
            print("\n--- 示例5: 写多个寄存器 | Example 5: Write Multiple Registers ---")
            try:
                values = [100, 200, 300, 400]
                client.write_multiple_registers(
                    slave_id=slave_id, start_address=10, values=values
                )
                print(
                    f"✓ 成功写入多个寄存器 | Successfully wrote multiple registers: {values}"
                )

                # 读回验证 | Read back for verification
                registers = client.read_holding_registers(
                    slave_id=slave_id, start_address=10, quantity=len(values)
                )
                print(f"验证读取 | Verification read: {registers}")
            except Exception as e:
                print(f"写多个寄存器失败 | Failed to write multiple registers: {e}")

            # 示例6: 高级数据类型操作 | Example 6: Advanced data type operations
            print(
                "\n--- 示例6: 高级数据类型操作 | Example 6: Advanced Data Type Operations ---"
            )
            try:
                # 写入32位浮点数 | Write 32-bit float
                temperature_setpoint = 23.5
                client.write_float32(
                    slave_id=slave_id, start_address=100, value=temperature_setpoint
                )
                print(
                    f"✓ 写入32位浮点数 | Wrote 32-bit float: {temperature_setpoint}°C"
                )

                # 读取32位浮点数 | Read 32-bit float
                read_temperature = client.read_float32(
                    slave_id=slave_id, start_address=100
                )
                print(f"读取32位浮点数 | Read 32-bit float: {read_temperature:.2f}°C")

                # 写入32位整数 | Write 32-bit integer
                device_id = 987654321
                client.write_int32(
                    slave_id=slave_id, start_address=102, value=device_id
                )
                print(f"✓ 写入32位整数 | Wrote 32-bit integer: {device_id}")

                # 读取32位整数 | Read 32-bit integer
                read_device_id = client.read_int32(slave_id=slave_id, start_address=102)
                print(f"读取32位整数 | Read 32-bit integer: {read_device_id}")

                # 写入字符串 | Write string
                device_name = "RTU_Device"
                client.write_string(
                    slave_id=slave_id, start_address=110, value=device_name
                )
                print(f"✓ 写入字符串 | Wrote string: '{device_name}'")

                # 读取字符串 | Read string
                read_name = client.read_string(
                    slave_id=slave_id,
                    start_address=110,
                    length=len(device_name.encode("utf-8")),
                )
                print(f"读取字符串 | Read string: '{read_name}'")

                # 演示不同字节序和字序 | Demonstrate different byte and word orders
                print("\n字节序和字序演示 | Byte and word order demonstration:")
                test_float = 3.14159

                # 大端字节序，高字在前 | Big endian, high word first
                client.write_float32(slave_id, 120, test_float, "big", "high")
                read_val1 = client.read_float32(slave_id, 120, "big", "high")
                print(f"  大端高字序 | Big endian high word: {read_val1:.5f}")

                # 小端字节序，低字在前 | Little endian, low word first
                client.write_float32(slave_id, 122, test_float, "little", "low")
                read_val2 = client.read_float32(slave_id, 122, "little", "low")
                print(f"  小端低字序 | Little endian low word: {read_val2:.5f}")

            except Exception as e:
                print(
                    f"高级数据类型操作失败 | Advanced data type operation failed: {e}"
                )

            # 示例7: 模拟传感器数据读取 | Example 7: Simulated sensor data reading
            print(
                "\n--- 示例7: 模拟传感器数据读取 | Example 7: Simulated Sensor Data Reading ---"
            )
            try:
                print("连续读取传感器数据... | Continuously reading sensor data...")
                for i in range(3):
                    # 读取温度传感器（浮点数）| Read temperature sensor (float)
                    temp = client.read_float32(slave_id, 100)

                    # 读取湿度传感器（整数，需要除以100）| Read humidity sensor (integer, divide by 100)
                    humidity_raw = client.read_holding_registers(slave_id, 104, 1)[0]
                    humidity = humidity_raw / 100.0

                    # 读取设备状态（线圈）| Read device status (coil)
                    status = client.read_coils(slave_id, 0, 1)[0]

                    print(
                        f"  第{i+1}次读取 | Reading #{i+1}: 温度={temp:.1f}°C, 湿度={humidity:.1f}%, 状态={'运行' if status else '停止'}"
                    )

                    if i < 2:  # 最后一次不等待 | Don't wait on last iteration
                        time.sleep(1)

            except Exception as e:
                print(f"传感器数据读取失败 | Sensor data reading failed: {e}")

            print("\n✓ 所有示例执行完成 | All examples completed")

    except ConnectionError as e:
        print(f"❌ 连接错误 | Connection error: {e}")
        print("请检查 | Please check:")
        print(f"  - 串口 | Serial port {port} 是否存在且可用 | exists and is available")
        print(
            "  - 串口是否被其他程序占用 | Serial port is not occupied by other programs"
        )
        print("  - 串口参数是否正确 | Serial port parameters are correct")

    except TimeoutError as e:
        print(f"❌ 超时错误 | Timeout error: {e}")
        print("请检查 | Please check:")
        print(
            "  - Modbus设备是否已连接并正常工作 | Modbus device is connected and working properly"
        )
        print("  - 串口线缆是否正常 | Serial cable is working properly")
        print(
            "  - 波特率等参数是否与设备匹配 | Baud rate and other parameters match the device"
        )

    except CRCError as e:
        print(f"❌ CRC校验错误 | CRC verification error: {e}")
        print("请检查 | Please check:")
        print("  - 串口线缆是否有干扰 | Serial cable has interference")
        print("  - 波特率是否正确 | Baud rate is correct")
        print("  - 设备是否支持Modbus RTU协议 | Device supports Modbus RTU protocol")

    except ModbusException as e:
        print(f"❌ Modbus协议异常 | Modbus protocol exception: {e}")
        print("请检查 | Please check:")
        print("  - 从站地址是否正确 | Slave address is correct")
        print("  - 寄存器地址是否有效 | Register address is valid")
        print(
            "  - 设备是否支持请求的功能码 | Device supports the requested function code"
        )

    except Exception as e:
        print(f"❌ 未知错误 | Unknown error: {e}")

    print("\n=== 示例结束 | Example End ===")


if __name__ == "__main__":
    main()
