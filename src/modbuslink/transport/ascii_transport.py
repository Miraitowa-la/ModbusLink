"""
ModbusLink ASCII传输层实现

ModbusLink ASCII Transport Layer Implementation
"""

import serial
import asyncio
import threading
import serial_asyncio
from typing import Optional

from .base_transport import SyncBaseTransport, AsyncBaseTransport
from ..utils.lrc import LRCModbus
from ..common.logging import get_logger
from ..common.language import get_message
from ..common.exceptions import ConnectError, TimeOutError, InvalidReplyError, ModbusException


class SyncAsciiTransport(SyncBaseTransport):
    """
    同步ASCII传输层实现

    Sync ASCII Transport Layer Implementation
    """

    def __init__(
            self,
            port: str,
            baudrate: int = 9600,
            bytesize: int = 7,
            parity: str = "E",
            stopbits: float = 1,
            timeout: float = 1.0
    ) -> None:
        """
        初始化同步ASCII传输层

        Initialize Sync ASCII Transport Layer

        Args:
            port: 串口名称（如 'COM1', '/dev/ttyUSB0'） | Serial port name (e.g. 'COM1', '/dev/ttyUSB0')
            baudrate: 波特率（默认9600） | Baud rate (default 9600)
            bytesize: 数据位（默认7） | Data bits (default 7)
            parity: 校验位（默认偶校验） | Parity (default even parity)
            stopbits: 停止位（默认1） | Stop bits (default 1)
            timeout: 超时时间（默认1.0秒） | Timeout time (default 1.0 second)

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

        self.port = port
        self.baudrate = baudrate
        self.bytesize = bytesize
        self.parity = parity
        self.stopbits = stopbits
        self.timeout = timeout

        self._serial: Optional[serial.Serial] = None
        self._lock = threading.Lock()
        self._logger = get_logger("transport.sync_ascii")

    def open(self) -> None:
        """
        打开同步ASCII传输层

        Open Sync ASCII Transport Layer
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
                    cn=f"无法建立ASCII连接 ({self.port}@{self.baudrate})",
                    en=f"Unable to established ASCII connection ({self.port}:{self.baudrate})"
                )

            self._logger.info(
                cn=f"ASCII连接建立成功 ({self.port}@{self.baudrate})",
                en=f"ASCII connection established successfully ({self.port}@{self.baudrate})"
            )

        except serial.SerialException as e:
            raise ConnectError(
                cn=f"ASCII连接建立失败: {e}",
                en=f"ASCII connection established failed: {e}"
            ) from e

    def close(self) -> None:
        """
        关闭同步ASCII传输层

        Close Sync ASCII Transport Layer
        """
        if self._serial and self.is_open:
            try:
                self._serial.close()
                self._logger.info(
                    cn=f"ASCII连接关闭成功 ({self.port}@{self.baudrate})",
                    en=f"ASCII connection closed successfully ({self.port}@{self.baudrate})"
                )
            except serial.SerialException as e:
                self._logger.debug(
                    cn=f"ASCII连接关闭失败 (可忽略): {e}",
                    en=f"ASCII connection closed failed (ignored): {e}"
                )
            finally:
                self._serial = None

    def is_open(self) -> bool:
        """
        检查同步ASCII传输层连接状态

        Check Sync ASCII Transport Layer connection status

        Returns:
            如果传输层打开则返回True，否则返回False

            True if the transport layer is open, otherwise False
        """
        return self._serial is not None and self._serial.is_open

    def send_and_receive(self, slave_id: int, pdu: bytes, timeout: Optional[float] = None) -> bytes:
        """
        同步ASCII传输层PDU发送和接收数据

        Sync ASCII Transport Layer PDU send and receive data

        通信流程 | Communication Process:

        1. 构建ASCII帧（: + 地址 + PDU + LRC + CR LF） | Build ASCII frame (: + address + PDU + LRC + CR LF)
        2. 发送请求 | Send request
        3. 接收响应 | Receive response
        4. 验证ASCII帧 | Verify ASCII frame
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
                    cn=f"ASCII连接未建立",
                    en=f"ASCII connection is not established"
                )

            # 1. 构建ASCII帧（: + 地址 + PDU + LRC + CR LF） | Build ASCII frame (: + address + PDU + LRC + CR LF)
            request_frame = bytes([slave_id]) + pdu
            crc = LRCModbus.calculate(request_frame)
            request_ascii = b':' + (request_frame + crc).hex().upper().encode('ascii') + b'\r\n'

            # 2. 发送请求 | Send request
            self._logger.debug(
                cn=f"ASCII发送数据: {(request_frame + crc).hex(' ').upper()}",
                en=f"ASCII Send data:    {(request_frame + crc).hex(' ').upper()}"
            )

            try:
                self._serial.reset_input_buffer()
                self._serial.write(request_ascii)
                self._serial.flush()

                # 3. 接收响应 | Receive response
                hex_ascii = self._receive_response()

                # self._logger.debug(
                #     cn=f"ASCII接收数据: {hex_ascii.decode('ascii', errors='ignore')}",
                #     en=f"ASCII Receive data: {hex_ascii.decode('ascii', errors='ignore')}"
                # )

                # 4. 验证ASCII帧 | Verify ASCII frame
                # 验证ASCII帧格式 | Validate ASCII frame format
                if not hex_ascii.startswith(b':'):
                    raise InvalidReplyError(
                        cn="ASCII帧格式错误：缺少起始符号",
                        en="ASCII frame format error: missing start colon"
                    )

                if not hex_ascii.endswith(b'\r\n'):
                    raise InvalidReplyError(
                        cn="ASCII帧格式错误：缺少结束符",
                        en="ASCII frame format error: missing end symbol"
                    )

                # 提取 （地址 + PDU + LRC） | Extract (address + PDU + LRC)
                str_ascii = hex_ascii[1:-2].decode('ascii')

                # 验证ASCII帧长度 | Validate ASCII frame length
                if len(str_ascii) % 2 != 0:
                    raise InvalidReplyError(
                        cn="ASCII帧格式错误：无效的帧长度（应该是偶数）",
                        en="ASCII frame format error: invalid frame length (should be even)"
                    )

                # 十六进制字符串转字节 | Hex string to byte
                try:
                    hex_ascii = bytes.fromhex(str_ascii)
                except ValueError:
                    raise InvalidReplyError(
                        cn="无效的十六进制数据",
                        en="Invalid hexadecimal data"
                    )

                self._logger.debug(
                    cn=f"ASCII接收数据: {hex_ascii.hex(' ').upper()}",
                    en=f"ASCII Receive data: {hex_ascii.hex(' ').upper()}"
                )

                # 检验字节长度 | Validate byte length
                if len(hex_ascii) < 3:  # 至少包含地址+功能码+LRC | At least contain address+function code+LRC
                    raise InvalidReplyError(
                        cn="无效的帧长度（应该大于3）",
                        en="Invalid frame length (should be greater than 3)"
                    )

                # 检验LRC | Validate LRC
                if not LRCModbus.validate(hex_ascii):
                    raise InvalidReplyError(
                        cn="LRC校验失败",
                        en="LRC check failed"
                    )

                # 验证从机地址 | Validate slave address
                if hex_ascii[0] != slave_id:
                    raise InvalidReplyError(
                        cn=f"从机地址不匹配: 期望 {slave_id}，实际 {hex_ascii[0]}",
                        en=f"Slave address does not match: expected {slave_id}, actual {hex_ascii[0]}"
                    )

                # 验证异常响应 | Validate exception response
                response_function_code = hex_ascii[1]
                if response_function_code & 0x80:  # 异常响应 | Exception response
                    exception_code = hex_ascii[2] if len(hex_ascii) > 2 else 0
                    raise ModbusException(exception_code, pdu[0])

                # 5. 返回响应PDU | Return response PDU
                return hex_ascii[1:-1]  # 去掉地址和LRC | Remove address and LRC


            except serial.SerialTimeoutException:
                raise TimeOutError(
                    cn=f"ASCII通信超时: ({self.timeout}秒)",
                    en=f"ASCII communication timeout: ({self.timeout} seconds)"
                )
            except serial.SerialException as e:
                raise ConnectError(
                    cn=f"ASCII通信错误: {e}",
                    en=f"ASCII communication error: {e}"
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
                cn=f"ASCII连接未建立",
                en=f"ASCII connection is not established"
            )

        response = self._serial.read_until(b'\r\n')

        if not response.endswith(b'\r\n'):
            raise TimeOutError(
                cn=f"ASCII接收数据超时 ({self.timeout}s)",
                en=f"ASCII receive data timeout ({self.timeout}s)"
            )

        return response

    def __repr__(self) -> str:
        """
        返回对象的字符串表示

        Return object's string representation

        Returns:
            对象的字符串表示

            Object's string representation
        """
        return f"<SyncAsciiTransport port={self.port} baudrate={self.baudrate} timeout={self.timeout}>"


class AsyncAsciiTransport(AsyncBaseTransport):
    """
    异步ASCII传输层实现

    Async ASCII Transport Layer Implementation
    """

    def __init__(
            self,
            port: str,
            baudrate: int = 9600,
            bytesize: int = 7,
            parity: str = "E",
            stopbits: float = 1,
            timeout: float = 1.0
    ) -> None:
        """
        初始化同步ASCII传输层

        Initialize Sync ASCII Transport Layer

        Args:
            port: 串口名称（如 'COM1', '/dev/ttyUSB0'） | Serial port name (e.g. 'COM1', '/dev/ttyUSB0')
            baudrate: 波特率（默认9600） | Baud rate (default 9600)
            bytesize: 数据位（默认7） | Data bits (default 7)
            parity: 校验位（默认偶校验） | Parity (default even parity)
            stopbits: 停止位（默认1） | Stop bits (default 1)
            timeout: 超时时间（默认1.0秒） | Timeout time (default 1.0 second)

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

        self.port = port
        self.baudrate = baudrate
        self.bytesize = bytesize
        self.parity = parity
        self.stopbits = stopbits
        self.timeout = timeout

        self._reader: Optional[asyncio.StreamReader] = None
        self._writer: Optional[asyncio.StreamWriter] = None
        self._lock = asyncio.Lock()
        self._logger = get_logger("transport.sync_ascii")

    async def open(self) -> None:
        """
        打开异步ASCII传输层

        Open Async ASCII Transport Layer
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
                    cn=f"无法建立ASCII连接 ({self.port}@{self.baudrate})",
                    en=f"Unable to established ASCII connection ({self.port}:{self.baudrate})"
                )

            self._logger.info(
                cn=f"ASCII连接建立成功 ({self.port}@{self.baudrate})",
                en=f"ASCII connection established successfully ({self.port}@{self.baudrate})"
            )

        except serial.SerialException as e:
            raise ConnectError(
                cn=f"ASCII连接建立失败: {e}",
                en=f"ASCII connection established failed: {e}"
            ) from e

    async def close(self) -> None:
        """
        关闭异步ASCII传输层

        Close Async ASCII Transport Layer
        """
        if self._writer:
            try:
                self._writer.close()
                await self._writer.wait_closed()
                self._logger.info(
                    cn=f"ASCII连接关闭成功 ({self.port}@{self.baudrate})",
                    en=f"ASCII connection closed successfully ({self.port}@{self.baudrate})"
                )
            except serial.SerialException as e:
                self._logger.debug(
                    cn=f"ASCII连接关闭失败 (可忽略): {e}",
                    en=f"ASCII connection closed failed (ignored): {e}"
                )
            finally:
                self._reader = None
                self._writer = None

    def is_open(self) -> bool:
        """
        检查异步ASCII传输层连接状态

        Check Async ASCII Transport Layer connection status

        Returns:
            如果传输层打开则返回True，否则返回False

            True if the transport layer is open, otherwise False
        """
        return self._reader is not None and self._writer is not None and not self._writer.is_closing()

    async def send_and_receive(self, slave_id: int, pdu: bytes, timeout: Optional[float] = None) -> bytes:
        """
        异步ASCII传输层PDU发送和接收数据

        Async ASCII Transport Layer PDU send and receive data

        通信流程 | Communication Process:

        1. 构建ASCII帧（: + 地址 + PDU + LRC + CR LF） | Build ASCII frame (: + address + PDU + LRC + CR LF)
        2. 发送请求 | Send request
        3. 接收响应 | Receive response
        4. 验证ASCII帧 | Verify ASCII frame
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
                    cn=f"ASCII连接未建立",
                    en=f"ASCII connection is not established"
                )

            # 1. 构建ASCII帧（: + 地址 + PDU + LRC + CR LF） | Build ASCII frame (: + address + PDU + LRC + CR LF)
            request_frame = bytes([slave_id]) + pdu
            crc = LRCModbus.calculate(request_frame)
            request_ascii = b':' + (request_frame + crc).hex().upper().encode('ascii') + b'\r\n'

            # 2. 发送请求 | Send request
            self._logger.debug(
                cn=f"ASCII发送数据: {(request_frame + crc).hex(' ').upper()}",
                en=f"ASCII Send data:    {(request_frame + crc).hex(' ').upper()}"
            )

            try:
                # 清空接收缓冲区 | Clear receive buffer
                while True:
                    try:
                        await asyncio.wait_for(self._reader.readexactly(1024), timeout=0.01)
                    except asyncio.TimeoutError:
                        break

                self._writer.write(request_ascii)
                await self._writer.drain()

                # 3. 接收响应 | Receive response
                hex_ascii = await self._receive_response()

                # self._logger.debug(
                #     cn=f"ASCII接收数据: {hex_ascii.decode('ascii', errors='ignore')}",
                #     en=f"ASCII Receive data: {hex_ascii.decode('ascii', errors='ignore')}"
                # )

                # 4. 验证ASCII帧 | Verify ASCII frame
                # 验证ASCII帧格式 | Validate ASCII frame format
                if not hex_ascii.startswith(b':'):
                    raise InvalidReplyError(
                        cn="ASCII帧格式错误：缺少起始符号",
                        en="ASCII frame format error: missing start colon"
                    )

                if not hex_ascii.endswith(b'\r\n'):
                    raise InvalidReplyError(
                        cn="ASCII帧格式错误：缺少结束符",
                        en="ASCII frame format error: missing end symbol"
                    )

                # 提取 （地址 + PDU + LRC） | Extract (address + PDU + LRC)
                str_ascii = hex_ascii[1:-2].decode('ascii')

                # 验证ASCII帧长度 | Validate ASCII frame length
                if len(str_ascii) % 2 != 0:
                    raise InvalidReplyError(
                        cn="ASCII帧格式错误：无效的帧长度（应该是偶数）",
                        en="ASCII frame format error: invalid frame length (should be even)"
                    )

                # 十六进制字符串转字节 | Hex string to byte
                try:
                    hex_ascii = bytes.fromhex(str_ascii)
                except ValueError:
                    raise InvalidReplyError(
                        cn="无效的十六进制数据",
                        en="Invalid hexadecimal data"
                    )

                self._logger.debug(
                    cn=f"ASCII接收数据: {hex_ascii.hex(' ').upper()}",
                    en=f"ASCII Receive data: {hex_ascii.hex(' ').upper()}"
                )

                # 检验字节长度 | Validate byte length
                if len(hex_ascii) < 3:  # 至少包含地址+功能码+LRC | At least contain address+function code+LRC
                    raise InvalidReplyError(
                        cn="无效的帧长度（应该大于3）",
                        en="Invalid frame length (should be greater than 3)"
                    )

                # 检验LRC | Validate LRC
                if not LRCModbus.validate(hex_ascii):
                    raise InvalidReplyError(
                        cn="LRC校验失败",
                        en="LRC check failed"
                    )

                # 验证从机地址 | Validate slave address
                if hex_ascii[0] != slave_id:
                    raise InvalidReplyError(
                        cn=f"从机地址不匹配: 期望 {slave_id}，实际 {hex_ascii[0]}",
                        en=f"Slave address does not match: expected {slave_id}, actual {hex_ascii[0]}"
                    )

                # 验证异常响应 | Validate exception response
                response_function_code = hex_ascii[1]
                if response_function_code & 0x80:  # 异常响应 | Exception response
                    exception_code = hex_ascii[2] if len(hex_ascii) > 2 else 0
                    raise ModbusException(exception_code, pdu[0])

                # 5. 返回响应PDU | Return response PDU
                return hex_ascii[1:-1]  # 去掉地址和LRC | Remove address and LRC


            except serial.SerialTimeoutException:
                raise TimeOutError(
                    cn=f"ASCII通信超时: ({self.timeout}秒)",
                    en=f"ASCII communication timeout: ({self.timeout} seconds)"
                )
            except serial.SerialException as e:
                raise ConnectError(
                    cn=f"ASCII通信错误: {e}",
                    en=f"ASCII communication error: {e}"
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
                cn=f"ASCII连接未建立",
                en=f"ASCII connection is not established"
            )

        try:
            response = await asyncio.wait_for(
                self._reader.readuntil(b'\r\n'),
                timeout=self.timeout
            )
        except asyncio.TimeoutError:
            raise TimeOutError(
                cn=f"ASCII接收数据超时 ({self.timeout}s)",
                en=f"ASCII receive data timeout ({self.timeout}s)"
            )

        return response

    def __repr__(self) -> str:
        """
        返回对象的字符串表示

        Return object's string representation

        Returns:
            对象的字符串表示

            Object's string representation
        """
        return f"<AsyncAsciiTransport port={self.port} baudrate={self.baudrate} timeout={self.timeout}>"
