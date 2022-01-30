---
abbrlink: 116795088
categories:
- 编程语言
date: 2019-08-01 16:44:59
description: POCOController 是 ASP.NET Core 中提供的一个新特性，按照约定大于配置的原则，在 ASP.NET Core 项目中，所有带有 Controller 后缀的类，或者是使用了[Controller]标记的类，即使它没有像模板中一样继承 Controller 类，ASP.NET
  Core 依然会将其识别为 Controller，并拥有和普通 Controller 一样的功能，说到这里，你是不是有点兴奋了呢，因为我们在 ASP.NET 里花了大力气去做类似的事情，因为 ASP.NET 里一个普通的类是没有办法成为 Controller 的，即使通过 Castle 的 Dynamic
  Proxy 黑科技，我们依然需要去 Hack 整个 MVC 框架创建、筛选 Controller 和 Action 的过程;所以，我们希望在提供默认路由的基础上，使用者可以自由配置路由风格，所以，我们需要通过这个接口来构造路由信息，值得一提的是，我们可以在这个过程中设置 ApiExplorer 是否可见，为接口参数设置合适的绑定模型等等，所以，我们会使用 HttpGet/HttpPost 等来标记接口的调用方式，使用 Route 来标记用户自定义的路由信息，使用 FromBody/FromQuery 等来标记参数的绑定信息，有了这些配合 Swagger 简直是无往不胜，并非是开发人员不愿意写文档，而是因为文档的更新速度往往赶不上需求的变化速度，一旦文档落后于实际业务，这样的文档实际是没有意义的，我真的讨厌所有人都来找你问接口的地址、参数这些东西，如果你写完了一个 Service，写好对应的方法注释，然后你就有了一个可用的 Web
  API，和一个可用的在线文档，何乐而不为呢;这篇博客延续了上一篇博客中关于动态 Controller 的设想，而借助于.NET Core 框架提供的良好特性，它以一种更为简洁的方式被实现了，核心的内容有两个点，其一是 ControllerFeatureProvider，它能决定 MVC 会不会把一个普通的类当做控制器
tags:
- .NET Core
- API
- Web
- 技巧
title: .NET Core POCOController 在动态 Web API 中的应用
---

