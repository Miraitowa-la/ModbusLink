#!/usr/bin/env python3
"""ModbusLink 异步ASCII服务器示例
演示如何创建和使用异步Modbus ASCII服务器。

ModbusLink Async ASCII Server Example
Demonstrates how to create and use async Modbus ASCII server.
"""

import asyncio
import logging
from modbuslink import AsyncAsciiModbusServer, ModbusDataStore
from modbuslink.utils.logging import ModbusLogger


async def setup_laboratory_data(data_store: ModbusDataStore) -> None:
    """
    设置实验室设备模拟数据
    
    Setup Laboratory Equipment Simulation Data
    
    Args:
        data_store: 数据存储实例 | Data store instance
    """
    # 实验室设备控制线圈 | Laboratory equipment control coils
    # 0-7: 加热器控制 | Heater control
    # 8-15: 风扇控制 | Fan control
    # 16-23: 泵控制 | Pump control
    # 24-31: 照明控制 | Lighting control
    data_store.write_coils(0, [False, True, False, True, False, False, True, False])  # 加热器 | Heaters
    data_store.write_coils(8, [True, True, False, False, True, True, False, False])  # 风扇 | Fans
    data_store.write_coils(16, [False, True, True, False, False, True, False, True])  # 泵 | Pumps
    data_store.write_coils(24, [True, True, True, True, False, False, False, False])  # 照明 | Lighting
    
    # 设备参数设置寄存器 | Equipment parameter setting registers
    # 0-9: 温度控制参数 | Temperature control parameters
    data_store.write_holding_registers(0, [250, 300, 180, 220, 350])  # 目标温度 | Target temperatures
    data_store.write_holding_registers(5, [5, 8, 3, 6, 10])  # 温度容差 | Temperature tolerance
    
    # 10-19: 时间控制参数 | Time control parameters
    data_store.write_holding_registers(10, [3600, 7200, 1800, 5400, 9000])  # 运行时间(秒) | Running time (seconds)
    data_store.write_holding_registers(15, [60, 120, 30, 90, 180])  # 采样间隔(秒) | Sampling interval (seconds)
    
    # 20-29: 速度控制参数 | Speed control parameters
    data_store.write_holding_registers(20, [1200, 1800, 800, 1500, 2000])  # 转速设定 | Speed settings
    data_store.write_holding_registers(25, [50, 75, 25, 60, 100])  # 速度百分比 | Speed percentage
    
    # 传感器测量值输入寄存器 | Sensor measurement input registers
    # 0-9: 温度传感器 | Temperature sensors
    data_store.write_input_registers(0, [248, 298, 178, 218, 348])  # 实际温度 | Actual temperatures
    data_store.write_input_registers(5, [252, 302, 182, 222, 352])  # 温度传感器2 | Temperature sensor 2
    
    # 10-19: 湿度传感器 | Humidity sensors
    data_store.write_input_registers(10, [45, 52, 38, 48, 55])  # 相对湿度% | Relative humidity %
    data_store.write_input_registers(15, [47, 54, 40, 50, 57])  # 湿度传感器2 | Humidity sensor 2
    
    # 20-29: pH传感器 | pH sensors
    data_store.write_input_registers(20, [700, 650, 720, 680, 710])  # pH值*100 | pH value * 100
    
    # 30-39: 压力传感器 | Pressure sensors
    data_store.write_input_registers(30, [1013, 1015, 1010, 1018, 1012])  # 大气压力 | Atmospheric pressure
    
    # 40-49: 转速反馈 | Speed feedback
    data_store.write_input_registers(40, [1198, 1795, 798, 1498, 1995])  # 实际转速 | Actual speed
    
    # 数字输入状态 | Digital input status
    # 0-7: 门开关状态 | Door switch status
    # 8-15: 安全开关 | Safety switches
    # 16-23: 液位开关 | Level switches
    # 24-31: 压力开关 | Pressure switches
    data_store.write_discrete_inputs(0, [False, True, False, False, True, True, False, True])  # 门开关 | Door switches
    data_store.write_discrete_inputs(8, [True, True, True, True, True, True, True, True])  # 安全开关 | Safety switches
    data_store.write_discrete_inputs(16, [False, False, True, True, False, True, True, False])  # 液位开关 | Level switches
    data_store.write_discrete_inputs(24, [True, False, True, False, True, False, True, False])  # 压力开关 | Pressure switches
    
    print("实验室设备数据初始化完成 | Laboratory equipment data initialized")
    print(f"加热器控制 0-7: {data_store.read_coils(0, 8)} | Heater control 0-7: {data_store.read_coils(0, 8)}")
    print(f"温度设定 0-4: {data_store.read_holding_registers(0, 5)} | Temperature settings 0-4: {data_store.read_holding_registers(0, 5)}")
    print(f"实际温度 0-4: {data_store.read_input_registers(0, 5)} | Actual temperatures 0-4: {data_store.read_input_registers(0, 5)}")
    print(f"门开关状态 0-7: {data_store.read_discrete_inputs(0, 8)} | Door switch status 0-7: {data_store.read_discrete_inputs(0, 8)}")


