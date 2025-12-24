"""
ModbusLink 语言配置模块
提供统一的语言设置，供日志和异常等模块使用。

Language Configuration Module
Provides unified language settings for logging, exceptions, and other modules.
"""


class Language:
    """语言常量 | Language constants"""
    CN = "CN"
    EN = "EN"


# 全局语言设置，默认为中文 | Global language settings, default is Chinese
_CURRENT_LANGUAGE = Language.CN


def set_language(lang: str) -> None:
    """
    设置全局语言 | Set global language

    Args:
        lang: Language.CN or Language.EN
    """
    global _CURRENT_LANGUAGE
    if lang not in (Language.CN, Language.EN):
        raise ValueError(f"Invalid language: {lang}. Use Language.CN or Language.EN")
    _CURRENT_LANGUAGE = lang


def get_language() -> str:
    """
    获取当前语言设置 | Get current language setting

    Returns:
        当前语言 | Current language (Language.CN or Language.EN)
    """
    return _CURRENT_LANGUAGE


def get_message(cn: str, en: str) -> str:
    """
    根据当前语言设置获取消息 | Get message based on current language setting

    Args:
        cn: 中文消息 | Chinese message
        en: 英文消息 | English message

    Returns:
        对应语言的消息 | Message in the corresponding language
    """
    return cn if _CURRENT_LANGUAGE == Language.CN else en
