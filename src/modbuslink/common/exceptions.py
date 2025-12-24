"""
ModbusLink 异常定义模块
定义了所有ModbusLink库中使用的异常类型。

Exception Definition Module
Defines all exception types used in the ModbusLink library.
"""

from typing import Optional
from .language import get_message


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

    def __init__(self, cn: str = "", en: str = ""):
        self.cn = cn
        self.en = en
        super().__init__(get_message(cn, en))

    def __str__(self) -> str:
        return get_message(self.cn, self.en)


class TimeoutError(ModbusLinkError):
    """
    超时错误异常
    当操作超过指定的超时时间时抛出。

    Timeout error exception
    Raised when operation exceeds the specified timeout period.
    """

    def __init__(self, cn: str = "", en: str = ""):
        self.cn = cn
        self.en = en
        super().__init__(get_message(cn, en))

    def __str__(self) -> str:
        return get_message(self.cn, self.en)


class CRCError(ModbusLinkError):
    """
    CRC校验错误异常
    当接收到的数据帧CRC校验失败时抛出。

    CRC validation error exception
    Raised when CRC validation of received data frame fails.
    """

    def __init__(self, cn: str = "", en: str = ""):
        self.cn = cn
        self.en = en
        super().__init__(get_message(cn, en))

    def __str__(self) -> str:
        return get_message(self.cn, self.en)


class InvalidResponseError(ModbusLinkError):
    """
    无效响应错误异常
    当接收到的响应格式不正确或不符合预期时抛出。

    Invalid response error exception
    Raised when received response format is incorrect or unexpected.
    """

    def __init__(self, cn: str = "", en: str = ""):
        self.cn = cn
        self.en = en
        super().__init__(get_message(cn, en))

    def __str__(self) -> str:
        return get_message(self.cn, self.en)


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

    # 异常码名称映射 | Exception code name mapping
    _EXCEPTION_NAMES_CN = {
        0x01: "非法功能码",
        0x02: "非法数据地址",
        0x03: "非法数据值",
        0x04: "从站设备故障",
        0x05: "确认",
        0x06: "从站设备忙",
        0x08: "存储奇偶性差错",
        0x0A: "不可用网关路径",
        0x0B: "网关目标设备响应失败",
    }

    _EXCEPTION_NAMES_EN = {
        0x01: "Illegal Function Code",
        0x02: "Illegal Data Address",
        0x03: "Illegal Data Value",
        0x04: "Slave Device Failure",
        0x05: "Acknowledge",
        0x06: "Slave Device Busy",
        0x08: "Memory Parity Error",
        0x0A: "Gateway Path Unavailable",
        0x0B: "Gateway Target Device Failed to Respond",
    }

    def __init__(
            self, exception_code: int, function_code: int, message: Optional[str] = None
    ):
        self.exception_code = exception_code
        self.function_code = function_code
        self._custom_message = message
        super().__init__(str(self))

    def __str__(self) -> str:
        if self._custom_message:
            return self._custom_message

        exception_name_cn = self._EXCEPTION_NAMES_CN.get(self.exception_code, "未知异常")
        exception_name_en = self._EXCEPTION_NAMES_EN.get(self.exception_code, "Unknown Exception")

        cn_msg = f"Modbus异常 (功能码: 0x{self.function_code:02X}, 异常码: 0x{self.exception_code:02X} - {exception_name_cn})"
        en_msg = f"Modbus Exception (Function Code: 0x{self.function_code:02X}, Exception Code: 0x{self.exception_code:02X} - {exception_name_en})"

        return get_message(cn_msg, en_msg)
