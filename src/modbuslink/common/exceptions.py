"""
ModbusLink 异常定义模块

Exception Definition Module
"""

from .language import get_message


class ModbusLinkError(Exception):
    """
    ModbusLink库的基础异常类

    所有ModbusLink相关的异常都继承自这个基类。

    Base exception class for ModbusLink library

    All ModbusLink-related exceptions inherit from this base class.
    """

    def __init__(self, cn: str = "", en: str = "") -> None:
        self.cn = cn
        self.en = en
        message = get_message(cn=cn, en=en)
        super().__init__(message)

    def __str__(self) -> str:
        return get_message(cn=self.cn, en=self.en)


# =========================================================================
# Level 2: 中间层基类 | Intermediate Base Classes
# =========================================================================

class CommunicationError(ModbusLinkError):
    """
    通信错误基类

    涉及物理连接、网络传输、IO超时等无法完成数据交换的错误。
    用于统一捕获连接中断或超时等网络层面的异常。

    Communication error base class

    Involves physical connection, network transmission, IO timeouts, and other
    errors preventing data exchange. Used to catch connection drops or timeouts
    at the network level.
    """
    pass


class ValidationError(ModbusLinkError):
    """
    数据校验错误基类

    涉及接收到的数据包损坏、校验和(CRC/LRC)不匹配、或帧格式不符合协议规范。
    表示通信物理层正常，但数据内容有问题。

    Data validation error base class

    Involves corrupted received packets, mismatched checksums (CRC/LRC),
    or frame formats not conforming to protocol specifications.
    Indicates the physical layer is working, but data content is invalid.
    """
    pass


# =========================================================================
# Level 3: 具体实现类 | Concrete Implementation Classes
# =========================================================================

# --- Communication Errors ---

class ConnectError(CommunicationError):
    """
    连接错误异常

    当无法建立或维持与Modbus设备的连接时抛出。
    例如：TCP连接被拒绝、串口无法打开、管道断裂。

    Connection error exception

    Raised when unable to establish or maintain connection with Modbus device.
    E.g., TCP connection refused, serial port cannot be opened, broken pipe.
    """
    pass


class TimeOutError(CommunicationError):
    """
    超时错误异常

    当操作超过指定的超时时间时抛出。
    通常意味着发出了请求，但在规定时间内未收到任何字节。

    Timeout error exception

    Raised when operation exceeds the specified timeout period.
    Usually means a request was sent but no bytes were received within the time limit.
    """
    pass


# --- Validation Errors ---

class CrcError(ValidationError):
    """
    CRC校验错误异常

    当接收到的Modbus-RTU数据帧CRC校验失败时抛出。

    CRC validation error exception

    Raised when CRC validation of received Modbus-RTU data frame fails.
    """
    pass


class LrcError(ValidationError):
    """
    LRC校验错误异常

    当接收到的Modbus-ASCII数据帧LRC校验失败时抛出。

    LRC validation error exception

    Raised when LRC validation of received Modbus-ASCII data frame fails.
    """
    pass


class InvalidReplyError(ValidationError):
    """
    无效响应错误异常

    当接收到的响应格式不正确或不符合预期时抛出。
    例如：数据长度不足、协议头错误、接收到的功能码与请求不匹配等。

    Invalid response error exception

    Raised when received response format is incorrect or unexpected.
    E.g., Insufficient data length, wrong protocol header, received function code does not match request, etc.
    """
    pass


# --- Protocol Errors ---

class ModbusException(ModbusLinkError):
    """
    Modbus协议异常

    当从站设备成功接收请求，但由于逻辑原因无法处理时返回的异常帧。
    （即返回了 0x80 + 功能码 的情况）

    Modbus protocol exception

    Raised when slave device successfully receives request but returns an exception
    frame because it cannot process it logically.
    (i.e., returned 0x80 + Function Code)

    Attributes:
        exception_code: Modbus异常码 (如0x01, 0x02等) | Modbus exception code
        function_code: 原始功能码 | Original function code
        custom_message: 自定义消息 | Custom message
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
            self,
            exception_code: int,
            function_code: int,
            message: str = ""
    ) -> None:
        self.exception_code = exception_code
        self.function_code = function_code
        self.custom_message = message

        if self.custom_message:
            super().__init__(cn=self.custom_message, en=self.custom_message)
        else:
            name_cn = self._EXCEPTION_NAMES_CN.get(exception_code, "未知异常")
            name_en = self._EXCEPTION_NAMES_EN.get(exception_code, "Unknown Exception")

            super().__init__(
                cn=f"Modbus异常 (功能码: 0x{self.function_code:02x}, 异常码: 0x{self.exception_code:02X} - {name_cn})",
                en=f"Modbus Exception (Function Code: 0x{self.function_code:02x}, Exception Code: 0x{self.exception_code:02X} - {name_en})"
            )

    def __repr__(self):
        return get_message(
            cn=f"Modbus异常 (功能码: 0x{self.function_code:02x}, 异常码: 0x{self.exception_code:02X})",
            en=f"ModbusException (code=0x{self.exception_code:02X} func=0x{self.function_code:02X})"
        )
