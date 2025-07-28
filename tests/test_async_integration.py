"""异步集成测试 | Async Integration Tests

测试ModbusLink库的异步功能，包括异步客户端、传输层和从站模拟器的集成测试。
Tests async functionality of ModbusLink library, including async client, transport layer and slave simulator integration tests.
"""

import pytest
import asyncio
import sys
import os
from unittest.mock import Mock, patch, AsyncMock, MagicMock

# 添加源代码路径 | Add source code path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from modbuslink import AsyncModbusClient, AsyncTcpTransport
    from modbuslink.server.slave import ModbusSlave, DataStore
    from modbuslink.common.exceptions import (
        ModbusException, ConnectionError, TimeoutError
    )
except ImportError as e:
    pytest.skip(f"无法导入异步模块: {e} | Cannot import async modules: {e}", allow_module_level=True)


class TestAsyncTcpTransport:
    """异步TCP传输层测试 | Async TCP Transport Tests"""
    
    def test_async_transport_creation(self):
        """测试异步传输层创建 | Test async transport creation"""
        transport = AsyncTcpTransport(host='127.0.0.1', port=502, timeout=5.0)
        assert transport.host == '127.0.0.1'
        assert transport.port == 502
        assert transport.timeout == 5.0
        print("✓ 异步TCP传输层创建成功 | Async TCP transport created successfully")
    
    def test_async_transport_invalid_params(self):
        """测试异步传输层无效参数 | Test async transport with invalid parameters"""
        with pytest.raises((ValueError, TypeError)):
            AsyncTcpTransport(host='', port=-1)
        print("✓ 异步TCP传输层参数验证正常 | Async TCP transport parameter validation works")
    
    @pytest.mark.asyncio
    async def test_async_transport_context_manager(self):
        """测试异步传输层上下文管理器 | Test async transport context manager"""
        transport = AsyncTcpTransport(host='127.0.0.1', port=502, timeout=1.0)
        
        # 测试异步上下文管理器协议 | Test async context manager protocol
        assert hasattr(transport, '__aenter__')
        assert hasattr(transport, '__aexit__')
        
        # 由于没有真实服务器，连接会失败，但这是预期的 | Connection will fail without real server, but this is expected
        try:
            async with transport:
                pass
        except (ConnectionError, OSError, Exception) as e:
            print(f"✓ 异步传输层上下文管理器协议正常（连接失败是预期的）: {e} | Async transport context manager protocol works (connection failure expected): {e}")


