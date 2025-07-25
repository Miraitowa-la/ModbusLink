#!/usr/bin/env python3
"""ModbusLink 异步集成测试


ModbusLink Async Integration Tests

测试异步客户端、异步传输层和从站模拟器的集成功能。


Tests integration of async client, async transport and slave simulator.
"""

import pytest
import asyncio
import threading
import time
from modbuslink import (
    AsyncModbusClient, AsyncTcpTransport, 
    ModbusSlave, DataStore
)


class TestAsyncIntegration:
    """异步集成测试类 | Async integration test class"""
    
    @pytest.fixture
    def data_store(self):
        """创建测试数据存储区 | Create test data store"""
        store = DataStore()
        # 设置一些初始数据 | Set some initial data
        store.set_holding_registers(0, [1000, 2000, 3000, 4000, 5000])
        store.set_coils(0, [True, False, True, False, True, False, True, False])
        store.set_input_registers(0, [100, 200, 300, 400, 500])
        store.set_discrete_inputs(0, [False, True, False, True, False, True, False, True])
        return store
    
    @pytest.fixture
    def tcp_slave(self, data_store):
        """创建TCP从站模拟器 | Create TCP slave simulator"""
        slave = ModbusSlave(slave_id=1, data_store=data_store)
        slave.start_tcp_server(host='127.0.0.1', port=5020)  # 使用不同端口避免冲突 | Use different port to avoid conflicts
        time.sleep(0.1)  # 等待服务器启动 | Wait for server to start
        yield slave
        slave.stop()
    
    @pytest.fixture
    def async_client(self):
        """创建异步客户端 | Create async client"""
        transport = AsyncTcpTransport(host='127.0.0.1', port=5020, timeout=5.0)
        return AsyncModbusClient(transport)
    
    @pytest.mark.asyncio
    async def test_async_read_holding_registers(self, tcp_slave, async_client):
        """测试异步读取保持寄存器 | Test async read holding registers"""
        async with async_client:
            registers = await async_client.read_holding_registers(slave_id=1, start_address=0, quantity=5)
            assert registers == [1000, 2000, 3000, 4000, 5000]
    
    @pytest.mark.asyncio
    async def test_async_write_single_register(self, tcp_slave, async_client):
        """测试异步写单个寄存器 | Test async write single register"""
        async with async_client:
            # 写入寄存器 | Write register
            await async_client.write_single_register(slave_id=1, address=0, value=9999)
            
            # 验证写入结果 | Verify write result
            registers = await async_client.read_holding_registers(slave_id=1, start_address=0, quantity=1)
            assert registers[0] == 9999
    
    @pytest.mark.asyncio
    async def test_async_write_multiple_registers(self, tcp_slave, async_client):
        """测试异步写多个寄存器 | Test async write multiple registers"""
        async with async_client:
            # 写入多个寄存器 | Write multiple registers
            values = [1111, 2222, 3333]
            await async_client.write_multiple_registers(slave_id=1, start_address=10, values=values)
            
            # 验证写入结果 | Verify write result
            registers = await async_client.read_holding_registers(slave_id=1, start_address=10, quantity=3)
            assert registers == values
    
    @pytest.mark.asyncio
    async def test_async_read_coils(self, tcp_slave, async_client):
        """测试异步读取线圈 | Test async read coils"""
        async with async_client:
            coils = await async_client.read_coils(slave_id=1, start_address=0, quantity=8)
            assert coils == [True, False, True, False, True, False, True, False]
    
    @pytest.mark.asyncio
    async def test_async_write_single_coil(self, tcp_slave, async_client):
        """测试异步写单个线圈 | Test async write single coil"""
        async with async_client:
            # 写入线圈 | Write coil
            await async_client.write_single_coil(slave_id=1, address=0, value=False)
            
            # 验证写入结果 | Verify write result
            coils = await async_client.read_coils(slave_id=1, start_address=0, quantity=1)
            assert coils[0] == False
    
    @pytest.mark.asyncio
    async def test_async_write_multiple_coils(self, tcp_slave, async_client):
        """测试异步写多个线圈 | Test async write multiple coils"""
        async with async_client:
            # 写入多个线圈 | Write multiple coils
            values = [False, True, False, True]
            await async_client.write_multiple_coils(slave_id=1, start_address=0, values=values)
            
            # 验证写入结果 | Verify write result
            coils = await async_client.read_coils(slave_id=1, start_address=0, quantity=4)
            assert coils == values
    
    @pytest.mark.asyncio
    async def test_async_read_input_registers(self, tcp_slave, async_client):
        """测试异步读取输入寄存器 | Test async read input registers"""
        async with async_client:
            registers = await async_client.read_input_registers(slave_id=1, start_address=0, quantity=5)
            assert registers == [100, 200, 300, 400, 500]
    
    @pytest.mark.asyncio
    async def test_async_read_discrete_inputs(self, tcp_slave, async_client):
        """测试异步读取离散输入 | Test async read discrete inputs"""
        async with async_client:
            inputs = await async_client.read_discrete_inputs(slave_id=1, start_address=0, quantity=8)
            assert inputs == [False, True, False, True, False, True, False, True]
    
    @pytest.mark.asyncio
    async def test_async_float32_operations(self, tcp_slave, async_client):
        """测试异步32位浮点数操作 | Test async 32-bit float operations"""
        async with async_client:
            # 写入浮点数 | Write float
            test_value = 3.14159
            await async_client.write_float32(slave_id=1, start_address=20, value=test_value)
            
            # 读取浮点数 | Read float
            read_value = await async_client.read_float32(slave_id=1, start_address=20)
            assert abs(read_value - test_value) < 0.0001  # 浮点数精度比较 | Float precision comparison
    
    @pytest.mark.asyncio
    async def test_async_int32_operations(self, tcp_slave, async_client):
        """测试异步32位整数操作 | Test async 32-bit integer operations"""
        async with async_client:
            # 写入32位整数 | Write 32-bit integer
            test_value = -123456
            await async_client.write_int32(slave_id=1, start_address=22, value=test_value)
            
            # 读取32位整数 | Read 32-bit integer
            read_value = await async_client.read_int32(slave_id=1, start_address=22)
            assert read_value == test_value
    
    @pytest.mark.asyncio
    async def test_async_callback_mechanism(self, tcp_slave, async_client):
        """测试异步回调机制 | Test async callback mechanism"""
        callback_results = []
        
        def register_callback(registers):
            callback_results.append(('registers', registers))
        
        def write_callback():
            callback_results.append(('write_completed', None))
        
        def float_callback(value):
            callback_results.append(('float', value))
        
        async with async_client:
            # 测试读取回调 | Test read callback
            registers = await async_client.read_holding_registers(
                slave_id=1, start_address=0, quantity=3, callback=register_callback
            )
            
            # 测试写入回调 | Test write callback
            await async_client.write_single_register(
                slave_id=1, address=5, value=7777, callback=write_callback
            )
            
            # 测试浮点数回调 | Test float callback
            await async_client.write_float32(slave_id=1, start_address=30, value=2.718)
            float_value = await async_client.read_float32(
                slave_id=1, start_address=30, callback=float_callback
            )
            
            # 等待回调执行 | Wait for callbacks to execute
            await asyncio.sleep(0.1)
            
            # 验证回调结果 | Verify callback results
            assert len(callback_results) == 3
            assert callback_results[0][0] == 'registers'
            assert callback_results[0][1] == [1000, 2000, 3000]
            assert callback_results[1] == ('write_completed', None)
            assert callback_results[2][0] == 'float'
            assert abs(callback_results[2][1] - 2.718) < 0.0001
    
    @pytest.mark.asyncio
    async def test_concurrent_operations(self, tcp_slave, async_client):
        """测试并发操作 | Test concurrent operations"""
        async with async_client:
            # 创建多个并发任务 | Create multiple concurrent tasks
            tasks = [
                async_client.read_holding_registers(slave_id=1, start_address=0, quantity=2),
                async_client.read_holding_registers(slave_id=1, start_address=2, quantity=2),
                async_client.read_coils(slave_id=1, start_address=0, quantity=4),
                async_client.read_input_registers(slave_id=1, start_address=0, quantity=3),
                async_client.read_discrete_inputs(slave_id=1, start_address=0, quantity=4),
            ]
            
            # 并发执行所有任务 | Execute all tasks concurrently
            results = await asyncio.gather(*tasks)
            
            # 验证结果 | Verify results
            assert results[0] == [1000, 2000]  # 保持寄存器0-1 | Holding registers 0-1
            assert results[1] == [3000, 4000]  # 保持寄存器2-3 | Holding registers 2-3
            assert results[2] == [True, False, True, False]  # 线圈0-3 | Coils 0-3
            assert results[3] == [100, 200, 300]  # 输入寄存器0-2 | Input registers 0-2
            assert results[4] == [False, True, False, True]  # 离散输入0-3 | Discrete inputs 0-3
    
    @pytest.mark.asyncio
    async def test_error_handling(self, tcp_slave, async_client):
        """测试错误处理 | Test error handling"""
        async with async_client:
            # 测试无效数量 | Test invalid quantity
            with pytest.raises(ValueError):
                await async_client.read_holding_registers(slave_id=1, start_address=0, quantity=0)
            
            # 测试无效寄存器值 | Test invalid register value
            with pytest.raises(ValueError):
                await async_client.write_single_register(slave_id=1, address=0, value=70000)
    
    def test_data_store_operations(self):
        """测试数据存储区操作 | Test data store operations"""
        store = DataStore()
        
        # 测试线圈操作 | Test coil operations
        coil_values = [True, False, True, False]
        store.set_coils(0, coil_values)
        read_coils = store.get_coils(0, 6)
        assert read_coils[:4] == coil_values
        assert read_coils[4:] == [False, False]  # 未设置的默认为False | Unset defaults to False
        
        # 测试寄存器操作 | Test register operations
        register_values = [1000, 2000, 3000]
        store.set_holding_registers(10, register_values)
        read_registers = store.get_holding_registers(10, 5)
        assert read_registers[:3] == register_values
        assert read_registers[3:] == [0, 0]  # 未设置的默认为0 | Unset defaults to 0
        
        # 测试无效值 | Test invalid values
        with pytest.raises(ValueError):
            store.set_holding_registers(0, [70000])  # 超出范围 | Out of range
    
    def test_slave_lifecycle(self, data_store):
        """测试从站生命周期 | Test slave lifecycle"""
        slave = ModbusSlave(slave_id=1, data_store=data_store)
        
        # 测试启动和停止 | Test start and stop
        slave.start_tcp_server(host='127.0.0.1', port=5021)
        time.sleep(0.1)
        
        # 测试重复启动会抛出异常 | Test duplicate start throws exception
        with pytest.raises(RuntimeError):
            slave.start_tcp_server(host='127.0.0.1', port=5022)
        
        slave.stop()
        
        # 测试停止后可以重新启动 | Test can restart after stop
        slave.start_tcp_server(host='127.0.0.1', port=5021)
        time.sleep(0.1)
        slave.stop()


if __name__ == "__main__":
    # 运行测试 | Run tests
    pytest.main([__file__, "-v"])