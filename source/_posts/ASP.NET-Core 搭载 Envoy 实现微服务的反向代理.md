---
toc: true
title: ASP.NET Core 搭载 Envoy 实现微服务的反向代理
categories:
  - 编程语言
tags:
  - Envoy
  - 微服务
  - 网关
  - 反向代理
copyright: true
abbrlink: 3599307335
date: 2021-07-01 22:49:47
---

回想起来，博主第一次接触到`Envoy`，其实是在微软的示例项目 [eShopOnContainers](https://github.com/dotnet-architecture/eShopOnContainers)，在这个示例项目中，微软通过它来为`Ordering API`、`Catalog API`、`Basket API` 等多个服务提供网关的功能。当时，博主并没有对它做深入的探索。此刻再度回想起来，大概是因为那个时候更迷恋领域驱动设计(DDD)的理念。直到最近这段时间，博主需要在一个项目中用到`Envoy`，终于决定花点时间来学习一下相关内容。所以，接下来这几篇博客，大体上会以记录我学习`Envoy`的历程为主。考虑到`Envoy`的配置项特别多，在写作过程中难免会出现纰漏，希望大家谅解。如对具体的配置项存在疑问，请以官方最新的 [文档](https://www.envoyproxy.io/docs/envoy/latest/) 为准，本文所用的示例代码已经上传至 [Github](https://hub.fastgit.org/Regularly-Archive/2021/tree/master/src/EnvoyGateway)，大家作为参考即可。对于今天这篇博客，我们来聊聊 ASP.NET Core 搭载 Envoy 实现微服务的反向代理 这个话题，或许你曾经接触过 [Nginx](https://www.nginx.com/) 或者 [Ocelot](https://github.com/ThreeMammals/Ocelot)，这次我们不妨来尝试一点新的东西，譬如，通过`Docker-Compose`来实现服务编排，如果对我说的这些东西感兴趣的话，请跟随我的脚步，一起来探索这广阔无垠的技术世界吧！

# 走近 Envoy

[Envoy](https://www.envoyproxy.io/) 官网对`Envoy`的定义是：

> Envoy 是一个开源边缘和服务代理，专为原生云应用设计。

而更进一步的定义是：

> Envoy 是专为大型现代服务导向架构设计的 L7 代理和通讯总线。

这两个定义依然让你感到云里雾里？没关系，请看下面这张图：

![Envoy架构图](https://i.loli.net/2021/07/02/k2DhXMudnibrzgt.png)

注：[图片来源](https://fuckcloudnative.io/envoy-handbook/docs/gettingstarted/architecture/)

相信从这张图中，大家多少能看到反向代理的身影，即下游客户端发起请求，`Envoy`对请求进行侦听(**Listeners**)，并按照路由转发请求到指定的集群(**Clusters**)。接下来，每一个集群可以配置多个终结点，`Envoy`按照指定的负载均衡算法来筛选终结点，而这些终结点则指向了具体的上游服务。例如，我们熟悉的 [Nginx](https://www.nginx.com/) ，使用`listen`关键字来指定侦听的端口，使用`location`关键字来指定路由，使用`proxy_pass`关键字来指定上游服务的地址。同样地，[Ocelot](https://github.com/ThreeMammals/Ocelot) 使用了类似的上下游(**Upstream**/**Downstream**)的概念，唯一的不同是，它的上下游的概念与这里是完全相反的。

你可能会说，这个`Envoy`看起来“平平无奇”嘛，简直就像是“平平无奇”的古天乐一般。事实上，`Envoy`强大的地方在于：

* 非侵入式的架构： 独立进程、对应用透明的`Sidecar`模式

![Envoy 的 Sidecar 模式](https://i.loli.net/2021/07/02/lMnPhZzBd38tpVF.png)

* L3/L4/L7 架构：`Envoy`同时支持 OSI 七层模型中的第三层(网络层, IP 协议)、第四层(传输层，TCP / UDP 协议)、第七层(应用层，HTTP 协议)
* 顶级 HTTP/2 支持： 视 `HTTP/2` 为一等公民，且可以在 `HTTP/2` 和 `HTTP/1.1`间相互转换
* gRPC 支持：`Envoy` 支持 `HTTP/2`，自然支持使用 `HTTP/2` 作为底层多路复用协议的 `gRPC`
* 服务发现和动态配置：与 `Nginx` 等代理的热加载不同，`Envoy` 可以通过 `API` 接口动态更新配置，无需重启代理。
* 特殊协议支持：Envoy 支持对特殊协议在 L7 进行嗅探和统计，包括：[MongoDB](https://www.envoyproxy.io/docs/envoy/latest/configuration/listeners/network_filters/mongo_proxy_filter#)、[DynamoDB](https://www.servicemesher.com/envoy/intro/arch_overview/dynamo.html#arch-overview-dynamo) 等。
* 可观测性：`Envoy` 内置 `stats` 模块，可以集成诸如 `prometheus/statsd` 等监控方案。还可以集成分布式追踪系统，对请求进行追踪。

# Envoy配置文件

`Envoy`通过配置文件来实现各种各样的功能，其完整的配置结构如下：

```json
{
  "node": "{...}",
  "static_resources": "{...}",
  "dynamic_resources": "{...}",
  "cluster_manager": "{...}",
  "hds_config": "{...}",
  "flags_path": "...",
  "stats_sinks": [],
  "stats_config": "{...}",
  "stats_flush_interval": "{...}",
  "watchdog": "{...}",
  "tracing": "{...}",
  "runtime": "{...}",
  "layered_runtime": "{...}",
  "admin": "{...}",
  "overload_manager": "{...}",
  "enable_dispatcher_stats": "...",
  "header_prefix": "...",
  "stats_server_version_override": "{...}",
  "use_tcp_for_dns_lookups": "..."
}
```

这里我们主要对侦听器(**Listeners**)、集群(**Clusters**) 和 管理(**Admin**)这三个常用的部分来进行说明。其中，(**Listeners**)、集群(**Clusters**) 均位于 `static_resources` 节点下，而 管理(**Admin**) 则有一个单独的`admin`节点。

## 侦听器(Listeners)

侦听器，顾名思义就是侦听一个或者多个端口：

```yaml
static_resources:
  listeners:
  - address:
      socket_address:
        address: 0.0.0.0
        port_value: 9090
```
在这里，它表示的是侦听`9090`这个端口，这里的`listeners`是一个数组，所以，你可以同时侦听多个端口。

### 过滤器(Filters)

我们知道，单单侦听一个或者多个端口，是无法完成一个`HTTP`请求的，因为它还不具备处理`HTTP`请求的能力。

![Envoy Filters 架构图](https://i.loli.net/2021/07/02/CQftjTErndyNh7q.png)

在 `Envoy` 中，这一工作由一个或者多个过滤器组成的过滤器链(**Filter Chains**) 来完成：

```yaml
static_resources:
  listeners:
  - address:
      socket_address:
        address: 0.0.0.0
        port_value: 9090
    filter_chains:
    - filters:
      - name: envoy.filters.network.http_connection_manager
        typed_config:
          "@type": type.googleapis.com/envoy.extensions.filters.network.http_connection_manager.v3.HttpConnectionManager
          codec_type: AUTO
          stat_prefix: ingress_http
          route_config:
            name: local_route
            virtual_hosts:
            - name: backend
              domains:
              - "*"
              routes:
              - match:
                  prefix: "/api/w"
                route:
                  auto_host_rewrite: true
                  prefix_rewrite: /Weather
                  cluster: weatherservice
              - match:
                  prefix: "/api/c"
                route:
                  auto_host_rewrite: true
                  prefix_rewrite: /City
                  cluster: cityservice
          http_filters:
          - name: envoy.filters.http.router
```

在这段配置中，`Http Connection Manager`表示的是位于 L3(**网络层**)/L4(**传输层**) 的过滤器，这个过滤器连接的下一个过滤器是`envoy.filters.http.router`，表示的是 L7(**应用层**) 的关于路由的过滤器。个人感觉，这和我们通常所说的中间件相当接近。注意到，我们在 L3/L4 这个层级上做了什么事情呢？其实应该是 TCP/IP 层面上请求转发，这里定义的路由规则如下：

* 当外部调用者访问`/api/w`时，请求会被转发到`WeatherService`。
* 当外部调用者访问`/api/c`时，请求会被转发到`CityService`。

## 集群(Clusters)

在过滤器部分，我们定义了路由，那么，请求的最终去向是哪里呢？这里 `Envoy` 将其称之为 集群：:

```yaml
static_resources:
  clusters:
  # City Service
  - name: cityservice
    connect_timeout: 0.25s
    type: STRICT_DNS
    lb_policy: ROUND_ROBIN
```
集群本身，其实只是一个名字，并没有实际的意义，真正工作的其实是指向上游服务的终结点，我们可以为每一个集群指定一个负载均衡策略，让它决定选择哪一个终结点来提供服务。

### 负载均衡(Load Assignment)

目前，`Envoy`支持以下负载均衡算法：
* ROUND_ROBIN：轮询
* LEAST_REQUEST：最少请求
* RING_HASH：哈希环
* RANDOM：随机
* MAGLEV：磁悬浮
* CLUSTER_PROVIDED

下面的示例展示了如何为某个集群配置负载均衡：

```yaml
static_resources:
  clusters:
  # Weather Service
  - name: weatherservice
    connect_timeout: 0.25s
    type: STRICT_DNS
    lb_policy: LEAST_REQUEST
    load_assignment:
      cluster_name: weatherservice
      endpoints:
      - lb_endpoints:
        - endpoint:
            address:
              socket_address:
                address: weatherservice1
                port_value: 80
        - endpoint:
            address:
              socket_address:
                address: weatherservice2
                port_value: 80
```
其中，`weatherservice1`和`weatherservice2`是同一个服务的两个容器实例，当我们使用`Docker-Compose`进行构建的时候，不需要显式地去指定每一个服务的IP地址，只要对应`docker-compose.yaml`文件中的服务名称即可。

## 管理(Admin)

管理(**Admin**)这块儿相对简单一点，主要用来指定`Envoy`的的管理接口的端口号、访问日志存储路径等等：

```yaml
admin:
  access_log_path: /tmp/admin_access.log
  address:
    socket_address: { address: 0.0.0.0, port_value: 9091 }
```

# 服务编排

好了，在正确配置`Envoy`以后，我们来考虑如何对这些服务进行编排，在本文的 [例子](https://hub.fastgit.org/Regularly-Archive/2021/tree/master/src/EnvoyGateway) 中，我们有两个后端服务，`WeatherService` 和 `CityService`，它们本质上是两个`ASP.NET Core`应用，我们希望通过`Envoy`来实现反向代理功能。这样做的好处是，后端服务的架构不会直接暴露给外部使用者。所以，你会注意到，在微服务架构的设计中，网关经常扮演着重要的角色。那么，如何对服务进行编排呢？这里我们使用`Docker-Compose`来完成这个工作：

```yaml
version: '3'
services:
  envoygateway:
    build: Envoy/
    ports:
      - "9090:9090"
      - "9091:9091"
    volumes:
      - ./Envoy/envoy.yaml:/etc/envoy/envoy.yaml
  cityservice:
    build: CityService/
    ports:
      - "8081:80"
    environment:
      ASPNETCORE_URLS: "http://+"
      ASPNETCORE_ENVIRONMENT: "Development"
  weatherservice:
    build: WeatherService/
    ports:
      - "8082:80"
    environment:
      ASPNETCORE_URLS: "http://+"
      ASPNETCORE_ENVIRONMENT: "Development"
```

可以注意到，这里需要部署3个服务，其中，`Envoy`负责监听`9090`端口，即对外的网关。而两个后端服务，`WeatherService` 和 `CityService`则被分别部署在`8082`和`8081`端口。这里最重要的是`envoy.yaml`这个配置文件，我们在上一节编写的配置文件会挂在到容器目录：`/etc/envoy/envoy.yaml`。`Envoy`将如何使用这个配置文件呢？事实上，这个`Dockerfile`是这样编写的：

```dockerfile
FROM envoyproxy/envoy-alpine:v1.16-latest
COPY ./envoy.yaml /etc/envoy.yaml
RUN chmod go+r /etc/envoy.yaml
CMD ["/usr/local/bin/envoy", "-c", "/etc/envoy.yaml", "--service-cluster", "reverse-proxy"]
```

除此之外，Envoy通过`9091`端口提供管理功能，我们可以通过这个端口来获得集群、请求、统计等信息，这一特性我们将会在接下来的文章里用到：

![Envoy 管理界面功能一览](https://i.loli.net/2021/07/02/1OlNJ7um6BnLFeb.png)

这里，想分享一个关于`Envoy`的小技巧，当我们在指定集群的地址时，可以使用`docker-compose.yaml`中定义的服务的名称，这会比填入一个固定的`IP`地址要更优雅一点，理由非常简单，我们不希望每次都来维护这个地址。

```yaml
 # Weather Service
  - name: weatherservice
    connect_timeout: 0.25s
    type: STRICT_DNS
    lb_policy: ROUND_ROBIN
    load_assignment:
      cluster_name: weatherservice
      endpoints:
      - lb_endpoints:
        - endpoint:
            address:
              socket_address:
                # 建议使用 docker-compose.yaml 文件中对应的服务名称来代替IP地址
                address: weatherservice
                port_value: 80
```

接下来，如果每一个服务的`Dockerfile`都编写正确的话，我们就可以通过`docker compose up`命令启动这一组服务，通过命令行下打印出来的信息，我们可以确认，基于`Envoy`的网关服务、两个基于`ASP.NET Core`的后端服务都已经成功运行起来：

![在 Docker-Compose 中成功启动服务](https://i.loli.net/2021/07/02/KMo4dn17m9p8NSg.png)

还记得我们的路由规则是是如何定义的吗？

* 当外部调用者访问`/api/w`时，请求会被转发到`WeatherService`。
* 当外部调用者访问`/api/c`时，请求会被转发到`CityService`。

实际的情况如何呢？我们不妨来验证一下：

![通过 Envoy 调用 WeatcherService ](https://i.loli.net/2021/07/02/YX4VywtkOCJ2rSI.png)

可以注意到，不管是浏览器返回的结果，还是容器内部输出的日志，都表明请求确实被转发到对应的服务上面去了，这说明我们设计的网关已经生效。至此，我们实现了基于`Envoy`的反向代理功能，有没有觉得比`Nginx`要简单一点？重要的是，基于`Docker-Compose`的服务编排使用起来真的舒适度爆棚，这意味着你会有更多的属于程序员的贤者时间。前段时间热映的电视剧《觉醒时代》，鲁迅先生写完《狂人日记》后那一滴眼泪令人动容。也许，这种如匠人一般反复雕琢、臻于完美的心境是互通的，即使人类的悲欢并不相通，对美和极致的追求竟然出奇的相似。

# 本文小结

本文主要介绍了 ASP.NET Core 搭载 [Envoy](https://www.envoyproxy.io/) 实现反向代理这一过程。对于 `Envoy`，有两个重要的定义：**第一、Envoy 是一个开源边缘和服务代理，专为原生云应用设计。第二、Envoy 是专为大型现代服务导向架构设计的 L7 代理和通讯总线**。相比 [Nginx](https://www.nginx.com/)  和 [Ocelot](https://github.com/ThreeMammals/Ocelot) ，Envoy 提供了 `L7` 级别的代理服务，支持 `HTTP/2` 和 `gRPC`，无侵入式的`Sidecar`模式可以提供与应用进程完全隔离的代理服务。接下来，博主对 `Envoy` 配置文件的结构及主要的配置项进行了说明，对于常见的 API 网关，我们应该重点关注侦听器(**Listeners**) 和 集群(**Clusters**)。最终，我们结合`Docker-Compose`对服务进行了编排，并由此构建出了一个基本的反向代理的方案。本文的源代码已托管至 [Github](https://hub.fastgit.org/Regularly-Archive/2021/tree/master/src/EnvoyGateway) ，大家可以在此基础上做进一步的探索。好了，以上就是这篇博客的的全部内容啦，欢迎大家就本文中提出的方案、代码等进行讨论，如果大家有任何意见或者建议，欢迎在评论区进行留言，谢谢大家！

# 参考文档

* [Envoy中文指南](https://fuckcloudnative.io/envoy-handbook/)
* [Envoy官方文档](https://www.envoyproxy.io/docs/envoy/latest/)
* [eShopOnContainers 知多少[12]：Envoy Gateways](https://www.cnblogs.com/sheng-jie/p/use-envoy-proxy-as-apigateways-in-eshoponcontainers.html)
