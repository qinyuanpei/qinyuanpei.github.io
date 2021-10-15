---
toc: true
title: .NET Core 原生 DI 扩展之属性注入实现
categories:
  - 编程语言
tags:
  - DI
  - 依赖注入
  - .NET Core
  - 技巧
copyright: true
abbrlink: 1658310834
date: 2020-06-20 13:10:31
---
在上一篇博客里，我们为`.NET Core`原生 DI 扩展了基于名称的注入功能。而今天，我们要来聊一聊属性注入。关于属性注入，历来争议不断，支持派认为，构造函数注入会让构造函数变得冗余，其立意点主要在代码的可读性。而反对派则认为，属性注入会让组件间的依赖关系变得模糊，其立意点主要在代码是否利于测试。我认识的一位前辈更是留下一句话：**只要构造函数中超过 5 个以上的参数，我就觉得无法忍受**。我个人是支持派，因为我写这篇博客的动机，正是一位朋友向我吐槽公司项目，说一个控制器里单单是构造函数里的参数就有十来个。在这其中最大的痛点是，有些在构造函数中注入的类型其实是重复的，譬如`ILogger<>`、`IMapper`、`IRepository<>`以及用户上下文信息等，虽然继承可以让痛苦减轻一点，可随之而来的就是冗长的 base 调用链。博主参与的项目里不乏有大量使用静态类、静态方法的，譬如 LogEx、UserContext 等等，可这种实践显然与依赖注入的思想背道而驰，为吾所不取也，这就是这篇博客产生的背景啦！

好了，当视角正式切入属性注入的时候，我们不妨先来考虑这样一件事情，即：当我们从容器里 Resolve 一个特定的类型的时候，这个实例到底是怎么被创建出来的呢？这个问题如果给到三年前的我，我会不假思索的说出两个字——反射。的确，这是最简单的一种实现方式，换句话说，首先，容器收集构造函数中的类型信息，并根据这些类型信息 Resolve 对应的实例；其次，这些实例最终会被放到一个`object[]`里，并作为参数传递给`Activator.CreateInstance()`方法。这是一个一般意义上的 Ioc 容器的工作机制。那么，相对应地，关于属性注入，我们可以认为容器 Reslove 一个特定类型的时候，这个类型提供了一个空的构造函数(**这一点非常重要**)，再创建完实例以后，再去 Reslove 这个类型中的字段或者是属性。所以，为了在微软自带的 DI 上实现属性注入，我们就必须实现自己的 ServiceProvider——AutowiredServiceProvider，这个 ServiceProvider 相比默认的 ServiceProvider 多了一部分功能，即反射属性或者字段的过程。一旦想通这一点，我们可以考虑装饰器模式。

```CSharp
public class AutowiredServiceProvider : IServiceProvider, ISupportRequiredService {
    private readonly IServiceProvider _serviceProvider;
    public AutowiredServiceProvider (IServiceProvider serviceProvider) {
        _serviceProvider = serviceProvider;
    }

    public object GetRequiredService (Type serviceType) {
        return GetService (serviceType);
    }

    public object GetService (Type serviceType) {
        var instance = _serviceProvider.GetService (serviceType);
        Autowried (instance);
        return instance;
    }

    private void Autowried (object instance) {
        if (_serviceProvider == null || instance == null)
            return;

        var flags = BindingFlags.Public | BindingFlags.NonPublic;
        var type = instance as Type ?? instance.GetType ();
        if (instance is Type) {
            instance = null;
            flags |= BindingFlags.Static;
        } else {
            flags |= BindingFlags.Instance;
        }

        //Feild
        foreach (var field in type.GetFields (flags)) {
        var autowriedAttr = field.GetCustomAttribute<AutowiredAttribute> ();
            if (autowriedAttr != null) {
                var dependency = GetService (field.FieldType);
                if (dependency != null)
                    field.SetValue (instance, dependency);
            }
        }

        //Property
        foreach (var property in type.GetProperties (flags)) {
            var autowriedAttr = property.GetCustomAttribute<AutowiredAttribute> ();
            if (autowriedAttr != null) {
                var dependency = GetService (property.PropertyType);
                if (dependency != null)
                    property.SetValue (instance, dependency);
            }
        }
    }
}
```

装饰器模式，又被称之为“静态代理"，是面向切面编程(**AOP**)的实现方式之一，我们在这里为默认的 ServiceProvider 增加了`Autowired()`方法，它会扫描所有含`[Autowired]`标签的字段或属性，并尝试从容器中获取对应类型的实例。所以，这又说到了反对属性注入第二个理由，即：使用反射带来的性能问题，尤其是当依赖项间的引用关系异常复杂的时候。当然，所谓“兵来将挡，水来土掩”，反射产生性能损失，可以考虑用 Emit 或者表达书树作来替代反射，不过，微软貌似在.NET Core 中阉割了一部分 Emit 的 API，这些都是 Todo 啦你懂就好，我们继续往下说。接下来，为了替换掉微软默认的 ServiceProvider，我们还必须实现自己的 ServiceProviderFactory，像 Autofac、Unity、Castle 等容器，都是采用类似的做法来支持.NET Core。

