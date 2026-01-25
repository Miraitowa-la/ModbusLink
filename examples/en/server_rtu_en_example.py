"""
ModbusLink RTU Server Example
"""

import random
import asyncio
import logging
from src.modbuslink import (
    AsyncRtuModbusServer,
    ModbusDataStore,
    ModbusLogger,
    Language,
    set_language
)


async def setup_data_store(data_store: ModbusDataStore) -> None:
    """
    Initialize data store values

    Args:
        data_store: Data store instance
    """
    # Set some initial coil values
    data_store.write_coils(0, [True, False, True, False, True, False, True, False])

    # Set some initial discrete input values
    data_store.write_discrete_inputs(1, [False, True, False, True, False, True, False, True])

    # Set some initial holding register values
    data_store.write_holding_registers(2, [100, 200, 300, 400, 500])

    # Set some initial input register values
    data_store.write_input_registers(3, [250, 251, 252, 253, 254])

    print("Data store initialization complete")
    print(f"Coils 0-7: {data_store.read_coils(0, 8)}")
    print(f"Discrete Inputs 1-8: {data_store.read_discrete_inputs(1, 8)}")
    print(f"Holding Registers 2-6: {data_store.read_holding_registers(2, 5)}")
    print(f"Input Registers 3-7: {data_store.read_input_registers(3, 5)}\n")


async def simulate_sensor_data(data_store: ModbusDataStore) -> None:
    """
    Simulate sensor data updates

    Args:
        data_store: Data store instance
    """
    counter = 0
    while True:
        try:
            # Simulate discrete input state changes
            discrete_states = [random.choice([True, False]) for _ in range(8)]
            data_store.write_discrete_inputs(1, discrete_states)

            # Simulate holding register data changes
            counter += 1
            data_store.write_holding_registers(2, [counter])

            # Simulate input register data changes
            input_value = [random.randint(200, 300) for _ in range(5)]
            data_store.write_input_registers(3, input_value)

            await asyncio.sleep(1.0)  # Update every second

        except Exception as e:
            print(f"Sensor data simulation error: {e}")
            await asyncio.sleep(1.0)


async def monitor_server(server: AsyncRtuModbusServer) -> None:
    """
    Monitor RTU server status

    Args:
        server: RTU server instance
    """
    while True:
        try:
            if await server.is_running():
                print(f"Server status: Running\n")
            else:
                print("Server status: Stopped\n")
                break

            await asyncio.sleep(30.0)  # Check every 30 seconds

        except Exception as e:
            print(f"Server monitoring error: {e}")
            await asyncio.sleep(10.0)


async def main() -> None:
    """Main Function"""
    # Setup logging
    ModbusLogger.setup_logging(
        level=logging.INFO,
        enable_debug=True
    )

    set_language(Language.EN)

    print("=== ModbusLink RTU Server Example ===")

    # Create data store
    data_store = ModbusDataStore(
        coils_size=10,
        discrete_inputs_size=10,
        holding_registers_size=10,
        input_registers_size=10
    )

    data_store.add_callback(
        "coils",
        lambda address, values: print(f"'data_store' Callback: Coils {address} updated: {values}")
    )
    data_store.add_callback(
        "discrete_inputs",
        lambda address, values: print(f"'data_store' Callback: Discrete Inputs {address} updated: {values}")
    )
    data_store.add_callback(
        "holding_registers",
        lambda address, values: print(f"'data_store' Callback: Holding Registers {address} updated: {values}")
    )
    data_store.add_callback(
        "input_registers",
        lambda address, values: print(f"'data_store' Callback: Input Registers {address} updated: {values}")
    )

    # Setup initial data
    await setup_data_store(data_store)

    # RTU Configuration
    rtu_config = {
        "port": "COM10",  # Windows
        # "port": "/dev/ttyUSB0",   # Linux
        # "port": "/dev/tty.usbserial-0001",  # macOS
        "baudrate": 9600,
        "bytesize": 8,
        "parity": "N",
        "stopbits": 1,
        "slave_id": 1,
    }

    # Create RTU server
    server = AsyncRtuModbusServer(
        port=rtu_config["port"],
        baudrate=rtu_config["baudrate"],
        bytesize=rtu_config["bytesize"],
        parity=rtu_config["parity"],
        stopbits=rtu_config["stopbits"],
        data_store=data_store,
        slave_id=rtu_config["slave_id"],
    )

    print(f"RTU Server Configuration:")
    print(f"  Port: {rtu_config['port']}")
    print(f"  Baudrate: {rtu_config['baudrate']}")
    print(f"  Data Bits: {rtu_config['bytesize']}")
    print(f"  Stop Bits: {rtu_config['stopbits']}")
    print(f"  Parity: {rtu_config['parity']}")
    print(f"  Slave ID: {rtu_config['slave_id']}\n")

    try:
        # Start server
        await server.start()
        print("RTU Server started successfully! Press Ctrl+C to stop server\n")

        # Start background tasks
        tasks = [
            asyncio.create_task(simulate_sensor_data(data_store)),
            asyncio.create_task(monitor_server(server)),
            asyncio.create_task(server.serve_forever())
        ]

        # Wait for tasks to complete
        await asyncio.gather(*tasks)

    except KeyboardInterrupt:
        print("\nStop signal received")
    except Exception as e:
        print(f"\nServer runtime error: {e}")
    finally:
        print("Stopping server...")
        await server.stop()
        print("Server stopped")


if __name__ == "__main__":
    # Run example
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nProgram interrupted by user")
    except Exception as e:
        print(f"\nProgram execution error: {e}")
