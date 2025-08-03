Examples
=========

This section provides comprehensive examples demonstrating various features of ModbusLink.

Basic Examples
--------------

Simple TCP Client
~~~~~~~~~~~~~~~~~

.. code-block:: python

   from modbuslink import ModbusClient, TcpTransport

   # Create TCP transport
   transport = TcpTransport(host='192.168.1.100', port=502)
   client = ModbusClient(transport)

   try:
       # Connect to the server
       client.connect()
       
       # Read holding registers
       registers = client.read_holding_registers(
           slave_id=1, 
           start_address=0, 
           quantity=10
       )
       print(f"Registers: {registers}")
       
       # Write single register
       client.write_single_register(
           slave_id=1, 
           address=0, 
           value=1234
       )
       
   finally:
       client.disconnect()

Simple RTU Client
~~~~~~~~~~~~~~~~~

.. code-block:: python

   from modbuslink import ModbusClient, RtuTransport

   # Create RTU transport
   transport = RtuTransport(
       port='COM1',
       baudrate=9600,
       bytesize=8,
       parity='N',
       stopbits=1
   )
   client = ModbusClient(transport)

   with client:
       # Read coils
       coils = client.read_coils(
           slave_id=1, 
           start_address=0, 
           quantity=8
       )
       print(f"Coils: {coils}")
       
       # Write multiple coils
       client.write_multiple_coils(
           slave_id=1, 
           start_address=0, 
           values=[True, False, True, False]
       )

Advanced Examples
-----------------

Asynchronous Operations
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import asyncio
   from modbuslink import AsyncModbusClient, AsyncTcpTransport

   async def async_modbus_operations():
       transport = AsyncTcpTransport(host='192.168.1.100', port=502)
       client = AsyncModbusClient(transport)
       
       async with client:
           # Concurrent read operations
           tasks = [
               client.read_holding_registers(slave_id=1, start_address=0, quantity=10),
               client.read_holding_registers(slave_id=1, start_address=10, quantity=10),
               client.read_holding_registers(slave_id=1, start_address=20, quantity=10)
           ]
           
           results = await asyncio.gather(*tasks)
           for i, registers in enumerate(results):
               print(f"Block {i}: {registers}")
           
           # Sequential write operations
           for i in range(10):
               await client.write_single_register(
                   slave_id=1, 
                   address=i, 
                   value=i * 100
               )

   # Run the async function
   asyncio.run(async_modbus_operations())

Callback Mechanisms
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from modbuslink import AsyncModbusClient, AsyncTcpTransport
   import asyncio

   def on_data_received(data):
       print(f"Data received: {data}")

   def on_error(error):
       print(f"Error occurred: {error}")

   async def callback_example():
       transport = AsyncTcpTransport(host='192.168.1.100', port=502)
       client = AsyncModbusClient(transport)
       
       # Set callbacks
       client.set_data_callback(on_data_received)
       client.set_error_callback(on_error)
       
       async with client:
           # Operations will trigger callbacks
           await client.read_holding_registers(
               slave_id=1, 
               start_address=0, 
               quantity=10
           )

   asyncio.run(callback_example())

Advanced Data Types
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from modbuslink import ModbusClient, TcpTransport

   transport = TcpTransport(host='192.168.1.100', port=502)
   client = ModbusClient(transport)

   with client:
       # Float32 operations
       temperature = 25.6
       client.write_float32(
           slave_id=1, 
           start_address=100, 
           value=temperature
       )
       
       read_temp = client.read_float32(
           slave_id=1, 
           start_address=100
       )
       print(f"Temperature: {read_temp}°C")
       
       # Int32 operations with custom byte/word order
       counter_value = -123456
       client.write_int32(
           slave_id=1, 
           start_address=102, 
           value=counter_value,
           byte_order='little',
           word_order='big'
       )
       
       read_counter = client.read_int32(
           slave_id=1, 
           start_address=102,
           byte_order='little',
           word_order='big'
       )
       print(f"Counter: {read_counter}")
       
       # UInt32 operations
       timestamp = 1640995200  # Unix timestamp
       client.write_uint32(
           slave_id=1, 
           start_address=104, 
           value=timestamp
       )
       
       read_timestamp = client.read_uint32(
           slave_id=1, 
           start_address=104
       )
       print(f"Timestamp: {read_timestamp}")

Performance Testing Examples
----------------------------

