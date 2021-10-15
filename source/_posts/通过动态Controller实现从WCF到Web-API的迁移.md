---
abbrlink: 4236649
categories:
- 编程语言
date: 2019-06-08 13:48:41
description: DynamicControllerActivator 实现了 IHttpControllerActivator 接口，这里我们通过单例模式获得了 DynamicHttpControllerManager 对象的一个实例，其内部封装了 Castle 的容器接口 IWindsorContainer，所以，在这里我们直接通过 controllerType 从容器中 Resolve 对应的 Controller 即可，而默认情况下，所有的 Controller 都实现了 IHttpController 接口，所以，这一步我们需要做一个显示的类型转换，后面我们会通过它替换微软默认的实现，这样，当一个请求被发送过来的时候，我们实际上是从这个自定义容器中获取对应 Controller 的实例;老实说，通过自定义 IHttpControllerActivator 的方式实现依赖注入的方式并不常见，因为更一般的情况是，大家在 Global.asax 里初始化像 Unity、Autofac 等等类似的容器，然后在 Controller 里通过容器去 Resolve 一个服务出来，对于 IHttpControllerActivator 接口而言，它只有一个 Create()方法，在这篇文章中，我们是通过 Castle 这个容器来实现依赖注入的，所以，你大概可以想象出它的过程，首先把所有动态生成的 Controller 全部注入到 Ioc 容器中，然后再根据传入的类型获取对应 Controller 的实例;在这个过程中，我们回顾了 ASP.NET
  MVC 的基本原理，了解了 MVC 是如何根据路由筛选 Controller、激活 Controller 和筛选 Action，在此基础上，我们对微软的 MVC 进行了一次 Hack，使用我们自定义的组件替换了微软的默认实现，从而可以让原来托管在 ServiceHost 上的接口，通过 Web
  API 来访问和调用
tags:
- RESTful
- WebApi
- 动态代理
title: 通过动态 Controller 实现从 WCF 到 Web API 的迁移.
---

在《**又见 AOP 之基于 RealProxy 实现 WCF 动态代理**》这篇文章中，我和大家分享了关于使用动态代理来简化 WCF 调用过程的相关内容，当时我试图解决的问题是，项目中大量通过 T4 生成甚至手动编写的“代理方法”。今天，我想和大家分享的是，如何通过动态的 Controller 来实现从 WCF 到 Web API 的迁移。为什么会有这个环节呢？因为我们希望把一个老项目逐步迁移到.NET Core 上面，在这个过程中首当其冲的就是 WCF，它在项目中主要承担着内部 RPC 的角色，因为.NET Core 目前尚未提供针对 WCF 服务端的支持，因此面对项目中成百上千的 WCF 接口，我们必须通过 Web API 重新“包装”一次，区别于那些通过逐个 API 进行改造的方式，这里我们通过 Castle 动态生成 Controller 来实现从 WCF 到 Web API 的迁移。

# 如何对类和接口进行组合

首先，我们来思考这样一个问题，假设现在有一个类 BaseClass、一个接口 IBaseService 及其实现类 BaseService，我们有没有什么办法，可以让这个类和接口组合起来呢？联系面向对象编程的相关知识，我们应该可以想到最常见的两种方式，即 BaseService 继承 BaseClass(或者反过来)、BaseClass 实现 IBaseService 接口。考虑到语言本身是否支持多继承的因素，第二种方式可能会更具有适用性。可如果这个问题，就仅仅到这种程度，我相信大家一定会感到失望，因为这的确没有什么好说的。现在的问题是，假如 BaseClass 类、BaseService 类都已经存在了，我们有没有什么思路，可以把它们组合到一个类中呢？这又和我们今天要讨论的内容有什么关系呢？

