"""ModbusLink 从站模拟器实现


ModbusLink Slave Simulator Implementation

提供Modbus从站模拟器，可以模拟RTU或TCP从站设备，
用于测试客户端功能和开发调试。


Provides Modbus slave simulator that can simulate RTU or TCP slave devices,
used for testing client functionality and development debugging.
"""

import struct
import socket
import serial
import threading
import time
from typing import Dict, List, Optional, Callable, Union
from ..common.exceptions import ModbusException, InvalidResponseError
from ..utils.crc import CRC16Modbus
from ..utils.logging import get_logger


class DataStore:
    """Modbus数据存储区 | Modbus Data Store
    
    模拟Modbus设备的内存区域，包括线圈、离散输入、
    保持寄存器和输入寄存器。
    
    
    Simulates Modbus device memory areas, including coils, discrete inputs,
    holding registers and input registers.
    """
    
    def __init__(self):
        """初始化数据存储区 | Initialize data store"""
        # 线圈状态（读写） | Coil status (read/write)
        self.coils: Dict[int, bool] = {}
        
        # 离散输入状态（只读） | Discrete input status (read-only)
        self.discrete_inputs: Dict[int, bool] = {}
        
        # 保持寄存器（读写） | Holding registers (read/write)
        self.holding_registers: Dict[int, int] = {}
        
        # 输入寄存器（只读） | Input registers (read-only)
        self.input_registers: Dict[int, int] = {}
    
    def set_coils(self, start_address: int, values: List[bool]) -> None:
        """设置线圈值 | Set coil values"""
        for i, value in enumerate(values):
            self.coils[start_address + i] = value
    
    def get_coils(self, start_address: int, quantity: int) -> List[bool]:
        """获取线圈值 | Get coil values"""
        return [self.coils.get(start_address + i, False) for i in range(quantity)]
    
    def set_discrete_inputs(self, start_address: int, values: List[bool]) -> None:
        """设置离散输入值 | Set discrete input values"""
        for i, value in enumerate(values):
            self.discrete_inputs[start_address + i] = value
    
    def get_discrete_inputs(self, start_address: int, quantity: int) -> List[bool]:
        """获取离散输入值 | Get discrete input values"""
        return [self.discrete_inputs.get(start_address + i, False) for i in range(quantity)]
    
    def set_holding_registers(self, start_address: int, values: List[int]) -> None:
        """设置保持寄存器值 | Set holding register values"""
        for i, value in enumerate(values):
            if not (0 <= value <= 65535):
                raise ValueError(f"寄存器值必须在0-65535之间: {value} | Register value must be between 0-65535: {value}")
            self.holding_registers[start_address + i] = value
    
    def get_holding_registers(self, start_address: int, quantity: int) -> List[int]:
        """获取保持寄存器值 | Get holding register values"""
        return [self.holding_registers.get(start_address + i, 0) for i in range(quantity)]
    
    def set_input_registers(self, start_address: int, values: List[int]) -> None:
        """设置输入寄存器值 | Set input register values"""
        for i, value in enumerate(values):
            if not (0 <= value <= 65535):
                raise ValueError(f"寄存器值必须在0-65535之间: {value} | Register value must be between 0-65535: {value}")
            self.input_registers[start_address + i] = value
    
    def get_input_registers(self, start_address: int, quantity: int) -> List[int]:
        """获取输入寄存器值 | Get input register values"""
        return [self.input_registers.get(start_address + i, 0) for i in range(quantity)]


