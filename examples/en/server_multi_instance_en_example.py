"""
ModbusLink Multi-Server Example
Demonstrates how to run multiple Modbus servers (TCP, RTU, ASCII) simultaneously.
"""

import asyncio
import logging
from src.modbuslink import (
    AsyncTcpModbusServer,
    AsyncRtuModbusServer,
    AsyncAsciiModbusServer,
    ModbusDataStore
)
from src.modbuslink.utils.logging import ModbusLogger, Language


class MultiServerManager:
    """
    Multi-Server Manager
    """

    def __init__(self):
        self.servers = {}
        self.data_stores = {}
        self.running = False
        self.tasks = []

    async def setup_tcp_server(self, host="localhost", port=5020, slave_id=1):
        """
        Setup TCP Server
        
        Args:
            host: Host address
            port: Port number
            slave_id: Slave address
        """
        # Create TCP server dedicated data store
        tcp_data_store = ModbusDataStore(
            coils_size=1000,
            discrete_inputs_size=1000,
            holding_registers_size=1000,
            input_registers_size=1000
        )

        # Initialize TCP server data
        tcp_data_store.write_coils(0, [True, False, True, False] * 10)
        tcp_data_store.write_holding_registers(0, list(range(100, 150)))
        tcp_data_store.write_input_registers(0, list(range(200, 250)))
        tcp_data_store.write_discrete_inputs(0, [False, True, False, True] * 10)

        # Create TCP server
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
            f"TCP server configured: {host}:{port}, slave address {slave_id}")

    async def setup_rtu_server(self, port="COM3", baudrate=9600, slave_id=2):
        """
        Setup RTU Server
        
        Args:
            port: Serial port name
            baudrate: Baudrate
            slave_id: Slave address
        """
        # Create RTU server dedicated data store
        rtu_data_store = ModbusDataStore(
            coils_size=1000,
            discrete_inputs_size=1000,
            holding_registers_size=1000,
            input_registers_size=1000
        )

        # Initialize RTU server data (industrial equipment simulation)
        rtu_data_store.write_coils(0, [False, True, False, True] * 8)  # Equipment status
        rtu_data_store.write_holding_registers(0, [1500, 2800, 3600, 1200, 750])  # Motor parameters
        rtu_data_store.write_input_registers(0, [248, 179, 318, 447, 682])  # Sensor readings
        rtu_data_store.write_discrete_inputs(0, [True, False, True, True] * 8)  # Switch status

        # Create RTU server
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
            f"RTU server configured: {port}@{baudrate}, slave address {slave_id}")

    async def setup_ascii_server(self, port="COM4", baudrate=9600, slave_id=3):
        """
        Setup ASCII Server
        
        Args:
            port: Serial port name
            baudrate: Baudrate
            slave_id: Slave address
        """
        # Create ASCII server dedicated data store
        ascii_data_store = ModbusDataStore(
            coils_size=1000,
            discrete_inputs_size=1000,
            holding_registers_size=1000,
            input_registers_size=1000
        )

        # Initialize ASCII server data (laboratory equipment simulation)
        ascii_data_store.write_coils(0, [True, True, False, False] * 8)  # Lab equipment control
        ascii_data_store.write_holding_registers(0, [250, 300, 180, 220, 350])  # Temperature settings
        ascii_data_store.write_input_registers(0, [248, 298, 178, 218, 348])  # Temperature readings
        ascii_data_store.write_discrete_inputs(0, [False, True, False, False] * 8)  # Sensor status

        # Create ASCII server
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
            f"ASCII server configured: {port}@{baudrate}, slave address {slave_id}")

    async def start_all_servers(self):
        """
        Start All Servers
        """
        print("\nStarting all servers...")

        for server_type, server in self.servers.items():
            try:
                await server.start()
                print(f"{server_type.upper()} server started successfully")
            except Exception as e:
                print(f"{server_type.upper()} server start failed: {e}")
                if "could not open port" in str(e).lower():
                    print(f"  Serial port may be occupied or not exist")

        self.running = True
        print("\nAll available servers started")

    async def stop_all_servers(self):
        """
        Stop All Servers
        """
        print("\nStopping all servers...")

        for server_type, server in self.servers.items():
            try:
                await server.stop()
                print(f"{server_type.upper()} server stopped")
            except Exception as e:
                print(f"{server_type.upper()} server stop failed: {e}")

        self.running = False
        print("All servers stopped")

    async def simulate_data_changes(self):
        """
        Simulate Data Changes
        """
        import random
        import math

        cycle = 0

        while self.running:
            try:
                cycle += 1

                # TCP server data simulation (network monitoring system)
                if "tcp" in self.data_stores:
                    tcp_store = self.data_stores["tcp"]
                    # Simulate network traffic data
                    traffic_data = [random.randint(100, 1000) for _ in range(10)]
                    tcp_store.write_input_registers(50, traffic_data)

                    # Simulate system status
                    system_status = [random.choice([True, False]) for _ in range(8)]
                    tcp_store.write_discrete_inputs(50, system_status)

                # RTU server data simulation (industrial process)
                if "rtu" in self.data_stores:
                    rtu_store = self.data_stores["rtu"]
                    # Simulate temperature sensors
                    base_temps = [248, 179, 318, 447, 682]
                    temp_variations = [base + random.randint(-10, 10) + int(5 * math.sin(cycle * 0.1)) for base in
                                       base_temps]
                    rtu_store.write_input_registers(0, temp_variations)

                    # Simulate motor speed
                    base_speeds = [1500, 2800, 3600, 1200, 750]
                    speed_variations = [base + random.randint(-100, 100) for base in base_speeds]
                    rtu_store.write_holding_registers(0, speed_variations)

                # ASCII server data simulation (laboratory equipment)
                if "ascii" in self.data_stores:
                    ascii_store = self.data_stores["ascii"]
                    # Simulate experiment temperature control
                    target_temps = ascii_store.read_holding_registers(0, 5)
                    current_temps = ascii_store.read_input_registers(0, 5)

                    new_temps = []
                    for current, target in zip(current_temps, target_temps):
                        diff = target - current
                        change = diff * 0.1 + random.randint(-2, 2)
                        new_temp = current + change
                        new_temps.append(int(max(0, min(500, new_temp))))

                    ascii_store.write_input_registers(0, new_temps)

                # Update global counter
                for store in self.data_stores.values():
                    store.write_holding_registers(999, [cycle])

                if cycle % 20 == 0:
                    print(f"\nData simulation cycle #{cycle}")
                    await self.print_server_status()

                await asyncio.sleep(2.0)  # Update every 2 seconds

            except Exception as e:
                print(f"Data simulation error: {e}")
                await asyncio.sleep(2.0)

    async def print_server_status(self):
        """
        Print Server Status
        """
        print("Server Status Summary:")

        for server_type, server in self.servers.items():
            try:
                is_running = await server.is_running()
                status = "Running" if is_running else "Stopped"

                if server_type == "tcp" and is_running:
                    client_count = server.get_connected_clients_count()
                    print(f"  {server_type.upper()}: {status}, connections {client_count}")
                else:
                    print(f"  {server_type.upper()}: {status}")

            except Exception as e:
                print(f"  {server_type.upper()}: Status check failed: {e}")

    async def monitor_servers(self):
        """
        Monitor Servers
        """
        while self.running:
            try:
                await asyncio.sleep(60.0)  # Check every minute
                await self.print_server_status()

            except Exception as e:
                print(f"Server monitoring error: {e}")
                await asyncio.sleep(10.0)

    async def serve_forever(self):
        """
        Serve Forever
        """
        # Start data simulation and monitoring tasks
        self.tasks = [
            asyncio.create_task(self.simulate_data_changes()),
            asyncio.create_task(self.monitor_servers())
        ]

        # Start serve_forever tasks for all servers
        for server_type, server in self.servers.items():
            try:
                if await server.is_running():
                    self.tasks.append(asyncio.create_task(server.serve_forever()))
            except Exception as e:
                print(
                    f"{server_type.upper()} server serve_forever start failed: {e}")

        # Wait for all tasks to complete
        await asyncio.gather(*self.tasks, return_exceptions=True)


