示例
====

本节提供了展示ModbusLink各种功能的综合示例。

基础示例
--------

简单TCP客户端
~~~~~~~~~~~~~

.. code-block:: python

   from modbuslink import ModbusClient, TcpTransport

   # 创建TCP传输层
   transport = TcpTransport(host='192.168.1.100', port=502)
   client = ModbusClient(transport)

   try:
       # 连接到服务器
       client.connect()
       
       # 读取保持寄存器
       registers = client.read_holding_registers(
           slave_id=1, 
           start_address=0, 
           quantity=10
       )
       print(f"寄存器: {registers}")
       
       # 写入单个寄存器
       client.write_single_register(
           slave_id=1, 
           address=0, 
           value=1234
       )
       
   finally:
       client.disconnect()

简单RTU客户端
~~~~~~~~~~~~~

.. code-block:: python

   from modbuslink import ModbusClient, RtuTransport

   # 创建RTU传输层
   transport = RtuTransport(
       port='COM1',
       baudrate=9600,
       bytesize=8,
       parity='N',
       stopbits=1
   )
   client = ModbusClient(transport)

   with client:
       # 读取线圈
       coils = client.read_coils(
           slave_id=1, 
           start_address=0, 
           quantity=8
       )
       print(f"线圈: {coils}")
       
       # 写入多个线圈
       client.write_multiple_coils(
           slave_id=1, 
           start_address=0, 
           values=[True, False, True, False]
       )

简单ASCII客户端
~~~~~~~~~~~~~~~

.. code-block:: python

   from modbuslink import ModbusClient, AsciiTransport

   # 创建ASCII传输层
   transport = AsciiTransport(
       port='COM1',
       baudrate=9600,
       bytesize=7,
       parity='E',
       stopbits=1
   )
   client = ModbusClient(transport)

   with client:
       # 读取保持寄存器
       registers = client.read_holding_registers(
           slave_id=1, 
           start_address=0, 
           quantity=4
       )
       print(f"寄存器: {registers}")
       
       # 写入单个寄存器
       client.write_single_register(
           slave_id=1, 
           address=0, 
           value=1234
       )

高级示例
--------

异步操作
~~~~~~~~

.. code-block:: python

   import asyncio
   from modbuslink import AsyncModbusClient, AsyncTcpTransport

   async def async_modbus_operations():
       transport = AsyncTcpTransport(host='192.168.1.100', port=502)
       client = AsyncModbusClient(transport)
       
       async with client:
           # 并发读取操作
           tasks = [
               client.read_holding_registers(slave_id=1, start_address=0, quantity=10),
               client.read_holding_registers(slave_id=1, start_address=10, quantity=10),
               client.read_holding_registers(slave_id=1, start_address=20, quantity=10)
           ]
           
           results = await asyncio.gather(*tasks)
           for i, registers in enumerate(results):
               print(f"块 {i}: {registers}")
           
           # 顺序写入操作
           for i in range(10):
               await client.write_single_register(
                   slave_id=1, 
                   address=i, 
                   value=i * 100
               )

   # 运行异步函数
   asyncio.run(async_modbus_operations())

异步RTU操作
~~~~~~~~~~~

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
           # 异步读取保持寄存器
           registers = await client.read_holding_registers(
               slave_id=1, 
               start_address=0, 
               quantity=10
           )
           print(f"寄存器: {registers}")
           
           # 异步写入多个寄存器
           await client.write_multiple_registers(
               slave_id=1, 
               start_address=0, 
               values=[100, 200, 300, 400]
           )

   asyncio.run(async_rtu_operations())

异步ASCII操作
~~~~~~~~~~~~~

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
           # 异步读取线圈
           coils = await client.read_coils(
               slave_id=1, 
               start_address=0, 
               quantity=8
           )
           print(f"线圈: {coils}")
           
           # 异步写入单个线圈
           await client.write_single_coil(
               slave_id=1, 
               address=0, 
               value=True
           )

   asyncio.run(async_ascii_operations())

回调机制
~~~~~~~~

