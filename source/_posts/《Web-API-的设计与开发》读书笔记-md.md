---
abbrlink: 3677280829
categories:
- 读书笔记
date: 2019-05-28 12:00:53
description: '- 指使用符合 RPC 风格的 XML 或 JSON + HTTP 接口的系统(不使用 SOAP);- 使用 HTTP;# 查询参数和路径的使用区别'
tags:
- Web API
- RSETful
- 笔记
- 提纲
title: 《Web API 的设计与开发》读书笔记
---

# 设计优美的 Web API
易于使用、便于更改、健壮性好、不怕公开

# REST 的两层含义
- 指符合 Fielding 的 REST 架构风格的 Web 服务系统
- 指使用符合 RPC 风格的 XML 或 JSON + HTTP 接口的系统(不使用 SOAP)

# 端点的基本设计
- 短小便于输入的 URI-
- 人可以读懂的 URI
- 没有大小写混用的 URI
- 修改方便的 URI
- 不暴露服务端架构的 URI
- 规则统一的 URI

# HTTP 方法和端点
- GET 获取资源
- POST 新增资源
- PUT 更新已有资源
- DELETE 删除资源
- PATCH 更新部分资源

# 查询参数和路径的使用区别
- 表示唯一资源时，放在路径中
- 当参数可以忽略时，放在查询参数中
# RESTful 的设计级别
- 使用 HTTP
- 引入资源的概念
- 引入 HTTP 动词
- 引入 HATEOAS
# 如何指定数据格式
- 查询参数：url?format=xml
- 扩展名：/url.json
- Accept 头部字段
# 让用户决定响应的内容
- GraphQL
# 通过状态码表示错误信息
1xx：消息
2xx：成功
3xx：重定向
4xx：客户端原因造成的错误
5xx：服务端原因造成的错误
# 缓存与 HTTP 协议规范
RFC7234：过期模型/验证模型
过期模型：Cache-Control/Expires
验证模型：Last-Modified/ETag
Vary 首部：指定缓存单位
Conent-Type/Accept：指定媒体类型

# API 版本控制
- 在 URI 中嵌入版本号
- 在查询字符串中加入版本信息
- 通过媒体类型指定版本
# API 安全问题
- 推荐使用 HTTPS
- XSS/XSRF 注入漏洞
- 返回正确的数据格式
- 使用安全相关首部
- 采用 KVS 实现访问限制
# 提供 API 文档
- API Blueprint
- API Console/Apigee
- 提供 SDK