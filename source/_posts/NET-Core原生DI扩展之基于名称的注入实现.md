---
toc: true
title: .NET Core原生DI扩展之基于名称的注入实现
categories:
  - 编程语言
tags:
  - DI
  - 依赖注入
  - .NET Core
copyright: true
abbrlink: 1734098504
date: 2020-06-01 13:08:03
---
接触 .NET Core 有一段时间了，最大的感受无外乎无所不在的依赖注入，以及抽象化程度更高的全新框架设计。想起三年前 Peter 同学手写 IoC 容器时的惊艳，此时此刻，也许会有不一样的体会。的确，那个基于字典实现的 IoC 容器相当“简陋”，就像 .NET Core 里的依赖注入，默认(原生)都是采用构造函数注入的方式，可其实从整个依赖注入的理论上而言，属性注入和方法注入的方式，同样是依赖注入的实现方式啊。最近一位朋友找我讨论，.NET Core 里该如何实现 Autowried ，这位朋友本身是 Java 出身，一番攀谈了解到原来是指属性注入啊。所以，我打算用两篇博客来聊聊 .NET Core 中的原生 DI 的扩展，而今天这篇，则单讲基于名称的注入的实现。

[Autofac]()是一个非常不错的 IoC 容器，通常我们会使用它来替换微软内置的 IoC 容器。为什么要这样做呢？其实，微软在其官方[文档]()中早已给出了说明，即微软内置的 IoC 容器实际上是不支持以下特性的： 属性注入、基于名称的注入、子容器、自定义生存期管理、对迟缓初始化的 Func<T> 支持、基于约定的注册。这是我们为什么要替换微软内置的 IoC  容器的原因，除了Autofac 以外，我们还可以考虑 Unity 、Castle 等容器，对我个人而言，其实最需要的一个功能是“扫描”，即它可以针对程序集中的组件或者服务进行自动注册。这个功能可以让人写起代码更省心一点，果然，人类的本质就是让自己变得更加懒惰呢。好了，话题拉回到本文主题，我们为什么需要基于名称的注入呢？它其实针对的是“同一个接口对应多种不同的实现”这种场景。