.. code-block:: python

   from modbuslink import AsyncModbusClient, AsyncTcpTransport
   import asyncio

   def on_data_received(data):
       print(f"接收到数据: {data}")

   def on_error(error):
       print(f"发生错误: {error}")

   async def callback_example():
       transport = AsyncTcpTransport(host='192.168.1.100', port=502)
       client = AsyncModbusClient(transport)
       
       # 设置回调
       client.set_data_callback(on_data_received)
       client.set_error_callback(on_error)
       
       async with client:
           # 操作将触发回调
           await client.read_holding_registers(
               slave_id=1, 
               start_address=0, 
               quantity=10
           )

   asyncio.run(callback_example())

高级数据类型
~~~~~~~~~~~~

.. code-block:: python

   from modbuslink import ModbusClient, TcpTransport

   transport = TcpTransport(host='192.168.1.100', port=502)
   client = ModbusClient(transport)

   with client:
       # Float32 操作
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
       print(f"温度: {read_temp}°C")
       
       # Int32 操作，自定义字节/字序
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
       print(f"计数器: {read_counter}")
       
       # UInt32 操作
       timestamp = 1640995200  # Unix时间戳
       client.write_uint32(
           slave_id=1, 
           start_address=104, 
           value=timestamp
       )
       
       read_timestamp = client.read_uint32(
           slave_id=1, 
           start_address=104
       )
       print(f"时间戳: {read_timestamp}")

性能测试示例
------------

批量操作性能
~~~~~~~~~~~~

.. code-block:: python

   import time
   import asyncio
   from modbuslink import AsyncModbusClient, AsyncTcpTransport

   async def performance_test():
       transport = AsyncTcpTransport(host='192.168.1.100', port=502)
       client = AsyncModbusClient(transport)
       
       async with client:
           # 测试批量读取性能
           start_time = time.time()
           
           # 并发读取多个寄存器块
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
           
           print(f"读取100个寄存器耗时: {end_time - start_time:.3f}秒")
           print(f"平均每个寄存器: {(end_time - start_time)*1000/100:.2f}ms")

   asyncio.run(performance_test())

连接池示例
~~~~~~~~~~

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

   # 使用连接池
   async def use_connection_pool():
       pool = ModbusConnectionPool('192.168.1.100', 502)
       await pool.initialize()
       
       try:
           # 获取连接
           client = await pool.get_connection()
           
           # 执行操作
           registers = await client.read_holding_registers(
               slave_id=1, start_address=0, quantity=10
           )
           print(f"读取结果: {registers}")
           
           # 归还连接
           await pool.return_connection(client)
           
       finally:
           await pool.close_all()

   asyncio.run(use_connection_pool())

错误处理示例
------------

综合错误处理
~~~~~~~~~~~~

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
               
               # 执行操作
               registers = client.read_holding_registers(
                   slave_id=1, 
                   start_address=0, 
                   quantity=10
               )
               print(f"成功读取寄存器: {registers}")
               break
               
           except ConnectionError as e:
               print(f"连接失败（尝试 {attempt + 1}）: {e}")
               if attempt < max_retries - 1:
                   time.sleep(retry_delay)
                   retry_delay *= 2  # 指数退避
               
           except TimeoutError as e:
               print(f"操作超时（尝试 {attempt + 1}）: {e}")
               if attempt < max_retries - 1:
                   time.sleep(retry_delay)
               
           except CRCError as e:
               print(f"检测到CRC错误: {e}")
               # CRC错误通常表示通信问题
               break
               
           except InvalidResponseError as e:
               print(f"接收到无效响应: {e}")
               break
               
           except ModbusException as e:
               print(f"Modbus协议错误: {e}")
               print(f"异常码: {e.exception_code}")
               break
               
           except Exception as e:
               print(f"意外错误: {e}")
               break
               
           finally:
               try:
                   client.disconnect()
               except:
                   pass

   robust_modbus_client()

日志配置
~~~~~~~~

.. code-block:: python

   from modbuslink import ModbusClient, TcpTransport
   from modbuslink.utils.logger import setup_logger
   import logging

   # 配置日志
   setup_logger(
       name='modbuslink',
       level=logging.DEBUG,
       log_file='modbus_operations.log',
       console_output=True
   )

   # 创建启用日志的客户端
   transport = TcpTransport(host='192.168.1.100', port=502)
   client = ModbusClient(transport)

   with client:
       # 所有操作都将被记录
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

集成示例
--------

