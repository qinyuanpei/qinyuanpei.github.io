---
abbrlink: 1679688265
categories:
  - 编程语言
tags:
  - .NET
  - gRPC
  - AOP
  - 日志
title: ASP.NET Core gRPC 拦截器的使用技巧分享
date: 2021-05-26 09:03:35
---

`gRPC`是微软在`.NET Core` 及其后续版本中主推的 RPC 框架，它使用 `Google` 的 `Protocol Buffers` 作为序列化协议，使用 **HTTP/2** 作为通信协议，具有**跨语言**、**高性能**、**双向流式调用**等优点。考虑到，接下来要参与的是，一个以`gRPC`为核心而构建的微服务项目。因此，博主准备调研一下`gRPC`的相关内容，而首当其冲的，则是从 .NET Core 3.1 开始就有的拦截器，它类似于`ASP.NET Core`中的过滤器和中间件，体现了一种面向切面编程(**AOP**)的思想，非常适合在RPC服务调用的时候做某种统一处理，譬如参数校验、身份验证、日志记录等等。在今天这篇博客中，博主主要和大家分享的是，利用 .NET Core gRPC 中的拦截器实现日志记录的简单技巧，希望能给大家带来一点启发。

![开源、多语言、高性能的 gRPC](https://i.loli.net/2021/05/28/1MgBG2uRHwEqXvt.jpg)

# 关于 Interceptor 类

`Interceptor`类是 gRPC 服务拦截器的基类，它本身是一个抽象类，其中定义了下面的虚方法：

```csharp
public virtual AsyncClientStreamingCall<TRequest, TResponse> AsyncClientStreamingCall<TRequest, TResponse>();
public virtual AsyncDuplexStreamingCall<TRequest, TResponse> AsyncDuplexStreamingCall<TRequest, TResponse>();
public virtual AsyncUnaryCall<TResponse> AsyncUnaryCall<TRequest, TResponse>();
public virtual TResponse BlockingUnaryCall<TRequest, TResponse>();
public virtual Task<TResponse> ClientStreamingServerHandler<TRequest, TResponse>();
public virtual AsyncServerStreamingCall<TResponse> AsyncServerStreamingCall<TRequest, TResponse>();
public virtual Task DuplexStreamingServerHandler<TRequest, TResponse>();
public virtual Task ServerStreamingServerHandler<TRequest, TResponse>();
public virtual Task<TResponse> UnaryServerHandler<TRequest, TResponse>();
```
整体而言，如果从通信方式上来划分，可以分为：**流式调用** 和 **普通调用**；而如果从使用方来划分，则可以分为：**客户端** 和 **服务端**。进一步讲的话，针对**流式调用**，它还分为："**单向流**" 和 "**双向流**"。关于这些细节上的差异，大家可以通过 `gRPC` 的 [官方文档](https://www.grpc.io/docs/what-is-grpc/core-concepts/) 来了解，这里我们给出的是每一种方法对应的用途：

| 方法名                        | 描述                               | 
| ---------------------------- | ---------------------------------- | 
| AsyncClientStreamingCall     | 拦截异步客户端流式调用               | 
| AsyncDuplexStreamingCall     | 拦截双向流式调用                     | 
| AsyncUnaryCall               | 拦截异步普通调用                     |
| BlockingUnaryCall            | 拦截阻塞普通调用                     | 
| AsyncServerStreamingCall     | 拦截异步服务端流式调用               |
| ClientStreamingServerHandler | 拦截客户端流式调用的服务端处理程序    | 
| DuplexStreamingServerHandler | 拦截双向流式调用的服务端处理程序      | 
| ServerStreamingServerHandler | 拦截服务端流式调用的服务端处理程序    | 
| UnaryServerHandler           | 拦截普通调用的服务端处理程序         | 

# 实现一个拦截器

好了，下面我们一起实现一个拦截器。这里，我们使用的是微软官方的例子：

```csharp
public class GreeterService : Greeter.GreeterBase
{
    private readonly ILogger<GreeterService> _logger;
    public GreeterService(ILogger<GreeterService> logger)
    {
        _logger = logger;
    }

    public override Task<HelloReply> SayHello(HelloRequest request, ServerCallContext context)
    {
        return Task.FromResult(new HelloReply
        {
            Message = "Hello " + request.Name
        });
    }
}
```

## 服务器端

实现服务器端的普通调用拦截，我们需要重写的方法是`UnaryServerHandler`:

```csharp
public class GRPCServerLoggingInterceptor : Interceptor
{
    private readonly ILogger<GRPCServerLoggingInterceptor> _logger;
    public GRPCServerLoggingInterceptor(ILogger<GRPCServerLoggingInterceptor> logger)
    {
        _logger = logger;
    }
    
    // 重写 UnaryServerHandler() 方法
    public override Task<TResponse> UnaryServerHandler<TRequest, TResponse>(
      TRequest request, ServerCallContext context, 
      UnaryServerMethod<TRequest, TResponse> continuation
    )
    {
        var builder = new StringBuilder();

        // Call gRPC begin
        builder.AppendLine($"Call gRPC {context.Host}/{context.Method} begin.");

        // Logging Request
        builder.AppendLine(LogRequest(request));

        // Logging Response
        var reply = continuation(request, context);
        var response = reply.Result;
        var exception = reply.Exception;
        builder.AppendLine(LogResponse(response, exception));

        // Call gRPC finish
        builder.AppendLine($"Call gRPC {context.Host}/{context.Method} finish.");
        _logger.LogInformation(builder.ToString());

        return reply;
    }
    
    // 记录gRPC请求
    private string LogRequest<TRequest>(TRequest request)
    {
        var payload = string.Empty;
        if (request is IMessage)
            payload = JsonConvert.SerializeObject(
                (request as IMessage)
                .Descriptor.Fields.InDeclarationOrder()
                .ToDictionary(x => x.Name, x => x.Accessor.GetValue(request as IMessage))
            );
        return $"Send request of {typeof(TRequest)}:{payload}";
    }
    
    // 记录gRPC响应
    private string LogResponse<TResponse>(TResponse response, AggregateException exception)
    {
        var payload = string.Empty;
        if (exception == null)
        {
            if (response is IMessage)
                payload = JsonConvert.SerializeObject(
                  (response as IMessage)
                  .Descriptor.Fields.InDeclarationOrder()
                  .ToDictionary(x => x.Name, x => x.Accessor.GetValue(response as IMessage))
                );
            return $"Receive response of {typeof(TResponse)}:{payload}";
        }
        else
        {
            var errorMsgs = string.Join(";", exception.InnerExceptions.Select(x => x.Message));
            return $"Receive response of {typeof(TResponse)} throws exceptions: {errorMsgs}";
        }
    }
}
```

对于`gRPC`而言，每一个由`.proto`声明文件生成的类，都带有一个叫做`Descriptor`的属性，我们可以利用这个属性获得`gRPC`请求和响应的详细信息。所以，在`LogRequest()`和`LogResponse()`两个方法中，我们均使用了这一思路来记录`gRPC`的报文信息，因为传输层的`gRPC`使用了二进制作为数据载体，这可以说是一种用可读性换取高效率的做法，不过幸运的是，我们在这里实现了这个小目标。

接下来，为了让这个拦截器真正生效，我们还需要修改一下`Startup`类中注册`gRPC`这部分的代码：

```csharp
services.AddGrpc(options => options.Interceptors.Add<GRPCServerLoggingInterceptor>());
```

此时，我们可以得到下面的结果：

![gRPC服务器端拦截器效果展示](https://i.loli.net/2021/05/27/3nZXelLPVwJ7AjS.png)

## 客户端

实现客户端的普通调用拦截，我们需要重写的方法是`AsyncUnaryCall()`，依样画葫芦即可：

```csharp
public class GRPCClientLoggingInterceptor : Interceptor
{
    // 重写 AsyncUnaryCall() 方法
    public override AsyncUnaryCall<TResponse> AsyncUnaryCall<TRequest, TResponse>(
        TRequest request,
        ClientInterceptorContext<TRequest, TResponse> context,
        AsyncUnaryCallContinuation<TRequest, TResponse> continuation
    )
    {
        var builder = new StringBuilder();

        // Call gRPC begin
        builder.AppendLine($"Call gRPC {context.Host}/{context.Method} begin.");

        // Logging Request
        builder.AppendLine(LogRequest(request));

        // Logging Response
        var reply = continuation(request, context);
        var response = reply.ResponseAsync.Result;
        var exception = reply.ResponseAsync.Exception;
        builder.AppendLine(LogResponse(response, exception));

        // Call gRPC finish
        builder.AppendLine($"Call gRPC {context.Host}/{context.Method} finish.");
        Console.WriteLine(builder.ToString());

        return reply;
    }
}
```

类似地，为了让拦截器在客户端生效，我们需要这样：


```csharp
using Grpc.Core.Interceptors;

var channel = GrpcChannel.ForAddress("https://localhost:5001");
// 简化写法
channel.Intercept(new GRPCClientLoggingInterceptor());
// 完整写法
var invoker = channel.CreateCallInvoker().Intercept(new GRPCClientLoggingInterceptor());
var client = new Greeter.GreeterClient(invoker);
await client.SayHelloAsync(new HelloRequest() { Name = "长安书小妆" });
```

此时，我们可以得到下面的结果：

![gRPC客户端拦截器效果展示](https://i.loli.net/2021/05/28/XcwmOQbzKTJPtUj.png)

客户端感觉不太好的一点就是，这个`Interceptor`传入的必须是一个实例，考虑到拦截器内部可能会依赖类似`ILogger`等等的组件，建议还是通过`IoC`容器来取得一个拦截器的实例，然后再传入`Intercept()`方法中。博主所在的项目中，则是非常“**土豪**”地使用了`PostSharp`，直接走动态编织的方案，果然，“**这次第，怎一个羡字了得**”。当然，`gRPC`的客户端，其实提供了日志相关的支持，不过，我个人感觉这个有一点无力：

```csharp
var loggerFactory = LoggerFactory.Create(logging =>
{
    logging.AddConsole();
    logging.SetMinimumLevel(LogLevel.Debug);
});
var channel = GrpcChannel.ForAddress(
    "https://localhost:5001",
    new GrpcChannelOptions { LoggerFactory = loggerFactory }
);
```

# 本文小结

本文主要分享了`gRPC`拦截器的使用技巧，`gRPC`支持一元调用(**UnaryCall**)、流式调用(**StreamingCall**)、阻塞调用(**BlockingCall**)，因为区分客户端和服务器端，所以，实际上会有各种各样的组合方式。`gRPC`的拦截器实际上就是选择对应的场景去重写相应的方法，其中，拦截器的基类为`Interceptor`类，这里我们都是以普通的一元调用为例的，大家可以结合各自的业务场景，去做进一步的调整和优化。这里，我们使用`IMessage`类的`Descriptor`属性来“反射”报文中定义的字段，这样就实现了针对`gRPC`服务请求/响应的日志记录功能。关于`gRPC`中日志和诊断的更进一步的话题，大家可以参考微软的 [官方文档](https://docs.microsoft.com/zh-cn/aspnet/core/grpc/diagnostics?view=aspnetcore-5.0) 。好了，以上就是这篇博客的全部内容啦，谢谢大家！


