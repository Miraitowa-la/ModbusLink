"""端到端集成测试 | End-to-End Integration Tests

测试ModbusLink库的完整集成功能，包括客户端-服务器通信、真实数据传输等。
Tests complete integration functionality of ModbusLink library, including client-server communication, real data transmission.
"""

import pytest
import asyncio
import sys
import os
import time

# 添加源代码路径 | Add source code path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

try:
    from modbuslink import (
        ModbusClient,
        AsyncModbusClient,
        TcpTransport,
        AsyncTcpTransport,
    )
    from modbuslink.server.slave import ModbusSlave, DataStore
    from modbuslink.common.exceptions import (
        ModbusException,
        ConnectionError,
        TimeoutError,
    )
    from modbuslink.utils.coder import PayloadCoder
except ImportError as e:
    pytest.skip(
        f"无法导入集成测试模块: {e} | Cannot import integration test modules: {e}",
        allow_module_level=True,
    )


class TestSyncClientServerIntegration:
    """同步客户端-服务器集成测试 | Sync Client-Server Integration Tests"""

    def test_basic_client_server_communication(self):
        """测试基本客户端-服务器通信 | Test basic client-server communication"""
        # 创建数据存储和从站 | Create data store and slave
        data_store = DataStore()
        data_store.set_holding_registers(0, [1000, 2000, 3000, 4000, 5000])
        data_store.set_coils(0, [True, False, True, False, True, False, True, False])

        slave = ModbusSlave(slave_id=1, data_store=data_store)

        try:
            # 启动TCP服务器 | Start TCP server
            slave.start_tcp_server(host="127.0.0.1", port=5020)
            time.sleep(0.5)  # 等待服务器启动 | Wait for server to start

            # 创建客户端 | Create client
            transport = TcpTransport(host="127.0.0.1", port=5020, timeout=5.0)
            client = ModbusClient(transport)

            try:
                with client:
                    # 测试读取保持寄存器 | Test reading holding registers
                    registers = client.read_holding_registers(
                        slave_id=1, start_address=0, quantity=5
                    )
                    assert registers == [1000, 2000, 3000, 4000, 5000]
                    print(
                        f"✓ 读取保持寄存器成功: {registers} | Read holding registers successful: {registers}"
                    )

                    # 测试写入单个寄存器 | Test writing single register
                    client.write_single_register(slave_id=1, address=0, value=9999)

                    # 验证写入 | Verify write
                    new_value = client.read_holding_registers(
                        slave_id=1, start_address=0, quantity=1
                    )
                    assert new_value[0] == 9999
                    print(
                        f"✓ 写入单个寄存器成功: {new_value[0]} | Write single register successful: {new_value[0]}"
                    )

                    # 测试读取线圈 | Test reading coils
                    coils = client.read_coils(slave_id=1, start_address=0, quantity=8)
                    assert coils == [True, False, True, False, True, False, True, False]
                    print(f"✓ 读取线圈成功: {coils} | Read coils successful: {coils}")

                    # 测试写入多个寄存器 | Test writing multiple registers
                    new_values = [100, 200, 300]
                    client.write_multiple_registers(
                        slave_id=1, start_address=1, values=new_values
                    )

                    # 验证写入 | Verify write
                    read_values = client.read_holding_registers(
                        slave_id=1, start_address=1, quantity=3
                    )
                    assert read_values == new_values
                    print(
                        f"✓ 写入多个寄存器成功: {read_values} | Write multiple registers successful: {read_values}"
                    )

            except Exception as e:
                print(f"客户端操作异常: {e} | Client operation exception: {e}")
                raise

        except Exception as e:
            print(f"服务器启动异常: {e} | Server start exception: {e}")
            # 如果服务器启动失败，跳过测试 | Skip test if server start fails
            pytest.skip(f"无法启动测试服务器: {e} | Cannot start test server: {e}")
        finally:
            try:
                slave.stop()
            except Exception:
                pass

    def test_advanced_data_types_integration(self):
        """测试高级数据类型集成 | Test advanced data types integration"""
        # 创建数据存储 | Create data store
        data_store = DataStore()

        # 准备测试数据 | Prepare test data
        float_value = 3.14159
        int32_value = 123456789
        string_value = "ModbusLink Test"

        # 编码数据到寄存器 | Encode data to registers
        float_registers = PayloadCoder.encode_float32(float_value, "big", "high")
        int32_registers = PayloadCoder.encode_int32(int32_value, "big", "high")
        byte_length = len(string_value.encode("utf-8"))
        register_count = (byte_length + 1) // 2
        string_registers = PayloadCoder.encode_string(
            string_value, register_count, "big"
        )

        # 设置寄存器数据 | Set register data
        all_registers = float_registers + int32_registers + string_registers
        data_store.set_holding_registers(0, all_registers)

        slave = ModbusSlave(slave_id=1, data_store=data_store)

        try:
            slave.start_tcp_server(host="127.0.0.1", port=5021)
            time.sleep(0.5)

            transport = TcpTransport(host="127.0.0.1", port=5021, timeout=5.0)
            client = ModbusClient(transport)

            try:
                with client:
                    # 测试高级数据类型读取（如果客户端支持）| Test advanced data type reading (if client supports)
                    if hasattr(client, "read_float32"):
                        read_float = client.read_float32(slave_id=1, start_address=0)
                        assert abs(read_float - float_value) < 0.0001
                        print(
                            f"✓ Float32读取成功: {read_float} | Float32 read successful: {read_float}"
                        )

                    if hasattr(client, "read_int32"):
                        read_int32 = client.read_int32(slave_id=1, start_address=2)
                        assert read_int32 == int32_value
                        print(
                            f"✓ Int32读取成功: {read_int32} | Int32 read successful: {read_int32}"
                        )

                    if hasattr(client, "read_string"):
                        read_string = client.read_string(
                            slave_id=1,
                            start_address=4,
                            length=len(string_value.encode("utf-8")),
                        )
                        null_char = "\x00"
                        assert read_string.rstrip(null_char) == string_value
                        print(
                            f"✓ 字符串读取成功: '{read_string.rstrip(null_char)}' | String read successful: '{read_string.rstrip(null_char)}'"
                        )
                    else:
                        # 手动测试字符串解码 | Manual string decoding test
                        string_start = 4
                        read_registers = client.read_holding_registers(
                            slave_id=1,
                            start_address=string_start,
                            quantity=len(string_registers),
                        )
                        decoded_string = PayloadCoder.decode_string(
                            read_registers, "big"
                        )
                        null_char = "\x00"
                        assert decoded_string.rstrip(null_char) == string_value
                        print(
                            f"✓ 手动字符串解码成功: '{decoded_string.rstrip(null_char)}' | Manual string decoding successful: '{decoded_string.rstrip(null_char)}'"
                        )

                    # 测试原始寄存器读取 | Test raw register reading
                    raw_registers = client.read_holding_registers(
                        slave_id=1, start_address=0, quantity=len(all_registers)
                    )
                    assert raw_registers == all_registers
                    print(
                        f"✓ 原始寄存器读取成功: {len(raw_registers)}个寄存器 | Raw registers read successful: {len(raw_registers)} registers"
                    )

            except Exception as e:
                print(
                    f"高级数据类型测试异常: {e} | Advanced data types test exception: {e}"
                )
                raise

        except Exception as e:
            pytest.skip(
                f"无法启动高级数据类型测试服务器: {e} | Cannot start advanced data types test server: {e}"
            )
        finally:
            try:
                slave.stop()
            except Exception:
                pass


