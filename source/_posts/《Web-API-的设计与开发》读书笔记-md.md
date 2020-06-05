---
abbrlink: 3677280829
categories:
- 读书笔记
date: 2019-05-28 12:00:53
description: '- 指使用符合RPC风格的XML或JSON + HTTP接口的系统(不使用SOAP);- 使用HTTP;# 查询参数和路径的使用区别'
tags:
- Web API
- RSETful
- 笔记
title: 《Web API 的设计与开发》读书笔记
---

# 设计优美的Web API：
易于使用、便于更改、健壮性好、不怕公开

# REST的两层含义：
- 指符合Fielding的REST架构风格的Web服务系统
- 指使用符合RPC风格的XML或JSON + HTTP接口的系统(不使用SOAP)

# 端点的基本设计：
- 短小便于输入的URI-
- 人可以读懂的URI
- 没有大小写混用的URI
- 修改方便的URI
- 不暴露服务端架构的URI
- 规则统一的URI

# HTTP方法和端点：
- GET获取资源
- POST新增资源
- PUT更新已有资源
- DELETE删除资源
- PATCH更新部分资源

# 查询参数和路径的使用区别
- 表示唯一资源时，放在路径中
- 当参数可以忽略时，放在查询参数中
# RESTful的设计级别
- 使用HTTP
- 引入资源的概念
- 引入HTTP动词
- 引入HATEOAS
# 如何指定数据格式？
- 查询参数：url?format=xml
- 扩展名：/url.json
- Accept头部字段
# 让用户决定响应的内容
- GraphQL
# 通过状态码表示错误信息
1xx：消息
2xx：成功
3xx：重定向
4xx：客户端原因造成的错误
5xx：服务端原因造成的错误
# 缓存与HTTP协议规范
RFC7234：过期模型/验证模型
过期模型：Cache-Control/Expires
验证模型：Last-Modified/ETag
Vary首部：指定缓存单位
Conent-Type/Accept：指定媒体类型

# API版本控制
- 在URI中嵌入版本号
- 在查询字符串中加入版本信息
- 通过媒体类型指定版本
# API安全问题
- 推荐使用HTTPS
- XSS/XSRF注入漏洞
- 返回正确的数据格式
- 使用安全相关首部
- 采用KVS实现访问限制
# 提供API文档
- API Blueprint
- API Console/Apigee
- 提供SDK