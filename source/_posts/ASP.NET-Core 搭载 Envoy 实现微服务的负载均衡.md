---
toc: true
title: ASP.NET Core 搭载 Envoy 实现微服务的负载均衡
categories:
  - 编程语言
tags:
  - Envoy
  - 微服务
  - 负载均衡
  - 熵增定律
copyright: true
abbrlink: 3599307336
date: 2021-07-05 22:49:47
---

如果说，我们一定要找出一个词来形容这纷繁复杂的世界，我希望它会是熵。有人说，熵增定律是宇宙中最绝望的定律，**所谓熵，即是指事物混乱或者无序的程度。在一个孤立系统下，熵是不断在增加的，当熵达到最大值时，系统就会出现严重混乱，直至最终走向死亡**。从某种意义上来讲，它揭示了事物结构衰退的必然性，甚至于我们的人生，本来就是一场对抗熵增的旅程。熵增的不可逆性，正如时光无法倒流一般，古人说，“覆水难收”正是这个道理。同样地，当我们开始讨论微服务的划分/编写/治理的时候，当我们使用服务网格来定义微服务架构的时候……我们是否有意或者无意的增加了系统中的熵呢？**一个孤立的系统尚且会因为熵增而最终走向死亡，更何况是相互影响和制约的复杂系统呢？**现代互联网企业都在追求4个9(即99.99%)的高可用，这意味着年平均停机时长只有52.56分钟。在此之前。我们介绍过重试和熔断这两种故障转移的策略，而今天我们来介绍一种更朴素的策略：负载均衡。

# 什么是负载均衡

> 负载均衡，即`Load Banlancing`，是一种计算机技术，用来在多个计算机(计算机集群)、网络连接、CPU、磁盘驱动器或其它资源中分配负载，以达到**最优化资源使用、最大化吞吐率、最小化响应时间、避免过载的目的**。

我们可以注意到，在这个定义中，使用负载均衡技术的直接原因是**避免过载**，而根本原因则是为了**优化资源使用**，确保**最大吞吐量**、**最小响应时间**。所以，这本质上是一个局部最优解的问题，而具体的手段就是"多个"。有人说，技术世界不过是真实世界的一个镜像，联系生活中实际的案例，我们发现负载均衡比比皆是。譬如车站在面对春运高峰时增加售票窗口，银行通过多个业务窗口来为客户办理业务……等等。这样做的好处显而易见，可以大幅度地减少排队时间，增加"窗口"这个行为，在技术领域我们将其称为：**水平扩展**，因为有多个"窗口"，发生单点故障的概率就会大大降低，而这正是现在软件追求的三"高"：高性能、高可用、高并发。