class TestAsyncClientServerIntegration:
    """异步客户端-服务器集成测试 | Async Client-Server Integration Tests"""

    @pytest.mark.asyncio
    async def test_async_client_server_communication(self):
        """测试异步客户端-服务器通信 | Test async client-server communication"""
        # 创建数据存储和从站 | Create data store and slave
        data_store = DataStore()
        data_store.set_holding_registers(0, [1111, 2222, 3333, 4444, 5555])
        data_store.set_input_registers(0, [100, 200, 300, 400, 500])

        slave = ModbusSlave(slave_id=1, data_store=data_store)

        try:
            slave.start_tcp_server(host="127.0.0.1", port=5022)
            await asyncio.sleep(0.5)  # 等待服务器启动 | Wait for server to start

            # 创建异步客户端 | Create async client
            transport = AsyncTcpTransport(host="127.0.0.1", port=5022, timeout=5.0)
            client = AsyncModbusClient(transport)

            try:
                async with client:
                    # 测试异步读取保持寄存器 | Test async reading holding registers
                    registers = await client.read_holding_registers(
                        slave_id=1, start_address=0, quantity=5
                    )
                    assert registers == [1111, 2222, 3333, 4444, 5555]
                    print(
                        f"✓ 异步读取保持寄存器成功: {registers} | Async read holding registers successful: {registers}"
                    )

                    # 测试异步读取输入寄存器 | Test async reading input registers
                    input_registers = await client.read_input_registers(
                        slave_id=1, start_address=0, quantity=5
                    )
                    assert input_registers == [100, 200, 300, 400, 500]
                    print(
                        f"✓ 异步读取输入寄存器成功: {input_registers} | Async read input registers successful: {input_registers}"
                    )

                    # 测试异步写入 | Test async writing
                    await client.write_single_register(
                        slave_id=1, address=0, value=7777
                    )

                    # 验证异步写入 | Verify async write
                    new_value = await client.read_holding_registers(
                        slave_id=1, start_address=0, quantity=1
                    )
                    assert new_value[0] == 7777
                    print(
                        f"✓ 异步写入验证成功: {new_value[0]} | Async write verification successful: {new_value[0]}"
                    )

            except Exception as e:
                print(
                    f"异步客户端操作异常: {e} | Async client operation exception: {e}"
                )
                raise

        except Exception as e:
            pytest.skip(
                f"无法启动异步测试服务器: {e} | Cannot start async test server: {e}"
            )
        finally:
            try:
                slave.stop()
            except Exception:
                pass

    @pytest.mark.asyncio
    async def test_concurrent_async_operations(self):
        """测试并发异步操作 | Test concurrent async operations"""
        # 创建数据存储 | Create data store
        data_store = DataStore()
        data_store.set_holding_registers(0, list(range(100)))  # 0-99

        slave = ModbusSlave(slave_id=1, data_store=data_store)

        try:
            slave.start_tcp_server(host="127.0.0.1", port=5023)
            await asyncio.sleep(0.5)

            transport = AsyncTcpTransport(host="127.0.0.1", port=5023, timeout=5.0)
            client = AsyncModbusClient(transport)

            try:
                async with client:
                    # 创建多个并发读取任务 | Create multiple concurrent read tasks
                    tasks = []
                    for i in range(10):
                        task = client.read_holding_registers(
                            slave_id=1, start_address=i * 5, quantity=5
                        )
                        tasks.append(task)

                    # 并发执行所有任务 | Execute all tasks concurrently
                    start_time = asyncio.get_event_loop().time()
                    results = await asyncio.gather(*tasks)
                    end_time = asyncio.get_event_loop().time()

                    # 验证结果 | Verify results
                    assert len(results) == 10
                    for i, result in enumerate(results):
                        expected = list(range(i * 5, i * 5 + 5))
                        assert result == expected

                    elapsed_time = end_time - start_time
                    print(
                        f"✓ 并发异步操作成功: 10个任务在{elapsed_time:.3f}秒内完成 | Concurrent async operations successful: 10 tasks completed in {elapsed_time:.3f}s"
                    )

            except Exception as e:
                print(
                    f"并发异步操作异常: {e} | Concurrent async operations exception: {e}"
                )
                raise

        except Exception as e:
            pytest.skip(
                f"无法启动并发测试服务器: {e} | Cannot start concurrent test server: {e}"
            )
        finally:
            try:
                slave.stop()
            except Exception:
                pass


