"""ModbusLink CRC16校验工具模块


ModbusLink CRC16 Checksum Utility Module

提供Modbus RTU协议所需的CRC16校验功能。


Provides CRC16 checksum functionality required by Modbus RTU protocol.
"""


class CRC16Modbus:
    """Modbus CRC16校验工具类
    
    
    Modbus CRC16 Checksum Utility Class
    
    实现Modbus RTU协议中使用的CRC16校验算法。
    使用多项式0xA001 (反向0x8005)。
    
    
    Implements the CRC16 checksum algorithm used in Modbus RTU protocol.
    Uses polynomial 0xA001 (reverse of 0x8005).
    """
    
    @staticmethod
    def calculate(data: bytes) -> bytes:
        """计算CRC16校验码
        
        
        Calculate CRC16 Checksum
        
        Args:
            data: 需要计算校验码的数据帧（地址+PDU） | Data frame for checksum calculation (address+PDU)
            
        Returns:
            2字节的CRC校验码 (little-endian bytes)
            
            
            2-byte CRC checksum (little-endian bytes)
            
        Example:
            >>> data = b'\x01\x03\x00\x00\x00\x01'
            >>> crc = CRC16Modbus.calculate(data)
            >>> crc.hex()
            '840a'
        """
        crc = 0xFFFF  # 初始值为0xFFFF | Initial value is 0xFFFF
        
        for byte in data:
            crc ^= byte  # 异或运算 | XOR operation
            for _ in range(8):  # 处理8位 | Process 8 bits
                if crc & 0x0001:  # 检查最低位 | Check lowest bit
                    crc >>= 1  # 右移一位 | Right shift by one bit
                    crc ^= 0xA001  # 异或多项式 | XOR with polynomial
                else:
                    crc >>= 1  # 右移一位 | Right shift by one bit
        
        # 返回little-endian格式的2字节CRC | Return 2-byte CRC in little-endian format
        return crc.to_bytes(2, byteorder='little')
    
    @staticmethod
    def validate(frame_with_crc: bytes) -> bool:
        """验证包含CRC的完整数据帧
        
        
        Validate Complete Data Frame with CRC
        
        Args:
            frame_with_crc: 包含CRC校验码的完整数据帧 | Complete data frame containing CRC checksum
            
        Returns:
            如果CRC校验正确返回True，否则返回False
            
            
            True if CRC verification is correct, False otherwise
            
        Example:
            >>> frame = b'\x01\x03\x00\x00\x00\x01\x84\x0a'
            >>> CRC16Modbus.validate(frame)
            True
        """
        if len(frame_with_crc) < 3:  # 至少需要1字节数据 + 2字节CRC | At least 1 byte data + 2 bytes CRC required
            return False
        
        # 分离数据和CRC | Separate data and CRC
        data = frame_with_crc[:-2]
        received_crc = frame_with_crc[-2:]
        
        # 计算期望的CRC | Calculate expected CRC
        expected_crc = CRC16Modbus.calculate(data)
        
        # 比较CRC | Compare CRC
        return received_crc == expected_crc
    
    @staticmethod
    def crc16_to_int(data: bytes) -> int:
        """计算CRC16校验码并返回整数值
        
        
        Calculate CRC16 Checksum and Return Integer Value
        
        这是一个兼容性方法，用于与旧代码保持兼容。
        推荐使用calculate()方法。
        
        
        This is a compatibility method for maintaining compatibility with old code.
        It is recommended to use the calculate() method.
        
        Args:
            data: 需要计算校验码的数据 | Data for checksum calculation
            
        Returns:
            CRC校验码的整数值 | Integer value of CRC checksum
        """
        crc_bytes = CRC16Modbus.calculate(data)
        return int.from_bytes(crc_bytes, byteorder='little')