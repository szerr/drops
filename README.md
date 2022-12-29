# drops
drops 是基于 ssh 和 docker-compose 的运维模板。
附带的 drops 命令可以方便的管理项目，部署服务。并提供常见服务配置示例以供参考。

## 快速入门

### 安装

1. 安装 rsync 和 ssh 客户端
2. 安装 drops：

``` sh
pip install --upgrade drops
```

*注：pip 是 python 的包管理器，视系统可能需要手动安装，像是 apt install python3-pip。*

### 初始化项目

```sh
drops new example	# 创建 drops 项目
cd example
```

### 配置远程服务器

```sh
drops host add ssh.example.com <port df:22> <user df:root> -k ~/.ssh/id_ed25519 # 配置一个服务器到默认的 test group。
drops init_env_debian # debian 系这样初始化远程环境
```
如果配置出现问题，请手动安装 `rsync`、`docker` 和 `docker-compose`
centos 配置太复杂了，参考 <https://mirrors.tuna.tsinghua.edu.cn/help/docker-ce/> 安装 docker，然后去 <https://github.com/docker/compose/releases/latest>  下载安装 docker-compose。
podman-compose 目前（2022年12月）还是有一些问题，会造成 drops 部署部分不能用。

### 部署示例服务
默认会下载并启动一个 nginx 容器。
```sh
drops deploy # 同步项目目录到 /usr/local/drops/<项目文件夹名> 并启动容器。
```

访问 http://<ip> 可以看到后端返回的数据。

## 项目背景

虽然看上去 drops 是一个部署工具；但我想表达的是：

- 一个项目的运维立一个项目。
- 用容器保证环境一致。
- 做版本控制，保证运维操作可追踪可回溯。
- 不要手动编辑线上和测试的配置文件，不要在线调试。
- 所有更改上测试通过之后传版本控制，再部署到线上；出问题马上回滚。
- 应用发布的包，静态文件，也应该纳入运维项目的版本控制，和服务配置绑定。
- 考虑对应用数据做冗余、快照和备份。

## 项目管理

将服务部署管理分为：`系统-机器-项目-服务`。

一台`机器`可以部署多个`项目`，一个系统由一到多台机器，一到多个项目组成。

`drops` 对应`项目`这一层，管理多个服务。

服务的配置文件、依赖文件，在`servers`下创建以服务名命名的文件夹，放到对应的文件夹中。

编辑`docker-compose.yaml`，定义你需要的服务。

为了方便管理和迁移，建议程序生成的目录映射统一放到`/srv/drops`，格式为：`/srv/drops/<项目名>/<服务名>/<映射到容器的文件夹>`

参照 `servers/crond/periodic_example/backup.sh` 快速搭建异地增量备份。

一个项目可以部署到多台机器，其中机器可以分为：线上，测试1，测试2，bulabula。。。。

`drops host` 可以管理多个分组的机器。可以试试 `drops ls` 输出目前的 `group` 和 `host`

`drops` 没有指定 `-g` 参数的时候，默认对 `test group`  下所有机器做操作。所以可以当作单机部署工具用。

## 数据管理

将项目分成运行时可变和不可变的

- 运行时可变的是服务产生的数据，如：用户数据， 日志，数据库
- 运行时不可变的，如：程序，服务配置，静态文件

运行时可变的数据是放到`/srv/drops/<项目名>/<服务名>/<映射到容器的文件夹>`，这是建议做冗余、快照和备份的地方。

不变的数据放到`servers`下并做版本控制。

如果拿不准，就考虑数据是否需要版本控制，需要的话就放到`servers`下。

## drops 命令

| drops 命令         | 功能                                                         |
| ------------------ | ------------------------------------------------------------ |
| `new`              | 创建一个`drops`项目。                                        |
| `init`             | 在当前目录初始化一个 `drops` 项目。                          |
| `host`             | 管理服务器连结配置。                                         |
| `deploy`           | 同步后启动容器。                                             |
| `redeploy`         | 同步后启动容器，不同的是它会重新 build，并删除不需要的容器。 |
| `sync`             | 同步项目到服务器。                                           |
| `ps`               | 查看当前运行的容器。                                         |
| `start`            | 启动容器。                                                   |
| `up`               | 创建和启动容器。                                             |
| `restart`          | 重启容器。                                                   |
| `stop`             | 停止容器。                                                   |
| `kill`             | 杀掉容器。                                                   |
| `rm`               | 删除容器。                                                   |
| `nginxReload`      | 对容器`nginx`执行`nginx -s reload`。                         |
| `nginxForceReload` | 更新`nginx`证书时，用这个脚本执行 `reload`。                 |
| `initDebianEnv`    | 初始化远程服务器环境`Debian`系用。                           |
| `undeploy`         | 清理掉服务器上的项目和容器。                                 |
| `clean`            | 删除当前项目下 `drops` 相关的文件。                          |
| `drops project name` | 输出或更改项目名，也就是部署到`/usr/local/drops/`下的文件夹名  |

`--help` 查看更多帮助。
`start`、`up`、`restart`、`stop`、`kill`、`rm` 默认对所有容器操作，可以用 -s 指定一个容器。
`-f` 强制执行，隐藏需要确认的选项。

## 包含的示例

`docker-compose.yaml` 中可以看到`nginx`，`crond`，`acme.sh`。

`servers/nginx/lib` 中有几个简单的配置

`servers/nginx/nginx.conf` 可以选择开启的配置

`servers/nginx/conf.d/default.conf` 有内部服务的示例，其中 `http_server` 是容器的名字。docker 有内置的`DNS`服务用来解析容器名。

`servers/crond/periodic_example/backup.sh` 是一个异地备份脚本。
`servers/acme.sh` 是目前我在用的 `acme.sh` 配置。
