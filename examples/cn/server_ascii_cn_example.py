"""
ModbusLink 异步ASCII服务器示例
演示如何创建和使用异步Modbus ASCII服务器
"""

import math
import random
import asyncio
import logging
from src.modbuslink import (
    AsyncAsciiModbusServer,
    ModbusDataStore,
    ModbusLogger,
    Language,
    set_language
)

set_language(Language.CN)


async def setup_laboratory_data(data_store: ModbusDataStore) -> None:
    """
    设置实验室设备模拟数据
    
    Args:
        data_store: 数据存储实例
    """
    # 实验室设备控制线圈
    # 0-7: 加热器控制
    # 8-15: 风扇控制
    # 16-23: 泵控制
    # 24-31: 照明控制
    data_store.write_coils(0, [False, True, False, True, False, False, True, False])  # 加热器
    data_store.write_coils(8, [True, True, False, False, True, True, False, False])  # 风扇
    data_store.write_coils(16, [False, True, True, False, False, True, False, True])  # 泵
    data_store.write_coils(24, [True, True, True, True, False, False, False, False])  # 照明

    # 设备参数设置寄存器
    # 0-9: 温度控制参数
    data_store.write_holding_registers(0, [250, 300, 180, 220, 350])  # 目标温度
    data_store.write_holding_registers(5, [5, 8, 3, 6, 10])  # 温度容差

    # 10-19: 时间控制参数 | Time control parameters
    data_store.write_holding_registers(10, [3600, 7200, 1800, 5400, 9000])  # 运行时间(秒)
    data_store.write_holding_registers(15, [60, 120, 30, 90, 180])  # 采样间隔(秒)

    # 20-29: 速度控制参数
    data_store.write_holding_registers(20, [1200, 1800, 800, 1500, 2000])  # 转速设定
    data_store.write_holding_registers(25, [50, 75, 25, 60, 100])  # 速度百分比

    # 传感器测量值输入寄存器
    # 0-9: 温度传感器
    data_store.write_input_registers(0, [248, 298, 178, 218, 348])  # 实际温度
    data_store.write_input_registers(5, [252, 302, 182, 222, 352])  # 温度传感器2

    # 10-19: 湿度传感器
    data_store.write_input_registers(10, [45, 52, 38, 48, 55])  # 相对湿度%
    data_store.write_input_registers(15, [47, 54, 40, 50, 57])  # 湿度传感器2

    # 20-29: pH传感器
    data_store.write_input_registers(20, [700, 650, 720, 680, 710])  # pH值*100

    # 30-39: 压力传感器
    data_store.write_input_registers(30, [1013, 1015, 1010, 1018, 1012])  # 大气压力

    # 40-49: 转速反馈
    data_store.write_input_registers(40, [1198, 1795, 798, 1498, 1995])  # 实际转速

    # 数字输入状态
    # 0-7: 门开关状态
    # 8-15: 安全开关
    # 16-23: 液位开关
    # 24-31: 压力开关
    data_store.write_discrete_inputs(0, [False, True, False, False, True, True, False, True])  # 门开关
    data_store.write_discrete_inputs(8, [True, True, True, True, True, True, True, True])  # 安全开关
    data_store.write_discrete_inputs(16, [False, False, True, True, False, True, True, False])  # 液位开关
    data_store.write_discrete_inputs(24, [True, False, True, False, True, False, True, False])  # 压力开关s

    print("实验室设备数据初始化完成")
    print(f"加热器控制 0-7: {data_store.read_coils(0, 8)}")
    print(f"温度设定 0-4: {data_store.read_holding_registers(0, 5)}")
    print(f"实际温度 0-4: {data_store.read_input_registers(0, 5)}")
    print(f"门开关状态 0-7: {data_store.read_discrete_inputs(0, 8)}")


