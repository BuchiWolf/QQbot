# -*- coding: utf-8 -*-
"""基础指令：help / ping / echo"""
from core import registry


@registry.command("help", help="help   - 显示本帮助")
def help_cmd(args: str) -> str:
    return registry.help_text()


@registry.command("ping", help="ping   - 测试机器人是否在线")
def ping(args: str) -> str:
    return "pong！我在线。"


@registry.command("echo", help="echo <内容> - 原样复述")
def echo(args: str) -> str:
    return args or "你想让我说什么？"
