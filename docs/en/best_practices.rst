Best Practices Guide
============

This guide contains best practices for developing high-quality, high-performance industrial applications using ModbusLink.

1. Connection Management
-------

1.1 Use Context Managers
~~~~~~~~~~~~~~

**Recommended approach**:

.. code-block:: python

   from modbuslink import SyncModbusClient, SyncTcpTransport
   
   # ✅ Recommended: Automatic connection management
   transport = SyncTcpTransport(host='192.168.1.100', port=502)
   client = SyncModbusClient(transport)
   
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

1.2 Connection Pool Pattern
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

2. Error Handling
-------

2.1 Layered Error Handling
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
                   self.logger.warning(f"Connection error (attempt {attempt + 1}): {e}")
                   if attempt < max_retries - 1:
                       time.sleep(1)
               except TimeOutError as e:
                   self.logger.warning(f"Timeout error (attempt {attempt + 1}): {e}")
                   if attempt < max_retries - 1:
                       time.sleep(2)
               except CrcError as e:
                   self.logger.error(f"CRC error: {e}")
                   raise  # CRC errors are not suitable for retry

2.2 Circuit Breaker Pattern
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

3. Performance Optimization
-------

3.1 Batch Operations
~~~~~~~~

.. code-block:: python

   # ❌ Inefficient: Read individually
   values = []
   for i in range(100):
       value = client.read_holding_registers(1, i, 1)[0]
       values.append(value)
   
   # ✅ Efficient: Batch read
   values = client.read_holding_registers(1, 0, 100)

3.2 Asynchronous Concurrency
~~~~~~~~

.. code-block:: python

   import asyncio
   from modbuslink import AsyncModbusClient, AsyncTcpTransport
   
   async def parallel_reads():
       client = AsyncModbusClient(AsyncTcpTransport('192.168.1.100', 502))
       
       async with client:
           # Parallel read multiple address ranges
           tasks = [
               client.read_holding_registers(1, 0, 50),
               client.read_holding_registers(1, 50, 50),
               client.read_holding_registers(1, 100, 50)
           ]
           results = await asyncio.gather(*tasks)
           return sum(results, [])

4. Data Validation
-------

4.1 Input Validation
~~~~~~~~

.. code-block:: python

   class ModbusDataValidator:
       @staticmethod
       def validate_slave_id(slave_id: int) -> int:
           if not isinstance(slave_id, int):
               raise ValueError(f"Slave ID must be integer: {type(slave_id)}")
           if slave_id < 1 or slave_id > 247:
               raise ValueError(f"Slave ID must be between 1-247: {slave_id}")
           return slave_id
       
       @staticmethod
       def validate_address(address: int) -> int:
           if not isinstance(address, int):
               raise ValueError(f"Address must be integer: {type(address)}")
           if address < 0 or address > 65535:
               raise ValueError(f"Address must be between 0-65535: {address}")
           return address
       
       @staticmethod
       def validate_quantity(quantity: int) -> int:
           if not isinstance(quantity, int):
               raise ValueError(f"Quantity must be integer: {type(quantity)}")
           if quantity < 1 or quantity > 125:
               raise ValueError(f"Quantity must be between 1-125: {quantity}")
           return quantity

4.2 Data Range Validation
~~~~~~~~~~~~

.. code-block:: python

   class DataRangeValidator:
       @staticmethod
       def validate_coil_value(value: bool) -> bool:
           if not isinstance(value, bool):
               raise ValueError(f"Coil value must be boolean: {type(value)}")
           return value
       
       @staticmethod
       def validate_register_value(value: int) -> int:
           if not isinstance(value, int):
               raise ValueError(f"Register value must be integer: {type(value)}")
           if value < 0 or value > 65535:
               raise ValueError(f"Register value must be between 0-65535: {value}")
           return value
       
       @staticmethod
       def validate_float_value(value: float) -> float:
           if not isinstance(value, (int, float)):
               raise ValueError(f"Float value must be numeric: {type(value)}")
           return float(value)

5. Configuration Management
-------

5.1 Environment-Based Configuration
~~~~~~~~~~~~~~~

.. code-block:: python

   import os
   from modbuslink import SyncModbusClient, SyncTcpTransport
   
   class ModbusConfig:
       def __init__(self):
           self.host = os.getenv('MODBUS_HOST', '192.168.1.100')
           self.port = int(os.getenv('MODBUS_PORT', '502'))
           self.timeout = float(os.getenv('MODBUS_TIMEOUT', '5.0'))
           self.slave_id = int(os.getenv('MODBUS_SLAVE_ID', '1'))
   
   def create_client():
       config = ModbusConfig()
       transport = SyncTcpTransport(
           host=config.host,
           port=config.port,
           timeout=config.timeout
       )
       return SyncModbusClient(transport), config.slave_id

