"""
ModbusLink 日志系统
提供统一的日志配置和管理功能。

Logging System
Provides unified logging configuration and management functionality.
"""

import logging
import sys
from typing import Optional


# 定义语言常量 | Define language constants
class Language:
    CN = "CN"
    EN = "EN"


# 全局语言设置，默认为中文 | Global language settings, default is Chinese
_CURRENT_LANGUAGE = Language.CN


def set_language(lang: str) -> None:
    """
    设置日志语言 | Set log language

    Args:
        lang: Language.CN or Language.EN
    """
    global _CURRENT_LANGUAGE
    _CURRENT_LANGUAGE = lang


class BilingualLogger:
    """
    双语日志适配器
    包装标准Logger，根据当前语言设置选择输出的消息

    Bilingual log adapter
    The packaging standard Logger selects the output messages based on the current language setting.
    """

    def __init__(self, name: str):
        self._logger = logging.getLogger(name)

    def _get_msg(self, cn: str, en: str) -> str:
        return cn if _CURRENT_LANGUAGE == Language.CN else en

    def debug(self, cn: str, en: str, *args, **kwargs):
        msg = self._get_msg(cn, en)
        self._logger.debug(msg, *args, stacklevel=2, **kwargs)

    def info(self, cn: str, en: str, *args, **kwargs):
        msg = self._get_msg(cn, en)
        self._logger.info(msg, *args, stacklevel=2, **kwargs)

    def warning(self, cn: str, en: str, *args, **kwargs):
        msg = self._get_msg(cn, en)
        self._logger.warning(msg, *args, stacklevel=2, **kwargs)

    def error(self, cn: str, en: str, *args, **kwargs):
        msg = self._get_msg(cn, en)
        self._logger.error(msg, *args, stacklevel=2, **kwargs)

    def critical(self, cn: str, en: str, *args, **kwargs):
        msg = self._get_msg(cn, en)
        self._logger.critical(msg, *args, stacklevel=2, **kwargs)

    def setLevel(self, level):
        self._logger.setLevel(level)


class ModbusLogger:
    """
    ModbusLink日志管理器
    提供统一的日志配置和格式化功能。

    ModbusLink Logger Manager
    Provides unified logging configuration and formatting functionality.
    """

    # 默认日志格式 | Default log format
    DEFAULT_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    DEBUG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s"

    @staticmethod
    def setup_logging(
            level: int = logging.INFO,
            format_string: Optional[str] = None,
            enable_debug: bool = False,
            log_file: Optional[str] = None,
            language: str = Language.CN
    ) -> None:
        """
        设置ModbusLink的日志配置 | Setup ModbusLink logging configuration

        Args:
            level: 日志级别，默认INFO | Log level, default INFO
            format_string: 自定义日志格式 | Custom log format
            enable_debug: 是否启用调试模式（显示详细信息） | Enable debug mode (show detailed info)
            log_file: 日志文件路径，如果提供则同时输出到文件 | Log file path, if provided, also output to file
            language: 语言设置 | Language settings (Language.CN or Language.EN)
        """
        # 设置语言 | Set language
        set_language(language)

        # 选择日志格式 | Choose log format
        if format_string is None:
            format_string = (
                ModbusLogger.DEBUG_FORMAT
                if enable_debug
                else ModbusLogger.DEFAULT_FORMAT
            )

        # 创建格式化器 | Create formatter
        formatter = logging.Formatter(format_string)

        # 获取根日志器 | Get root logger
        root_logger = logging.getLogger("modbuslink")
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
            file_handler = logging.FileHandler(log_file, encoding="utf-8")
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)

        # 防止日志传播到根日志器 | Prevent log propagation to root logger
        root_logger.propagate = False

        # 使用标准logger打印初始化消息，因为此时还没有BilingualLogger实例
        init_msg = (
            f"ModbusLink日志系统已初始化 - Level: {logging.getLevelName(level)}"
            if language == Language.CN
            else f"ModbusLink logging system initialized - Level: {logging.getLevelName(level)}"
        )
        root_logger.info(init_msg)

    @staticmethod
    def get_logger(name: str) -> BilingualLogger:
        """
        获取指定名称的日志器 | Get logger with specified name

        Args:
            name: 日志器名称 | Logger name

        Returns:
            配置好的日志器实例 | Configured logger instance
        """
        # 内部使用 modbuslink. 前缀，但对用户隐藏 | Internally, it uses the "modbuslink." prefix, but hides it from the users.
        return BilingualLogger(f"modbuslink.{name}")

    @staticmethod
    def enable_protocol_debug() -> None:
        """
        启用协议级别的调试日志
        显示原始的十六进制数据包，用于调试通信问题。

        Enable protocol-level debug logging
        Shows raw hexadecimal packets for debugging communication issues.
        """
        # 设置传输层日志级别为DEBUG | Set transport layer log level to DEBUG
        logging.getLogger("modbuslink.transport").setLevel(logging.DEBUG)

        # 设置客户端日志级别为DEBUG | Set client layer log level to DEBUG
        logging.getLogger("modbuslink.client").setLevel(logging.DEBUG)

        msg = "协议调试模式已启用" if _CURRENT_LANGUAGE == Language.CN else "Protocol debug mode enabled"
        logging.getLogger("modbuslink").info(msg)

    @staticmethod
    def disable_protocol_debug() -> None:
        """禁用协议级别的调试日志 | Disable protocol-level debug logging"""
        # 恢复传输层日志级别 | Restore transport layer log level
        logging.getLogger("modbuslink.transport").setLevel(logging.INFO)

        # 恢复客户端日志级别 | Restore client layer log level
        logging.getLogger("modbuslink.client").setLevel(logging.INFO)

        msg = "协议调试模式已禁用" if _CURRENT_LANGUAGE == Language.CN else "Protocol debug mode disabled"
        logging.getLogger("modbuslink").info(msg)


def get_logger(name: str) -> BilingualLogger:
    """
    便捷函数：获取ModbusLink日志器 | Convenience function: get ModbusLink logger

    Args:
        name: 日志器名称 | Logger name

    Returns:
        配置好的日志器实例 | Configured logger instance
    """
    return ModbusLogger.get_logger(name)
