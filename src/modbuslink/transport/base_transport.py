"""
ModbusLink 传输层抽象基类

ModbusLink Transport Layer Abstract Base Class
"""

from abc import ABC, abstractmethod
from typing import Optional, Any


class SyncBaseTransport(ABC):
    """
    同步传输层抽象基类

    所有同步传输层实现（TCP/RTU/ASCII）都必须继承此类并实现所有抽象方法。

    Sync Transport Layer Abstract Base Class

    All sync transport layer implementations (TCP, RTU, ASCII) must inherit from this class and implement all abstract methods.
    """

    @abstractmethod
    def open(self) -> None:
        """
        打开传输连接

        建立与Modbus设备的连接。

        Open Transport Connection

        Establish a connection with the Modbus device.

        Raises:
            ConnectError: 当无法建立连接时 | When connection cannot be established
        """
        pass

    @abstractmethod
    def close(self) -> None:
        """
        关闭传输连接

        关闭与Modbus设备的连接并释放相关资源。

        Close Transport Connection

        Close the connection with the Modbus device and releases related resources.
        """
        pass

    @abstractmethod
    def is_open(self) -> bool:
        """
        检查连接状态

        Check Connection Status

        Returns:
            如果连接已打开则返回True，否则返回False

            True if the connection is open, otherwise False
        """

    @abstractmethod
    def send_and_receive(self, slave_id: int, pdu: bytes,  timeout: Optional[float] = None) -> bytes:
        """
        发送PDU并接收响应

        传输层核心方法。接收纯净的PDU（协议数据单元），
        负责添加必要的传输层信息（TCP的MBAP，RTU的CRC或ASCII的LCR），
        发送请求，接收响应，验证响应的完整性，然后返回回应的PDU部分。

        Send UDP and Receive Response

        Core method of the transport layer. Receive the pure PDU (protocol data unit),
        be responsible for adding necessary transport layer information (MBAP of TCP, CRC of RTU or LCR of ASCII),
        send requests, receive responses, verify the integrity of the responses, and then return the PDU part of the responses.

        Args:
            slave_id: 从机地址/单元标识符 | Slave address/unit identifier
            pdu: 协议数据单元（功能码 + 数据） | Protocol data unit (function code + data)
            timeout: 超时时间（秒） | Timeout time (seconds)

        Returns:
            响应的PDU部分（功能码 + 数据）

            Response PDU part (function code + data)

        Raises:
            CommunicationError: 通信错误
            ValidationError: 数据校验错误
            ConnectError: 连接错误
            TimeOutError: 超时错误
            CrcError: CRC校验错误
            LrcError: LRC校验错误
            InvalidReplyError: 无效响应错误
            ModbusException: Modbus协议异常
        """
        pass

    def __enter__(self) -> "SyncBaseTransport":
        """
        上下文管理器入口

        Context Manager Entry

        Returns:
            当前对象

            Current object
        """
        self.open()
        return self

    def __exit__(
            self,
            exc_type: Optional[type],
            exc_val: Optional[BaseException],
            exc_tb: Optional[Any],
    ) -> None:
        """
        上下文管理器出口

        Context Manager Exit

        Args:
            exc_type: 异常类型 | Exception type
            exc_val: 异常值 | Exception value
            exc_tb: 异常 traceback | Exception traceback
        """
        self.close()


class AsyncBaseTransport(ABC):
    """
    异步传输层抽象基类

    所有异步步传输层实现（TCP/RTU/ASCII）都必须继承此类并实现所有抽象方法。

    Async Transport Layer Abstract Base Class

    All async transport layer implementations (TCP, RTU, ASCII) must inherit from this class and implement all abstract methods.
    """

    @abstractmethod
    async def open(self) -> None:
        """
        异步打开传输连接

        异步建立与Modbus设备的连接。

        Async Open Transport Connection

        Asynchronously establish a connection with the Modbus device.

        Raises:
            ConnectError: 当无法建立连接时 | When connection cannot be established
        """
        pass

    @abstractmethod
    async def close(self) -> None:
        """
        异步关闭传输连接

        异步关闭与Modbus设备的连接并释放相关资源。

        Async Close Transport Connection

        Asynchronously close the connection with the Modbus device and releases related resources.
        """
        pass

    @abstractmethod
    def is_open(self) -> bool:
        """
        检查连接状态

        Check Connection Status

        Returns:
            如果连接已打开则返回True，否则返回False

            True if the connection is open, otherwise False
        """

    @abstractmethod
    async def send_and_receive(self, slave_id: int, pdu: bytes, timeout: Optional[float] = None) -> bytes:
        """
        异步发送PDU并接收响应

        传输层核心方法。接收纯净的PDU（协议数据单元），
        负责添加必要的传输层信息（TCP的MBAP，RTU的CRC或ASCII的LCR），
        发送请求，接收响应，验证响应的完整性，然后返回回应的PDU部分。

        Async Send UDP and Receive Response

        Core method of the transport layer. Receive the pure PDU (protocol data unit),
        be responsible for adding necessary transport layer information (MBAP of TCP, CRC of RTU or LCR of ASCII),
        send requests, receive responses, verify the integrity of the responses, and then return the PDU part of the responses.

        Args:
            slave_id: 从机地址/单元标识符 | Slave address/unit identifier
            pdu: 协议数据单元（功能码 + 数据） | Protocol data unit (function code + data)
            timeout: 超时时间（秒） | Timeout time (seconds)

        Returns:
            响应的PDU部分（功能码 + 数据）

            Response PDU part (function code + data)

        Raises:
            CommunicationError: 通信错误
            ValidationError: 数据校验错误
            ConnectError: 连接错误
            TimeOutError: 超时错误
            CrcError: CRC校验错误
            LrcError: LRC校验错误
            InvalidReplyError: 无效响应错误
            ModbusException: Modbus协议异常
        """
        pass

    async def __aenter__(self) -> "AsyncBaseTransport":
        """
        异步上下文管理器入口

        Async Context Manager Entry

        Returns:
            当前对象

            Current object
        """
        await self.open()
        return self

    async def __aexit__(
            self,
            exc_type: Optional[type],
            exc_val: Optional[BaseException],
            exc_tb: Optional[Any],
    ) -> None:
        """
        异步上下文管理器出口

        Async Context Manager Exit

        Args:
            exc_type: 异常类型 | Exception type
            exc_val: 异常值 | Exception value
            exc_tb: 异常 traceback | Exception traceback
        """
        await self.close()