数据采集系统
~~~~~~~~~~~~

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
                       # 读取多个数据点
                       temperature = await self.client.read_float32(
                           slave_id=1, start_address=100
                       )
                       pressure = await self.client.read_float32(
                           slave_id=1, start_address=102
                       )
                       flow_rate = await self.client.read_float32(
                           slave_id=1, start_address=104
                       )
                       
                       # 创建数据记录
                       record = {
                           'timestamp': datetime.now().isoformat(),
                           'temperature': temperature,
                           'pressure': pressure,
                           'flow_rate': flow_rate
                       }
                       
                       self.data_buffer.append(record)
                       print(f"数据已采集: {record}")
                       
                       # 定期保存数据
                       if len(self.data_buffer) >= 10:
                           await self.save_data()
                           
                   except Exception as e:
                       print(f"采集错误: {e}")
                       
                   await asyncio.sleep(interval)
                   
       async def save_data(self):
           if self.data_buffer:
               filename = f"data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
               with open(filename, 'w') as f:
                   json.dump(self.data_buffer, f, indent=2)
               print(f"已保存 {len(self.data_buffer)} 条记录到 {filename}")
               self.data_buffer.clear()

   # 使用方法
   async def main():
       daq = DataAcquisitionSystem('192.168.1.100', 502)
       await daq.start_acquisition(interval=2.0)

   asyncio.run(main())

服务器示例
----------

基础TCP服务器
~~~~~~~~~~~~~

.. code-block:: python

   from modbuslink import AsyncTcpModbusServer, ModbusDataStore
   import asyncio
   import logging

   async def main():
       # 设置日志
       logging.basicConfig(level=logging.INFO)
       
       # 创建数据存储
       data_store = ModbusDataStore(
           coils_size=1000,
           discrete_inputs_size=1000,
           holding_registers_size=1000,
           input_registers_size=1000
       )
       
       # 设置初始数据
       data_store.write_coils(0, [True, False, True, False, True, False, True, False])
       data_store.write_holding_registers(0, [100, 200, 300, 400, 500])
       data_store.write_input_registers(0, [250, 251, 252, 253, 254])
       data_store.write_discrete_inputs(0, [False, True, False, True, False, True, False, True])
       
       # 创建TCP服务器
       server = AsyncTcpModbusServer(
           host="localhost",
           port=5020,
           data_store=data_store,
           slave_id=1,
           max_connections=5
       )
       
       print("启动TCP服务器: localhost:5020")
       print("从站地址: 1")
       
       try:
           # 启动服务器
           await server.start()
           print("TCP服务器启动成功!")
           
           # 永久运行
           await server.serve_forever()
           
       except KeyboardInterrupt:
           print("\n收到停止信号")
       finally:
           print("正在停止服务器...")
           await server.stop()
           print("服务器已停止")

   asyncio.run(main())

RTU服务器示例
~~~~~~~~~~~~~

