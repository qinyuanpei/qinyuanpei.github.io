---
toc: true
title: Envoy 集成 Jaeger 实现分布式链路跟踪
categories:
  - 编程语言
tags:
  - Envoy
  - Jaeger
  - Tracing
copyright: true
abbrlink: 768684858
date: 2022-01-14 16:46:23
---
当我们的应用架构，从单体系统演变为微服务时，一个永远不可能回避的现实是，业务逻辑会被拆分到不同的服务中。因此，微服务实际就是不同服务间的互相请求和调用。更重要的是，随着容器/虚拟化技术的发展，传统的物理服务器开始淡出我们的视野，软件被大量地部署在云服务器或者虚拟资源上。在这种情况下，分布式环境中的运维和诊断变得越来越复杂。如果按照按照功能来划分，目前主要有 Logging、Metrics 和 Tracing 三个方向，如下图所示，可以注意到，这三个方向上彼此都有交叉、重叠的部分。在我过去的博客里，我分享过关于 [ELK](/posts/3687594958) 和 [Prometheus](1519021197) 的内容，可以粗略地认为，这是对 Logging 和 Metrics 这两个方向的涉猎。所以，这篇文章我想和大家分享是 Tracing，即分布式跟踪，本文会结合 Envoy、Jaeger 以及 .NET Core 来实现一个分布式链路跟踪的案例，希望能带给大家一点 Amazing 的东西。

![可观测性：Metrics、Tracing & Logging](Obserability_Metrics_Tracing_Logging.jpg)

# 分布式跟踪

