---
abbrlink: 3291578070
categories:
- 编程语言
date: 2018-03-21 19:35:40
description: 今天这篇文章，我们从一个实际项目的背景出发，引出使用Unity框架来简化异常处理和日志记录流程这一想法，在正式实践这一想法前，我们首先了解了Unity框架中提供的三种拦截器及其各自优劣，在此基础上我们实现了LogHandler和ExceptionHandler两个组件，并展示了如何使用这两个组件，探讨使用整个AOP机制对现有项目的影响有多大，以及为什么我们需要Unity框架等问题，框架固然重要，了解为什么使用框架则更重要
tags:
- AOP
- 异常
- 日志
title: 使用Unity框架简化应用程序异常处理及日志记录流程
---

&emsp;&emsp;最近公司安排学习项目代码，前后花了一周左右的时间，基本熟悉了项目中的各个模块，感觉项目难度上整体偏中等。这是一个具备完整前端和后端流程的项目，在学习这个项目的过程中，我逐渐发现某些非常有趣的东西，比如在Web API的设计中采用严谨而完善的错误码、使用OAuth和JWT对API资源进行访问控制，在JavaScript中使用修饰器特性来实现日志记录等等，这些东西我会在后续的博客逐步去整理，今天想说的是如何通过Unity框架来简化应用程序异常处理和日志记录流程，而之所以关注这个问题，是因为我发现项目中接近滥用的异常处理，以及我不能忍受的大量重复代码。

# 背景描述
&emsp;&emsp;由于业务场景上的需要，我们在产品中集成了大量第三方硬件厂商的SDK，这些SDK主要都是由C/C++编写的动态链接库，因此在使用这些SDK的过程中，通常频繁地使用返回值来判断一个方法是否成功被调用，虽然项目上制定了严格的错误码规范，可当我看到大量的Log()方法和业务逻辑混合在一起时，我内心依然是表示拒绝的，甚至我看到在捕获异常以后记录日志然后继续throw异常，这都是些什么鬼操作啊，考虑到我的语言描述得可能不太准确，大家可以从下面两段代码来感受下整体画风：
```CSharp
public short LoginTerminal(string uid,string pwd)
{
    try
    {
	    Log.BeginLog()
	    return SDK.Login(uid,pwd)
    }
	catch(Exception ex)
	{
	    log.LogError(ErrorCode.E2301,ex)
	    throw new TerminalException(ex.Message);
	}
    finally
	{
	    Log.EndLog()
	}
}

```
&emsp;&emsp;这是一段相对完整的业务逻辑代码，当然这里都是伪代码实现，这里我比较反感的两个地方是：第一，从头出现到尾的BeginLog()/EndLog()这对方法；第二，在Catch块中记录完日志然后将异常再次抛出。经过我对项目的一番了解，BeginLog()/EndLog()这对方法会在日志中记录某个方法开始执行和结束执行的位置。在方法执行前后插入代码片段，这不就是面向切面编程(AOP)的思想吗？这里记录完日志然后再抛出异常的做法，我个人是不大认同的，因为我觉得拦截异常应该有一个统一的入口，因为异常会继续向上传递，既然如此，为什么我们不能统一地去处理异常和记录日志呢？难道就一定要让Log这个静态类无处不在吗？同样地，我们注意到项目还会有下面这样的代码：
```CSharp
public void ProcessTerminal(object sender,ProcessEventArgs args)
{
    try
    {
        Log.BeginLog();
        var terminal = (Termainal)sender;
        var result = terminal.Process(args);
    }
    finally
    {
        Log.EndLog();
    }

}
```
&emsp;&emsp;这种代码看起来不再关注异常，可和第一段一样，从头出现到尾的BeginLog()/EndLog()简直不能忍，而且这里的try...finally结构难免让人想起using的语法糖，那么这样是不是可以考虑让这个Log拥有类似的结构，换言之，我们总不能一直都在每一个方法里，重复写BeginLog()/EndLog()这两个方法吧，既然EndLog()方法总是在finally块里被执行，那为什么不考虑把它放到Dispose()方法里(前提是有一个结构实现IDispose接口)。你问我是不是有代码洁癖啊？我真的没有，我就是懒，不喜欢重复做一件事情。所谓"管中窥豹，可见一斑"，大家可以想象整个项目会是什么样子。