.. code-block:: python

   from modbuslink import AsyncRtuModbusServer, ModbusDataStore
   import asyncio
   import random
   import math

   async def simulate_industrial_data(data_store):
       """模拟工业设备数据"""
       cycle = 0
       
       while True:
           try:
               cycle += 1
               
               # 模拟温度传感器数据
               base_temps = [248, 179, 318, 447, 682]
               temp_variations = [base + random.randint(-5, 5) + int(3 * math.sin(cycle * 0.1)) for base in base_temps]
               data_store.write_input_registers(0, temp_variations)
               
               # 模拟压力传感器数据
               base_pressures = [1015, 1027, 996, 1043, 1004]
               pressure_variations = [base + random.randint(-3, 3) + int(2 * math.cos(cycle * 0.15)) for base in base_pressures]
               data_store.write_input_registers(10, pressure_variations)
               
               # 模拟电机转速变化
               current_speeds = data_store.read_holding_registers(0, 5)
               new_speeds = [speed + random.randint(-50, 50) for speed in current_speeds]
               new_speeds = [max(500, min(4000, speed)) for speed in new_speeds]
               data_store.write_holding_registers(0, new_speeds)
               
               if cycle % 20 == 0:
                   print(f"工业数据更新 #{cycle}")
                   print(f"  温度: {temp_variations}")
                   print(f"  压力: {pressure_variations}")
                   print(f"  电机转速: {new_speeds}")
               
               await asyncio.sleep(2.0)
               
           except Exception as e:
               print(f"数据模拟错误: {e}")
               await asyncio.sleep(2.0)

   async def main():
       # 创建数据存储
       data_store = ModbusDataStore(
           coils_size=1000,
           discrete_inputs_size=1000,
           holding_registers_size=1000,
           input_registers_size=1000
       )
       
       # 初始化工业设备数据
       data_store.write_coils(0, [True, False, True, True, False, False, True, False])  # 电机状态
       data_store.write_coils(8, [False, True, False, True, True, False, False, True])  # 阀门状态
       data_store.write_holding_registers(0, [1500, 2800, 3600, 1200, 750])  # 电机参数
       data_store.write_input_registers(0, [248, 179, 318, 447, 682])  # 温度传感器
       data_store.write_discrete_inputs(0, [True, False, True, True, False, True, False, True])  # 限位开关
       
       # 创建RTU服务器
       server = AsyncRtuModbusServer(
           port="COM3",  # 根据实际情况修改
           baudrate=9600,
           data_store=data_store,
           slave_id=1,
           parity="N",
           stopbits=1,
           bytesize=8,
           timeout=1.0
       )
       
       print("RTU服务器配置:")
       print("  串口: COM3")
       print("  波特率: 9600")
       print("  数据位: 8, 停止位: 1, 校验位: 无")
       print("  从站地址: 1")
       
       try:
           # 启动服务器
           await server.start()
           print("RTU服务器启动成功!")
           
           # 启动数据模拟任务
           simulation_task = asyncio.create_task(simulate_industrial_data(data_store))
           server_task = asyncio.create_task(server.serve_forever())
           
           # 等待任务完成
           await asyncio.gather(simulation_task, server_task)
           
       except KeyboardInterrupt:
           print("\n收到停止信号")
       except Exception as e:
           print(f"\n服务器运行错误: {e}")
       finally:
           print("正在停止服务器...")
           await server.stop()
           print("服务器已停止")

   asyncio.run(main())

ASCII服务器示例
~~~~~~~~~~~~~~~

.. code-block:: python

   from modbuslink import AsyncAsciiModbusServer, ModbusDataStore
   import asyncio
   import random
   import math

   async def simulate_laboratory_experiment(data_store):
       """模拟实验室实验过程"""
       experiment_time = 0
       
       while True:
           try:
               experiment_time += 1
               
               # 模拟温度控制过程
               target_temps = data_store.read_holding_registers(0, 5)
               current_temps = data_store.read_input_registers(0, 5)
               
               # 温度逐渐趋向目标值
               new_temps = []
               for i, (current, target) in enumerate(zip(current_temps, target_temps)):
                   diff = target - current
                   change = diff * 0.1 + random.randint(-2, 2) + math.sin(experiment_time * 0.05) * 1
                   new_temp = current + change
                   new_temps.append(int(max(0, min(500, new_temp))))
               
               data_store.write_input_registers(0, new_temps)
               
               # 模拟湿度变化
               base_humidity = [45, 52, 38, 48, 55]
               humidity_variations = [base + random.randint(-5, 5) + int(2 * math.cos(experiment_time * 0.08)) for base in base_humidity]
               humidity_variations = [max(0, min(100, h)) for h in humidity_variations]
               data_store.write_input_registers(10, humidity_variations)
               
               # 模拟pH值变化
               base_ph = [700, 650, 720, 680, 710]
               ph_variations = [base + random.randint(-10, 10) + int(3 * math.sin(experiment_time * 0.03)) for base in base_ph]
               ph_variations = [max(0, min(1400, ph)) for ph in ph_variations]
               data_store.write_input_registers(20, ph_variations)
               
               if experiment_time % 15 == 0:
                   print(f"实验过程模拟 #{experiment_time}")
                   print(f"  温度: {new_temps}")
                   print(f"  湿度: {humidity_variations}%")
                   print(f"  pH: {[ph/100.0 for ph in ph_variations]}")
               
               await asyncio.sleep(3.0)
               
           except Exception as e:
               print(f"实验模拟错误: {e}")
               await asyncio.sleep(3.0)

   async def main():
       # 创建数据存储
       data_store = ModbusDataStore(
           coils_size=1000,
           discrete_inputs_size=1000,
           holding_registers_size=1000,
           input_registers_size=1000
       )
       
       # 初始化实验室设备数据
       data_store.write_coils(0, [False, True, False, True, False, False, True, False])  # 加热器控制
       data_store.write_coils(8, [True, True, False, False, True, True, False, False])  # 风扇控制
       data_store.write_holding_registers(0, [250, 300, 180, 220, 350])  # 目标温度
       data_store.write_input_registers(0, [248, 298, 178, 218, 348])  # 实际温度
       data_store.write_discrete_inputs(0, [False, True, False, False, True, True, False, True])  # 门开关状态
       
       # 创建ASCII服务器
       server = AsyncAsciiModbusServer(
           port="COM4",  # 根据实际情况修改
           baudrate=9600,
           data_store=data_store,
           slave_id=2,
           parity="E",
           stopbits=1,
           bytesize=7,
           timeout=2.0
       )
       
       print("ASCII服务器配置:")
       print("  串口: COM4")
       print("  波特率: 9600")
       print("  数据位: 7, 停止位: 1, 校验位: 偶校验")
       print("  从站地址: 2")
       
       try:
           # 启动服务器
           await server.start()
           print("ASCII服务器启动成功!")
           
           # 启动实验模拟任务
           simulation_task = asyncio.create_task(simulate_laboratory_experiment(data_store))
           server_task = asyncio.create_task(server.serve_forever())
           
           # 等待任务完成
           await asyncio.gather(simulation_task, server_task)
           
       except KeyboardInterrupt:
           print("\n收到停止信号")
       except Exception as e:
           print(f"\n服务器运行错误: {e}")
       finally:
           print("正在停止服务器...")
           await server.stop()
           print("服务器已停止")

   asyncio.run(main())

