---
toc: true
title: 你不可不知的容器编排进阶技巧
categories:
  - 编程语言
tags:
  - Docker
  - 容器
  - 服务编排
  - 云原生
copyright: true
abbrlink: 172025911
date: 2021-08-14 22:13:32
---
在团队内推广`Docker Compose`有段时间啦，值得庆幸的是，最终落地效果还不错，因为说到底，大家都不大喜欢，那一长串复杂而枯燥的命令行参数。对我而言，最为重要的一点，团队内使用的技术变得更加透明化、标准化，因为每个微服务的配置信息都写在`docker-compose.yml`文件中，任何人都可以快速地构建出一套可用的服务，而不是每次都要去找具体的某一个人。我想说，这其实是一个信息流如何在团队内流动的问题。也许，我们有文档或者`Wiki`，可新人能不能快速融入其中，这才是检验信息流是否流动的唯一标准。就这样，团队从刀耕火种的`Docker`时代，进入到使用服务编排的`Docker Compose`时代。接下来，能否进入`K8S`甚至是云原生的时代，我终究不得而知。今天我想聊聊，在使用`Docker Compose`的过程中，我们遇到的诸如容器的**启动顺序**、**网络模式**、**健康检查**这类问题，我有一点`Docker Compose`的进阶使用技巧想和大家分享。

# 容器的启动顺序

使用服务编排以后，大家最关心的问题是，如果服务间存在依赖关系，那么如何保证容器的启动顺序？我承认，这是一个真实存在的问题，譬如，你的应用依赖某个数据库，理论上数据库要先启动，抑或者是像`Redis`、`Kafka`、`Envoy`这样的基础设施，总是要优先于应用服务本身启动。

