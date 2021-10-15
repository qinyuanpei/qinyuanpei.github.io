---
abbrlink: 3687594958
categories:
- 编程语言
date: 2020-02-15 16:01:13
description: 下面，按照惯例，我们将实现一个“**Hello World**”级别的实例，即：通过 ELK 来收集一个 ASP .NET Core 应用的日志信息;所以，从今天开始，我将为大家带来
  **.NET Core + ELK 搭建可视化日志分析平台** 系列文章，希望大家喜欢;博主计划在接下来的篇幅中介绍`Logstash`/`FireBeat`管道配置、Docker 容器内的日志收集、以及自定义日志组件开发这些话题，希望大家继续关注我的博客
tags:
- .NET Core
- ELK
- 日志
- 监控
title: .NET Core + ELK 搭建可视化日志分析平台(上)
---

Hi，各位朋友，大家好！欢迎大家关注我的博客，我的博客地址是: [https://blog.yuanpei.me](https://blog.yuanpei.me)。今天是远程办公以来的第一个周末，虽然公司计划在远程两周后恢复正常办公，可面对着每天都有人离开的疫情，深知这一切都不会那么容易。窗外的阳光透过玻璃照射进屋子，这一切都昭示着春天的脚步渐渐近了。可春天来了，有的人却没有再回来。那些在 2019 年结束时许下的美好期待、豪言壮语，在这样一场灾难面前，终究是如此的无力而苍白。可不管怎么样，生活还是要继续，在这些无法出门的日子里，在这样一个印象深刻的春节长假里，除了做好**勤洗手**、**多通风**、**戴口罩**这些防疫保护措施以外，博主还是希望大家能够抽空学习，通过知识来充实这“枯燥"的生活。所以，从今天开始，我将为大家带来 **.NET Core + ELK 搭建可视化日志分析平台** 系列文章，希望大家喜欢。

# 什么是 ELK

当接触到一个新的事物的时候，我们最好是从它的概念开始入手。那么，什么是 ELK 呢？ELK，是`Elastaicsearch`、`Logstash`和`Kibana`三款软件的简称。其中，`Elastaicsearch`是一个开源的全文搜索引擎。如果你没有听说过它，那至少应该听说过`Lucene`这个开源搜索引擎。事实上，`Elastaicsearch`是`Lucene`的封装，它提供了`REST` API 的操作接口 。而`Logstash`则是一个开源的数据收集引擎，具有实时的管道，它可以动态地将不同的数据源的数据统一起来。最后，`Kibana`是一个日志可视化分析的平台，它提供了一系列日志分析的 Web 接口，可以使用它对日志进行高效地搜索、分析和可视化操作。至此，我们可以给 ELK 一个简单的定义：

> ELK 是一个集日志收集、搜索、日志聚合和日志分析于一身的完整解决方案。

下面这张图，展示了`Elastaicsearch`、`Logstash`和`Kibana`三款软件间的协作关系。可以注意到，`Logstash`负责从应用服务器收集日志。我们知道，现在的应用程序都是跨端应用，程序可能运行在 PC、移动端、H5、小程序等等各种各样的终端上，而`Logstash`则可以将这些不同的日志信息通过管道转换为统一的数据接口。这些日志将被存储到`Elasticsearch`中。我们提到`Elastaicsearch`是一个开源的全文搜索引擎，故而它在数据查询上相对传统的数据库有着更好的优势，并且`Elasticsearch`可以根据需要搭建单机或者集群。最终，`Kibana`从`Elasticsearch`中查询数据并绘制可视化图表，并展示在浏览器中。在最新的 ELK 架构中，新增了`FireBeat`这个软件，它是它是一个轻量级的日志收集处理工具(Agent)，适合于在各个服务器上搜集日志后传输给`Logstash`。

![ELK-01.png](https://i.loli.net/2020/02/15/mbJRXGo56YA9jQP.png)

总而言之，ELK 可以让我们以一种更优雅的方式来收集日志，传统的日志收集通常会把日志写到文件或者数据库中。前者，不利于日志的集中管理和查询；后者，则无法应对海量文本检索的需求。所以，使用 ELK 可以为我们带来下面这些便利：**分布式日志数据集中式查询和管理；系统监控，譬如对系统硬件和应用各个组件的监控；故障排查；报表功能；日志查询，问题排查，上线检查； 服务器监控、应用监控、错误报警；性能分析、用户行为分析、时间管理等等**。

# 如何安装 ELK

安装 ELK 的方式，首推以 Docker 方式安装。关于 Docker 的安装、使用请大家查阅官方文档：[https://docs.docker.com/](https://docs.docker.com/)。这里我假设大家都已经掌握了 Linux 和 Docker 的使用。首先我们拉取 ELK 镜像：

```bash
docker pull sebp/elk
```

接下来，我们利用此镜像来运行一个容器:

```bash
docker run -p 5601:5601 -p 9200:9200 -p 5044:5044 --name elk sebp/elk 
```

通常情况下，完成这两个步骤以后，我们就完成了 ELK 安装。此时，我们可以在浏览器中输入地址：`http//localhost:9200`，这是`Elasticsearch`的默认端口。如果浏览器中返回了了类似下面的信息，则表示 ELK 安装成功。这里是博主获得的关于`Elasticseach`的信息：

```json
{
  "name" : "elk",
  "cluster_name" : "elasticsearch",
  "cluster_uuid" : "GGlJrOvtT2uSfoHioLCWww",
  "version" : {
    "number" : "7.5.2",
    "build_flavor" : "default",
    "build_type" : "tar",
    "build_hash" : "8bec50e1e0ad29dad5653712cf3bb580cd1afcdf",
    "build_date" : "2020-01-15T12:11:52.313576Z",
    "build_snapshot" : false,
    "lucene_version" : "8.3.0",
    "minimum_wire_compatibility_version" : "6.8.0",
    "minimum_index_compatibility_version" : "6.0.0-beta1"
  },
  "tagline" : "You Know, for Search"
}
```
接下来，我们继续在浏览器中输入地址：`http://localhost:5601/app/kibana`。显然，这是`Kibana`的默认地址，至此**ELK**的“庐山真面目”**终于揭晓，首次安装完**ELK，`Kibana`的界面应该试类似下面这样：

![ELK的庐山真面目](https://i.loli.net/2020/02/15/uOQSCUxfWYManK6.png)

按照指引，我们可以添加示例数据来感受下**ELK**全家桶的魅力：

![ELK示例 - Global Flight Dashboard](https://i.loli.net/2020/02/15/j6xFzedsPf7y9gL.png)

这样，我们就完成**ELK**环境的快速搭建。下面，按照惯例，我们将实现一个“**Hello World**”级别的实例，即：通过 ELK 来收集一个 ASP .NET Core 应用的日志信息。为了让这个示例尽可能地简单一点，我们选择了直接向`Elasticsearch`写入日志的方式，这里选择的日志库是[Serilog](https://serilog.net/)。

# Hello ELK

本文所用的例子已发布到[Github](https://github.com/qinyuanpei/DynamicWebApi/tree/master/DynamicWebApi.Core)。首先，我们准备一个 ASP.NET Core 的项目，MVC 或者 Web API 都可以。接下来，在项目中引入三个依赖项：`Serilog`、`Serilog.Extensions.Logging`和`Serilog.Sinks.ElasticSearch`。对于前两个，如果大家用过`Log4Net`或者`NLog`应该会感到非常熟悉啦，这一点不在赘述。而第三个，从名字就可以看出来这是冲着`Elasticsearch`来的，因为这是这个系列的第一篇文章，所以，我们直接写`Elasticsearch`即可。`Logstash`管道相关的内容，是一个非常复杂的东西，我们会在下一篇文章中单独来讲。

接下来，主要是`Serilog`在 ASP.NET Core 中的配置。首先是`Startup`类，在构造函数中初始化`Serilog`：

```csharp
public Startup(IConfiguration configuration)
{
 Log.Logger = new LoggerConfiguration()
  .Enrich.FromLogContext()
  .MinimumLevel.Debug()
  .WriteTo.Elasticsearch(
  new ElasticsearchSinkOptions(new Uri("http://localhost:9200"))
  {
   MinimumLogEventLevel = LogEventLevel.Verbose,
   AutoRegisterTemplate = true
  })
  .CreateLogger();
 Configuration = configuration;
}

```
还记得`http://localhost:9200`这个地址是什么吗？不错，这是`Elasticsearch`的默认地址，所以，这部分代码主要的作用就是告诉`Elasticsearch`，接下来的日志信息都写到`Elasticsearch`中。为了让日志的信息更丰富一点，我们这里设置最小的日志事件级别为`Verbose`。

接下来，在`ConfigureServices()`方法中注册 ILogger 实例：
```csharp
services.AddLogging(loggingBuilder => loggingBuilder.AddSerilog(dispose: true));
```

接下来，在业务层增加日志：
```csharp
private readonly ILogger _logger = Log.Logger;
      
[HttpGet]
public double Add(double n1, double n2)
{
 _logger.Information($"Invoke {typeof(CoreCalculatorService).Name}/Add: {n1},{n2}");
 return n1 + n2;
}
```
至此，ELK 在 ASP.NET Core 中的集成已经全部结束，这意味着我们所有的日志都会写入到 ELK 中。那么，要到那里去找这些日志信息呢？且听博主娓娓道来。我们在`Kibana`中点击左侧导航栏最底下的设置按钮，然后再点击右侧的`Create index pattern`按钮创建一个索引。什么叫做索引呢？在`Elasticsearch`中索引相当于一张"表"，而这个“表”中的一条行记录则被称为`Document`，如图：

![为Kibana创建索引1](https://i.loli.net/2020/02/15/fywAlQcH45mId1F.png)

创建索引的时候，会发现列表中列出了目前`Elasticsearch`中可用的数据。以博主为例，这里的`logstash-2020.02.15`就是本文中的 ASP.NET Core 应用产生的日志信息。在这里，我们可以通过一个模糊匹配来匹配同种类型的数据。通常这里需要我们选择一个过滤字段，我们选择时间戳即可：

![为Kibana创建索引2](https://i.loli.net/2020/02/15/8fD1EabSUV7OeZM.png)

创建完索引，就可以看到目前收集的日志信息了，在此基础上，我们可以做进一步的检索、过滤，来生成各种各样的“查询”。而每一个“查询”实际上就是一个数据源。我们就可以利用这些数据源来完成可视化，这是利用 ELK 进行可视化分析的一般流程：

![在Kibana中查看当前日志信息](https://i.loli.net/2020/02/15/m5jufkQW4qEiZAJ.png)

下面是博主自己制作的一个简单的可视化看板，果然很长时间没有再用过`Kibana`，我都快忘记了要怎么做一个折线图。这实在是一篇迟到的博客，我早该在 2019 年的时候就完成这个系列的，这要命的拖延症啊，虽然没有新冠病毒恐怖，可终究不是什么好习惯！

![一个简单的可视化看板](https://i.loli.net/2020/02/15/me7v2LBIOCUfM5a.png)

# 本文小结
这篇博客是这个系列的第一篇，是一篇珊珊来迟的博客，因为博主早在 2019 年就开始着手学习 ELK。考虑最新公司有使用 ELK 的打算，而因疫情又让博主有充足的时间，所以，博主决定把 ELK 相关的内容花点时间梳理出来。ELK 是一个集日志收集、搜索、日志聚合和日志分析于一身的完整解决方案。博主计划在接下来的篇幅中介绍`Logstash`/`FireBeat`管道配置、Docker 容器内的日志收集、以及自定义日志组件开发这些话题，希望大家继续关注我的博客。以上就是这篇博客的全部内容啦，晚安！