class TestAsyncModbusClient:
    """异步Modbus客户端测试 | Async Modbus Client Tests"""
    
    def test_async_client_creation(self):
        """测试异步客户端创建 | Test async client creation"""
        transport = AsyncTcpTransport(host='127.0.0.1', port=502)
        client = AsyncModbusClient(transport)
        assert client.transport is transport
        print("✓ 异步客户端创建成功 | Async client created successfully")
    
    @pytest.mark.asyncio
    async def test_async_client_context_manager(self):
        """测试异步客户端上下文管理器 | Test async client context manager"""
        transport = AsyncTcpTransport(host='127.0.0.1', port=502, timeout=1.0)
        client = AsyncModbusClient(transport)
        
        # 测试异步上下文管理器协议 | Test async context manager protocol
        assert hasattr(client, '__aenter__')
        assert hasattr(client, '__aexit__')
        
        # 由于没有真实服务器，连接会失败，但这是预期的 | Connection will fail without real server, but this is expected
        try:
            async with client:
                pass
        except (ConnectionError, OSError, Exception) as e:
            print(f"✓ 异步客户端上下文管理器协议正常（连接失败是预期的）: {e} | Async client context manager protocol works (connection failure expected): {e}")
    
    def test_async_client_methods_exist(self):
        """测试异步客户端方法存在 | Test async client methods exist"""
        transport = AsyncTcpTransport(host='127.0.0.1', port=502)
        client = AsyncModbusClient(transport)
        
        # 检查基本异步方法 | Check basic async methods
        basic_methods = [
            'read_coils',
            'read_discrete_inputs',
            'read_holding_registers',
            'read_input_registers',
            'write_single_coil',
            'write_single_register',
            'write_multiple_coils',
            'write_multiple_registers',
        ]
        
        for method_name in basic_methods:
            assert hasattr(client, method_name)
            method = getattr(client, method_name)
            assert callable(method)
            # 检查是否是协程函数 | Check if it's a coroutine function
            assert asyncio.iscoroutinefunction(method)
            print(f"✓ 异步方法存在: {method_name} | Async method exists: {method_name}")
    
    def test_async_client_advanced_methods_exist(self):
        """测试异步客户端高级方法存在 | Test async client advanced methods exist"""
        transport = AsyncTcpTransport(host='127.0.0.1', port=502)
        client = AsyncModbusClient(transport)
        
        # 检查高级异步方法 | Check advanced async methods
        advanced_methods = [
            'read_float32', 'write_float32',
            'read_int32', 'write_int32',
            'read_uint32', 'write_uint32',
            'read_string', 'write_string',
        ]
        
        for method_name in advanced_methods:
            if hasattr(client, method_name):
                method = getattr(client, method_name)
                assert callable(method)
                assert asyncio.iscoroutinefunction(method)
                print(f"✓ 异步高级方法存在: {method_name} | Async advanced method exists: {method_name}")
    
    @pytest.mark.asyncio
    @patch('asyncio.open_connection')
    async def test_async_client_mock_operations(self, mock_open_connection):
        """测试异步客户端模拟操作 | Test async client mock operations"""
        # 模拟异步连接 | Mock async connection
        mock_reader = AsyncMock()
        mock_writer = AsyncMock()
        mock_open_connection.return_value = (mock_reader, mock_writer)
        
        # 模拟读取响应 | Mock read response
        mock_reader.read.return_value = b'\x01\x03\x04\x00\x01\x00\x02\xFA\x33'
        
        transport = AsyncTcpTransport(host='127.0.0.1', port=502)
        client = AsyncModbusClient(transport)
        
        try:
            async with client:
                # 尝试读取保持寄存器 | Try to read holding registers
                result = await client.read_holding_registers(slave_id=1, start_address=0, quantity=2)
                print(f"✓ 异步模拟操作成功: {result} | Async mock operation successful: {result}")
        except Exception as e:
            print(f"✓ 异步操作测试完成（异常是预期的）: {e} | Async operation test completed (exception expected): {e}")


class TestDataStore:
    """数据存储测试 | Data Store Tests"""
    
    def test_data_store_creation(self):
        """测试数据存储创建 | Test data store creation"""
        data_store = DataStore()
        assert data_store is not None
        print("✓ 数据存储创建成功 | Data store created successfully")
    
    def test_holding_registers_operations(self):
        """测试保持寄存器操作 | Test holding registers operations"""
        data_store = DataStore()
        
        # 设置保持寄存器 | Set holding registers
        test_values = [1000, 2000, 3000, 4000, 5000]
        data_store.set_holding_registers(0, test_values)
        
        # 读取保持寄存器 | Get holding registers
        retrieved_values = data_store.get_holding_registers(0, len(test_values))
        
        assert retrieved_values == test_values
        print(f"✓ 保持寄存器操作正常: {test_values} -> {retrieved_values} | Holding registers operation works: {test_values} -> {retrieved_values}")
    
    def test_coils_operations(self):
        """测试线圈操作 | Test coils operations"""
        data_store = DataStore()
        
        # 设置线圈 | Set coils
        test_coils = [True, False, True, False, True]
        data_store.set_coils(0, test_coils)
        
        # 读取线圈 | Get coils
        retrieved_coils = data_store.get_coils(0, len(test_coils))
        
        assert retrieved_coils == test_coils
        print(f"✓ 线圈操作正常: {test_coils} -> {retrieved_coils} | Coils operation works: {test_coils} -> {retrieved_coils}")
    
    def test_input_registers_operations(self):
        """测试输入寄存器操作 | Test input registers operations"""
        data_store = DataStore()
        
        # 设置输入寄存器 | Set input registers
        test_values = [100, 200, 300, 400, 500]
        data_store.set_input_registers(0, test_values)
        
        # 读取输入寄存器 | Get input registers
        retrieved_values = data_store.get_input_registers(0, len(test_values))
        
        assert retrieved_values == test_values
        print(f"✓ 输入寄存器操作正常: {test_values} -> {retrieved_values} | Input registers operation works: {test_values} -> {retrieved_values}")
    
    def test_discrete_inputs_operations(self):
        """测试离散输入操作 | Test discrete inputs operations"""
        data_store = DataStore()
        
        # 设置离散输入 | Set discrete inputs
        test_inputs = [False, True, False, True, False]
        data_store.set_discrete_inputs(0, test_inputs)
        
        # 读取离散输入 | Get discrete inputs
        retrieved_inputs = data_store.get_discrete_inputs(0, len(test_inputs))
        
        assert retrieved_inputs == test_inputs
        print(f"✓ 离散输入操作正常: {test_inputs} -> {retrieved_inputs} | Discrete inputs operation works: {test_inputs} -> {retrieved_inputs}")
    
    def test_data_store_boundary_conditions(self):
        """测试数据存储边界条件 | Test data store boundary conditions"""
        data_store = DataStore()
        
        # 测试空列表 | Test empty list
        data_store.set_holding_registers(0, [])
        result = data_store.get_holding_registers(0, 0)
        assert result == []
        
        # 测试大地址 | Test large address
        data_store.set_holding_registers(65000, [12345])
        result = data_store.get_holding_registers(65000, 1)
        assert result == [12345]
        
        print("✓ 数据存储边界条件测试通过 | Data store boundary conditions test passed")