![假如章鱼的这些脚互相影响会怎么样？](https://i.loli.net/2021/08/15/LnAh6GSdMJ2NkVx.png)

熟悉`Docker Compose`的同学，也许会想到`depends_on`这个选项，可如果大家亲自去尝试过就会知道，这终究只是我们的一厢情愿。为什么呢？因为这个`depends_on`主要是看目标容器是不是处于`running`的状态，所以，在大多数情况下，我们会注意到`Docker Compose`并不是按我们期望的顺序去启动的，因为目标容器在某一瞬间的确已经是`running`的状态了，那这样简直太尴尬了有木有啊！我们从一个简单的例子开始：

```yaml
version: "3.8"
services:
  redis_server:
    image: redis:latest
    command: >
      /bin/bash -c '
      sleep 5;
      echo "sleep over";'
    networks:
      - backend
  city_service:
    build: CityService/
    container_name: city_service
    ports:
      - "8081:80"
    networks:
      - backend
    depends_on:
      - redis_server

networks:
  backend:
```

可以注意到，为了证明`city_service`服务不会等待`redis_server`服务，我故意让子弹飞了一会儿，结果如何呢？我们一起来看看：

![ Docker Compose 启动顺序：一厢情愿](https://i.loli.net/2021/08/15/BqDRtbJkpVcno3s.png)

果然，我没有骗各位，`city_service`服务不会等待`redis_server`服务。我们知道，`Redis`提供的命令行接口中，有一个`PING`命令，当`Redis`可以正常连接的时候，它会返回一个`PONG`，也许，这就是乒乓球的魅力所在。基于这个想法，我们继续修改`docker-compose.yml`文件：

```yaml
version: "3.8"
services:
  redis_server:
    image: redis:latest
    networks:
      - backend
  city_service:
    build: CityService/
    container_name: city_service
    ports:
      - "8081:80"
    networks:
      - backend
    depends_on:
      - redis_server
    command: >
      /bin/bash -c '
      while ! nc -z redis_server 6379;
      do
        echo "wait for redis_server";
        sleep 1;
      done;

      echo "redis_server is ready!";
      echo "start city_service here";
      '
networks:
  backend:
```
这里，我们用了一种取巧的方法，`Ubuntu`中的`nc`命令可以对指定主机、指定端口进行检测，换言之，我们简单粗暴的认为，只要`6379`这个端口可以访问，就认为`Redis`准备就绪啦，因为我们没有办法在`city_service`这个容器中调用`redis-cli`，这个做法本身并不严谨，我们这里更多的是验证想法：

![Docker Compose 启动顺序：检测 Redis](https://i.loli.net/2021/08/15/Hhx4R7obZL5FBrv.png)

可以注意到，此时，`city_service`服务会等待`redis_server`服务，直到`redis_server`服务就绪。所以，要解决服务编排时，容器的启动顺序的问题，本质上就是把需要等待的服务、端口以及当前服务的启动命令，统一到容器的入口中。为此，官方提供了 [wait-for-it](https://github.com/vishnubob/wait-for-it) 这个方案，官方关于容器启动顺序的文档，可以参考：[Startup Order](https://docs.docker.com/compose/startup-order/)。对于上面的例子，我们可以这样改写`docker-compose.yml`文件：

```yaml
version: "3.8"
services:
  redis_server:
    image: redis:latest
    networks:
      - backend
  city_service:
    build: CityService/
    container_name: city_service
    ports:
      - "8081:80"
    networks:
      - backend
    depends_on:
      - redis_server
    command: ["/wait-for-it.sh", "redis_server:6379", "--", "dotnet", "CityService.dll"]
networks:
  backend:
```
此时，启动容器时的效果如下，因为这个方案依赖 [Netcat](http://netcat.sourceforge.net/) 这样一个工具，所以，我们的容器中还需要加入这个工具，此时，可以使用下面的脚本片段：

```dockerfile
FROM debian:buster-slim as wait-for-it
RUN apt-get update && apt-get install -y "wait-for-it"
COPY --from=wait-for-it /usr/bin/wait-for-it .
```

不过，不太明白为什么这里一直提示路径不对：

![Docker Compose 启动顺序：wait-for-it.sh](https://i.loli.net/2021/08/16/jgbwuVHeJNvG5BY.png)

个人建议，最好将这个语句写在`Dockerfile`，或者试提供一个类似于`entrypoint.sh`的脚本文件。关于这个方案的更多细节，大家可以参考[官方文档](https://docs.docker.com/compose/startup-order/)，写这篇文章的时候，我不由得感慨：`Shell`脚本真的是太难学了(逃......。所以，点到为止。刚刚提到过，我个人觉得这种主机 + 端口号的检测方式不够严谨，因为一个端口可以`PING`通，并不代表服务一定是可用的，所以，在接下来的内容里，我会介绍基于健康检查的思路。

# 容器的健康检查

不知道大家有没有这样的经历，就是你明明看到一个容器的状态变成`Up` ，可对应的微服务就是死活调不通。面对来自前端同事的戏谑与嘲讽，你不禁仰天长叹一声，开始在容器里翻箱倒柜，一通操作如虎。过了许久，你终于发现是容器内部出现了始料不及的错误。看来，容器状态显示为`Up`，并不代表容器内的服务就是可用的啊！果然，还是需要一种机制来判断容器内的服务是否可用啊！等等，这不就是传说中的健康检查？恭喜你，答对了！

![ Docker 经典集装箱形象](https://i.loli.net/2021/08/15/fplPBvICiEOYsKR.jpg)

在`Docker`及`Docker Compse`中，均原生支持 [健康检查](https://docs.docker.com/engine/reference/builder/#healthcheck) 机制，一旦一个容器指定了`HEALTHCHECK`选项，`Docker`会定时检查容器内的服务是否可用。我们都知道，一个普通的 Docker 容器，无非是开始、运行中、停止这样三种状态，而提供了`HEALTHCHECK`选项的`Docker`容器，会在这个基础上增加健康(**healthy**)和非健康(**unhealthy**)两种状态，所以，我们应该用这两个状态来判断容器内的服务是否可用。下面是一个指定了`HEALTHCHECK`选项的容器示例：

```dockerfile
FROM FROM mcr.microsoft.com/dotnet/core/aspnet:3.1-buster-slim
EXPOSE 80
EXPOSE 443
WORKDIR /app
COPY /app/publish .
ENTRYPOINT ["dotnet", "CityService.dll"]
HEALTHCHECK --interval=5s --timeout=3s \
  CMD curl -fs http://localhost:80/city || exit 1
```
可以注意到，`Docker`原生的健康机制，需要通过`CMD`的方式来执行一个命令行，如果该命令行返回 0 ，则表示成功；返回 1，则表示失败。

此处，我们还可以配置以下三个参数，`--interval=<间隔>`表示健康检查的间隔，默认为30秒；`--timeout=<时长>`表示健康检查命令超时时间，超过该时间即表示`unhealthy`，默认为30秒；`--retries=<次数>`表示连续失败的次数，超过该次数即表示`unhealthy`。对于我们这里的`ASP.NET Core`应用而言，如果程序正常启动，显然这个地址是可以调通的，我们可以用这个来作为一个“探针”。

![ Docker 健康检查：healthy ](https://i.loli.net/2021/08/14/QnuPZ8vsCYKbVHm.png)

我们可以注意到，在容器启动的第14秒，其状态为：`health：starting`。而等到容器启动的第16秒，其状态则为：`healthy`，这表明我们的服务是健康的。此时此刻，如果我们耍点小心思，让`curl`去访问一个不存在的地址会怎么样呢？可以注意到，此时状态变成了：`unhealthy`:

![Docker 健康检查：unhealthy ](https://i.loli.net/2021/08/14/oNtX8G7UAqEDIzS.png)

`HEALTHCHECK`指令除了可以直接写在`Dockerfile`中以外，还可以直接附加到`docker run`命令上，还是以上面的项目作为示例：

```shell
docker run  --name city_service -d -p 8081:80  city_service \
--health-cmd="curl -fs http://localhost:80/city || exit 1" \
--health-interval=3s \
--health-timeout=5s \
--health-retries=3 
```
甚至，我们还可以使用下面的命令来查询容器的健康状态：`docker inspect --format='{{json .State.Health}}' <ContainerID>`

```json
{
  "Status": "unhealthy",
  "FailingStreak": 5,
  "Log": [{
	"Start": "2021-08-14T15:27:50.3325424Z",
	"End": "2021-08-14T15:27:50.3813102Z",
	"ExitCode": 1,
	"Output": ""
  }]
}
```
不过，我个人感觉这个`curl`的写法非常别扭，尤其是当我试图在`docker-compose`中写类似命令的时候，我觉得稍微复杂一点的健康检查，还是交给脚本语言来实现吧！例如，下面是官方提供的针对`MongoDB`的健康检查的脚本`docker-healthcheck.sh`：

```shell
#!/bin/bash
set -eo pipefail 
host="$(hostname --ip-address || echo '127.0.0.1')" 
if mongo --quiet "$host/test" --eval 'quit(db.runCommand({ ping: 1 }).ok ? 0 : 2)'; then 
   exit 0
fi 
   exit 1
```
此时，`HEALTHCHECK`可以简化为：

```dockerfile
HEALTHCHECK --interval=5s --timeout=3s \
  CMD bin/bash docker-healthcheck.sh
```
更多的示例，请参考：[docker-library/healthcheck/](https://github.com/docker-library/healthcheck/) 以及 [rodrigobdz/docker-compose-healthchecks](https://github.com/rodrigobdz/docker-compose-healthchecks)。

其实，对于容器的启动顺序问题，我们还可以借助检查检查的思路来解决，因为`depends_on`并不会等待目标容器进入`ready`状态，而是等目标容器进入`running`状态。这样，就回到了我们一开始描述的现象：一个容器明明都变为`Up`状态了，可为什么接口就是死活调不通呢？因为我们无法界定这样一个`ready`状态。考虑到`depends_on`可以指定`condition`，此时，我们可以这样编写`docker-compose.yml`文件：

```yaml
version: "3.8"
services:
  redis_server:
    image: redis:latest
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 1s
      timeout: 3s
      retries: 30
    networks:
      - backend
  city_service:
    build: CityService/
    container_name: city_service
    ports:
      - "8081:80"
    networks:
      - backend
    depends_on:
      redis_server:
        condition: service_healthy
networks:
  backend:
```
简单来说，我们使用了`Redis`内置的命令对`redis_server`服务进行健康检查，而`city_service`服务则依赖于`redis_server`服务的健康状态，只有当`Redis`准备就绪了以后，`city_service`才会开始启动。下面是实际启动过程的截图，看看是不是和我们想的一样：

![ Docker 健康检查：容器启动顺序](https://i.loli.net/2021/08/15/HKvjmoCdznlW6FV.png)

果然，奇怪的知识有增加了呢，我们唯一需要解决的问题，就是怎么给某一个服务做健康检查，以上！

# 容器的网络模式

接下来，我们来说说`Docker`里的网络模式，特别是当我们使用`docker-compose`来编排一组服务的时候，假设我们有一个目录`app`，在这个牡蛎里我们放置了服务编排文件`docker-compose.yml`，默认情况下，`Docker-Compose`会创建一个一个名为`app_default`的网络，并且这个网络是`bridge`，即网桥模式的一个网络。什么是网桥模式呢？你可能会感到困惑，而这要从`Docker`中的网络模式开始说起，这里简单下常用的几种：

* host模式，或叫做主机模式，可以认为容器和主机使用相同的端口进行访问，因为容器和主机在同一个网络下，此模式下，意味着通过`-p`绑定的端口失效，因为所有容器都使用主机的网络，所以容器间可以相互通信，此模式通过`--network=host`指定。
* bridge模式，或叫做网桥模式，这是`Docker`中默认的网络设置，此模式下，容器和主机有各自的IP/端口号，两者之间通过一个虚拟网桥进行通信，虚拟网桥的作用类似于物理交换机。因此，不同容器间的网络是相互隔离的，此模式通过`--network=bridge`指定。
* none模式，通俗讲就是无网络模式，意味着容器是一个封闭的环境，无法通过主机访问外部的网络，这种模式在那种讲究保密性质、封闭式开发的场合应该会有一点用，可这都2021年了，难道你还能把互联网上的软件全部下载下来吗？此模式通过`--network=none`指定。
* container模式，或叫做共享模式，通俗来讲，就是指一个容器共享某个已经存在的容器的`Network Namespace`，此时，该容器将不会拥有属于自己的IP/端口号等资源，因为这种模式可以节约一定的网络资源，此模式通过`--network=<Container_ID>/<Container_Name>`指定。

为了帮助大家理解和区分这四种模式，博主绘制了下面的图示来补充说明：

![容器的网络模式(主机、容器、网桥)示意图](https://i.loli.net/2021/08/16/DJq3CBrmktaRNex.png)

通过以上的图文信息反复加深印象，相信大家可以找出点规律：

* 如果你的容器网络与主机网络不需要隔离，那么选择主机模式(**host**)
* 如果你的应用运行在不同的容器里，并且这些容器间需要相互通信，那么选择网桥模式(**bridge**)
* 如果你的应用需要运行在一个隔绝外界网络的环境中，那么选择无网络模式(**none**)
* 如果你希望在节省网络资源的同时，实现不同容器间的通信，那么选择容器模式(**container**)

以上四种网络模式，除了可以在`docker run`的时候指定以外，我们还可以在`docker-compose.yml`文件中指定。例如，下面表示的是一个主机模式的容器：

```yaml
version: '3.8'
services:
  cache_server:
    build: .
    container_name: cache_server
    restart: always
    network_mode: host
```

大多数情况下，我们只需要连接到`docker0`这个虚拟网卡即可，而如果你想为某个容器或者一组容器单独建立这样一张网卡，此时，就不得不提到`Docker`中的自定义网络功能，我们一起来看下面的示例：

```shell
// 创建一个网络：test-network
docker network create test-network
// 创建一个Nginx的容器：nginx_8087，使用网络：test-network
docker run -d --name nginx_8087 --network test-network -p 8087:80 nginx:latest
// 创建一个Nginx的容器：nginx_8088
docker run -d --name nginx_8088 -p 8088:80 nginx:latest
// 连接容器：nginx_8088 至网络：test-network
docker network connect test-network nginx_8088
```
接下来，通过下面的命令，我们可以拿到两个容器的ID，在此基础上我们看一下两个容器各自分配的IP是多少：

```shell
docker ps -a
docker inspect --format='{{.NetworkSettings.IPAddress}}' <ContainerID>
```

此时，我们会发现一个有趣的现象，`nginx_8087`这个容器，可以获得IP地址`172.17.0.2`，而`nginx_8088`则无法获得IP地址，这是为什么呢？这其实就是我们前面提到过的容器模式(**container**)，此时，`nginx_8088`这个容器实际上是和`nginx_8087`共享一个`Network Namespace`，即使它们有各自的文件系统。同样地，我们可以使用下面的命令来让容器从某个网络中断开：

```shell
// 断开容器：nginx_8088 至网络：test-network
docker network disconnect test-network nginx_8088
// 删除网络
docker network rm test-network
```
是否觉得手动维护容器的网络非常痛苦？幸好，我们还有`Docker-Compose`可以用，上面两个`Nginx`的容器我们可以这样维护：

```yaml
version: "3.8"
services:
  nginx_8087:
    image: nginx:latest
    container_name: nginx_8087
    ports:
      - 8087:80
    networks:
      - test-network
  nginx_8088:
    image: nginx:latest
    container_name: nginx_8088
    ports:
      - 8088:80
    networks:
      - test-network

networks:
  test-network:
    driver: bridge
```
此时，我们可以注意到，`Docker Compose`会创建两个网络，即`network_mode_default`和`network_mode_test-network`：

![Docker Compose 中使用自定义网络](https://i.loli.net/2021/08/16/Sgsbpt1huUlmTQM.png)

这说明默认网络依然存在，如果我们希望完全地使用自定义网络，此时，我们可以这样修改服务编排文件：

```yaml
networks:
  default:
    driver: host
```
这表示默认网络会采用主机模式，相应地，你需要修改`nginx_8087`和`nginx_8088`两个容器的`network`选项，使其指向`default`。

除此之外，你还可以使用`external`指向一个已经存在的网络：

```yaml
networks:
  default:
    external: true
    name: a-existing-network
```
在`Docker`中，每个容器都会分配`IP`，因为这个`IP`总是不固定的，所以，如果我们希望像虚拟机那样使用一个静态`IP`的话，可以考虑下面的做法：

```yaml
version: "3.8"
services:
  nginx_8087:
    image: nginx:latest
    container_name: nginx_8087
    ports:
      - 8087:80
    networks:
      - test-network
          ipv4_address: 172.2.0.10
  nginx_8088:
    image: nginx:latest
    container_name: nginx_8088
    ports:
      - 8088:80
    networks:
      - test-network
          ipv4_address: 172.2.0.11

networks:
  test-network:
    driver: bridge
    config:
      - subnet: 172.2.0.0/24
```
关于`Docker`及`Docker Compose`中的网络驱动，如 [macvlan](https://docs.docker.com/network/macvlan/)、[overlay](https://docs.docker.com/network/overlay/) 等等，这些显然是更加深入的话题，考虑到篇幅，不在这里做进一步的展开，对此感兴趣的朋友可以参考官方文档：[Networking Overview](https://docs.docker.com/network/) 以及 [Networking in Compose](https://docs.docker.com/compose/networking/)。博主写这篇文章的想法，主要是源于团队内落地`Docker-Compose`时的一次经历，当时有台虚拟机偶尔会出现`IP`被篡改的情况，而罪魁祸首居然是`Docker-Compose`，虽然最终用主机模式勉强解决了这个问题，可终究留下了难以言说的疑问，此刻，大概能稍微对`Docker`的网络有点了解。果然，越靠近底层，就是越是抽象、越是难以理解。

# 文本小结

本文分享了`Docker`及`Docker-Compose`中的进阶使用技巧，主要探索了服务编排场景下容器的启动顺序、健康检查、网络模式三类问题。默认情况下，`Docker-Compose`的`depends_on`选项，取决于容器是否处于`running`状态，因此，当我们有多个服务需要启动时，实际上启动顺序并不会受到`depends_on`选项的影响，因为此时容器都是`running`的状态。为了解决这个问题，官方提供了 [wait-for-it](https://github.com/vishnubob/wait-for-it) 的方案，这是一种利用 [Netcat](http://netcat.sourceforge.net/) 对`TCP`和`UDP`进行检测的机制，当检测条件被满足的时候，它会执行由用户指定的启动脚本。从这里看，其实已经有了一点健康检查的影子，而官方的健康检查，则允许用户使用更加自由的命令或者脚本去实现检测逻辑，所以，从这个角度上来讲，`HEALTHCHECK`结合`depends_on`，这才是实现容器启动顺序控制的终极方案。`Docker`的网络是一个相对复杂的概念，所以，这里就是简单的介绍了下常见的四种网络模式，更深入的话题比如网络驱动等，还需要花时间去做进一步的探索。本文示例以上传至[Github](https://github.com/Regularly-Archive/2021/tree/master/src/DockerTips)，供大家参考。好了，以上就是这篇博客的全部内容啦，谢谢大家！

