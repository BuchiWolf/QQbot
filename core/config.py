# -*- coding: utf-8 -*-
"""集中配置：凭证统一从 .env 读取，不要硬编码"""
import os

from dotenv import load_dotenv

load_dotenv()

APP_ID = os.getenv("QQ_APP_ID", "")
APP_SECRET = os.getenv("QQ_APP_SECRET", "")
