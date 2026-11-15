# -*- coding: utf-8 -*-
"""消息分发：先跑前置匹配器（关键词回复），再按指令名查注册表"""
import re

from core import registry


def dispatch(content: str) -> "str | None":
    """把一条消息变成回复文本；没有匹配就返回 None（不回话）。"""
    text = content.strip()
    if not text:
        return None

    # 1) 关键词自动回复（优先级高于指令）
    hit = registry.run_preprocessors(text)
    if hit:
        return hit

    # 2) 指令：去掉斜杠前缀，第一个词是指令名，剩下的原样作为参数
    m = re.match(r"\s*(\S+)\s*(.*)\Z", text.lstrip("/"), re.S)
    if not m:
        return None
    handler = registry.lookup(m.group(1))
    if handler is None:
        return None
    return handler(m.group(2))
