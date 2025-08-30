Best Practices Guide
====================

.. contents:: Table of Contents
   :local:
   :depth: 2

This guide contains best practices for developing high-quality, high-performance industrial applications with ModbusLink.

Connection Management
=====================

Use Context Managers
--------------------

**Recommended approach**:

.. code-block:: python

   from modbuslink import ModbusClient, TcpTransport
   
   # ✅ Recommended: Automatic connection management
   transport = TcpTransport(host='192.168.1.100', port=502)
   client = ModbusClient(transport)
   
   with client:
       data = client.read_holding_registers(1, 0, 10)
       client.write_single_register(1, 100, 1234)

**Avoid this approach**:

.. code-block:: python

   # ❌ Avoid: Manual connection management
   client.connect()
   try:
       data = client.read_holding_registers(1, 0, 10)
   finally:
       client.disconnect()  # May be skipped due to exceptions

Connection Pool Pattern
-----------------------

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

Error Handling
==============

Layered Error Handling
----------------------

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
               except ConnectionError as e:
                   self.logger.warning(f"Connection error (attempt {attempt + 1}): {e}")
                   if attempt < max_retries - 1:
                       time.sleep(1)
               except TimeoutError as e:
                   self.logger.warning(f"Timeout error (attempt {attempt + 1}): {e}")
                   if attempt < max_retries - 1:
                       time.sleep(2)
               except CRCError as e:
                   self.logger.error(f"CRC error: {e}")
                   raise  # CRC errors not suitable for retry

Circuit Breaker Pattern
-----------------------

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

Performance Optimization
========================

Batch Operations
----------------

.. code-block:: python

   # ❌ Inefficient: Read one by one
   values = []
   for i in range(100):
       value = client.read_holding_registers(1, i, 1)[0]
       values.append(value)
   
   # ✅ Efficient: Batch read
   values = client.read_holding_registers(1, 0, 100)

Async Concurrency
-----------------

.. code-block:: python

   import asyncio
   from modbuslink import AsyncModbusClient, AsyncTcpTransport
   
   async def parallel_reads():
       client = AsyncModbusClient(AsyncTcpTransport('192.168.1.100', 502))
       
       async with client:
           # Read multiple address ranges in parallel
           tasks = [
               client.read_holding_registers(1, 0, 50),
               client.read_holding_registers(1, 50, 50),
               client.read_holding_registers(1, 100, 50)
           ]
           results = await asyncio.gather(*tasks)
           return sum(results, [])

Data Validation
===============

Input Validation
----------------

.. code-block:: python

   class ModbusDataValidator:
       @staticmethod
       def validate_slave_id(slave_id: int) -> int:
           if not isinstance(slave_id, int):
               raise ValueError(f"Slave ID must be integer: {type(slave_id)}")
           if not (1 <= slave_id <= 247):
               raise ValueError(f"Slave ID range 1-247: {slave_id}")
           return slave_id
   
       @staticmethod
       def validate_address(address: int, max_address: int = 65535) -> int:
           if not isinstance(address, int):
               raise ValueError(f"Address must be integer: {type(address)}")
           if not (0 <= address <= max_address):
               raise ValueError(f"Address range 0-{max_address}: {address}")
           return address
   
   class SafeModbusClient:
       def __init__(self, client):
           self.client = client
           self.validator = ModbusDataValidator()
   
       def safe_read(self, slave_id: int, address: int, count: int):
           slave_id = self.validator.validate_slave_id(slave_id)
           address = self.validator.validate_address(address)
           if not (1 <= count <= 125):
               raise ValueError(f"Read count range 1-125: {count}")
           return self.client.read_holding_registers(slave_id, address, count)

Data Conversion
---------------

.. code-block:: python

   import struct
   
   class ModbusDataConverter:
       @staticmethod
       def registers_to_float32(registers: list, byte_order: str = 'big') -> float:
           if len(registers) != 2:
               raise ValueError(f"Need 2 registers: {len(registers)}")
           
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

Monitoring and Diagnostics
===========================

Performance Monitoring
----------------------

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

Configuration Management
========================

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
               raise ValueError(f"Device config not found: {device_id}")
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

Production Best Practices
=========================

Environment Configuration
-------------------------

.. code-block:: python

   import os
   import logging
   
   class ProductionConfig:
       # Get configuration from environment variables
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

Deployment Checklist
--------------------

**Connection Configuration**
- ✅ Verify network connectivity and device addresses
- ✅ Configure appropriate timeout values
- ✅ Implement connection retry mechanisms

**Error Handling**
- ✅ Implement comprehensive exception catching
- ✅ Configure detailed error logging
- ✅ Design failure recovery strategies

**Performance Optimization**
- ✅ Use batch operations to reduce network overhead
- ✅ Implement connection pooling or long connections
- ✅ Monitor performance metrics

**Security Considerations**
- ✅ Validate input data
- ✅ Restrict access permissions
- ✅ Audit operation logs

**Monitoring and Alerting**
- ✅ Implement health checks
- ✅ Configure performance monitoring
- ✅ Set alert thresholds

Testing Strategy
================

Unit Testing
------------

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

Integration Testing
------------------

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

Summary
=======

Following these best practices will help you:

- 🔒 **Improve Reliability** - Through proper error handling and retry mechanisms
- ⚡ **Optimize Performance** - Using batch operations and async programming
- 🛡️ **Ensure Security** - Through data validation and access control
- 📊 **Ease Maintenance** - Through monitoring, logging, and testing
- 🚀 **Simplify Deployment** - Through configuration management and environment isolation