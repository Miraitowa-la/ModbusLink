#!/usr/bin/env python3
"""ModbusLink RTU使用示例 ModbusLink RTU usage example

演示如何使用ModbusLink库进行RTU通信。 Demonstrates how to use the ModbusLink library for RTU communication.
"""

import sys
import os

# 添加src目录到Python路径，以便导入modbuslink模块 Add src directory to Python path to import modbuslink module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from modbuslink import (
    ModbusClient, RtuTransport,
    ConnectionError, TimeoutError, CRCError, ModbusException
)


def main():
    """RTU通信示例主函数 RTU communication example main function"""
    print("=== ModbusLink RTU示例 ModbusLink RTU Example ===")
    
    # 配置串口参数 Configure serial port parameters
    port = 'COM1'  # Windows下的串口，Linux下可能是 '/dev/ttyUSB0' Serial port on Windows, might be '/dev/ttyUSB0' on Linux
    baudrate = 9600
    timeout = 2.0
    slave_id = 1
    
    print(f"串口配置 Serial port configuration: {port} @ {baudrate}bps, 超时 timeout: {timeout}秒 seconds")
    print(f"从站地址 Slave address: {slave_id}")
    print()
    
    # 创建RTU传输层 Create RTU transport layer
    transport = RtuTransport(
        port=port,
        baudrate=baudrate,
        timeout=timeout
    )
    
    # 创建Modbus客户端 Create Modbus client
    client = ModbusClient(transport)
    
    try:
        # 使用上下文管理器自动管理连接 Use context manager to automatically manage connections
        with client:
            print("✓ RTU连接已建立 RTU connection established")
            
            # 示例1: 读取保持寄存器 Example 1: Read holding registers
            print("\n--- 示例1: 读取保持寄存器 Example 1: Read Holding Registers ---")
            try:
                registers = client.read_holding_registers(
                    slave_id=slave_id,
                    start_address=0,
                    quantity=4
                )
                print(f"保持寄存器 Holding registers [0-3]: {registers}")
                for i, value in enumerate(registers):
                    print(f"  寄存器 Register {i}: {value} (0x{value:04X})")
            except Exception as e:
                print(f"读取保持寄存器失败 Failed to read holding registers: {e}")
            
            # 示例2: 写单个寄存器 Example 2: Write single register
            print("\n--- 示例2: 写单个寄存器 Example 2: Write Single Register ---")
            try:
                test_value = 1234
                client.write_single_register(
                    slave_id=slave_id,
                    address=0,
                    value=test_value
                )
                print(f"✓ 成功写入寄存器0 Successfully wrote to register 0: {test_value}")
                
                # 读回验证 Read back for verification
                registers = client.read_holding_registers(
                    slave_id=slave_id,
                    start_address=0,
                    quantity=1
                )
                print(f"验证读取 Verification read: {registers[0]}")
            except Exception as e:
                print(f"写单个寄存器失败 Failed to write single register: {e}")
            
            # 示例3: 读取线圈状态 Example 3: Read coil status
            print("\n--- 示例3: 读取线圈状态 Example 3: Read Coil Status ---")
            try:
                coils = client.read_coils(
                    slave_id=slave_id,
                    start_address=0,
                    quantity=8
                )
                print(f"线圈状态 Coil status [0-7]: {coils}")
                for i, state in enumerate(coils):
                    status = "ON" if state else "OFF"
                    print(f"  线圈 Coil {i}: {status}")
            except Exception as e:
                print(f"读取线圈状态失败 Failed to read coil status: {e}")
            
            # 示例4: 写单个线圈 Example 4: Write single coil
            print("\n--- 示例4: 写单个线圈 Example 4: Write Single Coil ---")
            try:
                client.write_single_coil(
                    slave_id=slave_id,
                    address=0,
                    value=True
                )
                print("✓ 成功设置线圈0为ON Successfully set coil 0 to ON")
                
                # 读回验证 Read back for verification
                coils = client.read_coils(
                    slave_id=slave_id,
                    start_address=0,
                    quantity=1
                )
                status = "ON" if coils[0] else "OFF"
                print(f"验证读取 Verification read: 线圈 Coil 0 = {status}")
            except Exception as e:
                print(f"写单个线圈失败 Failed to write single coil: {e}")
            
            # 示例5: 写多个寄存器 Example 5: Write multiple registers
            print("\n--- 示例5: 写多个寄存器 Example 5: Write Multiple Registers ---")
            try:
                values = [100, 200, 300, 400]
                client.write_multiple_registers(
                    slave_id=slave_id,
                    start_address=10,
                    values=values
                )
                print(f"✓ 成功写入多个寄存器 Successfully wrote multiple registers: {values}")
                
                # 读回验证 Read back for verification
                registers = client.read_holding_registers(
                    slave_id=slave_id,
                    start_address=10,
                    quantity=len(values)
                )
                print(f"验证读取 Verification read: {registers}")
            except Exception as e:
                print(f"写多个寄存器失败 Failed to write multiple registers: {e}")
            
            print("\n✓ 所有示例执行完成 All examples completed")
    
    except ConnectionError as e:
        print(f"❌ 连接错误 Connection error: {e}")
        print("请检查 Please check:")
        print(f"  - 串口 Serial port {port} 是否存在且可用 exists and is available")
        print("  - 串口是否被其他程序占用 Serial port is not occupied by other programs")
        print("  - 串口参数是否正确 Serial port parameters are correct")
    
    except TimeoutError as e:
        print(f"❌ 超时错误 Timeout error: {e}")
        print("请检查 Please check:")
        print("  - Modbus设备是否已连接并正常工作 Modbus device is connected and working properly")
        print("  - 串口线缆是否正常 Serial cable is working properly")
        print("  - 波特率等参数是否与设备匹配 Baud rate and other parameters match the device")
    
    except CRCError as e:
        print(f"❌ CRC校验错误 CRC verification error: {e}")
        print("请检查 Please check:")
        print("  - 串口线缆是否有干扰 Serial cable has interference")
        print("  - 波特率是否正确 Baud rate is correct")
        print("  - 设备是否支持Modbus RTU协议 Device supports Modbus RTU protocol")
    
    except ModbusException as e:
        print(f"❌ Modbus协议异常 Modbus protocol exception: {e}")
        print("请检查 Please check:")
        print("  - 从站地址是否正确 Slave address is correct")
        print("  - 寄存器地址是否有效 Register address is valid")
        print("  - 设备是否支持请求的功能码 Device supports the requested function code")
    
    except Exception as e:
        print(f"❌ 未知错误 Unknown error: {e}")
    
    print("\n=== 示例结束 Example End ===")


if __name__ == '__main__':
    main()