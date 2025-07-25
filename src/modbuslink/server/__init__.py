"""ModbusLink 服务器模块


ModbusLink Server Module

提供Modbus从站模拟器功能。


Provides Modbus slave simulator functionality.
"""

from .slave import ModbusSlave

__all__ = ['ModbusSlave']