多服务器示例
~~~~~~~~~~~~

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
       """多服务器管理器"""
       
       def __init__(self):
           self.servers = {}
           self.data_stores = {}
           self.running = False
       
       async def setup_servers(self):
           """设置所有服务器"""
           # TCP服务器
           tcp_data_store = ModbusDataStore(coils_size=1000, discrete_inputs_size=1000,
                                          holding_registers_size=1000, input_registers_size=1000)
           tcp_data_store.write_coils(0, [True, False, True, False] * 10)
           tcp_data_store.write_holding_registers(0, list(range(100, 150)))
           
           tcp_server = AsyncTcpModbusServer(
               host="localhost", port=5020, data_store=tcp_data_store, slave_id=1
           )
           
           self.servers["tcp"] = tcp_server
           self.data_stores["tcp"] = tcp_data_store
           
           # RTU服务器
           rtu_data_store = ModbusDataStore(coils_size=1000, discrete_inputs_size=1000,
                                          holding_registers_size=1000, input_registers_size=1000)
           rtu_data_store.write_coils(0, [False, True, False, True] * 8)
           rtu_data_store.write_holding_registers(0, [1500, 2800, 3600, 1200, 750])
           
           rtu_server = AsyncRtuModbusServer(
               port="COM3", baudrate=9600, data_store=rtu_data_store, slave_id=2
           )
           
           self.servers["rtu"] = rtu_server
           self.data_stores["rtu"] = rtu_data_store
           
           # ASCII服务器
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
           """启动所有服务器"""
           print("启动所有服务器...")
           
           for server_type, server in self.servers.items():
               try:
                   await server.start()
                   print(f"{server_type.upper()}服务器启动成功")
               except Exception as e:
                   print(f"{server_type.upper()}服务器启动失败: {e}")
           
           self.running = True
       
       async def stop_all_servers(self):
           """停止所有服务器"""
           print("停止所有服务器...")
           
           for server_type, server in self.servers.items():
               try:
                   await server.stop()
                   print(f"{server_type.upper()}服务器已停止")
               except Exception as e:
                   print(f"{server_type.upper()}服务器停止失败: {e}")
           
           self.running = False
       
       async def simulate_data_changes(self):
           """模拟数据变化"""
           cycle = 0
           
           while self.running:
               try:
                   cycle += 1
                   
                   # 更新各服务器数据
                   for server_type, store in self.data_stores.items():
                       if server_type == "tcp":
                           # 网络监控数据
                           traffic_data = [random.randint(100, 1000) for _ in range(10)]
                           store.write_input_registers(50, traffic_data)
                       elif server_type == "rtu":
                           # 工业过程数据
                           temp_data = [random.randint(200, 400) for _ in range(5)]
                           store.write_input_registers(0, temp_data)
                       elif server_type == "ascii":
                           # 实验室数据
                           lab_data = [random.randint(180, 350) for _ in range(5)]
                           store.write_input_registers(0, lab_data)
                       
                       # 更新计数器
                       store.write_holding_registers(999, [cycle])
                   
                   if cycle % 20 == 0:
                       print(f"数据模拟周期 #{cycle}")
                   
                   await asyncio.sleep(2.0)
                   
               except Exception as e:
                   print(f"数据模拟错误: {e}")
                   await asyncio.sleep(2.0)
       
       async def serve_forever(self):
           """永久运行"""
           # 启动数据模拟任务
           simulation_task = asyncio.create_task(self.simulate_data_changes())
           
           # 启动所有服务器的serve_forever任务
           server_tasks = []
           for server_type, server in self.servers.items():
               try:
                   if await server.is_running():
                       server_tasks.append(asyncio.create_task(server.serve_forever()))
               except Exception as e:
                   print(f"{server_type.upper()}服务器serve_forever启动失败: {e}")
           
           # 等待所有任务完成
           all_tasks = [simulation_task] + server_tasks
           await asyncio.gather(*all_tasks, return_exceptions=True)

   async def main():
       manager = MultiServerManager()
       
       try:
           # 配置和启动服务器
           await manager.setup_servers()
           await manager.start_all_servers()
           
           print("\n连接信息:")
           print("  TCP服务器: localhost:5020 (从站地址 1)")
           print("  RTU服务器: COM3@9600,8,N,1 (从站地址 2)")
           print("  ASCII服务器: COM4@9600,7,E,1 (从站地址 3)")
           print("\n按 Ctrl+C 停止所有服务器")
           
           # 永久运行
           await manager.serve_forever()
           
       except KeyboardInterrupt:
           print("\n收到停止信号")
       except Exception as e:
           print(f"\n多服务器运行错误: {e}")
       finally:
           await manager.stop_all_servers()

   asyncio.run(main())

