"""
ModbusLink 异步TCP服务器示例
演示如何创建和使用异步Modbus TCP服务器
"""

import random
import asyncio
import logging
from src.modbuslink import AsyncTcpModbusServer, ModbusDataStore
from src.modbuslink.utils.logging import ModbusLogger


async def setup_data_store(data_store: ModbusDataStore) -> None:
    """
    设置数据存储的初始值

    Args:
        data_store: 数据存储实例
    """
    # 设置一些初始的线圈值
    data_store.write_coils(0, [True, False, True, False, True, False, True, False])

    # 设置一些初始的离散输入值
    data_store.write_discrete_inputs(0, [False, True, False, True, False, True, False, True])

    # 设置一些初始的保持寄存器值
    data_store.write_holding_registers(0, [100, 200, 300, 400, 500])

    # 设置一些初始的输入寄存器值
    data_store.write_input_registers(0, [250, 251, 252, 253, 254])

    print("数据存储初始化完成")
    print(f"线圈 0-7: {data_store.read_coils(0, 8)}")
    print(f"离散输入 1-8: {data_store.read_discrete_inputs(0, 8)}")
    print(f"保持寄存器 2-6: {data_store.read_holding_registers(0, 5)}")
    print(f"输入寄存器 3-7: {data_store.read_input_registers(0, 5)}\n")


async def simulate_sensor_data(data_store: ModbusDataStore) -> None:
    """
    模拟传感器数据更新

    Args:
        data_store: 数据存储实例
    """
    counter = 0
    while True:
        try:
            # 模拟输入寄存器数据变化
            input_value = [random.randint(200, 300) for _ in range(5)]
            data_store.write_input_registers(0, input_value)

            # 模拟离散输入状态变化
            discrete_states = [random.choice([True, False]) for _ in range(8)]
            data_store.write_discrete_inputs(0, discrete_states)

            # 更新计数器
            counter += 1
            data_store.write_holding_registers(0, [counter])

            if counter % 10 == 0:
                print(f"传感器数据更新 #{counter}")
                print(f"  离散输入: {discrete_states}")
                print(f"  输入寄存器: {input_value}\n")

            await asyncio.sleep(1.0)  # 每秒更新一次

        except Exception as e:
            print(f"传感器数据模拟错误: {e}")
            await asyncio.sleep(1.0)


async def monitor_server(server: AsyncTcpModbusServer) -> None:
    """
    监控服务器状态

    Args:
        server: TCP服务器实例
    """
    while True:
        try:
            if await server.is_running():
                client_count = server.get_connected_clients_count()
                print(f"服务器状态: 运行中, 连接的客户端数: {client_count}")
            else:
                print("服务器状态: 已停止")
                break

            await asyncio.sleep(30.0)  # 每30秒检查一次 | Check every 30 seconds

        except Exception as e:
            print(f"服务器监控错误: {e}")
            await asyncio.sleep(5.0)


async def main() -> None:
    """主函数"""
    # 设置日志
    ModbusLogger.setup_logging(
        level=logging.INFO,
        enable_debug=True
    )

    print("=== ModbusLink 异步TCP服务器示例 ===\n")

    # 创建数据存储
    data_store = ModbusDataStore(
        coils_size=10,
        discrete_inputs_size=10,
        holding_registers_size=10,
        input_registers_size=10
    )

    # 设置初始数据
    await setup_data_store(data_store)

    # 创建TCP服务器
    server = AsyncTcpModbusServer(
        host="localhost",
        port=5020,
        data_store=data_store,
        slave_id=1,
        max_connections=5
    )

    print(f"启动TCP服务器: localhost:5020")
    print("从站地址: 1")
    print("最大连接数: 5")

    try:
        # 启动服务器
        await server.start()
        print("TCP服务器启动成功!\n ")
        print("可以使用以下方式连接服务器:")
        print("  - ModbusLink客户端")
        print("  - 其他Modbus TCP客户端工具")
        print("  - 地址: localhost:5020\n")
        print("按 Ctrl+C 停止服务器\n")

        # 启动后台任务
        tasks = [
            asyncio.create_task(simulate_sensor_data(data_store)),
            asyncio.create_task(monitor_server(server)),
            asyncio.create_task(server.serve_forever())
        ]

        # 等待任务完成
        await asyncio.gather(*tasks)

    except KeyboardInterrupt:
        print("\n收到停止信号")
    except Exception as e:
        print(f"\n服务器运行错误: {e}")
    finally:
        print("正在停止服务器...")
        await server.stop()
        print("服务器已停止")


if __name__ == '__main__':
    # 运行示例
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        print(f"\n程序运行错误：{e}")
