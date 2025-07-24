"""ModbusLink 日志系统


Logging System

提供统一的日志配置和管理功能。


Provides unified logging configuration and management functionality.
"""

import logging
import sys
from typing import Optional


class ModbusLogger:
    """ModbusLink日志管理器
    
    
    ModbusLink Logger Manager
    
    提供统一的日志配置和格式化功能。
    
    
    Provides unified logging configuration and formatting functionality.
    """
    
    # 默认日志格式 | Default log format
    DEFAULT_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    DEBUG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
    
    @staticmethod
    def setup_logging(
        level: int = logging.INFO,
        format_string: Optional[str] = None,
        enable_debug: bool = False,
        log_file: Optional[str] = None
    ) -> None:
        """设置ModbusLink的日志配置
        
        
        Setup ModbusLink logging configuration
        
        Args:
            level: 日志级别，默认INFO | Log level, default INFO
            format_string: 自定义日志格式 | Custom log format
            enable_debug: 是否启用调试模式（显示详细信息） | Enable debug mode (show detailed info)
            log_file: 日志文件路径，如果提供则同时输出到文件 | Log file path, if provided, also output to file
            
        Example:
            >>> ModbusLogger.setup_logging(level=logging.DEBUG, enable_debug=True)
            >>> ModbusLogger.setup_logging(log_file='modbus.log')
        """
        # 选择日志格式 | Choose log format
        if format_string is None:
            format_string = ModbusLogger.DEBUG_FORMAT if enable_debug else ModbusLogger.DEFAULT_FORMAT
        
        # 创建格式化器 | Create formatter
        formatter = logging.Formatter(format_string)
        
        # 获取根日志器 | Get root logger
        root_logger = logging.getLogger('modbuslink')
        root_logger.setLevel(level)
        
        # 清除现有处理器 | Clear existing handlers
        root_logger.handlers.clear()
        
        # 添加控制台处理器 | Add console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
        
        # 添加文件处理器（如果指定） | Add file handler (if specified)
        if log_file:
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)
        
        # 防止日志传播到根日志器 | Prevent log propagation to root logger
        root_logger.propagate = False
        
        root_logger.info(f"ModbusLink日志系统已初始化 | ModbusLink logging system initialized - Level: {logging.getLevelName(level)}")
    
    @staticmethod
    def get_logger(name: str) -> logging.Logger:
        """获取指定名称的日志器
        
        
        Get logger with specified name
        
        Args:
            name: 日志器名称 | Logger name
            
        Returns:
            配置好的日志器实例 | Configured logger instance
        """
        return logging.getLogger(f'modbuslink.{name}')
    
    @staticmethod
    def enable_protocol_debug() -> None:
        """启用协议级别的调试日志
        
        
        Enable protocol-level debug logging
        
        显示原始的十六进制数据包，用于调试通信问题。
        
        
        Shows raw hexadecimal packets for debugging communication issues.
        """
        # 设置传输层日志级别为DEBUG | Set transport layer log level to DEBUG
        transport_logger = logging.getLogger('modbuslink.transport')
        transport_logger.setLevel(logging.DEBUG)
        
        # 设置客户端日志级别为DEBUG | Set client layer log level to DEBUG
        client_logger = logging.getLogger('modbuslink.client')
        client_logger.setLevel(logging.DEBUG)
        
        logging.getLogger('modbuslink').info("协议调试模式已启用 | Protocol debug mode enabled")
    
    @staticmethod
    def disable_protocol_debug() -> None:
        """禁用协议级别的调试日志
        
        
        Disable protocol-level debug logging"""
        # 恢复传输层日志级别 | Restore transport layer log level
        transport_logger = logging.getLogger('modbuslink.transport')
        transport_logger.setLevel(logging.INFO)
        
        # 恢复客户端日志级别 | Restore client layer log level
        client_logger = logging.getLogger('modbuslink.client')
        client_logger.setLevel(logging.INFO)
        
        logging.getLogger('modbuslink').info("协议调试模式已禁用 | Protocol debug mode disabled")


def get_logger(name: str) -> logging.Logger:
    """便捷函数：获取ModbusLink日志器
    
    
    Convenience function: get ModbusLink logger
    
    Args:
        name: 日志器名称 | Logger name
        
    Returns:
        配置好的日志器实例 | Configured logger instance
        
    Example:
        >>> logger = get_logger('transport.rtu')
        >>> logger.info('RTU连接已建立')
    """
    return ModbusLogger.get_logger(name)