&emsp;&emsp;好了，为了避免让自己写这种糟糕的代码，我决心使用Unity框架来简化下这里的异常处理和日志记录流程，一个有追求的程序，如果可以交给自动化工具去做的事情，为什么要一次又一次地重复去写呢？我们可以吐槽一段代码写得有多糟糕，可我们所做的任何努力，都是为了让自己不变成这个样子。Unity框架提供的AOP，即面向切面编程，不就可以做这样的事情吗？所以，能动手的就直接动手，君子有所为有所不为，不要重复自己，

# Unity框架与AOP
&emsp;&emsp;好啦，交待完故事背景，今天的主角终于可以登场啦！经常关注我博客的朋友，一定知道我个人比较喜欢IoC/AOP这类所谓的"奇技淫巧"，就在今天我还在和一位同事在讨论Ioc，这位同事认为Ioc增加了代码的复杂性，不认为Ioc会为项目带来明显的便利性。其实我相信大道至简，任何框架对我们而言都是高度抽象的，可正是因为有了这些抽象的层次，我们渐渐学会了关注核心的东西。这里提到了Ioc，即控制反转，或者我们可以称之为依赖注入，那么Unity框架就是.NET下众多依赖注入框架之一，这里称之为Unity框架，主要是避免和跨平台游戏引擎Unity产生混淆，以下全部称之为Unity框架。Unity框架中提供了核心的依赖注入相关的接口，而微软的企业最佳实践库中为Unity扩展出了AOP相关的功能。除此以外，Spring.NET、Aspect.Core、AspectF等都是.NET下的AOP方案。那么在今天的故事中，我们遇到了的一个场景是在指定方法执行前、后插入代码片段，这是面向切面编程(AOP)的基本思想，为此，我们考虑使用Unity框架来简化应用程序中异常处理及日志记录流程。

## Unity中的三种拦截器
&emsp;&emsp;Unity中提供了三种典型的拦截器，为了选择一种合适的拦截器来实现我们的功能，我们首先来了解下这三种不同的拦截器各自的应用场景：
* TransparentProxyInterceptor：即透明代理拦截器，基于.NET Remoting 技术实现代理，它可以拦截对象的所有函数，缺点是被拦截对象必须继承自MarshalByRefObject。
* InterfaceInterceptor：顾名思义，即接口拦截器，仅拦截指定接口，显然只要目标类型实现了指定接口就可以拦截。C#不支持多继承，选择这种方式对代码的影响最小。
* VirtualMethodInterceptor：顾名思义，即虚方法拦截器，仅拦截虚方法，这个对目标类型的要求就非常高啦，一般我们不会考虑这种方式。

