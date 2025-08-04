"""
ModbusLink 异常定义模块
定义了所有ModbusLink库中使用的异常类型。

Exception Definition Module
Defines all exception types used in the ModbusLink library.
"""

from typing import Optional


class ModbusLinkError(Exception):
    """
    ModbusLink库的基础异常类
    所有ModbusLink相关的异常都继承自这个基类。

    Base exception class for ModbusLink library
    All ModbusLink-related exceptions inherit from this base class.
    """

    pass


class ConnectionError(ModbusLinkError):
    """
    连接错误异常
    当无法建立或维持与Modbus设备的连接时抛出。

    Connection error exception
    Raised when unable to establish or maintain connection with Modbus device.
    """

    pass


class TimeoutError(ModbusLinkError):
    """
    超时错误异常
    当操作超过指定的超时时间时抛出。

    Timeout error exception
    Raised when operation exceeds the specified timeout period.
    """

    pass


class CRCError(ModbusLinkError):
    """
    CRC校验错误异常
    当接收到的数据帧CRC校验失败时抛出。

    CRC validation error exception
    Raised when CRC validation of received data frame fails.
    """

    pass


class InvalidResponseError(ModbusLinkError):
    """
    无效响应错误异常
    当接收到的响应格式不正确或不符合预期时抛出。


    Invalid response error exception
    Raised when received response format is incorrect or unexpected.
    """

    pass


class ModbusException(ModbusLinkError):
    """
    Modbus协议异常
    当从站返回Modbus异常码时抛出。

    Modbus protocol exception
    Raised when slave returns Modbus exception code.

    Attributes:
        exception_code: Modbus异常码 (如0x01, 0x02等) | Modbus exception code (e.g. 0x01, 0x02, etc.)
        function_code: 原始功能码 | Original function code
    """

    def __init__(
        self, exception_code: int, function_code: int, message: Optional[str] = None
    ):
        self.exception_code = exception_code
        self.function_code = function_code

        if message is None:
            message = f"Modbus异常 | Modbus Exception: 功能码 | Function Code 0x{function_code:02X}, 异常码 | Exception Code 0x{exception_code:02X}"

        super().__init__(message)

    def __str__(self) -> str:
        exception_names = {
            0x01: "非法功能码 | Illegal Function Code",
            0x02: "非法数据地址 | Illegal Data Address",
            0x03: "非法数据值 | Illegal Data Value",
            0x04: "从站设备故障 | Slave Device Failure",
            0x05: "确认 | Acknowledge",
            0x06: "从站设备忙 | Slave Device Busy",
            0x08: "存储奇偶性差错 | Memory Parity Error",
            0x0A: "不可用网关路径 | Gateway Path Unavailable",
            0x0B: "网关目标设备响应失败 | Gateway Target Device Failed to Respond",
        }

        exception_name = exception_names.get(
            self.exception_code, "未知异常 | Unknown Exception"
        )
        return f"Modbus异常 | Modbus Exception (功能码 | Function Code: 0x{self.function_code:02X}, 异常码 | Exception Code: 0x{self.exception_code:02X} - {exception_name})"
