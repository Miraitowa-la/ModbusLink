最佳实践指南
============

本指南包含使用ModbusLink开发高质量、高性能工业应用的最佳实践。

1. 连接管理
-------

1.1 使用上下文管理器
~~~~~~~~~~~~~~

**推荐方式**：

.. code-block:: python

   from modbuslink import SyncModbusClient, SyncTcpTransport
   
   # ✅ 推荐：自动管理连接
   transport = SyncTcpTransport(host='192.168.1.100', port=502)
   client = SyncModbusClient(transport)
   
   with client:
       data = client.read_holding_registers(1, 0, 10)
       client.write_single_register(1, 100, 1234)

**避免的方式**：

.. code-block:: python

   # ❌ 避免：手动管理连接
   client.connect()
   try:
       data = client.read_holding_registers(1, 0, 10)
   finally:
       client.disconnect()  # 可能因异常而跳过

1.2 连接池模式
~~~~~~~~~~

.. code-block:: python

   import asyncio
   from modbuslink import AsyncModbusClient, AsyncTcpTransport
   
   class ModbusConnectionPool:
       def __init__(self, host: str, port: int, max_connections: int = 10):
           self.host = host
           self.port = port
           self._pool: asyncio.Queue = asyncio.Queue(maxsize=max_connections)
           self._created = 0
           self.max_connections = max_connections
   
       async def get_client(self) -> AsyncModbusClient:
           try:
               return self._pool.get_nowait()
           except asyncio.QueueEmpty:
               if self._created < self.max_connections:
                   transport = AsyncTcpTransport(self.host, self.port)
                   client = AsyncModbusClient(transport)
                   await client.connect()
                   self._created += 1
                   return client
               else:
                   return await self._pool.get()
   
       async def return_client(self, client: AsyncModbusClient):
           try:
               self._pool.put_nowait(client)
           except asyncio.QueueFull:
               await client.disconnect()
               self._created -= 1

2. 错误处理
-------

2.1 分层错误处理
~~~~~~~~~~~

.. code-block:: python

   from modbuslink.common.exceptions import *
   import logging
   import time
   
   class RobustModbusClient:
       def __init__(self, client):
           self.client = client
           self.logger = logging.getLogger(self.__class__.__name__)
   
       def read_with_retry(self, slave_id: int, address: int, count: int, 
                          max_retries: int = 3):
           for attempt in range(max_retries):
               try:
                   return self.client.read_holding_registers(slave_id, address, count)
               except ConnectError as e:
                   self.logger.warning(f"连接错误 (尝试 {attempt + 1}): {e}")
                   if attempt < max_retries - 1:
                       time.sleep(1)
               except TimeOutError as e:
                   self.logger.warning(f"超时错误 (尝试 {attempt + 1}): {e}")
                   if attempt < max_retries - 1:
                       time.sleep(2)
               except CrcError as e:
                   self.logger.error(f"CRC错误: {e}")
                   raise  # CRC错误不适合重试

2.2 断路器模式
~~~~~~~~~~

.. code-block:: python

   import time
   from enum import Enum
   
   class CircuitState(Enum):
       CLOSED = "closed"
       OPEN = "open" 
       HALF_OPEN = "half_open"
   
   class CircuitBreaker:
       def __init__(self, failure_threshold: int = 5, recovery_timeout: float = 60.0):
           self.failure_threshold = failure_threshold
           self.recovery_timeout = recovery_timeout
           self.failure_count = 0
           self.last_failure_time = None
           self.state = CircuitState.CLOSED
   
       def __call__(self, func):
           def wrapper(*args, **kwargs):
               if self.state == CircuitState.OPEN:
                   if time.time() - self.last_failure_time > self.recovery_timeout:
                       self.state = CircuitState.HALF_OPEN
                   else:
                       raise Exception("Circuit breaker is OPEN")
               
               try:
                   result = func(*args, **kwargs)
                   if self.state == CircuitState.HALF_OPEN:
                       self.state = CircuitState.CLOSED
                       self.failure_count = 0
                   return result
               except Exception as e:
                   self.failure_count += 1
                   self.last_failure_time = time.time()
                   if self.failure_count >= self.failure_threshold:
                       self.state = CircuitState.OPEN
                   raise
           return wrapper

