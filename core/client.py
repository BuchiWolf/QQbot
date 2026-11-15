# -*- coding: utf-8 -*-
"""QQ 客户端：接收事件，交给 dispatcher 决定回什么"""
import botpy

from core.dispatcher import dispatch


class MyClient(botpy.Client):
    def __init__(self):
        # 只监听群/C2C 公域消息事件，无需公网 IP
        super().__init__(intents=botpy.Intents(public_messages=True))

    async def on_ready(self):
        print("机器人已上线，登录成功！")

    async def on_group_at_message_create(self, message: "botpy.GroupMessage"):
        """群里 @机器人 时触发（沙箱/个人机器人只能收 @ 消息）"""
        content = (message.content or "").strip()
        print(f"[群 {message.group_openid}] {message.author.member_openid}: {content}")

        reply = dispatch(content)
        if reply:
            await message.reply(content=reply)

    async def on_c2c_message_create(self, message: "botpy.C2CMessage"):
        """好友私聊消息触发"""
        reply = dispatch((message.content or "").strip())
        if reply:
            await message.reply(content=reply)
