"""
ModbusLink 通用模块

ModbusLink Common Module
"""

from .exceptions import (
    ModbusLinkError,
    CommunicationError,
    ValidationError,
    ConnectError,
    TimeOutError,
    CrcError,
    LrcError,
    InvalidReplyError,
    ModbusException
)
from .language import Language, set_language, get_language, use_language, get_message
from .logging import BilingualLogger, ModbusLogger, get_logger

__all__ = [
    "ModbusLinkError",
    "CommunicationError",
    "ValidationError",
    "ConnectError",
    "TimeOutError",
    "CrcError",
    "LrcError",
    "InvalidReplyError",
    "ModbusException",
    "Language",
    "set_language",
    "get_language",
    "use_language",
    "get_message",
    "BilingualLogger",
    "ModbusLogger",
    "get_logger",
]
