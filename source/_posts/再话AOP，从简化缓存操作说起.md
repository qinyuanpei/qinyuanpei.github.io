---
toc: true
title: 再话AOP，从简化缓存操作说起
categories:
  - 编程语言
tags:
  - 缓存
  - AOP
  - 动态代理
  - Redis
copyright: true
abbrlink: 2126762870
date: 2021-08-04 20:49:47
---
AOP，即：**面向切面编程**，关于这个概念，博主其实写过好几篇[博客](https://blog.yuanpei.me/tags/AOP/)啦！从这个概念，我们可以引申出诸如代理模式、动态代理、装饰器模式、过滤器、拦截器等等相互关联的概念。从实现方式上而言，微软官方的 [.NET Remoting](https://docs.microsoft.com/zh-cn/previous-versions/dotnet/articles/ms973857(v=msdn.10)?redirectedfrom=MSDN) 提供了真实代理和透明代理的支持，我们熟悉的 `WebService` 和 `WCF` 均和这项技术息息相关，作为最早的分布式 RPC 解决方案，其本身更是与客户端的动态代理密不可分。或许，各位曾经接触过 `Unity`、`Castle`、`AspectCore`、[PostSharp](https://www.postsharp.net) 等等这些支持 AOP 特性的库，那么，我们是否已经抵达了 AOP 的边界呢？事实上，如果你仔细研究过 `Stub` 和 `Mock` 这样两个术语，你就发现 AOP 的应用范围远比我们想象的宽广。今天这篇文章，我不打算再介绍一遍这些第三方库的“**奇技淫巧**”，我更想聊聊，如何通过 AOP 来简化一个缓存操作。

缓存，一个面试时命中率100%的话题，曾记否？来自面试官的灵魂发问三连：**缓存击穿**、**缓存穿透**、**缓存雪崩**。与此同时，缓存是一个令人爱恨交加的东西，其一致性、持久化、高可用等等，均是实际应用中需要去考虑的东西。狭义的缓存主要指 [Redis](https://redis.io/)、[Memcached](https://www.memcached.org) 等分布式缓存系统，而广义的缓存则可以是 [HTTP 响应缓存](https://docs.microsoft.com/zh-cn/aspnet/core/performance/caching/response?view=aspnetcore-5.0)、EF/EF Core 查询缓存、二级缓存等等。我们都知道，使用缓存可以显著地提升软件性能，而究其本质，则是因为减少了和数据库交互的频次。于是，我们注意到，大多数的缓存代码，都是下面这样的风格：

```csharp
var cacheKey = "GetAllStudents";
var students = new List<Student>();
var cacheValue = distributedCache.GetString(cacheKey);
if (string.IsNullOrEmpty(cacheValue))
{
    // 未命中缓存：从数据库查询数据 + 写缓存
    students = repository.GetAll().ToList();
    var bytes = Encoding.UTF8.GetBytes(JsonConvert.SerializeObject(students));
    distributedCache.Set(cacheKey, bytes);
} 
else
{
    // 命中缓存：读缓存
    students = JsonConvert.DeserializeObject<List<Student>>(cacheValue);
}

return students;
```

正所谓：大道至简，“**高端的食材，往往只需要最朴素的烹饪方式**”。故而，最朴素的思想就是，首先从缓存中查询数据，如果数据存在则直接返回，否则从数据库中查询数据，并执行一次写缓存操作。这的确是个朴实无华的方案，因为我们每一次都要写这样的代码，其程度丝毫不亚于永远不会缺席的 `xxx != null`。写到这里，博主不由得陷入了沉思：难道真的没有更简单点的方案了吗？后来的故事大家都知道了，我们可以在方法的参数上附加 `[NotNull]` 特性。所以，接下来，我们会用类似的方案来解决缓存的问题，换言之，我们可以把我们经常写、写到不愿意再写的代码交给代理类来做，既然缓存本质上是为了查询数据，那我们就只需要关心查询数据这个行为本身。具体怎么实现的呢？我们一起来看下面的代码。

此时此刻，假设我们有这样一个接口：`IFakeService`，它通过`GetColors()`方法返回一组颜色：

```csharp
interface IFakeService
{
    [Cacheable(CacheKeyPrefix = "Fake", Expiration = 180)]
    List<string> GetColors();
}
```

我们希望，在调用这个方法的时候，可以对其返回值进行缓存，所以，可以注意到，这里添加了一个`[Cacheable]`的特性。其定义如下：

```csharp
[AttributeUsage(AttributeTargets.Method)]
public class CacheableAttribute : Attribute
{
    public string CacheKeyPrefix { get; set; }
    public int Expiration { get; set; }
}
```

其中，`CacheKeyPrefix`用于指定缓存键名前缀，`Expiration`用于指定缓存过期时间，单位为秒。接下来，博主通过`DispatchProxy`来实现动态代理，它可以视为`RealProxy`在后.NET时代的替代品：

```csharp
public class CacheInterceptor<TCacheService> : DispatchProxy
{
    private TCacheService _realObject => ServiceProvider.GetRequiredService<TCacheService>();
    private ICacheSerializer _cacheSerializer => ServiceProvider.GetRequiredService<ICacheSerializer>();
    private IDistributedCache _distributedCache => ServiceProvider.GetRequiredService<IDistributedCache>();

    public IServiceProvider ServiceProvider { get; set; }

    protected override object Invoke(MethodInfo targetMethod, object[] args)
    {
        byte[] cacheValue;
        var returnType = targetMethod.ReturnType;

        // void && Task
        if (returnType == typeof(void) || returnType == typeof(Task))
            return targetMethod.Invoke(_realObject, args);

        if (IsAsyncReturnValue(targetMethod))
            returnType = targetMethod.ReturnType.GetGenericArguments()[0];

        var cacheableAttribute = targetMethod.GetCustomAttribute<CacheableAttribute>();
        if (cacheableAttribute != null)
        {
            var cacheKey = GetCacheKey(cacheableAttribute, targetMethod);
            cacheValue = _distributedCache.Get(cacheKey);
            if (cacheValue != null)
            {
                // Task<T>
                if (IsAsyncReturnValue(targetMethod))
                    return Task.FromResult(_cacheSerializer.Deserialize(cacheValue, returnType));

                return _cacheSerializer.Deserialize(cacheValue, returnType);
            }

            dynamic returnValue = targetMethod.Invoke(_realObject, args);
            cacheValue = _cacheSerializer.Serialize(returnValue);

            // Task<T>
            if (IsAsyncReturnValue(targetMethod))
                cacheValue = _cacheSerializer.Serialize(returnValue.Result);

            var cacheOptions = new DistributedCacheEntryOptions() { 
              AbsoluteExpirationRelativeToNow = TimeSpan.FromSeconds(cacheableAttribute.Expiration) 
            };
            _distributedCache.Set(cacheKey, cacheValue, cacheOptions);
            return returnValue;
        }

        return targetMethod.Invoke(_realObject, args);
    }
}
```

这里，最为关键的地方是`Invoke()`方法，它负责对被代理对象的方法进行拦截，这里的被代理对象，其实就是`_realObject`，即真实对象，因为，我们最终调用的，实际上是真实对象上对应的方法。因为`DispatchProxy`在创建代理对象时，要求这个代理基类，即这里的拦截器，必须要有一个无参的构造函数。所以，我们这里用属性注入的方式赖注入`IServiceProvider`。说回这个方法，首先，我们会判断它的返回值类型是不是`void`或者`Task`，因为无返回值的方法本身就不需要缓存。接下来，我们会检查当前方法上是否附加了`[Cacheable]`特性，因为我们只需要处理有这个特性的方法。接下来，通过`GetCacheKey()`方法来生成一个唯一的键名，通过这个键名我们就可以在缓存中查询数据啦，该方法的实现细节如下：

```csharp
private string GetCacheKey(CacheableAttribute cacheableAttribute, MethodInfo methodInfo)
{
    var segments = new List<string>();

    if (!string.IsNullOrEmpty(cacheableAttribute.CacheKeyPrefix))
        segments.Add(cacheableAttribute.CacheKeyPrefix);

    segments.Add(methodInfo.DeclaringType.FullName.Replace(".", "_"));

    segments.Add(methodInfo.Name);

    methodInfo.GetParameters().ToList().ForEach(x => segments.Add(x.Name));

    return string.Join("_", segments);
}
```

对于分布式缓存，博主这里使用的是微软提供的`IDistributedCache`这个接口，接下来的事情就变得朴实无华起来，因为它和我们一开始写的代码一脉相承，唯一的不同是，这里考虑了`Task<T>`这种异步的返回值类型，同时对序列化/反序列化进行了抽象，即这里注入的`ICacheSerializer`接口，注意到`IDistributedCache`接口的`Set()`方法需要传入一个`byte[]`，显然二进制的序列化方案如 [Protobuf](https://developers.google.cn/protocol-buffers?hl=zh-cn) 、[MessagePack](https://msgpack.org/) 会更加得心应手一点。所以，我们将这一层单独抽象出来。至此，我们已经完成了最核心的部分。

对于一开始的`IFakeService`，我们提供一个简单的实现，并通过让线程阻塞的方式来模拟一个耗时操作：

```csharp
public class FakeService : IFakeService
{
    public List<string> GetColors()
    {
        Thread.Sleep(500);
        return new List<string> { "Red", "Yellow", "Green" };
    }
}
```

下面是一个简单的示例：

```csharp
// 注入IFakeService、ICacheSerializer、IDistributedCache
var services = new ServiceCollection();
services.AddTransient<IFakeService, FakeService>();
services.AddTransient<ICacheSerializer, JsonCacheSerializer>();
services.AddStackExchangeRedisCache(options =>
{
    options.Configuration = "localhost:6379";
    options.InstanceName = "Caching.AOP.Test";
});

// 生成代理对象
var serviceProvider = services.BuildServiceProvider();
var fakeServiceProxy = DispatchProxy.Create<IFakeService, CacheInterceptor<IFakeService>>();
(fakeServiceProxy as CacheInterceptor<IFakeService>).ServiceProvider = serviceProvider;

// 调用代理对象
for (var i = 0; i < 5; i++)
{
    var stopWatch = new Stopwatch();
    stopWatch.Start();
    var colors = fakeServiceProxy.GetColors();
    stopWatch.Stop();
    Console.WriteLine($" {i} - Invoke GetColors used {stopWatch.Elapsed.TotalMilliseconds} ms");
}
```
此时，我们可以得到下面的结果，可以注意到，第一次调用的时候，因为缓存不存在，调用的时间相对更长一点，而当缓存存在的时候，调用的时间会明显缩短。

![有无缓存对调用时长的影响](https://i.loli.net/2021/08/04/FdafGyS7zrl53W1.png)

虽然这个性能提升与缓存不无关系，可对于调用者来说，它完全不用关心缓存里有没有数据这件事情，它只需要像往常一样调用接口方法即可，这就是 AOP 之于缓存的意义所在，为了证明我没有说谎，我们可以看到 Redis 中对应的数据：

![Redis中对应的缓存数据](https://i.loli.net/2021/08/04/wkAQGMRKr8xuol3.png)

需要说明的是，这个思路同样可以扩展到`Unity`、`Castle`、`AspectCore`、[PostSharp](https://www.postsharp.net) 这些第三方库，实现方式上大同小异，大家可以结合自己的业务场景做相应的调整。其实，从业务上抽离出通用组件、功能作为公共库或者下沉到框架中，是及其自然而然的一件事情。这里面最关键的问题是，基础组件或者框架相对于业务方的职责范围，因为如果基础组件或者框架做得太多，业务上往往难以定制或者扩展；而如果基础组件或者框架做得太少，业务上就要写大量的辅助代码。写这篇文章的原因是，我对于一个缓存方案设计上的疑问，业务上想要缓存一张表中的数据，至少需要写 20 行代码，在下觉得这简直太离谱了，更不用说，业务方还要关心这个缓存是否可用。有人说，一个合格的前任就应该像死了一样，那么，我是不是可以说，一个合格的中间件，就应该像它从来没有来过一样，你甚至都感觉不到它的存在，可事实上它总是无所不在。也许，这听起来有点科幻的色彩，可这的确是我期待的某种自洽的、优雅的设计思路。

# 本文小结

本文分享了通过 AOP 来简化缓存操作的一种思路，考虑到常规的缓存代码写法，读/写缓存与业务代码严重耦合在一起，而博主心目中的缓存应该像水、电、煤气一样普普通通，你只需要告诉我哪些数据需要缓存，而无需关心这些数据怎么缓存。基于这样一种考虑，博主基于`DispatchProxy`实现了一个针对缓存的 AOP 方案，我们只需要在接口上打上`[Cachable]`标签，它会自动对方法的返回值进行缓存，从而简化我们平时使用缓存的流程。[Catcher Wong](https://www.cnblogs.com/catcher1994) 在其缓存框架 [EasyCaching](https://www.cnblogs.com/catcher1994/p/10806607.html) 同样集成了这一特性，如果大家有类似的使用场景，可以直接使用这个[框架](https://github.com/dotnetcore/EasyCaching)。如果大家对此有更好的想法或者思路，欢迎大家在评论区留言，本文示例已上传至 [Github](https://hub.fastgit.org/Regularly-Archive/2021/tree/master/src/Caching.AOP)，供大家学习或者参考。好了，以上就是这篇博客的全部内容啦，谢谢大家！









