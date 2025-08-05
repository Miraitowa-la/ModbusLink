"""
ModbusLink - 现代化、功能强大、开发者友好且高度可扩展的Python Modbus库

Modern, powerful, developer-friendly and highly scalable Python Modbus library
"""

__version__ = "0.1.9"
__author__ = "Miraitowa"
__email__ = "2056978412@qq.com"

# 导入主要的公共接口 | Import main public interfaces
from .client.sync_client import ModbusClient
from .client.async_client import AsyncModbusClient
from .transport.rtu import RtuTransport
from .transport.ascii import AsciiTransport
from .transport.tcp import TcpTransport
from .transport.async_rtu import AsyncRtuTransport
from .transport.async_ascii import AsyncAsciiTransport
from .transport.async_tcp import AsyncTcpTransport
from .server.data_store import ModbusDataStore
from .server.async_tcp_server import AsyncTcpModbusServer
from .server.async_rtu_server import AsyncRtuModbusServer
from .server.async_ascii_server import AsyncAsciiModbusServer
from .common.exceptions import (
    ModbusLinkError,
    ConnectionError,
    TimeoutError,
    CRCError,
    InvalidResponseError,
    ModbusException,
)

__all__ = [
    "ModbusClient",
    "AsyncModbusClient",
    "RtuTransport",
    "AsciiTransport",
    "TcpTransport",
    "AsyncRtuTransport",
    "AsyncAsciiTransport",
    "AsyncTcpTransport",
    "ModbusDataStore",
    "AsyncTcpModbusServer",
    "AsyncRtuModbusServer",
    "AsyncAsciiModbusServer",
    "ModbusLinkError",
    "ConnectionError",
    "TimeoutError",
    "CRCError",
    "InvalidResponseError",
    "ModbusException",
]