async def main():
    """
    Main Function
    """
    # Setup logging
    ModbusLogger.setup_logging(
        level=logging.INFO,
        enable_debug=True,
        language=Language.EN
    )

    print("=== ModbusLink Multi-Server Example ===")
    print()

    # Create multi-server manager
    manager = MultiServerManager()

    try:
        # Configure servers
        print("Configuring servers...")

        # Setup TCP server
        await manager.setup_tcp_server(
            host="localhost",
            port=5020,
            slave_id=1
        )

        # Setup RTU server (modify port name if needed)
        await manager.setup_rtu_server(
            port="COM3",  # Modify according to actual situation
            baudrate=9600,
            slave_id=2
        )

        # Setup ASCII server (modify port name if needed)
        await manager.setup_ascii_server(
            port="COM4",  # Modify according to actual situation
            baudrate=9600,
            slave_id=3
        )

        print("\nServer configuration completed")
        print()

        # Start all servers
        await manager.start_all_servers()

        print("\nConnection Information:")
        print("  TCP Server: localhost:5020 (slave address 1)")
        print("  RTU Server: COM3@9600,8,N,1 (slave address 2)")
        print("  ASCII Server: COM4@9600,7,E,1 (slave address 3)")
        print()
        print("Press Ctrl+C to stop all servers")
        print()

        # Run forever
        await manager.serve_forever()

    except KeyboardInterrupt:
        print("\nReceived stop signal")
    except Exception as e:
        print(f"\nMulti-server running error: {e}")
    finally:
        await manager.stop_all_servers()


if __name__ == "__main__":
    # Run example
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nProgram interrupted by user")
    except Exception as e:
        print(f"\nProgram running error: {e}")