async def simulate_laboratory_experiment(data_store: ModbusDataStore) -> None:
    """
    模拟实验室实验过程
    
    Args:
        data_store: 数据存储实例
    """

    experiment_time = 0

    while True:
        try:
            experiment_time += 1

            # 模拟温度控制过程
            target_temps = data_store.read_holding_registers(0, 5)
            current_temps = data_store.read_input_registers(0, 5)

            # 温度逐渐趋向目标值
            new_temps = []
            for i, (current, target) in enumerate(zip(current_temps, target_temps)):
                # 加入随机噪声和控制算法
                diff = target - current
                change = diff * 0.1 + random.randint(-2, 2) + math.sin(experiment_time * 0.05) * 1
                new_temp = current + change
                new_temps.append(int(max(0, min(500, new_temp))))  # 限制温度范围

            data_store.write_input_registers(0, new_temps)

            # 模拟湿度变化
            base_humidity = [45, 52, 38, 48, 55]
            humidity_variations = [base + random.randint(-5, 5) + int(2 * math.cos(experiment_time * 0.08)) for base in
                                   base_humidity]
            humidity_variations = [max(0, min(100, h)) for h in humidity_variations]  # 限制湿度范围
            data_store.write_input_registers(10, humidity_variations)

            # 模拟pH值变化
            base_ph = [700, 650, 720, 680, 710]
            ph_variations = [base + random.randint(-10, 10) + int(3 * math.sin(experiment_time * 0.03)) for base in
                             base_ph]
            ph_variations = [max(0, min(1400, ph)) for ph in ph_variations]  # 限制pH范围
            data_store.write_input_registers(20, ph_variations)

            # 模拟转速控制
            target_speeds = data_store.read_holding_registers(20, 5)
            current_speeds = data_store.read_input_registers(40, 5)

            new_speeds = []
            for current, target in zip(current_speeds, target_speeds):
                diff = target - current
                change = diff * 0.15 + random.randint(-20, 20)
                new_speed = current + change
                new_speeds.append(int(max(0, min(3000, new_speed))))  # 限制转速范围

            data_store.write_input_registers(40, new_speeds)

            # 模拟压力变化
            base_pressure = [1013, 1015, 1010, 1018, 1012]
            pressure_variations = [base + random.randint(-5, 5) + int(1 * math.sin(experiment_time * 0.02)) for base in
                                   base_pressure]
            data_store.write_input_registers(30, pressure_variations)

            # 随机改变一些开关状态
            if experiment_time % 30 == 0:
                # 随机改变门开关状态
                door_index = random.randint(0, 7)
                current_doors = data_store.read_discrete_inputs(0, 8)
                current_doors[door_index] = not current_doors[door_index]
                data_store.write_discrete_inputs(0, current_doors)
                print(
                    f"门开关状态变化: 开关 {door_index} = {current_doors[door_index]}")

            if experiment_time % 45 == 0:
                # 随机改变液位开关状态
                level_index = random.randint(16, 23)
                current_levels = data_store.read_discrete_inputs(16, 8)
                current_levels[level_index - 16] = not current_levels[level_index - 16]
                data_store.write_discrete_inputs(16, current_levels)
                print(
                    f"液位开关状态变化: 开关 {level_index} = {current_levels[level_index - 16]}")

            # 更新实验时间计数器
            data_store.write_holding_registers(100, [experiment_time])

            if experiment_time % 15 == 0:
                print(f"实验过程模拟 #{experiment_time}")
                print(f"  温度: {new_temps}")
                print(f"  湿度: {humidity_variations}%")
                print(f"  pH: {[ph / 100.0 for ph in ph_variations]}")
                print(f"  转速: {new_speeds}")
                print(f"  压力: {pressure_variations}")

            await asyncio.sleep(3.0)  # 每3秒更新一次

        except Exception as e:
            print(f"实验过程模拟错误: {e}")
            await asyncio.sleep(3.0)


async def monitor_ascii_server(server: AsyncAsciiModbusServer) -> None:
    """
    监控ASCII服务器状态
    
    Args:
        server: ASCII服务器实例
    """
    while True:
        try:
            if await server.is_running():
                print(f"ASCII服务器状态: 运行中")
                print(f"串口: {server.port}")
                print(f"波特率: {server.baudrate}")
                print(f"从站地址: {server.slave_id}")
            else:
                print("ASCII服务器状态: 已停止")
                break

            await asyncio.sleep(90.0)  # 每90秒检查一次

        except Exception as e:
            print(f"ASCII服务器监控错误: {e}")
            await asyncio.sleep(15.0)


async def main():
    """
    主函数
    """
    # 设置日志 | Setup logging
    ModbusLogger.setup_logging(
        level=logging.INFO,
        enable_debug=True
    )

    print("=== ModbusLink 异步ASCII服务器示例 ===")
    print()

    # 创建数据存储
    data_store = ModbusDataStore(
        coils_size=1000,
        discrete_inputs_size=1000,
        holding_registers_size=1000,
        input_registers_size=1000
    )

    # 设置实验室设备数据
    await setup_laboratory_data(data_store)
    print()

    # 串口配置
    # 注意：请根据实际情况修改串口名称
    port = "COM10"  # Windows
    # port = "/dev/ttyUSB1"  # Linux
    # port = "/dev/tty.usbserial-0002"  # macOS

    # 创建ASCII服务器
    server = AsyncAsciiModbusServer(
        port=port,
        baudrate=9600,
        data_store=data_store,
        slave_id=1,  # 使用不同的从站地址
        parity="E",  # ASCII通常使用偶校验
        stopbits=1,
        bytesize=7,  # ASCII通常使用7位数据
        timeout=2.0
    )

    print(f"ASCII服务器配置:")
    print(f"  串口: {port}")
    print(f"  波特率: 9600")
    print(f"  数据位: 7")
    print(f"  停止位: 1")
    print(f"  校验位: 偶校验")
    print(f"  从站地址: 2")
    print(f"  超时: 2.0秒")
    print()

    try:
        # 启动服务器
        await server.start()
        print("ASCII服务器启动成功!")
        print()
        print("可以使用以下方式连接服务器:")
        print("  - ModbusLink ASCII客户端")
        print("  - 其他Modbus ASCII主站设备")
        print(f"  - 串口: {port}")
        print("  - 通信参数: 9600,7,E,1")
        print("  - 帧格式: ASCII编码")
        print()
        print("按 Ctrl+C 停止服务器")
        print()

        # 启动后台任务
        tasks = [
            asyncio.create_task(simulate_laboratory_experiment(data_store)),
            asyncio.create_task(monitor_ascii_server(server)),
            asyncio.create_task(server.serve_forever())
        ]

        # 等待任务完成
        await asyncio.gather(*tasks)

    except KeyboardInterrupt:
        print("\n收到停止信号")
    except Exception as e:
        print(f"\n服务器运行错误: {e}")
        if "could not open port" in str(e).lower():
            print(f"\n串口打开失败，请检查:")
            print(f"  1. 串口名称是否正确 ({port})")
            print(f"  2. 串口是否被其他程序占用")
            print(f"  3. 串口设备是否已连接")
            print(f"  4. 是否有串口访问权限")
            print(f"  5. ASCII模式串口参数是否正确 (7,E,1)")
    finally:
        print("正在停止服务器...")
        await server.stop()
        print("服务器已停止")


if __name__ == "__main__":
    # 运行示例
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        print(f"\n程序运行错误: {e}")
