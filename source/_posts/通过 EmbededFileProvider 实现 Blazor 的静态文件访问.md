---
toc: true
title: 通过 EmbededFileProvider 实现 Blazor 的静态文件访问
categories:
  - 编程语言
tags:
  - Blazor
  - .NET Core
  - 文件
  - WebAssembly
copyright: true
abbrlink: 3789745079
date: 2021-02-23 05:37:47
---
重构我的 [独立博客](https://blog.yuanpei.me) ，是博主今年的计划之一，这个基于 [Hexo](https://hexo.io/) 的静态博客，最早搭建于2014年，可以说是比女朋友更亲密的存在，陪伴着博主走过了毕业、求职以及此刻的而立之年。其间虽然尝试过像 [Jekyll](https://jekyllrb.com/) 和 [Hugo](https://www.gohugo.org/) 这样的静态博客生成器，可是考虑到模板、插件等周边生态，这个想法一直被搁置下来。直到最近，突然涌现出通过 [Blazor](https://docs.microsoft.com/zh-cn/aspnet/core/blazor/?view=aspnetcore-3.1) 重写博客的想法，尤其是它对于 [WebAssembly](https://webassembly.org/) 的支持，而类似 [Vue](https://cn.vuejs.org/) 和 [React](https://reactjs.org/)的组件化开发模式，在开发体验上有着同样不错的表现。所以，今天这篇博客就来聊聊在重写博客过程中的一点收获，即如何让 Blazor 访问本地的静态文件。

# 从内嵌资源说起

首先，我们要引入一个概念，即：内嵌资源。我们平时接触的更多的是本地文件系统，或者是 FTP 、对象存储这类运行在远程服务器上的文件系统，这些都是非内嵌资源，所以，内嵌资源主要是指那些没有目录层级的文件资源，因为它会在编译的时候“**嵌入**”到动态链接库(DLL)中。一个典型的例子是`Swagger`，它在`.NET Core`平台下的实现是[Swashbuckle.AspNetCore](https://github.com/domaindrivendev/Swashbuckle.AspNetCore)，它允许使用自定义的HTML页面。这里可以注意到，它使用到了`GetManifestResourceStream()`方法：

```csharp
app.UseSwaggerUI(c =>
{
    // requires file to be added as an embedded resource
    c.IndexStream = () => GetType().Assembly
        .GetManifestResourceStream("CustomUIIndex.Swagger.index.html"); 
});
```
其实，这里使用的就是一个内嵌资源。关于内嵌资源，我们有两种方式来定义它：

* 在 Visual Studio 中选中指定文件，在其属性窗口中选择生成操作为嵌入的资源：

![如何定义一个文件资源为内嵌资源](https://i.loli.net/2021/02/23/Zftpl5UFnmcLK49.png)

* 在项目文件(**.csproj**)中修改对应`ItemGroup`节点，参考示例如下：

```xml
<Project Sdk="Microsoft.NET.Sdk.Web">
<!-- ... -->
  <ItemGroup>
    <EmbeddedResource Include="_config.yml">
      <CopyToOutputDirectory>Always</CopyToOutputDirectory>
    </EmbeddedResource>
  </ItemGroup>
<!-- ... -->
</Project>
```

这样，我们就完成了内嵌资源的定义。而定义内嵌资源，本质上还是为了在运行时期间去读取和使用，那么，自然而然地，我们不禁要问，该怎么读取这些内嵌资源呢？在`Assembly`类中，微软为我们提供了下列接口来处理内嵌资源：

```csharp
public virtual ManifestResourceInfo GetManifestResourceInfo(string resourceName);
public virtual string[] GetManifestResourceNames();
public virtual Stream GetManifestResourceStream(Type type, string name);
public virtual Stream GetManifestResourceStream(string name);
```

其中，`GetManifestResourceNames()`方法用来返回所有内嵌资源的名称，`GetManifestResourceInfo()`方法用来返回指定内嵌资源的描述信息，`GetManifestResourceStream()`方法用来返回指定内嵌资源的文件流。为了方便大家理解，这里我们准备了一个简单的示例：

```csharp
var assembly = Assembly.GetExecutingAssembly();
var resources = assembly.GetManifestResourceNames();
resources.ToList().ForEach(x => Console.WriteLine(x));
//ConsoleApp.A.B.示例文档.txt
//ConsoleApp.A._config.yml
var fileInfo = assembly.GetManifestResourceInfo(resources[0]);
var fileStream = assembly.GetManifestResourceStream(resources[0]);
```

此时，我们会发现，内嵌资源都是使用类似`A.B.C.D`这样的形式来表示资源路径的，因为内嵌资源本身是没有目录层级的。现在，如果我们再回过头去看`Swagger`的示例，就不难理解为什么会有`CustomUIIndex.Swagger.index.html`这样一个奇怪的值，因为它对应着实际的物理文件路径，如下图所示，示例代码中输出的资源路径和实际的物理路径存在着对应关系：

![项目中的物理路径与内嵌资源路径对照](https://i.loli.net/2021/02/23/jgqxFTPt2OnHMyh.png)

# EmbededFileProvider

OK，那么在了解了内嵌资源以后，接下来，我们需要关注的是`EmbededFileProvider`。需要说明的是，在`ASP.NET Core`中，微软是通过`IFileProvider`这个接口来解决文件读取问题的，典型的使用场景有静态文件中间件、Rozar模板引擎以及WWWRoot目录定位等等，通常情况下，我们使用`PhysicalFileProvider`更多一点，它和`EmbededFileProvider`一样，都实现了`IFileProvider`接口，所以，`ASP.NET Core`可以从不同的来源访问文件信息。

显然，`EmbededFileProvider`正是为了内嵌资源而生，它在内部使用到了`Assembly`类中和内嵌资源相关的接口.所以，除了上面的方式，我们还可以通过下面的方式来访问内嵌资源，需要注意的是，使用`EmbededFileProvider`需要引用`Microsoft.Extensions.FileProviders.Embedded`，大家可以比较一下这两种方式地差异：

```csharp
var assembly = Assembly.GetExecutingAssembly();
var provider = new EmbeddedFileProvider(assembly);
//注意，这里写"."或者""都可以
var resouces = provider.GetDirectoryContents(".").ToList();
var fileInfo = provider.GetFileInfo(resouces[0]);
var fileStream = fileInfo.CreateReadStream();
```

除此以外，`IFileProvider`还有一个最重要的功能，即`Watch()`方法，它可以监听文件的变化，并返回一个`IChangeToken`。有没有一种似曾相识燕归来的感觉？没错，博主曾经在 [基于选项模式实现.NET Core的配置热更新](https://blog.yuanpei.me/posts/835719605/) 这篇文章中介绍过它，它是实现配置热更新的关键。事实上，`FileConfigurationSource`这个类中有一个`Provider`属性，而它对应的类型恰好是`IFileProvider`，这难道是巧合吗？不，仔细顺着这条线，我们大概就能明白微软的良苦用心，我们的配置文件自然是来自文件系统，而考虑到内嵌资源的存在，我们面对的文件系统其实是一个广义的文件系统，它可以是物理文件、内嵌文件、Glob、对象存储(**OSS**)等等

# Blazor的奇妙缘分

好了，千呼万唤始出来，现在终于要讨论 [Blazor](https://docs.microsoft.com/zh-cn/aspnet/core/blazor/?view=aspnetcore-3.1) 这个话题啦！众所周知，静态博客生成器里主要存在着两种配置，即站点配置和主题配置，[Hexo](https://hexo.io/) 里甚至还支持从特定文件夹里加载自定义的数据。所以，对于静态博客而言，它需要有从外部加载数据这个特性。我们知道，[Blazor](https://docs.microsoft.com/zh-cn/aspnet/core/blazor/?view=aspnetcore-3.1) 分为服务器和客户端两个版本，两者的区别主要在于 [Rozar](https://docs.microsoft.com/zh-cn/aspnet/core/mvc/views/razor?view=aspnetcore-5.0) 模板由谁来渲染，前者相当于服务端渲染(**SSR**) + [SignalR](https://docs.microsoft.com/zh-cn/aspnet/core/signalr/javascript-client?view=aspnetcore-5.0)，而后者则是基于 [WebAssembly](https://webassembly.org/)，它可以直接在浏览器中加载。显然，后者更接近我们静态博客生成器的想法。由于 Hexo 使用 Yaml 作为配置语言，所以，为了读取原来 Hexo 博客的配置，参考 [实现自己的.NET Core配置Provider之Yaml](https://www.cnblogs.com/nianming/p/7097338.html) 这篇博客实现了一个YamlConfigurationProvider。

在使用的过程中，遇到的问题是，它无法识别配置文件的路径。原因很简单，经过编译的 Blazor 会被打包为 WebAssembly ，而 WebAssembly 在前端加载以后，原来的目录层级早已荡然无存。此时，基于物理文件的 `PhysicalFileProvider` 将无法工作。解决方案其实大家都能想到，换一种`IFileProvider`的实现就好了啊！至此，奇妙的缘分产生了：

```csharp
class YamlConfigurationProvider : FileConfigurationProvider
{
    private readonly FileConfigurationSource _source;
    public YamlConfigurationProvider(FileConfigurationSource source) : base(source)
    {
        _source = source;
    }

    public override void Load()
    {
        var path = _source.Path;
        var provider = _source.FileProvider;
        using (var stream = provider.GetFileInfo(path).CreateReadStream())
        {
            //核心问题就是这个Stream的来源发生了变化
            var parser = new YamlConfigurationFileParser();
            Data = parser.Parse(stream);
        }
    }
```

其实，[官方文档](https://docs.microsoft.com/zh-cn/aspnet/core/blazor/fundamentals/configuration?view=aspnetcore-3.1)中提到过，Blazor 的配置文件默认从 WWWRoot 下的`appsettings.json`加载，所以，对于像JSON这类静态文件，可以注入HttpClient，以API的方式进行访问。例如，官方文档中推荐的加载配置文件的方式为：

```csharp
var httpClient = new HttpClient()
{
    BaseAddress = new Uri(builder.HostEnvironment.BaseAddress)
};

builder.Services.AddScoped(sp => httpClient);

//前方有语法糖，高甜:)
using var response = await http.GetAsync("cars.json");
using var stream = await response.Content.ReadAsStreamAsync();

builder.Configuration.AddJsonStream(stream);
```

而经过我们这样改造以后，我们还可以这样加载配置：

```csharp
builder.Configuration.AddYamlFile(
    provider:new EmbeddedFileProvider(Assembly.GetExecutingAssembly()),
    path: "_config.yml",
    optional:false,
    reloadOnChange:true
);
```

一旦这些配置注入到 IoC 容器里，我们就可以纵享无所不在的依赖注入，这里以某个组件为例：

```html
@using Microsoft.Extensions.Configuration
@inject IConfiguration Configuration

<div class="mdui-container-fluid">
    <div class="mdui-row DreamCat-content-header">
        <div class="mdui-container fade-scale in">
            <h1 class="title">@Configuration["title"]</h1>
            <h5 class="subtitle">@Configuration["subtitle"]</h5>
        </div>
    </div>
</div>
```

同样地，对于组件内的数据，在大多数场景下，我们可以这样来处理，还是因为有无所不在的依赖注入：

```html
@page "/"
@layout MainLayout

@inject HttpClient httpClient
@using BlazorBlog.Core.Domain.Blog;
@using BlazorBlog.Web.Shared.Partials;
@if (posts != null && posts.Any())
{
    foreach (var post in posts)
    {
        //这是一个自定义组件
        <PostItem Model=post></PostItem>
    }
}

@code
{
    private List<Post> posts { get; set; }
    protected override async Task OnInitializedAsync()
    {
        posts = await httpClient.GetFromJsonAsync<List<Post>>("content.json");
        await base.OnInitializedAsync();
    }
}
```

这里可以给大家展示下尚在开发中的静态博客：

![基于 Balzor 的静态博客](https://i.loli.net/2021/02/23/wMED8k6SbqITpma.png)

理论上任何文件都可以这样做，主要是考虑到配置这种信息，用依赖注入会更好一点，这样每一个组件都可以使用这些配置，而如果是以 API 的形式集成，以目前 Blazor 打包以后加载的效果来看，页面会有比较大的“**空白期**”。我更加疑惑的是，如果 Blazor 打包后的体积过大，那么浏览器自带的存储空间是否够用呢？一句话总结的话， Blazor 是一个写起来非常舒服的框架，可未来是否会像当年的 Sliverlight 一样，这还要看大家对 WebAssembly 的接受程度，可谓是“**路漫漫其修远兮**”啊……

# 本文小结

这篇博客，是博主由一个个“**闪念**”而串联起来的脑洞，作为一个实验性质的尝试，希望通过 Blazor 的客户端模式(**WebAssembly**) 实现一个静态博客，而在这个过程中，需要解决 Balzor 读取本地文件的问题，由此，我们引入了这篇博客的主题之一，即：`EmbededFileProvider`。顺着这条线索，我们梳理了内嵌的文件资源、`IFileProvider`接口、`FileConfigurationProvider`、`FileConfigurationSource`等等一系列看起来毫无关联的概念。事实上，“**冥冥之中自有天意**”，这一切怎么会毫无关联呢？我们最终从文件系统看到了配置系统，聊到了 Blazor 中的配置问题，这里我们熟悉的依赖注入、配置系统都得以延续下来。其实，单单就解决这个问题而言，完全不值得专门写一篇博客，**可从一个点辐射到整个面的这种感悟，在人生的成长中更显得弥足珍贵，希望我们每一个人都能多多跳脱出自己的视角，去努力的看一看这个丰富多彩的世界，在多样性与多元化中去寻找整体上的统一，这是作为技术人员的我，一生都想去探索的哲学**。好了，以上就是这篇博客的全部内容啦，欢迎大家在评论中留下你的想法或者建议，谢谢大家！