---
abbrlink: 4116164325
categories:
- 编程语言
date: 2019-08-06 23:02:5
description: 这个接口位于`System.Web.Http.Description`命名空间下，而显然这是WebApi相关的命名空间，所以，对于一般的WebApi项目，因为微软已经帮我们实现了默认的ApiExplorer，所以，Swagger可以识别出项目中的Controller及其Action，并通过XML注释文档进一步填充接口相关的描述信息;我们的想法是通过反射取出所有的MVC控制器及其Action，然后组织出这些接口的描述信息，再将它们添加到默认的IApiExplorer实现中去，这样MVC和WebApi都可以被Swagger识别，为此，我们继承默认的ApiExplorer，并实现我们自定义的`MvcApiExplorer`：;一旦想到这一层，我们就会明白，为什么Swagger不支持MVC项目，因为MVC里压根就没有实现IApiExplorer接口啊
tags:
- Swagger
- MVC
- WebApi
title: 通过ApiExplorer为Swagger提供MVC扩展
---

我一直想吐槽下运维同事提供的Jekins项目模板，因为它居然不支持含有多个项目的解决方案。作为一个有追求的程序员，每个解决方案下最少应该含有两个项目，即项目本身和项目对应的单元测试。可惜在这样一种情形下，我没法再去坚持这样的原则，而这真正让我感到难过的是，为了在编译环节向Jekins妥协，大家在一个项目里极尽所能，在这一个项目里居然混合了`MVC`、`WebApi`和`WebService`三种技术，甚至到最后连传统三层的界限都越来越模糊了。这让我意识到一件事情，工程上的妥协和技术选型一样，在某种意义上它们都不能被称之为科学，因为确实没什么道理，完全是运维为了方便而制造出的问题。在我们意识到文档的重要性以后，写文档就变成了日常工作。我一直坚持的原则是，文档能通过工具生成就坚决不要手写，所以，看到项目目录里充斥着各种各样的文档格式，譬如Word、Excel、Pdf、Viso等等的时候，我毅然决然地选择了Swagger。而今天这篇文章的原由，恰恰来自于这个"混搭"的项目。说到这里，你可能已经想到我想做什么了。不错，我们有部分WebApi是写在MVC的控制器里的，我希望使用者可以通过Swagger看到这部分接口的文档，这样我就有时间在这里写博客了。😄

# 故事缘起

常规的Swagger的使用就不再说啦，因为基本上你通过Nuget安装完`Swashbuckle`以后，再配置下项目生成的XML注释文档就可以使用啦！不过，博主在这里遇到的第一个问题就是，按照常规套路配置好了以后，Swagger页面打开完全就是空白的啊，反复尝试直至怀疑人生后，我突然意识到，莫非是因为我这是一个MVC的项目？立马跑到官方的Issues下面逐个扫视，果不其然，大佬们一致给出了答案：**Swagger是不支持MVC类型的项目的**。这里补充说明，这里的MVC是指`ASP.NET MVC`。目前官方主推的`ASP.NET Core`是没有这种困惑的啦，因为微软在这个新版本中统一了MVC和WebApi。对于这种历史“遗留问题”，既然Swagger官方都不愿意提供支持，那么，博主只好勉为其难的提供一个实现，我不得不承认，带着历史包袱的ASP.NET在扩展性上的确不如全新的“Core”系列，因为单单是`System.Web`系列的动态链接库版本就令人痛苦不堪，因此，博主在写这个扩展的时候，全部升到了最新的5.2.7.0。

# 实现MvcApiExplorer

好了，Swagger之所以能够生成友好、可交互的API文档，其核心依赖于IApiExplorer接口。这一点，我们可以通过Swashbuckle项目中的源代码来得到验证。其中，生成符合Swagger规范的JSON文档，是通过SwaggerGenerator这个类来实现的。而进一步研究这个类，我们就会发现它依赖`IApiExplorer`接口。这个接口位于`System.Web.Http.Description`命名空间下，而显然这是WebApi相关的命名空间，所以，对于一般的WebApi项目，因为微软已经帮我们实现了默认的ApiExplorer，所以，Swagger可以识别出项目中的Controller及其Action，并通过XML注释文档进一步填充接口相关的描述信息。一旦想到这一层，我们就会明白，为什么Swagger不支持MVC项目，因为MVC里压根就没有实现IApiExplorer接口啊！那么，怎么办呢？我们的想法是通过反射取出所有的MVC控制器及其Action，然后组织出这些接口的描述信息，再将它们添加到默认的IApiExplorer实现中去，这样MVC和WebApi都可以被Swagger识别，为此，我们继承默认的ApiExplorer，并实现我们自定义的`MvcApiExplorer`：

