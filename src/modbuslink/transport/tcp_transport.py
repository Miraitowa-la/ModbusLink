"""
ModbusLink TCP传输层实现

ModbusLink TCP Transport Layer Implementation
"""

import time
import socket
import struct
import asyncio
import threading
from typing import Optional

from .base_transport import SyncBaseTransport, AsyncBaseTransport
from ..common.logging import get_logger
from ..common.language import get_message
from ..common.exceptions import ConnectError, TimeOutError, InvalidReplyError, ModbusException


class SyncTcpTransport(SyncBaseTransport):
    """
    同步TCP传输层实现

    Sync TCP Transport Layer Implementation
    """

    def __init__(
            self,
            host: str = "127.0.0.1",
            port: int = 502,
            timeout: float = 1.0
    ) -> None:
        """
        初始化同步TCP传输层

        Initialize Sync TCP Transport Layer
        Args:
            host: 目标主机IP地址或域名（默认"127.0.0.1"） | Target host IP address or domain name (default "127.0.0.1")
            port: 目标端口（默认502） | Target port (default 502)
            timeout: 超时时间（默认1.0秒） | Timeout time (default 1.0 second)

        Raises:
            ValueError: 当参数无效时 | When parameters are invalid
        """
        if not host or not isinstance(host, str):
            raise ValueError(get_message(
                cn="主机地址不能为空且必须是字符串",
                en="Host address cannot be empty and must be a string"
            ))

        if not isinstance(port, int) or port < 0 or port > 65535:
            raise ValueError(get_message(
                cn="端口必须是1-65535之间的整数",
                en="Port must be an integer between 1-65535"
            ))

        if not isinstance(timeout, (int, float)) or timeout < 0.0:
            raise ValueError(get_message(
                cn="超时时间必须是正数",
                en="Timeout time must be a positive number"
            ))

        self.host = host
        self.port = port
        self.timeout = timeout

        self._socket: Optional[socket.socket] = None
        self._transaction_id = 0
        self._lock = threading.Lock()
        self._logger = get_logger("transport.sync_tcp")

    def open(self) -> None:
        """
        打开同步TCP传输层

        Open Sync TCP Transport Layer
        """
        try:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)  # 禁用Nagle算法 | Disable Nagle algorithm
            self._socket.settimeout(self.timeout)
            self._socket.connect((self.host, self.port))

            if not self.is_open:
                raise ConnectError(
                    cn=f"无法建立TCP连接 ({self.host}:{self.port})",
                    en=f"Unable to established TCP connection ({self.host}:{self.port})"
                )

            self._logger.info(
                cn=f"TCP连接建立成功 ({self.host}:{self.port})",
                en=f"TCP connection established successfully ({self.host}:{self.port})"
            )

        except socket.error as e:
            raise ConnectError(
                cn=f"TCP连接建立失败: {e}",
                en=f"TCP connection established failed: {e}"
            ) from e

    def close(self) -> None:
        """
        关闭同步TCP传输层

        Close Sync TCP Transport Layer
        """
        if self._socket:
            try:
                self._socket.close()
                self._logger.info(
                    cn=f"TCP连接关闭成功 ({self.host}:{self.port})",
                    en=f"TCP connection closed successfully ({self.host}:{self.port})"
                )
            except socket.error as e:
                self._logger.debug(
                    cn=f"TCP连接关闭失败 (可忽略): {e}",
                    en=f"TCP connection closed failed (ignored): {e}"
                )
            finally:
                self._socket = None

    def is_open(self) -> bool:
        """
        检查同步TCP传输层连接状态

        Check Sync TCP Transport Layer connection status

        Returns:
            如果传输层打开则返回True，否则返回False

            True if the transport layer is open, otherwise False
        """
        if self._socket is None:
            return False

        try:
            self._socket.gettimeout()
            return True
        except socket.error:
            return False

    def send_and_receive(self, slave_id: int, pdu: bytes, timeout: Optional[float] = None) -> bytes:
        """
        同步TCP传输层PDU发送和接收数据

        Sync TCP Transport Layer PDU send and receive data

        通信流程 | Communication Process:

        1. 构建MBAP头 | Build MBAP header
        2. 发送MBAP头和PDU | Send MBAP header and PDU
        3. 接收响应MBAP头 | Receive response MBAP header
        4. 验证MBAP头 | Verify MBAP header
        5. 接收响应PDU | Receive response PDU
        6. 返回响应PDU | Return response PDU

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
                    cn=f"TCP连接未建立",
                    en=f"TCP connection is not established"
                )

            # 1. 构建MBAP头 | Build MBAP header
            # 生成事务ID
            transaction_id = self._transaction_id
            self._transaction_id = (self._transaction_id + 1) % 0x10000  # 16位回绕 | 16-bit wraparound

            # MBAP头格式： | MBAP header format:
            # - Transaction ID (2字节): 事务标识符 | Transaction identifier
            # - Protocol ID (2字节): 协议标识符，固定为0x0000 | Protocol identifier, fixed to 0x0000
            # - Length (2字节): 后续字节长度（Unit ID + PDU） | Length of following bytes (Unit ID + PDU)
            # - Unit ID (1字节): 单元标识符（从站地址） | Unit identifier (slave address)
            mbap_header = struct.pack(
                ">HHHB",
                transaction_id,  # Transaction ID
                0x0000,  # Protocol ID
                len(pdu) + 1,  # Length
                slave_id  # Unit ID
            )

            # 构建完整请求帧 | Build complete request frame
            request_frame = mbap_header + pdu

            # 2. 发送MBAP头和PDU | Send MBAP header and PDU
            self._logger.debug(
                cn=f"TCP发送数据: {request_frame.hex(' ').upper()}",
                en=f"TCP Send data:    {request_frame.hex(' ').upper()}"
            )

            try:
                self._socket.sendall(request_frame)

                # 3. 接收响应MBAP头 | Receive response MBAP header
                response_mbap_header = self._receive_exact(7)

                # 解析响应MBAP头 | Parse response MBAP header
                (
                    response_transaction_id,
                    response_protocol_id,
                    response_length,
                    response_slave_id
                ) = struct.unpack(">HHHB", response_mbap_header)

                # 4. 验证MBAP头 | Verify MBAP header
                if response_transaction_id != transaction_id:
                    raise InvalidReplyError(
                        cn=f"事务ID不匹配: 期望 {transaction_id}，实际 {response_transaction_id}",
                        en=f"Transaction ID does not match: expected {transaction_id}, actual {response_transaction_id}"
                    )

                if response_protocol_id != 0x0000:
                    raise InvalidReplyError(
                        cn=f"协议ID不匹配: 期望 0x0000，实际 {response_protocol_id}",
                        en=f"Protocol ID does not match: expected 0x0000, actual {response_protocol_id}"
                    )

                if response_slave_id != slave_id:
                    raise InvalidReplyError(
                        cn=f"从机地址不匹配: 期望 {slave_id}，实际 {response_slave_id}",
                        en=f"Slave address does not match: expected {slave_id}, actual {response_slave_id}"
                    )

                # 5.接收响应PDU | Receive response PDU
                pdu_length = response_length - 1

                if pdu_length <= 0:
                    raise InvalidReplyError(
                        cn=f"无效的PDU长度: {pdu_length}",
                        en=f"Invalid PDU length: {pdu_length}"
                    )

                response_pdu = self._receive_exact(pdu_length)

                self._logger.debug(
                    cn=f"TCP接收数据: {(response_mbap_header + response_pdu).hex(' ').upper()}",
                    en=f"TCP Receive data: {(response_mbap_header + response_pdu).hex(' ').upper()}"
                )

                response_function_code = response_pdu[0]
                if response_function_code & 0x80:  # 异常响应 | Exception response
                    exception_code = response_pdu[1] if len(response_pdu) >= 2 else 0
                    raise ModbusException(exception_code, pdu[0])

                return response_pdu
            except socket.timeout:
                raise TimeOutError(
                    cn=f"TCP通信超时: ({self.timeout}秒)",
                    en=f"TCP communication timeout: ({self.timeout} seconds)"
                )
            except socket.error as e:
                raise ConnectError(
                    cn=f"TCP通信错误: {e}",
                    en=f"TCP communication error: {e}"
                ) from e

    def _receive_exact(self, length: int) -> bytes:
        """
        接收指定长度的数据

        Receive exact length of data

        Args:
            length: 需要接收的字节数 | Number of bytes to receive

        Returns:
            接收到的数据

            Received data

        Raises:
            ConnectError: 连接错误 | Connection error
            TimeOutError: 接收超时错误 | Receive timeout error
        """
        if not self.is_open():
            raise ConnectError(
                cn=f"TCP连接未建立",
                en=f"TCP connection is not established"
            )

        data = bytearray()
        start_time = time.time()

        while len(data) < length:
            try:
                if time.time() - start_time > self.timeout:
                    raise TimeOutError(
                        cn=f"TCP接收数据超时 ({self.timeout}s)",
                        en=f"TCP receive data timeout ({self.timeout}s)"
                    )

                chunk = self._socket.recv(length - len(data))

                if not chunk:
                    raise ConnectError(
                        cn=f"连接被远程主机关闭，已接收 {len(data)}/{length} 字节",
                        en=f"Connection closed by remote host, received {len(data)}/{length} bytes"
                    )

                data.extend(chunk)
            except socket.timeout:
                raise TimeOutError(
                    cn=f"TCP接收数据超时，已接收 {len(data)}/{length} 字节",
                    en=f"TCP receive data timeout, received {len(data)}/{length} bytes"
                )
            except socket.error as e:
                raise ConnectError(
                    cn=f"TCP接收数据错误: {e}",
                    en=f"TCP receive data error: {e}"
                ) from e

        return data

    def __repr__(self) -> str:
        """
        返回对象的字符串表示

        Return object's string representation

        Returns:
            对象的字符串表示

            Object's string representation
        """
        return f"<SyncTcpTransport host={self.host} port={self.port} timeout={self.timeout}>"


class AsyncTcpTransport(AsyncBaseTransport):
    """
    异步TCP传输层实现

    Async TCP Transport Layer Implementation
    """

    def __init__(
            self,
            host: str = "127.0.0.1",
            port: int = 502,
            timeout: float = 1.0
    ) -> None:
        """
        初始化异步TCP传输层

        Initialize Async TCP Transport Layer
        Args:
            host: 目标主机IP地址或域名（默认"127.0.0.1"） | Target host IP address or domain name (default "127.0.0.1")
            port: 目标端口（默认502） | Target port (default 502)
            timeout: 超时时间（默认1.0秒） | Timeout time (default 1.0 second)

        Raises:
            ValueError: 当参数无效时 | When parameters are invalid
        """
        if not host or not isinstance(host, str):
            raise ValueError(get_message(
                cn="主机地址不能为空且必须是字符串",
                en="Host address cannot be empty and must be a string"
            ))

        if not isinstance(port, int) or port < 0 or port > 65535:
            raise ValueError(get_message(
                cn="端口必须是1-65535之间的整数",
                en="Port must be an integer between 1-65535"
            ))

        if not isinstance(timeout, (int, float)) or timeout < 0.0:
            raise ValueError(get_message(
                cn="超时时间必须是正数",
                en="Timeout time must be a positive number"
            ))

        self.host = host
        self.port = port
        self.timeout = timeout

        self._reader: Optional[asyncio.StreamReader] = None
        self._writer: Optional[asyncio.StreamWriter] = None
        self._transaction_id = 0
        self._lock = asyncio.Lock()
        self._logger = get_logger("transport.async_tcp")

    async def open(self) -> None:
        """
        打开异步TCP传输层

        Open Async TCP Transport Layer
        """
        try:
            self._reader, self._writer = await asyncio.wait_for(
                asyncio.open_connection(self.host, self.port),
                timeout=self.timeout
            )

            # 禁用Nagle算法 | Disable Nagle algorithm
            sock = self._writer.get_extra_info('socket')
            if sock is not None:
                sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

            if not self.is_open:
                raise ConnectError(
                    cn=f"无法建立TCP连接 ({self.host}:{self.port})",
                    en=f"Unable to established TCP connection ({self.host}:{self.port})"
                )

            self._logger.info(
                cn=f"TCP连接建立成功 ({self.host}:{self.port})",
                en=f"TCP connection established successfully ({self.host}:{self.port})"
            )

        except (ConnectionRefusedError, OSError) as e:
            raise ConnectError(
                cn=f"TCP连接建立失败: {e}",
                en=f"TCP connection established failed: {e}"
            ) from e

    async def close(self) -> None:
        """
        关闭异步TCP传输层

        Close Async TCP Transport Layer
        """
        if self._writer:
            try:
                self._writer.close()
                await self._writer.wait_closed()
                self._logger.info(
                    cn=f"TCP连接关闭成功 ({self.host}:{self.port})",
                    en=f"TCP connection closed successfully ({self.host}:{self.port})"
                )
            except (ConnectionRefusedError, OSError) as e:
                self._logger.debug(
                    cn=f"TCP连接关闭失败 (可忽略): {e}",
                    en=f"TCP connection closed failed (ignored): {e}"
                )
            finally:
                self._reader = None
                self._writer = None

    def is_open(self) -> bool:
        """
        检查异步TCP传输层连接状态

        Check Async TCP Transport Layer connection status

        Returns:
            如果传输层打开则返回True，否则返回False

            True if the transport layer is open, otherwise False
        """
        if self._writer is None or self._reader is None:
            return False

        if self._writer.is_closing():
            return False

        transport = self._writer.transport
        if transport is None or transport.is_closing():
            return False

        return True

    async def send_and_receive(self, slave_id: int, pdu: bytes, timeout: Optional[float] = None) -> bytes:
        """
        异步TCP传输层PDU发送和接收数据

        Async TCP Transport Layer PDU send and receive data

        通信流程 | Communication Process:

        1. 构建MBAP头 | Build MBAP header
        2. 发送MBAP头和PDU | Send MBAP header and PDU
        3. 接收响应MBAP头 | Receive response MBAP header
        4. 验证MBAP头 | Verify MBAP header
        5. 接收响应PDU | Receive response PDU
        6. 返回响应PDU | Return response PDU

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
                    cn=f"TCP连接未建立",
                    en=f"TCP connection is not established"
                )

            # 1. 构建MBAP头 | Build MBAP header
            # 生成事务ID
            transaction_id = self._transaction_id
            self._transaction_id = (self._transaction_id + 1) % 0x10000  # 16位回绕 | 16-bit wraparound

            # MBAP头格式： | MBAP header format:
            # - Transaction ID (2字节): 事务标识符 | Transaction identifier
            # - Protocol ID (2字节): 协议标识符，固定为0x0000 | Protocol identifier, fixed to 0x0000
            # - Length (2字节): 后续字节长度（Unit ID + PDU） | Length of following bytes (Unit ID + PDU)
            # - Unit ID (1字节): 单元标识符（从站地址） | Unit identifier (slave address)
            mbap_header = struct.pack(
                ">HHHB",
                transaction_id,  # Transaction ID
                0x0000,  # Protocol ID
                len(pdu) + 1,  # Length
                slave_id  # Unit ID
            )

            # 构建完整请求帧 | Build complete request frame
            request_frame = mbap_header + pdu

            # 2. 发送MBAP头和PDU | Send MBAP header and PDU
            self._logger.debug(
                cn=f"TCP发送数据: {request_frame.hex(' ').upper()}",
                en=f"TCP Send data:    {request_frame.hex(' ').upper()}"
            )

            try:
                self._writer.write(request_frame)
                await asyncio.wait_for(self._writer.drain(), timeout=timeout)

                # 3. 接收响应MBAP头 | Receive response MBAP header
                response_mbap_header = await self._receive_exact(7)

                # 解析响应MBAP头 | Parse response MBAP header
                (
                    response_transaction_id,
                    response_protocol_id,
                    response_length,
                    response_slave_id
                ) = struct.unpack(">HHHB", response_mbap_header)

                # 4. 验证MBAP头 | Verify MBAP header
                if response_transaction_id != transaction_id:
                    raise InvalidReplyError(
                        cn=f"事务ID不匹配: 期望 {transaction_id}，实际 {response_transaction_id}",
                        en=f"Transaction ID does not match: expected {transaction_id}, actual {response_transaction_id}"
                    )

                if response_protocol_id != 0x0000:
                    raise InvalidReplyError(
                        cn=f"协议ID不匹配: 期望 0x0000，实际 {response_protocol_id}",
                        en=f"Protocol ID does not match: expected 0x0000, actual {response_protocol_id}"
                    )

                if response_slave_id != slave_id:
                    raise InvalidReplyError(
                        cn=f"从机地址不匹配: 期望 {slave_id}，实际 {response_slave_id}",
                        en=f"Slave address does not match: expected {slave_id}, actual {response_slave_id}"
                    )

                # 5.接收响应PDU | Receive response PDU
                pdu_length = response_length - 1

                if pdu_length <= 0:
                    raise InvalidReplyError(
                        cn=f"无效的PDU长度: {pdu_length}",
                        en=f"Invalid PDU length: {pdu_length}"
                    )

                response_pdu = await self._receive_exact(pdu_length)

                self._logger.debug(
                    cn=f"TCP接收数据: {(response_mbap_header + response_pdu).hex(' ').upper()}",
                    en=f"TCP Receive data: {(response_mbap_header + response_pdu).hex(' ').upper()}"
                )

                response_function_code = response_pdu[0]
                if response_function_code & 0x80:  # 异常响应 | Exception response
                    exception_code = response_pdu[1] if len(response_pdu) >= 2 else 0
                    raise ModbusException(exception_code, pdu[0])

                return response_pdu
            except asyncio.TimeoutError:
                raise TimeOutError(
                    cn=f"TCP通信超时: ({self.timeout}秒)",
                    en=f"TCP communication timeout: ({self.timeout} seconds)"
                )
            except (ConnectionRefusedError, OSError) as e:
                raise ConnectError(
                    cn=f"TCP通信错误: {e}",
                    en=f"TCP communication error: {e}"
                ) from e

    async def _receive_exact(self, length: int) -> bytes:
        """
        接收指定长度的数据

        Receive exact length of data

        Args:
            length: 需要接收的字节数 | Number of bytes to receive

        Returns:
            接收到的数据

            Received data

        Raises:
            ConnectError: 连接错误 | Connection error
            TimeOutError: 接收超时错误 | Receive timeout error
        """
        if not self.is_open():
            raise ConnectError(
                cn=f"TCP连接未建立",
                en=f"TCP connection is not established"
            )

        data = bytearray()

        try:
            data = await asyncio.wait_for(
                self._reader.readexactly(length),
                timeout=self.timeout
            )
        except asyncio.IncompleteReadError:
            raise ConnectError(
                cn=f"连接被远程主机关闭，已接收 {len(data)}/{length} 字节",
                en=f"Connection closed by remote host, received {len(data)}/{length} bytes"
            )
        except asyncio.TimeoutError:
            raise TimeOutError(
                cn=f"TCP接收数据超时，已接收 {len(data)}/{length} 字节",
                en=f"TCP receive data timeout, received {len(data)}/{length} bytes"
            )
        except (ConnectionRefusedError, OSError) as e:
            raise ConnectError(
                cn=f"TCP接收数据错误: {e}",
                en=f"TCP receive data error: {e}"
            ) from e

        return data

    def __repr__(self) -> str:
        """
        返回对象的字符串表示

        Return object's string representation

        Returns:
            对象的字符串表示

            Object's string representation
        """
        return f"<AsyncTcpTransport host={self.host} port={self.port} timeout={self.timeout}>"
