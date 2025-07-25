#!/usr/bin/env python3
"""ModbusLink 从站模拟器示例


ModbusLink Slave Simulator Example

演示如何使用ModbusSlave类创建Modbus从站模拟器，
支持TCP和RTU模式，用于测试客户端功能。


Demonstrates how to use ModbusSlave class to create Modbus slave simulator,
supports TCP and RTU modes for testing client functionality.
"""

import time
import logging
import threading
from modbuslink import ModbusSlave, DataStore

# 配置日志 | Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def tcp_slave_example():
    """TCP从站模拟器示例 | TCP slave simulator example"""
    print("\n=== TCP从站模拟器示例 | TCP Slave Simulator Example ===")
    
    # 创建数据存储区 | Create data store
    data_store = DataStore()
    
    # 预设一些初始数据 | Preset some initial data
    print("\n设置初始数据 | Setting initial data...")
    
    # 设置线圈初始状态 | Set initial coil status
    data_store.set_coils(0, [True, False, True, False, True, False, True, False])
    print("   线圈0-7 | Coils 0-7: [True, False, True, False, True, False, True, False]")
    
    # 设置离散输入初始状态 | Set initial discrete input status
    data_store.set_discrete_inputs(0, [False, True, False, True, False, True, False, True])
    print("   离散输入0-7 | Discrete inputs 0-7: [False, True, False, True, False, True, False, True]")
    
    # 设置保持寄存器初始值 | Set initial holding register values
    data_store.set_holding_registers(0, [1000, 2000, 3000, 4000, 5000])
    print("   保持寄存器0-4 | Holding registers 0-4: [1000, 2000, 3000, 4000, 5000]")
    
    # 设置输入寄存器初始值 | Set initial input register values
    data_store.set_input_registers(0, [100, 200, 300, 400, 500])
    print("   输入寄存器0-4 | Input registers 0-4: [100, 200, 300, 400, 500]")
    
    # 创建从站模拟器 | Create slave simulator
    slave = ModbusSlave(slave_id=1, data_store=data_store)
    
    try:
        # 启动TCP服务器 | Start TCP server
        print("\n启动TCP从站服务器 | Starting TCP slave server...")
        slave.start_tcp_server(host='127.0.0.1', port=502)
        print("TCP从站服务器已启动，监听 127.0.0.1:502")
        print("TCP slave server started, listening on 127.0.0.1:502")
        
        print("\n现在你可以使用客户端连接到此从站：")
        print("Now you can use a client to connect to this slave:")
        print("\n  from modbuslink import ModbusClient, TcpTransport")
        print("  transport = TcpTransport('127.0.0.1', 502)")
        print("  client = ModbusClient(transport)")
        print("  with client:")
        print("      registers = client.read_holding_registers(1, 0, 5)")
        print("      print(registers)  # [1000, 2000, 3000, 4000, 5000]")
        
        print("\n或者运行异步客户端示例：")
        print("Or run the async client example:")
        print("  python examples/async_tcp_example.py")
        
        print("\n按Ctrl+C停止服务器 | Press Ctrl+C to stop server")
        
        # 模拟数据变化 | Simulate data changes
        def simulate_data_changes():
            """模拟数据变化 | Simulate data changes"""
            counter = 0
            while True:
                try:
                    time.sleep(5)  # 每5秒更新一次 | Update every 5 seconds
                    counter += 1
                    
                    # 更新输入寄存器（模拟传感器数据） | Update input registers (simulate sensor data)
                    sensor_values = [100 + counter, 200 + counter * 2, 300 + counter * 3, 400 + counter * 4, 500 + counter * 5]
                    data_store.set_input_registers(0, sensor_values)
                    print(f"\n[数据更新] 输入寄存器更新为 | [Data Update] Input registers updated to: {sensor_values}")
                    
                    # 切换一些线圈状态 | Toggle some coil status
                    current_coils = data_store.get_coils(0, 8)
                    current_coils[0] = not current_coils[0]  # 切换第一个线圈 | Toggle first coil
                    current_coils[7] = not current_coils[7]  # 切换最后一个线圈 | Toggle last coil
                    data_store.set_coils(0, current_coils)
                    print(f"[数据更新] 线圈状态更新为 | [Data Update] Coil status updated to: {current_coils}")
                    
                except Exception as e:
                    print(f"数据模拟错误 | Data simulation error: {e}")
                    break
        
        # 启动数据模拟线程 | Start data simulation thread
        sim_thread = threading.Thread(target=simulate_data_changes, daemon=True)
        sim_thread.start()
        
        # 保持服务器运行 | Keep server running
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\n收到中断信号，正在停止服务器... | Received interrupt signal, stopping server...")
    except Exception as e:
        print(f"\n服务器错误 | Server error: {e}")
    finally:
        slave.stop()
        print("TCP从站服务器已停止 | TCP slave server stopped")