async def simulate_laboratory_experiment(data_store: ModbusDataStore) -> None:
    """
    模拟实验室实验过程
    
    Simulate Laboratory Experiment Process
    
    Args:
        data_store: 数据存储实例 | Data store instance
    """
    import random
    import math
    
    experiment_time = 0
    
    while True:
        try:
            experiment_time += 1
            
            # 模拟温度控制过程 | Simulate temperature control process
            target_temps = data_store.read_holding_registers(0, 5)
            current_temps = data_store.read_input_registers(0, 5)
            
            # 温度逐渐趋向目标值 | Temperature gradually approaches target value
            new_temps = []
            for i, (current, target) in enumerate(zip(current_temps, target_temps)):
                # 加入随机噪声和控制算法 | Add random noise and control algorithm
                diff = target - current
                change = diff * 0.1 + random.randint(-2, 2) + math.sin(experiment_time * 0.05) * 1
                new_temp = current + change
                new_temps.append(int(max(0, min(500, new_temp))))  # 限制温度范围 | Limit temperature range
            
            data_store.write_input_registers(0, new_temps)
            
            # 模拟湿度变化 | Simulate humidity changes
            base_humidity = [45, 52, 38, 48, 55]
            humidity_variations = [base + random.randint(-5, 5) + int(2 * math.cos(experiment_time * 0.08)) for base in base_humidity]
            humidity_variations = [max(0, min(100, h)) for h in humidity_variations]  # 限制湿度范围 | Limit humidity range
            data_store.write_input_registers(10, humidity_variations)
            
            # 模拟pH值变化 | Simulate pH value changes
            base_ph = [700, 650, 720, 680, 710]
            ph_variations = [base + random.randint(-10, 10) + int(3 * math.sin(experiment_time * 0.03)) for base in base_ph]
            ph_variations = [max(0, min(1400, ph)) for ph in ph_variations]  # 限制pH范围 | Limit pH range
            data_store.write_input_registers(20, ph_variations)
            
            # 模拟转速控制 | Simulate speed control
            target_speeds = data_store.read_holding_registers(20, 5)
            current_speeds = data_store.read_input_registers(40, 5)
            
            new_speeds = []
            for current, target in zip(current_speeds, target_speeds):
                diff = target - current
                change = diff * 0.15 + random.randint(-20, 20)
                new_speed = current + change
                new_speeds.append(int(max(0, min(3000, new_speed))))  # 限制转速范围 | Limit speed range
            
            data_store.write_input_registers(40, new_speeds)
            
            # 模拟压力变化 | Simulate pressure changes
            base_pressure = [1013, 1015, 1010, 1018, 1012]
            pressure_variations = [base + random.randint(-5, 5) + int(1 * math.sin(experiment_time * 0.02)) for base in base_pressure]
            data_store.write_input_registers(30, pressure_variations)
            
            # 随机改变一些开关状态 | Randomly change some switch states
            if experiment_time % 30 == 0:
                # 随机改变门开关状态 | Randomly change door switch status
                door_index = random.randint(0, 7)
                current_doors = data_store.read_discrete_inputs(0, 8)
                current_doors[door_index] = not current_doors[door_index]
                data_store.write_discrete_inputs(0, current_doors)
                print(f"门开关状态变化 | Door switch status change: 开关 {door_index} = {current_doors[door_index]} | Switch {door_index} = {current_doors[door_index]}")
            
            if experiment_time % 45 == 0:
                # 随机改变液位开关状态 | Randomly change level switch status
                level_index = random.randint(16, 23)
                current_levels = data_store.read_discrete_inputs(16, 8)
                current_levels[level_index - 16] = not current_levels[level_index - 16]
                data_store.write_discrete_inputs(16, current_levels)
                print(f"液位开关状态变化 | Level switch status change: 开关 {level_index} = {current_levels[level_index - 16]} | Switch {level_index} = {current_levels[level_index - 16]}")
            
            # 更新实验时间计数器 | Update experiment time counter
            data_store.write_holding_registers(100, [experiment_time])
            
            if experiment_time % 15 == 0:
                print(f"实验过程模拟 #{experiment_time} | Experiment process simulation #{experiment_time}")
                print(f"  温度: {new_temps} | Temperature: {new_temps}")
                print(f"  湿度: {humidity_variations}% | Humidity: {humidity_variations}%")
                print(f"  pH: {[ph/100.0 for ph in ph_variations]} | pH: {[ph/100.0 for ph in ph_variations]}")
                print(f"  转速: {new_speeds} | Speed: {new_speeds}")
                print(f"  压力: {pressure_variations} | Pressure: {pressure_variations}")
            
            await asyncio.sleep(3.0)  # 每3秒更新一次 | Update every 3 seconds
            
        except Exception as e:
            print(f"实验过程模拟错误 | Experiment process simulation error: {e}")
            await asyncio.sleep(3.0)


