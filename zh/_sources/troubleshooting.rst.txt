故障排除指南
============

.. contents:: 本页内容
   :local:
   :depth: 3

本指南将帮您快速诊断和解决使用ModbusLink时遇到的常见问题。

连接问题
========

TCP连接问题
-----------

网络连接失败
~~~~~~~~~~~~

**问题现象**：
``ConnectionError: [Errno 10061] Connection refused`` 或类似网络错误

**解决步骤**：

1. **检查网络连接**
   
   .. code-block:: python
   
      import socket
      
      def test_tcp_connection(host, port, timeout=5):
          try:
              sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
              sock.settimeout(timeout)
              result = sock.connect_ex((host, port))
              sock.close()
              return result == 0
          except Exception:
              return False
      
      # 测试连接
      if test_tcp_connection('192.168.1.100', 502):
          print("✅ 网络连接正常")
      else:
          print("❌ 网络连接失败")

2. **检查设备状态**
   - 确认Modbus设备已开启
   - 验证IP地址和端口号正确
   - 检查防火墙设置

3. **网络诊断**
   
   .. code-block:: bash
   
      # Windows/Linux
      ping 192.168.1.100
      telnet 192.168.1.100 502
      
      # 或使用nmap检查端口
      nmap -p 502 192.168.1.100

连接超时
~~~~~~~~

**问题现象**：
``TimeoutError: Connection timeout after 10.0 seconds``

**解决方案**：

.. code-block:: python

   from modbuslink import ModbusClient, TcpTransport
   
   # 调整超时设置
   transport = TcpTransport(
       host='192.168.1.100',
       port=502,
       timeout=30.0,          # 增加超时时间
       connect_timeout=10.0   # 连接超时
   )
   
   client = ModbusClient(transport)
   
   # 实现重试机制
   import time
   
   def connect_with_retry(client, max_retries=3):
       for attempt in range(max_retries):
           try:
               client.connect()
               return True
           except Exception as e:
               print(f"连接尝试 {attempt + 1} 失败: {e}")
               if attempt < max_retries - 1:
                   time.sleep(2)  # 等待2秒后重试
       return False

串口连接问题
-----------

串口被占用
~~~~~~~~~~

**问题现象**：
``SerialException: [Errno 16] Device or resource busy``

**解决步骤**：

1. **检查串口占用**
   
   .. code-block:: python
   
      import serial.tools.list_ports
      
      # 列出所有串口
      ports = serial.tools.list_ports.comports()
      for port in ports:
          print(f"端口: {port.device}, 描述: {port.description}")
          print(f"硬件ID: {port.hwid}")
          print(f"正在使用: {port.device in [p.device for p in serial.tools.list_ports.comports()]}")

2. **释放串口资源**
   
   .. code-block:: bash
   
      # Linux - 查看占用进程
      sudo lsof /dev/ttyUSB0
      
      # 终止占用进程
      sudo kill -9 <PID>

3. **正确关闭串口**
   
   .. code-block:: python
   
      from modbuslink import ModbusClient, RtuTransport
      
      transport = RtuTransport(port='COM3', baudrate=9600)
      client = ModbusClient(transport)
      
      try:
          with client:  # 自动管理连接
              registers = client.read_holding_registers(1, 0, 10)
      except Exception as e:
          print(f"错误: {e}")
      # 连接会自动关闭

串口权限问题
~~~~~~~~~~~~

**问题现象**（Linux/macOS）：
``SerialException: [Errno 13] Permission denied``

**解决方案**：

.. code-block:: bash

   # Ubuntu/Debian
   sudo usermod -a -G dialout $USER
   newgrp dialout  # 立即生效
   
   # CentOS/RHEL
   sudo usermod -a -G uucp $USER
   
   # 或临时修改权限
   sudo chmod 666 /dev/ttyUSB0

协议错误
========

CRC校验错误
-----------

**问题现象**：
``CRCError: CRC check failed. Expected: 0x1234, Got: 0x5678``

**诊断和解决**：

1. **检查连接质量**
   
   .. code-block:: python
   
      # 降低波特率提高稳定性
      transport = RtuTransport(
          port='COM3',
          baudrate=4800,    # 从9600降到4800
          timeout=3.0       # 增加超时时间
      )

2. **检查电缆和接线**
   - 确认RS485/RS232线缆质量
   - 检查屏蔽接地
   - 验证终端电阻（RS485）

