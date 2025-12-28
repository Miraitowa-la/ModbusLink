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

Simple ASCII Client
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from modbuslink import ModbusClient, AsciiTransport

   # Create ASCII transport
   transport = AsciiTransport(
       port='COM1',
       baudrate=9600,
       bytesize=7,
       parity='E',
       stopbits=1
   )
   client = ModbusClient(transport)

   with client:
       # Read holding registers
       registers = client.read_holding_registers(
           slave_id=1, 
           start_address=0, 
           quantity=4
       )
       print(f"Registers: {registers}")
       
       # Write single register
       client.write_single_register(
           slave_id=1, 
           address=0, 
           value=1234
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

Asynchronous RTU Operations
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import asyncio
   from modbuslink import AsyncModbusClient, AsyncRtuTransport

   async def async_rtu_operations():
       transport = AsyncRtuTransport(
           port='COM1',
           baudrate=9600,
           timeout=3.0
       )
       client = AsyncModbusClient(transport)
       
       async with client:
           # Async read holding registers
           registers = await client.read_holding_registers(
               slave_id=1, 
               start_address=0, 
               quantity=10
           )
           print(f"Registers: {registers}")
           
           # Async write multiple registers
           await client.write_multiple_registers(
               slave_id=1, 
               start_address=0, 
               values=[100, 200, 300, 400]
           )

   asyncio.run(async_rtu_operations())

Asynchronous ASCII Operations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import asyncio
   from modbuslink import AsyncModbusClient, AsyncAsciiTransport

   async def async_ascii_operations():
       transport = AsyncAsciiTransport(
           port='COM1',
           baudrate=9600,
           timeout=3.0
       )
       client = AsyncModbusClient(transport)
       
       async with client:
           # Async read coils
           coils = await client.read_coils(
               slave_id=1, 
               start_address=0, 
               quantity=8
           )
           print(f"Coils: {coils}")
           
           # Async write single coil
           await client.write_single_coil(
               slave_id=1, 
               address=0, 
               value=True
           )

   asyncio.run(async_ascii_operations())

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

Server Examples
---------------

Basic TCP Server
~~~~~~~~~~~~~~~~

.. code-block:: python

   from modbuslink import AsyncTcpModbusServer, ModbusDataStore
   import asyncio
   import logging

   async def main():
       # Setup logging
       logging.basicConfig(level=logging.INFO)
       
       # Create data store
       data_store = ModbusDataStore(
           coils_size=1000,
           discrete_inputs_size=1000,
           holding_registers_size=1000,
           input_registers_size=1000
       )
       
       # Set initial data
       data_store.write_coils(0, [True, False, True, False, True, False, True, False])
       data_store.write_holding_registers(0, [100, 200, 300, 400, 500])
       data_store.write_input_registers(0, [250, 251, 252, 253, 254])
       data_store.write_discrete_inputs(0, [False, True, False, True, False, True, False, True])
       
       # Create TCP server
       server = AsyncTcpModbusServer(
           host="localhost",
           port=5020,
           data_store=data_store,
           slave_id=1,
           max_connections=5
       )
       
       print("Starting TCP server: localhost:5020")
       print("Slave ID: 1")
       
       try:
           # Start server
           await server.start()
           print("TCP server started successfully!")
           
           # Run forever
           await server.serve_forever()
           
       except KeyboardInterrupt:
           print("\nReceived stop signal")
       finally:
           print("Stopping server...")
           await server.stop()
           print("Server stopped")

   asyncio.run(main())

RTU Server Example
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from modbuslink import AsyncRtuModbusServer, ModbusDataStore
   import asyncio
   import random
   import math

   async def simulate_industrial_data(data_store):
       """Simulate industrial equipment data"""
       cycle = 0
       
       while True:
           try:
               cycle += 1
               
               # Simulate temperature sensor data
               base_temps = [248, 179, 318, 447, 682]
               temp_variations = [base + random.randint(-5, 5) + int(3 * math.sin(cycle * 0.1)) for base in base_temps]
               data_store.write_input_registers(0, temp_variations)
               
               # Simulate pressure sensor data
               base_pressures = [1015, 1027, 996, 1043, 1004]
               pressure_variations = [base + random.randint(-3, 3) + int(2 * math.cos(cycle * 0.15)) for base in base_pressures]
               data_store.write_input_registers(10, pressure_variations)
               
               # Simulate motor speed changes
               current_speeds = data_store.read_holding_registers(0, 5)
               new_speeds = [speed + random.randint(-50, 50) for speed in current_speeds]
               new_speeds = [max(500, min(4000, speed)) for speed in new_speeds]
               data_store.write_holding_registers(0, new_speeds)
               
               if cycle % 20 == 0:
                   print(f"Industrial data update #{cycle}")
                   print(f"  Temperature: {temp_variations}")
                   print(f"  Pressure: {pressure_variations}")
                   print(f"  Motor speeds: {new_speeds}")
               
               await asyncio.sleep(2.0)
               
           except Exception as e:
               print(f"Data simulation error: {e}")
               await asyncio.sleep(2.0)

   async def main():
       # Create data store
       data_store = ModbusDataStore(
           coils_size=1000,
           discrete_inputs_size=1000,
           holding_registers_size=1000,
           input_registers_size=1000
       )
       
       # Initialize industrial equipment data
       data_store.write_coils(0, [True, False, True, True, False, False, True, False])  # Motor status
       data_store.write_coils(8, [False, True, False, True, True, False, False, True])  # Valve status
       data_store.write_holding_registers(0, [1500, 2800, 3600, 1200, 750])  # Motor parameters
       data_store.write_input_registers(0, [248, 179, 318, 447, 682])  # Temperature sensors
       data_store.write_discrete_inputs(0, [True, False, True, True, False, True, False, True])  # Limit switches
       
       # Create RTU server
       server = AsyncRtuModbusServer(
           port="COM3",  # Modify according to actual situation
           baudrate=9600,
           data_store=data_store,
           slave_id=1,
           parity="N",
           stopbits=1,
           bytesize=8,
           timeout=1.0
       )
       
       print("RTU server configuration:")
       print("  Port: COM3")
       print("  Baudrate: 9600")
       print("  Data bits: 8, Stop bits: 1, Parity: None")
       print("  Slave ID: 1")
       
       try:
           # Start server
           await server.start()
           print("RTU server started successfully!")
           
           # Start data simulation task
           simulation_task = asyncio.create_task(simulate_industrial_data(data_store))
           server_task = asyncio.create_task(server.serve_forever())
           
           # Wait for tasks to complete
           await asyncio.gather(simulation_task, server_task)
           
       except KeyboardInterrupt:
           print("\nReceived stop signal")
       except Exception as e:
           print(f"\nServer runtime error: {e}")
       finally:
           print("Stopping server...")
           await server.stop()
           print("Server stopped")

   asyncio.run(main())

ASCII Server Example
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from modbuslink import AsyncAsciiModbusServer, ModbusDataStore
   import asyncio
   import random
   import math

   async def simulate_laboratory_experiment(data_store):
       """Simulate laboratory experiment process"""
       experiment_time = 0
       
       while True:
           try:
               experiment_time += 1
               
               # Simulate temperature control process
               target_temps = data_store.read_holding_registers(0, 5)
               current_temps = data_store.read_input_registers(0, 5)
               
               # Temperature gradually approaches target value
               new_temps = []
               for i, (current, target) in enumerate(zip(current_temps, target_temps)):
                   diff = target - current
                   change = diff * 0.1 + random.randint(-2, 2) + math.sin(experiment_time * 0.05) * 1
                   new_temp = current + change
                   new_temps.append(int(max(0, min(500, new_temp))))
               
               data_store.write_input_registers(0, new_temps)
               
               # Simulate humidity changes
               base_humidity = [45, 52, 38, 48, 55]
               humidity_variations = [base + random.randint(-5, 5) + int(2 * math.cos(experiment_time * 0.08)) for base in base_humidity]
               humidity_variations = [max(0, min(100, h)) for h in humidity_variations]
               data_store.write_input_registers(10, humidity_variations)
               
               # Simulate pH value changes
               base_ph = [700, 650, 720, 680, 710]
               ph_variations = [base + random.randint(-10, 10) + int(3 * math.sin(experiment_time * 0.03)) for base in base_ph]
               ph_variations = [max(0, min(1400, ph)) for ph in ph_variations]
               data_store.write_input_registers(20, ph_variations)
               
               if experiment_time % 15 == 0:
                   print(f"Experiment process simulation #{experiment_time}")
                   print(f"  Temperature: {new_temps}")
                   print(f"  Humidity: {humidity_variations}%")
                   print(f"  pH: {[ph/100.0 for ph in ph_variations]}")
               
               await asyncio.sleep(3.0)
               
           except Exception as e:
               print(f"Experiment simulation error: {e}")
               await asyncio.sleep(3.0)

   async def main():
       # Create data store
       data_store = ModbusDataStore(
           coils_size=1000,
           discrete_inputs_size=1000,
           holding_registers_size=1000,
           input_registers_size=1000
       )
       
       # Initialize laboratory equipment data
       data_store.write_coils(0, [False, True, False, True, False, False, True, False])  # Heater control
       data_store.write_coils(8, [True, True, False, False, True, True, False, False])  # Fan control
       data_store.write_holding_registers(0, [250, 300, 180, 220, 350])  # Target temperature
       data_store.write_input_registers(0, [248, 298, 178, 218, 348])  # Actual temperature
       data_store.write_discrete_inputs(0, [False, True, False, False, True, True, False, True])  # Door switch status
       
       # Create ASCII server
       server = AsyncAsciiModbusServer(
           port="COM4",  # Modify according to actual situation
           baudrate=9600,
           data_store=data_store,
           slave_id=2,
           parity="E",
           stopbits=1,
           bytesize=7,
           timeout=2.0
       )
       
       print("ASCII server configuration:")
       print("  Port: COM4")
       print("  Baudrate: 9600")
       print("  Data bits: 7, Stop bits: 1, Parity: Even")
       print("  Slave ID: 2")
       
       try:
           # Start server
           await server.start()
           print("ASCII server started successfully!")
           
           # Start experiment simulation task
           simulation_task = asyncio.create_task(simulate_laboratory_experiment(data_store))
           server_task = asyncio.create_task(server.serve_forever())
           
           # Wait for tasks to complete
           await asyncio.gather(simulation_task, server_task)
           
       except KeyboardInterrupt:
           print("\nReceived stop signal")
       except Exception as e:
           print(f"\nServer runtime error: {e}")
       finally:
           print("Stopping server...")
           await server.stop()
           print("Server stopped")

   asyncio.run(main())

Multi-Server Example
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from modbuslink import (
       AsyncTcpModbusServer,
       AsyncRtuModbusServer, 
       AsyncAsciiModbusServer,
       ModbusDataStore
   )
   import asyncio
   import random

   class MultiServerManager:
       """Multi-server manager"""
       
       def __init__(self):
           self.servers = {}
           self.data_stores = {}
           self.running = False
       
       async def setup_servers(self):
           """Setup all servers"""
           # TCP server
           tcp_data_store = ModbusDataStore(coils_size=1000, discrete_inputs_size=1000,
                                          holding_registers_size=1000, input_registers_size=1000)
           tcp_data_store.write_coils(0, [True, False, True, False] * 10)
           tcp_data_store.write_holding_registers(0, list(range(100, 150)))
           
           tcp_server = AsyncTcpModbusServer(
               host="localhost", port=5020, data_store=tcp_data_store, slave_id=1
           )
           
           self.servers["tcp"] = tcp_server
           self.data_stores["tcp"] = tcp_data_store
           
           # RTU server
           rtu_data_store = ModbusDataStore(coils_size=1000, discrete_inputs_size=1000,
                                          holding_registers_size=1000, input_registers_size=1000)
           rtu_data_store.write_coils(0, [False, True, False, True] * 8)
           rtu_data_store.write_holding_registers(0, [1500, 2800, 3600, 1200, 750])
           
           rtu_server = AsyncRtuModbusServer(
               port="COM3", baudrate=9600, data_store=rtu_data_store, slave_id=2
           )
           
           self.servers["rtu"] = rtu_server
           self.data_stores["rtu"] = rtu_data_store
           
           # ASCII server
           ascii_data_store = ModbusDataStore(coils_size=1000, discrete_inputs_size=1000,
                                            holding_registers_size=1000, input_registers_size=1000)
           ascii_data_store.write_coils(0, [True, True, False, False] * 8)
           ascii_data_store.write_holding_registers(0, [250, 300, 180, 220, 350])
           
           ascii_server = AsyncAsciiModbusServer(
               port="COM4", baudrate=9600, data_store=ascii_data_store, slave_id=3,
               parity="E", stopbits=1, bytesize=7
           )
           
           self.servers["ascii"] = ascii_server
           self.data_stores["ascii"] = ascii_data_store
       
       async def start_all_servers(self):
           """Start all servers"""
           print("Starting all servers...")
           
           for server_type, server in self.servers.items():
               try:
                   await server.start()
                   print(f"{server_type.upper()} server started successfully")
               except Exception as e:
                   print(f"{server_type.upper()} server failed to start: {e}")
           
           self.running = True
       
       async def stop_all_servers(self):
           """Stop all servers"""
           print("Stopping all servers...")
           
           for server_type, server in self.servers.items():
               try:
                   await server.stop()
                   print(f"{server_type.upper()} server stopped")
               except Exception as e:
                   print(f"{server_type.upper()} server failed to stop: {e}")
           
           self.running = False
       
       async def simulate_data_changes(self):
           """Simulate data changes"""
           cycle = 0
           
           while self.running:
               try:
                   cycle += 1
                   
                   # Update data for each server
                   for server_type, store in self.data_stores.items():
                       if server_type == "tcp":
                           # Network monitoring data
                           traffic_data = [random.randint(100, 1000) for _ in range(10)]
                           store.write_input_registers(50, traffic_data)
                       elif server_type == "rtu":
                           # Industrial process data
                           temp_data = [random.randint(200, 400) for _ in range(5)]
                           store.write_input_registers(0, temp_data)
                       elif server_type == "ascii":
                           # Laboratory data
                           lab_data = [random.randint(180, 350) for _ in range(5)]
                           store.write_input_registers(0, lab_data)
                       
                       # Update counter
                       store.write_holding_registers(999, [cycle])
                   
                   if cycle % 20 == 0:
                       print(f"Data simulation cycle #{cycle}")
                   
                   await asyncio.sleep(2.0)
                   
               except Exception as e:
                   print(f"Data simulation error: {e}")
                   await asyncio.sleep(2.0)
       
       async def serve_forever(self):
           """Run forever"""
           # Start data simulation task
           simulation_task = asyncio.create_task(self.simulate_data_changes())
           
           # Start serve_forever tasks for all servers
           server_tasks = []
           for server_type, server in self.servers.items():
               try:
                   if await server.is_running():
                       server_tasks.append(asyncio.create_task(server.serve_forever()))
               except Exception as e:
                   print(f"{server_type.upper()} server serve_forever failed to start: {e}")
           
           # Wait for all tasks to complete
           all_tasks = [simulation_task] + server_tasks
           await asyncio.gather(*all_tasks, return_exceptions=True)

   async def main():
       manager = MultiServerManager()
       
       try:
           # Configure and start servers
           await manager.setup_servers()
           await manager.start_all_servers()
           
           print("\nConnection information:")
           print("  TCP server: localhost:5020 (Slave ID 1)")
           print("  RTU server: COM3@9600,8,N,1 (Slave ID 2)")
           print("  ASCII server: COM4@9600,7,E,1 (Slave ID 3)")
           print("\nPress Ctrl+C to stop all servers")
           
           # Run forever
           await manager.serve_forever()
           
       except KeyboardInterrupt:
           print("\nReceived stop signal")
       except Exception as e:
           print(f"\nMulti-server runtime error: {e}")
       finally:
           await manager.stop_all_servers()

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