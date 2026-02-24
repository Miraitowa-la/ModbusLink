"""
ModbusLink - 现代化、功能强大、开发者友好且高度可扩展的Python Modbus库

ModbusLink - Modern, powerful, developer-friendly and highly scalable Python Modbus library
"""

__version__ = "1.5.1"
__author__ = "Miraitowa-la"
__email__ = "2056978412@qq.com"

# 导入主要的公共接口 | Import main public interfaces
from .server.tcp_server import AsyncTcpModbusServer
from .server.rtu_server import AsyncRtuModbusServer
from .server.ascii_server import AsyncAsciiModbusServer
from .server.data_store import ModbusDataStore

from .client.sync_client import SyncModbusClient
from .client.async_client import AsyncModbusClient

from .transport.rtu_transport import SyncRtuTransport, AsyncRtuTransport
from .transport.ascii_transport import SyncAsciiTransport, AsyncAsciiTransport
from .transport.tcp_transport import SyncTcpTransport, AsyncTcpTransport

from .common.exceptions import (
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
from .common.language import Language, set_language, get_language, use_language, get_message
from .common.logging import BilingualLogger, ModbusLogger, get_logger

from .utils.coder import PayloadCoder
from .utils.crc import CRC16Modbus
from .utils.lrc import LRCModbus

__all__ = [
    # 服务器模块 | Server Module
    "AsyncTcpModbusServer",
    "AsyncRtuModbusServer",
    "AsyncAsciiModbusServer",
    "ModbusDataStore",

    # 客户端模块 | Client Module
    "SyncModbusClient",
    "AsyncModbusClient",

    # 传输层模块 | Transport Layer Module
    "SyncRtuTransport",
    "SyncAsciiTransport",
    "SyncTcpTransport",
    "AsyncRtuTransport",
    "AsyncAsciiTransport",
    "AsyncTcpTransport",

    # 通用模块 | Common Module
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

    # 工具模块 | Utils Module
    "PayloadCoder",
    "CRC16Modbus",
    "LRCModbus",
]
