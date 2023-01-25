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

os.system("gh release create " + version)
