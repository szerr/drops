# periodic_example

在定时任务里常用的脚本示例
注意，即使 run-parts 可以执行其他脚本，在 crond 中只能执行 shell 脚本，其他不会被执行也没有错误信息和日志。
要执行 drops-backup.py ，用 drops-backup 调用