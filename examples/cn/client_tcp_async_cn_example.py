"""
ModbusLink 异步TCP客户端示例
"""

import asyncio
import logging
import traceback

from src.modbuslink import (
    AsyncModbusClient,
    AsyncTcpTransport,
    ConnectError,
    TimeOutError,
    CrcError,
    ModbusException,
    ModbusLogger,
    Language,
    set_language,
)


async def basic_operation_example(client: AsyncModbusClient):
    """基本操作示例"""
    print("\n=== 异步TCP基本操作示例 ===")

    # 创建异步客户端
    async with client:
        try:
            print("\n1. 读取线圈状态 (0x01)")
            coils = await client.read_coils(
                slave_id=1, start_address=0, quantity=10
            )
            print(f"   线圈状态: {coils}")

            print("\n2. 读取离散输入状态 (0x02)")
            discrete_inputs = await client.read_discrete_inputs(
                slave_id=1, start_address=0, quantity=10
            )
            print(f"   离散输入状态: {discrete_inputs}")

            print("\n3. 读取保持寄存器 (0x03)")
            holding_registers = await client.read_holding_registers(
                slave_id=1, start_address=0, quantity=10
            )
            print(f"   保持寄存器: {holding_registers}")

            print("\n4. 读取输入寄存器 (0x04)")
            input_registers = await client.read_input_registers(
                slave_id=1, start_address=0, quantity=10
            )
            print(f"   输入寄存器: {input_registers}")

            print("\n5. 写单个线圈 (0x05)")
            await client.write_single_coil(
                slave_id=1, address=0, value=True
            )
            coils = await client.read_coils(
                slave_id=1, start_address=0, quantity=1
            )
            print(f"   更新后线圈状态: {coils[0]}")

            print("\n6. 写单个寄存器 (0x06)")
            await client.write_single_register(
                slave_id=1, address=0, value=1234
            )
            registers = await client.read_holding_registers(
                slave_id=1, start_address=0, quantity=1
            )
            print(f"   更新后寄存器值: {registers[0]}")

            print("\n7. 写多个线圈 (0x0F)")
            await client.write_multiple_coils(
                slave_id=1, start_address=5, values=[False, True, False, True, False]
            )
            coils = await client.read_coils(
                slave_id=1, start_address=5, quantity=5
            )
            print(f"   更新后线圈状态: {coils}")

            print("\n8. 写多个寄存器 (0x10)")
            await client.write_multiple_registers(
                slave_id=1, start_address=5, values=[1234, 5678, 51011, 31314, 4789]
            )
            registers = await client.read_holding_registers(
                slave_id=1, start_address=5, quantity=5
            )
            print(f"   更新后寄存器值: {registers}")

        except Exception as e:
            print(f"操作失败: {e}")


async def advanced_operation_example(client: AsyncModbusClient):
    """高级操作示例"""
    print("\n=== 同步TCP高级操作示例 ===")

    try:
        async with client:
            print("\n1. 写入32位浮点数")
            value = 25.6
            await client.write_float32(
                slave_id=1, start_address=0, value=value
            )
            print(f"   写入值: {value}")

            print("\n2. 读取32位浮点数")
            read_value = await client.read_float32(
                slave_id=1, start_address=0
            )
            print(f"   读取值: {read_value}")

            print("\n3. 写入32位有符号整数")
            value = -12345
            await client.write_int32(
                slave_id=1, start_address=0, value=value
            )
            print(f"   写入值: {value}")

            print("\n4. 读取32位有符号整数")
            read_value = await client.read_int32(
                slave_id=1, start_address=0
            )
            print(f"   读取值: {read_value}")

            print("\n5. 写入32位无符号整数")
            value = 12345
            await client.write_uint32(
                slave_id=1, start_address=0, value=value
            )
            print(f"   写入值: {value}")

            print("\n6. 读取32位无符号整数")
            read_value = await client.read_uint32(
                slave_id=1, start_address=0
            )
            print(f"   读取值: {read_value}")

            print("\n7. 写入64位有符号整数")
            value = -123
            await client.write_int64(
                slave_id=1, start_address=0, value=value
            )
            print(f"   写入值: {value}")

            print("\n8. 读取64位有符号整数")
            read_value = await client.read_int64(
                slave_id=1, start_address=0
            )
            print(f"   读取值: {read_value}")

            print("\n9. 写入64位无符号整数")
            value = 123
            await client.write_uint64(
                slave_id=1, start_address=0, value=value
            )
            print(f"   写入值: {value}")

            print("\n10. 读取64位无符号整数")
            read_value = await client.read_uint64(
                slave_id=1, start_address=0
            )
            print(f"   读取值: {read_value}")

            print("\n11. 写入字符串")
            value = "TCP Modbus"
            await client.write_string(
                slave_id=1, start_address=0, value=value
            )
            print(f"   写入值: {value}")

            print("\n12. 读取字符串")
            read_value = await client.read_string(
                slave_id=1, start_address=0, length=10
            )
            print(f"   读取值: {read_value}")

            print("\n13. 测试不同的字节序和字序(大端序，高位字)")
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
            print(f"   Big/High: 写入 {value}, 读取 {read_value}")

            print("\n14. 测试不同的字节序和字序(小端序，低位字)")
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
            print(f"   Little/Low: 写入 {value}, 读取 {read_value}")

    except Exception as e:
        print(f"高级操作失败: {e}")