async def monitor_ascii_server(server: AsyncAsciiModbusServer) -> None:
    """
    监控ASCII服务器状态
    
    Monitor ASCII Server Status
    
    Args:
        server: ASCII服务器实例 | ASCII server instance
    """
    while True:
        try:
            if await server.is_running():
                print(f"ASCII服务器状态: 运行中 | ASCII server status: Running")
                print(f"串口: {server.port} | Serial port: {server.port}")
                print(f"波特率: {server.baudrate} | Baudrate: {server.baudrate}")
                print(f"从站地址: {server.slave_id} | Slave address: {server.slave_id}")
            else:
                print("ASCII服务器状态: 已停止 | ASCII server status: Stopped")
                break
            
            await asyncio.sleep(90.0)  # 每90秒检查一次 | Check every 90 seconds
            
        except Exception as e:
            print(f"ASCII服务器监控错误 | ASCII server monitoring error: {e}")
            await asyncio.sleep(15.0)


async def main():
    """
    主函数 | Main Function
    """
    # 设置日志 | Setup logging
    ModbusLogger.setup_logging(
        level=logging.INFO,
        enable_debug=True
    )
    
    print("=== ModbusLink 异步ASCII服务器示例 | ModbusLink Async ASCII Server Example ===")
    print()
    
    # 创建数据存储 | Create data store
    data_store = ModbusDataStore(
        coils_size=1000,
        discrete_inputs_size=1000,
        holding_registers_size=1000,
        input_registers_size=1000
    )
    
    # 设置实验室设备数据 | Setup laboratory equipment data
    await setup_laboratory_data(data_store)
    print()
    
    # 串口配置 | Serial port configuration
    # 注意：请根据实际情况修改串口名称 | Note: Please modify the serial port name according to actual situation
    port = "COM4"  # Windows
    # port = "/dev/ttyUSB1"  # Linux
    # port = "/dev/tty.usbserial-0002"  # macOS
    
    # 创建ASCII服务器 | Create ASCII server
    server = AsyncAsciiModbusServer(
        port=port,
        baudrate=9600,
        data_store=data_store,
        slave_id=2,  # 使用不同的从站地址 | Use different slave address
        parity="E",  # ASCII通常使用偶校验 | ASCII usually uses even parity
        stopbits=1,
        bytesize=7,  # ASCII通常使用7位数据 | ASCII usually uses 7-bit data
        timeout=2.0
    )
    
    print(f"ASCII服务器配置 | ASCII server configuration:")
    print(f"  串口: {port} | Serial port: {port}")
    print(f"  波特率: 9600 | Baudrate: 9600")
    print(f"  数据位: 7 | Data bits: 7")
    print(f"  停止位: 1 | Stop bits: 1")
    print(f"  校验位: 偶校验 | Parity: Even")
    print(f"  从站地址: 2 | Slave address: 2")
    print(f"  超时: 2.0秒 | Timeout: 2.0 seconds")
    print()
    
    try:
        # 启动服务器 | Start server
        await server.start()
        print("ASCII服务器启动成功! | ASCII server started successfully!")
        print()
        print("可以使用以下方式连接服务器: | You can connect to the server using:")
        print("  - ModbusLink ASCII客户端 | ModbusLink ASCII client")
        print("  - 其他Modbus ASCII主站设备 | Other Modbus ASCII master devices")
        print(f"  - 串口: {port} | Serial port: {port}")
        print("  - 通信参数: 9600,7,E,1 | Communication parameters: 9600,7,E,1")
        print("  - 帧格式: ASCII编码 | Frame format: ASCII encoding")
        print()
        print("按 Ctrl+C 停止服务器 | Press Ctrl+C to stop the server")
        print()
        
        # 启动后台任务 | Start background tasks
        tasks = [
            asyncio.create_task(simulate_laboratory_experiment(data_store)),
            asyncio.create_task(monitor_ascii_server(server)),
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
            print(f"  5. ASCII模式串口参数是否正确 (7,E,1) | 5. ASCII mode serial parameters are correct (7,E,1)")
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