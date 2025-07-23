#!/usr/bin/env python3
"""ModbusLink TCP使用示例 ModbusLink TCP Usage Example

演示如何使用ModbusLink库进行TCP通信。
Demonstrates how to use the ModbusLink library for TCP communication.
"""

import sys
import os

# 添加src目录到Python路径，以便导入modbuslink模块
# Add src directory to Python path to import modbuslink module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from modbuslink import (
    ModbusClient, TcpTransport,
    ConnectionError, TimeoutError, InvalidResponseError, ModbusException
)


def main():
    """TCP通信示例主函数 TCP communication example main function"""
    print("=== ModbusLink TCP示例 ModbusLink TCP Example ===")
    
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