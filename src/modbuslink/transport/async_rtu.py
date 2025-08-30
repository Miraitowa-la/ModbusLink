"""
ModbusLink 异步RTU传输层实现
实现基于asyncio的异步Modbus RTU协议传输，包括CRC16校验。

Async RTU Transport Layer Implementation
Implements async Modbus RTU protocol transport based on asyncio, including CRC16 validation.
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
from ..utils.crc import CRC16Modbus
from ..utils.logging import get_logger


class AsyncRtuTransport(AsyncBaseTransport):
    """
    异步Modbus RTU传输层实现
    处理基于asyncio的异步Modbus RTU通信，包括：

    Async Modbus RTU Transport Layer Implementation
    Handles async Modbus RTU communication based on asyncio, including:

    - 异步串口连接管理 | Async serial port connection management
    - CRC16校验码的计算和验证 | CRC16 checksum calculation and validation
    - ADU（应用数据单元）的构建和解析 | ADU (Application Data Unit) construction and parsing
    - 异步错误处理和超时管理 | Async error handling and timeout management
    """

    def __init__(
            self,
            port: str,
            baudrate: int = 9600,
            bytesize: int = 8,
            parity: str = "N",
            stopbits: float = 1,
            timeout: float = 1.0,
    ):
        """
        初始化异步RTU传输层 | Initialize async RTU transport layer

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

        self._reader: Optional[asyncio.StreamReader] = None
        self._writer: Optional[asyncio.StreamWriter] = None
        self._logger = get_logger("transport.async_rtu")

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
                f"异步RTU连接已建立 | Async RTU connection established: {self.port} @ {self.baudrate}bps"
            )

        except Exception as e:
            raise ConnectionError(f"异步串口连接失败 | Async serial port connection failed: {e}")

    async def close(self) -> None:
        """异步关闭串口连接 | Async close serial port connection"""
        if self._writer:
            try:
                self._writer.close()
                await self._writer.wait_closed()
                self._logger.info(f"异步RTU连接已关闭 | Async RTU connection closed: {self.port}")
            except Exception as e:
                self._logger.debug(
                    f"关闭异步串口连接时出现错误（可忽略）| Error during async serial connection close (ignorable): {e}"
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
        实现异步RTU协议的完整通信流程：

        Async send PDU and receive response
        Implements complete async RTU protocol communication flow:

        1. 构建ADU（地址 + PDU + CRC） | Build ADU (Address + PDU + CRC)
        2. 异步发送请求 | Async send request
        3. 异步接收响应 | Async receive response
        4. 验证CRC | Validate CRC
        5. 返回响应PDU | Return response PDU
        """
        if not await self.is_open():
            raise ConnectionError(
                "异步串口连接未建立 | Async serial port connection not established"
            )

        # 1. 构建请求帧 | Build request frame
        frame_prefix = bytes([slave_id]) + pdu
        crc = CRC16Modbus.calculate(frame_prefix)
        request_adu = frame_prefix + crc

        self._logger.debug(
            f"发送异步RTU请求 | Sending async RTU request: {request_adu.hex()}"
        )

        try:
            # 2. 清空接收缓冲区并发送请求 | Clear receive buffer and send request
            if self._reader.at_eof():
                raise ConnectionError("异步串口连接已断开 | Async serial connection lost")

            # 清空可能存在的旧数据 | Clear any existing old data
            while True:
                try:
                    await asyncio.wait_for(self._reader.read(1024), timeout=0.01)
                except asyncio.TimeoutError:
                    break

            self._writer.write(request_adu)
            await self._writer.drain()

            # 3. 接收响应 | Receive response
            function_code = pdu[0] if pdu else 0
            response_pdu = await self._receive_response(slave_id, function_code)

            self._logger.debug(
                f"接收到异步RTU响应PDU | Received async RTU response PDU: {response_pdu.hex()}"
            )

            return response_pdu

        except asyncio.TimeoutError:
            raise TimeoutError(
                f"异步RTU通信超时 | Async RTU communication timeout: {self.timeout}s"
            )
        except Exception as e:
            if isinstance(e, (ConnectionError, TimeoutError, CRCError, InvalidResponseError)):
                raise
            raise ConnectionError(f"异步RTU通信错误 | Async RTU communication error: {e}")

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
            CRCError: CRC校验失败 | CRC validation failed
            InvalidResponseError: 响应格式无效 | Invalid response format
        """
        try:
            # 接收从站地址 | Receive slave address
            slave_addr_bytes = await asyncio.wait_for(
                self._reader.read(1), timeout=self.timeout
            )
            if len(slave_addr_bytes) != 1:
                raise InvalidResponseError("未接收到从站地址 | No slave address received")

            received_slave_id = slave_addr_bytes[0]
            if received_slave_id != expected_slave_id:
                raise InvalidResponseError(
                    f"从站地址不匹配 | Slave address mismatch: expected {expected_slave_id}, got {received_slave_id}"
                )

            # 接收功能码 | Receive function code
            func_code_bytes = await asyncio.wait_for(
                self._reader.read(1), timeout=self.timeout
            )
            if len(func_code_bytes) != 1:
                raise InvalidResponseError("未接收到功能码 | No function code received")

            received_function_code = func_code_bytes[0]

            # 检查是否为异常响应 | Check if it's an exception response
            if received_function_code & 0x80:
                # 异常响应：功能码 + 异常码 + CRC | Exception response: function code + exception code + CRC
                exception_code_bytes = await asyncio.wait_for(
                    self._reader.read(1), timeout=self.timeout
                )
                if len(exception_code_bytes) != 1:
                    raise InvalidResponseError("未接收到异常码 | No exception code received")

                # 接收CRC | Receive CRC
                crc_bytes = await asyncio.wait_for(
                    self._reader.read(2), timeout=self.timeout
                )
                if len(crc_bytes) != 2:
                    raise InvalidResponseError("CRC数据不完整 | Incomplete CRC data")

                # 验证CRC | Validate CRC
                response_without_crc = slave_addr_bytes + func_code_bytes + exception_code_bytes
                expected_crc = CRC16Modbus.calculate(response_without_crc)
                if crc_bytes != expected_crc:
                    raise CRCError(
                        f"异常响应CRC校验失败 | Exception response CRC validation failed: "
                        f"expected {expected_crc.hex()}, got {crc_bytes.hex()}"
                    )

                # 返回异常响应PDU | Return exception response PDU
                return func_code_bytes + exception_code_bytes

            # 正常响应处理 | Normal response handling
            if received_function_code != function_code:
                raise InvalidResponseError(
                    f"功能码不匹配 | Function code mismatch: expected {function_code}, got {received_function_code}"
                )

            # 根据功能码确定数据长度 | Determine data length based on function code
            if function_code in [0x01, 0x02]:  # 读线圈/离散输入 | Read coils/discrete inputs
                data_length_bytes = await asyncio.wait_for(
                    self._reader.read(1), timeout=self.timeout
                )
                if len(data_length_bytes) != 1:
                    raise InvalidResponseError("未接收到数据长度 | No data length received")
                data_length = data_length_bytes[0]

            elif function_code in [0x03, 0x04]:  # 读保持寄存器/输入寄存器 | Read holding/input registers
                data_length_bytes = await asyncio.wait_for(
                    self._reader.read(1), timeout=self.timeout
                )
                if len(data_length_bytes) != 1:
                    raise InvalidResponseError("未接收到数据长度 | No data length received")
                data_length = data_length_bytes[0]

            elif function_code in [0x05, 0x06]:  # 写单个线圈/寄存器 | Write single coil/register
                data_length = 4  # 地址(2) + 值(2) | Address(2) + Value(2)
                data_length_bytes = b''

            elif function_code in [0x0F, 0x10]:  # 写多个线圈/寄存器 | Write multiple coils/registers
                data_length = 4  # 地址(2) + 数量(2) | Address(2) + Quantity(2)
                data_length_bytes = b''

            else:
                raise InvalidResponseError(f"不支持的功能码 | Unsupported function code: {function_code}")

            # 接收数据部分 | Receive data part
            data_bytes = await asyncio.wait_for(
                self._reader.read(data_length), timeout=self.timeout
            )
            if len(data_bytes) != data_length:
                raise InvalidResponseError(
                    f"数据长度不匹配 | Data length mismatch: expected {data_length}, got {len(data_bytes)}"
                )

            # 接收CRC | Receive CRC
            crc_bytes = await asyncio.wait_for(
                self._reader.read(2), timeout=self.timeout
            )
            if len(crc_bytes) != 2:
                raise InvalidResponseError("CRC数据不完整 | Incomplete CRC data")

            # 验证CRC | Validate CRC
            response_without_crc = slave_addr_bytes + func_code_bytes + data_length_bytes + data_bytes
            expected_crc = CRC16Modbus.calculate(response_without_crc)
            if crc_bytes != expected_crc:
                raise CRCError(
                    f"CRC校验失败 | CRC validation failed: "
                    f"expected {expected_crc.hex()}, got {crc_bytes.hex()}"
                )

            # 返回PDU（功能码 + 数据） | Return PDU (function code + data)
            return func_code_bytes + data_length_bytes + data_bytes

        except asyncio.TimeoutError:
            raise TimeoutError(f"异步接收响应超时 | Async receive response timeout: {self.timeout}s")

    def __repr__(self) -> str:
        """返回传输层的字符串表示 | Return string representation of transport layer"""
        status = "已连接 | Connected" if asyncio.run(self.is_open()) else "未连接 | Disconnected"
        return (
            f"AsyncRtuTransport(port='{self.port}', baudrate={self.baudrate}, "
            f"timeout={self.timeout}, status='{status}')"
        )