![银行柜员窗口示意图](https://i.loli.net/2021/07/05/jymw8KCeEgROcZN.png)

每次坐地铁经过小寨，时常听到地铁工作人员举着喇叭引导人们往不同的出口方向走动。此时，工作人员就是一个负载均衡器，它要做的就是避免某一个出口人流量过载。**从熵的角度来看，人流量过载，意味着无序/混乱状态加剧，现代社会通过道德和法律来对抗熵增，人类个体通过自律来对抗熵增。**有时候，我会忍不住去想，大人与小孩儿愈发内卷的恶性竞争，除了给这个世界带来更多的熵以外，还能带来什么？**如果参考社会达尔文主义的理论，在这个弱肉强食的世界里，增加熵是人为的选择，而同样的，你亦可以选择"躺平"。**

![负载均衡器示意图](https://i.loli.net/2021/07/05/hIAUw8JHkjWnxm6.png)

OK，将思绪拉回到负载均衡，它所做的事情，本质上就是控制信息或者说流量流动的方向。一个网站，以集群的方式对外提供服务，你只需要输入一个域名，它就可以把请求分发到不同的机器上面去，而这就是所谓的负载均衡。目前，负载均衡器从种类上可以分为：基于`DNS`、基于`MAC`地址(二层)、基于`IP`(三层)、基于`IP`和`Port`(四层)、基于`HTTP`(七层)。

![OSI七层模型与TCP/IP五层模型](https://i.loli.net/2021/07/04/giY1R8PVZB9JdWQ.jpg)

譬如，博主曾经参与过伊利的项目，它们使用的就是一个四层的负载均衡器：F5。而像更常见`Nginx`、`HAProxy`，基本都是四层和七层的负载均衡器，而`Envoy`就厉害了，它可以同时支持三/四/七层。负载均衡器需要配合负载均衡算法来使用，典型的算法有：**轮询法**、**随机法**、**哈希法**、**最小连接数法**等等，而这些算法都可以结合加权算法引出新的变式，这里就不再一一列举啦。

# Envoy中的负载均衡

通过上一篇博客，我们已经了解到，`Envoy`中一个`HTTP`请求的走向，大致会经历：客户端、侦听器(**Listeners**)、集群(**Clusters**)、终结点(**Endpoints**)、服务(**ervices**)这样几个阶段。其中，一个集群可以有多个终结点(**Endpoints**)。所以，这里天然地就存在着负载均衡的设计。因为，负载均衡本质上就是告诉集群，它应该选择哪一个终结点(**Endpoints**)来提供服务。而之所以我们需要负载均衡，一个核心的原因，其实是因为我们选择了分布式。

![Envoy架构图：负载均衡器连接集群和服务](https://i.loli.net/2021/07/02/k2DhXMudnibrzgt.png)

如果类比`RabbitMQ`、`Kafka`和`Redis`，你就会发现，这些产品中或多或少地都会涉及到主(**Leader**)、从(**Follower**)以及推举Leader的实现，我个人更愿意将其看作是更广义的负载均衡。最直观的，它可以分担流量，简称**分流**，不至于让某一台服务器满负荷做运行。其次，它可以作为故障转移的一种方案，**人生在世，多一个B计划，就多一种选择。同样地，多一台服务器，就多一分底气**。最后，它可以指导某一个产品或者功能的推广，通过给服务器设置不同的权重，在必要的时候，将流量局部地导入某一个环境，腾讯和阿里这样的大厂，经常利用这种方式来做**灰度测试**。

`Envoy`中支持常用的负载均衡算法，譬如：ROUND_ROBIN(轮询)、LEAST_REQUEST(最少请求)、RING_HASH(哈希环)、RANDOM(随机)、MAGLEV(磁悬浮)、CLUSTER_PROVIDED等等。因为一个集群下可以有多个终结点，所以，在`Envoy`中配置负载均衡，本质上就是在集群下面增加终结点，而每个终结点则会对应一个服务，特殊的点在于，这些服务可能是通过同一个`Dockerfile`或者`Docker`镜像来构建的。所以，一旦理解了这一点，`Envoy`的负载均衡就再没有什么神秘的地方。例如，下面的代码片段展示了，如何为`WeatherService`这个集群应用负载均衡：

```yaml
  clusters:
  # Weather Service
  - name: weatherservice
    connect_timeout: 0.25s
    type: STRICT_DNS
    # ROUND_ROBIN(轮询）
    # LEAST_REQUEST(最少请求)
    # RING_HASH(哈希环)
    # RANDOM(随机)
    # MAGLEV(磁悬浮)
    # CLUSTER_PROVIDED
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

是不是觉得特别简单？我想说，也许是`Envoy`更符合人的直观感受一些，理解起来本身没有太大的心智负担。最近看到一个缓存设计，居然还要依赖`Kafka`，使用者为了使用缓存这个功能，就必须先实现三个丑陋的委托，这就是所谓的心智负担，违背人类的直觉，使用缓存为什么要了解`Kafka`？到这里，你大概就能了解利用`Envoy`实现负载均衡的思路，首先是用同一个`Dockerfile`或者`Docker`镜像启动多个不同容器(服务)，然后将指定集群下面的终结点指定不同的服务，再告诉集群要用哪一种负载均衡策略即可。

# 邂逅 ASP.NET Core

OK，说了这么多，这里我们还是用`ASP.NET Core`写一个例子。可以预见到的是，我们需要一个`Envoy`网关，一个`ASP.NET Core`的服务。这里，我们还是用`Docker-Compose`来编排这些服务，下面是对应的`docker-compose.yaml`文件：

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
  weatherservice1:
    build: WeatherService/
    ports:
      - "8082:80"
    environment:
      ASPNETCORE_URLS: "http://+"
      ASPNETCORE_ENVIRONMENT: "Development"
  weatherservice2:
    build: WeatherService/
    ports:
      - "8084:80"
    environment:
      ASPNETCORE_URLS: "http://+"
      ASPNETCORE_ENVIRONMENT: "Development"  
```

而对于`Envoy`来说，主要是维护集群下的终结点信息。其实，这段配置在本文的上一节就出现过啦。故而，这里我们不再做更多的解释：

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
          http_filters:
          - name: envoy.filters.http.router

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

admin:
  access_log_path: /tmp/admin_access.log
  address:
    socket_address: { address: 0.0.0.0, port_value: 9091 }
```

使用`docker compose up`启动容器，我们可以注意到熟悉的`ASP.NET Core`的身影，这意味着，我们需要的服务都成功地跑起来了。简单调用下API看看，果然，可以正确地返回结果呢(逃……果然，我是一个喜新厌旧的人，自打用了`Encoy`以后，再不想用`Nginx`来做类似的事情(逃……

![通过管理接口查看集群的请求情况](https://i.loli.net/2021/07/04/lBIAyPZnSxiD3M8.png)

好了，如何验证我们选择的负载均衡策略呢？这是一个问题。不知道大家还记不记得`Envoy`的管理接口，它里面可以统计请求的次数，所以，我们只要看看两个服务各自请求了多少次里有好啦！这里以`RANDON`这个策略为例：

![两个实例拥有不同的请求次数](https://i.loli.net/2021/07/04/1U8RgZxaVcOFiXK.png)

可以注意到，两个的请求次数果然是随机的呢？而如果我们换成是`ROUND_ROBIN`，你就会发现这两个数值一前一后相互追赶。选择哪一种负载均衡策略，这个按大家实际的场景去决定就好。我倒觉得，按最少请求数的策略会好一点。虽然计算机永远不知疲倦地接收人们的指令，可考虑能者多劳这种人类世界里的策略，本身充满道德绑架的意味，使用负载均衡，站在计算机的角度来看，这是避免计算机内卷的一种方案。所以啊，老板们，请不要逮着一个老实人就拼了命的剥削，多学学负载均衡算法，**卓别林心目中的摩登时代，我一点都不期待，技术世界总告诉我们要严谨、冷静，可充满人情味的世界，同样值得你去热爱啊。**

# 本文小结

本文结合物理学中的熵增定律引出了负载均衡这个话题，而**负载均衡的本质，就是在多个计算机(计算机集群)、网络连接、CPU、磁盘驱动器或其它资源中分配负载，以达到最优化资源使用、最大化吞吐率、最小化响应时间、避免过载的目的。**对于这一点，我们可以结合现实生活中的"窗口"排队来理解。**负载均衡可以和水平扩展完美结合，通过降低单点的故障率，来达到提升整个系统可用性的目的**。接下来，我们介绍了常见的负载均衡器分类及其算法，`Envoy`中的负载均衡配置，并结合`ASP.NET Core`编写了一个实际的案例。好了，以上就是这篇博客的全部内容啦，如果大家对于熵增定律或者负载均衡器有任何的看法，欢迎大家在评论区留言，谢谢大家！