3. **调试CRC计算**
   
   .. code-block:: python
   
      from modbuslink.utils.crc import CRC16Modbus
      
      # 手动验证CRC
      data = b'\x01\x03\x00\x00\x00\x05'
      crc = CRC16Modbus.calculate(data)
      print(f"计算得到的CRC: 0x{crc:04X}")

无效响应错误
-----------

**问题现象**：
``InvalidResponseError: Invalid function code in response``

**常见原因和解决方案**：

1. **设备不支持该功能码**
   
   .. code-block:: python
   
      # 检查设备支持的功能码
      try:
          # 尝试读取保持寄存器
          result = client.read_holding_registers(1, 0, 1)
      except InvalidResponseError as e:
          print(f"设备可能不支持功能码0x03: {e}")
          # 尝试其他功能码
          try:
              result = client.read_input_registers(1, 0, 1)
              print("设备支持功能码0x04")
          except:
              print("设备可能不支持标准Modbus功能码")

2. **从站地址错误**
   
   .. code-block:: python
   
      # 扫描可用的从站地址
      def scan_slave_ids(client, start=1, end=247):
          active_slaves = []
          for slave_id in range(start, end + 1):
              try:
                  client.read_holding_registers(slave_id, 0, 1)
                  active_slaves.append(slave_id)
                  print(f"发现活动从站: {slave_id}")
              except:
                  pass
          return active_slaves
      
      # 使用示例
      with client:
          slaves = scan_slave_ids(client, 1, 10)
          print(f"活动从站列表: {slaves}")

性能问题
========

读取速度慢
----------

**优化策略**：

1. **批量读取**
   
   .. code-block:: python
   
      # 低效方式：逐个读取
      values = []
      for i in range(100):
          value = client.read_holding_registers(1, i, 1)[0]
          values.append(value)
      
      # 高效方式：批量读取
      values = client.read_holding_registers(1, 0, 100)

2. **使用异步操作**
   
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
              return sum(results, [])  # 合并结果

3. **连接复用**
   
   .. code-block:: python
   
      # 避免频繁连接/断开
      with client:
          for i in range(1000):
              data = client.read_holding_registers(1, 0, 10)
              # 处理数据

内存使用过高
-----------

**解决方案**：

1. **限制数据读取量**
   
   .. code-block:: python
   
      # 分块读取大量数据
      def read_large_data(client, slave_id, start_addr, total_count, chunk_size=100):
          all_data = []
          for offset in range(0, total_count, chunk_size):
              current_count = min(chunk_size, total_count - offset)
              chunk = client.read_holding_registers(
                  slave_id, start_addr + offset, current_count
              )
              all_data.extend(chunk)
          return all_data

2. **及时释放资源**
   
   .. code-block:: python
   
      import gc
      
      def process_large_dataset():
          with client:
              data = client.read_holding_registers(1, 0, 10000)
              # 处理数据
              processed = [x * 2 for x in data]
              
              # 手动清理内存
              del data
              gc.collect()
              
              return processed

数据问题
========

数据类型转换错误
-------------

**问题现象**：
数据读取结果与预期不符

**解决方案**：

1. **验证字节序**
   
   .. code-block:: python
   
      # 检查不同字节序
      registers = client.read_holding_registers(1, 100, 2)
      
      # 大端字节序 (默认)
      value_be = client.read_float32(1, 100)
      print(f"大端字节序: {value_be}")
      
      # 如果需要小端字节序，手动转换
      import struct
      data = struct.pack('>HH', registers[0], registers[1])
      value_le = struct.unpack('<f', data)[0]
      print(f"小端字节序: {value_le}")

2. **数据范围验证**
   
   .. code-block:: python
   
      def validate_sensor_data(value, min_val=-50, max_val=150):
          if not isinstance(value, (int, float)):
              raise ValueError(f"无效数据类型: {type(value)}")
          
          if not (min_val <= value <= max_val):
              raise ValueError(f"数据超出范围: {value} (期望: {min_val}-{max_val})")
          
          return value
      
      try:
          temp = client.read_float32(1, 100)
          validated_temp = validate_sensor_data(temp, -40, 100)
          print(f"温度: {validated_temp}°C")
      except ValueError as e:
          print(f"数据验证失败: {e}")

字符串编码问题
-----------

**问题现象**：
字符串读取出现乱码

**解决方案**：