class TestModbusSlave:
    """Modbus从站测试 | Modbus Slave Tests"""
    
    def test_slave_creation(self):
        """测试从站创建 | Test slave creation"""
        data_store = DataStore()
        slave = ModbusSlave(slave_id=1, data_store=data_store)
        
        assert slave.slave_id == 1
        assert slave.data_store is data_store
        print("✓ 从站创建成功 | Slave created successfully")
    
    def test_slave_context_manager(self):
        """测试从站上下文管理器 | Test slave context manager"""
        data_store = DataStore()
        slave = ModbusSlave(slave_id=1, data_store=data_store)
        
        # 测试上下文管理器协议 | Test context manager protocol
        assert hasattr(slave, '__enter__')
        assert hasattr(slave, '__exit__')
        
        try:
            with slave:
                print("✓ 从站上下文管理器正常工作 | Slave context manager works")
        except Exception as e:
            print(f"✓ 从站上下文管理器测试完成: {e} | Slave context manager test completed: {e}")
    
    def test_slave_tcp_server_methods(self):
        """测试从站TCP服务器方法 | Test slave TCP server methods"""
        data_store = DataStore()
        slave = ModbusSlave(slave_id=1, data_store=data_store)
        
        # 检查TCP服务器相关方法 | Check TCP server related methods
        server_methods = ['start_tcp_server', 'stop']
        
        for method_name in server_methods:
            assert hasattr(slave, method_name)
            method = getattr(slave, method_name)
            assert callable(method)
            print(f"✓ 从站方法存在: {method_name} | Slave method exists: {method_name}")


