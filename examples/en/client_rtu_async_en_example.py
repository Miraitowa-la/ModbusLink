"""
ModbusLink Async RTU Client Example
"""

import asyncio
import logging
import traceback

from src.modbuslink import (
    AsyncModbusClient,
    AsyncRtuTransport,
    ConnectError,
    TimeOutError,
    CrcError,
    ModbusException,
    ModbusLogger,
    Language,
    set_language,
)


async def basic_operation_example(client: AsyncModbusClient):
    """Basic Operation Example"""
    print("\n=== Async RTU Basic Operation Example ===")

    # Create async client
    async with client:
        try:
            print("\n1. Read Coil Status (0x01)")
            coils = await client.read_coils(
                slave_id=1, start_address=0, quantity=10
            )
            print(f"   Coil Status: {coils}")

            print("\n2. Read Discrete Input Status (0x02)")
            discrete_inputs = await client.read_discrete_inputs(
                slave_id=1, start_address=0, quantity=10
            )
            print(f"   Discrete Input Status: {discrete_inputs}")

            print("\n3. Read Holding Registers (0x03)")
            holding_registers = await client.read_holding_registers(
                slave_id=1, start_address=0, quantity=10
            )
            print(f"   Holding Registers: {holding_registers}")

            print("\n4. Read Input Registers (0x04)")
            input_registers = await client.read_input_registers(
                slave_id=1, start_address=0, quantity=10
            )
            print(f"   Input Registers: {input_registers}")

            print("\n5. Write Single Coil (0x05)")
            await client.write_single_coil(
                slave_id=1, address=0, value=True
            )
            coils = await client.read_coils(
                slave_id=1, start_address=0, quantity=1
            )
            print(f"   Updated Coil Status: {coils[0]}")

            print("\n6. Write Single Register (0x06)")
            await client.write_single_register(
                slave_id=1, address=0, value=1234
            )
            registers = await client.read_holding_registers(
                slave_id=1, start_address=0, quantity=1
            )
            print(f"   Updated Register Value: {registers[0]}")

            print("\n7. Write Multiple Coils (0x0F)")
            await client.write_multiple_coils(
                slave_id=1, start_address=5, values=[False, True, False, True, False]
            )
            coils = await client.read_coils(
                slave_id=1, start_address=5, quantity=5
            )
            print(f"   Updated Coil Status: {coils}")

            print("\n8. Write Multiple Registers (0x10)")
            await client.write_multiple_registers(
                slave_id=1, start_address=5, values=[1234, 5678, 51011, 31314, 4789]
            )
            registers = await client.read_holding_registers(
                slave_id=1, start_address=5, quantity=5
            )
            print(f"   Updated Register Values: {registers}")

        except Exception as e:
            print(f"Operation failed: {e}")


async def advanced_operation_example(client: AsyncModbusClient):
    """Advanced Operation Example"""
    print("\n=== Async RTU Advanced Operation Example ===")

    try:
        async with client:
            print("\n1. Write 32-bit Float")
            value = 25.6
            await client.write_float32(
                slave_id=1, start_address=0, value=value
            )
            print(f"   Written Value: {value}")

            print("\n2. Read 32-bit Float")
            read_value = await client.read_float32(
                slave_id=1, start_address=0
            )
            print(f"   Read Value: {read_value}")

            print("\n3. Write 32-bit Signed Integer")
            value = -12345
            await client.write_int32(
                slave_id=1, start_address=0, value=value
            )
            print(f"   Written Value: {value}")

            print("\n4. Read 32-bit Signed Integer")
            read_value = await client.read_int32(
                slave_id=1, start_address=0
            )
            print(f"   Read Value: {read_value}")

            print("\n5. Write 32-bit Unsigned Integer")
            value = 12345
            await client.write_uint32(
                slave_id=1, start_address=0, value=value
            )
            print(f"   Written Value: {value}")

            print("\n6. Read 32-bit Unsigned Integer")
            read_value = await client.read_uint32(
                slave_id=1, start_address=0
            )
            print(f"   Read Value: {read_value}")

            print("\n7. Write 64-bit Signed Integer")
            value = -123
            await client.write_int64(
                slave_id=1, start_address=0, value=value
            )
            print(f"   Written Value: {value}")

            print("\n8. Read 64-bit Signed Integer")
            read_value = await client.read_int64(
                slave_id=1, start_address=0
            )
            print(f"   Read Value: {read_value}")

            print("\n9. Write 64-bit Unsigned Integer")
            value = 123
            await client.write_uint64(
                slave_id=1, start_address=0, value=value
            )
            print(f"   Written Value: {value}")

            print("\n10. Read 64-bit Unsigned Integer")
            read_value = await client.read_uint64(
                slave_id=1, start_address=0
            )
            print(f"   Read Value: {read_value}")

            print("\n11. Write String")
            value = "RTU Modbus"
            await client.write_string(
                slave_id=1, start_address=0, value=value
            )
            print(f"   Written Value: {value}")

            print("\n12. Read String")
            read_value = await client.read_string(
                slave_id=1, start_address=0, length=10
            )
            print(f"   Read Value: {read_value}")

            print("\n13. Test different byte and word orders (Big Endian, High Word)")
            value = 3.14159

            await client.write_float32(
                slave_id=1,
                start_address=0,
                value=value,
                byte_order="big",
                word_order="high",
            )
            read_value = await client.read_float32(
                slave_id=1,
                start_address=0,
                byte_order="big",
                word_order="high"
            )
            print(f"   Big/High: Wrote {value}, Read {read_value}")

            print("\n14. Test different byte and word orders (Little Endian, Low Word)")
            value = 3.14159

            await client.write_float32(
                slave_id=1,
                start_address=0,
                value=value,
                byte_order="little",
                word_order="low",
            )
            read_value = await client.read_float32(
                slave_id=1,
                start_address=0,
                byte_order="little",
                word_order="low"
            )
            print(f"   Little/Low: Wrote {value}, Read {read_value}")

    except Exception as e:
        print(f"Advanced operation failed: {e}")


