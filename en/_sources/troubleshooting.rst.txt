Troubleshooting Guide
====================

.. contents:: Table of Contents
   :local:
   :depth: 3

This guide will help you quickly diagnose and resolve common issues when using ModbusLink.

Connection Issues
=================

TCP Connection Problems
-----------------------

Network Connection Failures
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Symptoms**:
``ConnectionError: [Errno 10061] Connection refused`` or similar network errors

**Resolution Steps**:

1. **Check Network Connectivity**
   
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
      
      # Test connection
      if test_tcp_connection('192.168.1.100', 502):
          print("✅ Network connection OK")
      else:
          print("❌ Network connection failed")

2. **Check Device Status**
   - Confirm Modbus device is powered on
   - Verify IP address and port number
   - Check firewall settings

3. **Network Diagnostics**
   
   .. code-block:: bash
   
      # Windows/Linux
      ping 192.168.1.100
      telnet 192.168.1.100 502
      
      # Or use nmap to check port
      nmap -p 502 192.168.1.100

Connection Timeouts
~~~~~~~~~~~~~~~~~~

**Symptoms**:
``TimeoutError: Connection timeout after 10.0 seconds``

**Solutions**:

.. code-block:: python

   from modbuslink import ModbusClient, TcpTransport
   
   # Adjust timeout settings
   transport = TcpTransport(
       host='192.168.1.100',
       port=502,
       timeout=30.0,          # Increase timeout
       connect_timeout=10.0   # Connection timeout
   )
   
   client = ModbusClient(transport)
   
   # Implement retry mechanism
   import time
   
   def connect_with_retry(client, max_retries=3):
       for attempt in range(max_retries):
           try:
               client.connect()
               return True
           except Exception as e:
               print(f"Connection attempt {attempt + 1} failed: {e}")
               if attempt < max_retries - 1:
                   time.sleep(2)  # Wait 2 seconds before retry
       return False

Serial Connection Problems
--------------------------

Port Already in Use
~~~~~~~~~~~~~~~~~~

**Symptoms**:
``SerialException: [Errno 16] Device or resource busy``

**Resolution Steps**:

1. **Check Port Usage**
   
   .. code-block:: python
   
      import serial.tools.list_ports
      
      # List all serial ports
      ports = serial.tools.list_ports.comports()
      for port in ports:
          print(f"Port: {port.device}, Description: {port.description}")
          print(f"Hardware ID: {port.hwid}")
          print(f"In use: {port.device in [p.device for p in serial.tools.list_ports.comports()]}")

2. **Release Port Resources**
   
   .. code-block:: bash
   
      # Linux - Check process using port
      sudo lsof /dev/ttyUSB0
      
      # Kill process
      sudo kill -9 <PID>

3. **Properly Close Serial Port**
   
   .. code-block:: python
   
      from modbuslink import ModbusClient, RtuTransport
      
      transport = RtuTransport(port='COM3', baudrate=9600)
      client = ModbusClient(transport)
      
      try:
          with client:  # Automatic connection management
              registers = client.read_holding_registers(1, 0, 10)
      except Exception as e:
          print(f"Error: {e}")
      # Connection will be closed automatically

Serial Permission Issues
~~~~~~~~~~~~~~~~~~~~~~~

**Symptoms** (Linux/macOS):
``SerialException: [Errno 13] Permission denied``

**Solutions**:

.. code-block:: bash

   # Ubuntu/Debian
   sudo usermod -a -G dialout $USER
   newgrp dialout  # Take effect immediately
   
   # CentOS/RHEL
   sudo usermod -a -G uucp $USER
   
   # Or temporarily change permissions
   sudo chmod 666 /dev/ttyUSB0

Protocol Errors
===============

CRC Check Failures
------------------

**Symptoms**:
``CRCError: CRC check failed. Expected: 0x1234, Got: 0x5678``

**Diagnosis and Solutions**:

1. **Check Connection Quality**
   
   .. code-block:: python
   
      # Lower baud rate for better stability
      transport = RtuTransport(
          port='COM3',
          baudrate=4800,    # Reduce from 9600 to 4800
          timeout=3.0       # Increase timeout
      )

2. **Check Cables and Wiring**
   - Verify RS485/RS232 cable quality
   - Check shield grounding
   - Verify termination resistors (RS485)

