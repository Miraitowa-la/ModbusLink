"""
ModbusLink 多服务器示例
演示如何同时运行多个Modbus服务器（TCP、RTU、ASCII）。
"""

import asyncio
import logging
from src.modbuslink import (
    AsyncTcpModbusServer,
    AsyncRtuModbusServer,
    AsyncAsciiModbusServer,
    ModbusDataStore
)
from src.modbuslink.utils.logging import ModbusLogger


class MultiServerManager:
    """
    多服务器管理器
    """

    def __init__(self):
        self.servers = {}
        self.data_stores = {}
        self.running = False
        self.tasks = []

    async def setup_tcp_server(self, host="localhost", port=5020, slave_id=1):
        """
        设置TCP服务器
        
        Args:
            host: 主机地址
            port: 端口号
            slave_id: 从站地址
        """
        # 创建TCP服务器专用数据存储
        tcp_data_store = ModbusDataStore(
            coils_size=1000,
            discrete_inputs_size=1000,
            holding_registers_size=1000,
            input_registers_size=1000
        )

        # 初始化TCP服务器数据
        tcp_data_store.write_coils(0, [True, False, True, False] * 10)
        tcp_data_store.write_holding_registers(0, list(range(100, 150)))
        tcp_data_store.write_input_registers(0, list(range(200, 250)))
        tcp_data_store.write_discrete_inputs(0, [False, True, False, True] * 10)

        # 创建TCP服务器
        tcp_server = AsyncTcpModbusServer(
            host=host,
            port=port,
            data_store=tcp_data_store,
            slave_id=slave_id,
            max_connections=10
        )

        self.servers["tcp"] = tcp_server
        self.data_stores["tcp"] = tcp_data_store

        print(
            f"TCP服务器配置完成: {host}:{port}, 从站地址 {slave_id}")

    async def setup_rtu_server(self, port="COM3", baudrate=9600, slave_id=2):
        """
        设置RTU服务器
        
        Args:
            port: 串口名称
            baudrate: 波特率
            slave_id: 从站地址
        """
        # 创建RTU服务器专用数据存储
        rtu_data_store = ModbusDataStore(
            coils_size=1000,
            discrete_inputs_size=1000,
            holding_registers_size=1000,
            input_registers_size=1000
        )

        # 初始化RTU服务器数据（工业设备模拟）
        rtu_data_store.write_coils(0, [False, True, False, True] * 8)  # 设备状态
        rtu_data_store.write_holding_registers(0, [1500, 2800, 3600, 1200, 750])  # 电机参数
        rtu_data_store.write_input_registers(0, [248, 179, 318, 447, 682])  # 传感器读数
        rtu_data_store.write_discrete_inputs(0, [True, False, True, True] * 8)  # 开关状态

        # 创建RTU服务器
        rtu_server = AsyncRtuModbusServer(
            port=port,
            baudrate=baudrate,
            data_store=rtu_data_store,
            slave_id=slave_id,
            parity="N",
            stopbits=1,
            bytesize=8,
            timeout=1.0
        )

        self.servers["rtu"] = rtu_server
        self.data_stores["rtu"] = rtu_data_store

        print(
            f"RTU服务器配置完成: {port}@{baudrate}, 从站地址 {slave_id}")

    async def setup_ascii_server(self, port="COM4", baudrate=9600, slave_id=3):
        """
        设置ASCII服务器
        
        Args:
            port: 串口名称
            baudrate: 波特率
            slave_id: 从站地址
        """
        # 创建ASCII服务器专用数据存储
        ascii_data_store = ModbusDataStore(
            coils_size=1000,
            discrete_inputs_size=1000,
            holding_registers_size=1000,
            input_registers_size=1000
        )

        # 初始化ASCII服务器数据（实验室设备模拟）
        ascii_data_store.write_coils(0, [True, True, False, False] * 8)  # 实验设备控制
        ascii_data_store.write_holding_registers(0, [250, 300, 180, 220, 350])  # 温度设定
        ascii_data_store.write_input_registers(0, [248, 298, 178, 218, 348])  # 温度读数
        ascii_data_store.write_discrete_inputs(0, [False, True, False, False] * 8)  # 传感器状态

        # 创建ASCII服务器
        ascii_server = AsyncAsciiModbusServer(
            port=port,
            baudrate=baudrate,
            data_store=ascii_data_store,
            slave_id=slave_id,
            parity="E",
            stopbits=1,
            bytesize=7,
            timeout=2.0
        )

        self.servers["ascii"] = ascii_server
        self.data_stores["ascii"] = ascii_data_store

        print(
            f"ASCII服务器配置完成: {port}@{baudrate}, 从站地址 {slave_id}")

    async def start_all_servers(self):
        """
        启动所有服务器
        """
        print("\n正在启动所有服务器...")

        for server_type, server in self.servers.items():
            try:
                await server.start()
                print(f"{server_type.upper()}服务器启动成功")
            except Exception as e:
                print(f"{server_type.upper()}服务器启动失败: {e}")
                if "could not open port" in str(e).lower():
                    print(f"  串口可能被占用或不存在")

        self.running = True
        print("\n所有可用服务器已启动")

    async def stop_all_servers(self):
        """
        停止所有服务器
        """
        print("\n正在停止所有服务器...")

        for server_type, server in self.servers.items():
            try:
                await server.stop()
                print(f"{server_type.upper()}服务器已停止")
            except Exception as e:
                print(f"{server_type.upper()}服务器停止失败: {e}")

        self.running = False
        print("所有服务器已停止")

    async def simulate_data_changes(self):
        """
        模拟数据变化
        """
        import random
        import math

        cycle = 0

        while self.running:
            try:
                cycle += 1

                # TCP服务器数据模拟（网络监控系统）
                if "tcp" in self.data_stores:
                    tcp_store = self.data_stores["tcp"]
                    # 模拟网络流量数据
                    traffic_data = [random.randint(100, 1000) for _ in range(10)]
                    tcp_store.write_input_registers(50, traffic_data)

                    # 模拟系统状态
                    system_status = [random.choice([True, False]) for _ in range(8)]
                    tcp_store.write_discrete_inputs(50, system_status)

                # RTU服务器数据模拟（工业过程）
                if "rtu" in self.data_stores:
                    rtu_store = self.data_stores["rtu"]
                    # 模拟温度传感器
                    base_temps = [248, 179, 318, 447, 682]
                    temp_variations = [base + random.randint(-10, 10) + int(5 * math.sin(cycle * 0.1)) for base in
                                       base_temps]
                    rtu_store.write_input_registers(0, temp_variations)

                    # 模拟电机转速
                    base_speeds = [1500, 2800, 3600, 1200, 750]
                    speed_variations = [base + random.randint(-100, 100) for base in base_speeds]
                    rtu_store.write_holding_registers(0, speed_variations)

                # ASCII服务器数据模拟（实验室设备）
                if "ascii" in self.data_stores:
                    ascii_store = self.data_stores["ascii"]
                    # 模拟实验温度控制
                    target_temps = ascii_store.read_holding_registers(0, 5)
                    current_temps = ascii_store.read_input_registers(0, 5)

                    new_temps = []
                    for current, target in zip(current_temps, target_temps):
                        diff = target - current
                        change = diff * 0.1 + random.randint(-2, 2)
                        new_temp = current + change
                        new_temps.append(int(max(0, min(500, new_temp))))

                    ascii_store.write_input_registers(0, new_temps)

                # 更新全局计数器
                for store in self.data_stores.values():
                    store.write_holding_registers(999, [cycle])

                if cycle % 20 == 0:
                    print(f"\n数据模拟周期 #{cycle}")
                    await self.print_server_status()

                await asyncio.sleep(2.0)  # 每2秒更新一次

            except Exception as e:
                print(f"数据模拟错误: {e}")
                await asyncio.sleep(2.0)

    async def print_server_status(self):
        """
        打印服务器状态
        """
        print("服务器状态摘要:")

        for server_type, server in self.servers.items():
            try:
                is_running = await server.is_running()
                status = "运行中" if is_running else "已停止"

                if server_type == "tcp" and is_running:
                    client_count = server.get_connected_clients_count()
                    print(f"  {server_type.upper()}: {status}, connections {client_count}")
                else:
                    print(f"  {server_type.upper()}: {status}")

            except Exception as e:
                print(f"  {server_type.upper()}: Status check failed: {e}")

    async def monitor_servers(self):
        """
        监控服务器
        """
        while self.running:
            try:
                await asyncio.sleep(60.0)  # 每分钟检查一次
                await self.print_server_status()

            except Exception as e:
                print(f"服务器监控错误: {e}")
                await asyncio.sleep(10.0)

    async def serve_forever(self):
        """
        永久运行服务器
        """
        # 启动数据模拟和监控任务
        self.tasks = [
            asyncio.create_task(self.simulate_data_changes()),
            asyncio.create_task(self.monitor_servers())
        ]

        # 启动所有服务器的serve_forever任务
        for server_type, server in self.servers.items():
            try:
                if await server.is_running():
                    self.tasks.append(asyncio.create_task(server.serve_forever()))
            except Exception as e:
                print(
                    f"{server_type.upper()}服务器serve_forever启动失败: {e}")

        # 等待所有任务完成
        await asyncio.gather(*self.tasks, return_exceptions=True)