```CSharp
public class MvcApiExplorer : ApiExplorer 
{
    /// <summary>
    /// HttpConfiguration
    /// </summary>
    private HttpConfiguration _configuration;

    public MvcApiExplorer (Assembly assembly, HttpConfiguration configuration) : base (configuration) 
    {
        _configuration = configuration;
        assembly.GetTypes ()
            .Where (type => typeof (IController).IsAssignableFrom (type) && type.Name != "ErrorController" && type.BaseType != typeof (ApiController))
            .ToList ().ForEach (controller => 
            {
                base.ApiDescriptions.AddRange (BuildControllerApiDescription (controller));
            });
    }

    /// <summary>
    /// ApiExolorer for Action is visible
    /// </summary>
    /// <param name="actionVariableValue"></param>
    /// <param name="actionDescriptor"></param>
    /// <param name="route"></param>
    /// <returns></returns>
    public override bool ShouldExploreAction (string actionVariableValue, HttpActionDescriptor actionDescriptor, IHttpRoute route) => true;

    /// <summary>
    /// ApiExolorer for Controller is visible
    /// </summary>
    /// <param name="controllerVariableValue"></param>
    /// <param name="controllerDescriptor"></param>
    /// <param name="route"></param>
    /// <returns></returns>
    public override bool ShouldExploreController (string controllerVariableValue, HttpControllerDescriptor controllerDescriptor, IHttpRoute route) => true;

    private List<ApiDescription> BuildControllerApiDescription (Type type) 
    {
        var controllerName = type.Name.Replace ("Controller", "");
        var methods = type.GetMethods (System.Reflection.BindingFlags.Instance | System.Reflection.BindingFlags.Public | BindingFlags.DeclaredOnly)
            .Where (m => typeof (ActionResult).IsAssignableFrom (m.ReturnType));

        var list = new List<ApiDescription> ();
        foreach (var method in methods)
        {
            var apiDescription = new ApiDescription ();
            apiDescription.ActionDescriptor = new MvcHttpActionDescriptor (method);
            apiDescription.ActionDescriptor.ControllerDescriptor = new HttpControllerDescriptor (_configuration, controllerName, type);
            apiDescription.HttpMethod = HttpMethod.Post;
            apiDescription.Route = new HttpRoute (string.Format ("{0}/{1}", controllerName, method.Name));
            apiDescription.RelativePath = string.Format ("{0}/{1}", controllerName, method.Name);
            apiDescription.Documentation = string.Empty;
            typeof (ApiDescription).GetProperty ("ParameterDescriptions").SetValue (apiDescription, BuildApiParameters (method));
            typeof (ApiDescription).GetProperty ("ResponseDescription").SetValue (apiDescription, new ResponseDescription () 
            {
                ResponseType = method.ReturnType,
                DeclaredType = method.DeclaringType,
                Documentation = string.Empty
            });
            list.Add (apiDescription);
        }

        return list;
    }

    private Collection<ApiParameterDescription> BuildApiParameters (MethodInfo methodInfo) 
    {
        return new Collection<ApiParameterDescription> (
            methodInfo.GetParameters ().Select (p => new ApiParameterDescription () 
            {
                Name = p.Name,
                Documentation = string.Empty,
                Source = ApiParameterSource.Unknown,
                ParameterDescriptor = new MvcHttpActionParameterDescriptor (p, new MvcHttpActionDescriptor (methodInfo)),
            }).ToList ());
    }
}
```

