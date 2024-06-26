# drops

drops 是一套基于 docker compose 的轻量级运维管理方案，提供项目管理方案和单机运维流程。提供版本控制，发布更新，异地备份和迁移。支持集成到现有 CI/CD 系统中。可以应用在：中小型项目运维，离线环境部署。

**环境要求**：Python >=3.9

**Requires:** Python >=3.9

## 快速开始

### 安装

1. 安装 rsync 和 ssh 客户端:
2. 安装 drops：

```sh
pip install --upgrade drops
```

### 初始化项目

```sh
drops new example	# 创建示例项目
cd example
```

### 在本地启动服务

```sh
drops up
drops ps
```

访问 http://localhost 可以看到服务正常运行。

### 部署远程服务

```sh
drops -e dev -H <hostname> -p <port> -u root -i <~/.ssh/id_ed25519> -P <password> env add # 替换 <xx> 的相应信息，增加一个 dev 环境的连接配置。-i 和 -P 填其中一个就好。
drops init_env_debian # debian 系这样初始化远程环境
drops -e dev deploy # 同步项目目录到 /srv/drops/example 并启动容器。
drops -e dev ps # 查看容器运行状态
```

如果 `init_env_debian` 出现问题，请手动安装 `rsync`、`docker` 和 `docker-compose`
`centOS `配置参考这里安装 docker <https://mirrors.tuna.tsinghua.edu.cn/help/docker-ce/> ，然后去 <https://github.com/docker/compose/releases/latest> 下载安装 docker-compose。
podman-compose 和 docker-compose 并不兼容，会导致`drops`部署功能出现问题。

## 在 docker 中使用

```sh
docker pull szerr/drops
# 创建示例项目
docker run -it --rm -v `pwd`:/srv/drops szerr/drops drops new example
cd example
```

## 项目结构

新建`drops`项目后，会生成一些预定的文件夹，结构如下：

```sh
├── docker-compose.yaml # 当前项目的 docker compsoe 文件
├── drops.yaml # drops 配置文件
├── release # 项目发布目录，存放项目的可执行文件，静态文件等。用 volumes 映射到容器中执行。
├── secret  # 存放验证文件，key 等。
├── servers # 容器中服务的配置文件，第三方提供的二进制文件。用 volumes 映射到容器中。
├── src     # 项目源码路径，每个项目一个文件夹。如果项目适配有 Dockerfile，放在项目根目录中。
├── var     # 容器暂存的文件，cache、log 等不重要的数据。推荐按 文件类型/容器名 映射到容器中。
└── volumes # 容器落地的数据，可以用 drops backup 备份，drops sync volumes 从本地同步到远程。
```

**注意！不要将应用数据，容器生成的文件放到 `servers`、`releace`，`docker sync` 同步时远程路径会被删除或覆盖。**

## 配置

`drops.yaml`

```yaml
env:
  example: # 环境名，env 名。
    host: example.com # 远程地址
    port: 22 # 远程服务器 SSH 端口号
    username: root # 远程服务器 SSH 用户名
    password: "" # SSH 密码，明文记录，建议用 identity_file 做验证。
    identity_file: ~/.ssh/id_ed25519 # SSH identity file，不填的话会自动搜索 ~/.ssh/ 或 ./secret/id_*
    deploy_path: /srv/drops/example # 部署路径，默认 /srv/drops/<项目名>
    encoding: utf-8 # 远程服务器编码，默认 utf-8
    type: remote # 环境类型，如果是 remote 会通过 SSH 执行部署和同步，如果是 local 只会在本地执行。
  local: # 默认有一个 local 配置，方便本地调试。
    deploy_path: . # 本地配置的部署路径可以是当前目录，也可以是其他路径
    type: local # 类型为 local
project:
  default_env: local # 没有 -e 指定 env 时默认使用的环境
  name: te # 项目名
```

## 设计理念

使用`docker-compose`编排服务，基于`rsync`实现增量备份和数据同步。用 `git `做版本控制。

`drops` 推荐使用基础容器，将项目文件映射到容器中，而不是`build`时打包到容器。这样可以不依赖自建`docker`源。如果有定制需求，容器在部署时现场 `build`。

使用 `build` 命令发布项目，结合 `sync`，`deploy` 等命令实现服务部署，`git tag` 的版本控制实现回滚。`backup` 和 `sync` 实现备份迁移和预发布环境的快速搭建。

## 与项目集成

将项目放到 src 下（或者使用软链接），不需要纳入版本控制。每个项目分开管理。

## 数据管理

配置文件映射到 `servers` 下并做版本控制。

程序生成的文件，不需要做保留的如日志，映射到 `./var/` 下。

落地的文件，数据库等映射到 `./volumes/<服务名>`，这也是默认备份的位置。

## CLI

### 全局参数

每个 `env` 代指一个服务器的连接，部署信息。