async def main():
    """
    主函数
    """
    # 设置日志
    ModbusLogger.setup_logging(
        level=logging.INFO,
        enable_debug=True
    )

    print("=== ModbusLink 多服务器示例 ===")
    print()

    # 创建多服务器管理器
    manager = MultiServerManager()

    try:
        # 配置服务器
        print("配置服务器...")

        # 设置TCP服务器
        await manager.setup_tcp_server(
            host="localhost",
            port=5020,
            slave_id=1
        )

        # 设置RTU服务器（如果需要，请修改串口名称）
        await manager.setup_rtu_server(
            port="COM3",  # 根据实际情况修改
            baudrate=9600,
            slave_id=2
        )

        # 设置ASCII服务器（如果需要，请修改串口名称）
        await manager.setup_ascii_server(
            port="COM4",  # 根据实际情况修改
            baudrate=9600,
            slave_id=3
        )

        print("\n服务器配置完成")
        print()

        # 启动所有服务器
        await manager.start_all_servers()
        
        print("\n连接信息:")
        print("  TCP服务器: localhost:5020 (从站地址 1)")
        print("  RTU服务器: COM3@9600,8,N,1 (从站地址 2)")
        print("  ASCII服务器: COM4@9600,7,E,1 (从站地址 3)")
        print()
        print("按 Ctrl+C 停止所有服务器")
        print()

        # 永久运行
        await manager.serve_forever()

    except KeyboardInterrupt:
        print("\n收到停止信号")
    except Exception as e:
        print(f"\n多服务器运行错误: {e}")
    finally:
        await manager.stop_all_servers()


if __name__ == "__main__":
    # 运行示例
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        print(f"\n程序运行错误: {e}")
