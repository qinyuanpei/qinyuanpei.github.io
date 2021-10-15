---
abbrlink: 2488769283
categories:
- 编程语言
copyright: true
date: 2020-04-02 10:26:53
description: 博主曾经在「[声明式RESTful客户端WebApiClient在项目中的应用](https://blog.yuanpei.me/posts/380519286/)」这篇博客中，介绍过.NET平台下的“Retrofit”——[WebApiClient](https://github.com/dotnetcore/WebApiClient)，它是一种声明式的RESTful客户端，通过动态代理来生成Http调用过程代码，而调用方只需要定义一个接口，并使用相关“注解”对接口进行修饰即可，类似的实现还有[Refit](https://github.com/reactiveui/refit)，是一种比HttpWebRequest、HttpClient和RestSharp更为优雅的接口调用方式;是的，你猜对了，实际运作过程中，测试环境和正式环境不单单会使用不同的域名，可能还会使用不同的路由，虽然，理论上两个环境的程序应该完全一样，应该使用相同的路由;在今天这篇博客中，我想聊聊WebApiClient中动态路由的实现与使用
tags:
- RESTful
- Retrofit
- WebApi
title: WebApiClient中动态路由的实现与使用
toc: true
---

博主曾经在「[声明式RESTful客户端WebApiClient在项目中的应用](https://blog.yuanpei.me/posts/380519286/)」这篇博客中，介绍过.NET平台下的“Retrofit”——[WebApiClient](https://github.com/dotnetcore/WebApiClient)，它是一种声明式的RESTful客户端，通过动态代理来生成Http调用过程代码，而调用方只需要定义一个接口，并使用相关“注解”对接口进行修饰即可，类似的实现还有[Refit](https://github.com/reactiveui/refit)，是一种比HttpWebRequest、HttpClient和RestSharp更为优雅的接口调用方式。在今天这篇博客中，我想聊聊WebApiClient中动态路由的实现与使用。

一个典型的WebApiClient使用流程如下，首先定义一个接口，并使用“注解”对接口进行修饰：
```CSharp
public interface ISinoiovApiClient : IHttpApiClient
{
    /// <summary>
    /// 运单取消接口
    /// </summary>
    /// <returns></returns>
    [HttpPost("/yl/api/waybill/cancel")]
    [AuthorizeFilter]
    [LoggingFilter]
    [JsonReturn]
    ITask<BaseApiResult<object>> CancelShipment([JsonContent]BaseShipmentDto shipment);
}
```
接下来，调用就变得非常简单：
```CSharp
var config = new HttpApiConfig () { HttpHost = new Uri (baseUrl) };
using (var client = HttpApiClient.Create<ISinoiovApiClient> (config)) 
{
    var result = await client.CancelShipment (new BaseShipmentDto () { });
    //TODO：TODO的意思就是永远都不做
}
```
有多简单呢？简单到调用的时候我们只需要给一个baseUrl就可以了！然而，如果你真这么想的话，就太天真了！虽然现在是一个遍地都是微服务和容器的时代，可是因为RESTful风格本身的约束力并不强，实际使用中难免会出现以下情况：
```CSharp
//测试环境
http://your-domain.com/test/api/waybill/cancel
//正式环境
http://your-domain.com/prod/api/waybill/cancel
```
是的，你猜对了，实际运作过程中，测试环境和正式环境不单单会使用不同的域名，可能还会使用不同的路由，虽然，理论上两个环境的程序应该完全一样，应该使用相同的路由。这样子就让我们有一点尴尬，因为我们的路由是写在特性(**Attribute**)里的，这玩意儿的实例化是附着在对应的类上面的，并且在整个运行时期间是不允许修改的。所谓**“兵来将挡水来土掩”**，接下来，我们来考虑如何解决这个问题。

# 使用[Uri]
第一种思路是给接口加一个Url参数，此时，调整接口方法声明如下：
```
    /// <summary>
    /// 运单取消接口
    /// </summary>
    /// <returns></returns>
    [HttpPost]
    [AuthorizeFilter]
    [LoggingFilter]
    [JsonReturn]
    ITask<BaseApiResult<object>> CancelShipment([Uri]string url, [JsonContent]BaseShipmentDto shipment);
```
这种方式可以解决问题，可我使用WebApiClient的原因之一，就是我不喜欢在客户端(调用方)维护这些地址。作为一个ApiCaller，在微服务架构流行以来，接口越来越多，逐渐呈现出爆炸式增加的趋势。当我作为一个后端工程师的时候，编写接口是件非常惬意的事情。可当我为了"全栈工程师"的虚名，去做一个面无表情的ApiCaller的时候，我是不情愿去配置这些Url的，有本事你把配置中心搭起来啊！所以，道理我都懂，But，我拒绝！

# 使用{foobar}
第二种思路是同样是给接口增加一个片段参数，此时，调整接口方法声明如下:
```
    /// <summary>
    /// 运单取消接口
    /// </summary>
    /// <returns></returns>
    [HttpPost('/{prefix}/api/waybill/cancel)]
    [AuthorizeFilter]
    [LoggingFilter]
    [JsonReturn]
    ITask<BaseApiResult<object>> CancelShipment([JsonContent]BaseShipmentDto shipment, string prefix = "yl");
```
这种方式和第一种方式原理一致，无非是需要配置的参数从多个变成一个。我个人更喜欢这种方式，为什么呢？可能我认为专业的Api接口会有版本的概念，类似于：
```CSharp
//版本号路由
/api/v2.0/abc/xyz
//查询参数路由
/api/abc/xyz?v=2.0
```
这样，我们就在无形中解决了一类问题，对于第二种形式，版本号以查询参数的方式出现，我们选择在过滤器中`AddUrlQuery()`或者使用`[PathQuery]`来解决。如果让我选择，我一定会选择这种方式，因为它更优雅一点吗？不，因为我懒，写程序的终究目的就是为了不写代码，就好像一个程序试图去杀死它自己的进程。

# 使用服务发现
第三种思路，我承认有一点赌的成份，你猜对接客户的接口的时候，会不会提供服务发现这套基础设施给你？可如果在自己的项目里有服务发现，还需要再配置每个服务的Url吗？这样想是不是觉得还不错，的确，我们在微服务架构里引入WebApiClient这种类Retrofit的库，本质上还是为了弱化服务的界限感，如果我调用一个服务和调用本地方法的体验一样，那么，这是什么呢？不用怀疑，这就是RPC(**大雾**)。这里，我实现了一个简单的示例：
```
//通过Consul获取可用地址
var services = await _consul.Health.Service("SinoiovApi", string.Empty, true);
var serviceUrls = services.Response.Select(s => $"{s.Service.Address}:{s.Service.Port}").ToList();
serviceUrl = serviceUrls[new Random().Next(0, serviceUrls.Count - 1)];
//今天的你我，怎样重复昨天的故事
var config = new HttpApiConfig () { HttpHost = new Uri (serviceUrl) };
using (var client = HttpApiClient.Create<ISinoiovApiClient> (config)) 
{
    var result = await client.CancelShipment (new BaseShipmentDto () { });
    //TODO：TODO的意思就是永远都不做
}
```
当然，我说了这有赌的成份，前提是这些服务在Consul中提前注册，这一点相信大家都知道啦！WebApiClient的[作者](https://www.cnblogs.com/kewei/)提供了类似扩展:[WebApiClient.Extensions.DiscoveryClient](https://github.com/xljiulang/WebApiClient.Extensions/blob/master/WebApiClient.Extensions.DiscoveryClient/DiscoveryClientExtensions.cs)，该扩展基于[Steeltoe](https://github.com/SteeltoeOSS/steeltoe)打造，感兴趣的朋友，可以前去了解一下。