好了，不卖关子啦，下面隆重请出 Castle 中的 Dynamic Proxy，我们曾经介绍过 Castle 中的动态代理，它可以为指定的类和接口创建对应的代理类，除此以外，它提供了一种称为**AdditionalInterfaces**的接口，这个接口可以在某个代理对象上“组合”一个或者多个接口，换句话说，代理对象本身包含被代理对象的全部功能，同时又可以包含某个接口的全部功能，这样就实现了一个类和一个接口的组合。为什么我们会需要这样一个功能呢？因为假如我们可以把一个 ApiController 类和指定的接口类如 CalculatorService 进行组合，在某种程度上，CalculatorService 就变成了一个 ApiController，这样就实现了我们的目标的第一步，即动态生成一个 ApiController。与此同时，它会包含我们现有的全部功能，为了方便大家理解，我们从下面这个简单的例子开始：

```CSharp
/// <summary>
 /// IEchoService定义
 /// </summary>
 public interface IEchoService {
     void Echo (string receiver);
 }

 /// <summary>
 /// IEchoServicee实现
 /// </summary>
 public class EchoService : IEchoService {
     public void Echo (string receiver) {
         Console.WriteLine ($"Hi，{receiver}");
     }
 }

 /// <summary>
 /// 空类EmptyClass
 /// </summary>
 public class EmptyClass { }

 public class EchoInterceptor : IInterceptor {
     private IEchoService _realObject;
     public EchoInterceptor (IEchoService realObject) {
         _realObject = realObject;
     }

     public void Intercept (IInvocation invocation) {
         invocation.Method.Invoke (_realObject, invocation.Arguments);
     }
 }
 
 var container = new WindsorContainer ();
 container.Register (
     Component.For<EchoService, IEchoService>(),
     Component.For (typeof (EchoInterceptor)).LifestyleTransient(),
     Component.For (typeof (EmptyClass)).Proxy.AdditionalInterfaces (typeof(IEchoService))
     .Interceptors (typeof (EchoInterceptor)).LifestyleTransient()
 );

 var emptyClass = container.Resolve<EmptyClass> ();
 var methodInfo = emptyClass.GetType().GetMethod ("Echo");
 methodInfo.Invoke (emptyClass, new object[] { "Dynamic WebApi" });
```

此时，我们会发现通过 Castle 动态生成的代理类，同时具备了类和接口的功能。