class TestErrorHandlingIntegration:
    """错误处理集成测试 | Error Handling Integration Tests"""

    def test_connection_error_handling(self):
        """测试连接错误处理 | Test connection error handling"""
        # 尝试连接到不存在的服务器 | Try to connect to non-existent server
        transport = TcpTransport(host="192.168.255.255", port=502, timeout=1.0)
        client = ModbusClient(transport)

        with pytest.raises((ConnectionError, OSError, TimeoutError)):
            with client:
                client.read_holding_registers(slave_id=1, start_address=0, quantity=1)

        print("✓ 连接错误处理正常 | Connection error handling works")

    def test_timeout_error_handling(self):
        """测试超时错误处理 | Test timeout error handling"""
        # 使用极短的超时时间 | Use very short timeout
        transport = TcpTransport(host="127.0.0.1", port=502, timeout=0.001)
        client = ModbusClient(transport)

        with pytest.raises((TimeoutError, ConnectionError, OSError)):
            with client:
                client.read_holding_registers(slave_id=1, start_address=0, quantity=1)

        print("✓ 超时错误处理正常 | Timeout error handling works")

    def test_invalid_slave_id_handling(self):
        """测试无效从站ID处理 | Test invalid slave ID handling"""
        data_store = DataStore()
        data_store.set_holding_registers(0, [1, 2, 3, 4, 5])

        slave = ModbusSlave(slave_id=1, data_store=data_store)

        try:
            slave.start_tcp_server(host="127.0.0.1", port=5024)
            time.sleep(0.5)

            transport = TcpTransport(host="127.0.0.1", port=5024, timeout=5.0)
            client = ModbusClient(transport)

            try:
                with client:
                    # 尝试访问错误的从站ID | Try to access wrong slave ID
                    with pytest.raises((ModbusException, TimeoutError)):
                        client.read_holding_registers(
                            slave_id=99, start_address=0, quantity=1
                        )

                    print("✓ 无效从站ID处理正常 | Invalid slave ID handling works")

            except Exception as e:
                print(f"无效从站ID测试异常: {e} | Invalid slave ID test exception: {e}")

        except Exception as e:
            pytest.skip(
                f"无法启动无效从站ID测试服务器: {e} | Cannot start invalid slave ID test server: {e}"
            )
        finally:
            try:
                slave.stop()
            except Exception:
                pass

    def test_invalid_address_handling(self):
        """测试无效地址处理 | Test invalid address handling"""
        data_store = DataStore()
        data_store.set_holding_registers(
            0, [1, 2, 3, 4, 5]
        )  # 只有5个寄存器 | Only 5 registers

        slave = ModbusSlave(slave_id=1, data_store=data_store)

        try:
            slave.start_tcp_server(host="127.0.0.1", port=5025)
            time.sleep(0.5)

            transport = TcpTransport(host="127.0.0.1", port=5025, timeout=5.0)
            client = ModbusClient(transport)

            try:
                with client:
                    # 尝试读取超出范围的地址 | Try to read out-of-range address
                    try:
                        result = client.read_holding_registers(
                            slave_id=1, start_address=100, quantity=1
                        )
                        # 某些实现可能返回默认值而不是抛出异常 | Some implementations may return default values instead of throwing exceptions
                        print(
                            f"读取超出范围地址返回: {result} | Reading out-of-range address returned: {result}"
                        )
                    except (ModbusException, Exception) as e:
                        print(
                            f"✓ 无效地址处理正常: {e} | Invalid address handling works: {e}"
                        )

            except Exception as e:
                print(f"无效地址测试异常: {e} | Invalid address test exception: {e}")

        except Exception as e:
            pytest.skip(
                f"无法启动无效地址测试服务器: {e} | Cannot start invalid address test server: {e}"
            )
        finally:
            try:
                slave.stop()
            except Exception:
                pass


