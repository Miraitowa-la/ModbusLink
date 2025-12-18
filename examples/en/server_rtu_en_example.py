"""
ModbusLink Async RTU Server Example
Demonstrates how to create and use async Modbus RTU server.
"""

import math
import random
import asyncio
import logging
from src.modbuslink import AsyncRtuModbusServer, ModbusDataStore
from src.modbuslink.utils.logging import ModbusLogger, Language


async def setup_industrial_data(data_store: ModbusDataStore) -> None:
    """
    Setup Industrial Equipment Simulation Data
    
    Args:
        data_store: Data store instance
    """
    # Equipment status coils
    # 0-7: Motor status
    # 8-15: Valve status
    # 16-23: Alarm status
    data_store.write_coils(0, [True, False, True, True, False, False, True, False])  # Motor status
    data_store.write_coils(8, [False, True, False, True, True, False, False, True])  # 阀Valve status
    data_store.write_coils(16, [False, False, False, False, False, False, False, False])  # Alarm status

    # Equipment parameter holding registers
    # 0-9: Motor parameters
    data_store.write_holding_registers(0, [1500, 2800, 3600, 1200, 750])  # Speed, torque, power, etc.
    data_store.write_holding_registers(5, [100, 85, 92, 78, 88])  # fficiency, temperature, etc.

    # 10-19: Process parameters
    data_store.write_holding_registers(10, [250, 180, 320, 450, 680])  # Temperature setpoints
    data_store.write_holding_registers(15, [1013, 1025, 998, 1045, 1002])  # Pressure setpoints

    # Sensor reading input registers
    # 0-9: Temperature sensors
    data_store.write_input_registers(0, [248, 179, 318, 447, 682])  # Actual temperature values
    data_store.write_input_registers(5, [251, 182, 322, 451, 685])  # Temperature sensor 2

    # 10-19: Pressure sensors
    data_store.write_input_registers(10, [1015, 1027, 996, 1043, 1004])  # Actual pressure values
    data_store.write_input_registers(15, [1012, 1023, 999, 1047, 1001])  # Pressure sensor 2

    # 20-29: Flow sensors
    data_store.write_input_registers(20, [125, 89, 156, 203, 178])  # Flow values

    # Digital input status
    # 0-7: Limit switches
    # 8-15: Safety switches
    data_store.write_discrete_inputs(0, [True, False, True, True, False, True, False, True])  # Limit switches
    data_store.write_discrete_inputs(8, [True, True, True, True, True, True, True, True])  # Safety switches

    print("Industrial equipment data initialized")
    print(f"Motor status coils 0-7: {data_store.read_coils(0, 8)}")
    print(f"Motor parameter registers 0-4: {data_store.read_holding_registers(0, 5)}")
    print(f"Temperature sensors 0-4: {data_store.read_input_registers(0, 5)}")
    print(f"Limit switches 0-7: {data_store.read_discrete_inputs(0, 8)}")


async def simulate_industrial_process(data_store: ModbusDataStore) -> None:
    """
    Simulate Industrial Process Data Changes
    
    Args:
        data_store: Data store instance
    """

    cycle_count = 0

    while True:
        try:
            cycle_count += 1

            # Simulate temperature sensor data fluctuation
            base_temps = [248, 179, 318, 447, 682]
            temp_variations = [base + random.randint(-5, 5) + int(3 * math.sin(cycle_count * 0.1)) for base in
                               base_temps]
            data_store.write_input_registers(0, temp_variations)

            # Simulate pressure sensor data fluctuation
            base_pressures = [1015, 1027, 996, 1043, 1004]
            pressure_variations = [base + random.randint(-3, 3) + int(2 * math.cos(cycle_count * 0.15)) for base in
                                   base_pressures]
            data_store.write_input_registers(10, pressure_variations)

            # Simulate flow sensor data
            base_flows = [125, 89, 156, 203, 178]
            flow_variations = [base + random.randint(-10, 10) + int(5 * math.sin(cycle_count * 0.2)) for base in
                               base_flows]
            data_store.write_input_registers(20, flow_variations)

            # Simulate motor speed changes
            current_speeds = data_store.read_holding_registers(0, 5)
            new_speeds = [speed + random.randint(-50, 50) for speed in current_speeds]
            # Limit speed range
            new_speeds = [max(500, min(4000, speed)) for speed in new_speeds]
            data_store.write_holding_registers(0, new_speeds)

            # Occasionally trigger alarms
            if cycle_count % 50 == 0:
                # Randomly trigger an alarm
                alarm_index = random.randint(16, 23)
                current_alarms = data_store.read_coils(16, 8)
                current_alarms[alarm_index - 16] = not current_alarms[alarm_index - 16]
                data_store.write_coils(16, current_alarms)
                print(f"Alarm status change: Coil {alarm_index} = {current_alarms[alarm_index - 16]}")

            # Update running counter
            data_store.write_holding_registers(100, [cycle_count])

            if cycle_count % 20 == 0:
                print(f"Industrial process simulation #{cycle_count}")
                print(f"  Temperature: {temp_variations}")
                print(f"  Pressure: {pressure_variations}")
                print(f"  Flow: {flow_variations}")
                print(f"  Motor speeds: {new_speeds}")

            await asyncio.sleep(2.0)  # Update every 2 seconds

        except Exception as e:
            print(f"Industrial process simulation error: {e}")
            await asyncio.sleep(2.0)


async def monitor_rtu_server(server: AsyncRtuModbusServer) -> None:
    """
    Monitor RTU Server Status
    
    Args:
        server: RTU server instance
    """
    while True:
        try:
            if await server.is_running():
                print(f"RTU server status: Running")
                print(f"Serial port: {server.port}")
                print(f"Baudrate: {server.baudrate}")
                print(f"Slave address: {server.slave_id}")
            else:
                print("RTU server status: Stopped")
                break

            await asyncio.sleep(60.0)  # Check every 60 seconds

        except Exception as e:
            print(f"RTU server monitoring error: {e}")
            await asyncio.sleep(10.0)


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

    print("=== ModbusLink Async RTU Server Example ===")
    print()

    # Create data store
    data_store = ModbusDataStore(
        coils_size=200,
        discrete_inputs_size=200,
        holding_registers_size=200,
        input_registers_size=200
    )

    # Setup industrial equipment data
    await setup_industrial_data(data_store)
    print()

    # Serial port configuration
    # Note: Please modify the serial port name according to actual situation
    port = "COM10"  # Windows
    # port = "/dev/ttyUSB0"  # Linux
    # port = "/dev/tty.usbserial-0001"  # macOS

    # Create RTU server
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

    print(f"RTU server configuration:")
    print(f"  Serial port: {port}")
    print(f"  Baudrate: 9600")
    print(f"  Data bits: 8")
    print(f"  Stop bits: 1")
    print(f"  Parity: None")
    print(f"  Slave address: 1")
    print(f"  Timeout: 1.0 seconds")
    print()

    try:
        # 启动服务器 | Start server
        await server.start()
        print("RTU server started successfully!")
        print()
        print("You can connect to the server using:")
        print("  - ModbusLink RTU client")
        print("  - Other Modbus RTU master devices")
        print(f"  - Serial port: {port}")
        print("  - Communication parameters: 9600,8,N,1")
        print()
        print("Press Ctrl+C to stop the server")
        print()

        # Start background tasks
        tasks = [
            asyncio.create_task(simulate_industrial_process(data_store)),
            asyncio.create_task(monitor_rtu_server(server)),
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