![通过Castle实现类和接口的组合功能](https://ww1.sinaimg.cn/large/4c36074fly1g4a1c3r3i8j20rz0f43yj.jpg)

# 重温 ASP.NET MVC 原理

OK，通过第一个例子，我们已经达到了第一个目的。接下来，顺着这个思路，我们不妨想象一下，如果把这个 BaseClass 换成 BaseController 会怎么样呢？因为在一个 OO 的语言里，一切都是 Class，所以，Web 开发中的 Controller 同样不会脱离这个体系。不过，在这之前，我们需要复习下 ASP.NET MVC 的原理，为什么要说这个呢？因为接下来的内容，都和它有重大的关联，我们实际上是自己实现了 ASP.NET MVC 中几个关键的环节，所以，在博主看来，这部分内容是非常重要的，这几乎是这篇文章中实现的最细节部分，因为第一个目标，说句实话，Castle 帮我们简化到了只有 4 行代码。

## 一张图了解 MVC 

![ 一张图了解MVC](https://ww1.sinaimg.cn/large/4c36074fly1g49w0oxqkej20p50fuwfa.jpg)

通常来讲，当我们在 MVC 中接收到一个 Url 请求后，这个请求会被 UrlRoutingModule 拦截。此时，请求的上下文 HttpContext 会被封装到 HttpContextWrapper 对象中。而根据当前请求的 HttpContext，则可以提取出符合当前 Url 的路由对象 RouteData，它会被进一步封装为 RequestContext 对象。接下来，从 RequestContext 对象中获取 RouteData，它对应一个 RouteHandler，是 IHttpHandler 的一个实现类。对于 MVC 而言，则对应 MvcHandler。通过调用 MvcHandler，对应的 Controller 会被反射激活，进而调用具体的 Action。以上就是整个 MVC 请求的过程描述，可以看出最关键的两个组件是 UrlRoutingModule 和 MvcHandler，前者的作用是解析 Controller 和 Action 名称，后者的作用则是根据 Controller 名称去反射调用具体的 Action，大家可以通过上面的图来理解这个过程。

在这里，其实我们只需要关注第二部分:-D，即 MvcHandler，因为我们会在默认路由的基础上，增加一个自定义路由来“标记”这些动态的 Controller，所以，我们集中关注 MvcHandler 这部分即可，虽然这里提到它会根据 Controller 的名称来反射激活相应的 Controller 实例、调用具体的 Action，但这仅仅是宏观上的一种认识。我们来看一下，它具体是怎么反射出 Controller 以及调用 Action 的。

## IControllerFactory 接口

第一个关键的组件是 IControllerFactory 接口，顾名思义，它是作用是创建 Controller，可实际上，这个组件除了完成创建 Controller 的工作以外，还会涉及到 Controller 类型的解析、Controller 实例激活、Controller 实例释放、会话状态行为选项获取等多个功能。这里有一个激活的过程，我们可以将其理解为 Controller 的初始化，因为 Controller 在使用的过程中往往会通过 IoC 容器来注入相关服务，所以，你可以理解为在构造 Controller 的过程中，我们需要一个 IoC 容器来完成依赖注入相关的事情，微软默认提供了一个 DefaultControllerFactory 的实现，它内部是通过 IHttpControllerActivator 接口来完成依赖注入的，而这恰恰是我们要关注的第二个组件。

## IHttpControllerActivator 接口

老实说，通过自定义 IHttpControllerActivator 的方式实现依赖注入的方式并不常见，因为更一般的情况是，大家在 Global.asax 里初始化像 Unity、Autofac 等等类似的容器，然后在 Controller 里通过容器去 Resolve 一个服务出来，对于 IHttpControllerActivator 接口而言，它只有一个 Create()方法，在这篇文章中，我们是通过 Castle 这个容器来实现依赖注入的，所以，你大概可以想象出它的过程，首先把所有动态生成的 Controller 全部注入到 Ioc 容器中，然后再根据传入的类型获取对应 Controller 的实例。在本文中，我们重写了默认的 HttpControllerActivator，这里主要指 Create()方法，因为我们希望实现的效果是，动态的 Controller 全部从 Castle 容器中获取，而静态的 Controller 依然按照微软的设计来获取。

## IHttpControllerSelector 接口

OK，现在有了 Controller 以后，我们怎么让 MVC 路由到正确的 Controller 上面去呢？这时候，必然需要有人来解析路由啊，这就是第三个组件——IHttpControllerSelector。这又是一个顾名思义的接口，充分说明命名是件多么重要的事情。在这里我们重写了 SelectController()方法，当路由信息中存在 ServiceName 和 ActionName 时，就去检查容器中是否存在对应的 Controller，如果存在就返回一个 HttpControllerDescriptor，这是一个用以描述控制器上下文信息的类型。反之，会调用默认的 base.SelectController()方法，这样做还是为了兼容微软原来的设计，因为我们不希望在引入动态 Controller 后，导致普通的 Controller 无法正常工作。

## IhttpActionSelector 接口

同理，我们还需要告诉 MvcHandler，它应该调用哪个方法，这时候我们需要 IHttpActionSelector，因为从路由信息中我们可以提取到 ActionName 参数，因此，通过通过 typeof(Controller).GetMethod(ActionName)，就可以获得对应 ActionName 对应的方法，熟悉反射的朋友应该都知道，它会返回 MethodInfo 这个类型，实际上 IHttpActionSelector 所做的事情，就是把 MethodInfo 传给 MvcHandler，因为此时只要通过反射调用这个方法即可，Controller 的实例在上一步就创建好了，而调用方法所需要的参数，则被存储在当前请求的上下文 HttpContext 里面，至此万事具备！我们要做的，就是顺着这些思路去实现以上组件。

# 关键组件的自定义实现

OK，下面我们来看看如何针对这些组件， 来分别实现我们的自定义组件，实现这些自定义组件并对 MVC 中的默认组件进行替换，这就是我们这篇文章中实现动态 Controller 的一个基本原理。

## DynamicControllerActivator 

DynamicControllerActivator 实现了 IHttpControllerActivator 接口，这里我们通过单例模式获得了 DynamicHttpControllerManager 对象的一个实例，其内部封装了 Castle 的容器接口 IWindsorContainer，所以，在这里我们直接通过 controllerType 从容器中 Resolve 对应的 Controller 即可，而默认情况下，所有的 Controller 都实现了 IHttpController 接口，所以，这一步我们需要做一个显示的类型转换，后面我们会通过它替换微软默认的实现，这样，当一个请求被发送过来的时候，我们实际上是从这个自定义容器中获取对应 Controller 的实例。

```CSharp
public class DynamicHttpControllerActivtor : IHttpControllerActivator
{
 public IHttpController Create(HttpRequestMessage request, HttpControllerDescriptor controllerDescriptor, Type controllerType)
 {
  return (IHttpController)DynamicHttpControllerManager.GetInstance().Resolve(controllerType);
 }
}
```

## DynamicHttpControllerSelector

如果说 DynamicControllerActivator 是真正实现控制器的**"激活"**部分，那么在此之前，我们需要实现控制器的**"筛选"**部分，换言之，一个请求被发送过来的时候，到底应该用哪一个 Controller 去处理这个请求呢？所以，我们来看看 DynamicHttpControllerSelector 这个组件是如何实现的，这里我们重写 SelectController()这个方法来完成控制器的**"筛选"**部分的工作。可以注意到，我们首先会判断路由信息中是否存在 ServiceName 和 ActionName 这两个值，因为对于动态的 Controller，我们默认使用的路由模板是**services/{ServiceName}/{ActionName}**，这里使用 services 前缀是为了区别于微软默认的 api 前缀，当然，强迫症的你同样可以使用相同的前缀。

接下来，我们会判断 ServiceName 是否在容器中注册过，如果注册了就从容器里取出对应的服务，并构造 DynamicHttpControllerDescriptor 对象，否则调用父类方法按微软默认实现去处理。那么，这个 DynamicHttpControllerDescriptor 对象，又是何方神圣呢？从名称上我们大概可以了解，这应该是一个对控制器相关信息进行描述的类型，它继承了 HttpControllerDescriptor 这个父类，目前没有任何扩展性的实现。对于 DynamicHttpControllerDescriptor，它最重要的参数是构造函数中第三个参数，即 controllerType，因为 DynamicControllerActivator 实际上就是根据它来工作的。

```CSharp
public class DynamicHttpControllerSelector: DefaultHttpControllerSelector
{
    private HttpConfiguration _configuration;
    /// <summary>
    /// 构造函数
    /// </summary>
    /// <param name="configuration"></param>
    public DynamicHttpControllerSelector(HttpConfiguration configuration) :
        base(configuration)
    {
        _configuration = configuration;
    }

    public override HttpControllerDescriptor SelectController(HttpRequestMessage request)
    {
        var routeData = request.GetRouteData().Values;
        if (routeData.ContainsKey("ServiceName") && routeData.ContainsKey("ActionName"))
        {
            var serviceName = routeData["ServiceName"].ToString();
            var actionName = routeData["ActionName"].ToString();

            if (DynamicHttpControllerManager.GetInstance().ContainsService(serviceName))
            {
                var controllerInfo = DynamicHttpControllerManager.GetInstance().GetControllerInfo(serviceName);
                var controller = DynamicHttpControllerManager.GetInstance().Resolve(serviceName);
                if (controller == null)
                    return base.SelectController(request);

                var controllerDescriptor = new DynamicHttpControllerDescriptor(_configuration, serviceName, controllerInfo.ControllerType);
                controllerDescriptor.Properties["ServiceName"] = serviceName;
                controllerDescriptor.Properties["ActionName"] = actionName;
                controllerDescriptor.Properties["IsDynamicController"] = true;
                controllerDescriptor.Properties["ServiceType"] = controllerInfo.ServiceType;
                controllerDescriptor.Properties["ControllerType"] = controller.GetType();
                return controllerDescriptor;
            }
                 
        }

        return base.SelectController(request);
    }
}
```

## DynamicHttpActionSelector

既然通过路由中的 ServiceName 可以对 Controller 进行**"筛选"**，那么，我们自然可以通过路由中的 ActionName 来对 Action 进行**筛选"**。Action 是控制器中的概念，对应一般的接口或者类，我们称之为方法，因此，DynamicHttpActionSelector 在这里实现针对 Action 的筛选，它继承 ApiControllerActionSelector 类并重写了 SelectAction()方法，下面给出具体的实现：

```CSharp
public class DynamicHttpActionSelector : ApiControllerActionSelector
{
    public override HttpActionDescriptor SelectAction(HttpControllerContext controllerContext)
    {
        var isDynamicController = controllerContext.ControllerDescriptor.Properties.ContainsKey("IsDynamicController");
        if (isDynamicController)
        {
            var controllerType = new object();
            if (controllerContext.ControllerDescriptor.Properties.TryGetValue("ControllerType", out controllerType))
            {
                var actionName = controllerContext.ControllerDescriptor.Properties["ActionName"].ToString();
                var methodInfo = ((Type)controllerType).GetMethod(actionName);
                if (methodInfo == null)
                    return base.SelectAction(controllerContext);

                return new DynamicHttpActionDescriptor(controllerContext.ControllerDescriptor, methodInfo);
            }
        }

        return base.SelectAction(controllerContext);
    }
}
```

和筛选 Controller 的过程类似，首先我们会判断这是不是一个动态的 Controller，请注意在 DynamicHttpControllerSelector 中，我们为 ControllerDescriptor 添加了大量的 Properties，这些 Properties 可以在这里继续使用。显然，我们只需要关注动态的 Controller 即可，如果可以通过 ActionName 找到对应的 MethodInfo，那就说明当前 Controller 中存在指定的 Action，反之则需要调用父类方法按微软默认的实现去处理。其实，这里不好的一点就是，我们的通过反射获取 MethodInfo 时，需要传入 ActionName 即方法的名字，而方法的名字是区分大小写的，这会导致我们的 URL 必须区分大小写，这不太符合 RESTful API 风格。同样额，这里定义了一个类型 DynamicHttpActionDescriptor，它继承自 ReflectedHttpActionDescriptor，它需要传入 MethodInfo，这样 MVC 就知道应该去调用控制器的哪一个方法了。

## 容器注册及服务替换

在我们实际的业务系统中，存在着大量的 WCF 接口，它们都是通过 ServiceHost 这种方式来托管，然后在调用端通过代理类的方式来相互调用，因此把 WCF 迁移到 Web API 上，被抛弃的仅仅是这些.svc 的文件，而这些 WCF 接口依然可以继续使用。在之前的文章中，我们用 Castle 的 Dynamic Proxy 来代替各种手写的代理类，在这篇文章中我们继续沿用 ICalculator 这个接口示例，它包含着最为简单加减乘除四个方法，那么，我们应该怎样把这个接口变成一个 Web API 呢？这就是所谓的容器注册和服务替换啦！首先我们来注册 ICalculator 这个服务，它的代码只有一行：

```CSharp
DynamicHttpControllerManager.GetInstance().RegisterType<CalculatorService, ICalculator>();
```

这是一个典型的依赖注入，其中 CalculatorService 是 ICalculator 的实现类，它到底做了什么呢？我们来看看本质：

```CSharp
public void RegisterType<TImplement, TInterface>(string serviceName = "")
{
    if (string.IsNullOrEmpty(serviceName))
        serviceName = GetServiceName<TImplement>();

    _container.Register(
        Component.For(typeof(TImplement), typeof(TInterface)),
        Component.For<DynamicApiInterceptor<TInterface>>().LifestyleTransient(),
        Component.For<BaseController<TInterface>>().Proxy.AdditionalInterfaces(typeof(TInterface))
            .Interceptors<DynamicApiInterceptor<TInterface>>().LifestyleTransient()
            .Named(serviceName)
        );

    _controllerInfoList.Add(serviceName, new DynamicControllerInfo(typeof(TInterface)));
}
```

有没有觉得这段代码非常熟悉，实际上这就是我们这篇文章最开始提出的问题：怎么样对一个类和接口进行租户。一开始我们是用一个最普通的类、一个最普通的接口来演示这种可能性，而这里我们不过将其推广到一个特殊的场景，如果这个类是一个继承了 ApiController 的 BaseController 呢？这是一个由一般到特殊的过程。如你所见，内部的确使用了 Castle 的容器来处理依赖注入，而_controllerInfoList 则存储了 Controller 相关的信息，方便我们在整个流程中随时获取这些信息。完成容器注册以后，我们就可以着手对 MVC 中的默认组件进行替换工作啦，我个人建议，替换工作放在整个 Global.asax 的最前面：

```CSharp
var configuration = GlobalConfiguration.Configuration;
var dynamicControllerSelector = new DynamicHttpControllerSelector(configuration);
var dynamicHttpControllerActivtor = new DynamicHttpControllerActivtor();
var dynamicActionSelector = new DynamicHttpActionSelector();
GlobalConfiguration.Configuration.Services.Replace(typeof(IHttpControllerSelector), dynamicControllerSelector);
GlobalConfiguration.Configuration.Services.Replace(typeof(IHttpActionSelector), dynamicActionSelector);
GlobalConfiguration.Configuration.Services.Replace(typeof(IHttpControllerActivator), dynamicHttpControllerActivtor);
```

假设现在我希望调用 ICalcultor 接口中的 Add 方法，理论上它的 URL 应该是**http://localhost/Service/Calculator/Add**，因为截至到目前为止，所有的接口默认都是通过 Get 来访问的，下面是整个流程第一次跑通时的截图：

![迁移后的ICalculator接口](https://ww1.sinaimg.cn/large/4c36074fly1g49z1cvrw3j20pe05njrj.jpg)

# 接口迁移后的二三事

现在，我们完成了 ICalculator 接口的改造，它从一个 WCF 服务变成了一个 Web API，而在这个过程中，我们发现一点点问题。首先，Web API 中的 URL 是不区分大小写的，而我们这里的 ServiceName、ActionName 都是严格区分大小写的。其次，接口方法中的 out、ref、params 等关键字不适用于 Web API 语境，需要进一步对接口进行改造。再者，Web API 需要区分 GET、POST、PUT、DELETE 等动词，返回值需要统一调整为 JSON 格式。最后，完成改造的动态 API 需要通过 RestSharp 或者 HttpClient 等 HTTP 客户端来调用，以替换原有的 WCF 代理方法。这里简单对后面这两个问题做下说明，因为前两个问题，都是历史遗留问题啦，哈哈😄。

## HTTP 动词支持

为了让接口支持不同的 HTTP 动词，我们需要对整个设计进行进一步优化。为什么我会把这件事情看得如此重要呢？因为在我看来，RESTful 风格的 API 大概会有这样几种级别，第一种级别指仅仅使用了 HTTP 协议来设计 API，第二种级别是在 API 设计中引入资源的概念，第三种级别是合理地使用 HTTP 动词如 GET、POST、PUT 等，第四种级别是使用 HATEOSA 来返回用户接下来可能的意图。可惜在实际的应用种，能做到第二种级别的都相当不容易啦。比如某接口不支持 GET 操作，原因是它需要附加 token 在 Body 中，因此在改造接口的过程中，哪怕参数是最简单的值类型，它还是必须要用 POST 方式来请求。可其实这种问题，如果把 token 附加在 HTTP 首部中，或者干脆就使用标准的 Authorizatin 字段完全就能解决啊。为了让这个方案更完美一点，我们对 DynamicHttpActionDescriptor 进行改造，重写它的 SupportedHttpMethods 属性：

```CSharp
var isDynamicController = controllerDescriptor.Properties.ContainsKey("IsDynamicController");
if (isDynamicController)
{
    var serviceType = controllerDescriptor.Properties["ServiceType"];
    var httpVerbAttributes = ((Type)serviceType).GetMethod(methodInfo.Name).GetCustomAttributes<Attribute>()
        .Where(t => typeof(IActionHttpMethodProvider).IsAssignableFrom(t.GetType()))
        .ToList();

    if (httpVerbAttributes.Any())
    {
        //根据路由来获取Http动词
        if (httpVerbAttributes.Count > 1)
            throw new Exception($"Multiple http verb matched in method {methodInfo.Name} of {((Type)serviceType).Name}");

             _httpVerbs = GetHttpVerbByRoute(httpVerbAttributes);
        }
        else
        {
            //根据方法名称获取Http动词
            _httpVerbs = GetHttpVerbByMethod(methodInfo);
        }
    }
}
```

其原理说起来并不复杂，检查方法上是否有 HTTPGet、HttpPost、HttpPut 等标签，如果存在，则添加相应的 HTTP 动词到**_httpVerbs**集合中；如果不存在，则根据方法的名字来构建相应的 HTTP 动词。譬如以 Add、Create 等开头的方法对应 POST 请求，以 Get 开头的方法对应 GET 请求，以 Update 开头的方法对应 PUT 请求，以 Delete 开头的方法对应 DELETE 请求等。最终，我们只需要把**_httpVerbs**作为 SupportedHttpMethods 属性的返回值即可。

## 接口返回值优化

通常在编写控制器的时候，我们会使用 JSON 作为接口的返回值，这是因为 JSON 在信息冗余度上相比 XML 更低，而且 JSON 和 JavaScript 有着密不可分的联系，所以使用 JSON 作为返回值会流行起来一点都不奇怪。我们知道，WCF 是可以实现 Web Service 这种所谓的 SOAP 架构的，而 WebService 本质上是使用 XML 进行通信的 HTTP，在调用 WCF 接口的时候，接口的参数、返回值都会被序列化为 XML。平时我们手写 Controller 的时候，通常是在 Controller 层调用一层薄薄的 Service 层，然后对结果进行封装，使其成为对前端更友好的数据类型，可当我们调用动态的 Controller 时，其接口的返回值是在接口中定义好的，我们不可能去修改已经在使用中的 Service 定义。

虽然微软的 Web API 中可以自动对返回值进行序列化，参考最经典的 ValuesController，它是微软对 RESTful 风格的一种标准实现，具体表现为 Get()、Post()、Put()、Delete()四个方法，分别对应 GTE、POST()、PUT()、DELETE(四个 HTTP 动词，这就是所谓的约定大于配置，并且这些方法的返回值都不是 ActionResult 或者 IHttpActionResult，但整个框架依然可以帮我们将其序列化为 JSON，这一切是为什么呢？其实，我们只需要重写 DynamicHttpActionDescriptor 的 ReturnType 属性，同时重写 DynamicHttpActionDescriptor 的 ExecuteAsync()方法就可以达到这一目的：

```CSharp
public override Type ReturnType
{
    get
    {
        return typeof(DynamicApiResult);
    }
}

public override Task<object> ExecuteAsync(HttpControllerContext controllerContext, IDictionary<string, object> arguments, CancellationToken cancellationToken)
{
    return base.ExecuteAsync(controllerContext, arguments, cancellationToken)
        .ContinueWith(task =>
        {
            try
            {
                if (task.Result == null)
                {
                    return new DynamicApiResult() { Flag = true };
                }

                if (task.Result is DynamicApiResult)
                {
                    return task.Result;
                }

                return new DynamicApiResult() { Flag = true, Result = task.Result };
            }
            catch (AggregateException ex)
            {
                throw ex;
            }
        });
}
```

从代码中大家大致可以猜出 DynamicApiResult 的结构了，它包含三个属性：Flag、Msg、Result。这是一个最常见的 Web API 的返回值封装，即通过 Flag 判断方法是否调用成功，通过 Msg 来返回异常信息，通过 Result 来返回具体的返回值。最近对接某公司的 API 接口的时候，发现一个非常奇葩的现象，一般没有返回值可以返回 null 或者空字符串，可这家公司居然返回的是**”无数据"**，你以为这是放在 Msg 里的吗？不，人家是放在 Result 里的。对此，我只能说，互联网发展到 2019 年了，那些年野蛮生长留下的坑却还一直都在。好了，现在我们来看看接口调用的结果，喏，这次是不是感觉顺眼多啦！

![优化后的ICalculator接口返回值](https://ww1.sinaimg.cn/large/4c36074fly1g49z2ku45tj20il06dmxa.jpg)

# POCOController 

其实，这篇文章写到这里就已经结束啦，因为对于一般的 ASP.NET 项目，这篇文章里所分享这些内容，基本上可以实现我们最初的目标，即把老系统中的 WCF 接口迁移到 Web API 上，从长远的角度来看，这是为了后续迁移到.NET Core 上做准备，其实不单单是 WCF，任何的接口、服务都可以顺着这种思路去做扩展，手写 Controller 虽然是最容易上手的实践方式，可随着业务的不断推进，无一例外地出现接口爆炸的现象，在没有注册中心的情况下，业务系统间互相调对方的 Web API 简直叫一个混乱，你能想象一家公司里的不同业务系统，居然没有通用的网关去做接口的授权吗？反正我最近是见识到了某友的混乱。这篇文章中的思路，其实是参考了 Abp 这个框架中的 DynamicApiController 这一功能，可我们大多数人都没怎么好好用过这项技术，.NET Core 就来了，Abp 官方着手开发的 Abp vNext 就是基于.NET Core 的下一代 Abp 框架，不知道届时会不会有这个功能。

既然说到了,NET Core，那么就不可避免地要说到.NET Core 里的 POCOController。因为 ASP.NET 与 ASP.NET Core 的机制完全不同，所以，我们在这篇文章里的实现是无法直接用到 ASP,NET Core 里的，这听起来有点遗憾是不是，就在我写这篇博客的前几天，我看到有人把 Abp 的 DynamicApiController 移植到了.NET Core 下面，还是熟悉的味道，但内部的原理已然大为不同。具体来讲, .NET Core 下的 POCOController 特性会让这一切更简单。所谓 POCOController，就是指任意一个类都可以是 Controller。我们都知道在 ASP.NET 下，要写一个 Web API 必须继承 ApiController，就是说这个类必须实现了 IHttpController 接口，就是因为有这个限制，所以，我们不得不通过 Castle 来动态生成一个 Controller，既然现在 ASP.NET Core 里可以打破这一限制，那么实现起来自然会非常简单。限于这篇文章的篇幅(截至到这里已经将近 6000 余字)，我将在下一篇文章中和大家分享这一特性的相关内容。

# 本文小结

在传统的 ASP.NET 项目向 ASP.NET Core 迁移的过程中，我们遇到的第一个阻力就是作为内部 RPC 使用的 WCF。因此，收到上一篇文章基于 Castle 动态代理这一思路的影响，参考 Abp 框架中的 DynamicApiController 功能，我们分享了一种可以为任意接口动态生成 Controller 的思路，其核心原理是通过 Castle 中的**AdditionalInterfaces**功能，将指定接口和 ApiController 进行组合，使得一个普通的接口可以像 Controller 一样被调用。在这个过程中，我们回顾了 ASP.NET MVC 的基本原理，了解了 MVC 是如何根据路由筛选 Controller、激活 Controller 和筛选 Action，在此基础上，我们对微软的 MVC 进行了一次 Hack，使用我们自定义的组件替换了微软的默认实现，从而可以让原来托管在 ServiceHost 上的接口，通过 Web API 来访问和调用。当然，这篇文章里没有实现自定义的路由、过滤器的支持，所谓抛砖引玉，Abp 的代码本身在 Github 上就可以找到，大家如何对此感兴趣的话，可以做进一步的研究和扩展。我们实现了服务端的切换，这意味着在客户端同样需要一次切换，预知后事如何，请大家关注我的下一篇博客，以上就是我这篇博客的全部内容了，谢谢大家！

# 参考文章

* [Castle 中 AdditionalInterfaces 用法介绍](https://www.cnblogs.com/1zhk/p/5399548.html)
* [ABP 源码分析三十五：ABP 中动态 WebAPI 原理解析](https://www.cnblogs.com/1zhk/p/5418694.html)
* https://github.com/FJQBT/ABP