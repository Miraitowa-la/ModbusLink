"""
ModbusLink 异步服务器抽象基类
定义了所有异步Modbus服务器实现必须遵循的统一接口。

ModbusLink Async Server Abstract Base Class
Defines the unified interface that all async Modbus server implementations must follow.
"""

from abc import ABC, abstractmethod
from typing import Optional, Any, Callable, Dict
import asyncio
import struct
from .data_store import ModbusDataStore
from ..common.exceptions import ModbusException, InvalidResponseError
from ..utils.logging import get_logger


class AsyncBaseModbusServer(ABC):
    """
    异步Modbus服务器抽象基类
    所有异步Modbus服务器实现（AsyncTCP、AsyncRTU、AsyncASCII等）都必须继承此类并实现所有抽象方法。
    这个设计将协议处理、数据存储管理等复杂性封装在基类中，
    为具体的传输层实现提供统一、简洁的接口。
    
    Async Modbus Server Abstract Base Class
    All async Modbus server implementations (AsyncTCP, AsyncRTU, AsyncASCII, etc.) must inherit from this class
    and implement all abstract methods. This design encapsulates complexities such as protocol processing
    and data store management in the base class, providing a unified and concise interface for specific
    transport layer implementations.
    """

    def __init__(self,
                 data_store: Optional[ModbusDataStore] = None,
                 slave_id: int = 1):
        """
        初始化异步Modbus服务器 | Initialize Async Modbus Server
        
        Args:
            data_store: 数据存储实例，如果为None则创建默认实例 | Data store instance, creates default if None
            slave_id: 从站地址 | Slave address
        """
        self.data_store = data_store or ModbusDataStore()
        self.slave_id = slave_id
        self._logger = get_logger("server.base")
        self._running = False
        self._server_task: Optional[asyncio.Task] = None

        # 功能码处理映射 | Function code handler mapping
        self._function_handlers: Dict[int, Callable[[int, bytes], bytes]] = {
            0x01: self._handle_read_coils,
            0x02: self._handle_read_discrete_inputs,
            0x03: self._handle_read_holding_registers,
            0x04: self._handle_read_input_registers,
            0x05: self._handle_write_single_coil,
            0x06: self._handle_write_single_register,
            0x0F: self._handle_write_multiple_coils,
            0x10: self._handle_write_multiple_registers,
        }

        self._logger.info(
            cn=f"Modbus服务器初始化完成: 从站地址 {slave_id}",
            en=f"Modbus server initialized: Slave ID {slave_id}"
        )

    @abstractmethod
    async def start(self) -> None:
        """
        启动异步服务器
        开始监听客户端连接和请求。
        
        Start Async Server
        Begin listening for client connections and requests.
        
        Raises:
            ConnectionError: 当无法启动服务器时 | When server cannot be started
        """
        pass

    @abstractmethod
    async def stop(self) -> None:
        """
        停止异步服务器
        停止监听并关闭所有连接。
        
        Stop Async Server
        Stop listening and close all connections.
        """
        pass

    @abstractmethod
    async def is_running(self) -> bool:
        """
        检查服务器运行状态 | Check Server Running Status
        
        Returns:
            如果服务器正在运行返回True，否则返回False | True if server is running, False otherwise
        """
        pass

    def process_request(self, slave_id: int, pdu: bytes) -> bytes:
        """
        处理Modbus请求PDU
        这是服务器的核心方法，处理接收到的PDU并返回响应PDU。
        
        Process Modbus Request PDU
        This is the core method of the server, processes received PDU and returns response PDU.
        
        Args:
            slave_id: 从站地址 | Slave address
            pdu: 请求的协议数据单元 | Request Protocol Data Unit
            
        Returns:
            响应的协议数据单元 | Response Protocol Data Unit
        """
        try:
            if len(pdu) < 1:
                raise InvalidResponseError(
                    cn="PDU长度不足",
                    en="PDU length insufficient"
                )

            # 检查从站地址 | Check slave address
            if slave_id != self.slave_id and slave_id != 0:  # 0是广播地址 | 0 is broadcast address
                self._logger.debug(
                    cn=f"忽略非本站请求: {slave_id}",
                    en=f"Ignoring request for different slave: {slave_id}"
                )
                return b''  # 不响应非本站请求 | Don't respond to requests for other slaves

            function_code = pdu[0]
            data = pdu[1:]

            self._logger.debug(
                cn=f"处理请求: 功能码 0x{function_code:02X}, 数据长度 {len(data)}",
                en=f"Proce ssing request: Function Code 0x{function_code:02X}, Data Length {len(data)}"
            )

            # 查找功能码处理器 | Find function code handler
            if function_code in self._function_handlers:
                response_pdu = self._function_handlers[function_code](slave_id, data)
                self._logger.debug(
                    cn=f"请求处理完成: 响应长度 {len(response_pdu)}",
                    en=f"Request processed: Response Length {len(response_pdu)}"
                )
                return response_pdu
            else:
                # 不支持的功能码 | Unsupported function code
                self._logger.warning(
                    cn=f"不支持的功能码: 0x{function_code:02X}",
                    en=f"Unsupported function code: 0x{function_code:02X}"
                )
                return self._create_exception_response(function_code, 0x01)  # 非法功能码 | Illegal function code

        except ModbusException as e:
            self._logger.warning(
                cn=f"Modbus异常: {e}",
                en=f"Modbus exception: {e}"
            )
            return self._create_exception_response(pdu[0], e.exception_code)
        except Exception as e:
            self._logger.error(
                cn=f"处理请求时发生错误: {e}",
                en=f"Error processing request: {e}"
            )
            return self._create_exception_response(pdu[0] if len(pdu) > 0 else 0x00,
                                                   0x04)  # 从站设备故障 | Slave device failure

    def _create_exception_response(self, function_code: int, exception_code: int) -> bytes:
        """
        创建异常响应PDU | Create Exception Response PDU
        
        Args:
            function_code: 原始功能码 | Original function code
            exception_code: 异常码 | Exception code
            
        Returns:
            异常响应PDU | Exception response PDU
        """
        return struct.pack(">BB", function_code | 0x80, exception_code)

    def _handle_read_coils(self, slave_id: int, data: bytes) -> bytes:
        """处理读取线圈请求（功能码0x01） | Handle Read Coils Request (Function Code 0x01)"""
        if len(data) < 4:
            raise ModbusException(0x03, 0x01)  # 非法数据值 | Illegal data value

        start_address, quantity = struct.unpack(">HH", data[:4])

        if not (1 <= quantity <= 2000):
            raise ModbusException(0x03, 0x01)  # 非法数据值 | Illegal data value

        try:
            coils = self.data_store.read_coils(start_address, quantity)
        except ValueError:
            raise ModbusException(0x02, 0x01)  # 非法数据地址 | Illegal data address

        # 将布尔值打包为字节 | Pack boolean values into bytes
        byte_count = (quantity + 7) // 8
        response_data = bytearray(byte_count)

        for i, coil in enumerate(coils):
            if coil:
                byte_index = i // 8
                bit_index = i % 8
                response_data[byte_index] |= (1 << bit_index)

        return struct.pack(">BB", 0x01, byte_count) + bytes(response_data)

    def _handle_read_discrete_inputs(self, slave_id: int, data: bytes) -> bytes:
        """处理读取离散输入请求（功能码0x02） | Handle Read Discrete Inputs Request (Function Code 0x02)"""
        if len(data) < 4:
            raise ModbusException(0x03, 0x02)  # 非法数据值 | Illegal data value

        start_address, quantity = struct.unpack(">HH", data[:4])

        if not (1 <= quantity <= 2000):
            raise ModbusException(0x03, 0x02)  # 非法数据值 | Illegal data value

        try:
            inputs = self.data_store.read_discrete_inputs(start_address, quantity)
        except ValueError:
            raise ModbusException(0x02, 0x02)  # 非法数据地址 | Illegal data address

        # 将布尔值打包为字节 | Pack boolean values into bytes
        byte_count = (quantity + 7) // 8
        response_data = bytearray(byte_count)

        for i, input_val in enumerate(inputs):
            if input_val:
                byte_index = i // 8
                bit_index = i % 8
                response_data[byte_index] |= (1 << bit_index)

        return struct.pack(">BB", 0x02, byte_count) + bytes(response_data)

    def _handle_read_holding_registers(self, slave_id: int, data: bytes) -> bytes:
        """处理读取保持寄存器请求（功能码0x03） | Handle Read Holding Registers Request (Function Code 0x03)"""
        if len(data) < 4:
            raise ModbusException(0x03, 0x03)  # 非法数据值 | Illegal data value

        start_address, quantity = struct.unpack(">HH", data[:4])

        if not (1 <= quantity <= 125):
            raise ModbusException(0x03, 0x03)  # 非法数据值 | Illegal data value

        try:
            registers = self.data_store.read_holding_registers(start_address, quantity)
        except ValueError:
            raise ModbusException(0x02, 0x03)  # 非法数据地址 | Illegal data address

        byte_count = quantity * 2
        response_data = struct.pack(">BB", 0x03, byte_count)

        for register in registers:
            response_data += struct.pack(">H", register)

        return response_data

    def _handle_read_input_registers(self, slave_id: int, data: bytes) -> bytes:
        """处理读取输入寄存器请求（功能码0x04） | Handle Read Input Registers Request (Function Code 0x04)"""
        if len(data) < 4:
            raise ModbusException(0x03, 0x04)  # 非法数据值 | Illegal data value

        start_address, quantity = struct.unpack(">HH", data[:4])

        if not (1 <= quantity <= 125):
            raise ModbusException(0x03, 0x04)  # 非法数据值 | Illegal data value

        try:
            registers = self.data_store.read_input_registers(start_address, quantity)
        except ValueError:
            raise ModbusException(0x02, 0x04)  # 非法数据地址 | Illegal data address

        byte_count = quantity * 2
        response_data = struct.pack(">BB", 0x04, byte_count)

        for register in registers:
            response_data += struct.pack(">H", register)

        return response_data

    def _handle_write_single_coil(self, slave_id: int, data: bytes) -> bytes:
        """处理写入单个线圈请求（功能码0x05） | Handle Write Single Coil Request (Function Code 0x05)"""
        if len(data) < 4:
            raise ModbusException(0x03, 0x05)  # 非法数据值 | Illegal data value

        address, value = struct.unpack(">HH", data[:4])

        if value not in (0x0000, 0xFF00):
            raise ModbusException(0x03, 0x05)  # 非法数据值 | Illegal data value

        coil_value = value == 0xFF00

        try:
            self.data_store.write_coils(address, [coil_value])
        except ValueError:
            raise ModbusException(0x02, 0x05)  # 非法数据地址 | Illegal data address

        # 回显请求 | Echo request
        return struct.pack(">BHH", 0x05, address, value)

    def _handle_write_single_register(self, slave_id: int, data: bytes) -> bytes:
        """处理写入单个寄存器请求（功能码0x06） | Handle Write Single Register Request (Function Code 0x06)"""
        if len(data) < 4:
            raise ModbusException(0x03, 0x06)  # 非法数据值 | Illegal data value

        address, value = struct.unpack(">HH", data[:4])

        try:
            self.data_store.write_holding_registers(address, [value])
        except ValueError:
            raise ModbusException(0x02, 0x06)  # 非法数据地址 | Illegal data address

        # 回显请求 | Echo request
        return struct.pack(">BHH", 0x06, address, value)

    def _handle_write_multiple_coils(self, slave_id: int, data: bytes) -> bytes:
        """处理写入多个线圈请求（功能码0x0F） | Handle Write Multiple Coils Request (Function Code 0x0F)"""
        if len(data) < 5:
            raise ModbusException(0x03, 0x0F)  # 非法数据值 | Illegal data value

        start_address, quantity, byte_count = struct.unpack(">HHB", data[:5])

        if not (1 <= quantity <= 1968) or byte_count != (quantity + 7) // 8:
            raise ModbusException(0x03, 0x0F)  # 非法数据值 | Illegal data value

        if len(data) < 5 + byte_count:
            raise ModbusException(0x03, 0x0F)  # 非法数据值 | Illegal data value

        coil_data = data[5:5 + byte_count]
        coils = []

        for i in range(quantity):
            byte_index = i // 8
            bit_index = i % 8
            coil_value = bool(coil_data[byte_index] & (1 << bit_index))
            coils.append(coil_value)

        try:
            self.data_store.write_coils(start_address, coils)
        except ValueError:
            raise ModbusException(0x02, 0x0F)  # 非法数据地址 | Illegal data address

        return struct.pack(">BHH", 0x0F, start_address, quantity)

    def _handle_write_multiple_registers(self, slave_id: int, data: bytes) -> bytes:
        """处理写入多个寄存器请求（功能码0x10） | Handle Write Multiple Registers Request (Function Code 0x10)"""
        if len(data) < 5:
            raise ModbusException(0x03, 0x10)  # 非法数据值 | Illegal data value

        start_address, quantity, byte_count = struct.unpack(">HHB", data[:5])

        if not (1 <= quantity <= 123) or byte_count != quantity * 2:
            raise ModbusException(0x03, 0x10)  # 非法数据值 | Illegal data value

        if len(data) < 5 + byte_count:
            raise ModbusException(0x03, 0x10)  # 非法数据值 | Illegal data value

        register_data = data[5:5 + byte_count]
        registers = []

        for i in range(quantity):
            register_value = struct.unpack(">H", register_data[i * 2:(i + 1) * 2])[0]
            registers.append(register_value)

        try:
            self.data_store.write_holding_registers(start_address, registers)
        except ValueError:
            raise ModbusException(0x02, 0x10)  # 非法数据地址 | Illegal data address

        return struct.pack(">BHH", 0x10, start_address, quantity)

    async def __aenter__(self) -> "AsyncBaseModbusServer":
        """异步上下文管理器入口 | Async Context Manager Entry"""
        await self.start()
        return self

    async def __aexit__(self, exc_type: Optional[type], exc_val: Optional[BaseException],
                        exc_tb: Optional[Any]) -> None:
        """异步上下文管理器出口 | Async Context Manager Exit"""
        await self.stop()