对Unity框架而言，不管我们使用哪一种拦截器，我们都需要通过UnityContainer这个容器来为目标类型注入拦截器，这样Unity框架会帮助我们生成代理对象，我们只要在使用代理对象的时候，这些拦截器才会真正工作。博主曾经以为定义好下面这些Handler就可以了，简直是图样图森破。好了，一个基本的代码流程如下，请不要问我配置文件怎么配，我真的不喜欢配置文件，搞得跟某配置狂魔语言似的，反正这些配置文件这次记住了下次还是会忘的，可下面这几行代码是不会轻易忘记的啊：
```CSharp
var container = new UnityContainer().AddNewExtension<Interception>().RegisterType<IBussiness, Bussiness>();
container.Configure<Interception>().SetInterceptorFor<IBussiness>(new InterfaceInterceptor());
var bussiness = container.Resolve<IBussiness>();
```
注意，这里不要直接从Github或者Nuget上下载Unity框架，因为最新版的Unity我实在是不会用啊！:joy: 我喜欢开箱即用的产品，我愿意钻研啊，可DeadLine永远会有终点！
我们需要从微软企业最佳实践库中[下载](https://www.microsoft.com/en-us/download/details.aspx?id=38789)以下动态链接库：
* CommonServiceLocator.dll
* Microsoft.Practices.Unity.Configuration.dll
* Microsoft.Practices.Unity.dll
* Microsoft.Practices.Unity.Interception.Configuration.dll
* Microsoft.Practices.Unity.Interception.dll
  考虑到我们这里需要实现两种功能，针对异常的异常处理流程，以及正常的日志记录流程，为此我们将实现ExceptionHandler和LogHandler两个组件。下面我们来一起了解这两个组件的实现过程，这里博主选择了最简单的ICallHandler接口，而非更一般的IInterceptionBehavior接口，主要希望让这个过程更简单些，同时实现在方法粒度上的可控，即我们可以选择性的去拦截某一个方法，而非全部的方法，因为在实际业务中并非所有的方法都需要拦截。

## LogHandler的实现
&emsp;&emsp;LogHandler主要用于记录日志，所以我们需要记录方法的名字，方法的参数以及方法执行的结果，甚至是是否引发异常，这些功能在AOP中是相对基础的功能，Unity框架为我们提供了这些基础设施，我们只要就可以获取到这些信息，然后将其记录到日志中即可。这里的代码如下：
```Csharp
public class LogHandler : ICallHandler
{
    int ICallHandler.Order { get; set; }

    IMethodReturn ICallHandler.Invoke(IMethodInvocation input, GetNextHandlerDelegate getNext)
    {
        var methodInfo = input.MethodBase;
        var methodName = methodInfo.Name;
        Logger.Log(string.Format("----------开始调用{0}----------", methodName));
        var parameters = methodInfo.GetParameters();
        var arguments = input.Arguments;
        var logInfo = parameters.Select(e => string.Format("{0}:{1}", e.Name, arguments[e.Position]));
        Logger.Log("传入的参数为:" + string.Join(",", logInfo.ToArray()));
        var result = getNext()(input, getNext);
        if (result.Exception != null)
            Logger.Log(string.Format("调用异常:{0}-{1}", result.Exception.Message, result.Exception.StackTrace));
        Logger.Log(string.Format("调用{0}的结果为：{1}", methodName, result.ReturnValue));
        Logger.Log(string.Format("----------结束调用{0}----------", methodName));
        return result;
    }
}
```
为了让这个Handler更好用一些，我们希望它可以以Attribute的方式出现在方法上面，这样被标记过的方法就会被Unity框架拦截，所以我们需要一个继承自Attribute类的东西，知道我为什么不喜欢配置文件吗？因为我有Attribute啊！幸运的是Unity框架为我们提供了这样一个基类：HandlerAttribute，由此下面的代码可以这样写：
```CSharp
[AttributeUsage(AttributeTargets.Method,AllowMultiple = true)]
class LogHandlerAttribute : HandlerAttribute
{
    public override ICallHandler CreateHandler(IUnityContainer container)
    {
        return new LogHandler();
    }
}

```

## ExceptionHandler的实现
&emsp;&emsp;对于ExceptionHandler来说，它相比LogHandler增加的功能在于，它需要处理异常，按照目前项目的异常处理习惯，这种和硬件相关的方法都会被定义为一个ErrorCode，为此我们的ExceptionHandler类中需要增加一个ErrorCode类型的成员，这是一个枚举类型。这里的代码实现如下：
```CSharp
public class ExceptionHandler : ICallHandler
{
    int ICallHandler.Order { get; set; }

    public string ErrorCode { get; set; }

    IMethodReturn ICallHandler.Invoke(IMethodInvocation input, GetNextHandlerDelegate getNext)
    {
        var methodInfo = input.MethodBase;
        var methodName = methodInfo.Name;
        Logger.Log(string.Format("--------------方法{0}执行开始--------------", methodName));
        var parameters = methodInfo.GetParameters();
        var arguments = input.Arguments;
        var logInfo = parameters.Select(e => string.Format("{0}:{1}", e.Name, arguments[e.Position]));
        Logger.Log("传入的参数为:" + string.Join(",", logInfo.ToArray()));
        var result = getNext()(input, getNext);
        if (result.Exception != null)
        {
            Logger.Log(string.Format("Error Code is {0}", ErrorCode));
            result.Exception = null;
            Logger.Log(string.Format("--------------方法{0}执行结束--------------", methodName));
            throw new Exception(ErrorCode);
        }
        Logger.Log(string.Format("--------------方法{0}执行结束--------------", methodName));
        return result;
    }
}

```
可以注意到ExceptionHandler相比LogHandler的变化，主要发生在异常处理这部分，如你所愿，我在拦截到异常以后抛出了一个对应ErrorCode的异常，虽然我不赞同这种做法，但为了尊重现有项目的编程风格，我只能写有这样一行看起来非常拙劣的代码，我真的没有代码洁癖，我仅仅是觉得它还不够好，就像我觉得自己还不够好一样，同样，它需要定义一个对应的Attribute类，这样我们可以更加自由地使用这些特性：
```CSharp
[AttributeUsage(AttributeTargets.Method,AllowMultiple = true)]
class LogHandlerAttribute : HandlerAttribute
{
    public override ICallHandler CreateHandler(IUnityContainer container)
    {
        return new LogHandler();
    }
}
```

# 本文小结
&emsp;&emsp;好了，现在我们可以来看，如何使用这篇文章中定义的两个组件：
```CSharp
var container = new UnityContainer().AddNewExtension<Interception>().RegisterType<IBussiness, Bussiness>();
container.Configure<Interception>().SetInterceptorFor<IBussiness>(new InterfaceInterceptor());
var bussiness = container.Resolve<IBussiness>();
var sum = bussiness.Add(12,23);
Console.WriteLine(sum);
var div = bussiness.Divide(1,0)
Console.WriteLine(div)
```
IBussiness接口及其实现类Bussiness定义如下：
```CSharp
public interface IBussiness
{

    int Add(int a, int b);
    int Divide(int a, int b);
}

public class Bussiness : MarshalByRefObject, IBussiness
{
    [LogHandler]
    public int Add(int a, int b)
    {
        return a + b;
    }

    [ExceptionHandler(ErrorCode = "E2303")]
    public int Divide(int a, int b)
    {
        return a / b;
    }
}
```

好了，现在我们来看一下结果：
![使用AOP简化后的异常处理和日志记录流程](http://img-blog.csdn.net/20180320235018714)

&emsp;&emsp;我们为此付出的代价是什么？第一，要有一个接口，写接口难道还有疑问吗？第二，要添加Attribute到指定方法上面，我保证这点时间足够你写好几遍重复代码了。第三，需要依赖注入机制，这个可能是到目前为止最大的影响，因为有了依赖注入以后，对象的实例化都交给了Unity框架，看起来我们好像被束缚了手脚，不能再任性地new一个对象实例出来，可这不正是依赖注入的精髓所在吗？我们就是需要Unity框架，来帮助我们管理这些模块间的依赖关系及其生命周期，如果你觉得这点代码不能接受，抱歉，任何依赖注入框架拯救不了你！


&emsp;&emsp;今天这篇文章，我们从一个实际项目的背景出发，引出使用Unity框架来简化异常处理和日志记录流程这一想法，在正式实践这一想法前，我们首先了解了Unity框架中提供的三种拦截器及其各自优劣，在此基础上我们实现了LogHandler和ExceptionHandler两个组件，并展示了如何使用这两个组件，探讨使用整个AOP机制对现有项目的影响有多大，以及为什么我们需要Unity框架等问题，框架固然重要，了解为什么使用框架则更重要！好啦，这就是今天这篇文章的内容啦，再次谢谢大家关注我的博客，各位晚安！:smile: