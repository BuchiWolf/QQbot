# -*- coding: utf-8 -*-
"""骰子指令

支持写法（不区分大小写，空格可有可无）：
  1d100        一颗 100 面骰
  d20          省略个数 = 1 颗
  2d6          两颗 6 面骰，分别显示点数
  2d6+3        带固定加值
  1d20+1d6-2   多组骰子混合
  4d6kh3       掷 4 颗取最高 3 颗（DND 属性生成）
  4d6kl2       取最低 2 颗
上限：一次最多 100 颗骰子，单颗 1~10000 面
"""
import random
import re

from core import registry

MAX_DICE = 100
MAX_FACES = 10000

_DICE_TERM_RE = re.compile(r"(\d*)d(\d+)(?:(kh|kl)(\d+))?")
_INT_TERM_RE = re.compile(r"\d+")

DICE_USAGE = "可用写法：1d100 / 2d6 / 2d6+3 / 1d20+1d6-2 / 4d6kh3"
DICE_LIST_LIMIT = 20  # 单组骰子超过这个数量时，结果列表折叠显示


def _fmt_dice(nums: list[int]) -> str:
    if len(nums) <= DICE_LIST_LIMIT:
        return ", ".join(map(str, nums))
    head = ", ".join(map(str, nums[:DICE_LIST_LIMIT]))
    return f"{head}, …共 {len(nums)} 颗"


class DiceError(ValueError):
    """骰子表达式解析失败"""


def parse_dice(expr: str) -> list[dict]:
    """把 '2d6+3' 解析成项列表；写法不对时抛 DiceError。"""
    # 只允许运算符和 d 两侧出现空格，例如 "2 d 6 + 3" 视作 "2d6+3"
    s = re.sub(r"\s*([+\-dD])\s*", r"\1", expr).strip().lower()
    if not s:
        raise DiceError("表达式为空")
    if re.search(r"\s", s):
        raise DiceError("数字之间多了空格（空格只允许出现在 + - d 两侧）")

    terms: list[dict] = []
    i = 0
    sign = 1
    expect_term = True  # 当前位置应该是一个「项」
    dice_total = 0

    while i < len(s):
        ch = s[i]

        if ch in "+-":
            if expect_term and terms:  # 连续运算符，例如 1d6++2
                raise DiceError(f"运算符位置不对：{s[i-1:i+2]}")
            sign = 1 if ch == "+" else -1
            expect_term = True
            i += 1
            if i >= len(s):
                raise DiceError("表达式以运算符结尾")
            continue

        m = _DICE_TERM_RE.match(s, i)
        if m:
            count = int(m.group(1)) if m.group(1) else 1
            faces = int(m.group(2))
            mode = m.group(3)
            keep = int(m.group(4)) if m.group(4) else None

            if count < 1:
                raise DiceError("骰子个数至少 1 颗")
            if not 1 <= faces <= MAX_FACES:
                raise DiceError(f"骰子面数需在 1~{MAX_FACES} 之间")
            if mode and (keep is None or not 1 <= keep <= count):
                raise DiceError(f"{mode} 后面要跟 1~{count} 之间的数字")
            dice_total += count
            if dice_total > MAX_DICE:
                raise DiceError(f"一次最多掷 {MAX_DICE} 颗骰子")

            terms.append(
                {"dice": True, "count": count, "faces": faces, "mode": mode, "keep": keep, "sign": sign}
            )
            i = m.end()
            sign, expect_term = 1, False
            continue

        m = _INT_TERM_RE.match(s, i)
        if m:
            terms.append({"dice": False, "value": int(m.group()), "sign": sign})
            i = m.end()
            sign, expect_term = 1, False
            continue

        raise DiceError(f"看不懂的部分：{s[i:i+10]}")

    if expect_term:
        raise DiceError("表达式不完整")
    return terms


def roll_dice(expr: str) -> str:
    """掷骰并返回一行结果文本。"""
    terms = parse_dice(expr)
    head = re.sub(r"\s+", "", expr).strip()

    total = 0
    pieces: list[str] = []

    for idx, t in enumerate(terms):
        negative = t["sign"] < 0
        if not t["dice"]:
            total += t["sign"] * t["value"]
            detail = str(t["value"])
        else:
            rolls = [random.randint(1, t["faces"]) for _ in range(t["count"])]
            if t["mode"]:
                ordered = sorted(rolls, reverse=(t["mode"] == "kh"))
                kept = ordered[: t["keep"]]
                subtotal = sum(kept)
                detail = f"[{_fmt_dice(rolls)}] {t['mode']}{t['keep']}→[{_fmt_dice(kept)}]"
            else:
                subtotal = sum(rolls)
                detail = f"[{_fmt_dice(rolls)}]"
            total += t["sign"] * subtotal

        if idx == 0:
            pieces.append(("-" if negative else "") + detail)
        else:
            pieces.append(f" {'-' if negative else '+'} {detail}")

    # 单颗 d100 顺带给个 CoC 风味提示
    crit = ""
    if len(terms) == 1:
        t = terms[0]
        if t["dice"] and t["count"] == 1 and t["faces"] == 100:
            crit = {1: " ｜ 大成功！", 100: " ｜ 大失败…"}.get(total, "")

    return f"🎲 {head} · {''.join(pieces)} = {total}{crit}"


@registry.command("roll", "r", "掷骰", help="roll <表达式> - 掷骰子，如 1d100 / 2d6 / 2d6+3 / 4d6kh3")
def roll(args: str) -> str:
    expr = args.strip() or "1d100"
    if expr.isdigit():  # roll 20 老写法 → 1d20
        expr = f"1d{expr}"
    try:
        return roll_dice(expr)
    except DiceError as e:
        return f"骰子表达式看不懂：{e}\n{DICE_USAGE}"
