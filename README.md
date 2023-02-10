# drops

drops 是基于 ssh 和 docker-compose 的运维模板。
附带的 drops 命令可以方便的管理项目，部署服务。

[快速入门](#快速入门)

[项目背景](#项目背景)

[项目管理](#项目管理)

[与项目集成](#与项目集成)

[数据管理](#数据管理)

[drops命令](#drops命令)

[包含的示例](#包含的示例)

[注意事项](#注意事项)


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
drops host add default ssh.example.com <port df:22> <user df:root> -k ~/.ssh/id_ed25519 # 配置一个测试服务器。
drops init_env_debian # debian 系这样初始化远程环境
```
如果配置出现问题，请手动安装 `rsync`、`docker` 和 `docker-compose`
centos 配置很复杂，参考 <https://mirrors.tuna.tsinghua.edu.cn/help/docker-ce/> 安装 docker，然后去 <https://github.com/docker/compose/releases/latest>  下载安装 docker-compose。
podman-compose 目前（2022年12月）还是有一些问题，会造成 drops 部署部分不能用。

### 部署示例服务
默认会启动一个 nginx 容器。
```sh
drops deploy # 同步项目目录到 /srv/drops/<项目文件夹名> 并启动容器。
```

访问 http://<ip> 可以看到服务正常启动了。

## 项目背景

虽然看上去 drops 是一个部署工具；但我想表达的是：

- 运维相关文件纳入版本控制，保证运维操作可追踪可回溯。
- 用文件保证环境一致，一切基于文件。
- 不要手动编辑线上和测试的配置文件，不要在线调试。
- 所有更改上测试通过之后传版本控制，再部署到线上；出问题利用`git`回滚。
- 应用发布的包，静态文件，视情况纳入运维项目的版本控制，和服务配置绑定。
- 考虑对应用数据做冗余、快照和备份。

## 项目管理

将服务部署管理分为：`机器-系统-容器/项目`。

一台`机器`可以部署一个或多个`系统`，一个系统由一到多个`容器`/`项目`组成。

`drops` 对应`系统`这一层，管理多个服务。

容器的配置文件、依赖文件，在`servers`下创建以服务名命名的文件夹，放到对应的文件夹中。

应用程序发布的包，静态文件，在`release`下创建相应的文件夹，在`docker-compose.yaml` 用相对路径（`./release/`）映射到容器内。如果 drops 创建为单独的项目，请考虑将`release`纳入版本控制。

应用数据，容器生成的文件，放到`volumes`对应的文件夹。在 `docker-compose.yaml` 用相对路径（`./volumes/`）映射到容器里。这样本地测试会很方便。
经常变化的文件，如 log、lock、sock 文件等，放到 `var` 中。按`文件类型/服务名`分类存放。不要做版本控制，不建议做备份。

编辑`docker-compose.yaml`，定义你需要的服务。

**注意！不要将应用数据，容器生成的文件放到 servers、releace，同步时文件会被删除或覆盖。**

参照 `servers/crond/periodic_example/backup.sh` 快速搭建异地增量备份。

一个系统可以部署到多台机器，其中机器可以分为：线上，测试1，测试2，bulabula。。。。

`drops host` 可以管理多台机器。可以试试 `drops ls` 输出目前的 `group` 和 `host`

`drops` 没有指定 `-a\--hostAlias` 参数的时候，默认对 `default`  下所有机器做操作。所以可以当作单机部署工具用。

## 与项目集成

两种方式，集成到项目内或作为单独的项目管理

### 集成到项目内

在需要管理的项目目录下执行`drops new drops <projectName>`，会在当前目录创建 drops 文件夹。这适合只有一个版本控制项目的情况。

默认`git`会排除`releace`，保持这样就好。写一个`build`脚本，输出指向`releace.<projectName>`。

### 作为单独的项目管理

当需要版本控制管理多个项目时，建议新建一个专为运维的项目：`drops new <projectName>`，这会在当前目录创建`<projectName>`文件夹。然后用`git init`初始化版本控制。

默认`git`会排除`releace`，这种情况建议从`.gitignore`删除`releace`，并将其纳入版本控制。每个项目写一个 build 脚本，将输出指向`releace.<projectName>`。



## 数据管理

将项目分成运行时可变和不可变的

- 运行时可变的是服务产生的数据，如：用户数据， 日志，数据库
- 运行时不可变的，如：程序，服务配置，静态文件

运行时可变的数据是放到`/srv/drops/<项目名>/volumes/<服务名>/<映射到容器的文件夹>`，这是建议做冗余、快照和备份的地方。

不变的数据放到`servers`下并做版本控制。

不确定的话，考虑数据是否需要版本控制，需要的话就放到`servers`下。不需要的放到源码中，`build`时复制到 `release`。

## drops 命令

| drops 命令         | 功能                                                         |
| ------------------ | ------------------------------------------------------------ |
| `new dirname <projectname>` | 创建一个`drops`项目。                                        |
| `init`             | 在当前目录初始化一个 `drops` 项目。                          |
| `host`             | 管理服务器连结配置。                                         |
| `deploy`           | 同步后启动容器。                                             |
| `redeploy`         | 同步后启动容器，不同的是它会重新 build，并删除不需要的容器。 |
| `sync`             | 同步项目到服务器。                                           |
| `backup` | 备份远程目录到本地。如 `drops backup -d %Y-%m-%d_%H:%M:%S` |
| `ps`               | 查看当前运行的容器。                                         |
| `start`            | 启动容器。                                                   |
| `up`               | 创建和启动容器。                                             |
| `restart`          | 重启容器。                                                   |
| `stop`             | 停止容器。                                                   |
| `kill`             | 杀掉容器。                                                   |
| `rm`               | 删除容器。                                                   |
| `logs` | 输出容器日志。-f 持续输出。 |
| `exec container cmd` | 执行容器中的命令，因为没有模拟`TTY`，只能执行非交互式命令。 |
| `nginxReload`      | 重载`nginx`配置，但不会更新证书。   |
| `nginxForceReload` | 重载`nginx`配置，会更新证书。 |
| `deployHttpsKey` | 申请并部署 `https` 证书。 |
| `initDebianEnv`    | 初始化远程服务器环境`Debian`系用。                           |
| `undeploy`         | 清理掉服务器上的项目和容器。                                 |
| `clean`            | 删除当前项目下 `drops` 相关的文件。                          |
| `drops project name` | 输出或更改项目名，也就是部署到`/srv/drops/<projectName>`的路径。 |

`--help` 查看更多帮助。
`start`、`up`、`restart`、`stop`、`kill`、`rm` 默认对所有容器操作，可以用 -s 指定一个容器。
`-f` 强制执行，隐藏需要确认的选项。

## 包含的示例

`docker-compose.yaml` 中可以看到`nginx`，`crond`，`acme.sh`。

`servers/nginx/lib` 中有几个简单的配置

`servers/nginx/nginx.conf` 可以选择开启的配置

`servers/crond/periodic_example/backup.sh` 是一个异地备份脚本。



## 注意事项
drops 的功能还在测试开发阶段，我认为可靠时会发 v1 版。版本号第二位变动时说明命令行界面有比较大的变化。
核心理念是不变的，drops 只是这个理念的工具。
使用过程中遇到任何问题或建议请发 issue 给我，我会尽快解决。
为了实现备份，同步，部署相关功能，执行的 `rsync` 命令 会带有 `--del` 参数，会删除不匹配的文件，保持文件夹内文件相同，**删除前不一定有提示**。我会在可能有风险的地方加提示，也会做相应测试。也请各位在使用时多加小心并承担相应风险。用测试确定流程，保障逻辑准确；用冗余，备份和快照防止数据丢失。