3. 性能优化
-------

3.1 批量操作
~~~~~~~~

.. code-block:: python

   # ❌ 低效：逐个读取
   values = []
   for i in range(100):
       value = client.read_holding_registers(1, i, 1)[0]
       values.append(value)
   
   # ✅ 高效：批量读取
   values = client.read_holding_registers(1, 0, 100)

3.2 异步并发
~~~~~~~~

.. code-block:: python

   import asyncio
   from modbuslink import AsyncModbusClient, AsyncTcpTransport
   
   async def parallel_reads():
       client = AsyncModbusClient(AsyncTcpTransport('192.168.1.100', 502))
       
       async with client:
           # 并行读取多个地址段
           tasks = [
               client.read_holding_registers(1, 0, 50),
               client.read_holding_registers(1, 50, 50),
               client.read_holding_registers(1, 100, 50)
           ]
           results = await asyncio.gather(*tasks)
           return sum(results, [])

4. 数据验证
-------

4.1 输入验证
~~~~~~~~

.. code-block:: python

   class ModbusDataValidator:
       @staticmethod
       def validate_slave_id(slave_id: int) -> int:
           if not isinstance(slave_id, int):
               raise ValueError(f"从站ID必须是整数: {type(slave_id)}")
           if not (1 <= slave_id <= 247):
               raise ValueError(f"从站ID范围1-247: {slave_id}")
           return slave_id
   
       @staticmethod
       def validate_address(address: int, max_address: int = 65535) -> int:
           if not isinstance(address, int):
               raise ValueError(f"地址必须是整数: {type(address)}")
           if not (0 <= address <= max_address):
               raise ValueError(f"地址范围0-{max_address}: {address}")
           return address
   
   class SafeModbusClient:
       def __init__(self, client):
           self.client = client
           self.validator = ModbusDataValidator()
   
       def safe_read(self, slave_id: int, address: int, count: int):
           slave_id = self.validator.validate_slave_id(slave_id)
           address = self.validator.validate_address(address)
           if not (1 <= count <= 125):
               raise ValueError(f"读取数量范围1-125: {count}")
           return self.client.read_holding_registers(slave_id, address, count)

4.2 数据转换
~~~~~~~~

.. code-block:: python

   import struct
   
   class ModbusDataConverter:
       @staticmethod
       def registers_to_float32(registers: list, byte_order: str = 'big') -> float:
           if len(registers) != 2:
               raise ValueError(f"需要2个寄存器: {len(registers)}")
           
           if byte_order == 'big':
               data = struct.pack('>HH', registers[0], registers[1])
               return struct.unpack('>f', data)[0]
           else:
               data = struct.pack('<HH', registers[1], registers[0])
               return struct.unpack('<f', data)[0]
   
       @staticmethod
       def float32_to_registers(value: float, byte_order: str = 'big') -> list:
           if byte_order == 'big':
               data = struct.pack('>f', value)
               return list(struct.unpack('>HH', data))
           else:
               data = struct.pack('<f', value)
               reg1, reg2 = struct.unpack('<HH', data)
               return [reg2, reg1]

5. 监控和诊断
---------

5.1 性能监控
~~~~~~~~

.. code-block:: python

   import time
   import statistics
   from collections import deque
   
   class PerformanceMonitor:
       def __init__(self, max_samples: int = 1000):
           self.response_times = deque(maxlen=max_samples)
           self.total_requests = 0
           self.successful_requests = 0
   
       def record_request(self, duration: float, success: bool):
           self.total_requests += 1
           if success:
               self.successful_requests += 1
               self.response_times.append(duration)
   
       @property
       def avg_response_time(self) -> float:
           return statistics.mean(self.response_times) if self.response_times else 0
   
       @property
       def success_rate(self) -> float:
           return self.successful_requests / self.total_requests if self.total_requests else 0
   
   class MonitoredClient:
       def __init__(self, client):
           self.client = client
           self.monitor = PerformanceMonitor()
   
       def read_holding_registers(self, *args, **kwargs):
           start_time = time.time()
           success = False
           try:
               result = self.client.read_holding_registers(*args, **kwargs)
               success = True
               return result
           finally:
               duration = time.time() - start_time
               self.monitor.record_request(duration, success)

