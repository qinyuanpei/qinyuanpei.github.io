---
toc: true
title: ASP.NET Core 搭载 Envoy 实现 gRPC 服务代理
categories:
  - 编程语言
tags:
  - Envoy
  - 微服务
  - gRPC
  - RESTful
copyright: true
abbrlink: 3942175942
date: 2021-08-08 22:49:47
---
在构建以 gRPC 为核心的微服务架构的过程中，博主曾经写过一篇名为 [ASP.NET Core gRPC 打通前端世界的尝试](https://blog.yuanpei.me/posts/2167892202/) 的文章，主要是希望打通 gRPC 和 前端这样两个异次元世界，因为无论我们构建出怎样高大上的微服务架构，最终落地的时候，我们还是要面对当下前后端分离的浪潮。所以，在那篇文章中，博主向大家介绍过 gRPC-Web 、gRPC-Gateway 、封装 API 、[编写中间件](https://github.com/qinyuanpei/Grpc.Gateway) 这样四种方案。我个人当时更喜欢编写中间件这种方案，甚至后来博主进一步实现了 gRPC 的 “扫描” 功能。

当时，博主曾模糊地提到过，Envoy 可以提供容器级别的某种实现，这主要是指 Envoy 独有的 [gRPC-JSON Transcoder](https://www.envoyproxy.io/docs/envoy/latest/configuration/http/http_filters/grpc_json_transcoder_filter) 功能。考虑到 Envoy 是一个同时支持 HTTP/1.1 和 HTTP/2 的代理软件，所以，它天然地支持基于 HTTP/2 实现的 gRPC。所谓 gRPC-JSON Transcoder，其实指 Envoy 充当了 JSON 到 Protobuf 间互相转换的角色，而它利用的正是 Envoy 中的 [过滤器](https://www.envoyproxy.io/docs/envoy/latest/configuration/http/http_filters/grpc_json_transcoder_filter) 这一重要组件。好了，在今天这篇文章中，博主就为大家介绍一下这种基于 Envoy 的方案，如果大家困惑于如何把 gRPC 提供给前端同事使用，不妨稍事休息、冲一杯卡布奇诺，一起来探索这广阔无垠的技术世界。

# 从 Envoy 说起

开辟鸿蒙，始有天地。上帝说，要有光，于是，就有了光。而故事的起源，则要追溯到我们最早提出的那个问题：假设我们有下面的 gRPC 服务，我们能否让它像一个 JSON API 一样被调用？ 通过查阅 Protobuf 的 [官方文档](https://developers.google.cn/protocol-buffers/docs/proto3#json)，我们可以发现 Protobuf 与 JSON间存在着对应关系，这是两者可以相互转化的前提。博主在编写 [中间件](https://hub.fastgit.org/qinyuanpei/Grpc.Gateway/blob/master/src/Grpc.Gateway/GrpcExtensions.cs) 时，同样借助了 Protobuf 暴露出来的接口 [MessageParser](https://developers.google.cn/protocol-buffers/docs/reference/csharp/class/google/protobuf/message-parser?hl=zh-cn)：

```protobuf
syntax = "proto3";
option csharp_namespace = "GrpcService";
package greet;

service Greeter {
  rpc SayHello (HelloRequest) returns (HelloReply);
}
message HelloRequest {
  string name = 1;
}
message HelloReply {
  string message = 1;
}
```

接下来，这个 gPRC 服务如何和 Envoy 这个代理服务器产生关联呢？首当其冲的自然是一个路由啦：

```yaml
routes:
- match:
    prefix: "/greet"
  route:
    cluster: grpc_service
    timeout: 
      seconds: 60
```
这表示以 `/greet` 开头的请求会被路由到 `grpc_service` 这个集群，如果按照一般的 Envoy 使用流程，接下来，我们只需要配置对应的集群节点即可。我们前面提到过，Envoy 的这个 [gRPC-JSON Transcoder](https://www.envoyproxy.io/docs/envoy/latest/configuration/http/http_filters/grpc_json_transcoder_filter) 功能，是通过过滤器来实现的，更确切地说，它是一个 HTTP 级别的过滤器，所以，我们继续耐心往下看：

```yaml
http_filters:
- name: envoy.filters.http.grpc_json_transcoder
  typed_config:
    "@type": type.googleapis.com/envoy.extensions.filters.http.grpc_json_transcoder.v3.GrpcJsonTranscoder
    proto_descriptor: "/etc/descriptor/greet.pb"
    services:
    - "greet.Greeter"
    print_options:
      add_whitespace: true
      always_print_primitive_fields: true
      always_print_enums_as_ints: false
      preserve_proto_field_names: false
    auto_mapping: true
- name: envoy.filters.http.router
```
可以注意到，这里使用了一个叫做 `envoy.filters.http.grpc_json_transcoder` 的过滤器。对于这个过滤器而言，核心的、需要注意的地方有两个：

* `proto_descriptor` 指向一个 Protobuf 的描述文件，这是一个二进制文件，可以由`protoc`编译器生成。
* `services` 表示一组服务，必须按照 `包名.服务名` 的格式进行填写，这里的示例为：`greet.Greeter`。

关于如何生成二进制的 Protobuf 描述文件，我们专门放在下一节来讲，在此基础上，我们只要增加集群即可完成 Envoy 的配置：

```yaml
clusters:
- name: grpc_service
  connect_timeout: 0.25s
  type: LOGICAL_DNS
  lb_policy: ROUND_ROBIN
  dns_lookup_family: V4_ONLY
  http2_protocol_options: {}
  upstream_connection_options:
    tcp_keepalive:
      keepalive_time: 300
  load_assignment:
    cluster_name: grpc_service
    endpoints:
    - lb_endpoints:
      - endpoint:
          address:
            socket_address:
              address: grpc_service
              port_value: 80
```
完整的 Envoy 配置文件，请参考 [这里](https://github.com/Regularly-Archive/2021/tree/master/src/EnvoyGrpc)，不再占用篇幅进行说明。

# 准备描述文件

生成 Protobuf 的二进制描述文件，需要借助 [protoc](https://github.com/protocolbuffers/protobuf/releases) 这个命令行工具，此前我们介绍 gRPC 生态中的 gRPC-Web、gRPC-Gateway 时曾经接触过它。Envoy 正是通过这个描述文件来处理 `JSON` 和 `Protobuf` 的相互转换，博主猜测这里可能用到了类似 [MessageParser](https://developers.google.cn/protocol-buffers/docs/reference/csharp/class/google/protobuf/message-parser?hl=zh-cn) 的东西，Envoy 从这个二进制的描述文件中获取 gRPC 的元数据信息，并由此从 `JSON` 构建出 `Protobuf`。这里，我们还是以本文开始的 `.proto`文件为例：

```shell
protoc --descriptor_set_out=./Protos/descriptor/greet.pb --include_imports Protos\greet.proto
```
这条命令行的含义是，为 `Protos\greet.proto` 生成对应的服务描述文件 `/Protos/descriptor/greet.pb`。下图即为博主生成的服务描述文件：

![通过命令行生成 Protobuf 描述文件](https://i.loli.net/2021/08/08/lhPofJFKytHGWja.png)

此时，我们只需要将其放到 Envoy 的目录中即可，本文中的示例位于以下路径：`/etc/descriptor/greet.pb`。好了，现在 Envoy 和 gRPC 均已就绪，我们通过 `docker-compose` 对服务进行编排：

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
  grpcservice:
    build: GrpcService/GrpcService/
    ports:
      - "8082:80"
    environment:
      ASPNETCORE_URLS: "http://+"
      ASPNETCORE_ENVIRONMENT: "Development"
```
启动服务后，如果我们像调用 gRPC 服务中的 `SayHello()`方法，此时，对应的路由为：`/greet.Greeter/SayHello`，即：`包名.服务名/方法名`。好了，我们用 Postman 或者 Apifox 对接口进行测试：

![像调用一个 JSON API 一样调用 gRPC ](https://i.loli.net/2021/08/08/RZpux1nwWDh6eJK.png)

至此，我们实现一开始的目的，通过 Envoy 代理 gRPC 服务以后，对于前端而言，它已不再关心，这个服务背后的服务提供者到底是什么？因为对它而言，JSON API 还是 Protobuf 已经完全没有差别。博主曾经评价它是容器级别的方案，因为它可以将多个 gRPC 服务统一到一个入口中，非常适合充当整个微服务的网关，如果你正在使用 gRPC，相信我，这会是一条必由之路。

目前，博主所在的公司，已经全面采用了这种方案，而博主则进一步在团队中推广了`Docker-Compose`，换言之，我们将多个微服务通过`Docker-Compose`进行编排，并通过 Envoy 为所有微服务提供统一入口，唯一的遗憾是，通过`protoc`生成服务描述文件这个过程没有纳入到 CI/CD 环节，靠手动生成、复制服务描述文件，到底还是会有点失落呢？如果结合前面分享过的 [Envoy 身份认证](https://blog.yuanpei.me/posts/731808750/)，整个微服务架构终于看起来形成闭环啦！

# 本文小结

本文分享了 Envoy 中的 [gRPC-JSON Transcoder](https://www.envoyproxy.io/docs/envoy/latest/configuration/http/http_filters/grpc_json_transcoder_filter) 功能，它可以将一个 gRPC 服务代理成一个 JSON API，从而方便前端或者是客户端去消费一个 gRPC 服务。其原理是，Envoy 中可以通过配置过滤器来实现 JSON 和 Protobuf 的相互转换，这一过程依赖 Protobuf 的元数据，故而，我们需要通过命令行工具`protoc`生成服务描述文件，我们只需要在 Envoy 中添加相关配置，就可以像调用一个 JSON API 一样调用 gRPC。至此， gRPC 与 Web 世界彻底打通，我们可以用我们熟悉的技术去消费一个 gRPC 服务。博主的 [Grpc.Gateway](https://github.com/qinyuanpei/Grpc.Gateway) 实现了类似的功能，如果大家感兴趣，欢迎大家前去体验一番。好了，以上就是这篇博客的全部内容啦，谢谢大家，祝各位晚安！