Batch Operation Performance
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import time
   import asyncio
   from modbuslink import AsyncModbusClient, AsyncTcpTransport

   async def performance_test():
       transport = AsyncTcpTransport(host='192.168.1.100', port=502)
       client = AsyncModbusClient(transport)
       
       async with client:
           # Test batch read performance
           start_time = time.time()
           
           # Concurrent read of multiple register blocks
           tasks = []
           for i in range(10):
               task = client.read_holding_registers(
                   slave_id=1, 
                   start_address=i*10, 
                   quantity=10
               )
               tasks.append(task)
           
           results = await asyncio.gather(*tasks)
           end_time = time.time()
           
           print(f"Reading 100 registers took: {end_time - start_time:.3f}s")
           print(f"Average per register: {(end_time - start_time)*1000/100:.2f}ms")

   asyncio.run(performance_test())

Connection Pool Example
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import asyncio
   from modbuslink import AsyncModbusClient, AsyncTcpTransport

   class ModbusConnectionPool:
       def __init__(self, host, port, pool_size=5):
           self.host = host
           self.port = port
           self.pool_size = pool_size
           self.connections = asyncio.Queue(maxsize=pool_size)
           
       async def initialize(self):
           for _ in range(self.pool_size):
               transport = AsyncTcpTransport(host=self.host, port=self.port)
               client = AsyncModbusClient(transport)
               await client.connect()
               await self.connections.put(client)
               
       async def get_connection(self):
           return await self.connections.get()
           
       async def return_connection(self, client):
           await self.connections.put(client)
           
       async def close_all(self):
           while not self.connections.empty():
               client = await self.connections.get()
               await client.disconnect()

   # Usage example
   async def use_connection_pool():
       pool = ModbusConnectionPool('192.168.1.100', 502)
       await pool.initialize()
       
       try:
           # Get connection
           client = await pool.get_connection()
           
           # Perform operations
           registers = await client.read_holding_registers(
               slave_id=1, start_address=0, quantity=10
           )
           print(f"Read result: {registers}")
           
           # Return connection
           await pool.return_connection(client)
           
       finally:
           await pool.close_all()

   asyncio.run(use_connection_pool())

Error Handling Examples
-----------------------

Comprehensive Error Handling
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from modbuslink import ModbusClient, TcpTransport
   from modbuslink.common.exceptions import (
       ConnectionError, TimeoutError, CRCError, 
       InvalidResponseError, ModbusException
   )
   import time

   def robust_modbus_client():
       transport = TcpTransport(host='192.168.1.100', port=502, timeout=5.0)
       client = ModbusClient(transport)
       
       max_retries = 3
       retry_delay = 1.0
       
       for attempt in range(max_retries):
           try:
               client.connect()
               
               # Perform operations
               registers = client.read_holding_registers(
                   slave_id=1, 
                   start_address=0, 
                   quantity=10
               )
               print(f"Successfully read registers: {registers}")
               break
               
           except ConnectionError as e:
               print(f"Connection failed (attempt {attempt + 1}): {e}")
               if attempt < max_retries - 1:
                   time.sleep(retry_delay)
                   retry_delay *= 2  # Exponential backoff
               
           except TimeoutError as e:
               print(f"Operation timed out (attempt {attempt + 1}): {e}")
               if attempt < max_retries - 1:
                   time.sleep(retry_delay)
               
           except CRCError as e:
               print(f"CRC error detected: {e}")
               # CRC errors usually indicate communication issues
               break
               
           except InvalidResponseError as e:
               print(f"Invalid response received: {e}")
               break
               
           except ModbusException as e:
               print(f"Modbus protocol error: {e}")
               print(f"Exception code: {e.exception_code}")
               break
               
           except Exception as e:
               print(f"Unexpected error: {e}")
               break
               
           finally:
               try:
                   client.disconnect()
               except:
                   pass

   robust_modbus_client()

Logging Configuration
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from modbuslink import ModbusClient, TcpTransport
   from modbuslink.utils.logger import setup_logger
   import logging

   # Configure logging
   setup_logger(
       name='modbuslink',
       level=logging.DEBUG,
       log_file='modbus_operations.log',
       console_output=True
   )

   # Create client with logging enabled
   transport = TcpTransport(host='192.168.1.100', port=502)
   client = ModbusClient(transport)

   with client:
       # All operations will be logged
       registers = client.read_holding_registers(
           slave_id=1, 
           start_address=0, 
           quantity=10
       )
       
       client.write_single_register(
           slave_id=1, 
           address=0, 
           value=1234
       )

