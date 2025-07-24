#!/usr/bin/env python3
"""ModbusLink TCP示例 TCP Example

演示如何使用ModbusLink库进行Modbus TCP通信，包括高级数据类型和日志功能。
Demonstrates how to use ModbusLink library for Modbus TCP communication, including advanced data types and logging features.
"""

import sys
import os

# 添加src目录到Python路径，以便导入modbuslink模块
# Add src directory to Python path to import modbuslink module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import time
import logging
from modbuslink import (
    ModbusClient, TcpTransport,
    ConnectionError, TimeoutError, InvalidResponseError, ModbusException
)
from modbuslink.utils.logging import ModbusLogger


def main():
    """TCP通信示例主函数 TCP communication example main function"""
    print("=== ModbusLink TCP示例 ModbusLink TCP Example ===")
    
    # 配置日志系统 Configure logging system
    ModbusLogger.setup_logging(
        level=logging.INFO,
        enable_debug=False  # 设置为True可查看详细的协议调试信息 Set to True to see detailed protocol debug info
    )
    
    # 如果需要查看原始数据包，可以启用协议调试 Enable protocol debug to see raw packets
    # ModbusLogger.enable_protocol_debug()
    
    # 配置TCP参数 Configure TCP parameters
    host = '192.168.1.100'  # 目标设备IP地址 Target device IP address
    port = 502              # Modbus TCP标准端口 Modbus TCP standard port
    timeout = 10.0          # 超时时间 Timeout duration
    slave_id = 1            # 单元标识符 Unit identifier
    
    print(f"TCP配置 TCP configuration: {host}:{port}, 超时 timeout: {timeout}秒 seconds")
    print(f"单元标识符 Unit identifier: {slave_id}")
    print()
    
    # 创建TCP传输层 Create TCP transport layer
    transport = TcpTransport(
        host=host,
        port=port,
        timeout=timeout
    )
    
    # 创建Modbus客户端 Create Modbus client
    client = ModbusClient(transport)
    
    try:
        # 使用上下文管理器自动管理连接 Use context manager to automatically manage connections
        with client:
            print("✓ TCP连接已建立 TCP connection established")
            
            # 示例1: 读取保持寄存器 Example 1: Read holding registers
            print("\n--- 示例1: 读取保持寄存器 Example 1: Read holding registers ---")
            try:
                registers = client.read_holding_registers(
                    slave_id=slave_id,
                    start_address=0,
                    quantity=10
                )
                print(f"保持寄存器 Holding registers [0-9]: {registers}")
                for i, value in enumerate(registers):
                    print(f"  寄存器 Register {i}: {value} (0x{value:04X})")
            except Exception as e:
                print(f"读取保持寄存器失败 Failed to read holding registers: {e}")
            
            # 示例2: 读取输入寄存器 Example 2: Read input registers
            print("\n--- 示例2: 读取输入寄存器 Example 2: Read input registers ---")
            try:
                registers = client.read_input_registers(
                    slave_id=slave_id,
                    start_address=0,
                    quantity=5
                )
                print(f"输入寄存器 Input registers [0-4]: {registers}")
                for i, value in enumerate(registers):
                    print(f"  输入寄存器 Input register {i}: {value} (0x{value:04X})")
            except Exception as e:
                print(f"读取输入寄存器失败 Failed to read input registers: {e}")
            
            # 示例3: 写单个寄存器 Example 3: Write single register
            print("\n--- 示例3: 写单个寄存器 Example 3: Write single register ---")
            try:
                test_value = 5678
                client.write_single_register(
                    slave_id=slave_id,
                    address=0,
                    value=test_value
                )
                print(f"✓ 成功写入寄存器0 Successfully wrote to register 0: {test_value}")
                
                # 读回验证 Read back verification
                registers = client.read_holding_registers(
                    slave_id=slave_id,
                    start_address=0,
                    quantity=1
                )
                print(f"验证读取 Verification read: {registers[0]}")
            except Exception as e:
                print(f"写单个寄存器失败 Failed to write single register: {e}")
            
            # 示例4: 读取离散输入 Example 4: Read discrete inputs
            print("\n--- 示例4: 读取离散输入 Example 4: Read discrete inputs ---")
            try:
                inputs = client.read_discrete_inputs(
                    slave_id=slave_id,
                    start_address=0,
                    quantity=16
                )
                print(f"离散输入 Discrete inputs [0-15]: {inputs}")
                for i, state in enumerate(inputs):
                    status = "ON" if state else "OFF"
                    print(f"  输入 Input {i}: {status}")
            except Exception as e:
                print(f"读取离散输入失败 Failed to read discrete inputs: {e}")
            
            # 示例5: 写多个寄存器 Example 5: Write multiple registers
            print("\n--- 示例5: 写多个寄存器 Example 5: Write multiple registers ---")
            try:
                values = [1000, 2000, 3000, 4000, 5000]
                client.write_multiple_registers(
                    slave_id=slave_id,
                    start_address=10,
                    values=values
                )
                print(f"✓ 成功写入多个寄存器 Successfully wrote multiple registers: {values}")
                
                # 读回验证 Read back verification
                registers = client.read_holding_registers(
                    slave_id=slave_id,
                    start_address=10,
                    quantity=len(values)
                )
                print(f"验证读取 Verification read: {registers}")
            except Exception as e:
                print(f"写多个寄存器失败 Failed to write multiple registers: {e}")
            
            # 示例6: 读取和写入线圈 Example 6: Read and write coils
            print("\n--- 示例6: 线圈操作 Example 6: Coil operations ---")
            try:
                # 读取线圈状态 Read coil status
                coils = client.read_coils(
                    slave_id=slave_id,
                    start_address=0,
                    quantity=8
                )
                print(f"当前线圈状态 Current coil status [0-7]: {coils}")
                
                # 写单个线圈 Write single coil
                client.write_single_coil(
                    slave_id=slave_id,
                    address=0,
                    value=True
                )
                print("✓ 设置线圈0为ON Set coil 0 to ON")
                
                # 写多个线圈 Write multiple coils
                coil_values = [True, False, True, False, True, False, True, False]
                client.write_multiple_coils(
                    slave_id=slave_id,
                    start_address=0,
                    values=coil_values
                )
                print(f"✓ 设置多个线圈 Set multiple coils: {coil_values}")
                
                # 读回验证 Read back verification
                coils = client.read_coils(
                    slave_id=slave_id,
                    start_address=0,
                    quantity=8
                )
                print(f"验证读取 Verification read: {coils}")
            except Exception as e:
                print(f"线圈操作失败 Coil operation failed: {e}")
            
            # 示例7: 模拟温度传感器读取 Example 7: Simulated temperature sensor reading
            print("\n--- 示例7: 模拟温度传感器读取 Example 7: Simulated temperature sensor reading ---")
            try:
                # 假设寄存器100存储温度值（放大100倍的整数）
                # Assume register 100 stores temperature value (integer scaled by 100)
                temp_registers = client.read_input_registers(
                    slave_id=slave_id,
                    start_address=100,
                    quantity=1
                )
                if temp_registers:
                    # 将整数值转换为浮点温度值 Convert integer value to floating point temperature
                    temperature = temp_registers[0] / 100.0
                    print(f"温度传感器读数 Temperature sensor reading: {temperature:.2f}°C")
                    
                    if temperature > 30.0:
                        print("⚠️  温度过高警告！ High temperature warning!")
                    elif temperature < 0.0:
                        print("❄️  温度过低警告！ Low temperature warning!")
                    else:
                        print("✓ 温度正常 Temperature normal")
            except Exception as e:
                print(f"读取温度传感器失败 Failed to read temperature sensor: {e}")
            
            # 示例8: 高级数据类型操作 Example 8: Advanced data type operations
            print("\n--- 示例8: 高级数据类型操作 Example 8: Advanced data type operations ---")
            try:
                # 写入32位浮点数 Write 32-bit float
                temperature_setpoint = 25.6
                client.write_float32(
                    slave_id=slave_id,
                    start_address=200,
                    value=temperature_setpoint
                )
                print(f"✓ 写入32位浮点数 Wrote 32-bit float: {temperature_setpoint}°C")
                
                # 读取32位浮点数 Read 32-bit float
                read_temperature = client.read_float32(
                    slave_id=slave_id,
                    start_address=200
                )
                print(f"读取32位浮点数 Read 32-bit float: {read_temperature:.2f}°C")
                
                # 写入32位整数 Write 32-bit integer
                counter_value = 123456789
                client.write_int32(
                    slave_id=slave_id,
                    start_address=202,
                    value=counter_value
                )
                print(f"✓ 写入32位整数 Wrote 32-bit integer: {counter_value}")
                
                # 读取32位整数 Read 32-bit integer
                read_counter = client.read_int32(
                    slave_id=slave_id,
                    start_address=202
                )
                print(f"读取32位整数 Read 32-bit integer: {read_counter}")
                
                # 写入字符串 Write string
                device_name = "ModbusLink"
                client.write_string(
                    slave_id=slave_id,
                    start_address=210,
                    value=device_name
                )
                print(f"✓ 写入字符串 Wrote string: '{device_name}'")
                
                # 读取字符串 Read string
                read_name = client.read_string(
                    slave_id=slave_id,
                    start_address=210,
                    length=len(device_name.encode('utf-8'))
                )
                print(f"读取字符串 Read string: '{read_name}'")
                
                # 演示不同字节序和字序 Demonstrate different byte and word orders
                print("\n字节序和字序演示 Byte and word order demonstration:")
                test_float = 3.14159
                
                # 大端字节序，高字在前 Big endian, high word first
                client.write_float32(slave_id, 220, test_float, 'big', 'high')
                read_val1 = client.read_float32(slave_id, 220, 'big', 'high')
                print(f"  大端高字序 Big endian high word: {read_val1:.5f}")
                
                # 小端字节序，低字在前 Little endian, low word first
                client.write_float32(slave_id, 222, test_float, 'little', 'low')
                read_val2 = client.read_float32(slave_id, 222, 'little', 'low')
                print(f"  小端低字序 Little endian low word: {read_val2:.5f}")
                
            except Exception as e:
                print(f"高级数据类型操作失败 Advanced data type operation failed: {e}")
            
            print("\n✓ 所有示例执行完成 All examples completed")
    
    except ConnectionError as e:
        print(f"❌ 连接错误 Connection error: {e}")
        print("请检查 Please check:")
        print(f"  - 目标设备 Target device {host}:{port} 是否可达 is reachable")
        print("  - 网络连接是否正常 Network connection is normal")
        print("  - 防火墙是否阻止连接 Firewall is blocking connection")
        print("  - 设备是否支持Modbus TCP协议 Device supports Modbus TCP protocol")
    
    except TimeoutError as e:
        print(f"❌ 超时错误 Timeout error: {e}")
        print("请检查 Please check:")
        print("  - 网络延迟是否过高 Network latency is too high")
        print("  - 设备响应是否正常 Device response is normal")
        print("  - 超时设置是否合理 Timeout setting is reasonable")
    
    except InvalidResponseError as e:
        print(f"❌ 响应格式错误 Invalid response format: {e}")
        print("请检查 Please check:")
        print("  - 设备是否正确实现Modbus TCP协议 Device correctly implements Modbus TCP protocol")
        print("  - 网络传输是否有数据损坏 Network transmission has data corruption")
    
    except ModbusException as e:
        print(f"❌ Modbus协议异常 Modbus protocol exception: {e}")
        print("请检查 Please check:")
        print("  - 单元标识符是否正确 Unit identifier is correct")
        print("  - 寄存器地址是否有效 Register address is valid")
        print("  - 设备是否支持请求的功能码 Device supports the requested function code")
    
    except Exception as e:
        print(f"❌ 未知错误 Unknown error: {e}")
    
    print("\n=== 示例结束 Example End ===")


if __name__ == '__main__':
    main()