Hi，大家好，我是 Payne，欢迎大家关注我的博客，我的博客地址是：[<https://blog.yuanpei.me>](https://blog.yuanpei.me)。在上一篇文章中，我和大家分享了 ASP.NET 中动态 Web API 的实现，这种方案的现实意义是，它可以让我们把任意一个接口转换为 Web API，所以，不单单局限在文章里提到的 WCF 迁移到 Web API，任意领域驱动开发(DDD)中的服务层，甚至是更为普遍的传统三层，都可以通过这种方式快速构建前后端分离的应用。可能大家会觉得直接把 Service 层暴露为 API，会引发一系列关于鉴权、参数设置(`FromQuery`/`FromBody`)等等的问题，甚至更极端的想法是，这样和手写的没什么区别，通过中间件反射能达到相同的目的，就像我们每天都在写各种接口，经常有人告诉我们说，不要在 Controller 层写太重的业务逻辑，所以，我们的做法就是不断地在 Service 层里增加新接口，然后再把 Service 层通过 `Controller` 层暴露出来，这样子真的是对的吗？



可我个人相信，技术总是在不断向前发展的，大家觉得 RESTful 完全够用啦，结果 GraphQL 突然发现了。大家写了这么多年后端，其实一直都在绕着数据转，可如果数据库本身就支持 RESTful 风格的接口，或者是数据库本身就支持某种 ORM，我们后端会立马变得无趣起来。其实，在 ASP.NET Core 中已经提供了这种特性，这就是我们今天要说的 POCOController，所以，这也许是个正确的思路，对吧？为什么 Service 层本身不能就是 Controller 层呢？通过今天这篇文章，或许你会接受这种想法，因为 POCOController，就是弱化 Controller 本身的特殊性，一个 Controller 未必需要继承自 Controller，或者在名称中含有 `Controller` 相关的字眼，如果 Controller 同普通的类没有区别会怎么样呢？答案就是 Service 层和 Controller 层的界限越来越模糊。扪心自问，我们真的需要中间这一层封装吗？



# 什么是 POCOController

POCOController 是 ASP.NET Core 中提供的一个新特性，按照约定大于配置的原则，在 ASP.NET Core 项目中，所有带有 Controller 后缀的类，或者是使用了[Controller]标记的类，即使它没有像模板中一样继承 Controller 类，ASP.NET Core 依然会将其识别为 Controller，并拥有和普通 Controller 一样的功能，说到这里，你是不是有点兴奋了呢，因为我们在 ASP.NET 里花了大力气去做类似的事情，因为 ASP.NET 里一个普通的类是没有办法成为 Controller 的，即使通过 Castle 的 Dynamic Proxy 黑科技，我们依然需要去 Hack 整个 MVC 框架创建、筛选 Controller 和 Action 的过程。可在 ASP.NET Core 里这一切居然变成了一个新的 feature，所以，我预感到这篇文章应该不会像上一篇文章那么长，果然 9102 有 9102 的好处呢……好了，现在我们来写一个 POCOController：

```CSharp
public class MessageController
{
    public string Echo(string receiver)
   {
        return $"Hello, {receiver}";
   }
}
```

接下来，我们通过浏览器访问：`http://localhost:6363/Message/Echo?receiver=PayneQin`，我们就会发现一件非常神奇的事情，那就是，我们并没有真的在写一个 Controller，它没有继承 Controller 类，虽然它的名字里带着 Controller 的后缀，可它确实实现了一个 Controller 所具备的功能，因为它返回了我们期望的信息。

![欢迎来到POCOController的世界](https://ww1.sinaimg.cn/large/4c36074fly1g5j4wxhvuaj20kw0c075r.jpg)

可以注意到，这个 Controller 使用起来和普通的 Controller 是没有任何区别的，这正是我们想要的结果。对于.NET Core 而言，一个普通的类想要成为 POCOController，只需要满足以下任意一个条件：第一，继承自 Microsoft.AspNetCore.Mvc.Controller 类，无论是否带有 Controller 后缀，都可以作为 POCOController。第二，不继承自 Microsoft.AspNetCore.Mvc.Controller 类，同时引用了 Microsoft.AspNetCore.Mvc 相关的程序集。在这里，博主一开始就犯了这个错误，因为博主建的是一个 Web API 类型的项目。



# ControllerFeatureProvider

那么，为什么 ASP.NET Core 里可以实现如此炫酷的功能呢？这里要介绍到 ControllerFeatureProvider。在.NET Core 中，微软引入了应用程序部件的概念，顾名思义，它是对应用程序资源的一种抽象，通过这些应用程序部件， .NET Core 提供了发现和加载 MVC 组件，如控制器、视图(View)、标记(TagHelper)、Razor 等等的功能。在 MVC 中，这些功能由 ApplicationPartManager 对象来进行管理，它维护着一个叫做 FeatureProviders 的列表，以上这些功能分别对应一个 Feature，所以，当我们希望引入一个新的功能的时候，只需要实现 `IApplicationFeatureProvider<T>` 接口即可，而这里的 `ControllerFeatureProvider` 显然是提供控制器相关的 Feature，它有一个最为关键的接口 `IsController(TypeInfo)`。

回到一开始的话题，微软定义了一个类成为 POCOController 的规则，实际上我们同样可以定义自己的规则，譬如 ABP 框架中限定的接口约束是实现 IAppService 这个接口，那么我们就可以把一个程序集或者多个程序集里的类型识别为控制器，这就是 POCOController 的奥秘所在。在比如我们的项目中难免会有大量 CRUD 的垃圾需求，区别仅仅是它访问不同的仓储，我们可能会想写一个泛型的控制器来处理，可惜在过去的 ASP.NET 里，实现这一切并不太容易。为什么说不大容易呢？通过我们上一篇文章里动态路由的整个过程，大家就知道有多麻烦了啊，可在.NET Core 里要实现一个泛型的控制器就非常容易了啊，因为我们只需要告诉 ControllerFeatureProvider，这是一个控制器，并且控制器的类型就是这个泛型参数 T，所以，综上所述，ControllerFeatureProvider 主要做两个事情，第一，判定一个类型能不能算作 Controller；第二，对程序集里的类型进行筛选和过滤。下面，我们顺着这个思路来实现我们自己的 ControllerFeatureProvider。
```CSharp
public class DynamicControllerFeatureProvider : ControllerFeatureProvider 
{
    protected override bool IsController (TypeInfo typeInfo) {
    	var type = typeInfo.AsType ();
        if (!typeof (IDynamicController).IsAssignableFrom (type) ||
            !typeInfo.IsPublic || typeInfo.IsAbstract || typeInfo.IsGenericType) {
            return false;
        }

    	return true;
    }
}
```
如你所见，我们采用了一种简单粗暴的方式，任何非 Public、非抽象、非泛型并且实现了 IDynamicController 接口的类型，都可以被认为是一个 Controller，原谅我起了这样一个直白而普通的接口名称，因为一开始做的时候，真的就是想延续动态 Web Api 这个想法而已，所以，大家明白就好了，不用太过纠结这个接口的名字，甚至你还可以通过 Attribute 来打上标记，反正都是为了辨别哪些类型可以被当做控制器。

# IApplicationModelConvention

OK，现在我们已经告诉.NET Core，怎么样去把一个类型识别为 Controller。因为 MVC 中有一些所谓“约定大于配置”的东西，比如默认的路由规则是：`{area}/{controller}/{action}/{id}`，相信从 ASP.NET 时代一起走过来的各位，对这个东西应该很熟悉啦，因为最早 `App_Start` 里会有 `RouteConfig` 和 `WebApiConfig` 这两个东西。我们在做 ASP.NET 版本的动态 Web API 的实现的时候，实际上就是配置了这样一个固定的路由，所以，理论上现在即使我们不讲下面这部分内容，现在我们已经实现了动态 Controller。可如果我们希望对路由进行全局配置，我们就不得不关注这个接口。简而言之，通过这个接口，我们可以修改 MVC 里约定俗成的这套规则，譬如在路由中带个版本号前缀，或者根据命名空间去生成某种规则的路由，我们都可以考虑去实现这个接口。一般情况下，我们会通过重写 Apply()方法来达到修改路由的目的。

在这篇文章里，我们希望在 MVC 这套默认路由的基础上，增加对特性路由的支持。说到这里，我们又会回到一个旧话题，即基于配置的路由和基于特性的路由这两种路由。前者是 MVC 里的路由设计的基础，而后者是 Web API 里提出并在 RESTful 风格 API 的设计中发扬光大。所以，我们希望在提供默认路由的基础上，使用者可以自由配置路由风格，所以，我们需要通过这个接口来构造路由信息，值得一提的是，我们可以在这个过程中设置 ApiExplorer 是否可见，为接口参数设置合适的绑定模型等等，所以，我们会使用 HttpGet/HttpPost 等来标记接口的调用方式，使用 Route 来标记用户自定义的路由信息，使用 FromBody/FromQuery 等来标记参数的绑定信息，有了这些配合 Swagger 简直是无往不胜，并非是开发人员不愿意写文档，而是因为文档的更新速度往往赶不上需求的变化速度，一旦文档落后于实际业务，这样的文档实际是没有意义的，我真的讨厌所有人都来找你问接口的地址、参数这些东西，如果你写完了一个 Service，写好对应的方法注释，然后你就有了一个可用的 Web API，和一个可用的在线文档，何乐而不为呢？

下面，是博主实现的一个动态路由，它主要涉及到 `ConfigureApiExplorer()`、`ConfigureSelector()` 和 `ConfigureParameters()` 这三个部分的实现，我们一起来看下面的代码，ASP.NET Core 版本相比 ASP.NET 版本，少了像 `Castle DynamicProxy` 这样的黑科技，因此，它的实现会更加纯粹一点。

## ConfigureApiExplorer()

首先，是对 ApiExplorer 进行配置。通过 ApiExplorer，我们可以控制 Controller 级别和 Action 级别的 Web API 的可见性。一般情况下的用法是在 Controller 或者 Action 上添加 ApiExplorerSettings 标记，而在这里，我们只需要给 ControllerModel 和 ActionModel 的 ApiExplorer 属性赋值即可。

```CSharp
private void ConfigureApiExplorer (ControllerModel controller) 
{
    if (string.IsNullOrEmpty (controller.ApiExplorer.GroupName))
        controller.ApiExplorer.GroupName = controller.ControllerName;

    if (controller.ApiExplorer.IsVisible == null)
        controller.ApiExplorer.IsVisible = true;

   controller.Actions.ToList ().ForEach (action => ConfigureApiExplorer (action));
}

private void ConfigureApiExplorer (ActionModel action) 
{
    if (action.ApiExplorer.IsVisible == null)
       action.ApiExplorer.IsVisible = true;
}
```

## ConfigureSelector()

接下来，是对路由进行配置。这部分的核心其实就是根据 AreaName、ControllerName、ActionName 来生成路由信息，我们会为没有配置过特性路由的 Action 生成默认的路由，这其实就是 MVC 里约定大于配置的一种体现啦。在这里会涉及到对 ControllerName 和 ActionName 的优化调整，主要体现在两个方面：其一，是对类似 XXXService、XXXController 等这样的后缀进行去除，使其构造出的 Api 路由更加短小精简；其二，是对 ActionName 里的 Get/Save/Update 等动词进行替换，使其构造出的 Api 路由更加符合 RESTful 风格。

```CSharp
private void ConfigureSelector (ControllerModel controller, DynamicControllerAttribute controllerAttribute) 
{
    if (_dynamicControllerOptions.UseFriendlyControllerName) {
        var suffixsToRemove = _dynamicControllerOptions.RemoveControllerSuffix;
        if (suffixsToRemove != null && suffixsToRemove.Any ())
            suffixsToRemove.ToList ().ForEach (suffix => controller.ControllerName = controller.ControllerName.Replace (suffix, ""));
    }

    controller.Selectors.ToList ().RemoveAll (selector =>
        selector.AttributeRouteModel == null && (selector.ActionConstraints == null || !selector.ActionConstraints.Any ())
    );

    if (controller.Selectors.Any (selector => selector.AttributeRouteModel != null))
        return;

    var areaName = string.Empty;
    if (controllerAttribute != null)
        areaName = controllerAttribute.AreaName;

    controller.Actions.ToList ().ForEach (action => ConfigureSelector (areaName, controller.ControllerName, action));
}

private void ConfigureSelector (string areaName, string controllerName, ActionModel action) 
{
    action.Selectors.ToList ().RemoveAll (selector =>
        selector.AttributeRouteModel == null && (selector.ActionConstraints == null || !selector.ActionConstraints.Any ())
    );

    if (!action.Selectors.Any ()) {
        action.Selectors.Add (CreateActionSelector (areaName, controllerName, action));
    } else {
        action.Selectors.ToList ().ForEach (selector => {
            var routePath = $"{_dynamicControllerOptions.DefaultApiRoutePrefix}/{areaName}/{controllerName}/{action.ActionName}".Replace ("//", "/");
            var routeModel = new AttributeRouteModel (new RouteAttribute (routePath));
            if (selector.AttributeRouteModel == null || !_dynamicControllerOptions.UseCustomRouteFirst)
                selector.AttributeRouteModel = routeModel;
        });
    }
}
```

我们知道，每个 API 接口都会有相对应的 HTTP 动词，譬如 GET、POST、PUT 等等，那么，我们在构造路由的时候，如何知道当前的 Action 应该使用什么 HTTP 动词呢？实际上，我们有两个来源来组织这些信息。第一个来源，是根据方法本身的名称，比如 Get/Save/Update 等等，我们通过对应关系将其转化为对应的 HTTP 动词。第二个来源是根据用户在接口中配置的路由信息，比如 RouteAttribute、HttpMethod 等等，将其转化为对应的 HTTP 动词。这个方法，其实我们在分享 ASP.NET 下的实现的时候，就已经用过一次啦，所谓“万变不离其宗”，大概就是如此：

```CSharp
private SelectorModel CreateActionSelector(string areaName, string controllerName, ActionModel action)
{
    var selectorModel = new SelectorModel();
    var actionName = action.ActionName;
    var routeAttributes = action.ActionMethod.GetCustomAttributes(typeof(HttpMethodAttribute), false);
    if (routeAttributes != null && routeAttributes.Any())
    {
        var httpVerbs = routeAttributes.SelectMany(s => (s as HttpMethodAttribute).HttpMethods).ToList().Distinct();
        var routePath = $"{_dynamicControllerOptions.DefaultApiRoutePrefix}/{areaName}/{controllerName}/{action.ActionName}".Replace("//", "/");
        selectorModel.AttributeRouteModel = new AttributeRouteModel(new RouteAttribute(routePath));
        selectorModel.ActionConstraints.Add(new HttpMethodActionConstraint(httpVerbs));
        return selectorModel;
    }
    else
    {
        var httpVerb = string.Empty;
        var methodName = action.ActionMethod.Name.ToUpper();
        if (methodName.StartsWith("GET") || methodName.StartsWith("QUERY"))
        {
            httpVerb = "GET";
        }
        else if (methodName.StartsWith("SAVE"))
        {
            httpVerb = "POST";
        }
        else if (methodName.StartsWith("UPDATE"))
        {
            httpVerb = "PUT";
        }
        else if (methodName.StartsWith("DELETE"))
        {
           httpVerb = "DELETE";
        }

        var routePath = $"api/{areaName}/{controllerName}/{action.ActionName}".Replace("//", "/");
        selectorModel.AttributeRouteModel = new AttributeRouteModel(new RouteAttribute(routePath));
        selectorModel.ActionConstraints.Add(new HttpMethodActionConstraint(new[] { httpVerb }));
        return selectorModel;
    }
}
```

由此可见，无论多么令人惊诧的黑科技，当我们一层层地拨开它的迷雾时，常常有种豁然开朗的感觉。当然，和那些令人看起来神清气爽的代码相比，博主远远达不到返璞归真的境界，因为这段代码怎么看都觉得丑陋。古美门律师告诉我们，要爱上丑陋，或许每个程序员都是从写烂代码开始的吧！

## ConfigureParameters()

接下来参数绑定相对简单，因为简单类型 MVC 自己就能完成绑定，所以，我们只需要关注复杂类型的绑定即可，最常见的一种绑定方式是 FromBody：
```csharp
private void ConfigureActionParameters(ActionModel action)
{
    foreach (var parameter in action.Parameters)
    {
        if (parameter.BindingInfo != null)
            continue;

        var type = parameter.ParameterInfo.ParameterType;
        if (type.IsPrimitive || type.IsEnum ||
            (type.IsGenericType && type.GetGenericTypeDefinition() == typeof(Nullable<>)))
        {
            if (IsFromBodyEnable(action, parameter))
            {
                parameter.BindingInfo = BindingInfo.GetBindingInfo(new[] { new FromBodyAttribute() });
            }
        }
    }
}
```
通过以上三个关键步骤，我们就能实现本文一开始的效果，感觉无形中我们又复习了一篇 MVC 匹配路由的原理呢！

# 集成 Swagger 和 WebApiClient

今天这篇文章，本质上依然是 ABP 框架中 Dynamic WebAPI 这一特性的延伸，无非是因为.NET Core 中提供了更为友好的机制，可以让这一切实现起来更简单而已。还记得博主研究这个特性的“初心”是什么吗？因为我们在升级.NET Core 的过程中打算抛弃 WCF，我们需要一种方法，可以让现有的一个普通的 Service 变成一个 Controller。固然，我们可以一个一个的去重新封装，可这真的是比较好的实践方式吗？从内部 RPC 逐渐转变为 Web API 调用，这种转变就像从 Dubbo 换成了 Spring Cloud，可是 Spring Cloud 有注册中心啊，现在我们什么都没有，从 RPC 转变为 Web API，会面临诸如接口授权、地址配置、不同上下文等等的问题。你经常需要告诉别人某个接口的地址是什么，不出意外地话，你至少会有三套环境的地址，别人还会问你各个参数的含义，甚至更懒的会要求你提供示例报文。所以，我觉得做微服务，尤其是全部采用 Web API 进行通信的微服务，提供实时更新、在线查看的文档真的非常重要，每次看到同事在 Git 里提交 Word 或者 Excel，我就感到非常纠结，一来这种东西没法正常 Merge，压缩包合并个鬼啊，二来我必须下载下来看，君不见，我下载目录里一堆重复文件，所以，我更推荐努力维护好一家公司的 API 资产，在我们用 JWT 保护这些资产以前，至少要先了解它们吧！


对于 API 文档，我个人推荐专门用一个站点来承载所有的 Web API，比如我们最常用的 Swagger，它在融合 OAuth2 以后可以更完美地去调试接口，了解每个接口的参数和返回值。尤其是在这篇博客的背景下，因为我们只需要把这些 POCOController 对应的注释文件(.XML)和程序集(.DLL)放到一起，同时把这些注释文件全部 Include 进来，Swagger 就可以把它们展示出来。这里用到一个非常重要的特性就是 IApiExploer 接口，你可以把它理解为，它是一切文档展示的核心，每个接口及其参数、返回值的描述信息都是由它提供的。在没有 Swagger 之前，微软提供了一个叫做 Web API HelpPage 的组件，它和 Swagger 的原理无出其右。这里剧透下，稍后我会专门写一篇博客来扩展 Swagger，目的是确保它可以为 ASP.NET MVC 提供文档支持。这里，我们使用 Swagger 来生成在线 API 文档，其核心配置如下：

```CSharp
services.AddMvcCore ().AddApiExplorer ();
services.AddSwaggerGen (swagger => {
    swagger.SwaggerDoc ("v1", new Swashbuckle.AspNetCore.Swagger.Info () {
        Title = "DynamicController",
        Version = "1.0",
    });
    
    swagger.DocInclusionPredicate ((docName, description) => true);
    var xmlFile = $"{Assembly.GetExecutingAssembly().GetName().Name}.xml";
    var xmlPath = Path.Combine (AppContext.BaseDirectory, xmlFile);
    swagger.IncludeXmlComments (xmlPath);
});
```

可以注意到，这篇文章里实现的动态 Controller 和默认的 ValuesController 都被展示了出来，两个字，完美，我们想要的就是这个效果。

![通过Swagger生成的在线Api文档](https://ww1.sinaimg.cn/large/4c36074fly1g5k84kvuzqj21hc0s03zo.jpg)



说完了 API 文档的事情，我们再来说说调用 Web API 的问题。按理说，这应该没啥大问题，因为虽然我们会为 HttpWebRequest、WebClient、HttpClient 和 RestSharp 等等不同的 API 而感到纠结，可这丝毫不会影响我们调用 Web API。那么，问题来了，当你面对数不胜数的 API 接口的时候，你打算如何考虑这些问题？我的 API 地址应该配置在哪里？是存到 Web.Config 里还是存到数据库里？我调用 API 的时候，Token 应该从哪里获取？是每次都获取还是获取了缓存起来？如果 Token 过期了我又该怎么办？这几乎是所有全部采用 Web API 进行微服务设计时都会遇到的问题。

此时，我们需要一种更优雅的方式，即 `Retrofit`，它能让我们像调用一个普通方法一样调用一个 Web API，这样，我们在调用方式上其实不会有太大的改变，因为 Web API 本质上是一种特殊的 RPC。在.NET 的世界里，我们有 WebApiClient 和 Refit 这样的轮子，我之前还专门为大家介绍过 `WebApiClient`。这里就不再展示它的具体细节了，所谓点到为止，希望大家可以自己去发现这种美，对博主而言，如果在定义 Service 的时候，就考虑到这一点，或许我们可以实现更理想的效果，即，服务端和客户端是一套代码，我们写完一个接口以后，它就是 Web API，而通过动态代理，它本身又会是客户端，此中乐趣，则不足为外人道也！



# 本文小结

又是漫长的一个夏天，下雨并不能让这座城市温柔起来。这篇博客延续了上一篇博客中关于动态 Controller 的设想，而借助于.NET Core 框架提供的良好特性，它以一种更为简洁的方式被实现了，核心的内容有两个点，其一是 ControllerFeatureProvider，它能决定 MVC 会不会把一个普通的类当做控制器。其二是 IApplicationModelConvention 接口，它能对全局的路由规则进行修改，以满足我们特殊的定制化需要。再此基础上，继续引入 Swagger 和 WebApiClient 两个轮子，来解决微服务构建中的 API 文档和 API 调用问题。写博客真的是一件辛苦的事情诶，好啦，今天这篇博客就先写到这里，我们下一篇博客再见，晚安！本文中涉及到的代码可以通过：[https://github.com/qinyuanpei/DynamicWCFProxy/tree/master/DynamicWebApi.Core](https://github.com/qinyuanpei/DynamicWCFProxy/tree/master/DynamicWebApi.Core) 来做进一步的了解，以上！