Integration Examples
--------------------

Data Acquisition System
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import asyncio
   import json
   from datetime import datetime
   from modbuslink import AsyncModbusClient, AsyncTcpTransport

   class DataAcquisitionSystem:
       def __init__(self, host, port):
           self.transport = AsyncTcpTransport(host=host, port=port)
           self.client = AsyncModbusClient(self.transport)
           self.data_buffer = []
           
       async def start_acquisition(self, interval=1.0):
           async with self.client:
               while True:
                   try:
                       # Read multiple data points
                       temperature = await self.client.read_float32(
                           slave_id=1, start_address=100
                       )
                       pressure = await self.client.read_float32(
                           slave_id=1, start_address=102
                       )
                       flow_rate = await self.client.read_float32(
                           slave_id=1, start_address=104
                       )
                       
                       # Create data record
                       record = {
                           'timestamp': datetime.now().isoformat(),
                           'temperature': temperature,
                           'pressure': pressure,
                           'flow_rate': flow_rate
                       }
                       
                       self.data_buffer.append(record)
                       print(f"Data acquired: {record}")
                       
                       # Save data periodically
                       if len(self.data_buffer) >= 10:
                           await self.save_data()
                           
                   except Exception as e:
                       print(f"Acquisition error: {e}")
                       
                   await asyncio.sleep(interval)
                   
       async def save_data(self):
           if self.data_buffer:
               filename = f"data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
               with open(filename, 'w') as f:
                   json.dump(self.data_buffer, f, indent=2)
               print(f"Saved {len(self.data_buffer)} records to {filename}")
               self.data_buffer.clear()

   # Usage
   async def main():
       daq = DataAcquisitionSystem('192.168.1.100', 502)
       await daq.start_acquisition(interval=2.0)

   asyncio.run(main())

Process Control System
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import asyncio
   from modbuslink import AsyncModbusClient, AsyncTcpTransport

   class ProcessController:
       def __init__(self, host, port):
           self.transport = AsyncTcpTransport(host=host, port=port)
           self.client = AsyncModbusClient(self.transport)
           self.setpoints = {
               'temperature': 25.0,
               'pressure': 1013.25
           }
           
       async def control_loop(self):
           async with self.client:
               while True:
                   try:
                       # Read process variables
                       current_temp = await self.client.read_float32(
                           slave_id=1, start_address=100
                       )
                       current_pressure = await self.client.read_float32(
                           slave_id=1, start_address=102
                       )
                       
                       # Simple proportional control
                       temp_error = self.setpoints['temperature'] - current_temp
                       pressure_error = self.setpoints['pressure'] - current_pressure
                       
                       # Calculate control outputs
                       heater_output = max(0, min(100, 50 + temp_error * 10))
                       pump_output = max(0, min(100, 50 + pressure_error * 5))
                       
                       # Write control outputs
                       await self.client.write_float32(
                           slave_id=1, start_address=200, value=heater_output
                       )
                       await self.client.write_float32(
                           slave_id=1, start_address=202, value=pump_output
                       )
                       
                       print(f"Temp: {current_temp:.2f}°C (SP: {self.setpoints['temperature']}°C), "
                             f"Heater: {heater_output:.1f}%")
                       print(f"Pressure: {current_pressure:.2f} mbar (SP: {self.setpoints['pressure']} mbar), "
                             f"Pump: {pump_output:.1f}%")
                       
                   except Exception as e:
                       print(f"Control error: {e}")
                       
                   await asyncio.sleep(1.0)  # 1 second control loop
                   
       def set_temperature_setpoint(self, value):
           self.setpoints['temperature'] = value
           
       def set_pressure_setpoint(self, value):
           self.setpoints['pressure'] = value

   # Usage
   async def main():
       controller = ProcessController('192.168.1.100', 502)
       
       # Start control loop
       control_task = asyncio.create_task(controller.control_loop())
       
       # Simulate setpoint changes
       await asyncio.sleep(10)
       controller.set_temperature_setpoint(30.0)
       
       await asyncio.sleep(10)
       controller.set_pressure_setpoint(1020.0)
       
       # Run for a while
       await asyncio.sleep(30)
       control_task.cancel()

   asyncio.run(main())