#!/usr/bin/env python3
"""ModbusLink 异步RTU服务器示例
演示如何创建和使用异步Modbus RTU服务器。

ModbusLink Async RTU Server Example
Demonstrates how to create and use async Modbus RTU server.
"""

import asyncio
import logging
from modbuslink import AsyncRtuModbusServer, ModbusDataStore
from modbuslink.utils.logging import ModbusLogger


async def setup_industrial_data(data_store: ModbusDataStore) -> None:
    """
    设置工业设备模拟数据
    
    Setup Industrial Equipment Simulation Data
    
    Args:
        data_store: 数据存储实例 | Data store instance
    """
    # 设备状态线圈 | Equipment status coils
    # 0-7: 电机状态 | Motor status
    # 8-15: 阀门状态 | Valve status
    # 16-23: 报警状态 | Alarm status
    data_store.write_coils(0, [True, False, True, True, False, False, True, False])  # 电机状态 | Motor status
    data_store.write_coils(8, [False, True, False, True, True, False, False, True])  # 阀门状态 | Valve status
    data_store.write_coils(16, [False, False, False, False, False, False, False, False])  # 报警状态 | Alarm status
    
    # 设备参数保持寄存器 | Equipment parameter holding registers
    # 0-9: 电机参数 | Motor parameters
    data_store.write_holding_registers(0, [1500, 2800, 3600, 1200, 750])  # 转速、扭矩、功率等 | Speed, torque, power, etc.
    data_store.write_holding_registers(5, [100, 85, 92, 78, 88])  # 效率、温度等 | Efficiency, temperature, etc.
    
    # 10-19: 工艺参数 | Process parameters
    data_store.write_holding_registers(10, [250, 180, 320, 450, 680])  # 温度设定值 | Temperature setpoints
    data_store.write_holding_registers(15, [1013, 1025, 998, 1045, 1002])  # 压力设定值 | Pressure setpoints
    
    # 传感器读数输入寄存器 | Sensor reading input registers
    # 0-9: 温度传感器 | Temperature sensors
    data_store.write_input_registers(0, [248, 179, 318, 447, 682])  # 实际温度值 | Actual temperature values
    data_store.write_input_registers(5, [251, 182, 322, 451, 685])  # 温度传感器2 | Temperature sensor 2
    
    # 10-19: 压力传感器 | Pressure sensors
    data_store.write_input_registers(10, [1015, 1027, 996, 1043, 1004])  # 实际压力值 | Actual pressure values
    data_store.write_input_registers(15, [1012, 1023, 999, 1047, 1001])  # 压力传感器2 | Pressure sensor 2
    
    # 20-29: 流量传感器 | Flow sensors
    data_store.write_input_registers(20, [125, 89, 156, 203, 178])  # 流量值 | Flow values
    
    # 数字输入状态 | Digital input status
    # 0-7: 限位开关 | Limit switches
    # 8-15: 安全开关 | Safety switches
    data_store.write_discrete_inputs(0, [True, False, True, True, False, True, False, True])  # 限位开关 | Limit switches
    data_store.write_discrete_inputs(8, [True, True, True, True, True, True, True, True])  # 安全开关 | Safety switches
    
    print("工业设备数据初始化完成 | Industrial equipment data initialized")
    print(f"电机状态线圈 0-7: {data_store.read_coils(0, 8)} | Motor status coils 0-7: {data_store.read_coils(0, 8)}")
    print(f"电机参数寄存器 0-4: {data_store.read_holding_registers(0, 5)} | Motor parameter registers 0-4: {data_store.read_holding_registers(0, 5)}")
    print(f"温度传感器 0-4: {data_store.read_input_registers(0, 5)} | Temperature sensors 0-4: {data_store.read_input_registers(0, 5)}")
    print(f"限位开关 0-7: {data_store.read_discrete_inputs(0, 8)} | Limit switches 0-7: {data_store.read_discrete_inputs(0, 8)}")


async def simulate_industrial_process(data_store: ModbusDataStore) -> None:
    """
    模拟工业过程数据变化
    
    Simulate Industrial Process Data Changes
    
    Args:
        data_store: 数据存储实例 | Data store instance
    """
    import random
    import math
    
    cycle_count = 0
    
    while True:
        try:
            cycle_count += 1
            
            # 模拟温度传感器数据波动 | Simulate temperature sensor data fluctuation
            base_temps = [248, 179, 318, 447, 682]
            temp_variations = [base + random.randint(-5, 5) + int(3 * math.sin(cycle_count * 0.1)) for base in base_temps]
            data_store.write_input_registers(0, temp_variations)
            
            # 模拟压力传感器数据波动 | Simulate pressure sensor data fluctuation
            base_pressures = [1015, 1027, 996, 1043, 1004]
            pressure_variations = [base + random.randint(-3, 3) + int(2 * math.cos(cycle_count * 0.15)) for base in base_pressures]
            data_store.write_input_registers(10, pressure_variations)
            
            # 模拟流量传感器数据 | Simulate flow sensor data
            base_flows = [125, 89, 156, 203, 178]
            flow_variations = [base + random.randint(-10, 10) + int(5 * math.sin(cycle_count * 0.2)) for base in base_flows]
            data_store.write_input_registers(20, flow_variations)
            
            # 模拟电机转速变化 | Simulate motor speed changes
            current_speeds = data_store.read_holding_registers(0, 5)
            new_speeds = [speed + random.randint(-50, 50) for speed in current_speeds]
            # 限制转速范围 | Limit speed range
            new_speeds = [max(500, min(4000, speed)) for speed in new_speeds]
            data_store.write_holding_registers(0, new_speeds)
            
            # 偶尔触发报警 | Occasionally trigger alarms
            if cycle_count % 50 == 0:
                # 随机触发一个报警 | Randomly trigger an alarm
                alarm_index = random.randint(16, 23)
                current_alarms = data_store.read_coils(16, 8)
                current_alarms[alarm_index - 16] = not current_alarms[alarm_index - 16]
                data_store.write_coils(16, current_alarms)
                print(f"报警状态变化 | Alarm status change: 线圈 {alarm_index} = {current_alarms[alarm_index - 16]} | Coil {alarm_index} = {current_alarms[alarm_index - 16]}")
            
            # 更新运行计数器 | Update running counter
            data_store.write_holding_registers(100, [cycle_count])
            
            if cycle_count % 20 == 0:
                print(f"工业过程模拟 #{cycle_count} | Industrial process simulation #{cycle_count}")
                print(f"  温度: {temp_variations} | Temperature: {temp_variations}")
                print(f"  压力: {pressure_variations} | Pressure: {pressure_variations}")
                print(f"  流量: {flow_variations} | Flow: {flow_variations}")
                print(f"  电机转速: {new_speeds} | Motor speeds: {new_speeds}")
            
            await asyncio.sleep(2.0)  # 每2秒更新一次 | Update every 2 seconds
            
        except Exception as e:
            print(f"工业过程模拟错误 | Industrial process simulation error: {e}")
            await asyncio.sleep(2.0)