3. **Debug CRC Calculation**
   
   .. code-block:: python
   
      from modbuslink.utils.crc import CRC16Modbus
      
      # Manually verify CRC
      data = b'\x01\x03\x00\x00\x00\x05'
      crc = CRC16Modbus.calculate(data)
      print(f"Calculated CRC: 0x{crc:04X}")

Invalid Response Errors
-----------------------

**Symptoms**:
``InvalidResponseError: Invalid function code in response``

**Common Causes and Solutions**:

1. **Device Doesn't Support Function Code**
   
   .. code-block:: python
   
      # Check supported function codes
      try:
          # Try reading holding registers
          result = client.read_holding_registers(1, 0, 1)
      except InvalidResponseError as e:
          print(f"Device may not support function code 0x03: {e}")
          # Try other function codes
          try:
              result = client.read_input_registers(1, 0, 1)
              print("Device supports function code 0x04")
          except:
              print("Device may not support standard Modbus function codes")

2. **Wrong Slave Address**
   
   .. code-block:: python
   
      # Scan for available slave addresses
      def scan_slave_ids(client, start=1, end=247):
          active_slaves = []
          for slave_id in range(start, end + 1):
              try:
                  client.read_holding_registers(slave_id, 0, 1)
                  active_slaves.append(slave_id)
                  print(f"Found active slave: {slave_id}")
              except:
                  pass
          return active_slaves
      
      # Usage example
      with client:
          slaves = scan_slave_ids(client, 1, 10)
          print(f"Active slaves: {slaves}")

Performance Issues
==================

Slow Read Operations
-------------------

**Optimization Strategies**:

1. **Batch Reading**
   
   .. code-block:: python
   
      # Inefficient: Read one by one
      values = []
      for i in range(100):
          value = client.read_holding_registers(1, i, 1)[0]
          values.append(value)
      
      # Efficient: Batch read
      values = client.read_holding_registers(1, 0, 100)

2. **Use Async Operations**
   
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
              return sum(results, [])  # Merge results

3. **Connection Reuse**
   
   .. code-block:: python
   
      # Avoid frequent connect/disconnect
      with client:
          for i in range(1000):
              data = client.read_holding_registers(1, 0, 10)
              # Process data

High Memory Usage
----------------

**Solutions**:

1. **Limit Data Read Size**
   
   .. code-block:: python
   
      # Read large data in chunks
      def read_large_data(client, slave_id, start_addr, total_count, chunk_size=100):
          all_data = []
          for offset in range(0, total_count, chunk_size):
              current_count = min(chunk_size, total_count - offset)
              chunk = client.read_holding_registers(
                  slave_id, start_addr + offset, current_count
              )
              all_data.extend(chunk)
          return all_data

2. **Release Resources Promptly**
   
   .. code-block:: python
   
      import gc
      
      def process_large_dataset():
          with client:
              data = client.read_holding_registers(1, 0, 10000)
              # Process data
              processed = [x * 2 for x in data]
              
              # Manual memory cleanup
              del data
              gc.collect()
              
              return processed

Data Issues
===========

Data Type Conversion Errors
---------------------------

**Symptoms**:
Data reading results don't match expectations

**Solutions**:

1. **Verify Byte Order**
   
   .. code-block:: python
   
      # Check different byte orders
      registers = client.read_holding_registers(1, 100, 2)
      
      # Big-endian (default)
      value_be = client.read_float32(1, 100)
      print(f"Big-endian: {value_be}")
      
      # If little-endian needed, convert manually
      import struct
      data = struct.pack('>HH', registers[0], registers[1])
      value_le = struct.unpack('<f', data)[0]
      print(f"Little-endian: {value_le}")

2. **Data Range Validation**
   
   .. code-block:: python
   
      def validate_sensor_data(value, min_val=-50, max_val=150):
          if not isinstance(value, (int, float)):
              raise ValueError(f"Invalid data type: {type(value)}")
          
          if not (min_val <= value <= max_val):
              raise ValueError(f"Data out of range: {value} (expected: {min_val}-{max_val})")
          
          return value
      
      try:
          temp = client.read_float32(1, 100)
          validated_temp = validate_sensor_data(temp, -40, 100)
          print(f"Temperature: {validated_temp}°C")
      except ValueError as e:
          print(f"Data validation failed: {e}")

String Encoding Issues
---------------------

**Symptoms**:
String reading produces garbled text

**Solutions**:

