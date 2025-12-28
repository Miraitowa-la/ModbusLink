"""
ModbusLink 异步ASCII传输层实现
实现基于asyncio的异步Modbus ASCII协议传输，包括LRC校验。

Async ASCII Transport Layer Implementation
Implements async Modbus ASCII protocol transport based on asyncio, including LRC validation.
"""

import asyncio
from typing import Optional

import serial_asyncio

from .async_base import AsyncBaseTransport
from ..common.exceptions import (
    ConnectionError,
    TimeoutError,
    CRCError,
    InvalidResponseError,
)
from ..common.language import get_message
from ..utils.logging import get_logger


class AsyncAsciiTransport(AsyncBaseTransport):
    """
    异步Modbus ASCII传输层实现
    处理基于asyncio的异步Modbus ASCII通信，包括：

    Async Modbus ASCII Transport Layer Implementation
    Handles async Modbus ASCII communication based on asyncio, including:

    - 异步串口连接管理 | Async serial port connection management
    - LRC校验码的计算和验证 | LRC checksum calculation and validation
    - ASCII编码和解码 | ASCII encoding and decoding
    - ADU（应用数据单元）的构建和解析 | ADU (Application Data Unit) construction and parsing
    - 异步错误处理和超时管理 | Async error handling and timeout management
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
        初始化异步ASCII传输层 | Initialize async ASCII transport layer

        Args:
            port: 串口名称 (如 'COM1', '/dev/ttyUSB0') | Serial port name (e.g. 'COM1', '/dev/ttyUSB0')
            baudrate: 波特率，默认9600 | Baud rate, default 9600
            bytesize: 数据位，默认7位 | Data bits, default 7 bits
            parity: 校验位，默认偶校验 | Parity, default even parity
            stopbits: 停止位，默认1位 | Stop bits, default 1 bit
            timeout: 超时时间（秒），默认1.0秒 | Timeout in seconds, default 1.0 seconds

        Raises:
            ValueError: 当参数无效时 | When parameters are invalid
        """
        if not port or not isinstance(port, str):
            raise ValueError(get_message(
                cn="串口名称不能为空且必须是字符串",
                en="Port name cannot be empty and must be a string"
            ))
        if not isinstance(baudrate, int) or baudrate <= 0:
            raise ValueError(get_message(
                cn="波特率必须是正整数",
                en="Baudrate must be a positive integer"
            ))
        if not isinstance(timeout, (int, float)) or timeout <= 0:
            raise ValueError(get_message(
                cn="超时时间必须是正数",
                en="Timeout must be a positive number"
            ))

        self.port = port
        self.baudrate = baudrate
        self.bytesize = bytesize
        self.parity = parity
        self.stopbits = stopbits
        self.timeout = timeout

        self._reader: Optional[asyncio.StreamReader] = None
        self._writer: Optional[asyncio.StreamWriter] = None
        self._logger = get_logger("transport.async_ascii")
        self._lock = asyncio.Lock()

    async def open(self) -> None:
        """异步打开串口连接 | Async open serial port connection"""
        try:
            self._reader, self._writer = await serial_asyncio.open_serial_connection(
                url=self.port,
                baudrate=self.baudrate,
                bytesize=self.bytesize,
                parity=self.parity,
                stopbits=self.stopbits,
            )

            self._logger.info(
                cn=f"异步ASCII连接已建立: {self.port} @ {self.baudrate}bps",
                en=f"Async ASCII connection established: {self.port} @ {self.baudrate}bps"
            )

        except Exception as e:
            raise ConnectionError(
                cn=f"异步串口连接失败: {e}",
                en=f"Async serial port connection failed: {e}"
            )

    async def close(self) -> None:
        """异步关闭串口连接 | sync close serial port connection"""
        if self._writer:
            try:
                self._writer.close()
                await self._writer.wait_closed()
                self._logger.info(
                    cn=f"异步ASCII连接已关闭: {self.port}",
                    en=f"Async ASCII connection closed: {self.port}"
                )
            except Exception as e:
                self._logger.debug(
                    cn=f"关闭异步串口连接时出现错误（可忽略）: {e}",
                    en=f"Error during async serial connection close (ignorable): {e}"
                )
            finally:
                self._reader = None
                self._writer = None

    async def is_open(self) -> bool:
        """异步检查串口连接状态 | Async check serial port connection status"""
        return self._reader is not None and self._writer is not None and not self._writer.is_closing()

    async def send_and_receive(self, slave_id: int, pdu: bytes) -> bytes:
        """
        异步发送PDU并接收响应
        实现异步ASCII协议的完整通信流程：

        Async send PDU and receive response
        Implements complete async ASCII protocol communication flow:

        1. 构建ASCII帧（:地址PDU LRC CR LF） | Build ASCII frame (:Address PDU LRC CR LF)
        2. 异步发送请求 | Async send request
        3. 异步接收响应 | Async receive response
        4. 验证LRC | Validate LRC
        5. 返回响应PDU | Return response PDU
        """
        # 使用锁确保并发安全 | Use lock to ensure concurrent safety
        async with self._lock:
            if not await self.is_open():
                raise ConnectionError(
                    cn="异步串口连接未建立",
                    en="Async serial port connection not established"
                )

            # 1. 构建请求帧 | Build request frame
            frame_data = bytes([slave_id]) + pdu
            lrc = self._calculate_lrc(frame_data)

            # ASCII编码：冒号 + 数据的十六进制表示 + LRC + CRLF | ASCII encoding: colon + hex data + LRC + CRLF
            ascii_data = frame_data + bytes([lrc])
            ascii_frame = b':' + ascii_data.hex().upper().encode('ascii') + b'\r\n'

            self._logger.debug(
                cn=f"发送异步ASCII请求: {ascii_frame.decode('ascii', errors='ignore')}",
                en=f"Sending async ASCII request: {ascii_frame.decode('ascii', errors='ignore')}"
            )

            try:
                # 2. 清空接收缓冲区并发送请求 | Clear receive buffer and send request
                if self._reader.at_eof():
                    raise ConnectionError(
                        cn="异步串口连接已断开",
                        en="Async serial connection lost"
                    )

                # 清空可能存在的旧数据 | Clear any existing old data
                while True:
                    try:
                        await asyncio.wait_for(self._reader.read(1024), timeout=0.01)
                    except asyncio.TimeoutError:
                        break

                self._writer.write(ascii_frame)
                await self._writer.drain()

                # 3. 接收响应 | Receive response
                function_code = pdu[0] if pdu else 0
                response_pdu = await self._receive_response(slave_id, function_code)

                self._logger.debug(
                    cn=f"接收到异步ASCII响应PDU: {response_pdu.hex()}",
                    en=f"Received async ASCII response PDU: {response_pdu.hex()}"
                )

                return response_pdu

            except asyncio.TimeoutError:
                raise TimeoutError(
                    cn=f"异步ASCII通信超时: {self.timeout}s",
                    en=f"Async ASCII communication timeout: {self.timeout}s"
                )
            except Exception as e:
                if isinstance(e, (ConnectionError, TimeoutError, CRCError, InvalidResponseError)):
                    raise
                raise ConnectionError(
                    cn=f"异步ASCII通信错误: {e}",
                    en=f"Async ASCII communication error: {e}"
                )

    async def _receive_response(self, expected_slave_id: int, function_code: int) -> bytes:
        """
        异步接收并验证响应帧 | Async receive and validate response frame

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
            response_line = await asyncio.wait_for(
                self._reader.readuntil(b'\r\n'), timeout=self.timeout
            )

            # 验证帧格式 | Validate frame format
            if not response_line.startswith(b':'):
                raise InvalidResponseError(
                    cn="ASCII响应帧格式无效：缺少起始冒号",
                    en="Invalid ASCII response frame format: missing start colon"
                )

            if not response_line.endswith(b'\r\n'):
                raise InvalidResponseError(
                    cn="ASCII响应帧格式无效：缺少结束符",
                    en="Invalid ASCII response frame format: missing end markers"
                )

            # 提取十六进制数据部分 | Extract hex data part
            hex_data = response_line[1:-2].decode('ascii')

            if len(hex_data) % 2 != 0:
                raise InvalidResponseError(
                    cn="ASCII响应帧格式无效：十六进制数据长度不是偶数",
                    en="Invalid ASCII response frame format: hex data length is not even"
                )

            # 将十六进制字符串转换为字节 | Convert hex string to bytes
            try:
                response_bytes = bytes.fromhex(hex_data)
            except ValueError as e:
                raise InvalidResponseError(
                    cn=f"ASCII响应帧格式无效：十六进制数据解析失败: {e}",
                    en=f"Invalid ASCII response frame format: hex data parsing failed: {e}"
                )

            if len(response_bytes) < 3:  # 至少需要：地址 + 功能码 + LRC | At least need: address + function code + LRC
                raise InvalidResponseError(
                    cn="ASCII响应帧太短",
                    en="ASCII response frame too short"
                )

            # 分离数据和LRC | Separate data and LRC
            frame_data = response_bytes[:-1]
            received_lrc = response_bytes[-1]

            # 验证LRC | Validate LRC
            expected_lrc = self._calculate_lrc(frame_data)
            if received_lrc != expected_lrc:
                raise CRCError(
                    cn=f"LRC校验失败: 预期 {expected_lrc:02X}, 得到 {received_lrc:02X}",
                    en=f"LRC validation failed: expected {expected_lrc:02X}, got {received_lrc:02X}"
                )

            # 验证从站地址 | Validate slave address
            received_slave_id = frame_data[0]
            if received_slave_id != expected_slave_id:
                raise InvalidResponseError(
                    cn=f"从站地址不匹配: 预期 {expected_slave_id}, 得到 {received_slave_id}",
                    en=f"Slave address mismatch: expected {expected_slave_id}, got {received_slave_id}"
                )

            # 提取PDU | Extract PDU
            response_pdu = frame_data[1:]

            if len(response_pdu) == 0:
                raise InvalidResponseError(
                    cn="响应PDU为空",
                    en="Response PDU is empty"
                )

            received_function_code = response_pdu[0]

            # 检查是否为异常响应 | Check if it's an exception response
            if received_function_code & 0x80:
                if len(response_pdu) != 2:
                    raise InvalidResponseError(
                        cn="异常响应格式无效",
                        en="Invalid exception response format"
                    )
                return response_pdu

            # 验证功能码 | Validate function code
            if received_function_code != function_code:
                raise InvalidResponseError(
                    cn=f"功能码不匹配: 预期 {function_code}, 得到 {received_function_code}",
                    en=f"Function code mismatch: expected {function_code}, got {received_function_code}"
                )

            return response_pdu

        except asyncio.TimeoutError:
            raise TimeoutError(
                cn=f"异步接收ASCII响应超时: {self.timeout}s",
                en=f"Async receive ASCII response timeout: {self.timeout}s"
            )

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
        """返回传输层的字符串表示 | Return string representation of transport layer"""
        status = "Connected" if asyncio.run(self.is_open()) else "Disconnected"
        return (
            f"AsyncAsciiTransport(port='{self.port}', baudrate={self.baudrate}, "
            f"timeout={self.timeout}, status='{status}')"
        )