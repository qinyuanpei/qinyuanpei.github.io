---
toc: true
title: 浅议非典型 Web 应用场景下的身份认证
categories:
  - 编程语言
tags:
  - gRPC
  - SignalR
  - Kafka
copyright: true
abbrlink: 2478147871
date: 2021-12-28 11:53:29
---
据我所知，软件行业，向来是充满着鄙视链的，人们时常会因为语言、框架、范式、架构等等问题而争执不休。不必说 PHP 到底是不是世界上最好的语言，不必说原生与 Web 到底哪一个真正代表着未来，更不必说前端与后端到底哪一个更有技术含量，单单一个 C++ 的版本，1998 与 2011 之间仿佛隔了一个世纪。我真傻，我单知道人们会因为 GCC 和 VC++ 而分庭抗礼多年，却不知道人们还会因为大括号换行、Tab 还是空格、CRLF 还是 CR……诸如此类的问题而永不休战。也许，正如 [王垠](http://www.yinwang.org/) 前辈所说，编程这个领域总是充满着某种 [宗教原旨](http://www.yinwang.org/blog-cn/2015/04/03/paradigms) 的意味。回想起刚毕业那会儿，因为没有 Web 开发的经验而被人轻视，当年流行的 SSH 全家桶，对我鼓捣 Windows 桌面开发这件事情，投来无限鄙夷的目光，仿佛 Windows 是一种原罪。可时间久了以后，我渐渐意识到，对工程派而言，一切都是工具；而对于学术派而言，一切都是包容。这个世界并不是只有 Web，对吧？所以，这篇博客我想聊聊非典型 Web 应用场景下的身份认证。

# 楔子

在讨论非典型 Web 应用场景前，我们不妨来回想一下，一个典型的 Web 应用是什么样子？打开浏览器、输入一个 URL、按下回车、输入用户名和密码、点击登录……，在这个过程中，Cookie/Session用来维持整个会话的状态。直到后来，前后端分离的大潮流下，无状态的服务开始流行，人们开始使用一个令牌(Token)来标识身份信息，无论是催生了 Web 2.0 的 `OAuth 2.0` 协议，还是在微服务里更为流行的 `JWT(JSON Web Token)`，其实，都在隐隐约约说明一件事情，那就是在后 Web 时代，特别是微信兴起以后，人们在线与离线的边界越来越模糊，疫情期间居家办公的这段时间，我最怕听到 Teams 会议邀请的声音，因为无论你是否在线，它都会不停地催促你，彻底模糊生活与工作的边界。那么，屏幕前聪明的你，你告诉我，什么是典型的 Web 应用？也许，我同样无法回答这个问题，可或许，下面这几种方式，即 gRPC、SignalR 和 Kafka，可以称之为：非典型的 Web 应用。



# gRPC

相信经常阅读我博客的朋友，都知道这样一件事情，那就是，过去这半年多的时间，我一直在探索，如何去构建一个以 gRPC 为核心的微服务架构。想了解这方面内容的朋友，不妨抽空看看我前面写过的博客。从整体上来说，我们对于 gRPC 的使用上，基本可以分为对内和对外两个方面。对内，不同的服务间通过 gRPC 客户端互相通信，我们称之为：直连；对外，不同的服务通过 Envoy 代理为 JSON API 供前端/客户端消费，我们称之为：代理。一个简单的微服务示意图，如下图所示：

![gRPC 微服务中的内与外](gRPC-MicroService.drawio.png)

目前，这个方案最大的问题，不同的服务间通过 gRPC 客户端直连的时候，无法提供身份认证信息，因为如果是单纯的读，即从某一个服务查询数据，其实是可以接受这种“裸奔”的状态，可一旦涉及到了写，这种方案就显得不大严谨。譬如现在的做法，如果从 `HttpContext` 里提取不到用户信息，就默认当前用户是 Sys，表示这是一个系统级别的操作。那么，如何解决这个问题呢？我们一起来看一下：

```csharp
var channel = GrpcChannel.ForAddress("https://localhost:5001");
var client = new Greeter.GreeterClient(channel);

var metadata = new Metadata();
metadata.Add("Authorization", $"Bearer {token}");

var reply = client.SayHello(new HelloRequest(), metadata);
```

可以注意到，这里的关键是构造一个`Metadata`，并在其中传入`Authorization`头部。当然，这一切的前提是你遵循并且沿用了 [ ASP.NET Core 身份验证](https://docs.microsoft.com/zh-cn/aspnet/core/security/authentication/identity?view=aspnetcore-3.0&tabs=visual-studio)，这里以最常见的 JWT 认证为例：

```csharp
services.AddAuthentication(x =>
{
   x.DefaultAuthenticateScheme = JwtBearerDefaults.AuthenticationScheme;
   x.DefaultChallengeScheme = JwtBearerDefaults.AuthenticationScheme;
} ).AddJwtBearer(x =>
{
   x.RequireHttpsMetadata = false;
   x.SaveToken = true;
   x.TokenValidationParameters = new TokenValidationParameters
  {
     ValidateIssuerSigningKey = true,
     IssuerSigningKey = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(jwtOptions.Secret)),
     ValidIssuer = jwtOptions.Issuer,
     ValidAudience = jwtOptions.Audience,
     ValidateIssuer = true,
     ValidateAudience = true,
   };
});
```

通常情况下，这里的`IssuerSigningKey`由一个证书文件来提供，例如最常用的是`X509SecurityKey`类。为了方便演示，这里采用一组字符串进行签名。不管采用哪一种方式，我们都应该保证它与生成令牌时的参数一致。例如，下面是一个典型的生成  `JWT` 令牌的代码片段：

```csharp
var claims = new[]
{
   new Claim(ClaimTypes.Name, userInfo.UserName),
   new Claim(ClaimTypes.Role, userInfo.UserRole)
};

var signKey = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(_jwtOptions.Value.Secret));
var credentials = new SigningCredentials(signKey, SecurityAlgorithms.HmacSha256);
var jwtToken = new JwtSecurityToken(
   _jwtOptions.Value.Issuer,
   _jwtOptions.Value.Audience, 
   claims, 
   expires: DateTime.Now.AddMinutes(_jwtOptions.Value.AccessExpiration), 
   signingCredentials: credentials
);

token = new JwtSecurityTokenHandler().WriteToken(jwtToken);
```

 除了以上两点，请确保你的正确地配置了认证和授权两个中间件，注意它们的顺序和位置：

```csharp
public void Configure(IApplicationBuilder app, IWebHostEnvironment env)
{
    // ...
    app.UseRouting();
    // 注意顺序
    app.UseAuthentication();
    app.UseAuthorization();
    app.UseEndpoints(endpoints =>
   {
       endpoints.MapGrpcService<GreeterService>();
   });
}
```

此时，我们就可以在 gRPC 中通过`IHttpContextAccessor`获取当前用户信息：

```csharp
public override Task<HelloReply> SayHello(HelloRequest request, ServerCallContext context)
{
    var userName = _httpContextAccessor.HttpContext.User?.Identity.Name;
    return Task.FromResult(new HelloReply { Message = $"Hello {userName}"});
}
```

当然，考虑到我们使用 gRPC 客户端工厂的场景更多一点，我们更希望这个令牌可以在一开始就准备好，而不是每调用一个方法都需要传一次令牌。此时，我们可以使用下面的做法：

```csharp
services.AddGrpcClient<Greeter.GreeterClient>(o =>
{
    o.Address = new Uri("https://localhost:5001");
}).ConfigureChannel(o =>
{
    var credentials = CallCredentials.FromInterceptor((context, metadata) =>
    {
      if (!string.IsNullOrEmpty(_token)
        metadata.Add("Authorization", $"Bearer {_token}");
      return Task.CompletedTask;
    });

    o.Credentials = ChannelCredentials.Create(new SslCredentials(), credentials);
});
```

至此，关于 gRPC 的身份认证问题终于得到了解决，无论是对内的直连还是对外的代理，我们都可以获得用户的身份信息。需要说明的是，默认情况下，gRPC  允许调用方在不携带令牌的情况下调用接口，所以，我们这里的认证方案更像是一种君子协定。如果希望做更严格的限制，可以考虑在具体的服务上添加 `[Authorize]`特性，就像我们在控制器上使用该特性一样。

# SignalR
[SignalR](https://docs.microsoft.com/zh-cn/aspnet/core/signalr/introduction?view=aspnetcore-6.0) 是由微软提供的一面向实时 Web 应用的、开源的库，你可以认为，它是集 [WebSockets](https://docs.microsoft.com/zh-cn/aspnet/core/fundamentals/websockets?view=aspnetcore-6.0)、Server-Sent 事件 和 长轮询于一身的综合性的库。当你需要从服务端实时地推送消息到特定的客户端(组)的时候，SignalR 将会是一个不错的选择。譬如可视化的仪表盘或者监视系统，需要接收数据的变更通知以实时地刷新视图；即时通讯(IM)、社交网络、邮件、游戏、协作等方面地应用都需要及时地发出通知。ASP.NET Core 版本的 SIgnalR 在自动处理连接管理方面做出来不小的改善，可很多时候，SIgnalR 里面的 ConnectionId 对我们而言是没有意义的，我们更想知道连接到 Hub 的用户是谁，这样就催生出来 SignalR 身份认证的需求场景，下面，我们就来看看对应的 [解决方案](https://docs.microsoft.com/zh-cn/aspnet/core/signalr/authn-and-authz?view=aspnetcore-6.0)。

```csharp
// 方式一、AccessTokenProvider 
var hubConnection = new HubConnectionBuilder()
  .WithUrl("http://localhost:5000/echohub",options =>
  {
    options.AccessTokenProvider = () => Task.FromResult("<Your Token>");
  })
  .WithAutomaticReconnect()
  .Build();


// 方式二、直接追加查询参数
var hubConnection = new HubConnectionBuilder()
  .WithUrl("http://localhost:5000/echohub?access_token=<Your Token>")
  .WithAutomaticReconnect()
  .Build();
```

首先，SignalR 的身份认证，整体上依然遵循 ASP.NET Core 里的这套认证/授权流程，所以，我们可以继续沿用 gRPC 这部分的代码。考虑到 SignalR 首次发起的是一个 GET 请求，通常的做法是在查询参数中追加令牌参数。当然，现在官方提供了`AccessTokenProvider`这个属性，允许你构造一个委托来提供令牌。接下来，为了让这个令牌更符合一般的场景，譬如，按照约定它应该出现在 HTTP 请求头的 `Authorization` 字段上，我们有下面两种方式来对它进行处理：

```csharp
// 方式一、设置 JwtBearer 的 Events 属性
services.AddAuthentication(x =>
{
  //...
})
.AddJwtBearer(x =>
{
  //...
  x.Events = new JwtBearerEvents()
  {
    OnMessageReceived = context =>
    {
      var accessToken = context.Request.Query["access_token"];
      var path = context.HttpContext.Request.Path;
      if (!string.IsNullOrEmpty(accessToken) && (path.StartsWithSegments("/echohub")))
        context.Token = accessToken;
      return Task.CompletedTask;
    }
  };
});

// 方式二，编写中间件，注意顺序
app.Use((context, next) =>
{
  var accessToken = context.Request.Query["access_token"].ToString();
  var path = context.Request.Path;
  if (!string.IsNullOrEmpty(accessToken) && (path.StartsWithSegments("/echohub")))
    context.Request.Headers.Add("Authorization", new StringValues($"Bearer {accessToken}"));

    return next.Invoke();
});

app.UseAuthentication();
app.UseAuthorization();
```

可以注意到，不管是哪一种方式，核心目的都是为了让令牌能在 ASP.NET Core 的请求管道中出现在它期望出现的地方，这是什么地方呢？我想，应该是为执行认证/授权中间件以前，所以，为什么我说这两个中间件的顺序非常重要，原因正在于此，一旦我们做了这一点，剩下的事情就交给微软，我们只需要通过 `HttpContext` 的 `User` 属性获取用户信息即可。

```csharp
public Task Echo(string message)
{
  var userName = Context.User?.Identity?.Name;
  Clients.Client(Context.ConnectionId).SendAsync("OnEcho", $"{userName}:{message}");
  return Task.CompletedTask;
}
```

对于 SignalR 而言，同一个用户会对应多个 ConnectionId，当然，我并不需要过度地去关注这个东西，除非我们真的要分清每一个 ConnectionId 具体代表什么。类似地，SignalR 一样可以用 `[Authorized]` 特性来限制 Hub 是否可以在未认证的情况下使用，甚至它可以配合不同的 Policy 来做更细致的划分：

```csharp
public class UserRoleRequirement : 
  AuthorizationHandler<UserRoleRequirement, HubInvocationContext>, IAuthorizationRequirement
{
  protected override Task HandleRequirementAsync(
    AuthorizationHandlerContext context, UserRoleRequirement requirement, HubInvocationContext resource)
  {
    var userRole = context.User.Claims.FirstOrDefault(x => x.Type == ClaimTypes.Role)?.Value;
    if (userRole == "Admin" && resource.HubMethodName == "Echo")
      context.Succeed(requirement);

    return Task.CompletedTask;
  }
}
```

这里，我们定义了一个`UserRoleRequirement`类，其作用是仅仅允许`Admin`角色访问`Echo()`方法。此时，为了让这个策略生效，我们还需要将其注册到容器中，如下面的代码片段所示：

```csharp
services
  .AddAuthorization(options =>
  {
    options.AddPolicy("UserRoleRestricted", policy =>
    {
      policy.Requirements.Add(new UserRoleRequirement());
    });
  });
```

现在，我们可以在集线器(Hub)上控制 `Echo()` 方法访问权限，考虑到 `gRPC` 和 `SignalR` 都可以使用这套身份认证方案，所以，这个做法同样适用于 `gRPC`，如果你希望实现方法级的权限控制：

```csharp
[Authorize]
public class EchoHub : Hub
{
  [Authorize("UserRoleRestricted")]
  public Task Echo(string message)
  {
    var userName = Context.User?.Identity?.Name;
    Clients.Client(Context.ConnectionId).SendAsync("OnEcho", $"{userName}:{message}");
    return Task.CompletedTask;
  }
}
```
# Kafka

无独有偶，除了 SignalR ，我们还用到了消息中间件 Kafka，事实上，SignalR 会从 Kafka 拉取消息，并将其发布到订阅了该 Topic 的客户端上，所以，Kafka 在整个系统中，其实扮演着非常重要的角色。如果你只是需要让 Kafka 充当一个消息中介者，那么，你完全不需要考虑 Kafka 的身份认证问题。可一旦你考虑用 Kafka 来做具体的业务，这个问题就会立刻凸显出来。譬如，当我们用 Kafka 来实现一个分布式事务的时候，我们采用了 SAGA 模式，即让主事务负责事务的协调，每个子事务在收到主事务的消息后，执行相应的操作并回复主事务一条消息，再由主事务来决定整个事务应该提交还是回滚。如图所示，下面是一个针对 SAGA 模式的简单示意图：

![分布式事务 SAGA 模式示意图](Kafka-Distributed-Transaction.drawio.png)

关于这个模式的细节，感兴趣的朋友可以从 [这里](https://docs.microsoft.com/zh-cn/azure/architecture/reference-architectures/saga/saga) 获取。这里我想说的是，当我们尝试用 Kafka 来做具体的业务的时候，我们其实是无法获得对应的用户信息的，因为此时此刻，基于 ASP.NET Core 的管道式的洋葱模型，对我们而言是暂时失效的，所以，我一直在说的非典型 Web 应用，其实可以指脱离了洋葱模型、脱离了授权/认证流程的这类场景。和 gRPC 类似，当我们需要用户信息，而又无法获得用户信息的时候，该怎么办呢？答案是在 Kafka 的消息中传递一个令牌(Token)，下面是一个简单的实现思路：

```csharp
var producerConfig = new ProducerConfig { BootstrapServers = "192.168.50.162:9092" };
using (var p = new ProducerBuilder<Null, string>(producerConfig).Build())
{
    var token = "<Your Token>";
    var topic = “<Your Topic>";
    var document = new { Id = "001", Name = "张三", Address = "北京市朝阳区", Event = "喝水未遂" };
    var message = new Message<Null, string> { Value = JsonConvert.SerializeObject(document) };
    // 在 Kafka 消息头里增加 Authorization 字段
    message.Headers = new Headers();
    message.Headers.Add("Authorization", Encoding.UTF8.GetBytes($"Bearer {token}"));
    var result = await p.ProduceAsync(topic, message);
}
```

显然，这是非常朴素的一个想法，发送 Kafka 消息的时候，在 Kafka 的消息头里增加 `Authorization`字段，完美借鉴`HTTP`协议里的做法。那么，相对应地，消费 Kafka 消息的时候需要做一点调整，因为 Kafka 完全独立于 ASP.NET Core 的请求管道，所以，校验令牌的工作此时需要我们来独立完成。不过，请放心，这一切不会特别难，因为`JwtSecurityTokenHandler`这个类我们已经在前面用过一次：

```csharp
var consumerConfig = new ConsumerConfig { BootstrapServers = "127.0.0.1:9092" };
using (var c = new ConsumerBuilder<Null, string>(consumerConfig).Build())
{
    c.Subscribe("<Your Topic");

    var cts = new CancellationTokenSource();
    var jwtHandler = new JwtSecurityTokenHandler();
    var tokenParameters = new TokenValidationParameters()
    {
      ValidateIssuerSigningKey = true,
      IssuerSigningKey = new SymmetricSecurityKey(Encoding.UTF8.GetBytes("<Your Secret>")),
      ValidIssuer = "<Your Issuer>",
      ValidAudience = "<Your Audience>",
      ValidateIssuer = true,
      ValidateAudience = true,
    };

    while (true)
    {
        var userName = string.Empty;
        var consumeResult = c.Consume(cts.Token);
        var headers = consumeResult.Message.Headers;
        if (headers != null && headers.TryGetLastBytes("Authorization", out byte[] values))
        {
            // 校验令牌
            var jwtToken = Encoding.UTF8.GetString(values).Replace("Bearer", "").Trim();
            var claimsPrincipal = jwtHandler.ValidateToken(jwtToken, tokenParameters, out SecurityToken securityToken);
            userName = claimsPrincipal.Identity.Name;
            
            // 处理消息
            // ......
        }
    }
}
```
不过，我个人感觉，这样会增加消息消费方的工作，更好的做法是采用 `CallContext` 或者 `AsyncLocal` 来做统一的处理，这样，消息订阅方只需要关心消息怎么处理即可，考虑到 Kafka 属于 Pull 模式的消息队列，这种思路不见得在性能上有多少提升，更多的是一种简化啦，算是少写一点重复代码：

```csharp
public static void Subscribe<TKey, TValue>(
  this IConsumer<TKey, TValue> consumer, string topic, 
  CancellationToken cancellationToken, Action<TValue> callback)
{
  consumer.Subscribe(topic);

  while (true)
  {
    try
    {
      var consumeResult = consumer.Consume(cancellationToken);
      if (consumeResult != null)
      {
        var headers = consumeResult.Message.Headers;
        if (headers != null && headers.TryGetLastBytes("Authorization", out byte[] values))
        {
          var jwtToken = Encoding.UTF8.GetString(values).Replace("Bearer", "").Trim();
          var userInfo = new JwtTokenResloverService().ValidateToken(jwtToken);
          UserContext.SetUserInfo(userInfo);
        }

        if (callback != null)
            callback(consumeResult.Message.Value);
      }
    }
    catch (ConsumeException e)
    {
      // ...
    }
  }
}
```

其中，`UserContext`内部利用`AsyncLocal`在不同线程间共享用户信息，这可以让我们在任意位置访问用户信息，因为该扩展方法中会调用一次`SetUserInfo()`方法，所以，只要在 Kafka 的消息头上维护了`Authorization`字段，就可以从中解析出常用的用户信息，譬如用户名、用户角色等等。当然，按照 [JWT](https://jwt.io/) 的 [规范](https://datatracker.ietf.org/doc/html/rfc7519)，我们最好还是不要在载荷(Payload)中存放敏感信息，如果需要更详细的信息，比如部门、权限等等，建议通过调接口或者查数据的库方式来实现。下面是`UserContext`的实现细节：

```csharp
static class UserContext
{
  private static AsyncLocal<UserInfo> _localUserInfo = new AsyncLocal<UserInfo>();
  public static void SetUserInfo(UserInfo userInfo) => _localUserInfo.Value = userInfo;
  public static UserInfo GetUserInfo() => _localUserInfo.Value;
}
```

非常的简单，对不对? 作为 `CallContext` 的继任者，`AsyncLocal`就是这样的优秀！也许，大家会好奇`JwtTokenResloverService`是什么？其实，它还是`JwtSecurityTokenHandler`那一堆东西，下面的代码片段展示了如何从`ClaimsPrincipal`中提取用户名和角色名称，再次说明，不要在这里放敏感信息：

```csharp
var claimsPrincipal = _jwtHandler.ValidateToken(token, tokenParameters, out SecurityToken securityToken);
if (claimsPrincipal != null)
{
  var userInfo = new UserInfo();
  userInfo.UserName = claimsPrincipal.Identity.Name;
  userInfo.UserRole = claimsPrincipal.Claims.FirstOrDefault(x => x.Type == ClaimTypes.Role)?.Value;
  return userInfo;
}
```

现在，我们一开始的例子，可以简化成下面这样：

```csharp
var consumerConfig = new ConsumerConfig { BootstrapServers = "127.0.0.1:9092" };
using (var c = new ConsumerBuilder<Null, string>(consumerConfig).Build())
{
  var cts = new CancellationTokenSource();
  c.Subscribe("<Your Topic>", cts.Token, message =>
 {
    // 获取当前用户信息
    var userInfo = UserContext.GetUserInfo();
    // 处理消息
  });
}
```

Kafka 的故事，讲述到这里本该结尾，可世界上哪里会有完美的方案呢？如果考虑到 Kafka 发生消息堆积的可能性，一旦消息没有被及时处理，那么，这个放在消息头上的令牌可能会出现过期的情况。这种事情就和你使用缓存一样，如果不考虑缓存的击穿、穿透、雪崩三大灾难，那你对缓存的认知简直是肤浅。同样的道理，你要考虑令牌的过期、刷新、撤销，整个认知网络才算是真正建立起来，这些就交给我聪明的读者啦，或者以后有机会单独写一写这些话题。

# 本文小结

2021年的最后一天，西安疫情可谓是涛声依旧，居家隔离、远程办公、买不到菜，注定要为这段时光写下注脚。也许，我们都习惯了饭来张口的外卖生活，可在这一刻，当一切线下互动被迫中止的时候，我们终于发现这些“典型”的生活场景变得不再“典型”；当人们开始在微信群里用接龙的方式来寻求生活物资的时候，微信这个社交工具的缺点就被不断地放大；当人们逐渐回归到一种“以物易物”的状态时，我不得不感慨这种从骨子里与生俱来的生存本能；当人们习以为常的“典型”被打破，其本身是否就是一种舒适圈？无论技术还是生活，你是否有做好随时面对“非典型”场景的准备？我想，在与新冠病毒长期对峙的后疫情时代，这是每一个人都应该去思考的问题，这篇博客断断续续地写了好几天，大概 2021 终究还是要这般潦草的过去罢。因为，我是一个长期悲观主义者，我确信这个世界依旧遵循熵增定律。如果你打算反驳，我会说：你说得对。