async def callback_operation_example(client: AsyncModbusClient):
    """回调操作示例"""
    print("\n=== 异步TCP回调操作示例 ===")

    # 定义回调函数
    def on_register_read(value):
        print(f"   [回调] 读取到寄存器值: {value}")

    def on_register_write():
        print("   [回调] 寄存器写入完成")

    async with client:
        try:
            print("\n1. 带回调的寄存器读取...")
            registers = await client.read_holding_registers(
                slave_id=1, start_address=0, quantity=1, callback=on_register_read
            )
            print(f"   主线程收到结果: {registers}")

            print("\n2. 带回调的寄存器写入...")
            await client.write_single_register(
                slave_id=1, address=0, value=9999, callback=on_register_write
            )
            print("   主线程写入完成")

            # 等待一下让回调函数执行完成
            await asyncio.sleep(0.1)

        except Exception as e:
            print(f"回调示例失败: {e}")


async def concurrent_operation_example(client: AsyncModbusClient):
    """并发操作示例"""
    print("\n=== 异步TCP并发操作示例 ===")

    async with client:
        try:
            print(
                "\n并发执行多个读取操作..."
            )

            # 创建多个并发任务
            tasks = [
                client.read_holding_registers(slave_id=1, start_address=0, quantity=2),
                client.read_holding_registers(slave_id=1, start_address=2, quantity=2),
                client.read_holding_registers(slave_id=1, start_address=4, quantity=2),
            ]

            # 并发执行所有任务
            start_time = asyncio.get_event_loop().time()
            results = await asyncio.gather(*tasks)
            end_time = asyncio.get_event_loop().time()

            print(
                f"   并发执行耗时: {end_time - start_time:.3f}秒"
            )
            print(f"   保持寄存器0-1: {results[0]}")
            print(f"   保持寄存器2-3: {results[1]}")
            print(f"   保持寄存器4-5: {results[2]}")

        except Exception as e:
            print(f"并发操作失败: {e}")


async def main():
    """主函数"""
    # 设置日志
    ModbusLogger.setup_logging(
        level=logging.INFO,
        enable_debug=True
    )

    set_language(Language.CN)

    # TCP配置
    tcp_config = {
        "host": "127.0.0.1",
        "port": 502,
        "timeout": 1,
    }

    # 创建TCP传输层
    transport = AsyncTcpTransport(
        host=tcp_config["host"],
        port=tcp_config["port"],
        timeout=tcp_config["timeout"],
    )

    # 创建TCP客户端
    client = AsyncModbusClient(transport)

    print(f"异步TCP客户端配置:")
    print(f"  主机: {tcp_config['host']}")
    print(f"  端口: {tcp_config['port']}")
    print(f"  超时: {tcp_config['timeout']}")
    print(f"  注意: 需要一个Modbus TCP设备服务器\n")

    try:
        # 依次执行各个示例
        await basic_operation_example(client)
        await advanced_operation_example(client)
        await callback_operation_example(client)
        await concurrent_operation_example(client)

        print("\n=== 所有示例执行完成 ===")


    except KeyboardInterrupt:
        print("\n收到停止信号")
    except ConnectError as e:
        print(f"\n'ConnectError' 连接错误: {e}")
    except TimeOutError as e:
        print(f"\n'TimeOutError' 超时错误: {e}")
    except CrcError as e:
        print(f"\n'CrcError' CRC校验错误: {e}")
    except ModbusException as e:
        print(f"\n'ModbusException' Modbus协议异常: {e}")
    except Exception as e:
        print(f"\n其他错误错误: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
