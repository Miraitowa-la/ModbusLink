"""ModbusLink Async TCP Server Example
Demonstrates how to create and use async Modbus TCP server.
"""

import random
import asyncio
import logging
from src.modbuslink import AsyncTcpModbusServer, ModbusDataStore
from src.modbuslink.utils.logging import ModbusLogger, Language


async def setup_data_store(data_store: ModbusDataStore) -> None:
    """
    Setup Initial Values for Data Store

    Args:
        data_store: Data store instance
    """
    # Set some initial coil values
    data_store.write_coils(0, [True, False, True, False, True, False, True, False])

    # Set some initial discrete input values
    data_store.write_discrete_inputs(0, [False, True, False, True, False, True, False, True])

    # Set some initial holding register values
    data_store.write_holding_registers(0, [100, 200, 300, 400, 500])

    # Set some initial input register values
    data_store.write_input_registers(0, [250, 251, 252, 253, 254])

    print("Data store initialized")
    print(f"Coils 0-7: {data_store.read_coils(0, 8)}")
    print(f"Discrete inputs 1-8: {data_store.read_discrete_inputs(0, 8)}")
    print(f"Holding registers 2-6: {data_store.read_holding_registers(0, 5)}")
    print(f"Input registers 3-7: {data_store.read_input_registers(0, 5)}\n")


async def simulate_sensor_data(data_store: ModbusDataStore) -> None:
    """
    Simulate Sensor Data Updates

    Args:
        data_store: Data store instance
    """
    counter = 0
    while True:
        try:
            # Simulate changes in the input register data
            input_value = [random.randint(200, 300) for _ in range(5)]
            data_store.write_input_registers(0, input_value)

            # Simulate the change of discrete input states
            discrete_states = [random.choice([True, False]) for _ in range(8)]
            data_store.write_discrete_inputs(0, discrete_states)

            # 更新计数器
            counter += 1
            data_store.write_holding_registers(0, [counter])

            if counter % 10 == 0:
                print(f"Sensor data update #{counter}")
                print(f"  Discrete input: {discrete_states}")
                print(f"  Input register: {input_value}\n")

            await asyncio.sleep(1.0)  # Update every second

        except Exception as e:
            print(f"Sensor data simulation error: {e}")
            await asyncio.sleep(1.0)


async def monitor_server(server: AsyncTcpModbusServer) -> None:
    """
    Monitor Server Status

    Args:
        server: TCP server instance
    """
    while True:
        try:
            if await server.is_running():
                client_count = server.get_connected_clients_count()
                print(f"Server status: Running, Connected clients: {client_count}")
            else:
                print("Server status: Stopped")
                break

            await asyncio.sleep(30.0)  # Check every 30 seconds

        except Exception as e:
            print(f"Server monitoring error: {e}")
            await asyncio.sleep(5.0)


async def main() -> None:
    """Main Function"""
    # Setup logging
    ModbusLogger.setup_logging(
        level=logging.INFO,
        enable_debug=True,
        language=Language.EN
    )

    print("=== ModbusLink Async TCP Server Example ===\n")

    # Create data store
    data_store = ModbusDataStore(
        coils_size=10,
        discrete_inputs_size=10,
        holding_registers_size=10,
        input_registers_size=10
    )

    # Setup initial data
    await setup_data_store(data_store)

    # Create TCP server
    server = AsyncTcpModbusServer(
        host="localhost",
        port=5020,
        data_store=data_store,
        slave_id=1,
        max_connections=5
    )

    print(f"Starting TCP server: localhost:5020")
    print("Slave address: 1")
    print("Max connections: 5")

    try:
        # 启动服务器 | Start server
        await server.start()
        print("TCP server started successfully!\n ")
        print("You can connect to the server using:")
        print("  - ModbusLink client")
        print("  - Other Modbus TCP client tools")
        print("  - Address: localhost:5020\n")
        print("Press Ctrl+C to stop the server\n")

        # Start background tasks
        tasks = [
            asyncio.create_task(simulate_sensor_data(data_store)),
            asyncio.create_task(monitor_server(server)),
            asyncio.create_task(server.serve_forever())
        ]

        # Wait for tasks to complete
        await asyncio.gather(*tasks)

    except KeyboardInterrupt:
        print("\nReceived stop signal")
    except Exception as e:
        print(f"\nServer running error: {e}")
    finally:
        print("Stopping server...")
        await server.stop()
        print("Server stopped")


if __name__ == '__main__':
    # 运行示例
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n程序被用户中断 | Program interrupted by user")
    except Exception as e:
        print(f"\n程序运行错误 | Program running error：{e}")