async def monitor_rtu_server(server: AsyncRtuModbusServer) -> None:
    """
    监控RTU服务器状态
    
    Monitor RTU Server Status
    
    Args:
        server: RTU服务器实例 | RTU server instance
    """
    while True:
        try:
            if await server.is_running():
                print(f"RTU服务器状态: 运行中 | RTU server status: Running")
                print(f"串口: {server.port} | Serial port: {server.port}")
                print(f"波特率: {server.baudrate} | Baudrate: {server.baudrate}")
                print(f"从站地址: {server.slave_id} | Slave address: {server.slave_id}")
            else:
                print("RTU服务器状态: 已停止 | RTU server status: Stopped")
                break
            
            await asyncio.sleep(60.0)  # 每60秒检查一次 | Check every 60 seconds
            
        except Exception as e:
            print(f"RTU服务器监控错误 | RTU server monitoring error: {e}")
            await asyncio.sleep(10.0)


async def main():
    """
    主函数 | Main Function
    """
    # 设置日志 | Setup logging
    ModbusLogger.setup_logging(
        level=logging.INFO,
        enable_debug=True
    )
    
    print("=== ModbusLink 异步RTU服务器示例 | ModbusLink Async RTU Server Example ===")
    print()
    
    # 创建数据存储 | Create data store
    data_store = ModbusDataStore(
        coils_size=1000,
        discrete_inputs_size=1000,
        holding_registers_size=1000,
        input_registers_size=1000
    )
    
    # 设置工业设备数据 | Setup industrial equipment data
    await setup_industrial_data(data_store)
    print()
    
    # 串口配置 | Serial port configuration
    # 注意：请根据实际情况修改串口名称 | Note: Please modify the serial port name according to actual situation
    port = "COM3"  # Windows
    # port = "/dev/ttyUSB0"  # Linux
    # port = "/dev/tty.usbserial-0001"  # macOS
    
    # 创建RTU服务器 | Create RTU server
    server = AsyncRtuModbusServer(
        port=port,
        baudrate=9600,
        data_store=data_store,
        slave_id=1,
        parity="N",
        stopbits=1,
        bytesize=8,
        timeout=1.0
    )
    
    print(f"RTU服务器配置 | RTU server configuration:")
    print(f"  串口: {port} | Serial port: {port}")
    print(f"  波特率: 9600 | Baudrate: 9600")
    print(f"  数据位: 8 | Data bits: 8")
    print(f"  停止位: 1 | Stop bits: 1")
    print(f"  校验位: 无 | Parity: None")
    print(f"  从站地址: 1 | Slave address: 1")
    print(f"  超时: 1.0秒 | Timeout: 1.0 seconds")
    print()
    
    try:
        # 启动服务器 | Start server
        await server.start()
        print("RTU服务器启动成功! | RTU server started successfully!")
        print()
        print("可以使用以下方式连接服务器: | You can connect to the server using:")
        print("  - ModbusLink RTU客户端 | ModbusLink RTU client")
        print("  - 其他Modbus RTU主站设备 | Other Modbus RTU master devices")
        print(f"  - 串口: {port} | Serial port: {port}")
        print("  - 通信参数: 9600,8,N,1 | Communication parameters: 9600,8,N,1")
        print()
        print("按 Ctrl+C 停止服务器 | Press Ctrl+C to stop the server")
        print()
        
        # 启动后台任务 | Start background tasks
        tasks = [
            asyncio.create_task(simulate_industrial_process(data_store)),
            asyncio.create_task(monitor_rtu_server(server)),
            asyncio.create_task(server.serve_forever())
        ]
        
        # 等待任务完成 | Wait for tasks to complete
        await asyncio.gather(*tasks)
        
    except KeyboardInterrupt:
        print("\n收到停止信号 | Received stop signal")
    except Exception as e:
        print(f"\n服务器运行错误 | Server running error: {e}")
        if "could not open port" in str(e).lower():
            print(f"\n串口打开失败，请检查: | Serial port open failed, please check:")
            print(f"  1. 串口名称是否正确 ({port}) | 1. Serial port name is correct ({port})")
            print(f"  2. 串口是否被其他程序占用 | 2. Serial port is not occupied by other programs")
            print(f"  3. 串口设备是否已连接 | 3. Serial port device is connected")
            print(f"  4. 是否有串口访问权限 | 4. Have serial port access permission")
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