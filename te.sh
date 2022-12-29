#!/bin/env sh

# 集成测试
sh build.sh && sh install.sh && python3 test.py && echo 测试成功