```CSharp
 public class AutowiredServiceProviderFactory : IServiceProviderFactory<IServiceCollection> {
     public IServiceProvider CreateServiceProvider (IServiceCollection containerBuilder) {
         var serviceProvider = containerBuilder.BuildServiceProvider ();
         return new AutowiredServiceProvider (serviceProvider);
     }

     IServiceCollection IServiceProviderFactory<IServiceCollection>.CreateBuilder (IServiceCollection services) {
         if (services == null) return new ServiceCollection ();
         return services;
     }
 }
```
因为我们是以微软内置的 DI 为基础来进行扩展的，所以，在实现`AutowiredServiceProviderFactory`的时候，提供的泛型参数依然是`IServiceCollection`。它需要实现两个方法：`CreateBuilder`和`CreateServiceProvider`，在这里我们需要返回我们“装饰”过的 ServiceProvider。接下来，万事俱备，只欠东风，我们需要在项目入口(**Program.cs**)调用`UseServiceProviderFactory()`方法，如果你在.NET Core 使用 Autofac，应该会对此感到亲切：

```CSharp
public static IHostBuilder CreateHostBuilder(string[] args) =>
  Host.CreateDefaultBuilder(args)
    .ConfigureWebHostDefaults(webBuilder =>
    {
      webBuilder.UseStartup<Startup>();
    })
    .UseServiceProviderFactory(new AutowiredServiceProviderFactory());
```
至此，我们就完成了对微软默认的 ServiceProvider 的替换。假设我们有两个接口：`IFooService`和`IBarService`：
```CSharp
//IFooService && FooService
public interface IFooService {
  string Foo ();
  IBarService Bar { get; set; }
}

public class FooService : IFooService {
  [Autowired]
  public IBarService Bar { get; set; }
  public string Foo () => "I am Foo";
}

//IBarService && BarService
public interface IBarService {
  string Bar();
}

public class BarService : IBarService {
  public string Bar () => "I am Bar";
}
```
注意到`FooService`依赖`IBarService`，而我们只需要给`Bar`加上`[Autowired]`标签即可，风格上借鉴了`Spring`的`@Autowired`。只要这两个接口被注入到 Ioc 容器中，这个属性就可以自动获得相应的服务实例。一起来看下面的代码：
```CSharp
services.AddTransient<IFooService,FooService>();
services.AddTransient<IBarService, BarService>();
var serviceProvider = new AutowiredServiceProvider(services.BuildServiceProvider());
var fooService = serviceProvier.GetRequiredService<IFooService>();
Console.WriteLine($"{fooService.Foo()} , {fooService.Bar.Bar()}");
```
回到我们一开始遇到的那个问题，如果我们让`IFooService`变成 Controller 中的一个属性，是否就能解决构造函数参数冗余的问题了呢？下面是一段简单的代码：
```CSharp
[ApiController]
[Route("[controller]")]
public class WeatherForecastController : ControllerBase
{
  [Autowired]
  public IFooService Foo { get; set; }

  [Autowired]
  public ILogger<WeatherForecastController> Logger { get; set; }

  [HttpGet]
  [Route("Autowired")]
  public ActionResult GetAutowriedService()
  {
    return Content($"{Foo.Foo()} , {Foo.Bar.Bar()}");
  }
}
```
此时，我们会发现`Foo`属性提示空引用错误，这是为什么呢？这是因为 Controller 并不是通过 IoC 容器来负责创建和销毁的，为了实现属性注入的目的，我们就必须让 IoC 容器来全面接管 Controller 的创建和销毁，此时，我们需要做两件事情，其一，注册 Controller 到 IoC 容器中；其二，实现自定义的`IControllerActivator`，并替换默认的 ControllerActivator:
```CSharp
services.AddControllers();
services.AddControllersWithViews().AddControllersAsServices();
services.Replace(ServiceDescriptor.Transient<IControllerActivator, AutowiredControllerActivator>());
```
其中，`AutowiredControllerActivator`实现如下：
```CSharp
public class AutowiredControllerActivator : IControllerActivator
{
  public object Create(ControllerContext context)
  {
    if (context == null)
      throw new ArgumentNullException(nameof(ControllerContext));

    var controllerType = context.ActionDescriptor.ControllerTypeInfo.AsType();
    var serviceProvider = context.HttpContext.RequestServices;
    if(!(serviceProvider is AutowiredServiceProvider))
      serviceProvider = new AutowiredServiceProvider(context.HttpContext.RequestServices);
    var controller = serviceProvider.GetRequiredService(controllerType);
    return controller;
  }

  public void Release(ControllerContext context, object controller)
  {
    if (context == null)
      hrow new ArgumentNullException(nameof(ControllerContext));
    if (controller == null)
      throw new ArgumentNullException(nameof(controller));

    var disposeable = controller as IDisposable;
    if (disposeable != null)
      disposeable.Dispose();
    }
  }
}
```
此时，一切都会像我们期待的那样美好，返回正确的结果。目前，这个方案最大的问题是，在非 Controller 层使用的时候，还是需要构造`AutowirdServiceProvider`实例。其实，在`AutowiredControllerActivator`里同样有这个问题，就是你即使实现`IServiceProviderFactory`接口，依然没有办法替换掉默认的 ServiceProvider 实现，只能说它能解决一部分问题，同时又引入了新的问题，最直观的例子是，你看到一个接口的时候，你并不能找全所有加了`[Autowired]`标签的依赖项，所以，直接造成了依赖关系模糊、不透明、难以测试等等的一系列问题，我认为，在一个可控的、小范围内使用还是可以的。

