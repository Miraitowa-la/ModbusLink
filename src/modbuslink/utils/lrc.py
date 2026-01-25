"""
ModbusLink LRC校验工具模块

ModbusLink LRC Checksum Utils Module
"""

from typing import Union


class LRCModbus:
    """
    Modbus LRC校验工具类

    Modbus LRC Check Utils Module
    """

    @staticmethod
    def calculate(data: Union[bytes, bytearray]) -> bytes:
        """
        计算LRC校验码

        Calculate LRC Checksum

        Args:
            data: 需要计算的数据（不包含起始符':'和结束符CRLF） | Data to calculate (excluding start ':' and end CRLF)

        Returns:
            bytes: 1字节的LRC校验码 (0x00 - 0xFF)

            1-byte LRC checksum (0x00 - 0xFF)
        """
        if not data:
            return b'\x00'

        # 1. 累加所有字节 | Sum all bytes
        total = sum(data)

        # 2. 取模 0xFF (保留低8位) | Modulo 0xFF (Keep lower 8 bits)
        total &= 0xFF

        # 3. 取补码 (Two's complement)
        # 方式: (0x100 - total) & 0xFF
        # 或者: ((total ^ 0xFF) + 1) & 0xFF
        lrc = (0x100 - total) & 0xFF

        return bytes([lrc])

    @staticmethod
    def validate(data_with_lrc: Union[bytes, bytearray]) -> bool:
        """
        验证包含LRC的数据

        Validate data with LRC

        Args:
            data_with_lrc: 包含LRC的完整二进制数据 | Complete binary data containing LRC

        Returns:
            bool: 校验是否通过

            Whether verification passed
        """
        if len(data_with_lrc) < 2:
            return False

        # 方法1：重新计算对比
        # Method 1: Recalculate and compare
        # data = data_with_lrc[:-1]
        # received_lrc = data_with_lrc[-1]
        # return LRCModbus.calculate(data) == received_lrc

        # 方法2：利用数学特性（所有字节+LRC 的和，模256应为0）
        # Method 2: Use mathematical property (Sum of all bytes + LRC, modulo 256 should be 0)
        return (sum(data_with_lrc) & 0xFF) == 0
