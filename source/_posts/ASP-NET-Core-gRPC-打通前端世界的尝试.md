---
abbrlink: 2167892202
categories:
  - 编程语言
tags:
  - gRPC
  - 微服务
  - 前端
  - Web
title: ASP.NET Core gRPC 打通前端世界的尝试
date: 2021-06-20 21:37:36
---

在构建以gRPC为核心的微服务架构的过程中，我们逐渐接触到了gRPC的过滤器、健康检查、重试等方面的内容。虽然， Protocol Buffers 搭配 HTTP/2 ，在整个传输层上带来了显著的性能提升，可当这套微服务方案面对前后端分离的浪潮时，我们能明显地有点“**水土不服**”。其实，如果单单是以 Protocol Buffers 来作为 HTTP 通信的载体，通过 [protobuf.js](https://github.com/dcodeIO/protobuf.js) 就可以实现前端的二进制化。考虑到 gRPC 实际的通信过程远比这个复杂，同时还要考虑`.proto`文件在前/后端共享的问题，所以，我们面对的其实是一个相当复杂的问题。现代的前端世界，是一个`React`、`Angular`和`Vue`三足鼎立的世界，如果这个世界不能和微服务的世界打通，我们面对的或许并不是一个真实的世界。因为博主注意到，项目中有一部分 gRPC 服务被封装为`Web API`并提供给前端，这说明大家都意识到了这个问题。所以，这篇博客想和大家分享的是，如何打通 gRPC 和 前端 两个不同的世界，这里介绍四种方式：**gRPC-Web**、**gRpc-Gateway**、**封装Web API**、**编写中间件**，希望能给大家带来一点启发。

# gRPC-Web

[gRPC-Web](https://github.com/grpc-ecosystem/grpc-gateway) 是官方提供的一个方案，它的原理是利用命令行工具`ptotoc`及其插件`protoc-gen-grpc-web`来生成`.proto`对应的客户端代码，这些代码经过`webpack`这类打包工具处理以后，就可以在前端使用。所以，对于 gRPC-Web ，你可以从两个方面来考虑它：第一，它支持生成强类型的客户端代码；第二，它支持在非 HTTP/2 环境下使用 gRPC 。下面是一个基本的使用流程：

首先，我们需要下载命令行工具：[protoc](https://github.com/protocolbuffers/protobuf/releases) 及其插件：[protoc-gen-grpc-web](https://github.com/grpc/grpc-web/releases)。

此时，我们可以使用下面的命令来生成`JavaScript`版本的 gRPC 代码：

```shell
protoc greetjs.proto \
  --js_out=import_style=commonjs:. \
  --grpc-web_out=import_style=commonjs,mode=grpcwebtext:. \
  --plugin=protoc-gen-grpc-web=C:\Users\Payne\go\bin\protoc-gen-grpc-web.exe
```

其中：
* `--js_out` 和 `--grpc-web_out` 分别指定了我们要生成的`JavaScript`代码的模块化标准，这里使用的是 [CommonJS](http://javascript.ruanyifeng.com/nodejs/module.html) 规范。
* `mode=grpcwebtext` 指定 gRPC-Web 的数据传输方式。目前：支持两种方式，application/grpc-web-text(Base64编码，文本格式) 和 application/grpc-web+proto(二进制格式)，前者支持 Unary Calls 和 Server Streaming Calls，后者只支持 Unary Calls。

在这个例子中，会生成下面两个文件，它们分别定义了`客户端`和`消息`这两个部分：

![利用 protoc 生成 JavaScript 代码](https://i.loli.net/2021/06/22/Yd9A5CEONkZgBjU.png)


此时，我们可以这样编写我们的逻辑代码：

```javascript
var client = new proto.greet.GreeterClient('http://localhost:8000');
var request = new proto.greet.HelloRequest();
var metadata = { }
request.setName('长安书小妆');
client.sayHello(request, metadata, function(error, response) {
    if (error) {
        console.log(error);
    } else {
        console.log(response.getMessage());
    }
});
```

如果你更倾向于使用类型安全的 TypeScript，你还可以按下面的方式来生成代码：

* import_style=commonjs+dts: CommonJS & .d.ts typings
* import_style=typescript: 100% TypeScript

更多的细节请参考官方文档：[https://hub.fastgit.org/grpc/grpc-web#typescript-support](https://hub.fastgit.org/grpc/grpc-web#typescript-support)

接下来，对于 .NET 开发者而言， gRPC-Web 意味着我们只需要简单地配置下 ASP.NET Core 的中间件管道，就可以享受到上面提供的这些便利。因为 Visual Studio 会在编译`.proto`文件时，自动帮你生成这个客户端代码，我们可以将这一技术应用到单页面应用(**SPA**) 和 WebAssembly 中，最典型的例子莫过于微软的 [Blazor](https://docs.microsoft.com/zh-cn/aspnet/core/blazor/?view=aspnetcore-5.0)，它使得 gRPC 可以充当客户端与服务端间的信使。同样地，这里准备了相关的示例代码：

```csharp
public void ConfigureServices(IServiceCollection services)
{
    services.AddGrpc();
}

public void Configure(IApplicationBuilder app, IWebHostEnvironment env)
{
    // ...
    app.UseGrpcWeb();
    app.UseEndpoints(endpoints =>
    {
        endpoints.MapGrpcService<GreeterService>().EnableGrpcWeb();
    );
}
```

如果大家留意一下微软官方的 [示例项目](https://hub.fastgit.org/grpc/grpc-dotnet/blob/master/examples/Browser/Server/wwwroot/Scripts/index.js)，就会发现和这里类似的东西，因为原理上一脉相承：

```javascript
const { HelloRequest, HelloReply } = require('./greet_pb.js');
const { GreeterClient } = require('./greet_grpc_web_pb.js');

var client = new GreeterClient(window.location.origin);

var nameInput = document.getElementById('name');
var sendInput = document.getElementById('send');
var streamInput = document.getElementById('stream');
var resultText = document.getElementById('result');

// Unary call
sendInput.onclick = function () {
    var request = new HelloRequest();
    request.setName(nameInput.value);

    client.sayHello(request, {}, (err, response) => {
        resultText.innerHTML = htmlEscape(response.getMessage());
    });
};
```

gRPC-Web 在将 gRPC 带入前端世界的过程中，其实是牺牲了一部分重要特性的，譬如浏览器中无法实现 HTTP/2，相对应地，gRPC-Web不再支持客户端流和双向流，依然支持服务端流，博主猜测可能是利用了服务端发送事件(**Server Sent Event**)。不过，这并不影响我们对这个项目的敬意，感谢它将 gRPC 带入了前端的世界。

# gRPC-Gateway

[gRPC-Gateway](https://github.com/grpc-ecosystem/grpc-gateway) 同样是命令行工具`protoc`的一个插件，其原理是，读取 gRPC 服务定义，并生成一个反向代理服务器，将 RESTful JSON API 转换为 gRPC 。而两者间的对应关系，则是通过`.proto`文件中的自定义选项来维护的。简单来说，就是在我们定义 gRPC 服务的同时，增加一组选项来表明这是一个 RESTful JSON API 。目前，这个插件只支持`Go`语言的代码生成。所以，如果想玩一玩这个插件，需要大家安装好`Go`的环境。

首先，我们从 [Github](https://hub.fastgit.org/protocolbuffers/protobuf/releases/tag/v3.6.1) 下载 Protocol Buffers 的编译器，它负责从从`.proto`文件生成代码。

这里我们选择 Windows 版本，直接将其解压到一个非中文的路径下即可。

![Protocol Buffers 的编译器](https://i.loli.net/2021/06/21/eTfGF9hI6cPSlwR.png)

这里，我们需要配置下面两个环境变量：

* PATH：C:\Program Files\Protobuf\bin
* PROTOC_INCLUDE：C:\Program Files\Protobuf\include

接下来，在`Go`环境中进行以下设置：

```shell
go env -w GO111MODULE=on
go env -w GOPROXY=https://goproxy.cn,direct
go install github.com/grpc-ecosystem/grpc-gateway/protoc-gen-grpc-gateway \
go install github.com/grpc-ecosystem/grpc-gateway/protoc-gen-swagger \
go install github.com/golang/protobuf/protoc-gen-go
```

这样，我们就通过`Go`完成了`protoc`的插件的安装。此时，我们可以通过下面的命令来生成`Go`代码：

```shell
# 生成Go的客户端代码
protoc --proto_path=. \
  --go_out=. \
  --plugin=protoc-gen-go=C:\Users\Payne\go\bin\protoc-gen-go.exe \
  ./greet.proto 

# 生成Go的反向代理服务器端代码
protoc \
  -I C:\Users\Payne\go\pkg\mod\github.com\grpc-ecosystem\grpc-gateway@v1.9.0\third_party\googleapis\ \
  --proto_path=. \
  --grpc-gateway_out=. \
  --plugin=protoc-gen-grpc-gateway=C:\Users\Payne\go\bin\protoc-gen-grpc-gateway.exe \
  ./greet.proto 
```

此时，我们可以得到下面两个`.go`格式的文件：

![通过 grpc-gateway 生成 Go 代码](https://i.loli.net/2021/06/22/wHvUzr5OybAtfkS.png)

关于反向代理服务器的观点的验证，大家可以从生成的第二个文件中去发现。

而关于 [gRPC-Gateway](https://github.com/grpc-ecosystem/grpc-gateway) 这个插件的使用，最直观的用法，其实应该来自`.proto`文件：

```
syntax = "proto3";

// Go里面的包名，必选
option go_package = "grpc-gateway/hello-word";

package greet;

// Google的API注解相关的.proto文件，必选
import "Protos/google/api/annotations.proto";

service Greeter {
  rpc SayHello (HelloRequest) returns (HelloReply) {
      option (google.api.http) = { 
          post: "/v1/greet/sayHello"
          body: "*" 
      };
  };
}

message HelloRequest {
  string name = 1;
}

message HelloReply {
  string message = 1;
}
```

考虑到博主并不擅长`Go`这门语言，这里我们就不再对它做进一步的探索啦！事实上，我觉得这个方案非常糟糕，因为只要修改了`.proto`文件，这个代理服务器就要重新生成，更不用说只支持`Go`这一显著的缺点啦！

# 封装 Web API

封装Web API，这是一个非常朴实无华的方案，博主目前的公司就是采用这种方案，所以，你能想象得到，基本就是在控制器中调用客户端。唯一的弊病在于，这是一个非常低效的工作。当年，博主的前公司，就是风风火火地要这样替换掉WCF，结果最终还是不了了之。所以说，世间没有银弹，历史不过是一次次地重复上演。下面是一个简单的示例：

```csharp
public async Task<ActionResult> SayHello(HelloRequestDTO requestDTO)
{
    var request = requestDTO.Adapt<HelloRequest>();
    var client = _serviceProvider.GetService<Greeter.GreeterClient>();
    var replay = await client.SayHelloAsync(request);
    return new JsonResult(replay);
}
```

而一旦做到这一层，其实我们是把一个未知的问题转化成一个已知的问题，这是数学家最常用的思路。

```javascript
var headers = new Headers();
headers.append("Content-Type", "application/json");

var options = {
   method: 'POST',
   headers: headers,
   body: JSON.stringify({name: '长安书小妆'}),
};

fetch("https://localhost:44372/Greet/SayHello", options)
   .then(response => response.json())
   .then(result => console.log(result))
   .catch(error => console.log(error));
```

那么，下一个问题，你打算用 Fetch API 还是 Axios 呢？这个问题就交给前端的朋友啦！因为，我是一个伪全栈工程师(逃。


# 编写中间件

其实，读到这里，你就会明白，这才是我真正要分享的内容，而此前种种，不过是我为了丰富这个话题而抛出的它山之石。既然觉得手写 Web API 太麻烦，那么我们能不能用一种新的思路来解决这个问题呢？这里说一下博主的思路，用户传入JSON，经过中间件反序列化为`.proto`对应的类型，我们将这个类型传递给 gRPC 的客户端作为请求参数，等拿到结果以后，我们再将它序列化为 JSON 即可。这样，我们就实现了将一个 gRPC 服务转化为 Web API 的想法。下面是具体的代码，其实这个代码并不复杂，我最初打算用反射来解决，可惜 gRPC 生成的这个客户端方法重载实在太多啦，所以，我最后决定用下面的这种方式。当然啦，缺点就和 gRPC-Gateway 一样，每一个接口都要单独写，好处大概是代码量减少了好多。

```csharp
// 定义扩展方法：AddGrpcGateway
public static void AddGrpcGateway<TClient,TRequest,TResponse>(
  this IApplicationBuilder app, 
  string route, 
  Func<string, TRequest> requestBuilder, 
  Func<TClient,TRequest,TResponse> responseBuilder
)
{
    app.UseEndpoints(endpoints => endpoints.MapPost(route, async context =>
    {
        using (var streamReader = new StreamReader(context.Request.Body))
        {
            var client = (TClient)app.ApplicationServices.GetService(typeof(TClient));

            var payload = await streamReader.ReadToEndAsync();
            var request = requestBuilder(payload);

            var reply = responseBuilder(client, request);
            var response = JsonConvert.SerializeObject(reply);

            await context.Response.Body.WriteAsync(Encoding.UTF8.GetBytes(response));
            context.Response.StatusCode = 200;
            context.Response.ContentType = "application/json";
        }
    }));
}
```

从代码中可以看出，这个方案依赖 gRPC 的客户端代码，同时需要读取 HTTP 的请求体，所以，我们还需要下面的代码作为辅助：

```csharp
public void ConfigureServices(IServiceCollection services)
{
    services.Configure<KestrelServerOptions>(x => x.AllowSynchronousIO = true);
    services.Configure<IISServerOptions>(x => x.AllowSynchronousIO = true);
    services.AddGrpcClient<Greeter.GreeterClient>(opt =>
    {
        opt.Address = new Uri("https://localhost:8001");
    });
}
```

接下来，我们通过中间件配置一个路由即可：

```csharp
// 建议放在 UseEndpoints() 方法下面
app.AddGrpcGateway<Greeter.GreeterClient, HelloRequest, HelloReply>(
    route: "greet/SayHello",
    requestBuilder: json => new MessageParser<HelloRequest>(() => new HelloRequest()).ParseJson(json),
    responseBuilder: (client, request) => client.SayHelloAsync(request).ResponseAsync.Result
);
```

为了证明这个中间件真的有用，我们用 [Apifox](https://www.apifox.cn/)  或者 [Postman](https://www.postman.com/downloads/) 测试一下看看。

![自定义中间件实现 gRPC 转 API 效果](https://i.loli.net/2021/06/21/hEmSVqOCy9tBbdv.png)

此时，可以看到，这就真的和调用一个 Web API 一样，我们完全意识不到，这是一个 gRPC 服务。你觉得，这样子算是达到目的了吗？

# 本文小结

其实，本文完全是临时想起来决定要写的一篇文章，起因就是看到了项目中有人在手动地封装 gRPC 服务为 RESTful 服务，当时就在想有没有一种方案，可以让这个过程稍微好一点点。所以，你可以认为，我写这篇博客的初衷，原来就是为了炫耀我写的那几行代码。不过，人到了一定的阶段以后，不管是写作还是思考，都似乎越来越喜欢某种框架结构，这种体验就有点像是上学时候写论文一样，虽然你明确地知道自己在做什么，可当你真正要把你的思路或者过程复述出来的时候，你还是需要有一个“文献综述”的环节。我个人以为，这是一种由外及内的认知方法，通过内外世界的对比来寻找自我提升的突破口。对于本文而言，不管是 [gRPC-Web](https://github.com/grpc-ecosystem/grpc-gateway) 还是 [gRPC-Gateway](https://github.com/grpc-ecosystem/grpc-gateway)，从本质上来讲，它们都是 Protocol Buffers 工具链中的插件，在这个过程中发现了平时使用 gRPC 过程中被隐藏了的一部分细节，这些细节如果能和开发工具完美结合的话，就可以极大地提升我们在 gRPC 方面的开发效率，譬如 gRPC-Web 在 .NET 中的实现就利用了 MSBuild 的自定义编译任务，这就让底层的Protocol Buffers 工具链、前端构建工具等对使用者来说是无感知的，从开发体验上就给人心旷神怡的感觉。我个人还是倾向于结合 ASP.NET Core 或者容器级别的 Envoy 来解决这个问题，我觉得应该还有更好的方案，希望大家可以在评论区写下你的想法。好啦，这篇博客就先写到这里，谢谢大家！