OK ，假设我们现在有一个接口ISayHello，它对外提供一个方法SayHello：
``` CSharp
public interface ISayHello
{
  string SayHello(string receiver);
}
```
相对应地，我们有两个实现类，ChineseSayHello和EnglishSayHello：
```CSharp
//ChineseSayHello
public class ChineseSayHello : ISayHello
{
  public string SayHello(string receiver)
  {
      return $"你好，{receiver}";
  }
}

//EnglishSayHello
public class EnglishSayHello : ISayHello
{
  public string SayHello(string receiver)
  {
      return $"Hello，{receiver}";
  }
}
```
接下来，一顿操作猛如虎：
```CSharp
var services = new ServiceCollection();
services.AddTransient<ISayHello, ChineseSayHello>();
services.AddTransient<ISayHello, EnglishSayHello>();
var serviceProvider = services.BuildServiceProvider();
var sayHello = serviceProvider.GetRequiredService<ISayHello>();
```
没想到，尴尬的事情就发生了，大家来猜猜看，这个时候我们获取到的`ISayHello`到底是哪一个呢？事实上，它会获取到`EnglishSayHello`这个实现类，为什么呢？因为它后注册的呀！当然，微软的工程师们不可能想不到这个问题，所以，官方推荐的做法是使用`IEnumerable<ISayHello>`，这样我们就能拿到所有注册的`ISayHello`，然后自己决定到底要使用一种实现，类似下面这样：
```CSharp
var sayHellos = _serviceProvider.GetRequiredService<IEnumerable<ISayHello>>();
var chineseSayHello = sayHellos.FirstOrDefault(x => x.GetType() == (typeof(ChineseSayHello)));
var englishSayHello = sayHellos.FirstOrDefault(x => x.GetType() == (typeof(EnglishSayHello)));
```
可这样还是有一点不方便啊，继续改造：
```CSharp
services.AddTransient<ChineseSayHello>();
services.AddTransient<EnglishSayHello>();
services.AddTransient(implementationFactory =>
{
  Func<string, ISayHello> sayHelloFactory = lang =>
  {
    switch (lang)
    {
      case "Chinese":
        return implementationFactory.GetService<ChineseSayHello>();
      case "English":
        return implementationFactory.GetService<EnglishSayHello>();
      default:
        throw new NotImplementedException();
    }
  };

  return sayHelloFactory;
});
```
这样子，这个工厂类看起来就消失了对吧，其实并没有(逃
```CSharp
var sayHelloFactory = _serviceProvider.GetRequiredService<Func<string, ISayHello>>();
var chineseSayHello = sayHelloFactory("Chinese");
var englishSayHello = sayHelloFactory("English");
```
这距离我们的目标有一点接近了哈，唯一的遗憾是这个工厂类对调用方是透明的，可谓是隐藏细节上的失败。有没有更好的方案呢？好了，我不卖关子啦，一起来看下面的实现。

首先，我们定义一个接口`INamedServiceProvider`, 顾名思义，就不需要再解释什么了:
```CSharp
public interface INamedServiceProvider
{
  TService GetService<TService>(string serviceName);
}
```
接下来，编写实现类`NamedServiceProvider`:
```CSharp
public class NamedServiceProvider : INamedServiceProvider
{
  private readonly IServiceProvider _serviceProvider;
  private readonly IDictionary<string, Type> _registrations;
  public NamedServiceProvider(IServiceProvider serviceProvider, IDictionary<string, Type> registrations)
  {
    _serviceProvider = serviceProvider;
    _registrations = registrations;
  }

  public TService GetService<TService>(string serviceName)
  {
    if(!_registrations.TryGetValue(serviceName, out var implementationType))
      throw new ArgumentException($"Service \"{serviceName}\" is not registered in container");
    return (TService)_serviceProvider.GetService(implementationType);
  }
}
```
可以注意到，我们这里用一个字典来维护名称和类型间的关系，一切仿佛又回到三年前Peter手写IoC的那个下午。接下来，我们定义一个`INamedServiceProviderBuilder`, 它可以让我们使用链式语法注册服务：
```CSharp
public interface INamedServiceProviderBuilder
{
  INamedServiceProviderBuilder AddNamedService<TService>(string serviceName, ServiceLifetime lifetime) where TService : class;

  INamedServiceProviderBuilder TryAddNamedService<TService>(string serviceName, ServiceLifetime lifetime) where TService : class;

  void Build();
}
```
这里，Add和TryAdd的区别就是后者会对已有的键进行检查，如果键存在则不会继续注册，和微软自带的DI中的Add/TryAdd对应，我们一起来看它的实现：
```CSharp
public class NamedServiceProviderBuilder : INamedServiceProviderBuilder
{
  private readonly IServiceCollection _services;
  private readonly IDictionary<string, Type> _registrations = new Dictionary<string, Type>();
  public NamedServiceProviderBuilder(IServiceCollection services)
  {
    _services = services;
  }

  public void Build()
  {
    _services.AddTransient<INamedServiceProvider>(sp => new NamedServiceProvider(sp, _registrations));
  }

  public INamedServiceProviderBuilder AddNamedService<TImplementation>(string serviceName, ServiceLifetime lifetime) where TImplementation : class
  {
    switch (lifetime)
    {
      case ServiceLifetime.Transient:
        _services.AddTransient<TImplementation>();
      break;
      case ServiceLifetime.Scoped:
        _services.AddScoped<TImplementation>();
      break;
      case ServiceLifetime.Singleton:
        _services.AddSingleton<TImplementation>();
      break;
    }

    _registrations.Add(serviceName, typeof(TImplementation));
    return this;
  }

  public INamedServiceProviderBuilder TryAddNamedService<TImplementation>(string serviceName, ServiceLifetime lifetime) where TImplementation : class
  {
    switch (lifetime)
    {
      case ServiceLifetime.Transient:
        _services.TryAddTransient<TImplementation>();
      break;
      case ServiceLifetime.Scoped:
        _services.TryAddScoped<TImplementation>();
      break;
      case ServiceLifetime.Singleton:
        _services.TryAddSingleton<TImplementation>();
      break;
    }

    _registrations.TryAdd(serviceName, typeof(TImplementation));
    return this;
  }
}
```
相信到这里，大家都明白博主的意图了吧，核心其实是在`Build()`方法中，因为我们最终需要的是其实是`NamedServiceProvider`，而在此之前的种种，都属于收集依赖、构建ServiceProvider的过程，所以，它被定义为`NamedServiceProviderBuilder`，我们在这里维护的这个字典，最终会被传入到`NamedServiceProvider`的构造函数中，这样我们就知道根据名称应该返回哪一个服务了。

接下来，为了让它和微软自带的DI无缝粘合，我们需要编写一点扩展方法：
```CSharp
public static class ServiceCollectionExstension
{
  public static TService GetNamedService<TService>(this IServiceProvider serviceProvider, string serviceName)
  {
    var namedServiceProvider = serviceProvider.GetRequiredService<INamedServiceProvider>();
    if (namedServiceProvider == null)
      throw new ArgumentException($"Service \"{nameof(INamedServiceProvider)}\" is not registered in container");

    return namedServiceProvider.GetService<TService>(serviceName);
  }


  public static INamedServiceProviderBuilder AsNamedServiceProvider(this IServiceCollection services)
  {
    var builder = new NamedServiceProviderBuilder(services);
    return builder;
  }
}
```

现在，回到我们一开始的问题，它是如何被解决的呢？
```CSharp
services
  .AsNamedServiceProvider()
  .AddNamedService<ChineseSayHello>("Chinese", ServiceLifetime.Transient)
  .AddNamedService<EnglishSayHello>("English", ServiceLifetime.Transient)
  .Build();
var serviceProvider = services.BuildServiceProvier();
var chineseSayHello = serviceProvider.GetNamedService<ISayHello>("Chinese");
var englishSayHello = serviceProvider.GetNamedService<ISayHello>("English");
```
这个时候，对调用方而已，依然是熟悉的ServiceProvider，它只需要传入一个名称来获取服务即可，由此，我们就实现了基于名称的依赖注入。回顾一下它的实现过程，其实是一个逐步推进的过程，我们使用依赖注入，本来是希望依赖抽象，即针对同一个接口，可以无痛地从一种实现切换到另外一种实现。可我们发现，当这些实现同时被注册到容器里的时候，容器一样会迷惑于到底用哪一种实现，这就让我们开始思考，这种基于字典的IoC容器设计方案是否存在缺陷。所以，在.NET Core里的DI设计中还引入了工厂的概念，因为并不是所以的Resolve<T>都可以通过`Activator.Create`来实现，更不必说Autofac和Castle中还有子容器的概念，只能说人生不同的阶段总会有不同的理解吧！好了，这篇博客就先写到这里，欢迎大家给我留言，晚安！