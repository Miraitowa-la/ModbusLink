"""
ModbusLink 异步传输层抽象基类
定义了所有异步传输层实现必须遵循的统一接口。

ModbusLink Async Transport Layer Abstract Base Class
Defines the unified interface that all async transport layer implementations must follow.
"""

from abc import ABC, abstractmethod
from typing import Optional, Any


class AsyncBaseTransport(ABC):
    """
    异步传输层抽象基类
    所有异步传输层实现（AsyncTCP等）都必须继承此类并实现所有抽象方法。
    这个设计将CRC校验、MBAP头处理等复杂性完全封装在传输层内部，
    为异步客户端提供统一、简洁的接口。

    Async Transport Layer Abstract Base Class
    All async transport layer implementations (AsyncTCP, etc.) must inherit from this class
    and implement all abstract methods. This design completely encapsulates complexities
    such as CRC verification and MBAP header processing within the transport layer,
    providing a unified and concise interface for async clients.
    """

    @abstractmethod
    async def open(self) -> None:
        """
        异步打开传输连接
        异步建立与Modbus设备的连接。对于TCP是建立异步socket连接。

        Async Open Transport Connection
        Asynchronously establishes connection with Modbus device. For TCP, establishes async socket connection.

        Raises:
            ConnectionError: 当无法建立连接时 | When connection cannot be established
        """
        pass

    @abstractmethod
    async def close(self) -> None:
        """
        异步关闭传输连接
        异步关闭与Modbus设备的连接并释放相关资源。

        Async Close Transport Connection
        Asynchronously closes connection with Modbus device and releases related resources.
        """
        pass

    @abstractmethod
    async def is_open(self) -> bool:
        """
        异步检查连接状态

        Async Check Connection Status

        Returns:
            如果连接已建立且可用返回True，否则返回False

            True if connection is established and available, False otherwise
        """
        pass

    @abstractmethod
    async def send_and_receive(self, slave_id: int, pdu: bytes) -> bytes:
        """
        异步发送PDU并接收响应
        这是异步传输层的核心方法。它接收纯净的PDU（协议数据单元），
        负责添加必要的传输层信息（如TCP的MBAP头），
        异步发送请求，接收响应，验证响应的完整性，然后返回响应的PDU部分。


        Async Send PDU and Receive Response

        This is the core method of the async transport layer. It receives pure PDU (Protocol Data Unit),
        is responsible for adding necessary transport layer information (such as TCP MBAP header),
        asynchronously sends requests, receives responses, verifies response integrity,
        and then returns the PDU part of the response.

        Args:
            slave_id: 从站地址/单元标识符 | Slave address/unit identifier
            pdu: 协议数据单元，包含功能码和数据，不包含地址和校验 | Protocol Data Unit, contains function code and data, excludes address and checksum

        Returns:
            响应的PDU部分，已去除传输层信息

            PDU part of response with transport layer information removed

        Raises:
            ConnectionError: 连接错误 | Connection error
            TimeoutError: 操作超时 | Operation timeout
            InvalidResponseError: 响应格式无效 | Invalid response format
        """
        pass

    async def __aenter__(self) -> "AsyncBaseTransport":
        """异步上下文管理器入口 | Async Context Manager Entry"""
        await self.open()
        return self

    async def __aexit__(
        self,
        exc_type: Optional[type],
        exc_val: Optional[BaseException],
        exc_tb: Optional[Any],
    ) -> None:
        """异步上下文管理器出口 | Async Context Manager Exit"""
        await self.close()
