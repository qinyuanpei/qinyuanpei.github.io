---
toc: true
title: .NET Core中对象池(Object Pool)的使用
categories:
  - 编程语言
tags:
  - 对象池
  - 设计模式
  - .NET Core
copyright: true
abbrlink: 2414960312
date: 2020-08-22 16:37:23
---
在此前的博客中，博主参考 [eShopOnContainers](https://github.com/dotnet-architecture/eShopOnContainers) 实现了一个基于RabbitMQ的事件总线(EventBus)。在这个项目中，它提供了一个持久化连接的类`DefaultRabbitMQPersistentConnection`，主要解决了RabbitMQ在连接断开后自动重连的问题，可实际上我们都知道，RabbitMQ提供的连接数是有一个上限的，如果频繁地使用短连接的方式，即通过`ConnectionFactory`的`CreateConnection()`方法来创建一个连接，从本质上讲，一个`Connection`对象就是一个TCP连接，而`Channel`则是每个`Connection`对象下有限的虚拟连接，注意“有限”这个限定词，这意味着`Channel`和`Connection`一样，都不能毫无节制的创建下去。此时，官方推荐的做法有两种：(1)：一个`Connection`对应多个`Channel`同时保证每个`Channel`线程独占；(2)：创建一个`Connection`池同时定期清除无效连接。这里的第二种做法，显然就是我们今天要说的对象池(Object Pool)啦，我们将从这里拉开这篇博客的帷幕。

# 什么是对象池
首先，我们来回答第一个问题，什么是对象池？简单来说，它就是一种为对象提供可复用性能力的软件设计思路。俗话说**“有借有还，再借不难”**，而对象池就是通过“借”和“还”这样两个动作来保证对象可以被重复使用，进而节省频繁创建对象的性能开销。对象池在游戏设计中使用的更普遍一点，因为游戏中大量存在着像子弹、怪物等等这类可复用的对象，你在玩第一人称射击游戏(FPS)时，总是有源源不断的子弹或者丧尸出现，可事实上这不过是数字世界的循环再生，因为玩家的电脑内存始终都有一个上限。而在数据库的世界里，则存在着一个被称为“连接池”的东西，每当出现数据库无法连接的情况时，经验丰富的开发人员往往会先检查“连接池”是否满了，这其实就是对象池模式在特定领域的具体实现啦，所以，对象池本质上就是负责一组对象创建和销毁的容器，下面是一个基本的对象池示意图：

![对象池示意图](https://i.loli.net/2020/08/22/lReo7LQa1SODZpc.png)

可以注意到， 对象池最大的优势就是可以自主地管理“池子”内的每个对象，决定它们是需要被回收还是可以重复使用。我们都知道，创建一个新的对象，需要消耗一定的系统资源，而一旦这些对象可以重复地使用，就能有效地节省系统资源的开销，这对于我们提高系统性能会非常有帮助。也许，现在计算机的硬件水平越来越好，可我们还是要重新拾起这个领域的基础知识，即数据结构、算法、数学和英语。如果你完全理解了对象池模式，你应该可以非常轻松地给出你的实现：

```CSharp
public class ObjectPool<T> : IObjectPool<T>
{
  private Func<T> _instanceFactory;
  private ConcurrentBag<T> _instanceItems;

  public ObjectPool(Func<T> instanceFactory)
  {
    _instanceFactory = instanceFactory ?? 
      throw new ArgumentNullException(nameof(instanceFactory));
    _instanceItems = new ConcurrentBag<T>();
  }

  public T Get()
  {
    T item;
    if (_instanceItems.TryTake(out item)) return item;
    return _instanceFactory();
  }

  public void Return(T item)
  {
    _instanceItems.Add(item);
  }
}
```
注：以上代码片段来自微软的一篇文档：[How to: Create an Object Pool by Using a ConcurrentBag](https://docs.microsoft.com/en-us/dotnet/standard/collections/thread-safe/how-to-create-an-object-pool)。实际上，除了`ConcurrentBag<T>`，我们可以选择的数据结构还可以是`Stack<T>`、`Queue<T>`以及`BlockingCollection<T>`，此中差别，大家可以自己去体会。

# .NET Core中的对象池
在.NET Core中，微软已经为我们提供了对象池的实现，即`Microsoft.Extensions.ObjectPool`。它主要提供了三个核心的组件，分别是`ObjectPool`、`ObjectPoolProvider`和`IPooledObjectPolicy`，关于这三者间的关系，我绘制了下面的UML图来作为说明：

![ObjectPool核心组件及其关系](https://i.loli.net/2020/08/22/M6ojLtqgKc5pfCA.png)

可以注意到，`ObjectPool<T>`是一个抽象类，它对外提供了Get()和Return()两个方法，所谓的“有借有还”，这一点没什么可说的。接下来，`ObjectPoolProvider`同样是一个抽象类，它的职责就是创建`ObjectPool<T>`，所以，它提供了两个`Create<T>()`方法，两者的区别是，无参数版本本质上使用的是`DefaultPooledObjectPolicy<T>`。顾名思义，它同`DefaultObjectPool<T>`、`DefaultObjectPoolProvider`一样，都是微软提供的默认实现，其中`IPooledObjectPolicy<T>`可以为不同的对象池定义不同的策略，来决定对象如何“借”、是否可以“还”。默认的对象池`DefaultObjectPool<T>`内部使用`ObjectWrapper[]`这个数组来管理对象，数组的大小等于maximumRetained - 1，因为它单独指定了首项，默认情况下，这个maximumRetained等于`Environment.ProcessorCount * 2`，这里主要用到了`Interlocked.CompareExchange()`方法：
```CSharp
public override T Get()
{
  var item = _firstItem;
  if (item == null || Interlocked.CompareExchange(ref _firstItem, null, item) != item)
  {
    var items = _items;
    for (var i = 0; i < items.Length; i++)
    {
      item = items[i].Element;
      if (item != null && Interlocked.CompareExchange(ref items[i].Element, null, item) == item)
      {
        return item;
      }
    }

    item = Create();
  }

  return item;
}

// Non-inline to improve its code quality as uncommon path
[MethodImpl(MethodImplOptions.NoInlining)]
private T Create() => _fastPolicy?.Create() ?? _policy.Create();

public override void Return(T obj)
{
  if (_isDefaultPolicy || (_fastPolicy?.Return(obj) ?? _policy.Return(obj)))
  {
    if (_firstItem != null || Interlocked.CompareExchange(ref _firstItem, obj, null) != null)
    {
      var items = _items;
      for (var i = 0; i < items.Length && Interlocked.CompareExchange(ref items[i].Element, obj, null) != null; ++i)
      {

      }
    }
  }
}
```
这里主要用到`Interlocked.CompareExchange()`这个方法，对于`Get()`方法而言，它将`items[i].Element`和`null`进行交换，相当于将指定元素设为null并返回原始值；而对于`Return()`方法而言，如果将`items[i].Element`和`obj`交换后的值不为null，则表示指定元素已经“归还”，因为这个方法只有在第一个参数和第三个参数相等时才会发生交换。好了，了解了.NET Core中对象池的实现以后，我们来一起看看具体的使用：
```CSharp
var service = new ServiceCollection();

//使用DefaultObjectPoolProvider
service.AddSingleton<ObjectPoolProvider, DefaultObjectPoolProvider>();
//使用默认策略
service.AddSingleton<ObjectPool<Foo>>(serviceProvider =>
{
  var objectPoolProvider = serviceProvider.GetRequiredService<ObjectPoolProvider>();
  return objectPoolProvider.Create<Foo>();
});
//使用自定义策略
service.AddSingleton<ObjectPool<Foo>>(serviceProvider =>
{
  var objectPoolProvider = serviceProvider.GetRequiredService<ObjectPoolProvider>();
  return objectPoolProvider.Create(new FooObjectPoolPolicy());
});

var serviceProvider = _service.BuildServiceProvider();

var objectPool = _serviceProvider.GetService<ObjectPool<Foo>>();

//有借有还，两次是同一个对象
var item1 = objectPool.Get();
objectPool.Return(item1);
var item2 = objectPool.Get();
Assert.AreEqual(item1, item2);//true

//有借无还，两次是不同的对象
var item3 = objectPool.Get();
var item4 = objectPool.Get();
Assert.AreEqual(item3, item4);//false
```
其中，`Foo`和`FooObjectPoolPolicy`是两个非常典型的“工具类”，类似我们所说的“工具人”：
```CSharp
public class Foo
{
  public string Id { get; set; }
  public DateTime? CreatedAt { get; set; }
  public string CreatedBy { get; set; }
}

public class FooObjectPoolPolicy : IPooledObjectPolicy<Foo>
{
  public Foo Create()
  {
    return new Foo()
    {
      Id = Guid.NewGuid().ToString("N"),
      CreatedAt = DateTime.Now,
      CreatedBy = "Ezio"
    };
  }

  public bool Return(Foo obj)
  {
    return true;
  }
}
```
当你需要控制对象池内的对象如何被创建的时候，你可以考虑实现自定义的`IPooledObjectPolicy<T>`，否则，`DefaultPooledObjectPolicy<T>`这个默认实现完全可以满足你的使用，而这就是.NET Core中对象池的所有用法，一个实现起来并不复杂但是在某些场景下非常有用的软件设计模式。

# 回到起点
好了，回到我们一开始的问题，即：如何解决RabbitMQ在多次重连后提示连接数不足的问题。由于Channel对象本质上是Connection对象上的TCP连接的软连接，所以，每当创建一个新的Channel的时候，实际上会独占一个TCP连接。考虑到在使用RabbitMQ的时候，发布消息/消费消息每次都是创建一个Channel，在高并发场景下可能会导致TCP连接数被用完，进而出现无法连接或者响应过慢等一系列问题。既然TCP连接数是有限的，为什么不考虑复用这些TCP连接呢？从这个角度上来看，数据库连接池承担了相同的角色，增加连接数说到底是一种“治标不治本”的做法。在具体实现上，可以考虑Connection“池”和Channel“池”，我们我们像官方推荐的做法一样，一个Connection对应多个Channel，实际上只需要实现Channel“池”。除非在多个Connection对应多个Channel的情况下，我们需要考虑同时实现Connection“池”和Channel“池”。坦白说，我这里一直没能找到实现Connection“池”的相关资料，高冷的 [Catcher](https://www.cnblogs.com/catcher1994/) 大神只是让我去认真读官方文档，搞清楚Connection和Channel的关系。而这个Channel“池”的实现，结合这篇博客里的内容，实现起来是非常简单的：
```CSharp
public class ChannelObjectPoolPolicy : IPooledObjectPolicy<IModel>
{
  private readonly IConnectionFactory _connectionFactory;
  public ChannelObjectPoolPolicy(IConnectionFactory connectionFactory)
  {
    _connectionFactory = connectionFactory;
  }

  public IModel Create()
  {
    var connection = _connectionFactory.CreateConnection();
    return connection.CreateModel();
  }

  public bool Return(IModel obj)
  {
    if (!obj.IsOpen)
    {
      obj?.Dispose();
      return false;
    }

    return true;
  }
}
```
第一步是实现`IPooledObjectPolicy<IModel>`，注意到，这里通过构造函数注入了`ConnectionFactory`，所以，除了常规的注入项以外，这里还需要注入`ConnectionFactory`:
```CSharp
services.AddSingleton<IConnectionFactory, ConnectionFactory>(sp => new ConnectionFactory() { 
    HostName = "localhost", 
    UserName = "guest", 
    Password = "guest" 
});
services.AddSingleton<ObjectPoolProvider, DefaultObjectPoolProvider>();
services.AddSingleton<ObjectPool<IModel>>(serviceProvider =>
{
  var objectPoolProvider = serviceProvider.GetRequiredService<ObjectPoolProvider>();
  var connectionFactory = serviceProvider.GetRequiredService<ConnectionFactory>();
  return objectPoolProvider.Create(new ChannelObjectPoolPolicy(connectionFactory));
});
```
然后，我们只需要在EventBus里注入`ObjectPool<IModel>`即可，此时，我们调用Channel的画风是下面这样子的：
```CSharp
var channel = _channelPool.Get();
try {  //在这里做点什么吧  }
finaly
{
  //好借好还，再借不难
  _channelPool.Return(channel);
}
```
关于Connection“池”的实现，我认为我的想法还不太成熟，暂时列入未来的思考计划中，所以，这篇博客就先写到这里。

# 本文小结
对象池(ObjectPool)是一种通过复用对象来减少资源开销进而实现提高系统性能的软件设计模式，其核心是控制容器内对象的生命周期来规避系统的主动回收，从对象池中(ObjectPool)“借”出的对象必须要及时“归还”，否则会造成对象池(ObjectPool)中没有可用资源。实现对象池可以考虑`ConcurrentBag<T>`、`Stack<T>`、`Queue<T>`以及`BlockingCollection<T>`等多种数据结构，而微软在.NET Core中已经为我们实现了一个简单的对象池，大多数情况下，我们只需要定义自己的`IPooledObjectPolicy<T>`去决定对象应该怎么样“借”、怎么样“还”。因为此前实现基于RabbitMQ的EventBus的时候，我们是每次创建一个Channel，即官方所谓的“短连接”的方式，因为Channel本质上是Connection在TCP连接上的一个虚拟连接，所以，每次创建Channel都会占用一个TCP连接，当我们系统中的TCP连接被用完的时候，就会出现无法连接、连接过慢的问题，为了解决这个问题，我们最终引入了对象池，实际上这里是实现了一个Channel“池”，关于是否应该实现Connection“池”，这一点我还没有想好，总而言之，游戏世界里可以复用的GameObject、各种数据库里的连接池，都是对象池模式在各自领域中的具体实现，这就是这篇博客的内容啦，欢迎大家在评论中留言，谢谢大家！
