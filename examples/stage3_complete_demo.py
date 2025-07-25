#!/usr/bin/env python3
"""ModbusLink 第三阶段完整演示

ModbusLink Stage 3 Complete Demo

本演示展示了第三阶段的所有功能：
- 异步传输层和客户端
- 回调机制
- 从站模拟器
- 并发操作

This demo showcases all Stage 3 features:
- Async transport and client
- Callback mechanism
- Slave simulator
- Concurrent operations
"""

import asyncio
import threading
import time
import logging
from typing import List, Any

# 导入ModbusLink组件 | Import ModbusLink components
from modbuslink import (
    AsyncModbusClient, AsyncTcpTransport,
    ModbusSlave, DataStore,
    ModbusException
)

# 配置日志 | Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Stage3Demo:
    """第三阶段完整演示类 | Stage 3 complete demo class"""
    
    def __init__(self):
        self.slave = None
        self.client = None
        self.callback_results = []
    
    def setup_slave_simulator(self):
        """设置从站模拟器 | Setup slave simulator"""
        logger.info("设置从站模拟器... | Setting up slave simulator...")
        
        # 创建数据存储区 | Create data store
        data_store = DataStore()
        
        # 初始化数据 | Initialize data
        data_store.set_holding_registers(0, [1000, 2000, 3000, 4000, 5000])
        data_store.set_coils(0, [True, False, True, False, True, False, True, False])
        data_store.set_input_registers(0, [100, 200, 300, 400, 500])
        data_store.set_discrete_inputs(0, [False, True, False, True, False, True, False, True])
        
        # 创建从站 | Create slave
        self.slave = ModbusSlave(slave_id=1, data_store=data_store)
        
        # 启动TCP服务器 | Start TCP server
        self.slave.start_tcp_server(host='127.0.0.1', port=5020)
        logger.info("从站模拟器已启动在 127.0.0.1:5020 | Slave simulator started on 127.0.0.1:5020")
        
        # 等待服务器启动 | Wait for server to start
        time.sleep(0.5)
    
    def setup_async_client(self):
        """设置异步客户端 | Setup async client"""
        logger.info("设置异步客户端... | Setting up async client...")
        
        # 创建异步TCP传输层 | Create async TCP transport
        transport = AsyncTcpTransport(host='127.0.0.1', port=5020, timeout=5.0)
        
        # 创建异步客户端 | Create async client
        self.client = AsyncModbusClient(transport)
        logger.info("异步客户端已创建 | Async client created")
    
    def create_callbacks(self):
        """创建回调函数 | Create callback functions"""
        def register_read_callback(registers: List[int]):
            """寄存器读取回调 | Register read callback"""
            self.callback_results.append(f"读取到寄存器: {registers} | Read registers: {registers}")
            logger.info(f"回调: 读取到 {len(registers)} 个寄存器 | Callback: Read {len(registers)} registers")
        
        def coil_read_callback(coils: List[bool]):
            """线圈读取回调 | Coil read callback"""
            self.callback_results.append(f"读取到线圈: {coils} | Read coils: {coils}")
            logger.info(f"回调: 读取到 {len(coils)} 个线圈 | Callback: Read {len(coils)} coils")
        
        def write_callback():
            """写入完成回调 | Write completion callback"""
            self.callback_results.append("写入操作完成 | Write operation completed")
            logger.info("回调: 写入操作完成 | Callback: Write operation completed")
        
        def float_callback(value: float):
            """浮点数回调 | Float callback"""
            self.callback_results.append(f"浮点数值: {value:.4f} | Float value: {value:.4f}")
            logger.info(f"回调: 浮点数值 {value:.4f} | Callback: Float value {value:.4f}")
        
        return {
            'register_read': register_read_callback,
            'coil_read': coil_read_callback,
            'write': write_callback,
            'float': float_callback
        }
    
    async def demo_basic_operations(self, callbacks):
        """演示基本操作 | Demo basic operations"""
        logger.info("\n=== 演示基本操作 | Demo Basic Operations ===")
        
        async with self.client:
            # 读取保持寄存器 | Read holding registers
            logger.info("读取保持寄存器... | Reading holding registers...")
            registers = await self.client.read_holding_registers(
                slave_id=1, start_address=0, quantity=5, 
                callback=callbacks['register_read']
            )
            logger.info(f"保持寄存器: {registers} | Holding registers: {registers}")
            
            # 读取线圈 | Read coils
            logger.info("读取线圈... | Reading coils...")
            coils = await self.client.read_coils(
                slave_id=1, start_address=0, quantity=8,
                callback=callbacks['coil_read']
            )
            logger.info(f"线圈状态: {coils} | Coil states: {coils}")
            
            # 写入单个寄存器 | Write single register
            logger.info("写入单个寄存器... | Writing single register...")
            await self.client.write_single_register(
                slave_id=1, address=0, value=9999,
                callback=callbacks['write']
            )
            
            # 验证写入 | Verify write
            new_value = await self.client.read_holding_registers(
                slave_id=1, start_address=0, quantity=1
            )
            logger.info(f"写入后的值: {new_value[0]} | Value after write: {new_value[0]}")
            
            # 写入多个寄存器 | Write multiple registers
            logger.info("写入多个寄存器... | Writing multiple registers...")
            values = [1111, 2222, 3333, 4444]
            await self.client.write_multiple_registers(
                slave_id=1, start_address=10, values=values,
                callback=callbacks['write']
            )
            
            # 验证写入 | Verify write
            new_values = await self.client.read_holding_registers(
                slave_id=1, start_address=10, quantity=4
            )
            logger.info(f"写入的多个值: {new_values} | Written multiple values: {new_values}")
    
    async def demo_advanced_data_types(self, callbacks):
        """演示高级数据类型 | Demo advanced data types"""
        logger.info("\n=== 演示高级数据类型 | Demo Advanced Data Types ===")
        
        async with self.client:
            # 32位浮点数操作 | 32-bit float operations
            logger.info("32位浮点数操作... | 32-bit float operations...")
            float_value = 3.14159265
            await self.client.write_float32(slave_id=1, start_address=20, value=float_value)
            
            read_float = await self.client.read_float32(
                slave_id=1, start_address=20,
                callback=callbacks['float']
            )
            logger.info(f"写入浮点数: {float_value:.8f} | Written float: {float_value:.8f}")
            logger.info(f"读取浮点数: {read_float:.8f} | Read float: {read_float:.8f}")
            
            # 32位整数操作 | 32-bit integer operations
            logger.info("32位整数操作... | 32-bit integer operations...")
            int_value = -123456789
            await self.client.write_int32(slave_id=1, start_address=22, value=int_value)
            
            read_int = await self.client.read_int32(slave_id=1, start_address=22)
            logger.info(f"写入整数: {int_value} | Written integer: {int_value}")
            logger.info(f"读取整数: {read_int} | Read integer: {read_int}")
    
    async def demo_concurrent_operations(self):
        """演示并发操作 | Demo concurrent operations"""
        logger.info("\n=== 演示并发操作 | Demo Concurrent Operations ===")
        
        async with self.client:
            # 创建多个并发任务 | Create multiple concurrent tasks
            start_time = time.time()
            
            tasks = [
                self.client.read_holding_registers(slave_id=1, start_address=0, quantity=5),
                self.client.read_coils(slave_id=1, start_address=0, quantity=8),
                self.client.read_input_registers(slave_id=1, start_address=0, quantity=5),
                self.client.read_discrete_inputs(slave_id=1, start_address=0, quantity=8),
                self.client.write_single_register(slave_id=1, address=50, value=5555),
                self.client.write_multiple_coils(slave_id=1, start_address=10, values=[True, False, True, False]),
            ]
            
            logger.info(f"启动 {len(tasks)} 个并发任务... | Starting {len(tasks)} concurrent tasks...")
            
            # 并发执行所有任务 | Execute all tasks concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            end_time = time.time()
            logger.info(f"并发操作完成，耗时: {end_time - start_time:.3f}秒 | Concurrent operations completed in {end_time - start_time:.3f}s")
            
            # 显示结果 | Show results
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"任务 {i+1} 失败: {result} | Task {i+1} failed: {result}")
                else:
                    logger.info(f"任务 {i+1} 结果: {result} | Task {i+1} result: {result}")
    
    async def demo_error_handling(self):
        """演示错误处理 | Demo error handling"""
        logger.info("\n=== 演示错误处理 | Demo Error Handling ===")
        
        async with self.client:
            # 测试无效参数 | Test invalid parameters
            try:
                await self.client.read_holding_registers(slave_id=1, start_address=0, quantity=0)
            except ValueError as e:
                logger.info(f"捕获到预期的ValueError: {e} | Caught expected ValueError: {e}")
            
            # 测试超出范围的值 | Test out-of-range values
            try:
                await self.client.write_single_register(slave_id=1, address=0, value=70000)
            except ValueError as e:
                logger.info(f"捕获到预期的ValueError: {e} | Caught expected ValueError: {e}")
            
            # 测试无效从站ID | Test invalid slave ID
            try:
                await self.client.read_holding_registers(slave_id=255, start_address=0, quantity=1)
            except ModbusException as e:
                logger.info(f"捕获到ModbusException: {e} | Caught ModbusException: {e}")
    
    def demo_slave_data_manipulation(self):
        """演示从站数据操作 | Demo slave data manipulation"""
        logger.info("\n=== 演示从站数据操作 | Demo Slave Data Manipulation ===")
        
        if self.slave and self.slave.data_store:
            data_store = self.slave.data_store
            
            # 直接操作数据存储区 | Direct data store manipulation
            logger.info("直接修改从站数据... | Directly modifying slave data...")
            
            # 修改保持寄存器 | Modify holding registers
            new_registers = [7777, 8888, 9999]
            data_store.set_holding_registers(100, new_registers)
            logger.info(f"设置寄存器100-102为: {new_registers} | Set registers 100-102 to: {new_registers}")
            
            # 修改线圈 | Modify coils
            new_coils = [True, True, False, False, True]
            data_store.set_coils(50, new_coils)
            logger.info(f"设置线圈50-54为: {new_coils} | Set coils 50-54 to: {new_coils}")
            
            # 读取修改后的数据 | Read modified data
            read_registers = data_store.get_holding_registers(100, 3)
            read_coils = data_store.get_coils(50, 5)
            logger.info(f"读取寄存器100-102: {read_registers} | Read registers 100-102: {read_registers}")
            logger.info(f"读取线圈50-54: {read_coils} | Read coils 50-54: {read_coils}")
    
    async def run_complete_demo(self):
        """运行完整演示 | Run complete demo"""
        try:
            # 设置组件 | Setup components
            self.setup_slave_simulator()
            self.setup_async_client()
            
            # 创建回调函数 | Create callbacks
            callbacks = self.create_callbacks()
            
            # 运行各种演示 | Run various demos
            await self.demo_basic_operations(callbacks)
            await self.demo_advanced_data_types(callbacks)
            await self.demo_concurrent_operations()
            await self.demo_error_handling()
            self.demo_slave_data_manipulation()
            
            # 显示回调结果 | Show callback results
            logger.info("\n=== 回调结果汇总 | Callback Results Summary ===")
            for i, result in enumerate(self.callback_results, 1):
                logger.info(f"{i}. {result}")
            
            logger.info("\n=== 演示完成 | Demo Completed ===")
            logger.info("第三阶段所有功能演示成功！| All Stage 3 features demonstrated successfully!")
            
        except Exception as e:
            logger.error(f"演示过程中发生错误: {e} | Error during demo: {e}")
            raise
        
        finally:
            # 清理资源 | Cleanup resources
            if self.slave:
                self.slave.stop()
                logger.info("从站模拟器已停止 | Slave simulator stopped")


async def main():
    """主函数 | Main function"""
    logger.info("ModbusLink 第三阶段完整演示开始 | ModbusLink Stage 3 Complete Demo Starting")
    logger.info("="*80)
    
    demo = Stage3Demo()
    await demo.run_complete_demo()
    
    logger.info("="*80)
    logger.info("演示结束 | Demo Finished")


if __name__ == "__main__":
    # 运行演示 | Run demo
    asyncio.run(main())