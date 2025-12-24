"""
ModbusLink Async ASCII Server Example
Demonstrates how to create and use async Modbus ASCII server.
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
    set_language,
)

set_language(Language.EN)


async def setup_laboratory_data(data_store: ModbusDataStore) -> None:
    """
    Setup Laboratory Equipment Simulation Data
    
    Args:
        data_store: Data store instance
    """
    # Laboratory equipment control coils
    # 0-7: Heater control
    # 8-15: Fan control
    # 16-23: Pump control
    # 24-31: Lighting control
    data_store.write_coils(0, [False, True, False, True, False, False, True, False])  # Heaters
    data_store.write_coils(8, [True, True, False, False, True, True, False, False])  # Fans
    data_store.write_coils(16, [False, True, True, False, False, True, False, True])  # Pumps
    data_store.write_coils(24, [True, True, True, True, False, False, False, False])  # Lighting

    # Equipment parameter setting registers
    # 0-9: Temperature control parameters
    data_store.write_holding_registers(0, [250, 300, 180, 220, 350])  # Target temperatures
    data_store.write_holding_registers(5, [5, 8, 3, 6, 10])  # Temperature tolerance

    # 10-19: Time control parameters
    data_store.write_holding_registers(10, [3600, 7200, 1800, 5400, 9000])  # Running time (seconds)
    data_store.write_holding_registers(15, [60, 120, 30, 90, 180])  # Sampling interval (seconds)

    # 20-29: Speed control parameters
    data_store.write_holding_registers(20, [1200, 1800, 800, 1500, 2000])  # Speed settings
    data_store.write_holding_registers(25, [50, 75, 25, 60, 100])  # Speed percentage

    # Sensor measurement input registers
    # 0-9: Temperature sensors
    data_store.write_input_registers(0, [248, 298, 178, 218, 348])  # Actual temperatures
    data_store.write_input_registers(5, [252, 302, 182, 222, 352])  # Temperature sensor 2

    # 10-19: Humidity sensors
    data_store.write_input_registers(10, [45, 52, 38, 48, 55])  # Relative humidity %
    data_store.write_input_registers(15, [47, 54, 40, 50, 57])  # Humidity sensor 2

    # 20-29: pH sensors
    data_store.write_input_registers(20, [700, 650, 720, 680, 710])  # pH value * 100

    # 30-39: Pressure sensors
    data_store.write_input_registers(30, [1013, 1015, 1010, 1018, 1012])  # Atmospheric pressure

    # 40-49: Speed feedback
    data_store.write_input_registers(40, [1198, 1795, 798, 1498, 1995])  # Actual speed

    # Digital input status
    # 0-7: Door switch status
    # 8-15: Safety switches
    # 16-23: Level switches
    # 24-31: Pressure switches
    data_store.write_discrete_inputs(0, [False, True, False, False, True, True, False, True])  # Door switches
    data_store.write_discrete_inputs(8, [True, True, True, True, True, True, True, True])  # Safety switches
    data_store.write_discrete_inputs(16, [False, False, True, True, False, True, True, False])  # Level switches
    data_store.write_discrete_inputs(24, [True, False, True, False, True, False, True, False])  # Pressure switches

    print("Laboratory equipment data initialized")
    print(f"Heater control 0-7: {data_store.read_coils(0, 8)}")
    print(f"Temperature settings 0-4: {data_store.read_holding_registers(0, 5)}")
    print(f"Actual temperatures 0-4: {data_store.read_input_registers(0, 5)}")
    print(f"Door switch status 0-7: {data_store.read_discrete_inputs(0, 8)}")


async def simulate_laboratory_experiment(data_store: ModbusDataStore) -> None:
    """
    Simulate Laboratory Experiment Process
    
    Args:
        data_store: Data store instance
    """

    experiment_time = 0

    while True:
        try:
            experiment_time += 1

            # Simulate temperature control process
            target_temps = data_store.read_holding_registers(0, 5)
            current_temps = data_store.read_input_registers(0, 5)

            # Temperature gradually approaches target value
            new_temps = []
            for i, (current, target) in enumerate(zip(current_temps, target_temps)):
                # Add random noise and control algorithm
                diff = target - current
                change = diff * 0.1 + random.randint(-2, 2) + math.sin(experiment_time * 0.05) * 1
                new_temp = current + change
                new_temps.append(int(max(0, min(500, new_temp))))  # Limit temperature range

            data_store.write_input_registers(0, new_temps)

            # Simulate humidity changes
            base_humidity = [45, 52, 38, 48, 55]
            humidity_variations = [base + random.randint(-5, 5) + int(2 * math.cos(experiment_time * 0.08)) for base in
                                   base_humidity]
            humidity_variations = [max(0, min(100, h)) for h in humidity_variations]  # Limit humidity range
            data_store.write_input_registers(10, humidity_variations)

            # Simulate pH value changes
            base_ph = [700, 650, 720, 680, 710]
            ph_variations = [base + random.randint(-10, 10) + int(3 * math.sin(experiment_time * 0.03)) for base in
                             base_ph]
            ph_variations = [max(0, min(1400, ph)) for ph in ph_variations]  # 限制pH范围 | Limit pH range
            data_store.write_input_registers(20, ph_variations)

            # Simulate speed control
            target_speeds = data_store.read_holding_registers(20, 5)
            current_speeds = data_store.read_input_registers(40, 5)

            new_speeds = []
            for current, target in zip(current_speeds, target_speeds):
                diff = target - current
                change = diff * 0.15 + random.randint(-20, 20)
                new_speed = current + change
                new_speeds.append(int(max(0, min(3000, new_speed))))  # Limit speed range

            data_store.write_input_registers(40, new_speeds)

            # Simulate pressure changes
            base_pressure = [1013, 1015, 1010, 1018, 1012]
            pressure_variations = [base + random.randint(-5, 5) + int(1 * math.sin(experiment_time * 0.02)) for base in
                                   base_pressure]
            data_store.write_input_registers(30, pressure_variations)

            # Randomly change some switch states
            if experiment_time % 30 == 0:
                # Randomly change door switch status
                door_index = random.randint(0, 7)
                current_doors = data_store.read_discrete_inputs(0, 8)
                current_doors[door_index] = not current_doors[door_index]
                data_store.write_discrete_inputs(0, current_doors)
                print(f"Door switch status change: Switch {door_index} = {current_doors[door_index]}")

            if experiment_time % 45 == 0:
                # Randomly change level switch status
                level_index = random.randint(16, 23)
                current_levels = data_store.read_discrete_inputs(16, 8)
                current_levels[level_index - 16] = not current_levels[level_index - 16]
                data_store.write_discrete_inputs(16, current_levels)
                print(f"Level switch status change: Switch {level_index} = {current_levels[level_index - 16]}")

            # Update experiment time counter
            data_store.write_holding_registers(100, [experiment_time])

            if experiment_time % 15 == 0:
                print(f"Experiment process simulation #{experiment_time}")
                print(f"  Temperature: {new_temps}")
                print(f"  Humidity: {humidity_variations}%")
                print(f"  pH: {[ph / 100.0 for ph in ph_variations]}")
                print(f"  Speed: {new_speeds}")
                print(f"  Pressure: {pressure_variations}")

            await asyncio.sleep(3.0)  # Update every 3 seconds

        except Exception as e:
            print(f"Experiment process simulation error: {e}")
            await asyncio.sleep(3.0)


async def monitor_ascii_server(server: AsyncAsciiModbusServer) -> None:
    """
    监控ASCII服务器状态
    
    Monitor ASCII Server Status
    
    Args:
        server: ASCII server instance
    """
    while True:
        try:
            if await server.is_running():
                print(f"ASCII server status: Running")
                print(f"Serial port: {server.port}")
                print(f"Baudrate: {server.baudrate}")
                print(f"Slave address: {server.slave_id}")
            else:
                print("ASCII server status: Stopped")
                break

            await asyncio.sleep(90.0)  # Check every 90 seconds

        except Exception as e:
            print(f"ASCII server monitoring error: {e}")
            await asyncio.sleep(15.0)


async def main():
    """
    Main Function
    """
    # Setup logging
    ModbusLogger.setup_logging(
        level=logging.INFO,
        enable_debug=True
    )

    print("=== ModbusLink Async ASCII Server Example ===")
    print()

    # Create data store
    data_store = ModbusDataStore(
        coils_size=1000,
        discrete_inputs_size=1000,
        holding_registers_size=1000,
        input_registers_size=1000
    )

    # Setup laboratory equipment data
    await setup_laboratory_data(data_store)
    print()

    # Serial port configuration
    # Note: Please modify the serial port name according to actual situation
    port = "COM10"  # Windows
    # port = "/dev/ttyUSB1"  # Linux
    # port = "/dev/tty.usbserial-0002"  # macOS

    # Create ASCII server
    server = AsyncAsciiModbusServer(
        port=port,
        baudrate=9600,
        data_store=data_store,
        slave_id=1,  # Use different slave address
        parity="E",  # ASCII usually uses even parity
        stopbits=1,
        bytesize=7,  # ASCII usually uses 7-bit data
        timeout=2.0
    )

    print(f"ASCII server configuration:")
    print(f"  Serial port: {port}")
    print(f"  Baudrate: 9600")
    print(f"  Data bits: 7")
    print(f"  Stop bits: 1")
    print(f"  Parity: Even")
    print(f"  Slave address: 2")
    print(f"  Timeout: 2.0 seconds")
    print()

    try:
        # Start server
        await server.start()
        print("ASCII server started successfully!")
        print()
        print("You can connect to the server using:")
        print("  - ModbusLink ASCII client")
        print("  - Other Modbus ASCII master devices")
        print(f"  - Serial port: {port}")
        print("  - Communication parameters: 9600,7,E,1")
        print("  - Frame format: ASCII encoding")
        print()
        print("Press Ctrl+C to stop the server")
        print()

        # Start background tasks
        tasks = [
            asyncio.create_task(simulate_laboratory_experiment(data_store)),
            asyncio.create_task(monitor_ascii_server(server)),
            asyncio.create_task(server.serve_forever())
        ]

        # Wait for tasks to complete
        await asyncio.gather(*tasks)

    except KeyboardInterrupt:
        print("\nReceived stop signal")
    except Exception as e:
        print(f"\nServer running error: {e}")
        if "could not open port" in str(e).lower():
            print(f"\nSerial port open failed, please check:")
            print(f"  1. Serial port name is correct ({port})")
            print(f"  2. Serial port is not occupied by other programs")
            print(f"  3. Serial port device is connected")
            print(f"  4. Have serial port access permission")
            print(f"  5. ASCII mode serial parameters are correct (7,E,1)")
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
        print(f"\nProgram running error: {e}")