6. 配置管理
-------

.. code-block:: python

   import json
   from pathlib import Path
   
   class ModbusConfig:
       def __init__(self, config_path: str):
           self.config_path = Path(config_path)
           self.config = self._load_config()
   
       def _load_config(self):
           with open(self.config_path, 'r', encoding='utf-8') as f:
               return json.load(f)
   
       def get_device_config(self, device_id: str):
           devices = self.config.get('devices', {})
           if device_id not in devices:
               raise ValueError(f"设备配置不存在: {device_id}")
           return devices[device_id]
   
       def create_client(self, device_id: str):
           config = self.get_device_config(device_id)
           
           if config['transport'] == 'tcp':
               transport = TcpTransport(
                   host=config['host'],
                   port=config.get('port', 502),
                   timeout=config.get('timeout', 10.0)
               )
           elif config['transport'] == 'rtu':
               transport = RtuTransport(
                   port=config['port'],
                   baudrate=config.get('baudrate', 9600),
                   timeout=config.get('timeout', 1.0)
               )
           
           return ModbusClient(transport)

7. 生产环境最佳实践
-------

7.1 环境配置
~~~~~~~~

.. code-block:: python

   import os
   import logging
   
   class ProductionConfig:
       # 从环境变量获取配置
       MODBUS_HOST = os.getenv('MODBUS_HOST', '192.168.1.100')
       MODBUS_PORT = int(os.getenv('MODBUS_PORT', '502'))
       MODBUS_TIMEOUT = float(os.getenv('MODBUS_TIMEOUT', '5.0'))
       LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
       
       @classmethod
       def setup_logging(cls):
           logging.basicConfig(
               level=getattr(logging, cls.LOG_LEVEL),
               format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
           )

7.2 部署检查清单
~~~~~~~~~~

**连接配置**
- ✅ 验证网络连接和设备地址
- ✅ 配置适当的超时值
- ✅ 实现连接重试机制

**错误处理**
- ✅ 实现全面的异常捕获
- ✅ 配置详细的错误日志
- ✅ 设计故障恢复策略

**性能优化**
- ✅ 使用批量操作减少网络开销
- ✅ 实现连接池或长连接
- ✅ 监控性能指标

**安全考虑**
- ✅ 验证输入数据
- ✅ 限制访问权限
- ✅ 审计操作日志

**监控告警**
- ✅ 实现健康检查
- ✅ 配置性能监控
- ✅ 设置告警阈值

8. 测试策略
-------

8.1 单元测试
~~~~~~~~

.. code-block:: python

   import unittest
   from unittest.mock import Mock
   
   class TestModbusClient(unittest.TestCase):
       def setUp(self):
           self.mock_transport = Mock()
           self.client = ModbusClient(self.mock_transport)
   
       def test_read_success(self):
           self.mock_transport.send_and_receive.return_value = b'\x01\x03\x04\x00\x01\x00\x02'
           result = self.client.read_holding_registers(1, 0, 2)
           self.assertEqual(result, [1, 2])

8.2 集成测试
~~~~~~~~

.. code-block:: python

   import pytest
   from modbuslink import AsyncTcpModbusServer, ModbusDataStore
   
   @pytest.fixture
   async def test_server():
       data_store = ModbusDataStore()
       server = AsyncTcpModbusServer(data_store, '127.0.0.1', 0)
       await server.start()
       yield server
       await server.stop()

9. 总结
----

遵循这些最佳实践可以帮助您：

- 🔒 **提高可靠性** - 通过正确的错误处理和重试机制
- ⚡ **优化性能** - 使用批量操作和异步编程
- 🛡️ **确保安全** - 通过数据验证和访问控制
- 📊 **便于维护** - 通过监控、日志和测试
- 🚀 **简化部署** - 通过配置管理和环境隔离