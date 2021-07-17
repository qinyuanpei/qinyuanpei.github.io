---
toc: true
title: ASP.NET-Core 搭载 Envoy 实现 gRPC 服务代理
categories:
  - 编程语言
tags:
  - Envoy
  - 微服务
  - gRPC
  - RESTful
copyright: true
abbrlink: 3942175942
date: 2021-07-12 22:49:47
---
在构建以 gRPC 为核心的微服务架构的过程中，博主曾经写过一篇名为 [ASP.NET Core gRPC 打通前端世界的尝试](https://blog.yuanpei.me/posts/2167892202/) 的文章，主要是希望打通 gRPC 和 前端这样两个异次元世界，因为无论我们构建出怎高大上的微服务架构，最终落地的时候我们还是要面对当下前后端分离的浪潮。所以，在那篇文章中，博主向大家介绍过 gRPC-Web 、gRPC-Gateway 、封装 API 、编写中间件这样四种方案。我个人当时更喜欢编写中间件这种方案，甚至后来博主进一步实现了 gRPC 的 “扫描”功能。当时，博主曾模糊地提到过，Envoy 可以提供容器级别的某种实现，这主要是指 Envoy 独有的 JSON [转码](https://www.envoyproxy.io/docs/envoy/latest/configuration/http/http_filters/grpc_json_transcoder_filter) 功能。考虑到 Envoy 是一个同时支持 HTTP/1.1 和 HTTP/2 的代理软件，所以，它天然地支持基于 HTTP/2 实现的 gRPC。所谓 JSON 转码，其实指 Envoy 充当了 JSON 到 Protobuff 的这层转换角色，而它利用的正是 Envoy 中的 [过滤器](https://www.envoyproxy.io/docs/envoy/latest/configuration/http/http_filters/grpc_json_transcoder_filter) 这一重要组件。好了，在今天这篇文章中，博主就为大家介绍一下这种基于 Envoy 的方案，如果大家困惑于如何把 gRPC 提供给前端同事使用，不妨稍事休息、冲一杯卡布奇诺，一起来探索这广阔无垠的技术世界。

# 从 Envoy 说起

“上帝说，要有光，于是，就有了光”。故事的起源，要追溯到我们最早提出的那个问题，假设我们有下面的 gRPC 服务，我们能否让它像一个 JSON API 一样被调用？

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
          stat_prefix: grpc_json
          route_config:
            name: local_route
            virtual_hosts:
            - name: backend
              domains:
              - "*"
              routes:
              - match:
                  prefix: "/greet"
                route:
                  cluster: grpc_service
                  timeout: 
                    seconds: 60
```
这表示以`/greet`开头的请求会被路由到`grpc_service`这个集群(**Cluster**)，如果按照一般的 Envoy 使用流程，接下来，我们只需要配置对应的集群节点(**Cluster**)即可。我们前面提到过，Envoy 的这个 [JSON 转码](https://www.envoyproxy.io/docs/envoy/latest/configuration/http/http_filters/grpc_json_transcoder_filter) 功能，是通过过滤器来实现的，更确切地说，它是一个 HTTP 级别的过滤器，所以，我们继续耐心往下看：

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
          stat_prefix: grpc_json
          route_config:
            name: local_route
            virtual_hosts:
            - name: backend
              domains:
              - "*"
              routes:
              - match:
                  prefix: "/greet"
                route:
                  cluster: grpc_service
                  timeout: 
                    seconds: 60
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
可以注意到，这里使用了一个叫做`envoy.filters.http.grpc_json_transcoder`的过滤器。对于这个过滤器而言，核心的地方有两个：

* `proto_descriptor`指向一个 Protobuf 的描述文件，这是一个二进制文件，可以由`protoc`编译器生成。
* `services`表示一组服务，必须按照 `包名.服务名` 的格式进行填写，这里的示例为：`greet.Greeter`。

关于如何生成二进制的描述文件，我们专门放在下一节来讲。在此基础上，我们只要增加集群(**Cluster**)就可以完成 Envoy 的配置：

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
          stat_prefix: grpc_json
          route_config:
            name: local_route
            virtual_hosts:
            - name: backend
              domains:
              - "*"
              routes:
              - match:
                  prefix: "/greet"
                route:
                  cluster: grpc_service
                  timeout: 
                    seconds: 60
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

# 准备描述文件

Protobuf 的二进制描述文件，需要通过 [protoc](https://github.com/protocolbuffers/protobuf/releases) 这个命令行工具来生成。因为 Envoy 需要通过这个描述文件来处理`JSON`->`Protobuf`的转换，博主猜测这里可能用到了类似 [MessageParser](https://developers.google.cn/protocol-buffers/docs/reference/csharp/class/google/protobuf/message-parser?hl=zh-cn) 的东西，可以从`JSON`构建出`Protobuf`，这个过程中需要的元数据信息，则是由这个二进制描述工具来提供的。
# 
