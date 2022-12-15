#!/bin/env sh

# 从打包开始跑一个完整的部署测试
sh build.sh && sh install.sh && python3 test.py