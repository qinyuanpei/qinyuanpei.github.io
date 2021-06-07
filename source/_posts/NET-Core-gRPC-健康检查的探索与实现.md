---
abbrlink: 1657075397
categories:
  - 编程语言
tags:
  - gRPC
  - 微服务
  - 健康检查
  - Consul
title: ASP.NET Core gRPC 健康检查的探索与实现
date: 2021-06-01 11:37:36
---

各位朋友，大家好，欢迎大家关注我的博客。在上一篇 [博客](https://blog.yuanpei.me/posts/1679688265/) 中，博主和大家分享了`gRPC`的拦截器在日志记录方面的简单应用，今天我们继续来探索`gRPC`在构建微服务架构方面的可能性。其实，从博主个人的理解而言，不管我们的微服务架构是采用`RPC`方式还是采用`RESTful`方式，我们最终要面对的问题本质上都是一样的，博主这里将其归纳为：服务划分、服务编写 和 服务治理。首先，服务划分决定了每一个服务的上下文边界以及服务颗粒度大小，如果按照领域驱动设计(**DDD**)的思想来描述微服务，我认为它更接近于限界上下文(**BoundedContext**)的概念。其次，服务编写决定了每一个服务的具体实现方式，譬如是采用无状态的`RESTful`风格的`API`，还是采用强类型的、基于代理的`RPC`风格的`API`。最后，服务治理是微服务架构中永远避不开的话题，服务注册、服务发现、健康检查、日志监控等等一切的话题，其实都是在围绕着**服务治理**而展开，尤其是当我们编写了一个又一个的服务以后，此时该如何管理这些浩如“**星**”海的服务呢？所以，在今天这篇博客中，博主想和大家一起探索下`gRPC`的健康检查，希望能给大家带来一点启发。

![健康检查-服务注册-服务发现示意图](https://i.loli.net/2021/06/02/oVS3YkPIncr2xM9.jpg)

关于“健康检查”，大家都知道的一点是，它起到一种“防微杜渐”的作用。不知道大家还记不记得，语文课本里的经典故事《扁鹊见蔡桓公》，扁鹊一直在告知蔡桓公其病情如何，而蔡桓公讳疾忌医，直至病入骨髓、不治而亡。其实，对应到我们的领域知识，后端依赖的各种服务譬如数据库、消息队列、Redis、API等等，都需要这样一个“**扁鹊**”来实时地“**望闻问切**”，当发现问题的时候及时地采取相应措施，不要像“**蔡桓公**”一样病入骨髓，等到整个系统都瘫痪了，这时候火急火燎地去“救火”，难免会和蔡桓公一样，发出“悔之晚矣”的喟叹。当我们决定使用`gRPC`来构建微服务架构的时候，我们如何确保这些服务一直是可用的呢？所以，提供一种针对`gRPC`服务的健康检查方案就会显得非常迫切。这里，博主主要为大家介绍两种实现方式，它们分别是：基于`IHostedService`的实现方式 以及 基于`Consul`的实现方式。

# 基于 IHostedService 的实现方式

第一种方式，主要是利用`IHostedService`可以在程序后台执行的特点，搭配`Timer`就可以实现定时轮询。在 [gRPC](https://github.com/grpc/grpc) 的 [官方规范](https://github.com/grpc/grpc/blob/master/doc/health-checking.md) 中，提供了一份`Protocol Buffers`的声明文件，它规定了一个健康检查服务必须实现`Check()`和`Watch()`两个方法。既然是官方定义好的规范，建议大家不要修改这份声明文件，我们直接沿用即可：

```shell
syntax = "proto3";

package grpc.health.v1;

message HealthCheckRequest {
  string service = 1;
}

message HealthCheckResponse {
  enum ServingStatus {
    UNKNOWN = 0;
    SERVING = 1;
    NOT_SERVING = 2;
  }
  ServingStatus status = 1;
}

service Health {
  rpc Check(HealthCheckRequest) returns (HealthCheckResponse);
  rpc Watch(HealthCheckRequest) returns (stream HealthCheckResponse);
}
```

接下来，我们需要实现对应的`HealthCheckService`:

```csharp
public class HealthCheckService : Health.HealthBase
{
    public override Task<HealthCheckResponse> Check(
      HealthCheckRequest request, 
      ServerCallContext context
    )
    {
        // TODO: 在这里添加更多的细节
        return Task.FromResult(new HealthCheckResponse() { 
            Status = HealthCheckResponse.Types.ServingStatus.Serving 
        });
    }

    public override async Task Watch(
      HealthCheckRequest request, 
      IServerStreamWriter<HealthCheckResponse> responseStream, 
      ServerCallContext context
    )
    {
        // TODO: 在这里添加更多的细节
        await responseStream.WriteAsync(new HealthCheckResponse(){
            Status = HealthCheckResponse.Types.ServingStatus.Serving 
        });
    }
}
```

接下来，我们需要实现`HostedHealthCheckService`，它实现了`IHostedService`接口，并在其中调用`HealthCheckService`:

```csharp
public class HostedHealthCheckService : IHostedService
{
    private Timer _timer = null;
    private readonly ILogger<HostedHealthCheckService> _logger;

    public HostedHealthCheckService(ILogger<HostedHealthCheckService> logger)
    {
        _logger = logger;
    }

    public Task StartAsync(CancellationToken cancellationToken)
    {
        _logger.LogInformation($"{nameof(HostedHealthCheckService)} start running....");
        _timer = new Timer(DoCheck, null, TimeSpan.Zero, TimeSpan.FromSeconds(5));
        return Task.CompletedTask;
    }

    public Task StopAsync(CancellationToken cancellationToken)
    {
        _logger.LogInformation($"{nameof(HostedHealthCheckService)} stop running....");
        _timer?.Change(Timeout.Infinite, 0);
        return Task.CompletedTask;
    }

    private void DoCheck(object state)
    {
        using var channel = GrpcChannel.ForAddress("https://localhost:5001"); ;
        var client = new Health.HealthClient(channel);
        client.Check(new HealthCheckRequest() { Service = "https://localhost:5001" });
    }
}
```
接下来，是大家非常熟悉的**依赖注入**环节：

```csharp
// ConfigureServices
public void ConfigureServices(IServiceCollection services)
{
    services.AddGrpc(options => options.Interceptors.Add<GrpcServerLoggingInterceptor>());
    services.AddHostedService<HostedHealthCheckService>();
}

// Configure
public void Configure(IApplicationBuilder app, IWebHostEnvironment env)
{
    app.UseEndpoints(endpoints =>
    {
        endpoints.MapGrpcService<HealthCheckService>();
    });
}
```

如果大家对上一篇博客中的拦截器还有印象，对于下面的结果应该会感到非常亲切：

![基于 IHostedService 的 gRPC 健康检查](https://i.loli.net/2021/06/02/vx2QLUoMzXaWpZY.png)

除此以外，我们还可以直接安装第三方库：`Grpc.HealthCheck`。此时，我们需要继承`HealthServiceImpl`类并重写其中的`Check()`和`Watch()`方法:

```csharp
public class HealthCheckService : HealthServiceImpl
{
    public override Task<HealthCheckResponse> Check(
      HealthCheckRequest request, 
      ServerCallContext context
    )
    {
        // TODO: 在这里添加更多的细节
        return Task.FromResult(new HealthCheckResponse()
        {
            Status = HealthCheckResponse.Types.ServingStatus.Serving
        });
    }

    public override async Task Watch(
      HealthCheckRequest request, 
      IServerStreamWriter<HealthCheckResponse> responseStream, 
      ServerCallContext context
    )
    {
        // TODO: 在这里添加更多的细节
        await responseStream.WriteAsync(new HealthCheckResponse()
        {
            Status = HealthCheckResponse.Types.ServingStatus.Serving
        });
    }
}
```

接下来，我们只需要在`HostedHealthCheckService`调用它即可，这个非常简单。

故，无需博主多言，相信屏幕前的你都能写得出来，如果写不出来，参考博主给出得实现即可(逃！

# 基于 Consul 的实现方式

[Consul](https://www.consul.io/) 是一个由 [HashiCorp](https://www.hashicorp.com/about) 提供的产品，它提供了服务注册、服务发现、健康检查、键值存储等等的特性。这里，我们通过集成它的`SDK`来实现`gRPC`服务的服务注册、服务发现、健康检查，从某种程度上来讲，它无形中帮助我们实现了客户端的负载均衡，因为我们可以将每一个服务的终结点都注册到`Consul`中，而`Consul`的健康检查则可以定时移除那些不可用的服务。所以，客户端获得的终结点实际上都是可用的终结点。

首先，我们需要安装第三方库：`Consul`。接下来，我们可需要通过`Docker`安装一下`Consul`:

```shell
docker pull consul
docker run --name consul -d -p 8500:8500 consul
```

默认情况下，`Consul`的端口号为：8500，我们可以直接访问：`http://localhost:8500`：

![Consul 界面效果展示](https://i.loli.net/2021/06/02/Gjb9XhpRCI7g2w5.png)

接下来，为了让`Startup`类看起来清爽一点，首先，我们先来写一点扩展方法：

```csharp
// 为指定的gRPC服务添加健康检查
public static void AddGrpcHealthCheck<TService>(this IServiceCollection services)
{
    var configuration = services.BuildServiceProvider().GetService<IConfiguration>();

    // 注册ConsulClient
    services.AddSingleton<IConsulClient, ConsulClient>(_ => new ConsulClient(consulConfig =>
    {
        var baseUrl = configuration.GetValue<string>("Consul:BaseUrl");
        consulConfig.Address = new Uri(baseUrl);
    }));

    // 注册gRPC服务
    RegisterConsul<TService>(services).Wait();
}
```
其中，`RegisterConsul()`方法负责告诉`Consul`，某个服务对应的IP和端口号分别是多少，采用什么样的方式进行健康检查。

不过，由于`Consul`默认不支持`gRPC`的健康检查，所以，我们使用了更为常见的基于`TCP`方式的健康检查。你可以认为，只要服务器连接畅通，`gRPC`服务就是健康的。

```csharp
// 注册指定服务到Consul
private static async Task RegisterConsul<TService>(IServiceCollection services)
{
    var serverHost = GetLocalIP();
    var serverPort = services.BuildServiceProvider().GetService<IConfiguration>().GetValue<int>("gRPC:Port");
    await RegisterConsul<TService>(services, serverHost, serverPort);
}

// 注册指定服务到Consul
private static async Task RegisterConsul<TService>(
  IServiceCollection services, 
  string serverHost, 
  int serverPort
)
{
    var client = services.BuildServiceProvider().GetService<IConsulClient>();
    var registerID = $"{typeof(TService).Name}-{serverHost}:{serverPort}";
    await client.Agent.ServiceDeregister(registerID);
    var result = await client.Agent.ServiceRegister(new AgentServiceRegistration()
    {
        ID = registerID,
        Name = typeof(TService).Name,
        Address = serverHost,
        Port = serverPort,
        Check = new AgentServiceCheck
        {
            TCP = $"{serverHost}:{serverPort}",
            Status = HealthStatus.Passing,
            DeregisterCriticalServiceAfter = TimeSpan.FromSeconds(10),
            Interval = TimeSpan.FromSeconds(10),
            Timeout = TimeSpan.FromSeconds(5)
        },
        Tags = new string[] { "gRpc" }
    }) ;
}
```
对于`Consul`中的健康检查，更常用的是基于`HTTP`的健康检查，简单来说，就是我们提供一个接口，供`Consul`来调用，我们可以去设置请求的头(Header)、消息体(Body)、方法(Method)等等。所以，对于这里的实现，你还可以替换为更一般的实现，即提供一个API接口，然后在这个接口中调用`gRPC`的客户端。除此以外，如果你擅长写脚本，`Consul`同样支持脚本级别的健康检查。

在这里，博主水平扩展(复制)了两套服务，它们分别被部署在`5001`和`6001`两个端口上，通过`Consul`能达到什么效果呢？我们一起来看一下：

```csharp
// ConfigureServices
public void ConfigureServices(IServiceCollection services)
{
    services.AddGrpc(options => options.Interceptors.Add<GrpcServerLoggingInterceptor>());
    services.AddGrpcHealthCheck<GreeterService>();
    services.AddGrpcHealthCheck<CalculatorService>();
}

// Configure
public void Configure(IApplicationBuilder app, IWebHostEnvironment env)
{
    app.UseEndpoints(endpoints =>
    {
        endpoints.MapGrpcService<GreeterService>();
        endpoints.MapGrpcService<CalculatorService>();
    });
}
```

OK，此时，我们注意到`Consul`中有两个服务注册进去，它们分别是：`GreeterService` 和 `CalculatorService`：

![gRPC 服务成功注册到 Consul 中](https://i.loli.net/2021/06/02/eTBj7Iqn256GXKw.png)

以其中一个`CalculatorService`为例，我们可以注意到，它的确注册了`5001`和`6001`两个实例：

![CalculatorService 的两个实例](https://i.loli.net/2021/06/03/xlhMjJ1ZcN3nwBe.png)

至此，我们就完成了基于`Consul`的健康检查，在这里，图中的绿色标记表示服务可用。

# 关于 gRPC 的引申话题

其实，写到这里的时候，这篇博客就该接近尾声啦，因为对于 gRPC 健康检查的探索基本都已找到答案，可我还是想聊一聊关于 gRPC 的引申话题。理由特别简单，就是在我看来，接下来要讲的这点内容，完全撑不起一篇博客的篇幅，索性就在这篇博客里顺带一提。我打算分享两个话题，**其一，是 gRPC 客户端的负载均衡；其二，是 gRPC 接口的测试工具。**

## gRPC 客户端的负载均衡

截止到目前为止，结合`Consul`我们已经实现了服务注册和服务发现两个功能。通过调研我们可以发现，针对服务器端的`gRPC`的负载均衡，目前主要有`Nginx`和`Envoy`两种方案，这两种相方案对要更复杂一点，博主目前所在的公司，在`gRPC`的负载均衡上感觉是个空白，这算是博主想要研究`gRPC`的一个主要原因。而在这里，由于`Consul`里注册了所有`gRPC`服务的终结点信息，所以，我们更容易想到的，其实是客户端的负载均衡，具体怎么实现呢？我们一起看一下：

```csharp
// 从Consul中获取服务终结点信息
var consulClient = serviceProvider.GetService<IConsulClient>();
var serviceName = typeof(TGrpcClient).Name.Replace("Client", "Service");
var services = await consulClient.Health.Service(serviceName, string.Empty, true);
var serviceUrls = services.Response.Select(s => $"{s.Service.Address}:{s.Service.Port}").ToList();
if (serviceUrls == null || !serviceUrls.Any())
    throw new Exception($"Please make sure service {serviceName} is registered in consul");

// 构造Channel和Client
var serviceUrl = serviceUrls[new Random().Next(0, serviceUrls.Count - 1)];
var channel = GrpcChannel.ForAddress($"https://{serviceUrl}");
var client = new var client = new Calculator.CalculatorClient(channel);
await client.CalcAsync(new CalculatorRequest() { Num1 = 10, Op = "+", Num2 = 12 });
```

可以看出，基本思路就是从`Consul`里拿到对应服务的终结点信息，然后构造出`GrpcChannel`，再通过`GrpcChannel`构造出Client即可。

不过，博主觉得这个过程有一点繁琐，我们有没有办法让这些细节隐藏起来呢？于是，我们有了下面的改进方案：

```csharp
public static async Task<TGrpcClient> GetGrpcClientAsync<TGrpcClient>(
  this IServiceProvider serviceProvider
)
{
    var consulClient = serviceProvider.GetService<IConsulClient>();
    var serviceName = typeof(TGrpcClient).Name.Replace("Client", "Service");
    var services = await consulClient.Health.Service(serviceName, string.Empty, true);
    var serviceUrls = services.Response.Select(s => $"{s.Service.Address}:{s.Service.Port}").ToList();
    if (serviceUrls == null || !serviceUrls.Any())
        throw new Exception($"Please make sure service {serviceName} is registered in consul");

    var serviceUrl = serviceUrls[new Random().Next(0, serviceUrls.Count - 1)];
    var channel = GrpcChannel.ForAddress($"https://{serviceUrl}");
    var constructorInfo = typeof(TGrpcClient).GetConstructor(new Type[] { typeof(GrpcChannel) });
    if (constructorInfo == null)
        throw new Exception($"Please make sure {typeof(TGrpcClient).Name} is a gRpc client");

    var clientInstance = (TGrpcClient)constructorInfo.Invoke(new object[] { channel });
    return clientInstance;
}
```

现在，有没有觉得简单一点？完美！

```csharp
var client = await serviceProvider.GetGrpcClientAsync<CalculatorClient>();
await client.CalcAsync(new CalculatorRequest() { Num1 = 1, Num2 = 2, Op = "+" });
```

## gRPC 接口的测试工具

我猜，大多数看到这个标题会一脸鄙夷，心里大概会想，就测试工具这种东西值得特地写出来吗？诚然，以前写API接口的时候，大家都是用 [Postman](https://www.postman.com/downloads/) 或者 [Apifox](https://www.apifox.cn/) 这样的工具来进行测试的，可是突然有一天你要调试一个`gRPC`的接口，你总不能每次都调用客户端啊，所以，这里要给大家推荐两个`gRPC`接口的测试工具，它们分别是: [grpcurl](https://github.com/fullstorydev/grpcurl) 和 [grpcui](https://github.com/fullstorydev/grpcui)，它们都出自同一个人 [FullStory](https://github.com/fullstorydev) 之手，基于Go语言开发，简单介绍下使用方法：

```shell
// grpcurl
brew install grpcurl

// grpcui
go get github.com/fullstorydev/grpcui/...
go install github.com/fullstorydev/grpcui/cmd/grpcui
```

虽然这个说明简单而直白，可我还是没能装好，我不得不祭出Docker这个神器，果然它不会令我失望：

```shell
docker run -e GRPCUI_SERVER=localhost:5001 -p 8080:8080 wongnai/grpcui
```

这里有两个重要的参数，其中，`8080`是`grpcui`的服务地址，可以按个人喜好进行修改，`GRPCUI_SERVER`是`gRPC`服务地址，该工具运行效果如下：

![gRPCUI 接口测试工具](https://i.loli.net/2021/06/03/gGMaVKquDbtdWUN.png)

对于使用者来说，我们只需要选择服务(service)、方法(rpc)、然后填入参数即可，个人感觉非常方便。

# 本文小结

本文探索并实现了`gRPC`服务健康检查，主要提供了两种思路：基于`IHostedService` + `Timer`的轮询的方案 以及 基于`Consul`的集服务注册、服务发现、健康检查于一身的方案。特别地，对于后者而言，我们可以顺理成章地联想到客户端的负载均衡，其原理是：`Consul`中注册了所有`gRPC`服务的终结点信息，通过`IConsulClient`可以拿到所有可用的终结点信息，只要以此为基础来构建`GrpcChannel`即可。根据这个原理，我们引申出了`gRPC`客户端负载均衡的相关话题，这里我们采用的是随机选择一个终结点信息的做法，事实上，按照一般负载均衡的理论，我们还可以采取轮询、加权、Hash等等的算法，大家可以按照自己的业务场景来选择合适的方法。最后，我们简单介绍了下`gRPC`接口测试方面的内容，它可以帮助我们更高效地编写、验证`gRPC`接口。好了，以上就是这篇博客的全部内容啦，欢迎大家在评论区留言、参与讨论，谢谢大家！
