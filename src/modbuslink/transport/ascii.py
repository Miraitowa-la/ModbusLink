"""ModbusLink ASCII传输层实现
实现基于串口的Modbus ASCII协议传输，包括LRC校验。

ASCII Transport Layer Implementation
Implements Modbus ASCII protocol transport based on serial port, including LRC validation.
"""

import time
from typing import Optional

import serial

from .base import BaseTransport
from ..common.exceptions import (
    ConnectionError,
    TimeoutError,
    CRCError,
    InvalidResponseError,
)
from ..utils.logging import get_logger


class AsciiTransport(BaseTransport):
    """
    Modbus ASCII传输层实现
    处理基于串口的Modbus ASCII通信，包括：

    Modbus ASCII Transport Layer Implementation
    Handles Modbus ASCII communication based on serial port, including:

    - 串口连接管理 | Serial port connection management
    - LRC校验码的计算和验证 | LRC checksum calculation and validation
    - ASCII编码和解码 | ASCII encoding and decoding
    - ADU（应用数据单元）的构建和解析 | ADU (Application Data Unit) construction and parsing
    - 错误处理和超时管理 | Error handling and timeout management
    """

    def __init__(
        self,
        port: str,
        baudrate: int = 9600,
        bytesize: int = 7,
        parity: str = "E",
        stopbits: float = 1,
        timeout: float = 1.0,
    ):
        """
        初始化ASCII传输层

        Initialize ASCII transport layer

        Args:
            port: 串口名称 (如 'COM1', '/dev/ttyUSB0') | Serial port name (e.g. 'COM1', '/dev/ttyUSB0')
            baudrate: 波特率，默认9600 | Baud rate, default 9600
            bytesize: 数据位，默认7位 | Data bits, default 7 bits
            parity: 校验位，默认偶校验 | Parity, default even parity
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
        self._logger = get_logger("transport.ascii")

    def open(self) -> None:
        """
        打开串口连接

        Open serial port connection
        """
        try:
            self._serial = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                bytesize=self.bytesize,
                parity=self.parity,
                stopbits=self.stopbits,
                timeout=self.timeout,
            )

            self._logger.info(
                f"ASCII连接已建立 | ASCII connection established: {self.port} @ {self.baudrate}bps"
            )

        except Exception as e:
            raise ConnectionError(f"串口连接失败 | Serial port connection failed: {e}")

    def close(self) -> None:
        """
        关闭串口连接

        Close serial port connection
        """
        if self._serial and self._serial.is_open:
            try:
                self._serial.close()
                self._logger.info(f"ASCII连接已关闭 | ASCII connection closed: {self.port}")
            except Exception as e:
                self._logger.debug(
                    f"关闭串口连接时出现错误（可忽略）| Error during serial connection close (ignorable): {e}"
                )
            finally:
                self._serial = None

    def is_open(self) -> bool:
        """
        检查串口连接状态

        Check serial port connection status
        """
        return self._serial is not None and self._serial.is_open

    def send_and_receive(self, slave_id: int, pdu: bytes) -> bytes:
        """
        发送PDU并接收响应
        实现ASCII协议的完整通信流程：

        Send PDU and receive response
        Implements complete ASCII protocol communication flow:

        1. 构建ASCII帧（:地址PDU LRC CR LF） | Build ASCII frame (:Address PDU LRC CR LF)
        2. 发送请求 | Send request
        3. 接收响应 | Receive response
        4. 验证LRC | Validate LRC
        5. 返回响应PDU | Return response PDU
        """
        if not self.is_open():
            raise ConnectionError("串口连接未建立 | Serial port connection not established")

        # 1. 构建请求帧 | Build request frame
        frame_data = bytes([slave_id]) + pdu
        lrc = self._calculate_lrc(frame_data)
        
        # ASCII编码：冒号 + 数据的十六进制表示 + LRC + CRLF | ASCII encoding: colon + hex data + LRC + CRLF
        ascii_data = frame_data + bytes([lrc])
        ascii_frame = b':' + ascii_data.hex().upper().encode('ascii') + b'\r\n'

        self._logger.debug(
            f"发送ASCII请求 | Sending ASCII request: {ascii_frame.decode('ascii', errors='ignore')}"
        )

        try:
            # 2. 清空接收缓冲区并发送请求 | Clear receive buffer and send request
            if self._serial.in_waiting > 0:
                self._serial.read(self._serial.in_waiting)

            self._serial.write(ascii_frame)
            self._serial.flush()

            # 3. 接收响应 | Receive response
            function_code = pdu[0] if pdu else 0
            response_pdu = self._receive_response(slave_id, function_code)

            self._logger.debug(
                f"接收到ASCII响应PDU | Received ASCII response PDU: {response_pdu.hex()}"
            )

            return response_pdu

        except serial.SerialTimeoutException:
            raise TimeoutError(
                f"ASCII通信超时 | ASCII communication timeout: {self.timeout}s"
            )
        except Exception as e:
            if isinstance(e, (ConnectionError, TimeoutError, CRCError, InvalidResponseError)):
                raise
            raise ConnectionError(f"ASCII通信错误 | ASCII communication error: {e}")

    def _receive_response(self, expected_slave_id: int, function_code: int) -> bytes:
        """
        接收并验证响应帧

        Receive and validate response frame

        Args:
            expected_slave_id: 期望的从站地址 | Expected slave address
            function_code: 功能码 | Function code

        Returns:
            响应的PDU部分 | PDU part of response

        Raises:
            TimeoutError: 接收超时 | Receive timeout
            CRCError: LRC校验失败 | LRC validation failed
            InvalidResponseError: 响应格式无效 | Invalid response format
        """
        try:
            # 接收完整的ASCII帧直到CRLF | Receive complete ASCII frame until CRLF
            response_line = b''
            start_time = time.time()
            
            while True:
                if time.time() - start_time > self.timeout:
                    raise TimeoutError(f"接收ASCII响应超时 | Receive ASCII response timeout: {self.timeout}s")
                
                if self._serial.in_waiting > 0:
                    char = self._serial.read(1)
                    if not char:
                        continue
                    
                    response_line += char
                    
                    # 检查是否接收到完整帧 | Check if complete frame received
                    if response_line.endswith(b'\r\n'):
                        break
                else:
                    time.sleep(0.001)  # 短暂等待避免CPU占用过高 | Short wait to avoid high CPU usage

            # 验证帧格式 | Validate frame format
            if not response_line.startswith(b':'):
                raise InvalidResponseError("ASCII响应帧格式无效：缺少起始冒号 | Invalid ASCII response frame format: missing start colon")
            
            if not response_line.endswith(b'\r\n'):
                raise InvalidResponseError("ASCII响应帧格式无效：缺少结束符 | Invalid ASCII response frame format: missing end markers")

            # 提取十六进制数据部分 | Extract hex data part
            hex_data = response_line[1:-2].decode('ascii')
            
            if len(hex_data) % 2 != 0:
                raise InvalidResponseError("ASCII响应帧格式无效：十六进制数据长度不是偶数 | Invalid ASCII response frame format: hex data length is not even")

            # 将十六进制字符串转换为字节 | Convert hex string to bytes
            try:
                response_bytes = bytes.fromhex(hex_data)
            except ValueError as e:
                raise InvalidResponseError(f"ASCII响应帧格式无效：十六进制数据解析失败 | Invalid ASCII response frame format: hex data parsing failed: {e}")

            if len(response_bytes) < 3:  # 至少需要：地址 + 功能码 + LRC | At least need: address + function code + LRC
                raise InvalidResponseError("ASCII响应帧太短 | ASCII response frame too short")

            # 分离数据和LRC | Separate data and LRC
            frame_data = response_bytes[:-1]
            received_lrc = response_bytes[-1]

            # 验证LRC | Validate LRC
            expected_lrc = self._calculate_lrc(frame_data)
            if received_lrc != expected_lrc:
                raise CRCError(
                    f"LRC校验失败 | LRC validation failed: "
                    f"expected {expected_lrc:02X}, got {received_lrc:02X}"
                )

            # 验证从站地址 | Validate slave address
            received_slave_id = frame_data[0]
            if received_slave_id != expected_slave_id:
                raise InvalidResponseError(
                    f"从站地址不匹配 | Slave address mismatch: expected {expected_slave_id}, got {received_slave_id}"
                )

            # 提取PDU | Extract PDU
            response_pdu = frame_data[1:]
            
            if len(response_pdu) == 0:
                raise InvalidResponseError("响应PDU为空 | Response PDU is empty")

            received_function_code = response_pdu[0]

            # 检查是否为异常响应 | Check if it's an exception response
            if received_function_code & 0x80:
                if len(response_pdu) != 2:
                    raise InvalidResponseError("异常响应格式无效 | Invalid exception response format")
                return response_pdu

            # 验证功能码 | Validate function code
            if received_function_code != function_code:
                raise InvalidResponseError(
                    f"功能码不匹配 | Function code mismatch: expected {function_code}, got {received_function_code}"
                )

            return response_pdu

        except serial.SerialTimeoutException:
            raise TimeoutError(f"接收ASCII响应超时 | Receive ASCII response timeout: {self.timeout}s")

    @staticmethod
    def _calculate_lrc(data: bytes) -> int:
        """
        计算LRC（纵向冗余校验）
        LRC = (-(所有字节的和)) & 0xFF

        Calculate LRC (Longitudinal Redundancy Check)
        LRC = (-(sum of all bytes)) & 0xFF

        Args:
            data: 要计算LRC的数据 | Data to calculate LRC for

        Returns:
            LRC校验码 | LRC checksum
        """
        lrc = 0
        for byte in data:
            lrc += byte
        return (-lrc) & 0xFF

    def __repr__(self) -> str:
        """
        返回传输层的字符串表示

        Return string representation of transport layer
        """
        status = "已连接 | Connected" if self.is_open() else "未连接 | Disconnected"
        return (
            f"AsciiTransport(port='{self.port}', baudrate={self.baudrate}, "
            f"timeout={self.timeout}, status='{status}')"
        )