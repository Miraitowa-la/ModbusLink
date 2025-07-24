"""ModbusLink 传输层抽象基类


ModbusLink Transport Layer Abstract Base Class

定义了所有传输层实现必须遵循的统一接口。


Defines the unified interface that all transport layer implementations must follow.
"""

from abc import ABC, abstractmethod


class BaseTransport(ABC):
    """传输层抽象基类
    
    
    Transport Layer Abstract Base Class
    
    所有传输层实现（RTU, TCP等）都必须继承此类并实现所有抽象方法。
    这个设计将CRC校验、MBAP头处理等复杂性完全封装在传输层内部，
    为客户端提供统一、简洁的接口。
    
    
    All transport layer implementations (RTU, TCP, etc.) must inherit from this class
    and implement all abstract methods. This design completely encapsulates complexities
    such as CRC verification and MBAP header processing within the transport layer,
    providing a unified and concise interface for clients.
    """
    
    @abstractmethod
    def open(self) -> None:
        """打开传输连接
        
        
        Open Transport Connection
        
        建立与Modbus设备的连接。对于串口是打开串口，
        对于TCP是建立socket连接。
        
        
        Establishes connection with Modbus device. For serial port, opens the port;
        for TCP, establishes socket connection.
        
        Raises:
            ConnectionError: 当无法建立连接时 | When connection cannot be established
        """
        pass
    
    @abstractmethod
    def close(self) -> None:
        """关闭传输连接
        
        
        Close Transport Connection
        
        关闭与Modbus设备的连接并释放相关资源。
        
        
        Closes connection with Modbus device and releases related resources.
        """
        pass
    
    @abstractmethod
    def is_open(self) -> bool:
        """检查连接状态
        
        
        Check Connection Status
        
        Returns:
            如果连接已建立且可用返回True，否则返回False
            
            
            True if connection is established and available, False otherwise
        """
        pass
    
    @abstractmethod
    def send_and_receive(self, slave_id: int, pdu: bytes) -> bytes:
        """发送PDU并接收响应
        
        
        Send PDU and Receive Response
        
        这是传输层的核心方法。它接收纯净的PDU（协议数据单元），
        负责添加必要的传输层信息（如RTU的地址和CRC，或TCP的MBAP头），
        发送请求，接收响应，验证响应的完整性，然后返回响应的PDU部分。
        
        
        This is the core method of the transport layer. It receives pure PDU (Protocol Data Unit),
        is responsible for adding necessary transport layer information (such as RTU address and CRC,
        or TCP MBAP header), sends requests, receives responses, verifies response integrity,
        and then returns the PDU part of the response.
        
        Args:
            slave_id: 从站地址/单元标识符 | Slave address/unit identifier
            pdu: 协议数据单元，包含功能码和数据，不包含地址和校验 | Protocol Data Unit, contains function code and data, excludes address and checksum
            
        Returns:
            响应的PDU部分，已去除传输层信息
            
            
            PDU part of response with transport layer information removed
            
        Raises:
            ConnectionError: 连接错误 | Connection error
            TimeoutError: 操作超时 | Operation timeout
            CRCError: CRC校验失败（仅RTU） | CRC verification failed (RTU only)
            InvalidResponseError: 响应格式无效 | Invalid response format
        """
        pass
    
    def __enter__(self):
        """上下文管理器入口 | Context Manager Entry"""
        self.open()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口 | Context Manager Exit"""
        self.close()