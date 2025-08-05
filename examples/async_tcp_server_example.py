#!/usr/bin/env python3
"""ModbusLink 异步TCP服务器示例
演示如何创建和使用异步Modbus TCP服务器。

ModbusLink Async TCP Server Example
Demonstrates how to create and use async Modbus TCP server.
"""

import asyncio
import logging
from modbuslink import AsyncTcpModbusServer, ModbusDataStore
from modbuslink.utils.logging import ModbusLogger


async def setup_data_store(data_store: ModbusDataStore) -> None:
    """
    设置数据存储的初始值
    
    Setup Initial Values for Data Store
    
    Args:
        data_store: 数据存储实例 | Data store instance
    """
    # 设置一些初始的线圈值 | Set some initial coil values
    data_store.write_coils(0, [True, False, True, False, True, False, True, False])
    
    # 设置一些初始的保持寄存器值 | Set some initial holding register values
    data_store.write_holding_registers(0, [100, 200, 300, 400, 500])
    data_store.write_holding_registers(10, [1000, 2000, 3000, 4000, 5000])
    
    # 设置一些初始的输入寄存器值（模拟传感器数据） | Set some initial input register values (simulate sensor data)
    data_store.write_input_registers(0, [250, 251, 252, 253, 254])  # 温度传感器 | Temperature sensors
    data_store.write_input_registers(10, [1013, 1014, 1015, 1016, 1017])  # 压力传感器 | Pressure sensors
    
    # 设置一些初始的离散输入值 | Set some initial discrete input values
    data_store.write_discrete_inputs(0, [False, True, False, True, False, True, False, True])
    
    print("数据存储初始化完成 | Data store initialized")
    print(f"线圈 0-7: {data_store.read_coils(0, 8)} | Coils 0-7: {data_store.read_coils(0, 8)}")
    print(f"保持寄存器 0-4: {data_store.read_holding_registers(0, 5)} | Holding registers 0-4: {data_store.read_holding_registers(0, 5)}")
    print(f"输入寄存器 0-4: {data_store.read_input_registers(0, 5)} | Input registers 0-4: {data_store.read_input_registers(0, 5)}")
    print(f"离散输入 0-7: {data_store.read_discrete_inputs(0, 8)} | Discrete inputs 0-7: {data_store.read_discrete_inputs(0, 8)}")


async def simulate_sensor_data(data_store: ModbusDataStore) -> None:
    """
    模拟传感器数据更新
    
    Simulate Sensor Data Updates
    
    Args:
        data_store: 数据存储实例 | Data store instance
    """
    import random
    
    counter = 0
    while True:
        try:
            # 模拟温度传感器数据变化 | Simulate temperature sensor data changes
            temperatures = [random.randint(200, 300) for _ in range(5)]
            data_store.write_input_registers(0, temperatures)
            
            # 模拟压力传感器数据变化 | Simulate pressure sensor data changes
            pressures = [random.randint(1000, 1100) for _ in range(5)]
            data_store.write_input_registers(10, pressures)
            
            # 模拟离散输入状态变化 | Simulate discrete input status changes
            discrete_states = [random.choice([True, False]) for _ in range(8)]
            data_store.write_discrete_inputs(0, discrete_states)
            
            # 更新计数器 | Update counter
            counter += 1
            data_store.write_holding_registers(100, [counter])
            
            if counter % 10 == 0:
                print(f"传感器数据更新 #{counter} | Sensor data update #{counter}")
                print(f"  温度: {temperatures} | Temperature: {temperatures}")
                print(f"  压力: {pressures} | Pressure: {pressures}")
            
            await asyncio.sleep(1.0)  # 每秒更新一次 | Update every second
            
        except Exception as e:
            print(f"传感器数据模拟错误 | Sensor data simulation error: {e}")
            await asyncio.sleep(1.0)


async def monitor_server(server: AsyncTcpModbusServer) -> None:
    """
    监控服务器状态
    
    Monitor Server Status
    
    Args:
        server: TCP服务器实例 | TCP server instance
    """
    while True:
        try:
            if await server.is_running():
                client_count = server.get_connected_clients_count()
                print(f"服务器状态: 运行中, 连接的客户端数: {client_count} | Server status: Running, Connected clients: {client_count}")
            else:
                print("服务器状态: 已停止 | Server status: Stopped")
                break
            
            await asyncio.sleep(30.0)  # 每30秒检查一次 | Check every 30 seconds
            
        except Exception as e:
            print(f"服务器监控错误 | Server monitoring error: {e}")
            await asyncio.sleep(5.0)


async def main():
    """
    主函数 | Main Function
    """
    # 设置日志 | Setup logging
    ModbusLogger.setup_logging(
        level=logging.INFO,
        enable_debug=True
    )
    
    print("=== ModbusLink 异步TCP服务器示例 | ModbusLink Async TCP Server Example ===")
    print()
    
    # 创建数据存储 | Create data store
    data_store = ModbusDataStore(
        coils_size=1000,
        discrete_inputs_size=1000,
        holding_registers_size=1000,
        input_registers_size=1000
    )
    
    # 设置初始数据 | Setup initial data
    await setup_data_store(data_store)
    print()
    
    # 创建TCP服务器 | Create TCP server
    server = AsyncTcpModbusServer(
        host="localhost",
        port=5020,  # 使用非标准端口避免冲突 | Use non-standard port to avoid conflicts
        data_store=data_store,
        slave_id=1,
        max_connections=5
    )
    
    print(f"启动TCP服务器: localhost:5020 | Starting TCP server: localhost:5020")
    print("从站地址: 1 | Slave address: 1")
    print("最大连接数: 5 | Max connections: 5")
    print()
    
    try:
        # 启动服务器 | Start server
        await server.start()
        print("TCP服务器启动成功! | TCP server started successfully!")
        print()
        print("可以使用以下方式连接服务器: | You can connect to the server using:")
        print("  - ModbusLink客户端 | ModbusLink client")
        print("  - 其他Modbus TCP客户端工具 | Other Modbus TCP client tools")
        print("  - 地址: localhost:5020 | Address: localhost:5020")
        print()
        print("按 Ctrl+C 停止服务器 | Press Ctrl+C to stop the server")
        print()
        
        # 启动后台任务 | Start background tasks
        tasks = [
            asyncio.create_task(simulate_sensor_data(data_store)),
            asyncio.create_task(monitor_server(server)),
            asyncio.create_task(server.serve_forever())
        ]
        
        # 等待任务完成 | Wait for tasks to complete
        await asyncio.gather(*tasks)
        
    except KeyboardInterrupt:
        print("\n收到停止信号 | Received stop signal")
    except Exception as e:
        print(f"\n服务器运行错误 | Server running error: {e}")
    finally:
        print("正在停止服务器... | Stopping server...")
        await server.stop()
        print("服务器已停止 | Server stopped")


if __name__ == "__main__":
    # 运行示例 | Run example
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n程序被用户中断 | Program interrupted by user")
    except Exception as e:
        print(f"\n程序运行错误 | Program running error: {e}")