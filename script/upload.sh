#!/bin/env sh

sh build.sh && cd .. && python3 -m twine upload dist/*