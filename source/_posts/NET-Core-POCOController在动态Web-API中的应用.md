---
abbrlink: 116795088
categories:
- 编程语言
date: 2019-08-01 16:44:59
description: POCOController是ASP.NET Core中提供的一个新特性，按照约定大于配置的原则，在ASP.NET Core项目中，所有带有Controller后缀的类，或者是使用了[Controller]标记的类，即使它没有像模板中一样继承Controller类，ASP.NET
  Core依然会将其识别为Controller，并拥有和普通Controller一样的功能，说到这里，你是不是有点兴奋了呢，因为我们在ASP.NET里花了大力气去做类似的事情，因为ASP.NET里一个普通的类是没有办法成为Controller的，即使通过Castle的Dynamic
  Proxy黑科技，我们依然需要去Hack整个MVC框架创建、筛选Controller和Action的过程
tags:
- .NET Core
- Dynamic WebApi
- POCOController
title: .NET Core POCOController在动态Web API中的应用
---

Hi，大家好，我是Payne，欢迎大家关注我的博客，我的博客地址是：[<https://blog.yuanpei.me>](https://blog.yuanpei.me)。在上一篇文章中，我和大家分享了ASP.NET中动态Web API的实现，这种方案的现实意义是，它可以让我们把任意一个接口转换为Web API，所以，不单单局限在文章里提到的WCF迁移到Web API，任意领域驱动开发(DDD)中的服务层，甚至是更为普遍的传统三层，都可以通过这种方式快速构建前后端分离的应用。可能大家会觉得直接把Service层暴露为API，会引发一系列关于鉴权、参数设置(FromQuery/FromBody)等等的问题，甚至更极端的想法是，这样和手写的没什么区别，通过中间件反射能达到相同的目的，就像我们每天都在写各种接口，经常有人告诉我们说，不要在Controller层写太重的业务逻辑，所以，我们的做法就是不断地在Service层里增加新接口，然后再把Service层通过Controller层暴露出来，这样子真的是对的吗？



可我个人相信，技术总是在不断向前发展的，大家觉得RESTful完全够用啦，结果GraphQL突然发现了。大家写了这么多年后端，其实一直都在绕着数据转，可如果数据库本身就支持RESTful风格的接口，或者是数据库本身就支持某种ORM，我们后端会立马变得无趣起来。其实，在ASP.NET Core中已经提供了这种特性，这就是我们今天要说的POCOController，所以，这也许是个正确的思路，对吧？为什么Service层本身不能就是Controller层呢？通过今天这篇文章，或许你会接受这种想法，因为POCOController，就是弱化Controller本身的特殊性，一个Controller未必需要继承自Controller，或者在名称中含有**Controller**相关的字眼，如果Controller同普通的类没有区别会怎么样呢？答案就是Service层和Controller层的界限越来越模糊。扪心自问，我们真的需要中间这一层封装吗？



# 什么是POCOController

POCOController是ASP.NET Core中提供的一个新特性，按照约定大于配置的原则，在ASP.NET Core项目中，所有带有Controller后缀的类，或者是使用了[Controller]标记的类，即使它没有像模板中一样继承Controller类，ASP.NET Core依然会将其识别为Controller，并拥有和普通Controller一样的功能，说到这里，你是不是有点兴奋了呢，因为我们在ASP.NET里花了大力气去做类似的事情，因为ASP.NET里一个普通的类是没有办法成为Controller的，即使通过Castle的Dynamic Proxy黑科技，我们依然需要去Hack整个MVC框架创建、筛选Controller和Action的过程。可在ASP.NET Core里这一切居然变成了一个新的feature，所以，我预感到这篇文章应该不会像上一篇文章那么长，果然9102有9102的好处呢……好了，现在我们来写一个POCOController：

```CSharp
public class MessageController
{
    public string Echo(string receiver)
   {
        return $"Hello, {receiver}";
   }
}
```

接下来，我们通过浏览器访问：http://localhost:6363/Message/Echo?receiver=PayneQin，我们就会发现一件非常神奇的事情，那就是，我们并没有真的在写一个Controller，它没有继承Controller类，虽然它的名字里带着Controller的后缀，可它确实实现了一个Controller所具备的功能，因为它返回了我们期望的信息。

![欢迎来到POCOController的世界](https://ww1.sinaimg.cn/large/4c36074fly1g5j4wxhvuaj20kw0c075r.jpg)

可以注意到，这个Controller使用起来和普通的Controller是没有任何区别的，这正是我们想要的结果。对于.NET Core而言，一个普通的类想要成为POCOController，只需要满足以下任意一个条件：第一，继承自Microsoft.AspNetCore.Mvc.Controller类，无论是否带有Controller后缀，都可以作为POCOController。第二，不继承自Microsoft.AspNetCore.Mvc.Controller类，同时引用了Microsoft.AspNetCore.Mvc相关的程序集。在这里，博主一开始就犯了这个错误，因为博主建的是一个Web API类型的项目。



# ControllerFeatureProvider

那么，为什么ASP.NET Core里可以实现如此炫酷的功能呢？这里要介绍到ControllerFeatureProvider。在.NET Core中，微软引入了应用程序部件的概念，顾名思义，它是对应用程序资源的一种抽象，通过这些应用程序部件， .NET Core提供了发现和加载MVC组件，如控制器、视图(View)、标记(TagHelper)、Razor等等的功能。在MVC中，这些功能由ApplicationPartManager对象来进行管理，它维护着一个叫做FeatureProviders的列表，以上这些功能分别对应一个Feature，所以，当我们希望引入一个新的功能的时候，只需要实现IApplicationFeatureProvider<T>接口即可，而这里的ControllerFeatureProvider显然是提供“控制器”相关的Feature，它有一个最为关键的接口IsController(TypeInfo)。

回到一开始的话题，微软定义了一个类成为POCOController的规则，实际上我们同样可以定义自己的规则，譬如ABP框架中限定的接口约束是实现IAppService这个接口，那么我们就可以把一个程序集或者多个程序集里的类型识别为控制器，这就是POCOController的奥秘所在。在比如我们的项目中难免会有大量CRUD的垃圾需求，区别仅仅是它访问不同的仓储，我们可能会想写一个泛型的控制器来处理，可惜在过去的ASP.NET里，实现这一切并不太容易。为什么说不大容易呢？通过我们上一篇文章里动态路由的整个过程，大家就知道有多麻烦了啊，可在.NET Core里要实现一个泛型的控制器就非常容易了啊，因为我们只需要告诉ControllerFeatureProvider，这是一个控制器，并且控制器的类型就是这个泛型参数T，所以，综上所述，ControllerFeatureProvider主要做两个事情，第一，判定一个类型能不能算作Controller；第二，对程序集里的类型进行筛选和过滤。下面，我们顺着这个思路来实现我们自己的ControllerFeatureProvider。
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
如你所见，我们采用了一种简单粗暴的方式，任何非Public、非抽象、非泛型并且实现了IDynamicController接口的类型，都可以被认为是一个Controller，原谅我起了这样一个直白而普通的接口名称，因为一开始做的时候，真的就是想延续动态Web Api这个想法而已，所以，大家明白就好了，不用太过纠结这个接口的名字，甚至你还可以通过Attribute来打上标记，反正都是为了辨别哪些类型可以被当做控制器。

# IApplicationModelConvention

OK，现在我们已经告诉.NET Core，怎么样去把一个类型识别为Controller。因为MVC中有一些所谓“约定大于配置”的东西，比如默认的路由规则是{area}/{controller}/{action}/{id}，相信从ASP.NET时代一起走过来的各位，对这个东西应该很熟悉啦，因为最早App_Start里会有RouteConfig和WebApiConfig这两个东西。我们在做ASP.NET版本的动态Web API的实现的时候，实际上就是配置了这样一个固定的路由，所以，理论上现在即使我们不讲下面这部分内容，现在我们已经实现了动态Controller。可如果我们希望对路由进行全局配置，我们就不得不关注这个接口。简而言之，通过这个接口，我们可以修改MVC里约定俗成的这套规则，譬如在路由中带个版本号前缀，或者根据命名空间去生成某种规则的路由，我们都可以考虑去实现这个接口。一般情况下，我们会通过重写Apply()方法来达到修改路由的目的。

在这篇文章里，我们希望在MVC这套默认路由的基础上，增加对特性路由的支持。说到这里，我们又会回到一个旧话题，即基于配置的路由和基于特性的路由这两种路由。前者是MVC里的路由设计的基础，而后者是Web API里提出并在RESTful风格API的设计中发扬光大。所以，我们希望在提供默认路由的基础上，使用者可以自由配置路由风格，所以，我们需要通过这个接口来构造路由信息，值得一提的是，我们可以在这个过程中设置ApiExplorer是否可见，为接口参数设置合适的绑定模型等等，所以，我们会使用HttpGet/HttpPost等来标记接口的调用方式，使用Route来标记用户自定义的路由信息，使用FromBody/FromQuery等来标记参数的绑定信息，有了这些配合Swagger简直是无往不胜，并非是开发人员不愿意写文档，而是因为文档的更新速度往往赶不上需求的变化速度，一旦文档落后于实际业务，这样的文档实际是没有意义的，我真的讨厌所有人都来找你问接口的地址、参数这些东西，如果你写完了一个Service，写好对应的方法注释，然后你就有了一个可用的Web API，和一个可用的在线文档，何乐而不为呢？

下面，是博主实现的一个动态路由，它主要涉及到ConfigureApiExplorer()、ConfigureSelector()和ConfigureParameters()这三个部分的实现，我们一起来看下面的代码，ASP.NET Core版本相比ASP.NET版本，少了像Castle DynamicProxy这样的黑科技，因此它的实现会更加纯粹一点。

## ConfigureApiExplorer()

首先，是对ApiExplorer进行配置。通过ApiExplorer，我们可以控制Controller级别和Action级别的Web API的可见性。一般情况下的用法是在Controller或者Action上添加ApiExplorerSettings标记，而在这里，我们只需要给ControllerModel和ActionModel的ApiExplorer属性赋值即可。

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

接下来，是对路由进行配置。这部分的核心其实就是根据AreaName、ControllerName、ActionName来生成路由信息，我们会为没有配置过特性路由的Action生成默认的路由，这其实就是MVC里约定大于配置的一种体现啦。在这里会涉及到对ControllerName和ActionName的优化调整，主要体现在两个方面，其一是对类似XXXService、XXXController等这样的后缀进行去除，使其构造出的Api路由更加短小精简；其二是对ActionName里的Get/Save/Update等动词进行替换，使其构造出的Api路由更加符合RESTful风格。

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

我们知道，每个API接口都会有相对应的HTTP动词，譬如GET、POST、PUT等等，那么，我们在构造路由的时候，如何知道当前的Action应该使用什么HTTP动词呢？实际上，我们有两个来源来组织这些信息。第一个来源，是根据方法本身的名称，比如Get/Save/Update等等，我们通过对应关系将其转化为对应的HTTP动词。第二个来源是根据用户在接口中配置的路由信息，比如RouteAttribute、HttpMethod等等，将其转化为对应的HTTP动词。这个方法，其实我们在分享ASP.NET下的实现的时候，就已经用过一次啦，所谓“万变不离其宗”，大概就是如此：

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

接下来参数绑定相对简单，因为简单类型MVC自己就能完成绑定，所以，我们只需要关注复杂类型的绑定即可，最常见的一种绑定方式是FromBody：
```
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
通过以上三个关键步骤，我们就能实现本文一开始的效果，感觉无形中我们又复习了一篇MVC匹配路由的原理呢！

# 集成Swagger和WebApiClient

今天这篇文章，本质上依然是ABP框架中Dynamic WebAPI这一特性的延伸，无非是因为.NET Core中提供了更为友好的机制，可以让这一切实现起来更简单而已。还记得博主研究这个特性的“初心”是什么吗？因为我们在升级.NET Core的过程中打算抛弃WCF，我们需要一种方法，可以让现有的一个普通的Service变成一个Controller。固然，我们可以一个一个的去重新封装，可这真的是比较好的实践方式吗？从内部RPC逐渐转变为Web API调用，这种转变就像从Dubbo换成了Spring Cloud，可是Spring Cloud有注册中心啊，现在我们什么都没有，从RPC转变为Web API，会面临诸如接口授权、地址配置、不同上下文等等的问题。你经常需要告诉别人某个接口的地址是什么，不出意外地话，你至少会有三套环境的地址，别人还会问你各个参数的含义，甚至更懒的会要求你提供示例报文。所以，我觉得做微服务，尤其是全部采用Web API进行通信的微服务，提供实时更新、在线查看的文档真的非常重要，每次看到同事在Git里提交Word或者Excel，我就感到非常纠结，一来这种东西没法正常Merge(压缩包合并个鬼啊)，二来我必须下载下来看(君不见我下载目录里一堆重复文件)，所以，我更推荐努力维护好一家公司的API资产，在我们用JWT保护这些资产以前，至少要先了解它们吧！



对于API文档，我个人推荐专门用一个站点来承载所有的Web API，比如我们最常用的Swagger，它在融合OAuth2以后可以更完美地去调试接口，了解每个接口的参数和返回值。尤其是在这篇博客的背景下，因为我们只需要把这些POCOController对应的注释文件(.XML)和程序集(.DLL)放到一起，同时把这些注释文件全部Include进来，Swagger就可以把它们展示出来。这里用到一个非常重要的特性就是IApiExploer接口，你可以把它理解为，它是一切文档展示的核心，每个接口及其参数、返回值的描述信息都是由它提供的。在没有Swagger之前，微软提供了一个叫做Web API HelpPage的组件，它和Swagger的原理无出其右。这里剧透下，稍后我会专门写一篇博客来扩展Swagger，目的是确保它可以为ASP.NET MVC提供文档支持。这里，我们使用Swagger来生成在线API文档，其核心配置如下：

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

可以注意到，这篇文章里实现的动态Controller和默认的ValuesController都被展示了出来，两个字，完美，我们想要的就是这个效果。

![通过Swagger生成的在线Api文档](https://ww1.sinaimg.cn/large/4c36074fly1g5k84kvuzqj21hc0s03zo.jpg)



说完了API文档的事情，我们再来说说调用Web API的问题。按理说，这应该没啥大问题，因为虽然我们会为HttpWebRequest、WebClient、HttpClient和RestSharp等等不同的API而感到纠结，可这丝毫不会影响我们调用Web API。那么，问题来了，当你面对数不胜数的API接口的时候，你打算如何考虑这些问题？我的API地址应该配置在哪里？是存到Web.Config里还是存到数据库里？我调用API的时候，Token应该从哪里获取？是每次都获取还是获取了缓存起来？如果Token过期了我又该怎么办？这几乎是所有全部采用Web API进行微服务设计时都会遇到的问题。

此时，我们需要一种更优雅的方式，即Retrofit，它能让我们像调用一个普通方法一样调用一个Web API，这样，我们在调用方式上其实不会有太大的改变，因为Web API本质上是一种特殊的RPC。在.NET的世界里，我们有WebApiClient和Refit这样的轮子，我之前还专门为大家介绍过WebApiClient。这里就不再展示它的具体细节了，所谓点到为止，希望大家可以自己去发现这种美，对博主而言，如果在定义Service的时候，就考虑到这一点，或许我们可以实现更理想的效果，即，服务端和客户端是一套代码，我们写完一个接口以后，它就是Web API，而通过动态代理，它本身又会是客户端，此中乐趣，则不足为外人道也！



# 本文小结

又是漫长的一个夏天，下雨并不能让这座城市温柔起来。这篇博客延续了上一篇博客中关于动态Controller的设想，而借助于.NET Core框架提供的良好特性，它以一种更为简洁的方式被实现了，核心的内容有两个点，其一是ControllerFeatureProvider，它能决定MVC会不会把一个普通的类当做控制器。其二是IApplicationModelConvention接口，它能对全局的路由规则进行修改，以满足我们特殊的定制化需要。再此基础上，继续引入Swagger和WebApiClient两个轮子，来解决微服务构建中的API文档和API调用问题。写博客真的是一件辛苦的事情诶，好啦，今天这篇博客就先写到这里，我们下一篇博客再见，晚安！本文中涉及到的代码可以通过：[https://github.com/qinyuanpei/DynamicWCFProxy/tree/master/DynamicWebApi.Core](https://github.com/qinyuanpei/DynamicWCFProxy/tree/master/DynamicWebApi.Core)来做进一步的了解，以上！