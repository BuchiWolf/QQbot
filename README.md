# QQ 群聊自用机器人

基于 QQ 官方开放平台 + `qq-botpy`（WebSocket 接入，无需公网 IP），部署在本机 Windows。

## 首次配置

1. **开放平台控制台**（q.qq.com）确认：
   - 机器人已开通「群聊」能力（沙箱环境即可）
   - 在「沙箱配置」里把你的测试 QQ 号 / 测试群加进去
2. 复制 `.env.example` 为 `.env`，填入你的 AppID 和 AppSecret：
   ```
   copy .env.example .env
   ```
3. 安装依赖（使用已建好的隔离环境，或自建 venv）：
   ```
   C:\Users\90327\.workbuddy\binaries\python\envs\default\Scripts\pip install -r requirements.txt
   ```

## 运行

```
C:\Users\90327\.workbuddy\binaries\python\envs\default\Scripts\python main.py
```

看到「机器人已上线」后，在沙箱群里 **@机器人 + 指令** 即可，例如：

- `@机器人 help` — 查看指令
- `@机器人 ping` — 存活测试
- `@机器人 roll 2d6` — 掷骰子

## 指令一览

| 指令 | 说明 |
| --- | --- |
| `help` | 帮助 |
| `ping` | 存活测试，回 `pong！我在线。` |
| `echo <内容>` | 原样复述 |
| `roll <表达式>` | 掷骰子，别名 `r` / `掷骰` |
| `随机监管者` | 从 36 个监管者名单里随机抽一个 |
| 关键词 | 消息命中 `KEYWORD_REPLIES` 时自动回复（优先级高于指令） |

### 骰子语法

不区分大小写，空格可有可无（`2 d 6` = `2d6`）：

| 写法 | 含义 |
| --- | --- |
| `roll` | 默认 `1d100` |
| `roll 1d100` / `roll d20` | 1 颗 100 面 / 20 面骰（省略个数即 1 颗） |
| `roll 2d6` | 2 颗 6 面骰，显示每颗点数与总和 |
| `roll 2d6+3` / `roll 1d20-2` | 带固定加值/减值 |
| `roll 1d20+1d6-2` | 多组骰子混合 |
| `roll 4d6kh3` | 4 颗取最高 3 颗（`kh`=keep highest） |
| `roll 4d6kl2` | 4 颗取最低 2 颗（`kl`=keep lowest） |
| `roll 20` | 老写法，等价 `1d20` |

上限：一次最多 100 颗骰子、单颗最多 10000 面；单组超过 20 颗时结果列表自动折叠显示。
单颗 `d100` 掷出 1/100 会附带「大成功 / 大失败」提示。

输出示例：

```
🎲 2d6+3 · [4, 2] + 3 = 9
🎲 4d6kh3 · [2, 6, 4, 1] kh3→[6, 4, 2] = 12
```

## 注意事项

- 沙箱机器人**只能收到 @ 它的消息**，且只在沙箱群/沙箱好友中生效
- 被动回复（reply）必须在收到消息后 **5 分钟内** 发出，且不能主动给非沙箱用户发消息
- `.env` 含 AppSecret，已被 `.gitignore` 排除，**不要提交到仓库**
- 个人开发者机器人有审核流程，正式上线前仅沙箱可用

## 常见报错：接口访问源IP不在白名单（code 11298）

```
botpy.errors.AuthenticationFailedError: 接口访问源IP不在白名单
```

含义：开放平台的 **IP 白名单** 里没有你当前这条网络出口的 IP。
注意「WebSocket 接入无需公网 IP」不等于「不需要 IP 白名单」，白名单是必须配的。

排查步骤：

1. 运行 `python netcheck.py`，记下「直连出口 IP」（botpy 用 aiohttp，默认**不走**系统代理，
   所以要在**第 1 项**里取，而不是代理节点的 IP）。
2. 打开 q.qq.com → 你的机器人 → 开发设置 → **IP 白名单**，把该 IP 加进去并保存。
3. 等 1 分钟左右生效，再 `python main.py`。
4. 家宽 IP 会变，重启光猫/重新拨号后可能要重加；长期方案是换成有固定 IP 的云服务器，
   或者给 bot 进程固定一个出口代理。

## 项目结构

```
main.py              入口：读配置 + 启动 client
core/                框架层，功能多了基本不用改
  config.py          从 .env 读凭证
  client.py          MyClient，接收消息事件
  registry.py        指令注册表（@command / @preprocessor）
  dispatcher.py      先关键词、再指令的分发逻辑
plugins/             功能层：一个功能一个文件，放进来就自动注册
  basic.py           help / ping / echo
  dice.py            骰子
  keywords.py        关键词自动回复
netcheck.py          网络出口 IP 自检脚本
data/                运行期数据（sqlite、状态文件），已被 .gitignore 忽略
```

## 添加新指令

在 `plugins/` 下新建一个 `.py`，用装饰器声明即可，**不用动 `core/` 和 `main.py`**：

```python
from core import registry

@registry.command("now", "时间", help="now - 看当前时间")
def now(args: str) -> str | None:
    import datetime
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
```

- 函数收到的是指令名之后剩下的原始参数文本，返回字符串即回复、返回 `None` 表示不回话
- 多个名字都是别名（大小写不敏感）
- `help=` 那段文字会自动出现在 `help` 输出里
- 需要在新消息刚到时抢先匹配（如关键词），用 `@registry.preprocessor` 代替 `@registry.command`
- 这些指令都是纯函数，方便单独测试
