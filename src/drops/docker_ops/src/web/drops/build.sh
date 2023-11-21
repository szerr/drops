#!/bin/sh
dest="../replase/"

help_str="
参数说明：
  -h, --help:           打印帮助信息
  -d, --dest [path]:    编译输出路径
"
# 解析命令行参数 -o 短选项 -l 长选项。
# 如果某个要解析的选项需要一个参数，则在选项名后面跟一个冒号。
# 如果某个要解析的选项的参数可选，则在选项名后面跟两个冒号。
# 多个短选项可以连在一起，多个长选项要用逗号分割。
getopt_cmd=$(getopt -o d:h -l dest:,help -- "$@")
[ $? -ne 0 ] && exit 1
eval set -- "$getopt_cmd"
# 解析选项
while [ -n "$1" ]
do
    case "$1" in
        -h|--help)
            echo -e "$help_str"
            exit ;;
        -d|--dest)
            dest="$2"
            shift ;;
        --) shift
            break ;;
         *) echo "$1 is not an option"
            exit 1 ;;  # 发现未知参数，退出
    esac
    shift
done
cp -a ../index.html $dest