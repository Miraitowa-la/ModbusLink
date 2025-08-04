"""
ModbusLink TCP传输层实现
实现基于TCP/IP的Modbus TCP协议传输，包括MBAP头处理。

TCP Transport Layer Implementation
Implements Modbus TCP protocol transport based on TCP/IP, including MBAP header processing.
"""

import socket
import struct
from typing import Optional

from .base import BaseTransport
from ..common.exceptions import ConnectionError, TimeoutError, InvalidResponseError
from ..utils.logging import get_logger


class TcpTransport(BaseTransport):
    """
    Modbus TCP传输层实现
    处理基于TCP/IP的Modbus TCP通信，包括：


    Modbus TCP Transport Layer Implementation
    Handles Modbus TCP communication based on TCP/IP, including:

    - TCP socket连接管理 | TCP socket connection management
    - MBAP头的构建和解析 | MBAP header construction and parsing
    - 事务标识符管理 | Transaction identifier management
    - 错误处理和超时管理 | Error handling and timeout management
    """

    def __init__(self, host: str, port: int = 502, timeout: float = 10.0):
        """
        初始化TCP传输层

        Initialize TCP transport layer

        Args:
            host: 目标主机IP地址或域名 | Target host IP address or domain name
            port: 目标端口，默认502（Modbus TCP标准端口） | Target port, default 502 (Modbus TCP standard port)
            timeout: 超时时间（秒），默认10.0秒 | Timeout in seconds, default 10.0 seconds

        Raises:
            ValueError: 当参数无效时 | When parameters are invalid
            TypeError: 当参数类型错误时 | When parameter types are incorrect
        """
        if not host or not isinstance(host, str):
            raise ValueError(
                "主机地址不能为空且必须是字符串 | Host address cannot be empty and must be a string"
            )
        if not isinstance(port, int) or port <= 0 or port > 65535:
            raise ValueError(
                "端口必须是1-65535之间的整数 | Port must be an integer between 1-65535"
            )
        if not isinstance(timeout, (int, float)) or timeout <= 0:
            raise ValueError("超时时间必须是正数 | Timeout must be a positive number")

        self.host = host
        self.port = port
        self.timeout = timeout

        self._socket: Optional[socket.socket] = None
        self._transaction_id = 0
        self._logger = get_logger("transport.tcp")

    def open(self) -> None:
        """建立TCP连接 | Establish TCP connection"""
        try:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._socket.settimeout(self.timeout)
            self._socket.connect((self.host, self.port))

            self._logger.info(
                f"TCP连接已建立 | TCP connection established: {self.host}:{self.port}"
            )

        except socket.error as e:
            raise ConnectionError(f"TCP连接失败 | TCP connection failed: {e}")

    def close(self) -> None:
        """关闭TCP连接 | Close TCP connection"""
        if self._socket:
            try:
                self._socket.close()
                self._logger.info(
                    f"TCP连接已关闭 | TCP connection closed: {self.host}:{self.port}"
                )
            except socket.error as e:
                self._logger.debug(
                    f"关闭连接时出现错误（可忽略）| Error during connection close (ignorable): {e}"
                )
            finally:
                self._socket = None

    def is_open(self) -> bool:
        """检查TCP连接状态 | Check TCP connection status"""
        if self._socket is None:
            return False

        try:
            # 尝试获取对端地址来检查连接状态 | Try to get peer address to check connection status
            self._socket.getpeername()
            return True
        except socket.error:
            return False

    def send_and_receive(self, slave_id: int, pdu: bytes) -> bytes:
        """
        发送PDU并接收响应
        实现TCP协议的完整通信流程：


        Send PDU and receive response
        Implements complete TCP protocol communication flow:

        1. 构建MBAP头 | Build MBAP header
        2. 发送请求（MBAP头 + PDU） | Send request (MBAP header + PDU)
        3. 接收响应MBAP头 | Receive response MBAP header
        4. 验证MBAP头 | Validate MBAP header
        5. 接收响应PDU | Receive response PDU
        6. 返回响应PDU | Return response PDU
        """
        if not self.is_open():
            raise ConnectionError("TCP连接未建立 | TCP connection not established")

        # 1. 生成事务ID并构建MBAP头 | Generate transaction ID and build MBAP header
        current_transaction_id = self._transaction_id
        self._transaction_id = (
            self._transaction_id + 1
        ) % 0x10000  # 16位回绕 | 16-bit wraparound

        # MBAP头格式： | MBAP header format:
        # - Transaction ID (2字节): 事务标识符 | Transaction identifier
        # - Protocol ID (2字节): 协议标识符，固定为0x0000 | Protocol identifier, fixed to 0x0000
        # - Length (2字节): 后续字节长度（Unit ID + PDU） | Length of following bytes (Unit ID + PDU)
        # - Unit ID (1字节): 单元标识符（从站地址） | Unit identifier (slave address)
        mbap_header = struct.pack(
            ">HHHB",  # 大端序：2个short, 1个short, 1个byte | Big endian: 2 shorts, 1 short, 1 byte
            current_transaction_id,  # Transaction ID
            0x0000,  # Protocol ID
            len(pdu)
            + 1,  # Length (PDU长度 + Unit ID的1字节) | Length (PDU length + 1 byte for Unit ID)
            slave_id,  # Unit ID
        )

        # 2. 构建完整请求帧 | Build complete request frame
        request_frame = mbap_header + pdu

        self._logger.debug(f"TCP发送 | TCP Send: {request_frame.hex(' ').upper()}")

        try:
            # 3. 发送请求 | Send request
            if self._socket is None:
                raise ConnectionError("TCP连接未建立 | TCP connection not established")
            self._socket.sendall(request_frame)

            # 4. 接收响应MBAP头（7字节） | Receive response MBAP header (7 bytes)
            response_mbap = self._receive_exact(7)

            # 5. 解析响应MBAP头 | Parse response MBAP header
            (
                response_transaction_id,
                response_protocol_id,
                response_length,
                response_unit_id,
            ) = struct.unpack(">HHHB", response_mbap)

            # 6. 验证MBAP头 | Validate MBAP header
            if response_transaction_id != current_transaction_id:
                raise InvalidResponseError(
                    f"事务ID不匹配 | Transaction ID mismatch: 期望 | Expected {current_transaction_id}, 收到 | Received {response_transaction_id}"
                )

            if response_protocol_id != 0x0000:
                raise InvalidResponseError(
                    f"协议ID无效 | Invalid Protocol ID: 期望 | Expected 0x0000, 收到 | Received 0x{response_protocol_id:04X}"
                )

            if response_unit_id != slave_id:
                raise InvalidResponseError(
                    f"单元ID不匹配 | Unit ID mismatch: 期望 | Expected {slave_id}, 收到 | Received {response_unit_id}"
                )

            # 7. 接收响应PDU | Receive response PDU
            pdu_length = (
                response_length - 1
            )  # 减去Unit ID的1字节 | Subtract 1 byte for Unit ID
            if pdu_length <= 0:
                raise InvalidResponseError(
                    f"PDU长度无效 | Invalid PDU length: {pdu_length}"
                )

            response_pdu = self._receive_exact(pdu_length)

            self._logger.debug(
                f"TCP接收 | TCP Receive: {(response_mbap + response_pdu).hex(' ').upper()}"
            )

            # 8. 检查是否为异常响应 | Check if it's an exception response
            if (
                len(response_pdu) > 0 and response_pdu[0] & 0x80
            ):  # 异常响应 | Exception response
                from ..common.exceptions import ModbusException

                function_code = (
                    response_pdu[0] & 0x7F
                )  # 去除异常标志位 | Remove exception flag bit
                exception_code = response_pdu[1] if len(response_pdu) > 1 else 0
                raise ModbusException(exception_code, function_code)

            return response_pdu

        except socket.timeout:
            raise TimeoutError(
                f"TCP通信超时 | TCP communication timeout ({self.timeout}秒 | seconds)"
            )
        except socket.error as e:
            raise ConnectionError(f"TCP通信错误 | TCP communication error: {e}")

    def _receive_exact(self, length: int) -> bytes:
        """
        精确接收指定长度的数据

        Receive exact length of data

        Args:
            length: 需要接收的字节数 | Number of bytes to receive

        Returns:
            接收到的数据 | Received data

        Raises:
            TimeoutError: 接收超时 | Receive timeout
            ConnectionError: 连接错误 | Connection error
        """
        data = b""
        while len(data) < length:
            try:
                if self._socket is None:
                    raise ConnectionError(
                        "TCP连接未建立 | TCP connection not established"
                    )
                chunk = self._socket.recv(length - len(data))
                if not chunk:
                    raise ConnectionError(
                        "连接被远程主机关闭 | Connection closed by remote host"
                    )
                data += chunk
            except socket.timeout:
                raise TimeoutError(
                    f"接收数据超时 | Data receive timeout，已接收 | Received {len(data)}/{length} 字节 | bytes"
                )
            except socket.error as e:
                raise ConnectionError(f"接收数据错误 | Data receive error: {e}")

        return data

    def __repr__(self) -> str:
        """字符串表示 | String representation"""
        status = "已连接 | Connected" if self.is_open() else "未连接 | Disconnected"
        return f"TcpTransport({self.host}:{self.port}, {status})"
