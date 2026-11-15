# -*- coding: utf-8 -*-
"""关键词自动回复

在 KEYWORD_REPLIES 里加一行就是一个新回复：
  - 普通 key：完全匹配，发「在吗」→ 回「在的」
  - "re:开头" 的 key：子串匹配，消息里含有该词就触发
  - 值可以是字符串，也可以是字符串列表（随机选一条）
"""
import random

from core import registry

KEYWORD_REPLIES: dict[str, str | list[str]] = {
    "在吗": ["在的，有什么事？", "我在！"],
    "早": "早上好！新的一天加油~",
    "晚安": "晚安，好梦！",
    "re:天气": "我查不了实时天气，不过记得看窗外 :)",
    "re:谢谢": "不客气！",
}


@registry.preprocessor
def match_keywords(text: str) -> "str | None":
    """按 KEYWORD_REPLIES 匹配：普通 key 完全匹配，re: 开头的 key 子串匹配"""
    lowered = text.lower()
    for key, value in KEYWORD_REPLIES.items():
        hit = (key[3:].lower() in lowered) if key.startswith("re:") else (lowered == key.lower())
        if hit:
            return random.choice(value) if isinstance(value, list) else value
    return None
