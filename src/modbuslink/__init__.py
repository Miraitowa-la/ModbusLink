"""
ModbusLink - 现代化、功能强大、开发者友好且高度可扩展的Python Modbus库

Modern, powerful, developer-friendly and highly scalable Python Modbus library
"""

__version__ = "0.1.7"
__author__ = "Miraitowa"
__email__ = "2056978412@qq.com"

# 导入主要的公共接口 | Import main public interfaces
from .client.sync_client import ModbusClient
from .client.async_client import AsyncModbusClient
from .transport.rtu import RtuTransport
from .transport.tcp import TcpTransport
from .transport.async_tcp import AsyncTcpTransport
from .transport.async_rtu import AsyncRtuTransport
from .transport.ascii import AsciiTransport
from .transport.async_ascii import AsyncAsciiTransport
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
    "TcpTransport",
    "AsciiTransport",
    "AsyncRtuTransport",
    "AsyncTcpTransport",
    "AsyncAsciiTransport",
    "ModbusLinkError",
    "ConnectionError",
    "TimeoutError",
    "CRCError",
    "InvalidResponseError",
    "ModbusException",
]