通过代码可以看出，实现MvcApiExplorer的过程，其实就是向ApiDescriptions集合中添加元素的过程。为此，我们通过程序集去反射所有实现了`IController接口`，同时其父类不是`ApiController`，并且方法返回值类型为`ActionResult`的所有类型，通过这个类型信息，我们进一步反射每个方法以及方法的参数，并把这些参数转换为ApiDescription类型需要的参数类型。在组织信息的过程中，有一部分属性被微软设计为只读，故而不得不通过反射的方式来解决。我们知道，MVC里默认的路由模板是：`{controller}/{action}`，这是WebApi里的特性路由流行以前默认的、最基础的路由。我们这里基于沿用这个规则，所谓“约定大于配置”，这可以为我们节省不少时间。MVC里的HTTP动词我全部使用了POST，这是因为MVC里真正控制一个方法是GET还是POST请求，其实是`JsonRequestBehavior`这个参数，当它设置为AllowGet时，该方法可以同时支持这两种HTTP动词。同样，在模模型绑定阶段，我全部使用了Unknown，因为MVC会尝试通过Body或者Form的形式来接受一个参数，这两个地方完全是来自MVC本身机制的限制，如果大家有更好的思路，欢迎大家在博客里留言。

一旦实现了自定义的MvcApiExplorer，我们就可以尝试用它来替换微软默认的实现。在ASP.NET中，我们通过`GlobalConfiguration.Configuration.Services.Replace()`方法来实现服务的替换。其实，这种思路在ASP.NET Core里依然存在，比如我们在实现动态WebApi时采用的`ControllerFeatureProvider`都属于服务替换，所不同的时，ASP.NET时代是通过一个内置的IoC容器来实现服务替换，而ASP.NET Core时代，我们显然有了更多的选择，甚至依赖注入渗透到了整个.NET Core的方方面面，这的确是一种相当大的进步。曾几何时，Javaer嘲笑我们只会拖控件，可今天的我们，Java里有的概念我们都有对应的实现，反倒是Java开始从C#身上学习那些有点“甜”的语法糖啦！的确，我们写了这么多代码，其实最关键的就只有下面这一句，住口！这明明是三行：

```CSharp
var assembly = typeof(DefaultMvcProject.MvcApplication).Assembly;
var apiExplorer = new MvcApiExplorer(assembly, GlobalConfiguration.Configuration);         GlobalConfiguration.Configuration.Services.Replace(typeof(IApiExplorer), apiExplorer);
```
OK，接下来我们简单写几个MVC的控制器，来验证下我们为Swagger编写的MVC控制。在此之前，请确保完成了Swagger的两步常规配置，即为Swagger引入XML注释文档、在项目属性中勾选XML注释文档。这是使用Swagger的最小配置，相信大家一定都知道啦！

```CSharp
 GlobalConfiguration.Configuration
     .EnableSwagger (c => {
         c.SingleApiVersion ("v1", "DefaultMvcProject");
         c.IncludeXmlComments ($"{System.AppDomain.CurrentDomain.BaseDirectory}/bin/DefaultMvcProject.XML");
     })
     .EnableSwaggerUi (c => {
         c.DocumentTitle ("My Swagger UI");
     });
```

两个非常简单的Controller，这里就不再贴代码啦！

![非常简单的Controller](https://ww1.sinaimg.cn/large/4c36074fly1g5sqi6pwx2j20kh0ggtav.jpg)

可以注意到，一切都工作的很好，我们在Swagger里可以看到我们编写的Api接口，并且可以直接对接口进行调试。因为MVC本身的原因，这些MVC控制器的注释都不会生成到XML注释文档里。所以，稍微有一点遗憾的地方就是，这些接口都没有对应注释。不过，这已经达到了本文最初的目的，至少我不用再去写文档，告诉使用者这个接口里有哪些参数，以及这个接口的地址是什么啦，说到底啊，懒惰是人类进步的阶梯。这篇博客里实现的扩展，我已经发布到Github上，并附带了一个简单的示例(不要想太多哦，就是这篇文章里的示例)，感兴趣的朋友可以自助研究，仓库地址为：[https://github.com/qinyuanpei/Swashbuckle.Extension.Mvc](https://github.com/qinyuanpei/Swashbuckle.Extension.Mvc)

![差一点就完美了](https://ww1.sinaimg.cn/large/4c36074fly1g5sqlzk1mrj211y0ifgn1.jpg)

# 本文小结

本文实现了一个针对MVC项目的Swagger扩展，它可以让你编写在MVC控制器里的API接口，像普通WebApi项目一样展示在Swagger里。其原理是继承并重写了`ApiExplorer`类，这是Swagger生成API文档的核心接口。好了，以上就是这篇文章的全部内容啦，写这种短小的文章没有那么累，希望大家读起来一样不会累吧，晚安，世界！