---
toc: true
title: gRPC 搭配 Swagger 实现微服务文档化
categories:
  - 编程语言
tags:
  - gRPC
  - Swagger
  - 微服务
  - 文档
copyright: true
abbrlink: 4056800047
date: 2021-09-28 14:13:32
---

有人说，程序员最讨厌两件事情，一件是写文档，一件是别人不写文档，这充分展现了人类双标的本质，所谓的“严于律人”、“宽于律己”就是在说这件事情。虽然这种听来有点自私的想法，是生物自然选择的结果，可一旦人类的大脑皮层在进化过程中产生了“理性”，就会试图去纠正这种来自动物世界的阴暗面。所以，人类双标的本质，大概还是因为这个行为本身就有种超越规则、凌驾于众人之上的感觉，毕竟每个人生来就习惯这种使用特权的感觉。回到写文档这个话题，时下流行的微服务架构，最为显著的一个特点是：仓库多、服务多、接口多，此时，接口文档的重要性就凸显出来，因为接口本质上是一种契约，特别在前后端分离的场景中，只要前、后端约定好接口的参数、返回值，就可以独立进行开发，提供一份清晰的接口文档就显得很有必要。在 RESTful 风格的 API 设计中，[Swagger](https://swagger.io/) 是最为常见的接口文档方案，那么，当我们开始构建以 gRPC 为核心的微服务的时候，我们又该如何考虑接口文档这件事情呢？今天我们就来一起探讨下这个话题。

# protoc-gen-doc 方案

当视角从 RESTful 转向 gRPC 的时候，本质上是接口的描述语言发生了变化，前者是 JSON 而后者则是 Protobuf，因此，gRPC 服务的文档化自然而然地就落在 Protobuf 上。事实上，官方提供了 [protoc-gen-doc](https://github.com/pseudomuto/protoc-gen-doc) 这个方案，如果大家阅读过我以前的博客，就会意识到这是 Protobuf 编译器，即 [protoc](https://github.com/protocolbuffers/protobuf/releases) 的插件，因为我们曾经通过这个编译器来生成代码、服务描述文件等等。protoc-gen-doc 这个插件的基本用法如下：

```shell
protoc \
  --plugin=protoc-gen-doc=./protoc-gen-doc \
  --doc_out=./doc \
  --doc_opt=html,index.html \
  proto/*.proto
```

其中，官方更推荐使用 Docker 来进行部署：

```shell
docker run --rm \
  -v $(pwd)/examples/doc:/out \
  -v $(pwd)/examples/proto:/protos \
  pseudomuto/protoc-gen-doc
```

默认情况下，它会生成 HTML 格式的接口文档，看一眼就会发现，就是那种传统的 Word 文档的感觉：

![通过 protoc-gen-doc 生成的接口文档](https://i.loli.net/2021/09/28/h756tJjApsGgcDW.png)

除此以外，这个插件还可以生成 Markdown 格式的接口文档，这个就挺符合程序员的审美，因为此时此刻，你眼前看到的这篇文章，就是通过 Markdown 写成的：

```shell
docker run --rm \
  -v $(pwd)/examples/doc:/out \
  -v $(pwd)/examples/proto:/protos \
  pseudomuto/protoc-gen-doc --doc_opt=markdown,docs.md
```

这个方案如果整合到 CI/CD 中还是挺不错的，传统的 Word 文档形式的接口文档，最主要的缺点是没有版本控制、无法实时更新，因为对于团队间的协作是非常不利的，我本身挺讨厌这种 Word 文档发来发去的。有时候，只有接口文档是不完美的，因为懒惰的人类希望你能提供个调用示例，最好是直接`Ctrl+C`、`Ctrl+V`这种程度的，对此，博主只有仰天长叹：悠悠苍天，此何人哉......

# Swagger 方案

考虑到，第一种方案没有办法对接口进行调试，所以，下面我们来尝试第二种方案，即整合 Swagger 的方案，可能有小伙伴会好奇，Swagger 还能和 Protobuf 这样混搭起来玩？目前，Swagger 是事实上的 [OpenAPI](https://swagger.io/specification/) 标准，我们只需要在 Protobuf 和 OpenAPI 规范间做一个适配层即可。还记得博主曾经为 ASP.NET MVC 编写的 Swagger [扩展](http://localhost:2333/posts/4116164325/)吗？没错，我们要再次“整活”了，首先，这里给出的是 OpenAPI 规范的定义：

```json
{
  "openapi": "3.0.1",
  "info": { },
  "servers": [ ],
  "paths": { },
  "components": { }
}
```
其中，`info` 节点里存放的是接口文档的基本信息，例如标题、作者、许可证等。`servers` 节点里存放的是接口所属服务的主机名、端口号等。`paths` 节点里存放的是每个 API 端点的信息，例如路由、请求参数、返回值等。`components` 节点里存放的是类型信息，例如请求参数、返回值中每个属性或者字段的具体类型等。一旦搞清楚了这些内容，我们发现这个里面最关键的两个信息是：`paths` 和 `components`，如果我们回过头来看 Protobuf 的声明文件，就会发现这两个东西，分别对应的是 `rpc` 和 `message`，如下图所示：

![Swagger 与 Protobuf 的对应关系](https://i.loli.net/2021/09/28/nPN5QgY2MWrGJBK.png)

通常情况下，我们使用 `Swashbuckle.AspNetCore.Swagger` 这个库来为 ASP.NET Core 项目提供 Swagger 支持，其中最为关键的是`ISwaggerProvider`接口，这里我们来尝试为 Protobuf 提供一个具体的实现：

```csharp
public class GrpcSwaggerProvider : ISwaggerProvider
{
    private readonly ISchemaGenerator _schemaGenerator;
    private readonly SwaggerGeneratorOptions _options;
    private readonly IApiDescriptionGroupCollectionProvider _apiDescriptionsProvider;
    private readonly GrpcSwaggerSchemaGenerator _swaggerSchemaGenerator;

    public GrpcSwaggerProvider(
        SwaggerGeneratorOptions options, 
        ISchemaGenerator schemaGenerator, 
        IApiDescriptionGroupCollectionProvider apiDescriptionsProvider,
        GrpcSwaggerSchemaGenerator swaggerSchemaGenerator
    )
    {
        _options = options;
        _schemaGenerator = schemaGenerator;
        _apiDescriptionsProvider = apiDescriptionsProvider;
        _swaggerSchemaGenerator = swaggerSchemaGenerator;
    }

    public OpenApiDocument GetSwagger(string documentName, string host = null, string basePath = null)
    {
        if (!_options.SwaggerDocs.TryGetValue(documentName, out OpenApiInfo info))
            throw new UnknownSwaggerDocument(documentName, _options.SwaggerDocs.Select(d => d.Key));

        var schemaRepository = new SchemaRepository(documentName);

        // Swagger Document
        var swaggerDoc = new OpenApiDocument
        {
            Info = info,
            Servers = BuildOpenApiServers(host, basePath),
            Paths = new OpenApiPaths() { },
            Components = new OpenApiComponents
            {
                Schemas = schemaRepository.Schemas,
                SecuritySchemes = new Dictionary<string, OpenApiSecurityScheme>(_options.SecuritySchemes)
            },
            SecurityRequirements = new List<OpenApiSecurityRequirement>(_options.SecurityRequirements)
        };

        // Swagger Filters
        var apiDescriptions = _apiDescriptionsProvider.GetApiDescriptions().Where(x => x.Properties["ServiceAssembly"]?.ToString() == documentName);
        var filterContext = new DocumentFilterContext(apiDescriptions, _schemaGenerator, schemaRepository);
        foreach (var filter in _options.DocumentFilters)
        {
            filter.Apply(swaggerDoc, filterContext);
        }

        // Swagger Schemas
        swaggerDoc.Components.Schemas = _swaggerSchemaGenerator.GenerateSchemas(apiDescriptions);
        var apiDescriptionsGroups = _apiDescriptionsProvider.ApiDescriptionGroups.Items.Where(x => x.Items.Any(y => y.Properties["ServiceAssembly"]?.ToString() == documentName));
        swaggerDoc.Paths = _swaggerSchemaGenerator.BuildOpenApiPaths(apiDescriptionsGroups);

        return swaggerDoc;
    }
}
```

这里的`OpenApiDocument`对应着 OpenAPI 规范中的定义的结构，我们需要返回一个`OpenApiDocument`，并对其`Components`和`Paths`属性进行填充，这部分工作由`GrpcSwaggerSchemaGenerator`类来完成。我们这里不会直接去解析 Protobuf 文件，而是利用`Google.Protobuf.Reflection`这个包来反射 Protobuf 生成的类，然后将其转化为 OpenAPI 规范中定义的结构，更多的细节，大家可以参考[这里](https://github.com/qinyuanpei/FluentGrpc.Gateway/blob/master/src/FluentGrpc.Gateway/Swagger/GrpcSwaggerSchemaGenerator.cs)。

接下来，在实现了`ISwaggerProvider`以后，我们还需要替换掉默认的实现：

```csharp
public static void AddGrpcGateway(
  this IServiceCollection services, 
  IConfiguration configuration, 
  Action<Microsoft.OpenApi.Models.OpenApiInfo> setupAction = null, 
  string sectionName = "GrpcGateway"
)
{
    var configSection = configuration.GetSection(sectionName);
    services.Configure<GrpcGatewayOptions>(configSection);

    var swaggerGenOptions = new GrpcGatewayOptions();
    configSection.Bind(swaggerGenOptions);

    var swaggerGenSetupAction = BuildDefaultSwaggerGenSetupAction(swaggerGenOptions, setupAction);
    services.AddSwaggerGen(swaggerGenSetupAction);

    // Replace ISwaggerProvider
    services.Replace(new ServiceDescriptor(
        typeof(ISwaggerProvider),
        typeof(GrpcSwaggerProvider),
        ServiceLifetime.Transient
    ));

    // Replace IApiDescriptionGroupCollectionProvider
    services.Replace(new ServiceDescriptor(
        typeof(IApiDescriptionGroupCollectionProvider),
        typeof(GrpcApiDescriptionsProvider),
        ServiceLifetime.Transient
    ));

    // GrpcDataContractResolver
    services.AddTransient<GrpcDataContractResolver>();

    // GrpcSwaggerSchemaGenerator
    services.AddTransient<GrpcSwaggerSchemaGenerator>();

    // Configure GrpcClients
    services.ConfigureGrpcClients(swaggerGenOptions);

    // AllowSynchronousIO
    services.Configure<KestrelServerOptions>(x => x.AllowSynchronousIO = true);
    services.Configure<IISServerOptions>(x => x.AllowSynchronousIO = true);
}
```
接下来，就是见证奇迹的时刻，gRPC 和 Swagger 牵手成功。从此，查阅和调试 gRPC 接口，我们有了更时尚的做法：

![ gRPC 成功牵手 Swagger ](https://i.loli.net/2021/09/28/Uj9Z3EcbQmdhriD.png)

调一下接口看看效果：

![ 通过 Swagger 调试 gRPC 接口](https://i.loli.net/2021/09/28/z9Umj6t5hcSQeTv.png)

可以注意到，此时，Swagger 中返回了我们期望的结果，事实上，只有 Swagger 还不足以令它运作起来，其中的诀窍是，博主利用终结点(**Endpoints**)动态创建了路由。关于这一点，博主曾在 [ASP.NET Core gRPC 打通前端世界的尝试](https://blog.yuanpei.me/posts/2167892202/) 这篇文章中提到过。最终，博主编写了一个更为完整的项目：[FluentGrpc.Gateway](https://github.com/qinyuanpei/FluentGrpc.Gateway)，而关于 Swagger 的这部分内容则成为了这篇博客的内容，如果大家对这个项目感兴趣的话，欢迎大家去做进一步的探索，欢迎大家 Star 和 PR，而到这里，这篇博客差不多就可以结尾啦！

# 本文小结

有时候，博主会不由地感慨，整个微服务架构的落地过程中，服务治理是花费时间和精力最多的环节，除了保证接口的稳定性，更多的时候，其实是不同的服务间相互打交道。那么，除了口头传达外，最好的管理接口的方式是什么呢？显然是接口文档。本文分享了两种针对 gRPC 的服务文档化的方案，第一种是由官方提供的 [protoc-gen-doc](https://github.com/pseudomuto/protoc-gen-doc)，它可以从 Protobuf 生成 HTML 或者 Markdown 格式的接口文档。第二种是由博主实现的 [FluentGrpc.Gateway](https://github.com/qinyuanpei/FluentGrpc.Gateway)，它实现了从 Protobuf 到 Swagger 的转换，只需要在项目中引入这个中间件，就可以把 gRPC 带进 Swagger 的世界，不管是查阅接口还是调试接口，都多了一种玩法，如果你还需要给非开发人员提供接口文档，那么，我觉得你还可以试试 [YAPI](http://yapi.smart-xwork.cn/)，只需要导入 Swagger 格式的服务描述信息即可，而这一步，我们已经实现了。好了，以上就是这篇博客的全部内容啦，谢谢大家！