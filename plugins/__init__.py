# -*- coding: utf-8 -*-
"""功能层：本包下的每个模块都会被自动导入，导入即完成指令注册。

新增功能只需在这里放一个 .py 文件，用 @command / @preprocessor 声明即可，
不需要改动 core/ 或 main.py。
"""
import importlib
import pkgutil

for _finder, _name, _ispkg in pkgutil.iter_modules(__path__):
    importlib.import_module(f"{__name__}.{_name}")
