"""
ModbusLink 语言配置模块

ModbusLink language configuration module
"""
from enum import Enum
from typing import Union
from contextvars import ContextVar
from contextlib import contextmanager


class Language(str, Enum):
    """
    语言常量

    Language constants
    """
    CN = "CN"
    EN = "EN"


# 全局语言设置，默认为中文 | Global language setting, default is Chinese
_CURRENT_LANGUAGE: ContextVar[Language] = ContextVar("language", default=Language.CN)


def set_language(lang: Union[str, Language]) -> None:
    """
    设置全局语言

    Set global language

    Args:
        lang: Language.CN or Language.EN
    """
    try:
        target = lang if isinstance(lang, Language) else Language(lang)
        _CURRENT_LANGUAGE.set(target)
    except ValueError:
        raise ValueError(get_message(
            cn="语言必须为 Language.CN 或 Language.EN",
            en="Language must be Language.CN or Language.EN."
        ))


def get_language() -> str:
    """
    获取当前语言

    Get current language

    Returns:
        Language.CN or Language.EN
    """
    return _CURRENT_LANGUAGE.get()


@contextmanager
def use_language(lang: Union[str, Language]) -> None:
    """
    临时切换语言的上下文管理器

    Context manager for temporary language switching

    Args:
        lang: Language.CN or Language.EN
    """
    try:
        target_lang = lang if isinstance(lang, Language) else Language(lang)
    except ValueError:
        raise ValueError(get_message(
            cn="语言必须为 Language.CN 或 Language.EN",
            en="Language must be Language.CN or Language.EN."
        ))

    token = _CURRENT_LANGUAGE.set(target_lang)

    try:
        yield
    finally:
        _CURRENT_LANGUAGE.reset(token)


def get_message(cn: str = "", en: str = "") -> str:
    """
    获取当前语言对应的消息

    Get message for current language

    Args:
        cn: 中文消息 | Chinese message
        en: 英文消息 | English message

    Returns:
        当前语言对应的消息

        Message for current language
    """
    return cn if get_language() == Language.CN else en