为了保持灵活的交互界面，`drops` 执行时可以指定 `env` 的任意属性，覆盖配置文件。

| 短参数 | 长参数            | 功能                                                                                 |
| ------ | ----------------- | ------------------------------------------------------------------------------------ |
| `-e`   | `--env`           | 操作的 `env` 名字，默认取 `drops.yaml` 的 `project.default_env`                      |
| `-t`   | `--env-type`      | 操作的`env`类型，默认为 `drops.yaml `                                                |
| `-H`   | `--host`          | 主机名或 ip                                                                          |
| `-p`   | `--port`          | 远程 ssh 端口号，默认 22                                                             |
| `-u`   | `--username`      | 用户名，默认 `root`                                                                  |
| `-P`   | `--password`      | 密码，默认空                                                                         |
| `-i `  | `--identity-file` | SSH `identity-file`，和密码二选一，都不填的话会自动搜索 `~/.ssh/` 或 `./secret/id_*` |
| `-E`   | `--encoding`      | 远程服务器的编码，默认 utf-8                                                         |
| `-d`   | `--deploy-path`   | 部署路径，默认 `/srv/drops/[project name]`                                           |
| `-c`   | `--config`        | 指定读取的配置文件                                                                   |
|        | `--debug`         | 输出异常栈，解锁 `undeploy`、`clean` 命令                                            |

### 命令

| drops 命令                  | 功能                                                                                     |
| --------------------------- | ---------------------------------------------------------------------------------------- |
| `new dirname <projectname>` | 创建一个`drops`项目。                                                                    |
| `init`                      | 在当前目录初始化一个 `drops` 项目。                                                      |
| `env`                       | 管理服务器连结配置。                                                                     |
| `deploy`                    | 同步后启动容器。                                                                         |
| `redeploy`                  | 同步后启动容器，不同的是它会重新 build，并删除不需要的容器。                             |
| `sync`                      | 同步项目到服务器。                                                                       |
| `backup`                    | 备份远程目录到本地。使用时间做文件夹实现增量备份，如 `drops backup -d %Y-%m-%d_%H:%M:%S` |
| `ps`                        | 查看当前运行的容器。                                                                     |
| `start`                     | 启动容器。                                                                               |
| `up`                        | 创建和启动容器。                                                                         |
| `restart`                   | 重启容器。                                                                               |
| `stop`                      | 停止容器。                                                                               |
| `kill`                      | 杀掉容器。                                                                               |
| `rm`                        | 删除容器。                                                                               |
| `logs`                      | 输出容器日志。-f 持续输出。                                                              |
| `exec container cmd`        | 执行容器中的命令，因为没有模拟`TTY`，只能执行非交互式命令。                              |
| `watch`                     | 监视文件系统事件，执行传入的 command。                                                   |
| `nginxReload`               | 重载`nginx`配置，但不会更新证书。                                                        |
| `nginxForceReload`          | 重载`nginx`配置，会更新证书。                                                            |
| `deployHttpsKey`            | 申请并部署 `https` 证书。                                                                |
| `deployHttpsKey`            | 申请并部署 `https` 证书。                                                                |
| `initDebianEnv`             | 初始化远程服务器环境`Debian`系用。                                                       |
| `drops project <name>`      | 输出或更改项目名，也就是部署到`/srv/drops/<projectName>`的路径。                         |
| `undeploy`                  | 清理掉服务器上的项目和容器。（危）                                                       |
| `clean`                     | 删除当前项目下 `drops` 相关的文件。（危）                                                |

`--help` 查看命令的更多帮助。
`start`、`up`、`restart`、`stop`、`kill`、`rm` 默认对所有容器操作，可以用 -s 指定一个容器。
`-f` 强制执行，隐藏需要确认的选项。

## 包含的示例

`docker-compose.yaml` 中可以看到`nginx`，`drops`，`acme.sh`。

`servers/nginx/lib` 中有几个可复用的配置

`servers/nginx/nginx.conf` 可以选择开启的配置

`servers/crond/periodic_example/drops-backup.py` 是一个异地备份脚本。

## 测试与打包

首先安装打包需要的依赖

```sh
pip install build
```

进入 script 目录，`build.sh` 生成包，`install.sh` 会先调用 `build.sh` ，并安装包到本地。

执行 `release.py <版本号>`  更改版本信息，并用 `gh` 创建发布，联合 `workflows` 实现发包。

## 致谢

感谢 [JetBrains](https://jb.gg/OpenSourceSupport) 提供的 IDE

## 如何贡献

非常欢迎你的加入！[提一个 Issue](https://github.com/szerr/drops/issues/new) 或者提交一个 Pull Request。

标准 Readme 遵循 [Contributor Covenant](http://contributor-covenant.org/version/1/3/0/) 行为规范。

## 使用许可

[GNUv3](https://github.com/szerr/drops/blob/master/LICENSE) © Richard Littauer
