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

从站模拟器示例
--------------

基本从站设置
~~~~~~~~~~~~

.. code-block:: python

   from modbuslink import ModbusSlave, DataStore
   import time

   # 创建带初始值的数据存储
   data_store = DataStore()
   
   # 初始化保持寄存器
   data_store.set_holding_registers(0, [1000, 2000, 3000, 4000, 5000])
   
   # 初始化线圈
   data_store.set_coils(0, [True, False, True, False, True, False])
   
   # 初始化离散输入
   data_store.set_discrete_inputs(0, [False, True, False, True])
   
   # 初始化输入寄存器
   data_store.set_input_registers(0, [100, 200, 300, 400])
   
   # 创建并启动从站
   slave = ModbusSlave(slave_id=1, data_store=data_store)
   
   try:
       slave.start_tcp_server(host='127.0.0.1', port=5020)
       print("从站服务器已启动在 127.0.0.1:5020")
       
       # 保持服务器运行
       while True:
           time.sleep(1)
           
   except KeyboardInterrupt:
       print("正在停止从站服务器...")
   finally:
       slave.stop()

动态数据更新
~~~~~~~~~~~~

.. code-block:: python

   from modbuslink import ModbusSlave, DataStore
   import time
   import random
   import threading

   def update_sensor_data(data_store):
       """模拟传感器数据更新"""
       while True:
           # 模拟温度传感器（寄存器100）
           temperature = random.uniform(20.0, 30.0)
           temp_int = int(temperature * 100)  # 转换为整数
           data_store.set_holding_registers(100, [temp_int])
           
           # 模拟压力传感器（寄存器101）
           pressure = random.uniform(1000.0, 1100.0)
           pressure_int = int(pressure * 10)
           data_store.set_holding_registers(101, [pressure_int])
           
           # 模拟数字输入
           digital_states = [random.choice([True, False]) for _ in range(8)]
           data_store.set_discrete_inputs(0, digital_states)
           
           time.sleep(2)  # 每2秒更新一次

   # 创建数据存储
   data_store = DataStore()
   
   # 启动后台线程进行数据更新
   update_thread = threading.Thread(
       target=update_sensor_data, 
       args=(data_store,), 
       daemon=True
   )
   update_thread.start()
   
   # 创建并启动从站
   slave = ModbusSlave(slave_id=1, data_store=data_store)
   
   with slave:
       slave.start_tcp_server(host='127.0.0.1', port=5020)
       print("动态从站服务器已启动在 127.0.0.1:5020")
       
       try:
           while True:
               time.sleep(1)
       except KeyboardInterrupt:
           print("正在停止从站服务器...")

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