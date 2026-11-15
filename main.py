# -*- coding: utf-8 -*-
"""QQ 群聊自用机器人入口
- 基于 QQ 官方开放平台 + qq-botpy SDK (WebSocket 接入，无需公网 IP)
- 凭证从 .env 读取，不要硬编码
"""
import plugins  # noqa: F401  导入即注册全部指令 / 关键词
from core.client import MyClient
from core.config import APP_ID, APP_SECRET

if not APP_ID or not APP_SECRET:
    raise SystemExit("请在 .env 中配置 QQ_APP_ID 和 QQ_APP_SECRET（参考 .env.example）")


def main():
    client = MyClient()
    client.run(appid=APP_ID, secret=APP_SECRET)


if __name__ == "__main__":
    main()
