#!/usr/bin/env python3

import os
import sys

if len(sys.argv) < 2:
    print("没有输入版本号")
    sys.exit(1)

version = sys.argv[1]
if version[0] != 'v':
    version = 'v' + version

with open('pyproject.toml.template') as fd:
    tm = fd.read().replace("${version}", version)
with open('pyproject.toml', 'w') as fd:
    fd.write(tm)

b = "git add pyproject.toml && git commit -m %s && git push" % version
print(b)
s = os.system(b)
if s != 0:
    raise Exception("cmd run error, code:", s)

os.system("gh release create " + version)