过程控制系统
~~~~~~~~~~~~

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
                       # 读取过程变量
                       current_temp = await self.client.read_float32(
                           slave_id=1, start_address=100
                       )
                       current_pressure = await self.client.read_float32(
                           slave_id=1, start_address=102
                       )
                       
                       # 简单比例控制
                       temp_error = self.setpoints['temperature'] - current_temp
                       pressure_error = self.setpoints['pressure'] - current_pressure
                       
                       # 计算控制输出
                       heater_output = max(0, min(100, 50 + temp_error * 10))
                       pump_output = max(0, min(100, 50 + pressure_error * 5))
                       
                       # 写入控制输出
                       await self.client.write_float32(
                           slave_id=1, start_address=200, value=heater_output
                       )
                       await self.client.write_float32(
                           slave_id=1, start_address=202, value=pump_output
                       )
                       
                       print(f"温度: {current_temp:.2f}°C (设定值: {self.setpoints['temperature']}°C), "
                             f"加热器: {heater_output:.1f}%")
                       print(f"压力: {current_pressure:.2f} mbar (设定值: {self.setpoints['pressure']} mbar), "
                             f"泵: {pump_output:.1f}%")
                       
                   except Exception as e:
                       print(f"控制错误: {e}")
                       
                   await asyncio.sleep(1.0)  # 1秒控制循环
                   
       def set_temperature_setpoint(self, value):
           self.setpoints['temperature'] = value
           
       def set_pressure_setpoint(self, value):
           self.setpoints['pressure'] = value

   # 使用方法
   async def main():
       controller = ProcessController('192.168.1.100', 502)
       
       # 启动控制循环
       control_task = asyncio.create_task(controller.control_loop())
       
       # 模拟设定值变化
       await asyncio.sleep(10)
       controller.set_temperature_setpoint(30.0)
       
       await asyncio.sleep(10)
       controller.set_pressure_setpoint(1020.0)
       
       # 运行一段时间
       await asyncio.sleep(30)
       control_task.cancel()

   asyncio.run(main())