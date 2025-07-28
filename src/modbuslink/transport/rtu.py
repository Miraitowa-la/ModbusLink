"""ModbusLink RTU传输层实现


RTU Transport Layer Implementation

实现基于串口的Modbus RTU协议传输，包括CRC16校验。


Implements Modbus RTU protocol transport based on serial port, including CRC16 validation.
"""

from typing import Optional

import serial

from .base import BaseTransport
from ..common.exceptions import (
    ConnectionError,
    TimeoutError,
    CRCError,
    InvalidResponseError,
)
from ..utils.crc import CRC16Modbus
from ..utils.logging import get_logger


class RtuTransport(BaseTransport):
    """Modbus RTU传输层实现


    Modbus RTU Transport Layer Implementation

    处理基于串口的Modbus RTU通信，包括：


    Handles Modbus RTU communication based on serial port, including:
    - 串口连接管理 | Serial port connection management
    - CRC16校验码的计算和验证 | CRC16 checksum calculation and validation
    - ADU（应用数据单元）的构建和解析 | ADU (Application Data Unit) construction and parsing
    - 错误处理和超时管理 | Error handling and timeout management
    """

    def __init__(
        self,
        port: str,
        baudrate: int = 9600,
        bytesize: int = serial.EIGHTBITS,
        parity: str = serial.PARITY_NONE,
        stopbits: float = serial.STOPBITS_ONE,
        timeout: float = 1.0,
    ):
        """初始化RTU传输层


        Initialize RTU transport layer

        Args:
            port: 串口名称 (如 'COM1', '/dev/ttyUSB0') | Serial port name (e.g. 'COM1', '/dev/ttyUSB0')
            baudrate: 波特率，默认9600 | Baud rate, default 9600
            bytesize: 数据位，默认8位 | Data bits, default 8 bits
            parity: 校验位，默认无校验 | Parity, default no parity
            stopbits: 停止位，默认1位 | Stop bits, default 1 bit
            timeout: 超时时间（秒），默认1.0秒 | Timeout in seconds, default 1.0 seconds

        Raises:
            ValueError: 当参数无效时 | When parameters are invalid
            TypeError: 当参数类型错误时 | When parameter types are incorrect
        """
        if not port or not isinstance(port, str):
            raise ValueError(
                "串口名称不能为空且必须是字符串 | Port name cannot be empty and must be a string"
            )
        if not isinstance(baudrate, int) or baudrate <= 0:
            raise ValueError("波特率必须是正整数 | Baudrate must be a positive integer")
        if not isinstance(timeout, (int, float)) or timeout <= 0:
            raise ValueError("超时时间必须是正数 | Timeout must be a positive number")

        self.port = port
        self.baudrate = baudrate
        self.bytesize = bytesize
        self.parity = parity
        self.stopbits = stopbits
        self.timeout = timeout

        self._serial: Optional[serial.Serial] = None
        self._logger = get_logger("transport.rtu")

    def open(self) -> None:
        """打开串口连接


        Open serial port connection"""
        try:
            self._serial = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                bytesize=self.bytesize,
                parity=self.parity,
                stopbits=self.stopbits,
                timeout=self.timeout,
            )

            if not self._serial.is_open:
                raise ConnectionError(
                    f"无法打开串口 | Unable to open serial port {self.port}"
                )

            self._logger.info(
                f"RTU连接已建立 | RTU connection established: {self.port} @ {self.baudrate}bps"
            )

        except serial.SerialException as e:
            raise ConnectionError(f"串口连接失败 | Serial port connection failed: {e}")

    def close(self) -> None:
        """关闭串口连接


        Close serial port connection"""
        if self._serial and self._serial.is_open:
            self._serial.close()
            self._logger.info(f"RTU连接已关闭 | RTU connection closed: {self.port}")

    def is_open(self) -> bool:
        """检查串口连接状态


        Check serial port connection status"""
        return self._serial is not None and self._serial.is_open

    def send_and_receive(self, slave_id: int, pdu: bytes) -> bytes:
        """发送PDU并接收响应


        Send PDU and receive response

        实现RTU协议的完整通信流程：


        Implements complete RTU protocol communication flow:
        1. 构建ADU（地址 + PDU + CRC） | Build ADU (Address + PDU + CRC)
        2. 发送请求 | Send request
        3. 接收响应 | Receive response
        4. 验证CRC | Validate CRC
        5. 返回响应PDU | Return response PDU
        """
        if not self.is_open():
            raise ConnectionError(
                "串口连接未建立 | Serial port connection not established"
            )

        # 1. 构建请求帧 | Build request frame
        frame_prefix = bytes([slave_id]) + pdu
        crc = CRC16Modbus.calculate(frame_prefix)
        request_adu = frame_prefix + crc

        self._logger.debug(f"RTU发送 | RTU Send: {request_adu.hex(' ').upper()}")

        try:
            # 2. 清空接收缓冲区并发送请求 | Clear receive buffer and send request
            self._serial.reset_input_buffer()
            self._serial.write(request_adu)

            # 3. 接收响应 | Receive response
            response_adu = self._receive_response(slave_id, pdu[0])

            self._logger.debug(
                f"RTU接收 | RTU Receive: {response_adu.hex(' ').upper()}"
            )

            # 4. 验证CRC | Validate CRC
            if not CRC16Modbus.validate(response_adu):
                raise CRCError("响应CRC校验失败 | Response CRC validation failed")

            # 5. 验证从站地址 | Validate slave address
            if response_adu[0] != slave_id:
                raise InvalidResponseError(
                    f"从站地址不匹配 | Slave address mismatch: 期望 | Expected {slave_id}, 收到 | Received {response_adu[0]}"
                )

            # 6. 检查是否为异常响应 | Check if it's an exception response
            response_function_code = response_adu[1]
            if response_function_code & 0x80:  # 异常响应 | Exception response
                from ..common.exceptions import ModbusException

                exception_code = response_adu[2] if len(response_adu) > 2 else 0
                raise ModbusException(exception_code, pdu[0])

            # 7. 返回PDU部分（去除地址和CRC） | Return PDU part (remove address and CRC)
            return response_adu[1:-2]

        except serial.SerialTimeoutException:
            raise TimeoutError(
                f"RTU通信超时 | RTU communication timeout ({self.timeout}秒 | seconds)"
            )
        except serial.SerialException as e:
            raise ConnectionError(
                f"串口通信错误 | Serial port communication error: {e}"
            )

    def _receive_response(self, expected_slave_id: int, function_code: int) -> bytes:
        """接收完整的响应帧


        Receive complete response frame

        根据功能码预估响应长度，智能接收数据。


        Estimate response length based on function code and intelligently receive data.
        """
        # 首先读取最小响应（地址 + 功能码） | First read minimum response (address + function code)
        response = self._serial.read(2)
        if len(response) < 2:
            raise TimeoutError("接收响应超时 | Receive response timeout")

        # 检查是否为异常响应 | Check if it's an exception response
        if response[1] & 0x80:  # 异常响应 | Exception response
            # 异常响应格式：地址 + 异常功能码 + 异常码 + CRC (共5字节) | Exception response format: address + exception function code + exception code + CRC (total 5 bytes)
            remaining = self._serial.read(3)  # 异常码 + CRC | Exception code + CRC
            if len(remaining) < 3:
                raise TimeoutError(
                    "接收异常响应超时 | Receive exception response timeout"
                )
            return response + remaining

        # 正常响应，根据功能码确定剩余长度 | Normal response, determine remaining length based on function code
        if function_code in [
            0x01,
            0x02,
        ]:  # 读取线圈/离散输入 | Read coils/discrete inputs
            # 格式：地址 + 功能码 + 字节数 + 数据 + CRC | Format: address + function code + byte count + data + CRC
            byte_count_data = self._serial.read(1)
            if len(byte_count_data) < 1:
                raise TimeoutError("接收字节数超时 | Receive byte count timeout")
            byte_count = byte_count_data[0]
            remaining_data = self._serial.read(
                byte_count + 2
            )  # 数据 + CRC | Data + CRC
            if len(remaining_data) < byte_count + 2:
                raise TimeoutError("接收数据超时 | Receive data timeout")
            return response + byte_count_data + remaining_data

        elif function_code in [
            0x03,
            0x04,
        ]:  # 读取保持寄存器/输入寄存器 | Read holding registers/input registers
            # 格式：地址 + 功能码 + 字节数 + 数据 + CRC | Format: address + function code + byte count + data + CRC
            byte_count_data = self._serial.read(1)
            if len(byte_count_data) < 1:
                raise TimeoutError("接收字节数超时 | Receive byte count timeout")
            byte_count = byte_count_data[0]
            remaining_data = self._serial.read(
                byte_count + 2
            )  # 数据 + CRC | Data + CRC
            if len(remaining_data) < byte_count + 2:
                raise TimeoutError("接收数据超时 | Receive data timeout")
            return response + byte_count_data + remaining_data

        elif function_code in [
            0x05,
            0x06,
        ]:  # 写单个线圈/寄存器 | Write single coil/register
            # 格式：地址 + 功能码 + 地址 + 值 + CRC (共8字节) | Format: address + function code + address + value + CRC (total 8 bytes)
            remaining = self._serial.read(6)  # 地址 + 值 + CRC | Address + value + CRC
            if len(remaining) < 6:
                raise TimeoutError("接收写响应超时 | Receive write response timeout")
            return response + remaining

        elif function_code in [
            0x0F,
            0x10,
        ]:  # 写多个线圈/寄存器 | Write multiple coils/registers
            # 格式：地址 + 功能码 + 起始地址 + 数量 + CRC (共8字节) | Format: address + function code + starting address + quantity + CRC (total 8 bytes)
            remaining = self._serial.read(
                6
            )  # 起始地址 + 数量 + CRC | Starting address + quantity + CRC
            if len(remaining) < 6:
                raise TimeoutError("接收写响应超时 | Receive write response timeout")
            return response + remaining

        else:
            # 未知功能码，尝试读取更多数据 | Unknown function code, try to read more data
            remaining = self._serial.read(
                10
            )  # 最多再读10字节 | Read at most 10 more bytes
            return response + remaining

    def __repr__(self) -> str:
        """字符串表示


        String representation"""
        status = "已连接 | Connected" if self.is_open() else "未连接 | Disconnected"
        return f"RtuTransport({self.port}@{self.baudrate}bps, {status})"