async def callback_operation_example(client: AsyncModbusClient):
    """Callback Operation Example"""
    print("\n=== Async RTU Callback Operation Example ===")

    # Define callback functions
    def on_register_read(value):
        print(f"   [Callback] Read register value: {value}")

    def on_register_write():
        print("   [Callback] Register write complete")

    async with client:
        try:
            print("\n1. Register read with callback...")
            registers = await client.read_holding_registers(
                slave_id=1, start_address=0, quantity=1, callback=on_register_read
            )
            print(f"   Main thread received result: {registers}")

            print("\n2. Register write with callback...")
            await client.write_single_register(
                slave_id=1, address=0, value=9999, callback=on_register_write
            )
            print("   Main thread write complete")

            # Wait a bit for the callback to finish
            await asyncio.sleep(0.1)

        except Exception as e:
            print(f"Callback example failed: {e}")


async def concurrent_operation_example(client: AsyncModbusClient):
    """Concurrent Operation Example"""
    print("\n=== Async RTU Concurrent Operation Example ===")

    async with client:
        try:
            print(
                "\nExecuting multiple read operations concurrently..."
            )

            # Create multiple concurrent tasks
            tasks = [
                client.read_holding_registers(slave_id=1, start_address=0, quantity=2),
                client.read_holding_registers(slave_id=1, start_address=2, quantity=2),
                client.read_holding_registers(slave_id=1, start_address=4, quantity=2),
            ]

            # Execute all tasks concurrently
            start_time = asyncio.get_event_loop().time()
            results = await asyncio.gather(*tasks)
            end_time = asyncio.get_event_loop().time()

            print(
                f"   Concurrent execution time: {end_time - start_time:.3f} seconds"
            )
            print(f"   Holding Registers 0-1: {results[0]}")
            print(f"   Holding Registers 2-3: {results[1]}")
            print(f"   Holding Registers 4-5: {results[2]}")

        except Exception as e:
            print(f"Concurrent operation failed: {e}")


async def main():
    """Main Function"""
    # Setup logging
    ModbusLogger.setup_logging(
        level=logging.INFO,
        enable_debug=True
    )

    set_language(Language.EN)

    # RTU Configuration
    rtu_config = {
        "port": "COM10",  # Windows
        # "port": "/dev/ttyUSB0",   # Linux
        # "port": "/dev/tty.usbserial-0001",  # macOS
        "baudrate": 9600,
        "bytesize": 8,
        "parity": "N",
        "stopbits": 1,
        "timeout": 1,
    }

    # Create RTU transport layer
    transport = AsyncRtuTransport(
        port=rtu_config["port"],
        baudrate=rtu_config["baudrate"],
        bytesize=rtu_config["bytesize"],
        parity=rtu_config["parity"],
        stopbits=rtu_config["stopbits"],
        timeout=rtu_config["timeout"]
    )

    # Create RTU client
    client = AsyncModbusClient(transport)

    print(f"Async RTU Client Configuration:")
    print(f"  Port: {rtu_config['port']}")
    print(f"  Baudrate: {rtu_config['baudrate']}")
    print(f"  Data Bits: {rtu_config['bytesize']}")
    print(f"  Stop Bits: {rtu_config['stopbits']}")
    print(f"  Parity: {rtu_config['parity']}")
    print(f"  Note: Requires a Modbus RTU device server\n")

    try:
        # Execute examples sequentially
        await basic_operation_example(client)
        await advanced_operation_example(client)
        await callback_operation_example(client)
        await concurrent_operation_example(client)

        print("\n=== All examples execution completed ===")


    except KeyboardInterrupt:
        print("\nStop signal received")
    except ConnectError as e:
        print(f"\n'ConnectError' Connection error: {e}")
    except TimeOutError as e:
        print(f"\n'TimeOutError' Timeout error: {e}")
    except CrcError as e:
        print(f"\n'CrcError' Checksum error: {e}")
    except ModbusException as e:
        print(f"\n'ModbusException' Modbus protocol exception: {e}")
    except Exception as e:
        print(f"\nOther error: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
