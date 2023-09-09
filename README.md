# drops

drops 是总结了我用 docker 的运维经验所做的部署和管理工具。
便于在没有完善 `CI/CD` 流程的情况下部署服务，版本控制，并提供备份和迁移。
发布文件通过目录映射到容器里，减少对容器的定制需求。如果有定制需求，容器在部署时现场 `build`，不需要自建镜像源。
基于 docker-compose 管理服务，基于 rsync 实现的备份和同步。

[快速入门](#快速入门)

[项目结构](#项目结构)

[与项目集成](#与项目集成)

[数据管理](#数据管理)

[命令](#命令)

[包含的示例](#包含的示例)

## 快速入门

### 安装

1. 安装 rsync 和 ssh 客户端
2. 安装 drops：

```sh
pip install --upgrade drops
```

_注：pip 是 python 的包管理器，视系统可能需要手动安装，像是 apt install python3-pip。_

### 初始化项目

```sh
drops new example	# 创建 drops 项目
cd example
```

### 配置远程服务器

```sh
drops -H <hostname> -p 22 -u root -i ~/.ssh/id_ed25519 -P 1 -e dev -E utf-8 -d /srv/drops -c drops.yaml env add# 配置一个测试服务器。
drops init_env_debian # debian 系这样初始化远程环境
```

如果配置出现问题，请手动安装 `rsync`、`docker` 和 `docker-compose`
centos 配置很复杂，参考 <https://mirrors.tuna.tsinghua.edu.cn/help/docker-ce/> 安装 docker，然后去 <https://github.com/docker/compose/releases/latest> 下载安装 docker-compose。
podman-compose 和 docker-compose 并不兼容，会造成 drops 部署部分不能用。

### 部署示例服务

默认会启动一个 nginx 容器。

```sh
drops -e dev deploy # 同步项目目录到 /srv/drops/example 并启动容器。
```

访问 http://<ip> 可以看到服务正常启动了。

## 项目结构

新建`drops`项目后，会生成一些预定的文件夹，其中：

- `src` 是项目的源码路径，每个项目一个文件夹。每个项目对应一个到多个容器。项目的 Dockerfile 也应该放在这里。
- `servers` 下存放每个容器的依赖文件，配置等。需要对第三方容器做 build 的 Dockerfile 放在这里。
- `releace` 存放项目的可执行文件，静态文件等，并映射到容器中执行。使用 `drops build` 执行编译发布到这个文件夹。
- `volumes` 容器落地的数据，可以用 `drops backup` 备份。
- `backup` 如果没有，运行`drops backup` 会创建。存放备份文件。
- `var` 容器暂存的文件，cache、log 等不重要的数据。
- `secret` 存放验证文件

**注意！不要将应用数据，容器生成的文件放到 servers、releace，`docker sync` 同步时远程路径会被删除或覆盖。**

## 与项目集成

将项目放到 src 下，不需要纳入版本控制。每个项目分开管理。

## 数据管理

配置文件映射到 `servers` 下并做版本控制。
程序生成的文件，不需要做保留的如日志，映射到 `./var/` 下。
落地的文件，数据库等映射到 `./volumes/<服务名>`，这里支持做备份。

不确定的话，考虑数据是否需要版本控制，需要的话就放到`servers`下。不需要的放到源码中，`build`时复制到 `release`。

## 命令

| drops 命令                  | 功能                                                             |
| --------------------------- | ---------------------------------------------------------------- |
| `new dirname <projectname>` | 创建一个`drops`项目。                                            |
| `init`                      | 在当前目录初始化一个 `drops` 项目。                              |
| `env`                       | 管理服务器连结配置。                                             |
| `deploy`                    | 同步后启动容器。                                                 |
| `redeploy`                  | 同步后启动容器，不同的是它会重新 build，并删除不需要的容器。     |
| `sync`                      | 同步项目到服务器。                                               |
| `backup`                    | 备份远程目录到本地。如 `drops backup -d %Y-%m-%d_%H:%M:%S`       |
| `ps`                        | 查看当前运行的容器。                                             |
| `start`                     | 启动容器。                                                       |
| `up`                        | 创建和启动容器。                                                 |
| `restart`                   | 重启容器。                                                       |
| `stop`                      | 停止容器。                                                       |
| `kill`                      | 杀掉容器。                                                       |
| `rm`                        | 删除容器。                                                       |
| `logs`                      | 输出容器日志。-f 持续输出。                                      |
| `exec container cmd`        | 执行容器中的命令，因为没有模拟`TTY`，只能执行非交互式命令。      |
| `nginxReload`               | 重载`nginx`配置，但不会更新证书。                                |
| `nginxForceReload`          | 重载`nginx`配置，会更新证书。                                    |
| `deployHttpsKey`            | 申请并部署 `https` 证书。                                        |
| `initDebianEnv`             | 初始化远程服务器环境`Debian`系用。                               |
| `undeploy`                  | 清理掉服务器上的项目和容器。                                     |
| `clean`                     | 删除当前项目下 `drops` 相关的文件。                              |
| `drops project name`        | 输出或更改项目名，也就是部署到`/srv/drops/<projectName>`的路径。 |

`--help` 查看更多帮助。
`start`、`up`、`restart`、`stop`、`kill`、`rm` 默认对所有容器操作，可以用 -s 指定一个容器。
`-f` 强制执行，隐藏需要确认的选项。

## 包含的示例

`docker-compose.yaml` 中可以看到`nginx`，`crond`，`acme.sh`。

`servers/nginx/lib` 中有几个简单的配置

`servers/nginx/nginx.conf` 可以选择开启的配置

`servers/crond/periodic_example/backup.sh` 是一个异地备份脚本。

## 致谢

感谢 [JetBrains](https://jb.gg/OpenSourceSupport) 提供的 IDE