class ModbusSlave:
    """Modbus从站模拟器 | Modbus Slave Simulator
    
    可以模拟RTU或TCP从站设备，支持标准Modbus功能码，
    提供数据存储区用于测试和开发。
    
    
    Can simulate RTU or TCP slave devices, supports standard Modbus function codes,
    provides data store for testing and development.
    """
    
    def __init__(self, slave_id: int = 1, data_store: Optional[DataStore] = None):
        """初始化从站模拟器
        
        
        Initialize slave simulator
        
        Args:
            slave_id: 从站地址 | Slave address
            data_store: 数据存储区实例，如果为None则创建新实例 | Data store instance, create new if None
        """
        self.slave_id = slave_id
        self.data_store = data_store or DataStore()
        self._logger = get_logger('server.slave')
        self._running = False
        self._server_thread: Optional[threading.Thread] = None
        
        # TCP服务器相关 | TCP server related
        self._tcp_socket: Optional[socket.socket] = None
        self._tcp_host = '127.0.0.1'
        self._tcp_port = 502
        
        # RTU服务器相关 | RTU server related
        self._rtu_serial: Optional[serial.Serial] = None
    
    def start_tcp_server(self, host: str = '127.0.0.1', port: int = 502) -> None:
        """启动TCP从站服务器 | Start TCP slave server
        
        Args:
            host: 监听地址 | Listen address
            port: 监听端口 | Listen port
        """
        if self._running:
            raise RuntimeError("从站已在运行 | Slave is already running")
        
        self._tcp_host = host
        self._tcp_port = port
        self._running = True
        
        self._server_thread = threading.Thread(target=self._tcp_server_loop, daemon=True)
        self._server_thread.start()
        
        self._logger.info(f"TCP从站服务器已启动，监听 {host}:{port} | TCP slave server started, listening on {host}:{port}")
    
    def start_rtu_server(self, port: str, baudrate: int = 9600, 
                        bytesize: int = 8, parity: str = 'N', stopbits: int = 1) -> None:
        """启动RTU从站服务器 | Start RTU slave server
        
        Args:
            port: 串口名称 | Serial port name
            baudrate: 波特率 | Baud rate
            bytesize: 数据位 | Data bits
            parity: 校验位 | Parity
            stopbits: 停止位 | Stop bits
        """
        if self._running:
            raise RuntimeError("从站已在运行 | Slave is already running")
        
        self._rtu_serial = serial.Serial(
            port=port,
            baudrate=baudrate,
            bytesize=bytesize,
            parity=parity,
            stopbits=stopbits,
            timeout=1.0
        )
        
        self._running = True
        self._server_thread = threading.Thread(target=self._rtu_server_loop, daemon=True)
        self._server_thread.start()
        
        self._logger.info(f"RTU从站服务器已启动，串口 {port} | RTU slave server started, serial port {port}")
    
    def stop(self) -> None:
        """停止从站服务器 | Stop slave server"""
        if not self._running:
            return
        
        self._running = False
        
        # 关闭TCP套接字 | Close TCP socket
        if self._tcp_socket:
            try:
                self._tcp_socket.close()
            except Exception:
                pass
            self._tcp_socket = None
        
        # 关闭串口 | Close serial port
        if self._rtu_serial:
            try:
                self._rtu_serial.close()
            except Exception:
                pass
            self._rtu_serial = None
        
        # 等待服务器线程结束 | Wait for server thread to finish
        if self._server_thread and self._server_thread.is_alive():
            self._server_thread.join(timeout=2.0)
        
        self._logger.info("从站服务器已停止 | Slave server stopped")
    
    def _tcp_server_loop(self) -> None:
        """TCP服务器主循环 | TCP server main loop"""
        try:
            self._tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self._tcp_socket.bind((self._tcp_host, self._tcp_port))
            self._tcp_socket.listen(5)
            self._tcp_socket.settimeout(1.0)
            
            while self._running:
                try:
                    client_socket, client_address = self._tcp_socket.accept()
                    self._logger.debug(f"客户端连接: {client_address} | Client connected: {client_address}")
                    
                    # 在新线程中处理客户端 | Handle client in new thread
                    client_thread = threading.Thread(
                        target=self._handle_tcp_client,
                        args=(client_socket,),
                        daemon=True
                    )
                    client_thread.start()
                    
                except socket.timeout:
                    continue
                except Exception as e:
                    if self._running:
                        self._logger.error(f"TCP服务器错误: {e} | TCP server error: {e}")
                    break
        
        except Exception as e:
            self._logger.error(f"TCP服务器启动失败: {e} | TCP server startup failed: {e}")
    
    def _handle_tcp_client(self, client_socket: socket.socket) -> None:
        """处理TCP客户端连接 | Handle TCP client connection"""
        try:
            client_socket.settimeout(5.0)
            
            while self._running:
                try:
                    # 接收MBAP头（7字节） | Receive MBAP header (7 bytes)
                    mbap_header = self._receive_exact(client_socket, 7)
                    if not mbap_header:
                        break
                    
                    # 解析MBAP头 | Parse MBAP header
                    transaction_id, protocol_id, length, unit_id = struct.unpack('>HHHB', mbap_header)
                    
                    if protocol_id != 0:
                        self._logger.warning(f"无效的协议ID: {protocol_id} | Invalid protocol ID: {protocol_id}")
                        continue
                    
                    if unit_id != self.slave_id:
                        self._logger.debug(f"忽略非本站请求: {unit_id} | Ignoring request for other slave: {unit_id}")
                        continue
                    
                    # 接收PDU | Receive PDU
                    pdu_length = length - 1  # 减去unit_id的1字节 | Subtract 1 byte for unit_id
                    pdu = self._receive_exact(client_socket, pdu_length)
                    if not pdu:
                        break
                    
                    self._logger.debug(f"收到TCP请求: {pdu.hex()} | Received TCP request: {pdu.hex()}")
                    
                    # 处理PDU并生成响应 | Process PDU and generate response
                    response_pdu = self._process_pdu(pdu)
                    
                    # 构建响应MBAP头 | Build response MBAP header
                    response_length = len(response_pdu) + 1  # 加上unit_id的1字节 | Add 1 byte for unit_id
                    response_mbap = struct.pack('>HHHB', transaction_id, 0, response_length, unit_id)
                    
                    # 发送响应 | Send response
                    response_frame = response_mbap + response_pdu
                    client_socket.send(response_frame)
                    
                    self._logger.debug(f"发送TCP响应: {response_pdu.hex()} | Sent TCP response: {response_pdu.hex()}")
                    
                except socket.timeout:
                    continue
                except Exception as e:
                    self._logger.error(f"处理TCP客户端错误: {e} | Handle TCP client error: {e}")
                    break
        
        finally:
            try:
                client_socket.close()
            except Exception:
                pass
    
    def _rtu_server_loop(self) -> None:
        """RTU服务器主循环 | RTU server main loop"""
        try:
            while self._running:
                try:
                    # 读取数据直到超时 | Read data until timeout
                    data = b''
                    start_time = time.time()
                    
                    while time.time() - start_time < 1.0:  # 1秒超时 | 1 second timeout
                        if self._rtu_serial.in_waiting > 0:
                            chunk = self._rtu_serial.read(self._rtu_serial.in_waiting)
                            data += chunk
                            start_time = time.time()  # 重置超时 | Reset timeout
                        else:
                            time.sleep(0.01)  # 短暂休眠 | Short sleep
                    
                    if len(data) < 4:  # 最小帧长度：地址+功能码+CRC | Minimum frame length: address+function+CRC
                        continue
                    
                    # 验证CRC | Verify CRC
                    if not CRC16Modbus.validate(data):
                        self._logger.warning(f"CRC校验失败: {data.hex()} | CRC validation failed: {data.hex()}")
                        continue
                    
                    # 提取地址和PDU | Extract address and PDU
                    slave_address = data[0]
                    pdu = data[1:-2]  # 去掉地址和CRC | Remove address and CRC
                    
                    if slave_address != self.slave_id:
                        self._logger.debug(f"忽略非本站请求: {slave_address} | Ignoring request for other slave: {slave_address}")
                        continue
                    
                    self._logger.debug(f"收到RTU请求: {pdu.hex()} | Received RTU request: {pdu.hex()}")
                    
                    # 处理PDU并生成响应 | Process PDU and generate response
                    response_pdu = self._process_pdu(pdu)
                    
                    # 构建响应帧 | Build response frame
                    response_prefix = bytes([slave_address]) + response_pdu
                    response_crc = CRC16Modbus.calculate(response_prefix)
                    response_frame = response_prefix + response_crc
                    
                    # 发送响应 | Send response
                    self._rtu_serial.write(response_frame)
                    
                    self._logger.debug(f"发送RTU响应: {response_pdu.hex()} | Sent RTU response: {response_pdu.hex()}")
                    
                except Exception as e:
                    if self._running:
                        self._logger.error(f"RTU服务器错误: {e} | RTU server error: {e}")
                    time.sleep(0.1)
        
        except Exception as e:
            self._logger.error(f"RTU服务器循环错误: {e} | RTU server loop error: {e}")
    
    def _receive_exact(self, sock: socket.socket, length: int) -> bytes:
        """精确接收指定长度的数据 | Receive exact length of data"""
        data = b''
        while len(data) < length:
            chunk = sock.recv(length - len(data))
            if not chunk:
                return b''
            data += chunk
        return data
    
    def _process_pdu(self, pdu: bytes) -> bytes:
        """处理PDU并生成响应 | Process PDU and generate response
        
        Args:
            pdu: 请求PDU | Request PDU
            
        Returns:
            响应PDU | Response PDU
        """
        if len(pdu) < 1:
            return self._create_exception_response(0x01, 0x01)  # 非法功能码 | Illegal function code
        
        function_code = pdu[0]
        
        try:
            if function_code == 0x01:  # 读线圈 | Read coils
                return self._handle_read_coils(pdu)
            elif function_code == 0x02:  # 读离散输入 | Read discrete inputs
                return self._handle_read_discrete_inputs(pdu)
            elif function_code == 0x03:  # 读保持寄存器 | Read holding registers
                return self._handle_read_holding_registers(pdu)
            elif function_code == 0x04:  # 读输入寄存器 | Read input registers
                return self._handle_read_input_registers(pdu)
            elif function_code == 0x05:  # 写单个线圈 | Write single coil
                return self._handle_write_single_coil(pdu)
            elif function_code == 0x06:  # 写单个寄存器 | Write single register
                return self._handle_write_single_register(pdu)
            elif function_code == 0x0F:  # 写多个线圈 | Write multiple coils
                return self._handle_write_multiple_coils(pdu)
            elif function_code == 0x10:  # 写多个寄存器 | Write multiple registers
                return self._handle_write_multiple_registers(pdu)
            else:
                return self._create_exception_response(function_code, 0x01)  # 非法功能码 | Illegal function code
        
        except Exception as e:
            self._logger.error(f"处理PDU错误: {e} | Process PDU error: {e}")
            return self._create_exception_response(function_code, 0x04)  # 从站设备故障 | Slave device failure
    
    def _handle_read_coils(self, pdu: bytes) -> bytes:
        """处理读线圈请求 | Handle read coils request"""
        if len(pdu) != 5:
            return self._create_exception_response(0x01, 0x03)  # 非法数据值 | Illegal data value
        
        start_address, quantity = struct.unpack('>HH', pdu[1:5])
        
        if not (1 <= quantity <= 2000):
            return self._create_exception_response(0x01, 0x03)  # 非法数据值 | Illegal data value
        
        # 读取线圈数据 | Read coil data
        coils = self.data_store.get_coils(start_address, quantity)
        
        # 打包成字节 | Pack into bytes
        byte_count = (quantity + 7) // 8
        coil_bytes = []
        
        for byte_idx in range(byte_count):
            byte_val = 0
            for bit_idx in range(8):
                coil_idx = byte_idx * 8 + bit_idx
                if coil_idx < quantity and coils[coil_idx]:
                    byte_val |= (1 << bit_idx)
            coil_bytes.append(byte_val)
        
        return struct.pack('>BB', 0x01, byte_count) + bytes(coil_bytes)
    
    def _handle_read_discrete_inputs(self, pdu: bytes) -> bytes:
        """处理读离散输入请求 | Handle read discrete inputs request"""
        if len(pdu) != 5:
            return self._create_exception_response(0x02, 0x03)  # 非法数据值 | Illegal data value
        
        start_address, quantity = struct.unpack('>HH', pdu[1:5])
        
        if not (1 <= quantity <= 2000):
            return self._create_exception_response(0x02, 0x03)  # 非法数据值 | Illegal data value
        
        # 读取离散输入数据 | Read discrete input data
        inputs = self.data_store.get_discrete_inputs(start_address, quantity)
        
        # 打包成字节 | Pack into bytes
        byte_count = (quantity + 7) // 8
        input_bytes = []
        
        for byte_idx in range(byte_count):
            byte_val = 0
            for bit_idx in range(8):
                input_idx = byte_idx * 8 + bit_idx
                if input_idx < quantity and inputs[input_idx]:
                    byte_val |= (1 << bit_idx)
            input_bytes.append(byte_val)
        
        return struct.pack('>BB', 0x02, byte_count) + bytes(input_bytes)
    
    def _handle_read_holding_registers(self, pdu: bytes) -> bytes:
        """处理读保持寄存器请求 | Handle read holding registers request"""
        if len(pdu) != 5:
            return self._create_exception_response(0x03, 0x03)  # 非法数据值 | Illegal data value
        
        start_address, quantity = struct.unpack('>HH', pdu[1:5])
        
        if not (1 <= quantity <= 125):
            return self._create_exception_response(0x03, 0x03)  # 非法数据值 | Illegal data value
        
        # 读取寄存器数据 | Read register data
        registers = self.data_store.get_holding_registers(start_address, quantity)
        
        byte_count = quantity * 2
        response = struct.pack('>BB', 0x03, byte_count)
        
        for register in registers:
            response += struct.pack('>H', register)
        
        return response
    
    def _handle_read_input_registers(self, pdu: bytes) -> bytes:
        """处理读输入寄存器请求 | Handle read input registers request"""
        if len(pdu) != 5:
            return self._create_exception_response(0x04, 0x03)  # 非法数据值 | Illegal data value
        
        start_address, quantity = struct.unpack('>HH', pdu[1:5])
        
        if not (1 <= quantity <= 125):
            return self._create_exception_response(0x04, 0x03)  # 非法数据值 | Illegal data value
        
        # 读取寄存器数据 | Read register data
        registers = self.data_store.get_input_registers(start_address, quantity)
        
        byte_count = quantity * 2
        response = struct.pack('>BB', 0x04, byte_count)
        
        for register in registers:
            response += struct.pack('>H', register)
        
        return response
    
    def _handle_write_single_coil(self, pdu: bytes) -> bytes:
        """处理写单个线圈请求 | Handle write single coil request"""
        if len(pdu) != 5:
            return self._create_exception_response(0x05, 0x03)  # 非法数据值 | Illegal data value
        
        address, value = struct.unpack('>HH', pdu[1:5])
        
        if value not in (0x0000, 0xFF00):
            return self._create_exception_response(0x05, 0x03)  # 非法数据值 | Illegal data value
        
        # 写入线圈 | Write coil
        coil_value = value == 0xFF00
        self.data_store.set_coils(address, [coil_value])
        
        # 返回原请求 | Return original request
        return pdu
    
    def _handle_write_single_register(self, pdu: bytes) -> bytes:
        """处理写单个寄存器请求 | Handle write single register request"""
        if len(pdu) != 5:
            return self._create_exception_response(0x06, 0x03)  # 非法数据值 | Illegal data value
        
        address, value = struct.unpack('>HH', pdu[1:5])
        
        # 写入寄存器 | Write register
        self.data_store.set_holding_registers(address, [value])
        
        # 返回原请求 | Return original request
        return pdu
    
    def _handle_write_multiple_coils(self, pdu: bytes) -> bytes:
        """处理写多个线圈请求 | Handle write multiple coils request"""
        if len(pdu) < 6:
            return self._create_exception_response(0x0F, 0x03)  # 非法数据值 | Illegal data value
        
        start_address, quantity, byte_count = struct.unpack('>HHB', pdu[1:6])
        
        if not (1 <= quantity <= 1968) or byte_count != (quantity + 7) // 8:
            return self._create_exception_response(0x0F, 0x03)  # 非法数据值 | Illegal data value
        
        if len(pdu) != 6 + byte_count:
            return self._create_exception_response(0x0F, 0x03)  # 非法数据值 | Illegal data value
        
        # 解析线圈数据 | Parse coil data
        coil_data = pdu[6:]
        coils = []
        
        for byte_idx, byte_val in enumerate(coil_data):
            for bit_idx in range(8):
                if len(coils) >= quantity:
                    break
                coils.append(bool(byte_val & (1 << bit_idx)))
        
        # 写入线圈 | Write coils
        self.data_store.set_coils(start_address, coils[:quantity])
        
        # 返回确认响应 | Return confirmation response
        return struct.pack('>BHH', 0x0F, start_address, quantity)
    
    def _handle_write_multiple_registers(self, pdu: bytes) -> bytes:
        """处理写多个寄存器请求 | Handle write multiple registers request"""
        if len(pdu) < 6:
            return self._create_exception_response(0x10, 0x03)  # 非法数据值 | Illegal data value
        
        start_address, quantity, byte_count = struct.unpack('>HHB', pdu[1:6])
        
        if not (1 <= quantity <= 123) or byte_count != quantity * 2:
            return self._create_exception_response(0x10, 0x03)  # 非法数据值 | Illegal data value
        
        if len(pdu) != 6 + byte_count:
            return self._create_exception_response(0x10, 0x03)  # 非法数据值 | Illegal data value
        
        # 解析寄存器数据 | Parse register data
        register_data = pdu[6:]
        registers = []
        
        for i in range(0, len(register_data), 2):
            register_value = struct.unpack('>H', register_data[i:i+2])[0]
            registers.append(register_value)
        
        # 写入寄存器 | Write registers
        self.data_store.set_holding_registers(start_address, registers)
        
        # 返回确认响应 | Return confirmation response
        return struct.pack('>BHH', 0x10, start_address, quantity)
    
    def _create_exception_response(self, function_code: int, exception_code: int) -> bytes:
        """创建异常响应 | Create exception response
        
        Args:
            function_code: 原功能码 | Original function code
            exception_code: 异常码 | Exception code
                0x01: 非法功能码 | Illegal function code
                0x02: 非法数据地址 | Illegal data address
                0x03: 非法数据值 | Illegal data value
                0x04: 从站设备故障 | Slave device failure
        
        Returns:
            异常响应PDU | Exception response PDU
        """
        return struct.pack('>BB', function_code | 0x80, exception_code)
    
    def __enter__(self):
        """上下文管理器入口 | Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口 | Context manager exit"""
        self.stop()