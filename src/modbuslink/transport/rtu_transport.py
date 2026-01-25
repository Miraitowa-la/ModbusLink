"""
ModbusLink RTU传输层实现

ModbusLink RTU Transport Layer Implementation
"""

import serial
import asyncio
import threading
import serial_asyncio
from typing import Optional
from serial.rs485 import RS485Settings

from .base_transport import SyncBaseTransport, AsyncBaseTransport
from ..utils.crc import CRC16Modbus
from ..common.logging import get_logger
from ..common.language import get_message
from ..common.exceptions import ConnectError, TimeOutError, InvalidReplyError, ModbusException


class SyncRtuTransport(SyncBaseTransport):
    """
    同步RTU传输层实现

    Sync RTU Transport Layer Implementation
    """

    def __init__(
            self,
            port: str,
            baudrate: int = 9600,
            bytesize: int = 8,
            parity: str = "N",
            stopbits: float = 1,
            timeout: float = 1.0,
            rs485_mode: Optional[RS485Settings] = None
    ) -> None:
        """
        初始化同步RTU传输层

        Initialize Sync RTU Transport Layer

        Args:
            port: 串口名称（如 'COM1', '/dev/ttyUSB0'） | Serial port name (e.g. 'COM1', '/dev/ttyUSB0')
            baudrate: 波特率（默认9600） | Baud rate (default 9600)
            bytesize: 数据位（默认8） | Data bits (default 8)
            parity: 校验位（默认无校验） | Parity (default no parity)
            stopbits: 停止位（默认1） | Stop bits (default 1)
            timeout: 超时时间（默认1.0秒） | Timeout time (default 1.0 second)
            rs485_mode: RS485模式（默认None） | RS485 mode (default None)

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
                en="Baud rate must be a positive integer"
            ))

        if not isinstance(timeout, (int, float)) or timeout < 0.0:
            raise ValueError(get_message(
                cn="超时时间必须是正数",
                en="Timeout time must be a positive number"
            ))

        if not isinstance(rs485_mode, (RS485Settings, type(None))):
            raise ValueError(get_message(
                cn="RS485模式必须是RS485Settings类型",
                en="RS485 mode must be RS485Settings type"
            ))

        self.port = port
        self.baudrate = baudrate
        self.bytesize = bytesize
        self.parity = parity
        self.stopbits = stopbits
        self.timeout = timeout
        self.rs485_mode = rs485_mode

        self._serial: Optional[serial.Serial] = None
        self._lock = threading.Lock()
        self._logger = get_logger("transport.sync_rtu")

    def open(self) -> None:
        """
        打开同步RTU传输层

        Open Sync RTU Transport Layer
        """
        try:
            self._serial = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                bytesize=self.bytesize,
                parity=self.parity,
                stopbits=self.stopbits,
                timeout=self.timeout
            )

            if not self.is_open:
                raise ConnectError(
                    cn=f"无法建立RTU连接 ({self.port}@{self.baudrate})",
                    en=f"Unable to established RTU connection ({self.port}:{self.baudrate})"
                )

            self._logger.info(
                cn=f"RTU连接建立成功 ({self.port}@{self.baudrate})",
                en=f"RTU connection established successfully ({self.port}@{self.baudrate})"
            )

            if self.rs485_mode:
                self._serial.rs485_mode = self.rs485_mode

                self._logger.info(
                    cn=f"RTU RS485模式设置成功",
                    en=f"RTU RS485 mode set successfully"
                )

        except serial.SerialException as e:
            raise ConnectError(
                cn=f"RTU连接建立失败: {e}",
                en=f"RTU connection established failed: {e}"
            ) from e

    def close(self) -> None:
        """
        关闭同步RTU传输层

        Close Sync RTU Transport Layer
        """
        if self._serial and self.is_open:
            try:
                self._serial.close()
                self._logger.info(
                    cn=f"RTU连接关闭成功 ({self.port}@{self.baudrate})",
                    en=f"RTU connection closed successfully ({self.port}@{self.baudrate})"
                )
            except serial.SerialException as e:
                self._logger.debug(
                    cn=f"RTU连接关闭失败 (可忽略): {e}",
                    en=f"RTU connection closed failed (ignored): {e}"
                )
            finally:
                self._serial = None

    def is_open(self) -> bool:
        """
        检查同步RTU传输层连接状态

        Check Sync RTU Transport Layer connection status

        Returns:
            如果传输层打开则返回True，否则返回False

            True if the transport layer is open, otherwise False
        """
        return self._serial is not None and self._serial.is_open

    def send_and_receive(self, slave_id: int, pdu: bytes, timeout: Optional[float] = None) -> bytes:
        """
        同步RTU传输层PDU发送和接收数据

        Sync RTU Transport Layer PDU send and receive data

        通信流程 | Communication Process:

        1. 构建ADU（地址 + PDU + CRC） | Build ADU (address + PDU + CRC)
        2. 发送请求 | Send request
        3. 接收响应 | Receive response
        4. 验证ADU | Verify ADU
        5. 返回响应PDU | Return response PDU

        Args:
            slave_id: 从机地址/单元标识符 | Slave address/unit identifier
            pdu: 协议数据单元（功能码 + 数据） | Protocol data unit (function code + data)
            timeout: 超时时间（秒） | Timeout time (seconds)

        Returns:
            响应的PDU部分（功能码 + 数据）

            Response PDU part (function code + data)
        """
        with self._lock:
            if not self.is_open():
                raise ConnectError(
                    cn=f"RTU连接未建立",
                    en=f"RTU connection is not established"
                )

            # 1. 构建ADU（地址 + PDU + CRC） | Build ADU (address + PDU + CRC)
            request_frame = bytes([slave_id]) + pdu
            crc = CRC16Modbus.calculate(request_frame)
            request_adu = request_frame + crc

            # 2. 发送请求 | Send request
            self._logger.debug(
                cn=f"RTU发送数据: {request_adu.hex(' ').upper()}",
                en=f"RTU Send data:    {request_adu.hex(' ').upper()}"
            )

            try:
                self._serial.reset_input_buffer()
                self._serial.write(request_adu)
                self._serial.flush()

                # 3. 接收响应 | Receive response
                response_adu = self._receive_response()

                self._logger.debug(
                    cn=f"RTU接收数据: {response_adu.hex(' ').upper()}",
                    en=f"RTU Receive data: {response_adu.hex(' ').upper()}"
                )

                # 4. 验证ADU | Verify ADU
                # 验证CRC | Validate CRC
                if not CRC16Modbus.validate(response_adu):
                    raise InvalidReplyError(
                        cn="CRC校验失败",
                        en="CRC check failed"
                    )

                # 验证从机地址 | Validate slave address
                if response_adu[0] != slave_id:
                    raise InvalidReplyError(
                        cn=f"从机地址不匹配: 期望 {slave_id}，实际 {response_adu[0]}",
                        en=f"Slave address does not match: expected {slave_id}, actual {response_adu[0]}"
                    )

                # 验证异常响应 | Validate exception response
                response_function_code = response_adu[1]
                if response_function_code & 0x80:  # 异常响应 | Exception response
                    exception_code = response_adu[2] if len(response_adu) > 2 else 0
                    raise ModbusException(exception_code, pdu[0])

                # 5. 返回响应PDU | Return response PDU
                return response_adu[1:-2]  # 去掉地址和CRC | Remove address and CRC


            except serial.SerialTimeoutException:
                raise TimeOutError(
                    cn=f"RTU通信超时: ({self.timeout}秒)",
                    en=f"RTU communication timeout: ({self.timeout} seconds)"
                )
            except serial.SerialException as e:
                raise ConnectError(
                    cn=f"RTU通信错误: {e}",
                    en=f"RTU communication error: {e}"
                ) from e

    def _receive_response(self) -> bytes:
        """
        接收完整的响应帧

        Receive complete response frame

        Returns:
            响应的PDU部分

            PDU part of response

        Raises:
            ConnectError: 连接错误 | Connection error
            TimeOutError: 接收超时错误 | Receive timeout error
        """
        if not self.is_open():
            raise ConnectError(
                cn=f"RTU连接未建立",
                en=f"RTU connection is not established"
            )

        # 读取地址 + 功能码 | Read address + function code
        response = bytes(self._serial.read(2))
        if len(response) < 2:
            raise TimeOutError(
                cn=f"RTU接收数据超时，已接收 {len(response)}/2 字节",
                en=f"RTU receive data timeout, received {len(response)}/2 bytes"
            )

        function_code = response[1]

        # 检查是否为异常响应 | Check if it's an exception response
        if function_code & 0x80:
            # 异常响应格式：地址 + 异常功能码 + 异常码 + CRC | Exception response format: address + exception function code + exception code + CRC
            remaining = bytes(self._serial.read(3))  # 异常码 + CRC | Exception code + CRC
            if len(remaining) < 3:
                raise TimeOutError(
                    cn=f"RTU接收数据超时，已接收 {len(remaining)}/3 字节",
                    en=f"RTU receive data timeout, received {len(remaining)}/3 bytes"
                )
            return response + remaining

        # 正常响应 | Normal response
        # 读取线圈/离散输入/读取保持寄存器/输入寄存器 | Read coils/discrete inputs/holding registers/input registers
        if function_code in [0x01, 0x02, 0x03, 0x04]:
            # 格式：地址 + 功能码 + 字节数 + 数据 + CRC | Format: address + function code + byte count + data + CRC
            byte_count = self._serial.read(1)  # 字节数 | Byte count
            if len(byte_count) < 1:
                raise TimeOutError(
                    cn=f"RTU接收数据超时，已接收 {len(byte_count)}/1 字节",
                    en=f"RTU receive data timeout, received {len(byte_count)}/1 bytes"
                )
            remaining = self._serial.read(byte_count[0] + 2)  # 数据 + CRC | Data + CRC
            if len(remaining) < byte_count[0]:
                raise TimeOutError(
                    cn=f"RTU接收数据超时，已接收 {len(remaining)}/{byte_count[0]} 字节",
                    en=f"RTU receive data timeout, received {len(remaining)}/{byte_count[0]} bytes"
                )
            return response + byte_count + remaining

        # 写单个线圈/寄存器/写多个线圈/寄存器 | Write single coil/register/write multiple coils/registers
        if function_code in [0x05, 0x06, 0x0F, 0x10]:
            # 格式：地址 + 功能码 + 地址 + 值 + CRC | Format: address + function code + address + value + CRC
            remaining = bytes(self._serial.read(6))  # 地址 + 值 + CRC | Address + value + CRC
            if len(remaining) < 6:
                raise TimeOutError(
                    cn=f"RTU接收数据超时，已接收 {len(remaining)}/6 字节",
                    en=f"RTU receive data timeout, received {len(remaining)}/6 bytes"
                )
            return response + remaining

        else:
            # 未知功能码 | Unknown function code
            remaining = bytes(self._serial.read(10))  # 最多再读10字节 | Read at most 10 more bytes
            return response + remaining

    def __repr__(self) -> str:
        """
        返回对象的字符串表示

        Return object's string representation

        Returns:
            对象的字符串表示

            Object's string representation
        """
        return f"<SyncRtuTransport port={self.port} baudrate={self.baudrate} timeout={self.timeout}>"


class AsyncRtuTransport(AsyncBaseTransport):
    """
    异步RTU传输层实现

    Async RTU Transport Layer Implementation
    """

    def __init__(
            self,
            port: str,
            baudrate: int = 9600,
            bytesize: int = 8,
            parity: str = "N",
            stopbits: float = 1,
            timeout: float = 1.0,
            rs485_mode: Optional[RS485Settings] = None
    ) -> None:
        """
        初始化异步RTU传输层

        Initialize Async RTU Transport Layer

        Args:
            port: 串口名称（如 'COM1', '/dev/ttyUSB0'） | Serial port name (e.g. 'COM1', '/dev/ttyUSB0')
            baudrate: 波特率（默认9600） | Baud rate (default 9600)
            bytesize: 数据位（默认8） | Data bits (default 8)
            parity: 校验位（默认无校验） | Parity (default no parity)
            stopbits: 停止位（默认1） | Stop bits (default 1)
            timeout: 超时时间（默认1.0秒） | Timeout time (default 1.0 second)
            rs485_mode: RS485模式（默认None） | RS485 mode (default None)

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
                en="Baud rate must be a positive integer"
            ))

        if not isinstance(timeout, (int, float)) or timeout < 0.0:
            raise ValueError(get_message(
                cn="超时时间必须是正数",
                en="Timeout time must be a positive number"
            ))

        if not isinstance(rs485_mode, (RS485Settings, type(None))):
            raise ValueError(get_message(
                cn="RS485模式必须是RS485Settings类型",
                en="RS485 mode must be RS485Settings type"
            ))

        self.port = port
        self.baudrate = baudrate
        self.bytesize = bytesize
        self.parity = parity
        self.stopbits = stopbits
        self.timeout = timeout
        self.rs485_mode = rs485_mode

        self._reader: Optional[asyncio.StreamReader] = None
        self._writer: Optional[asyncio.StreamWriter] = None
        self._lock = asyncio.Lock()
        self._logger = get_logger("transport.async_rtu")

    async def open(self) -> None:
        """
        打开异步RTU传输层

        Open Async RTU Transport Layer
        """
        try:
            self._reader, self._writer = await serial_asyncio.open_serial_connection(
                url=self.port,
                baudrate=self.baudrate,
                bytesize=self.bytesize,
                parity=self.parity,
                stopbits=self.stopbits,
            )

            if not self.is_open:
                raise ConnectError(
                    cn=f"无法建立RTU连接 ({self.port}@{self.baudrate})",
                    en=f"Unable to established RTU connection ({self.port}:{self.baudrate})"
                )

            self._logger.info(
                cn=f"RTU连接建立成功 ({self.port}@{self.baudrate})",
                en=f"RTU connection established successfully ({self.port}@{self.baudrate})"
            )

            if self.rs485_mode:
                transport = self._writer.transport

                if hasattr(transport, 'serial'):
                    transport.serial.rs485_mode = self.rs485_mode

                    self._logger.info(
                        cn=f"RTU RS485模式设置成功",
                        en=f"RTU RS485 mode set successfully"
                    )
                else:
                    self._logger.warning(
                        cn=f"RTU RS485模式设置失败（无法访问底层串口对象）",
                        en=f"RTU RS485 mode set failed (Unable to access the underlying serial port object)"
                    )

        except serial.SerialException as e:
            raise ConnectError(
                cn=f"RTU连接建立失败: {e}",
                en=f"RTU connection established failed: {e}"
            ) from e

    async def close(self) -> None:
        """
        关闭异步RTU传输层

        Close Async RTU Transport Layer
        """
        if self._writer:
            try:
                self._writer.close()
                await self._writer.wait_closed()
                self._logger.info(
                    cn=f"RTU连接关闭成功 ({self.port}@{self.baudrate})",
                    en=f"RTU connection closed successfully ({self.port}@{self.baudrate})"
                )
            except serial.SerialException as e:
                self._logger.debug(
                    cn=f"RTU连接关闭失败 (可忽略): {e}",
                    en=f"RTU connection closed failed (ignored): {e}"
                )
            finally:
                self._reader = None
                self._writer = None

    def is_open(self) -> bool:
        """
        检查异步RTU传输层连接状态

        Check Async RTU Transport Layer connection status

        Returns:
            如果传输层打开则返回True，否则返回False

            True if the transport layer is open, otherwise False
        """
        return self._reader is not None and self._writer is not None and not self._writer.is_closing()

    async def send_and_receive(self, slave_id: int, pdu: bytes, timeout: Optional[float] = None) -> bytes:
        """
        异步RTU传输层PDU发送和接收数据

        Async RTU Transport Layer PDU send and receive data

        通信流程 | Communication Process:

        1. 构建ADU（地址 + PDU + CRC） | Build ADU (address + PDU + CRC)
        2. 发送请求 | Send request
        3. 接收响应 | Receive response
        4. 验证ADU | Verify ADU
        5. 返回响应PDU | Return response PDU

        Args:
            slave_id: 从机地址/单元标识符 | Slave address/unit identifier
            pdu: 协议数据单元（功能码 + 数据） | Protocol data unit (function code + data)
            timeout: 超时时间（秒） | Timeout time (seconds)

        Returns:
            响应的PDU部分（功能码 + 数据）

            Response PDU part (function code + data)
        """
        async with self._lock:
            if not self.is_open():
                raise ConnectError(
                    cn=f"RTU连接未建立",
                    en=f"RTU connection is not established"
                )

            # 1. 构建ADU（地址 + PDU + CRC） | Build ADU (address + PDU + CRC)
            request_frame = bytes([slave_id]) + pdu
            crc = CRC16Modbus.calculate(request_frame)
            request_adu = request_frame + crc

            # 2. 发送请求 | Send request
            self._logger.debug(
                cn=f"RTU发送数据: {request_adu.hex(' ').upper()}",
                en=f"RTU Send data:    {request_adu.hex(' ').upper()}"
            )

            try:
                # 清空接收缓冲区 | Clear receive buffer
                while True:
                    try:
                        await asyncio.wait_for(self._reader.readexactly(1024), timeout=0.01)
                    except asyncio.TimeoutError:
                        break

                self._writer.write(request_adu)
                await self._writer.drain()

                # 3. 接收响应 | Receive response
                response_adu = await self._receive_response()

                self._logger.debug(
                    cn=f"RTU接收数据: {response_adu.hex(' ').upper()}",
                    en=f"RTU Receive data: {response_adu.hex(' ').upper()}"
                )

                # 4. 验证ADU | Verify ADU
                # 验证CRC | Validate CRC
                if not CRC16Modbus.validate(response_adu):
                    raise InvalidReplyError(
                        cn="CRC校验失败",
                        en="CRC check failed"
                    )

                # 验证从机地址 | Validate slave address
                if response_adu[0] != slave_id:
                    raise InvalidReplyError(
                        cn=f"从机地址不匹配: 期望 {slave_id}，实际 {response_adu[0]}",
                        en=f"Slave address does not match: expected {slave_id}, actual {response_adu[0]}"
                    )

                # 验证异常响应 | Validate exception response
                response_function_code = response_adu[1]
                if response_function_code & 0x80:  # 异常响应 | Exception response
                    exception_code = response_adu[2] if len(response_adu) > 2 else 0
                    raise ModbusException(exception_code, pdu[0])

                # 5. 返回响应PDU | Return response PDU
                return response_adu[1:-2]  # 去掉地址和CRC | Remove address and CRC


            except serial.SerialTimeoutException:
                raise TimeOutError(
                    cn=f"RTU通信超时: ({self.timeout}秒)",
                    en=f"RTU communication timeout: ({self.timeout} seconds)"
                )
            except serial.SerialException as e:
                raise ConnectError(
                    cn=f"RTU通信错误: {e}",
                    en=f"RTU communication error: {e}"
                ) from e

    async def _receive_response(self) -> bytes:
        """
        接收完整的响应帧

        Receive complete response frame

        Returns:
            响应的PDU部分

            PDU part of response

        Raises:
            ConnectError: 连接错误 | Connection error
            TimeOutError: 接收超时错误 | Receive timeout error
        """
        if not self.is_open():
            raise ConnectError(
                cn=f"RTU连接未建立",
                en=f"RTU connection is not established"
            )

        # 读取地址 + 功能码 | Read address + function code
        response = await asyncio.wait_for(
            self._reader.readexactly(2),
            timeout=self.timeout
        )
        if len(response) < 2:
            raise TimeOutError(
                cn=f"RTU接收数据超时，已接收 {len(response)}/2 字节",
                en=f"RTU receive data timeout, received {len(response)}/2 bytes"
            )

        function_code = response[1]

        # 检查是否为异常响应 | Check if it's an exception response
        if function_code & 0x80:
            # 异常响应格式：地址 + 异常功能码 + 异常码 + CRC | Exception response format: address + exception function code + exception code + CRC
            remaining = await asyncio.wait_for(
                self._reader.readexactly(3),
                timeout=self.timeout
            )  # 异常码 + CRC | Exception code + CRC
            if len(remaining) < 3:
                raise TimeOutError(
                    cn=f"RTU接收数据超时，已接收 {len(remaining)}/3 字节",
                    en=f"RTU receive data timeout, received {len(remaining)}/3 bytes"
                )
            return response + remaining

        # 正常响应 | Normal response
        # 读取线圈/离散输入/读取保持寄存器/输入寄存器 | Read coils/discrete inputs/holding registers/input registers
        if function_code in [0x01, 0x02, 0x03, 0x04]:
            # 格式：地址 + 功能码 + 字节数 + 数据 + CRC | Format: address + function code + byte count + data + CRC
            byte_count = await asyncio.wait_for(
                self._reader.readexactly(1),
                timeout=self.timeout
            )  # 字节数 | Byte count
            if len(byte_count) < 1:
                raise TimeOutError(
                    cn=f"RTU接收数据超时，已接收 {len(byte_count)}/1 字节",
                    en=f"RTU receive data timeout, received {len(byte_count)}/1 bytes"
                )
            remaining = await asyncio.wait_for(
                self._reader.readexactly(byte_count[0] + 2),
                timeout=self.timeout
            )  # 数据 + CRC | Data + CRC
            if len(remaining) < byte_count[0]:
                raise TimeOutError(
                    cn=f"RTU接收数据超时，已接收 {len(remaining)}/{byte_count[0]} 字节",
                    en=f"RTU receive data timeout, received {len(remaining)}/{byte_count[0]} bytes"
                )
            return response + byte_count + remaining

        # 写单个线圈/寄存器/写多个线圈/寄存器 | Write single coil/register/write multiple coils/registers
        if function_code in [0x05, 0x06, 0x0F, 0x10]:
            # 格式：地址 + 功能码 + 地址 + 值 + CRC | Format: address + function code + address + value + CRC
            remaining = await asyncio.wait_for(
                self._reader.readexactly(6),
                timeout=self.timeout
            )  # 地址 + 值 + CRC | Address + value + CRC
            if len(remaining) < 6:
                raise TimeOutError(
                    cn=f"RTU接收数据超时，已接收 {len(remaining)}/6 字节",
                    en=f"RTU receive data timeout, received {len(remaining)}/6 bytes"
                )
            return response + remaining

        else:
            # 未知功能码 | Unknown function code
            remaining = await asyncio.wait_for(
                self._reader.readexactly(10),
                timeout=self.timeout
            )  # 最多再读10字节 | Read at most 10 more bytes
            return response + remaining

    def __repr__(self) -> str:
        """
        返回对象的字符串表示

        Return object's string representation

        Returns:
            对象的字符串表示

            Object's string representation
        """
        return f"<AsyncRtuTransport port={self.port} baudrate={self.baudrate} timeout={self.timeout}>"
