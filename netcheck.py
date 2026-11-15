# -*- coding: utf-8 -*-
"""
网络出口 IP 自检（用于排查 QQ 开放平台「接口访问源IP不在白名单」11298）

用法：
    python netcheck.py

它会打印：
  1) 直连（不走代理）时对外看到的 IPv4  —— 这才是 botpy 实际使用的出口 IP
  2) 走系统代理时对外看到的 IPv4        —— 若你开了 Clash/V2Ray，这个是代理节点的 IP
  3) Windows 系统代理设置
  4) api.sgroup.qq.com 是否可解析

把第 1) 项填进 q.qq.com → 机器人 → 开发设置 → IP白名单 即可。
"""
import json
import socket
import urllib.request

# 纯 HTTP 的取 IP 接口：不依赖 TLS，失败概率最低
IP_ENDPOINTS = [
    "http://ip.3322.net",          # 返回纯文本 IPv4
    "http://ip-api.com/line?fields=query",
]


def fetch(opener, url, timeout=8):
    with opener.open(url, timeout=timeout) as r:
        return r.read().decode("utf-8", "replace").strip()


def first_ip(opener):
    for url in IP_ENDPOINTS:
        try:
            text = fetch(opener, url)
            if not text:
                continue
            if text.startswith("{"):
                data = json.loads(text)
                return data.get("query") or data.get("ip") or text
            return text.split()[0]
        except Exception as exc:  # noqa: BLE001 - 逐个接口降级
            last = f"{type(exc).__name__}: {exc}"
    return f"<获取失败 {last}>"


def main():
    print("=" * 56)
    direct = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    print("1) 直连出口 IP (botpy 实际使用的) :", first_ip(direct))

    system = urllib.request.build_opener()  # 默认读取系统/环境变量代理
    print("2) 走代理时的出口 IP            :", first_ip(system))

    print("3) 系统代理设置                  :", end=" ")
    try:
        import winreg

        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Internet Settings",
        )
        enabled = winreg.QueryValueEx(key, "ProxyEnable")[0]
        server = winreg.QueryValueEx(key, "ProxyServer")[0] if enabled else ""
        print(f"{'开启 ' + server if enabled else '关闭'}")
    except OSError as exc:
        print(f"<读取失败 {exc}>")

    print("4) api.sgroup.qq.com             :", end=" ")
    try:
        infos = socket.getaddrinfo("api.sgroup.qq.com", 443, socket.AF_INET)
        print(", ".join(sorted({i[4][0] for i in infos})))
    except OSError as exc:
        print(f"<解析失败 {exc}>")
    print("=" * 56)
    print("把第 1) 项的 IP 加到 q.qq.com → 机器人 → 开发设置 → IP白名单。")
    print("注意：botpy 走 aiohttp，默认不读 Windows 系统代理，所以填代理 IP 通常无效。")


if __name__ == "__main__":
    main()
