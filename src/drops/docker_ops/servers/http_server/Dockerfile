FROM golang:1.19.2-bullseye
COPY ${PWD}/main.go .
# go 当脚本用
ENTRYPOINT ["go", "run", "main.go"]