5.2 Configuration Files
~~~~~~~~~~~~

.. code-block:: python

   import yaml
   from modbuslink import SyncModbusClient, SyncTcpTransport
   
   class ModbusConfigManager:
       def __init__(self, config_file='modbus_config.yaml'):
           with open(config_file, 'r') as f:
               self.config = yaml.safe_load(f)
       
       def get_client(self, device_name: str):
           device_config = self.config['devices'][device_name]
           transport = SyncTcpTransport(
               host=device_config['host'],
               port=device_config['port'],
               timeout=device_config.get('timeout', 5.0)
           )
           return SyncModbusClient(transport)

6. Testing Strategies
-------

6.1 Unit Testing
~~~~~~~~

.. code-block:: python

   import unittest
   from unittest.mock import Mock, patch
   from modbuslink import SyncModbusClient, SyncTcpTransport
   
   class TestModbusClient(unittest.TestCase):
       def setUp(self):
           self.mock_transport = Mock()
           self.client = SyncModbusClient(self.mock_transport)
       
       def test_read_holding_registers(self):
           # Mock response
           self.mock_transport.send_and_receive.return_value = b'\x03\x04\x00\x01\x00\x02'
           
           result = self.client.read_holding_registers(1, 0, 2)
           
           self.assertEqual(result, [1, 2])
           self.mock_transport.send_and_receive.assert_called_once()

6.2 Integration Testing
~~~~~~~~~~~~~~

.. code-block:: python

   import pytest
   from modbuslink import AsyncTcpModbusServer, ModbusDataStore
   from modbuslink import AsyncModbusClient, AsyncTcpTransport
   
   @pytest.fixture
   async def test_server():
       data_store = ModbusDataStore()
       server = AsyncTcpModbusServer(
           host='127.0.0.1',
           port=5020,
           data_store=data_store
       )
       await server.start()
       yield server
       await server.stop()
   
   @pytest.mark.asyncio
   async def test_client_server_integration(test_server):
       client = AsyncModbusClient(AsyncTcpTransport('127.0.0.1', 5020))
       
       async with client:
           # Test read/write operations
           await client.write_single_register(1, 0, 1234)
           result = await client.read_holding_registers(1, 0, 1)
           
           assert result == [1234]

7. Security Considerations
-------

7.1 Network Security
~~~~~~~~~~

- Use VPN for remote connections
- Implement firewall rules to restrict access
- Use secure protocols (TLS/SSL) when available
- Regularly update firmware and software

7.2 Access Control
~~~~~~~~~

- Implement proper authentication and authorization
- Use least privilege principle for device access
- Monitor and log access attempts
- Regularly review access permissions

8. Monitoring and Logging
-------

8.1 Comprehensive Logging
~~~~~~~~~~~~

.. code-block:: python

   import logging
   from modbuslink import setup_logger
   
   # Configure logging
   setup_logger(
       name='modbuslink',
       level=logging.DEBUG,
       log_file='modbus_operations.log',
       console_output=True,
       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
   )

8.2 Performance Monitoring
~~~~~~~~~~~~~~

.. code-block:: python

   import time
   from functools import wraps
   
   def measure_performance(func):
       @wraps(func)
       async def wrapper(*args, **kwargs):
           start_time = time.time()
           try:
               result = await func(*args, **kwargs)
               return result
           finally:
               end_time = time.time()
               duration = end_time - start_time
               print(f"{func.__name__} took {duration:.3f} seconds")
       return wrapper

   # Usage
   @measure_performance
   async def read_data():
       # Your modbus operations here
       pass

9. Deployment Best Practices
-------

9.1 Containerization
~~~~~~~~~~

.. code-block:: dockerfile

   FROM python:3.11-slim
   
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   
   COPY . .
   
   CMD ["python", "main.py"]

9.2 Health Checks
~~~~~~~~~

.. code-block:: python

   from modbuslink import SyncModbusClient, SyncTcpTransport
   
   class HealthChecker:
       def __init__(self, client):
           self.client = client
       
       def check_health(self) -> bool:
           try:
               # Simple read operation to test connectivity
               self.client.read_holding_registers(1, 0, 1)
               return True
           except Exception:
               return False

10. Summary
-------

Following these best practices will help you build robust, maintainable, and high-performance Modbus applications:

- Use context managers for automatic resource management
- Implement proper error handling and retry mechanisms
- Optimize performance with batch operations and concurrency
- Validate all inputs and data ranges
- Use configuration management for flexibility
- Implement comprehensive testing strategies
- Consider security and monitoring requirements
- Follow deployment best practices