.. code-block:: python

   def read_string_safe(client, slave_id, start_addr, length, encoding='utf-8'):
       try:
           # 使用ModbusLink内置方法
           return client.read_string(slave_id, start_addr, length)
       except UnicodeDecodeError:
           # 回退到手动处理
           registers = client.read_holding_registers(slave_id, start_addr, length)
           
           # 转换为字节
           byte_data = []
           for reg in registers:
               byte_data.extend([reg >> 8, reg & 0xFF])
           
           # 尝试不同编码
           for enc in ['utf-8', 'ascii', 'latin1', 'gb2312']:
               try:
                   decoded = bytes(byte_data).decode(enc).rstrip('\x00')
                   print(f"使用 {enc} 编码成功: {decoded}")
                   return decoded
               except UnicodeDecodeError:
                   continue
           
           return "解码失败"

调试和监控
==========

启用详细日志
-----------

.. code-block:: python

   import logging
   from modbuslink.utils.logging import enable_debug_logging
   
   # 启用ModbusLink调试日志
   enable_debug_logging()
   
   # 配置Python日志
   logging.basicConfig(
       level=logging.DEBUG,
       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
   )
   
   # 现在所有操作都会显示详细信息
   with client:
       data = client.read_holding_registers(1, 0, 5)

协议包分析
----------

.. code-block:: python

   class DebugTransport:
       def __init__(self, transport):
           self.transport = transport
       
       def send_and_receive(self, data):
           print(f"发送数据: {data.hex()}")
           response = self.transport.send_and_receive(data)
           print(f"接收数据: {response.hex()}")
           return response
       
       def __getattr__(self, name):
           return getattr(self.transport, name)
   
   # 使用调试传输层
   original_transport = TcpTransport('192.168.1.100', 502)
   debug_transport = DebugTransport(original_transport)
   client = ModbusClient(debug_transport)

性能监控
--------

.. code-block:: python

   import time
   from contextlib import contextmanager
   
   @contextmanager
   def measure_time(operation_name):
       start = time.time()
       try:
           yield
       finally:
           duration = time.time() - start
           print(f"{operation_name} 耗时: {duration:.3f}秒")
   
   # 使用示例
   with client:
       with measure_time("读取100个寄存器"):
           data = client.read_holding_registers(1, 0, 100)
       
       with measure_time("写入10个寄存器"):
           client.write_multiple_registers(1, 0, list(range(10)))

常见错误汇总
============

错误代码对照表
-----------

.. list-table:: 
   :widths: 15 25 60
   :header-rows: 1

   * - 错误类型
     - 典型信息
     - 解决方案
   * - ConnectionError
     - Connection refused
     - 检查设备IP、端口、网络连接
   * - TimeoutError
     - Request timeout
     - 增加超时时间、检查设备响应
   * - CRCError
     - CRC check failed
     - 检查线缆质量、降低波特率
   * - InvalidResponseError
     - Invalid function code
     - 确认设备支持该功能码、检查从站地址
   * - SerialException
     - Device busy
     - 检查串口占用、正确关闭连接
   * - AddressError
     - Invalid address
     - 确认寄存器地址在设备支持范围内
   * - ValueRangeError
     - Value out of range
     - 检查写入值是否在允许范围内

预防措施
========

代码最佳实践
-----------

1. **总是使用上下文管理器**
   
   .. code-block:: python
   
      # 推荐方式
      with client:
          data = client.read_holding_registers(1, 0, 10)
      
      # 避免的方式
      client.connect()
      data = client.read_holding_registers(1, 0, 10)
      client.disconnect()  # 可能被异常跳过

2. **实现健壮的错误处理**
   
   .. code-block:: python
   
      def robust_modbus_read(client, slave_id, address, count, max_retries=3):
          for attempt in range(max_retries):
              try:
                  return client.read_holding_registers(slave_id, address, count)
              except (ConnectionError, TimeoutError) as e:
                  if attempt == max_retries - 1:
                      raise
                  print(f"尝试 {attempt + 1} 失败，重试中...")
                  time.sleep(1)

3. **定期健康检查**
   
   .. code-block:: python
   
      def health_check(client):
          try:
              # 读取一个已知存在的寄存器
              client.read_holding_registers(1, 0, 1)
              return True
          except Exception as e:
              print(f"健康检查失败: {e}")
              return False

获取帮助
========

如果问题仍未解决，请：

1. **查看日志输出** - 启用调试模式获取详细信息
2. **检查GitHub Issues** - 搜索类似问题的解决方案
3. **提交Bug报告** - 包含完整的错误信息和最小复现代码
4. **参考设备手册** - 确认设备的Modbus实现细节

联系方式：
- GitHub: https://github.com/Miraitowa-la/ModbusLink/issues
- 文档: https://miraitowa-la.github.io/ModbusLink/