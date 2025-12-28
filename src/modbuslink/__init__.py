"""
ModbusLink - 现代化、功能强大、开发者友好且高度可扩展的Python Modbus库

Modern, powerful, developer-friendly and highly scalable Python Modbus library
"""

__version__ = "1.3.4"
__author__ = "Miraitowa-la"
__email__ = "2056978412@qq.com"

import serial.rs485

# 导入主要的公共接口 | Import main public interfaces
from .server.async_tcp_server import AsyncTcpModbusServer
from .server.async_rtu_server import AsyncRtuModbusServer
from .server.async_ascii_server import AsyncAsciiModbusServer
from .server.data_store import ModbusDataStore

from .client.sync_client import ModbusClient
from .client.async_client import AsyncModbusClient

from .transport.rtu import RtuTransport
from .transport.ascii import AsciiTransport
from .transport.tcp import TcpTransport
from .transport.async_rtu import AsyncRtuTransport
from .transport.async_ascii import AsyncAsciiTransport
from .transport.async_tcp import AsyncTcpTransport

from .common.exceptions import ModbusLinkError, ConnectionError, TimeoutError, CRCError, InvalidResponseError, ModbusException
from .common.language import Language, set_language, get_language, get_message

from .utils.coder import PayloadCoder
from .utils.crc import CRC16Modbus
from .utils.logging import ModbusLogger, get_logger

RS485Settings = serial.rs485.RS485Settings  # Re-export for convenience

__all__ = [
    # 服务器模块 | Server Module
    "AsyncTcpModbusServer",
    "AsyncRtuModbusServer",
    "AsyncAsciiModbusServer",
    "ModbusDataStore",

    # 客户端模块 | Client Module
    "ModbusClient",
    "AsyncModbusClient",

    # 传输层模块 | Transport Layer Module
    "RtuTransport",
    "AsciiTransport",
    "TcpTransport",
    "AsyncRtuTransport",
    "AsyncAsciiTransport",
    "AsyncTcpTransport",

    # 通用模块 | Common Module
    "ModbusLinkError",
    "ConnectionError",
    "TimeoutError",
    "CRCError",
    "InvalidResponseError",
    "ModbusException",

    "Language",
    "set_language",
    "get_language",
    "get_message",

    # 工具模块 | Utils Module
    "PayloadCoder",
    "CRC16Modbus",
    "ModbusLogger",
    "get_logger",

    # 其他模块 | Other Module
    "RS485Settings",
]
