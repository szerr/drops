#!/bin/env sh
sh build.sh
cd ..
pip install --upgrade dist/*.whl --force-reinstall