def rtu_slave_example():
    """RTU从站模拟器示例 | RTU slave simulator example"""
    print("\n=== RTU从站模拟器示例 | RTU Slave Simulator Example ===")
    
    # 注意：此示例需要真实的串口设备或虚拟串口
    # Note: This example requires real serial device or virtual serial port
    print("\n注意：此示例需要真实的串口设备或虚拟串口")
    print("Note: This example requires real serial device or virtual serial port")
    print("\n在Windows上，你可以使用com0com创建虚拟串口对")
    print("On Windows, you can use com0com to create virtual serial port pairs")
    print("\n在Linux上，你可以使用socat创建虚拟串口对：")
    print("On Linux, you can use socat to create virtual serial port pairs:")
    print("  socat -d -d pty,raw,echo=0 pty,raw,echo=0")
    
    # 串口配置 | Serial port configuration
    port = input("\n请输入串口名称 (例如: COM1, /dev/ttyUSB0) | Enter serial port name (e.g., COM1, /dev/ttyUSB0): ").strip()
    
    if not port:
        print("未输入串口名称，跳过RTU示例 | No serial port entered, skipping RTU example")
        return
    
    # 创建数据存储区 | Create data store
    data_store = DataStore()
    
    # 设置一些初始数据 | Set some initial data
    data_store.set_holding_registers(0, [100, 200, 300, 400, 500])
    data_store.set_coils(0, [True, False, True, False])
    
    # 创建从站模拟器 | Create slave simulator
    slave = ModbusSlave(slave_id=1, data_store=data_store)
    
    try:
        # 启动RTU服务器 | Start RTU server
        print(f"\n启动RTU从站服务器，串口: {port} | Starting RTU slave server, serial port: {port}")
        slave.start_rtu_server(
            port=port,
            baudrate=9600,
            bytesize=8,
            parity='N',
            stopbits=1
        )
        print(f"RTU从站服务器已启动 | RTU slave server started")
        
        print("\n现在你可以使用RTU客户端连接到此从站：")
        print("Now you can use RTU client to connect to this slave:")
        print("\n  from modbuslink import ModbusClient, RtuTransport")
        print(f"  transport = RtuTransport('{port}', 9600)")
        print("  client = ModbusClient(transport)")
        print("  with client:")
        print("      registers = client.read_holding_registers(1, 0, 5)")
        print("      print(registers)  # [100, 200, 300, 400, 500]")
        
        print("\n按Ctrl+C停止服务器 | Press Ctrl+C to stop server")
        
        # 保持服务器运行 | Keep server running
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\n收到中断信号，正在停止服务器... | Received interrupt signal, stopping server...")
    except Exception as e:
        print(f"\n服务器错误 | Server error: {e}")
    finally:
        slave.stop()
        print("RTU从站服务器已停止 | RTU slave server stopped")


def data_store_example():
    """数据存储区操作示例 | Data store operations example"""
    print("\n=== 数据存储区操作示例 | Data Store Operations Example ===")
    
    # 创建数据存储区 | Create data store
    data_store = DataStore()
    
    print("\n1. 线圈操作 | Coil operations:")
    # 设置线圈 | Set coils
    coil_values = [True, False, True, False, True]
    data_store.set_coils(0, coil_values)
    print(f"   设置线圈0-4 | Set coils 0-4: {coil_values}")
    
    # 读取线圈 | Read coils
    read_coils = data_store.get_coils(0, 8)
    print(f"   读取线圈0-7 | Read coils 0-7: {read_coils}")
    
    print("\n2. 离散输入操作 | Discrete input operations:")
    # 设置离散输入 | Set discrete inputs
    input_values = [False, True, False, True]
    data_store.set_discrete_inputs(10, input_values)
    print(f"   设置离散输入10-13 | Set discrete inputs 10-13: {input_values}")
    
    # 读取离散输入 | Read discrete inputs
    read_inputs = data_store.get_discrete_inputs(10, 6)
    print(f"   读取离散输入10-15 | Read discrete inputs 10-15: {read_inputs}")
    
    print("\n3. 保持寄存器操作 | Holding register operations:")
    # 设置保持寄存器 | Set holding registers
    register_values = [1000, 2000, 3000, 4000, 5000]
    data_store.set_holding_registers(100, register_values)
    print(f"   设置保持寄存器100-104 | Set holding registers 100-104: {register_values}")
    
    # 读取保持寄存器 | Read holding registers
    read_registers = data_store.get_holding_registers(100, 8)
    print(f"   读取保持寄存器100-107 | Read holding registers 100-107: {read_registers}")
    
    print("\n4. 输入寄存器操作 | Input register operations:")
    # 设置输入寄存器 | Set input registers
    input_register_values = [500, 600, 700]
    data_store.set_input_registers(200, input_register_values)
    print(f"   设置输入寄存器200-202 | Set input registers 200-202: {input_register_values}")
    
    # 读取输入寄存器 | Read input registers
    read_input_registers = data_store.get_input_registers(200, 5)
    print(f"   读取输入寄存器200-204 | Read input registers 200-204: {read_input_registers}")
    
    print("\n数据存储区操作完成 | Data store operations completed")


def main():
    """主函数 | Main function"""
    print("ModbusLink 从站模拟器示例 | ModbusLink Slave Simulator Example")
    print("=" * 60)
    
    while True:
        print("\n请选择示例 | Please select an example:")
        print("1. TCP从站模拟器 | TCP Slave Simulator")
        print("2. RTU从站模拟器 | RTU Slave Simulator")
        print("3. 数据存储区操作 | Data Store Operations")
        print("4. 退出 | Exit")
        
        choice = input("\n输入选择 (1-4) | Enter choice (1-4): ").strip()
        
        if choice == '1':
            tcp_slave_example()
        elif choice == '2':
            rtu_slave_example()
        elif choice == '3':
            data_store_example()
        elif choice == '4':
            print("\n再见！| Goodbye!")
            break
        else:
            print("\n无效选择，请重试 | Invalid choice, please try again")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n用户中断 | User interrupted")
    except Exception as e:
        print(f"\n程序错误 | Program error: {e}")
        import traceback
        traceback.print_exc()