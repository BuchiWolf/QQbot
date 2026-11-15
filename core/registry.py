# -*- coding: utf-8 -*-
"""指令注册表

功能模块（plugins/ 下）用装饰器把函数登记进来，dispatcher 只负责查表，
互不依赖——新增功能不需要改动框架层。
"""
from typing import Callable

Handler = Callable[[str], "str | None"]

_commands: dict[str, Handler] = {}
_preprocessors: list[Handler] = []
_helps: list[str] = []


def command(*names: str, help: str | None = None):
    """把一个函数注册为指令，names 是全部别名（大小写不敏感）。

    用法：
        @command("roll", "r", "掷骰", help="roll <表达式> - 掷骰子")
        def roll(args: str) -> str | None: ...
    """
    def deco(fn: Handler) -> Handler:
        for name in names:
            _commands[name.lower()] = fn
        if help:
            _helps.append(help)
        return fn
    return deco


def preprocessor(fn: Handler) -> Handler:
    """注册前置匹配器（如关键词自动回复）。

    按注册顺序执行，一旦返回非空就短路，不会再走指令分发。
    """
    _preprocessors.append(fn)
    return fn


def lookup(name: str) -> Handler | None:
    return _commands.get(name.lower())


def run_preprocessors(text: str) -> "str | None":
    for fn in _preprocessors:
        out = fn(text)
        if out:
            return out
    return None


def help_text() -> str:
    lines = ["可用指令：", *_helps, "另外，消息里包含关键词时我会自动回复"]
    return "\n".join(lines)
