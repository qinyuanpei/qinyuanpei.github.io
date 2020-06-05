---
abbrlink: 2954591764
categories:
- 编程语言
date: 2019-05-10 16:27:50
description: 顺着这样的思路，如果我们可以把ChannelFactory注入到RealProxy中，就可以在接口调用过程中记录相关信息，这样我们就可以关注调用本身，因为所有的我们不想写的代码，现在全部都由代理类接管了，更重要的是，所有通过这种方式调用的WCF服务，都可以以一种统一而简洁的方式去处理，永远不用担心因为某个人忘记写代理方法而出现问题，下面给出整个实现的关键代码：;现在，我们来考虑WCF，WCF需要通过ChannelFactory来创建和释放，而这恰恰是代理类所做的事情，就像下面的代码一样，我们通常会把所有的WCF集中配置在一个地方，并通过构造Binding和终结点地址来创建一个WCF服务，在调用服务的过程中，会对调用时间、异常信息等进行记录，这其实和我举的第一个例子完全一致，那么我们能不能用RealProxy来实现这些功能呢;首先，我们定义一个简单的接口ICalculator，它含有加、减、乘、除四种基本运算，我们希望记录每个方法调用的参数、结果和执行时间，因此通过RealProxy对现有类型CalculatorService进行代理，并动态地创建代理对象来供调用方使用，下面给出关键代码：
tags:
- AOP
- Castle
- Dynamic Proxy
title: 又见AOP之基于RealProxy实现WCF动态代理
---

最近一直在研究Mongodb和ElasticSearch之间同步数据的问题，苦于到目前为止，并没有取得任何实质性的进展。偶尔“趁得浮生半日闲暇”，看一看Web API设计方面的书籍，和前辈交流下项目中的历史遗留问题，最为直观的感受就是，这个世界上任何方案的最终落地，都经过理想和现实的无数次挣扎，比如我们希望迁移项目到.NET Core平台上，初步分析大概有将近1000多个无法兼容的地方，维持现状固然可以保证整个项目的稳定，可如果真到了不得不升级的地步，面临的问题可能会越来越多，所谓“凡事预则立，不预则废”，早一点准备总是好的。既然说到里历史问题，那么，今天这篇文章就来说一说，基于RealProxy实现WCF动态代理。

# 故事背景

在我们的业务系统中，对内是使用WCF来进行相互通信的，而对外则是使用Web API来进行数据交换。关于RPC还是REST的争论由来已有，严格地来说，两者没有绝对的高下之分，从风格上而言，RPC倾向于让接口映射到一个方法上，而REST则倾向于让接口映射到一个资源上。从我们实际的使用情况来看，REST在系统中应用得并不是很完美，因为大多数情况下，我们实现的仅仅是HTTP+JSON这样一种协议组合，因此业务系统中存在着大量的WCF接口供系统内部调用。