如果要追溯分布式跟踪的起源，我想，Google 的这篇名为 [《Dapper, a Large-Scale Distributed Systems Tracing Infrastructure》](https://dirtysalt.github.io/html/dapper.html) 的论文功不可没，因为后来主流的分布式跟踪系统，譬如 [Zipkin](https://zipkin.io/)、[Jeager](https://www.jaegertracing.io/)、[Skywalking](https://skywalking.apache.org/)、[LightStep](https://lightstep.com)……等等，均以这篇论文作为理论基础，它们在功能上或许存在差异，原理上则是一脉相承，一个典型的分布式跟踪系统，大体上可以分为代码埋点、数据存储和查询展示三个步骤，如下图所示，Tracing 系统可以展示出服务在时序上的调用层级，这对于我们分析微服务系统中的调用关系会非常有用。

![分布式跟踪系统基本原理](Basic-Principles-Of-Distributed-Tracking-System.png)

一个非常容易想到的思路是，我们在前端发出的请求的时候，动态生成一个唯一的 `x-request-id`，并保证它可以传递到与之交互的所有服务中去，那么，此时系统产生的日志中就会携带这一信息，只要以此作为关键字，就可以检索到当前请求的所有日志。这的确是个不错的方案，但它无法告诉你每个调用完成的先后顺序，以及每个调用花费了多少时间。基于这样的想法，人们在这上面传递了更多的信息(`Tag`)，使得它可以表达层级关系、调用时长等等的特征。如图所示，这是一个由 `Jaeger` 产生的跟踪信息，我们从中甚至可以知道请求由哪台服务器处理，以及上/下游集群信息等等：

![通过 Jaeger 收集 gRPC 请求信息](Jaeger-Works-On-gRPC.png)

目前，为了统一不同 Tracing 系统在 API、数据格式等方面上的差异，社区主导并产生了 [OpenTracing](https://opentracing.io/) 规范，在这个 [规范](https://github.com/opentracing/specification/blob/master/specification.md) 中，一个 Trace，即调用链，是由多个 `Span` 组成的有向无环图，而每个 `Span` 则可以含有多个键值对组成的 Tag。如图所示，下面是 [OpenTracing](https://opentracing.io/) 规范的一个简单示意图，此时，图中一共有 8 个 `Span`，其中 `Span A` 是根节点，`Span C` 是 `Span A` 的子节点， `Span G` 和  `Span F` 之间没有通过任何一个子节点连接，称为 `FollowsFrom`。

```
        [Span A]  ←←←(the root span)
            |
     +------+------+
     |             |
 [Span B]      [Span C] ←←←(Span C is a `ChildOf` Span A)
     |             |
 [Span D]      +---+-------+
               |           |
           [Span E]    [Span F] >>> [Span G] >>> [Span H]
                                       ↑
                                       ↑
                                       ↑
                         (Span G `FollowsFrom` Span F)
```

事实上，我们上面提到的 [Zipkin](https://zipkin.io/) 和 [Jeager](https://www.jaegertracing.io/) 都兼容这一规范，这使得我们可以更加灵活和自由地更换 Tracing 系统。除了 [OpenTracing](https://opentracing.io/) 规范，目前，[OpenTelemetry](https://opentelemetry.io/) 在考虑统一 Logging、Metrics 和 Tracing，即我们通常所说的 APM，如果大家对这个感兴趣，可以做更进一步的了解。
# Envoy & Jaeger

目前，主流的服务网格平台如 [Istio](https://istio.io/latest)，选择 [Envoy](https://www.envoyproxy.io/) 作为其数据平面的核心组件。通俗地来讲，Envoy 主要是作为代理层来调节服务网格中所有服务的进/出站流量，它可以实现诸如负载均衡、服务发现、流量转移、速率限制、可观测性等等的功能。考虑到不同的服务都可以通过 `Gateway` 或者 `Sidecar` 来互相访问，我们更希望通过 Envoy 这个代理层来实现分布式跟踪，而不是在每个应用内都去集成 SDK，这正是服务网络区别于传统微服务的地方，即微服务治理需要的各种能力，逐步下沉到基础设施层。如果你接触过微软的 [Dpar](https://docs.microsoft.com/zh-cn/dotnet/architecture/dapr-for-net-developers/getting-started)，大概就能体会到我这里描述的这种变化。

![Envoy 在 Istio 中扮演着重要角色](Manaing-Microservice-With-Istio.png)

事实上，Envoy 提供了入口来接入不同的 Tracing 系统，以 [Zipkin](https://zipkin.io/) 或者 [Jeager](https://www.jaegertracing.io/) 为例，除了前面提到的 `x-request-id`，它可以帮我们生成类似 `x-b3-traceid`、`x-b3-spanid` 等等的请求头。参照 [官方文档](https://www.envoyproxy.io/docs/envoy/latest/intro/arch_overview/observability/tracing#arch-overview-tracing)，它大体上提供了下面 3 种策略来支撑系统范围内的跟踪：


* 生成 `UUID` ：Envoy 会在需要的时候生成 `UUID`，并操作名为 `x-request-id` 的 HTTP 头部，应用可以转发这个 HTTP 头部用于统一的记录和跟踪。
* 集成外部跟踪服务：Envoy 支持可插拔的外部跟踪可视化服务，例如 LightStep、Zipkin 或者 Zipkin 兼容的后端（比如说 Jaeger）等等。
* 客户端跟踪 ID 连接：`x-client-trace-id` 这个 HTTP 头部可以用来把不信任的请求 ID 连接到受信的 `x-request-id` HTTP 头部上。

这意味着，我们可以从客户端或者由 Envoy 来产生一个 `x-request-id`，只要应用转发这个 `x-request-id` 或者 外部跟踪系统需要的 HTTP 头部，Envoy 就可以帮我们完成把这些跟踪信息告诉这些外部跟踪系统，甚至在 `SIdecar` 模式下这一切都是自动完成的。我在写这篇博客时发现，官方还是比较推崇 `Sidecar` 模式，即一个服务就是一个 `Pod`，每个 `Pod` 里自带一个 Envoy 作为代理，对于 `Sidecar` 模式而言，它的分布式跟踪呈现出下面这样的结构，如果你认真阅读过官方的文档和示例，就会发现其 [示例](https://github.com/envoyproxy/envoy/tree/main/examples) 基本都是这种结构：

![Sidecar 模式下的分布式跟踪示意图](Envoy-Tracing-Sidecar.drawio.png)

考虑到，2022 年还有没有用上 `K8S` 的人，以及 [Catcher Wong](https://www.cnblogs.com/catcher1994/) 大佬反映 `Sidecar` 模式比较浪费资源，这里我们还是用 `Gateway` 模式来实现，譬如我们有两个服务，订单服务(`OrderSevice`) 和 支付服务(`PaymentService`)，它们都由同一个 Envoy 来代理，当我们在订单服务中调用支付服务时，就会产生一条调用链。对于大多数的微服务而言，从它被拆分地那一刻起，就不可避免地走向了像蜘蛛网一般错综复杂的结局，此时，它的分布式跟踪呈现出下面的结构：

![Gateway 模式下的分布式跟踪示意图](Envoy-Tracing-Gateway.drawio.png)

如果从代码侵入角度来审视这个问题，`Sidecar` 模式，每个服务都由 Envoy 去生成或者是设置一系列相关的请求头；而如果采取 `Gateway` 模式，当你在订单服务里调用支付服务时，无论你使用 `HttpClient` 还是 `gRPC`，你都需要确保这一系列的请求头能传递下去，这意味着我们要写一点无关紧要的代码，这样看起来前者更好一点，不是吗？可惜，合适和正确，就像鱼和熊掌一样，永远不可兼得。

![Span 模型示意图](Jaeger-Span-Model.png)

关于 Jeager，这是一个由 Uber 开发的、受 Dapper 和 Zipkin 启发的分布式跟踪系统，它主要适用于：分布式跟踪信息传递、分布式事务监控、问题分析、服务依赖性分析、性能优化这些场景，因为它兼容 OpenTracing 标准，所以 `Span` 这个术语对它来说依然使用，什么是 `Span` 呢？它是一个跟踪的最小逻辑单位，可以记录操作名，操作开始时间 和 操作耗时，下面是 Jaeger 的架构示意图，大家可以混个眼熟：

![Jaeger 的架构示意图](Jaeger-Architecture-v1.png)

# 第一个实例

OK，现在来分享本文的第一个示例，如前文所述，我们要实现的是一个 `Gateway` 模式下的请求跟踪。为此，我们准备了两个 ASP.NET Core 项目，分别来模拟订单服务(`OrderService`) 和 支付服务(`PaymentService`)，当我们通过 Envoy 访问 `OrderService` 的时候，会在其内部访问 `PaymentService`，以此来验证 Envoy 能否帮我们找到这条调用链。首先，我们来编写 `OrderService`，代码非常简单，从 HTTP 请求头中拿到 Jeager 需要的字段，并在调用 `OrderService` 的时候传递这些字段：

```csharp
[HttpPost]
public async Task<IActionResult> Post([FromBody] OrderInfo orderInfo)
{
  var paymentInfo = new PaymentInfo()
  {
    OrderId = orderInfo.OrderId,
    PaymentId = Guid.NewGuid().ToString("N"),
    Remark = orderInfo.Remark,
  };

  // 设置请求头
  _httpClient.DefaultRequestHeaders.Add("x-request-id", Request.Headers["x-request-id"].ToString());
  _httpClient.DefaultRequestHeaders.Add("x-b3-traceid", Request.Headers["x-b3-traceid"].ToString());
  _httpClient.DefaultRequestHeaders.Add("x-b3-spanid", Request.Headers["x-b3-spanid"].ToString());
  _httpClient.DefaultRequestHeaders.Add("x-b3-parentspanid", Request.Headers["x-b3-parentspanid"].ToString());
  _httpClient.DefaultRequestHeaders.Add("x-b3-sampled", Request.Headers["x-b3-sampled"].ToString());
  _httpClient.DefaultRequestHeaders.Add("x-b3-flags", Request.Headers["x-b3-flags"].ToString());
  _httpClient.DefaultRequestHeaders.Add("x-ot-span-context", Request.Headers["x-ot-span-context"].ToString());

  // 调用/Payment接口
  var content = new StringContent(JsonConvert.SerializeObject(paymentInfo), Encoding.UTF8, "application/json");
  var response = await _httpClient.PostAsync("/Payment", content);

  var result = response.IsSuccessStatusCode ? "成功" : "失败";
  return new JsonResult(new { Msg = $"订单创建{result}" });
}
```

接下来，`PaymentService` 就会变得非常简单，因为我们不会真的去对接一个支付系统，所以，就简单意思一下好啦！

```csharp
 [HttpPost]
public IActionResult Post([FromBody] PaymentInfo paymentInfo)
{
  var requestId = Request.Headers["x-request-id"].ToString();
  return new JsonResult(new { Msg = $"支付成功, 流水号：{requestId}" });
}
```

服务编写好以后，按照惯例，我们使用 `docker-compose.yaml` 文件来进行编排，除了 `OrderService` 和 `PaymentService`，我们还需要 `Envoy` 和 `Jeager`，即至少需要四个服务：


```yaml
version: '3'
services:
  envoy_gateway:
    build: Envoy/
    ports:
      - "9090:9090"
      - "9091:9091"
    volumes:
      - "./Envoy/envoy.yaml:/etc/envoy/envoy.yaml"
      - "./Envoy/logs/:/etc/envoy/logs/"
  order_service:
    build: OrderService/
    ports:
      - "8081:80"
    environment:
      ASPNETCORE_URLS: "http://+"
  payment_service:
    build: PaymentService/
    ports:
      - "8082:80"
    environment:
      ASPNETCORE_URLS: "http://+"
  jaeger:
    image: jaegertracing/all-in-one
    environment:
    - COLLECTOR_ZIPKIN_HOST_PORT=9411
    ports:
    - "9411:9411"
    - "16686:16686"
```

此时，重头戏终于来了，Envoy 是如何连接外部跟踪系统的呢？我们可以设置 `HttpConnectionManager` 这个过滤器下的 `tracing` 字段，这里我们选择 `ZipkinConfig` 这个类型，因为 Jaeger 完全兼容 Zipkin，所以，我们可以直接使用这个 Provider。

```yaml
    filter_chains:
    - filters:
      - name: envoy.filters.network.http_connection_manager
        typed_config:
          "@type": type.googleapis.com/envoy.extensions.filters.network.http_connection_manager.v3.HttpConnectionManager
          generate_request_id: true
          tracing:
            provider:
              name: envoy.tracers.zipkin
              typed_config:
                "@type": type.googleapis.com/envoy.config.trace.v3.ZipkinConfig
                collector_cluster: jaeger
                collector_endpoint: "/api/v2/spans"
                collector_endpoint_version: HTTP_JSO
```

基本上，只要是官方支持的 Provider，我们都可以照猫画虎接入进来，当然每一种 Provider 的配置项可能会不一样，这里我们唯一要注意的是 `collector_cluster`, 它表示的是指向 Jeager 服务器的一个 Cluster，这意味着我们要为它单独定义一个 Cluster :

```yaml
  clusters:
  - name: jaeger
    type: STRICT_DNS
    connect_timeout: 0.25s
    lb_policy: ROUND_ROBIN
    load_assignment:
      cluster_name: jaeger
      endpoints:
      - lb_endpoints:
        - endpoint:
            address:
              socket_address:
                address: jaeger
                port_value: 9411
```

还记得 Envoy 支撑系统内的分布式跟踪的三个支撑策略是什么吗？显然，我们恶意通过 `generate_request_id` 字段来控制 Envoy 生成作用于 `x-request-id` 的 `UUID`，我们希望用户从 前端 或者 cURL 中发送的请求，都能自动地带上 `x-request-id` 请求头，所以，我们这里将其设为 `true`，这意味着，从现在开始，我们的请求有了这样一个 `x-request-id`， 其实，如果不考虑 Jeager 的话，我们请求已经可以实现跟踪了，只要后续的请求都像我这里一样传递 `x-request-id` 即可。原因我们已经在前面说过，此时，这些请求没有一个上下文的概念，更不要说要理清楚其中的调用层级，所以，接下来，我们还要做一点微不足道的工作：

```yaml
            virtual_hosts:
            - name: backend
              domains:
              - "*"
              routes:
              - match:
                  prefix: "/Payment"
                route:
                  auto_host_rewrite: true
                  prefix_rewrite: /api/Payment
                  cluster: payment_service
                decorator:
                  operation: PaymentService
              - match:
                  prefix: "/Order"
                route:
                  auto_host_rewrite: true
                  prefix_rewrite: /api/Order
                  cluster: order_service
                decorator:
                  operation: OrderService
```

如上所示，如果我们希望 Envoy 能记录我们的请求，那么，我们的请求必须要从它这里经过，这听起来像一句废话，可是在我调用 `PaymentService`经确保我的请求是从 `/Payment` 这个路由上发起。默认情况下，在生成 `Span` 的时候，Envoy 会使用 `--service-cluster` 这个参数来作为 `Span` 的名称，这个参数通常写在 Envoy 的启动命令里，在这个示例中，它的取值是 `reverse-proxy`。仔细一想，会觉得哪里不太对，这样一来，所以的 `Span` 不就是同一个名字了吗？事实上，一开始我做实验的时候，确实是这个结果。解决方是设置一个 `operation`。此时，如果我们通过 `Postman` 访问订单接口 `/Order`，不出意外的话，我们会收到订单创建成功的结果，在浏览器里输入`http://localhost:16686`，我们来看看 Jeager 都收集到了哪些信息：

![JeagerUI 数据查询](Envoy-JeagerUI-01.png)

从图中我们可以非常容易地识别出 Service 和 Operation 在 Envoy 中分别对应着什么，我们注意到这里检索到了三个 Span，因为博主后来又加了一个 `EchoService`，从这里我们能看到它整个过程从何时开始，经过多长时间以后结束。如哦我们点击它，会看到更加详细的说明，如下图所示：

![JeagerUI 数据展示](Envoy-JeagerUI-02.png)

显然，这个调用关系是符合我们预期的，即客户端调用了`OrderService`，`OrderService`调用了`PaymentService`，对于每一次调用，我们均可以从 Span 的 Tag 中获得更多信息，文章中的第三张图，实际上就是出自这里，有了这些信息以后，我们排查或者分析微服务中的问题，是不是感觉容易了很多呢？结合 ELK，你可以知道要去找哪里的日志，而这些正是分布式跟踪的意义所在！

![通过 Jaeger 收集 gRPC 请求信息](Jaeger-Works-On-gRPC.png)

好了，到这里为止，关于 Envoy 在分布式跟踪上的探索，终于可以告一段落，完整的项目文件我已经放在 [Github](https://github.com/Regularly-Archive/2022/tree/master/src/EnvoyTrace) 上供大家参考，谢谢大家！

# 本文小结

可观测性(Logging、Metrics & Tracing) 是当下微服务中重要的一个组成部分，从 ELk 收集日志，到 Prometheus 监控指标， 再到 Jeager 跟踪调用链，我们看到了一种完全不同于单体系统中打断点、单步调试的诊断思路，这是否说明，微服务的治理永远是一个绕不过去的话题，我一直在想，是不是我们有时候太在乎编写服务这件事情了？我们写了那么多的代码，最终是依靠别人喊一嗓子“接口报错”这种相当原始的“人治”来管理，难道不觉得惭愧且对不起这个世界吗？明明我们这个社会都在提倡“法治”。诚然，推崇法家的商君，最后等来的是一次车裂。技术革新步履不停，到底是技术远远达不到人类的要求，还是因为我们无知，诸如相对论、黑洞、量子力学、黎曼猜想、二向箔......都不曾窥见天空的一角，却自以为能掌控一切，就像你能操作计算机，并不是因为你比它聪明，而是它让你显得那么聪明。这篇文章里的做法同样算不上聪明，可能写这篇文章我原本就不是一个聪明的人，每当某种纠缠不清、模棱两可的思绪涌上心头的时候，果然程序员的生涯让我失去了对混乱的耐心，我很想对着这团混乱说一声：
```
Are you paying attention? 
Good. If you’re not listening carefully, you will miss things.
```