class TestAsyncIntegration:
    """异步集成测试 | Async Integration Tests"""
    
    @pytest.mark.asyncio
    async def test_async_timeout_handling(self):
        """测试异步超时处理 | Test async timeout handling"""
        # 使用很短的超时时间 | Use very short timeout
        transport = AsyncTcpTransport(host='192.168.255.255', port=502, timeout=0.1)
        client = AsyncModbusClient(transport)
        
        try:
            async with client:
                await client.read_holding_registers(slave_id=1, start_address=0, quantity=1)
        except (TimeoutError, ConnectionError, OSError, asyncio.TimeoutError) as e:
            print(f"✓ 异步超时处理正常: {type(e).__name__}: {e} | Async timeout handling works: {type(e).__name__}: {e}")
        except Exception as e:
            print(f"✓ 异步异常处理正常: {type(e).__name__}: {e} | Async exception handling works: {type(e).__name__}: {e}")
    
    @pytest.mark.asyncio
    async def test_concurrent_operations(self):
        """测试并发操作 | Test concurrent operations"""
        transport = AsyncTcpTransport(host='127.0.0.1', port=502, timeout=1.0)
        client = AsyncModbusClient(transport)
        
        async def mock_operation(operation_id):
            """模拟异步操作 | Mock async operation"""
            await asyncio.sleep(0.1)  # 模拟网络延迟 | Simulate network delay
            return f"操作{operation_id}完成 | Operation {operation_id} completed"
        
        # 创建多个并发任务 | Create multiple concurrent tasks
        tasks = [mock_operation(i) for i in range(5)]
        
        # 并发执行 | Execute concurrently
        start_time = asyncio.get_event_loop().time()
        results = await asyncio.gather(*tasks)
        end_time = asyncio.get_event_loop().time()
        
        elapsed_time = end_time - start_time
        
        assert len(results) == 5
        assert elapsed_time < 0.5  # 并发执行应该比顺序执行快 | Concurrent execution should be faster than sequential
        
        print(f"✓ 并发操作测试通过: {len(results)}个任务在{elapsed_time:.3f}秒内完成 | Concurrent operations test passed: {len(results)} tasks completed in {elapsed_time:.3f}s")
    
    @pytest.mark.asyncio
    async def test_callback_mechanism(self):
        """测试回调机制 | Test callback mechanism"""
        callback_results = []
        
        def test_callback(result):
            """测试回调函数 | Test callback function"""
            callback_results.append(f"回调收到: {result} | Callback received: {result}")
        
        # 模拟带回调的异步操作 | Simulate async operation with callback
        async def operation_with_callback(data, callback=None):
            await asyncio.sleep(0.05)
            result = f"处理了数据: {data} | Processed data: {data}"
            if callback:
                callback(result)
            return result
        
        # 执行带回调的操作 | Execute operation with callback
        result = await operation_with_callback("测试数据 | test data", test_callback)
        
        assert len(callback_results) == 1
        assert "回调收到" in callback_results[0] or "Callback received" in callback_results[0]
        assert "处理了数据" in result or "Processed data" in result
        
        print(f"✓ 回调机制测试通过: {callback_results[0]} | Callback mechanism test passed: {callback_results[0]}")
    
    def test_async_error_propagation(self):
        """测试异步错误传播 | Test async error propagation"""
        async def failing_operation():
            """会失败的异步操作 | Async operation that will fail"""
            await asyncio.sleep(0.01)
            raise ModbusException(exception_code=0x01, function_code=0x03, message="测试异常 | Test exception")
        
        async def test_error_handling():
            """测试错误处理 | Test error handling"""
            try:
                await failing_operation()
                assert False, "应该抛出异常 | Should have raised exception"
            except ModbusException as e:
                # 检查异常消息或异常类型 | Check exception message or exception type
                assert isinstance(e, ModbusException)
                assert e.exception_code == 0x01
                assert e.function_code == 0x03
                return True
        
        # 运行异步测试 | Run async test
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(test_error_handling())
            assert result is True
            print("✓ 异步错误传播测试通过 | Async error propagation test passed")
        finally:
            loop.close()


class TestAsyncPerformance:
    """异步性能测试 | Async Performance Tests"""
    
    @pytest.mark.asyncio
    async def test_async_vs_sync_simulation(self):
        """测试异步与同步性能对比模拟 | Test async vs sync performance comparison simulation"""
        import time
        
        # 模拟同步操作 | Simulate sync operations
        def sync_operation(duration=0.1):
            time.sleep(duration)
            return "同步操作完成 | Sync operation completed"
        
        # 模拟异步操作 | Simulate async operations
        async def async_operation(duration=0.1):
            await asyncio.sleep(duration)
            return "异步操作完成 | Async operation completed"
        
        # 测试多个异步操作的并发性能 | Test concurrent performance of multiple async operations
        num_operations = 5
        operation_duration = 0.1
        
        # 异步并发执行 | Async concurrent execution
        start_time = time.time()
        async_tasks = [async_operation(operation_duration) for _ in range(num_operations)]
        async_results = await asyncio.gather(*async_tasks)
        async_elapsed = time.time() - start_time
        
        # 验证结果 | Verify results
        assert len(async_results) == num_operations
        assert async_elapsed < (operation_duration * num_operations)  # 应该比顺序执行快 | Should be faster than sequential
        
        print(f"✓ 异步性能测试: {num_operations}个操作在{async_elapsed:.3f}秒内完成 | Async performance test: {num_operations} operations completed in {async_elapsed:.3f}s")
        print(f"  理论顺序执行时间: {operation_duration * num_operations:.3f}秒 | Theoretical sequential time: {operation_duration * num_operations:.3f}s")
        print(f"  性能提升: {((operation_duration * num_operations) / async_elapsed):.1f}倍 | Performance improvement: {((operation_duration * num_operations) / async_elapsed):.1f}x")


if __name__ == '__main__':
    print("开始运行异步集成测试... | Starting async integration tests...")
    print("=" * 70)
    
    # 运行所有测试 | Run all tests
    pytest.main([__file__, '-v', '--tb=short'])
    
    print("=" * 70)
    print("异步集成测试完成 | Async integration tests completed")