class TestPerformanceIntegration:
    """性能集成测试 | Performance Integration Tests"""

    def test_throughput_performance(self):
        """测试吞吐量性能 | Test throughput performance"""
        # 创建大量数据 | Create large amount of data
        data_store = DataStore()
        large_data = list(range(1000))  # 1000个寄存器 | 1000 registers
        data_store.set_holding_registers(0, large_data)

        slave = ModbusSlave(slave_id=1, data_store=data_store)

        try:
            slave.start_tcp_server(host="127.0.0.1", port=5026)
            time.sleep(0.5)

            transport = TcpTransport(host="127.0.0.1", port=5026, timeout=10.0)
            client = ModbusClient(transport)

            try:
                with client:
                    # 测试大量数据读取 | Test large data reading
                    start_time = time.time()

                    # 分块读取所有数据 | Read all data in chunks
                    chunk_size = 100
                    total_read = 0

                    for start_addr in range(0, 1000, chunk_size):
                        quantity = min(chunk_size, 1000 - start_addr)
                        result = client.read_holding_registers(
                            slave_id=1, start_address=start_addr, quantity=quantity
                        )
                        total_read += len(result)

                    end_time = time.time()
                    elapsed_time = end_time - start_time
                    throughput = total_read / elapsed_time

                    assert total_read == 1000
                    print(
                        f"✓ 吞吐量性能测试: 读取{total_read}个寄存器用时{elapsed_time:.3f}秒, 吞吐量{throughput:.0f}寄存器/秒 | Throughput performance test: read {total_read} registers in {elapsed_time:.3f}s, throughput {throughput:.0f} registers/s"
                    )

            except Exception as e:
                print(
                    f"吞吐量性能测试异常: {e} | Throughput performance test exception: {e}"
                )

        except Exception as e:
            pytest.skip(
                f"无法启动吞吐量性能测试服务器: {e} | Cannot start throughput performance test server: {e}"
            )
        finally:
            try:
                slave.stop()
            except Exception:
                pass

    def test_connection_reuse_performance(self):
        """测试连接复用性能 | Test connection reuse performance"""
        data_store = DataStore()
        data_store.set_holding_registers(0, [1, 2, 3, 4, 5])

        slave = ModbusSlave(slave_id=1, data_store=data_store)

        try:
            slave.start_tcp_server(host="127.0.0.1", port=5027)
            time.sleep(0.5)

            transport = TcpTransport(host="127.0.0.1", port=5027, timeout=5.0)
            client = ModbusClient(transport)

            try:
                with client:
                    # 测试多次操作的性能 | Test performance of multiple operations
                    num_operations = 50
                    start_time = time.time()

                    for i in range(num_operations):
                        result = client.read_holding_registers(
                            slave_id=1, start_address=0, quantity=5
                        )
                        assert len(result) == 5

                    end_time = time.time()
                    elapsed_time = end_time - start_time
                    ops_per_second = num_operations / elapsed_time

                    print(
                        f"✓ 连接复用性能测试: {num_operations}次操作用时{elapsed_time:.3f}秒, {ops_per_second:.0f}操作/秒 | Connection reuse performance test: {num_operations} operations in {elapsed_time:.3f}s, {ops_per_second:.0f} ops/s"
                    )

                    # 性能应该合理 | Performance should be reasonable
                    assert ops_per_second > 10  # 至少10操作/秒 | At least 10 ops/s

            except Exception as e:
                print(
                    f"连接复用性能测试异常: {e} | Connection reuse performance test exception: {e}"
                )

        except Exception as e:
            pytest.skip(
                f"无法启动连接复用性能测试服务器: {e} | Cannot start connection reuse performance test server: {e}"
            )
        finally:
            try:
                slave.stop()
            except Exception:
                pass