.. code-block:: python

   def read_string_safe(client, slave_id, start_addr, length, encoding='utf-8'):
       try:
           # Use ModbusLink built-in method
           return client.read_string(slave_id, start_addr, length)
       except UnicodeDecodeError:
           # Fallback to manual handling
           registers = client.read_holding_registers(slave_id, start_addr, length)
           
           # Convert to bytes
           byte_data = []
           for reg in registers:
               byte_data.extend([reg >> 8, reg & 0xFF])
           
           # Try different encodings
           for enc in ['utf-8', 'ascii', 'latin1', 'gb2312']:
               try:
                   decoded = bytes(byte_data).decode(enc).rstrip('\x00')
                   print(f"Successfully decoded with {enc}: {decoded}")
                   return decoded
               except UnicodeDecodeError:
                   continue
           
           return "Decoding failed"

Debugging and Monitoring
========================

Enable Verbose Logging
----------------------

.. code-block:: python

   import logging
   from modbuslink.utils.logging import enable_debug_logging
   
   # Enable ModbusLink debug logging
   enable_debug_logging()
   
   # Configure Python logging
   logging.basicConfig(
       level=logging.DEBUG,
       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
   )
   
   # All operations will now show detailed information
   with client:
       data = client.read_holding_registers(1, 0, 5)

Protocol Packet Analysis
------------------------

.. code-block:: python

   class DebugTransport:
       def __init__(self, transport):
           self.transport = transport
       
       def send_and_receive(self, data):
           print(f"Sending: {data.hex()}")
           response = self.transport.send_and_receive(data)
           print(f"Received: {response.hex()}")
           return response
       
       def __getattr__(self, name):
           return getattr(self.transport, name)
   
   # Use debug transport
   original_transport = TcpTransport('192.168.1.100', 502)
   debug_transport = DebugTransport(original_transport)
   client = ModbusClient(debug_transport)

Performance Monitoring
----------------------

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
           print(f"{operation_name} took: {duration:.3f}s")
   
   # Usage example
   with client:
       with measure_time("Read 100 registers"):
           data = client.read_holding_registers(1, 0, 100)
       
       with measure_time("Write 10 registers"):
           client.write_multiple_registers(1, 0, list(range(10)))

Common Error Reference
=====================

Error Code Lookup Table
-----------------------

.. list-table:: 
   :widths: 15 25 60
   :header-rows: 1

   * - Error Type
     - Typical Message
     - Solution
   * - ConnectionError
     - Connection refused
     - Check device IP, port, network connection
   * - TimeoutError
     - Request timeout
     - Increase timeout, check device response
   * - CRCError
     - CRC check failed
     - Check cable quality, reduce baud rate
   * - InvalidResponseError
     - Invalid function code
     - Verify device supports function code, check slave address
   * - SerialException
     - Device busy
     - Check port usage, properly close connections
   * - AddressError
     - Invalid address
     - Verify register address is within device range
   * - ValueRangeError
     - Value out of range
     - Check if write value is within allowed range

Prevention Measures
==================

Code Best Practices
-------------------

1. **Always Use Context Managers**
   
   .. code-block:: python
   
      # Recommended
      with client:
          data = client.read_holding_registers(1, 0, 10)
      
      # Avoid this
      client.connect()
      data = client.read_holding_registers(1, 0, 10)
      client.disconnect()  # May be skipped due to exception

2. **Implement Robust Error Handling**
   
   .. code-block:: python
   
      def robust_modbus_read(client, slave_id, address, count, max_retries=3):
          for attempt in range(max_retries):
              try:
                  return client.read_holding_registers(slave_id, address, count)
              except (ConnectionError, TimeoutError) as e:
                  if attempt == max_retries - 1:
                      raise
                  print(f"Attempt {attempt + 1} failed, retrying...")
                  time.sleep(1)

3. **Regular Health Checks**
   
   .. code-block:: python
   
      def health_check(client):
          try:
              # Read a known existing register
              client.read_holding_registers(1, 0, 1)
              return True
          except Exception as e:
              print(f"Health check failed: {e}")
              return False

Getting Help
============

If issues persist, please:

1. **Check Log Output** - Enable debug mode for detailed information
2. **Search GitHub Issues** - Look for similar problems and solutions
3. **Submit Bug Report** - Include complete error information and minimal reproduction code
4. **Check Device Manual** - Verify device's Modbus implementation details

Contact Information:
- GitHub: https://github.com/Miraitowa-la/ModbusLink/issues
- Documentation: https://miraitowa-la.github.io/ModbusLink/