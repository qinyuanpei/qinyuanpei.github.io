---
toc: true
title: ASP.NET-Core 搭载 Envoy 实现 gRPC 服务的 JSON 转码
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
在构建以 gRPC 为核心的微服务架构的过程中，博主曾经写过一篇名为 [ASP.NET Core gRPC 打通前端世界的尝试](https://blog.yuanpei.me/posts/2167892202/) 的文章，主要是希望打通 gRPC 和 前端这样两个异次元世界，因为无论我们构建出怎高大上的微服务架构，最终落地的时候我们还是要面对当下前后端分离的浪潮。所以，在那篇文章中，博主向大家介绍过 gRPC-Web 、gRPC-Gateway 、封装 API 、编写中间件这样四种方案。我个人当时更喜欢编写中间件这种方案，甚至后来博主进一步实现了 gRPC 的 “扫描”功能。当时，博主曾模糊地提到过，Envoy 可以提供容器级别的某种实现，这主要是指 Envoy 独有的 JSON 转码功能。考虑到 Envoy 是一个同时支持 HTTP/1 和 HTTP/2 的代理软件，所以，它天然地支持基于 HTTP/2 实现的 gRPC。所谓 JSON 转码，其实指 Envoy 充当了 JSON 到 Protobuff 的这层转换角色，而它利用的正是 Envoy 中的过滤器这一重要组件。好了，在今天这篇文章中，博主就为大家介绍一下这种基于 Envoy 的方案，如果大家困惑于如何把 gRPC 提供给前端同事使用，不妨稍事休整、冲一杯卡布奇诺，一起来探索这广阔无垠的技术世界。

# 从 Envoy 说起
# 生成 .pb 文件
# 