![内部服务调用示意图](https://ww1.sinaimg.cn/large/4c36074fly1g2wasftjc2j20dl0b6t8z.jpg)


最早的时候，是通过T4模板来生成针对某个接口的代理类，而代理类中通常封装了ChannelFactory的创建、释放等等WCF相关的代码，实际应用中还会对WCF接口的异常进行捕获、记录日志、统计调用时间等，因此早期的T4模板实际上承担了生成代理类的职责。虽然业务的不断推进，接口中加入的新方法越来越多，导致具体业务类中的代码越来越多，动辄出现单个文件中代码行数达3000行以上，与此同时，每当WCF接口中增加了新方法，就不得不在其相关的代理类中增加代理方法。坦白地讲，就是增加一个看起来差不多的方法，因为你依然要处理ChannelFactory的创建、释放、异常处理、日志记录等等的工作。

其实，WCF可以直接生成客户端代码，因为每个WCF的服务都可以以WebService服务的形式暴露出来，而只要是WebService，总可以通过WSDL生成一个代理类。不过这显然不利于团队间的协作，更不利于服务终结点配置的集中化，更失去了异常处理、日志记录等等这些“通用”工作的可能性。T4应该可以基于“工作”，可显然大家觉得手写比生成要来得更容易些，所以，这个故事最终演变成这样一个局面，我们不得不通过局部类(Partial Class)的方式来开辟新的类文件。

![系统中充斥着大量类似的代码](https://ww1.sinaimg.cn/large/4c36074fly1g2wad7ddv6j20tn09bt9o.jpg)

那么，说了这么多，从一个历史遗留问题入手，它真正的痛点在哪里呢？在我看来，主要有两点：第一，是手写代理类的“此恨绵绵无绝期”，明明就是对接口的简单封装，看起来是增加一个代理方法，其实最多就是复制黏贴，因为代理方法的核心代码就是调用接口，而剩下的都是重复的“服务型”代码；第二，是异常处理、日志记录的“哀鸿遍野”，同核心代码交织在一起，一遍又一遍的“重复”，为什么不考虑让它统一地去处理呢？难道每个人都抄着同一段代码，这样就实现了某种意义上的复用吗？

# RealProxy介绍

既然像我这样懒惰的人，不愿意像别人一样手写代理类，那么我的思路又是什么呢？显然，从这篇文章的题目，你就可以看出，我这里要说的是动态代理，原来的代理类同样属于代理，它是在编译时期间生成了一个代理类，我们以为在调用这个代理类，可其实真正去工作的是ChannelFactory，这种方式称之为“静态代理”。如果你了解过设计模式，应该会知道相对应的代理模式，这里不再展开开来讲这这个设计模式，可以明确的是，动态代理就是在运行时期间动态创建一个代理对象的实例，它可以完全模拟被代理对象的行为，而我们的目的，就是要和手写的代理类永远地说再见！

好了，下面隆重介绍本文的主角——RealProxy。相信大家一定听说过AOP，即所谓的面向切面编程。它可以让我们在某一个所针对的横切面编程，并讲这种功能应用到所有相同的横切面上。譬如对方法级别的横切面增加拦截器，那么所有的方法都可以在执行前后具备相同的逻辑，典型的如日志记录、指定操作前的检验等等。而RealProxy 类恰恰提供最基本的代理功能，它是一个抽象类，必须通过重写其 Invoke()方法并添加新功能来继承，该类位于System.Runtime.Remoting.Proxies 命名空间中，通过重写Invoke()方法，我们就可以在被代理对象调用前后插入相关逻辑，而通过GetTransparentProxy()方法，则可以返回实际的代理对象。所以，通过这个原理，我们就可以在运行时期间，动态创建出指定类型的实例。这里，我们从一个简单的例子来开始，以帮助大家更好的理解RealProxy。

```CSharp
public interface ICalculator
{
    double Add(double n1, double n2);
    double Subtract(double n1, double n2);
    double Multiply(double n1, double n2);
    double Divide(double n1, double n2);
}

public class CalculatorService : ICalculator
{
    public double Add(double n1, double n2)
    {
        return n1 + n2;
    }

    public double Subtract(double n1, double n2)
    {
        return n1 - n2;
    }

    public double Multiply(double n1, double n2)
    {
        return n1 * n2;
    }

    public double Divide(double n1, double n2)
    {
        return n1 / n2;
    }
}
```

首先，我们定义一个简单的接口ICalculator，它含有加、减、乘、除四种基本运算，我们希望记录每个方法调用的参数、结果和执行时间，因此通过RealProxy对现有类型CalculatorService进行代理，并动态地创建代理对象来供调用方使用，下面给出关键代码：

```CSharp
public class CalculatorServiceProxy : RealProxy
    {
        private Server.Service.ICalculator _calculator;

        public CalculatorServiceProxy(Server.Service.ICalculator calculator) :
            base(typeof(Server.Service.ICalculator))
        {
            _calculator = calculator;
        }

        public override IMessage Invoke(IMessage message)
        {
            var methodCall = message as IMethodCallMessage;
            var methodInfo = methodCall.MethodBase as MethodInfo;
            var startTime = DateTime.Now;
            var serviceName = _calculator.GetType().Name;
            var methodName = methodInfo.Name;

            try
            {
                Console.WriteLine("调用{0}服务的{1}方法开始...", serviceName, methodName);
                var argsInfo = new Dictionary<string, object>();
                for (int i = 0; i < methodCall.ArgCount; i++)
                {
                    argsInfo.Add(methodCall.GetArgName(i), methodCall.Args[i]);
                }
                Console.WriteLine("当前传入参数:{0}", JsonConvert.SerializeObject(argsInfo));
                var result = methodInfo.Invoke(_calculator, methodCall.InArgs);
                if (result != null)
                    Console.WriteLine("当前返回值:{0}", JsonConvert.SerializeObject(result));
                return new ReturnMessage(result, null, 0, methodCall.LogicalCallContext, methodCall);
            }
            catch (Exception ex)
            {
                Console.WriteLine("调用{0}服务的{1}方法失败,失败原因：{2}", serviceName, methodName, ex.Message);
                throw ex;
            }
            finally
            {
                Console.WriteLine("调用{0}服务的{1}方法结束,共耗时{2}秒", serviceName, methodName, DateTime.Now.Subtract(startTime).TotalSeconds);
                Console.WriteLine("----------------------------------");
            }
        }
    }
```

可以注意到，最核心的代码是在Invoke()方法中，在这里我们增加了我们想要的功能，但这些功能丝毫不会影响到CalculatorService，当我们通过构造函数给RealProxy传入被代理对象后，它就会对被代理对象的特定方法进行拦截，这里实际上就是加、减、乘、除四个方法。OK，到现在为止，这些都是我们的想像而已，具体我们实现执行结果来看。

```CSharp
var serviceProxy = new CalculatorServiceProxy(new CalculatorService());
var calculator = (ICalculator)serviceProxy.GetTransparentProxy();
calculator.Add(12, 24);
calculator.Subtract(36, 10);
calculator.Multiply(12, 35);
calculator.Divide(36, 12);
```

现在，我们可以说，刚刚所说的一切都是真的，因为我们真的创建了一个ICalculator接口的实例，它真的记录了每个方法调用的参数、结果和执行时间。

![RealPrxoy牛刀小试](https://ww1.sinaimg.cn/large/4c36074fly1g2w7brst4dj20rm0eqgmc.jpg)

# WCF动态代理

现在，我们来考虑WCF，WCF需要通过ChannelFactory来创建和释放，而这恰恰是代理类所做的事情，就像下面的代码一样，我们通常会把所有的WCF集中配置在一个地方，并通过构造Binding和终结点地址来创建一个WCF服务，在调用服务的过程中，会对调用时间、异常信息等进行记录，这其实和我举的第一个例子完全一致，那么我们能不能用RealProxy来实现这些功能呢？

```CSharp

public class ServiceInfo<TService>
{
    private readonly ChannelFactory _channelFactory;
    public ServiceInfo(ChannelFactory channelFactory)
    {
        _channelFactory = channelFactory;
    }

    public TService Service { get; set; }

    public void Close()
    {
        if (_channelFactory != null)
            _channelFactory.Close();
    }
    
}

private ServiceInfo<TService> FindService()
{
    ChannelFactory<TService> channelFactory = new ChannelFactory<TService>(_binding, _endpointAddress);
    var serviceInfo = new ServiceInfo<TService>(channelFactory);
    serviceInfo.Service = channelFactory.CreateChannel();
    return serviceInfo;
}

```

顺着这样的思路，如果我们可以把ChannelFactory注入到RealProxy中，就可以在接口调用过程中记录相关信息，这样我们就可以关注调用本身，因为所有的我们不想写的代码，现在全部都由代理类接管了，更重要的是，所有通过这种方式调用的WCF服务，都可以以一种统一而简洁的方式去处理，永远不用担心因为某个人忘记写代理方法而出现问题，下面给出整个实现的关键代码：

```CSharp
public class DynamicServiceProxy<TService> : RealProxy
{
    private readonly Binding _binding;
    private readonly EndpointAddress _endpointAddress;

    public DynamicServiceProxy(Binding binding, EndpointAddress endpointAddress)
        : base(typeof(TService))
    {
        _binding = binding;
        _endpointAddress = endpointAddress;
    }

    public DynamicServiceProxy(Binding binding, string serviceUrl)
        : this(binding, new EndpointAddress(serviceUrl))
    {

    }

    public override IMessage Invoke(IMessage message)
    {
        var serviceInfo = FindService();
        var methodCall = message as IMethodCallMessage;
        var methodInfo = methodCall.MethodBase as MethodInfo;
        var startTime = DateTime.Now;
        var serviceName = serviceInfo.Service.GetType().Name;
        var methodName = methodInfo.Name;

        try
        {
            Console.WriteLine("RealProxy调用{0}服务{1}方法开始...", serviceName, methodName);
            var argsInfo = new Dictionary<string, object>();
            for (int i = 0; i < methodCall.ArgCount; i++)
            {
                argsInfo.Add(methodCall.GetArgName(i), methodCall.Args[i]);
            }
            Console.WriteLine("RealProxy当前传入参数:{0}", JsonConvert.SerializeObject(argsInfo));
            var result = methodInfo.Invoke(serviceInfo.Service, methodCall.InArgs);
            if (result != null)
                Console.WriteLine("RealProxy当前返回值:{0}", JsonConvert.SerializeObject(result));
            return new ReturnMessage(result, null, 0, methodCall.LogicalCallContext, methodCall);
        }
        catch (Exception ex)
        {
            Console.WriteLine("RealProxy调用{0}服务{1}方法失败,失败原因：{2}", serviceName, methodName, ex.Message);
            throw ex;
        }
        finally
        {
            serviceInfo.Close();
            Console.WriteLine("调用{0}服务{1}方法结束,共耗时{2}秒", serviceName, methodName, DateTime.Now.Subtract(startTime).TotalSeconds);
            Console.WriteLine("----------------------------------");
        }
    }
}

```

对于WCF服务端的实现，我们依然使用ICalculator这个接口，需要注意的是为其添加[ServiceContract]和[OperationContract]标签，在这个例子中，我们共有CalculatorService和MessageService两个服务，为了简化这个实例，我们采用BasicHttpBinding的方式进行绑定，并为其指定各自的终结点地址。可以注意到，现在我们的动态代理实现了和原来代理类一样的效果。

```CSharp
var binding = new BasicHttpBinding();
var serviceUrl = "http://localhost:8502/Calculator.svc";
var calculator = ServiceProxyFactory.CreatePorxy<Server.Service.ICalculator>(binding, serviceUrl);
```

![通过RealPrxoy动态代理WCF服务](https://ww1.sinaimg.cn/large/4c36074fly1g2w85svbrfj20rp0eqq41.jpg)

在调用WCF的时候，因为超时、网络等原因造成的调用异常，此时，我们可以为WCF添加异常处理相关的标签，而相应地，我们可以在异常中对异常的种类进行判断和处理，以便于及时地关闭ChannelFactory，因为如果它不能正确地关闭，会导致后续的通信出现问题，而这恰好是当初的代理类想要解决的问题，考虑到创建ChannelFactory是需要付出一定的性能代价的，因此，可以适当地考虑对ChannelFactory进行缓存，而这恰好是原来业务中的一个盲点。

# Castle.DynamicProxy

通过RealProxy，我们已经实现了WCF服务的动态代理，这里介绍第二种方式，即Castle.DynamicProxy，Castle和AspectCore、Unity等项目一样，提供了AOP相关的能力，可以让我们对接口、虚方法、类等进行拦截。Castle中的动态代理使用的是透明代理，而.NET Remoting的动态代理必须继承自MarshalByRefObject。博主暂时没有搞清楚，这两种是否属于同一种技术上的实现，作为延伸，我们来一起看看如何使用Castle中的DynamicProxy实现类似的功能，首先我们定义一个拦截器，它需要实现IInterceptor接口中的Intercept()方法：

```CSharp
public void Intercept(IInvocation invocation)
{
    var serviceInfo = FindService();
    var methodInfo = invocation.Method;
    var startTime = DateTime.Now;
    var serviceName = serviceInfo.Service.GetType().Name;
    var methodName = methodInfo.Name;

    try
    {
        Console.WriteLine("CastleProxy调用{0}服务{1}方法开始...", serviceName, methodName);
        var argsInfo = new Dictionary<string, object>();
        var parameters = methodInfo.GetParameters();
        for (int i = 0; i < invocation.Arguments.Length; i++)
        {
            argsInfo.Add(parameters[i].Name, invocation.Arguments[i]);
        }
        Console.WriteLine("当前传入参数:{0}", JsonConvert.SerializeObject(argsInfo));
        var result = methodInfo.Invoke(serviceInfo.Service, invocation.Arguments);
        if (result != null) { 
        Console.WriteLine("当前返回值:{0}", JsonConvert.SerializeObject(result));
            invocation.ReturnValue = result;
        }
    }
    catch (Exception ex)
    {
        Console.WriteLine("CastleProxy调用{0}服务{1}方法失败,失败原因：{2}", serviceName, methodName, ex.Message);
        throw ex;
    }
    finally
    {
        serviceInfo.Close();
        Console.WriteLine("CastleProxy调用{0}服务{1}方法结束,共耗时{2}秒", serviceName, methodName, DateTime.Now.Subtract(startTime).TotalSeconds);
        Console.WriteLine("----------------------------------");
    }
}
```

接下来，我们通过ProxyGenerator来生成新的代理类，我们需要告诉ProxyGenerator要创建的类型是什么，是一个接口还是类，以及要应用哪一个拦截器。这里我们用到的方法是CreateInterfaceWithoutTarget()，它在这里的作用就是动态创建ICalculator接口的代理类。而通过查看Castle的API，我们会发现它可以在以下几种情况下创建某个类型的实例。首先是CreateInterfaceWithoutTarget()这个方法，当你希望创建一个接口的代理而又不想提供具体的实现时可以使用。其次是CreateInterfaceProxyWithTarget()这个方法，当你希望创建一个接口的代理同时又有提供具体实现时使用可以使用。接下来，是CreateInterfaceProxyWithTargetInterface()这个方法，它的命名看起来让人感到迷惑，甚至在某种角度来看，它和CreateInterfaceProxyWithTarget()这个方法还有点相似，其实。这两者最大的不同就是：后者允许你将调用目标替换为目标接口的不同实现。这种在实际场景中使用得不多，从Castle官方的使用场景来看，唯一用到这种技术的是Castle.Facilities，它可以和Windsor 这样的容器整合在一起使用，这个时候调用者就可以把WCF服务当作一个普通接口来使用，果然，大家都想到这一点，英雄所见略同啊，哈哈。好了，下面我们来看具体的代码实现：

```CSharp
ProxyGenerator generator = new ProxyGenerator();
var interceptor = new CastleServicePorxy<ICalculator>(binding, serviceUrl);
var calculator = (ICalculator)generator.CreateInterfaceProxyWithoutTarget(typeof(ICalculator),interceptor);
```




# 迁移至.NET Core

其实，我对WCF是不太感冒的，因为第一个字母W表明，它是一个只能运行在Windows平台的产物，现在依然有大量的Web Service存在，如果可以让我像使用普通接口一样使用WCF接口，我还是非常愿意去使用它的，毕竟系统中有大量依赖WCF的东西。可话又说回来，现在到.NET Core这个版本，微软并没有把WCF的服务端移植到.NET Core上，仅仅是提供了客户端调用的支持，或许还是因为WCF里有太多平台相关的东西吧！如果希望自己的.NET应用可以跨平台，越早摆脱这些Windows平台东西越好，譬如IIS、SQLServer等等。不过我这里想说的是，RealProxy在.NET Core中有类似的实现，我们可以用下面这种方式来进行迁移，当然，如果你直接Castle就更没有问题啦！

```CSharp
public class InvokeSerice
{
    public static T Proxy<T>()
    {
        return DispatchProxy.Create<T, InvokeProxy<T>>();
    }
}

public class InvokeProxy<T> : DispatchProxy
{
    private Type type = null;
    public InvokeProxy()
    {
        type = typeof(T);
    }

    protected override object Invoke(MethodInfo targetMethod, object[] args)
    {
        //TODO: 在这里实现拦截逻辑
    }
}
```

# 本文小结

这篇博客再次让大家领略了AOP的魅力，通过动态代理来创建相关的服务接口，让我们逐渐摆脱了手写代理类的深渊。本文主要分享了两种动态代理的实现方式，一种是基于.NET Remoting的RealProxy，一种是基于Castle的DynamicProxy。两种方式在使用上是非常相近的，通过这种方式。我们实现了WCF服务创建细节的隐藏，调用者不再需要去关心ChannelFactory相关的底层细节，可以像使用普通接口一样调用WCF服务，并且可以用一种统一的方式去记录调用相关的细节、对异常进行处理等等。早期的T4模板本质上是一种静态代理的方式，其缺点是难以适应快速迭代的变化，必须人手编写代理方法，而通过动态代理，这一切只需要写一次就好了，从而做到了真正意义上的“一次编写，到处运行”，这就是所谓的面向横切面编程的思路。关于Castle动态代理更多的应用场景，以及Castle.Facilities相关的内容，大家可以从各自的文档中去了解，以上就是这篇博客的全部内容了。