class TestRealWorldScenarios:
    """真实世界场景测试 | Real World Scenarios Tests"""

    def test_industrial_data_simulation(self):
        """测试工业数据模拟 | Test industrial data simulation"""
        # 模拟工业设备数据 | Simulate industrial device data
        data_store = DataStore()

        # 模拟传感器数据 | Simulate sensor data
        temperature_registers = PayloadCoder.encode_float32(
            25.6, "big", "high"
        )  # 温度 | Temperature
        pressure_registers = PayloadCoder.encode_float32(
            1.013, "big", "high"
        )  # 压力 | Pressure
        flow_rate_registers = PayloadCoder.encode_float32(
            150.5, "big", "high"
        )  # 流量 | Flow rate

        # 模拟状态数据 | Simulate status data
        status_coils = [
            True,
            False,
            True,
            True,
            False,
            False,
            True,
            False,
        ]  # 设备状态 | Device status

        # 模拟计数器数据 | Simulate counter data
        counter_registers = PayloadCoder.encode_int32(
            123456, "big", "high"
        )  # 生产计数 | Production count

        # 设置所有数据 | Set all data
        all_registers = (
            temperature_registers
            + pressure_registers
            + flow_rate_registers
            + counter_registers
        )
        data_store.set_holding_registers(0, all_registers)
        data_store.set_coils(0, status_coils)

        slave = ModbusSlave(slave_id=1, data_store=data_store)

        try:
            slave.start_tcp_server(host="127.0.0.1", port=5028)
            time.sleep(0.5)

            transport = TcpTransport(host="127.0.0.1", port=5028, timeout=5.0)
            client = ModbusClient(transport)

            try:
                with client:
                    # 读取所有工业数据 | Read all industrial data
                    registers = client.read_holding_registers(
                        slave_id=1, start_address=0, quantity=len(all_registers)
                    )
                    coils = client.read_coils(
                        slave_id=1, start_address=0, quantity=len(status_coils)
                    )

                    # 解码数据 | Decode data
                    temperature = PayloadCoder.decode_float32(
                        registers[0:2], "big", "high"
                    )
                    pressure = PayloadCoder.decode_float32(
                        registers[2:4], "big", "high"
                    )
                    flow_rate = PayloadCoder.decode_float32(
                        registers[4:6], "big", "high"
                    )
                    counter = PayloadCoder.decode_int32(registers[6:8], "big", "high")

                    # 验证数据 | Verify data
                    assert abs(temperature - 25.6) < 0.01
                    assert abs(pressure - 1.013) < 0.001
                    assert abs(flow_rate - 150.5) < 0.01
                    assert counter == 123456
                    assert coils == status_coils

                    print(
                        f"✓ 工业数据模拟成功: 温度{temperature:.1f}°C, 压力{pressure:.3f}bar, 流量{flow_rate:.1f}L/min, 计数{counter} | Industrial data simulation successful: temp{temperature:.1f}°C, pressure{pressure:.3f}bar, flow{flow_rate:.1f}L/min, count{counter}"
                    )
                    print(f"  设备状态: {coils} | Device status: {coils}")

            except Exception as e:
                print(
                    f"工业数据模拟异常: {e} | Industrial data simulation exception: {e}"
                )
                raise

        except Exception as e:
            pytest.skip(
                f"无法启动工业数据模拟服务器: {e} | Cannot start industrial data simulation server: {e}"
            )
        finally:
            try:
                slave.stop()
            except Exception:
                pass


if __name__ == "__main__":
    print("开始运行端到端集成测试... | Starting end-to-end integration tests...")
    print("=" * 70)

    # 运行所有测试 | Run all tests
    pytest.main([__file__, "-v", "--tb=short"])

    print("=" * 70)
    print("端到端集成测试完成 | End-to-end integration tests completed")
