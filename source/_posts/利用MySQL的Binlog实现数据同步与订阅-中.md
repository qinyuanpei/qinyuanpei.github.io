---
toc: true
title: 利用MySQL的Binlog实现数据同步与订阅(中)：RabbitMQ篇
categories:
  - 数据存储
tags:
  - RabbitMQ
  - EventBus
  - 事件订阅
copyright: true
abbrlink: 580694660
date: 2020-07-15 14:39:07
---
紧接上一篇博客中的思路，这次我们来说说事件总线(EventBus)，回首向来，关于这个话题，我们可能会联想到发布-订阅模式、观察者模式、IObservable<T>与IObserver<T>、消息队列等等一系列的概念。所以，当我们尝试着去解释这个概念的时候，它到底是什么呢？是一种设计模式？是一组API接口？还是一种新的技术？显而易见，发布-订阅模式和观察者模式都是设计模式，而IObservable<T>与IObserver<T>、消息队列则是具体的实现方式，就像你可以用委托或者事件去实现一个观察者模式，而Redis里同样内置了发布-订阅模型，换言之，这是抽象与具体的区别，消息队列可以用来实现EventBus，而EventBus主要的用途则是系统间的解耦，说到解耦，你可能会对观察者模式和发布-订阅模式这两种模式感到困惑，因为它们实在是太像了，一个最本质的区别在于发布者(主题)是否与订阅者(观察者)存在强依赖关系，而发布-订阅引入了类似主题/Topic/Channel的中介者，显然从解耦的角度要更彻底一些，所以，我们今天就来一起实现一个事件总线(EventBus)。

# EventBus整体设计
通过前面的探讨，我们可以知道，EventBus其实是针对事件的`发布-订阅`模式的实现，所以，在设计EventBus的时候，我们可以结合`发布-定阅`模式来作为对照，而一个典型的`发布-订阅`模式至少需要三个角色，即`发布者`、`订阅者`和`消息`，所以，一般在设计EventBus的时候，基本都会从这三个方面入手，提供**发布消息**、**订阅消息**、**退订消息**的接口。由于EventBus本身并不负责消费消息，所以，还需要借助`IEventHandler<T>`来编写对应的事件处理器，这是EventBus可以实现业务解耦的重要原因。而为了维护事件和事件处理器的关系，通常需要借助IoC容器来注册这些EventHandler，提供类似`Castle`或者`Autofac`从程序集中批量注册的机制，下面是博主借鉴 [eShopOnContainers](https://github.com/dotnet-architecture/eShopOnContainers) 设计的EventBus，首先是IEventBus接口，其定义如下：
```CSharp
public interface IEventBus 
{
    void Publish<TEvent> (TEvent @event) where TEvent : EventBase;
    void Subscribe<T, TH> ()
        where T : EventBase
        where TH : IEventHandler<T>;
    void Unsubscribe<T, TH> ()
        where TH : IEventHandler<T>
        where T : EventBase;
}
```
注意到，这里对事件(**EventBase**)和事件处理器(**EventHandler**)均有一定约束，这是为了整个EventBus的实现，在某些EventBus的实现中，可能会支持非泛型的`EventHandler`，以及`Func`这样的委托类型，这里不考虑这种情形，因为从Binlog中获取的数据，基本上都是格式固定的JSON。关于这部分，下面给出对应的定义：
```CSharp
public interface IEventHandlerBase { }
public interface IEventHandler<TEvent> : IEventHandlerBase where TEvent : EventBase 
{
    Task Handle (TEvent @ebent);
}

public class EventBase 
{
    public Guid EventId { get; set; } = Guid.NewGuid ();
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
}
```
而为了维护事件(**EventBase**)和事件处理器(**EventHandler**)间的订阅关系，博主这里定义了`IEventBusSubscriptionManager`接口，相信以你对`发布-订阅`模式的理解，你可以非常容易地想到，这里应该会用到一个字典来存储每一个事件以及该事件对应的事件处理器的类型信息。你猜对了，事实上大多数的`EventBus`都是这样实现的，尤其当你在实现一个基于内存或者进程内通信的`EventBus`的时候, 到这一步其实已经完成了大多数的功能。理论上你还应该定义一个`IEventStore`接口，显而易见，这是针对事件的持久化接口，不过当我们选择`RabbitMQ`的时候，它无形中就自动帮我们实现了这个接口。
```CSharp
public interface IEventBusSubscriptionManager 
{
    EventHandler<EventBusSubscriptionEventArgs> OnSubscribe { get; set; }
    EventHandler<EventBusSubscriptionEventArgs> OnUnsubscribe { get; set; }
    void Subscribe<T, TH> ()
        where T : EventBase
        where TH : IEventHandler<T>;
    void Unsubscribe<T, TH> ()
        where T : EventBase
        where TH : IEventHandler<T>;
    bool IsEventSubscribed<T> () where T : EventBase;
    bool IsEventSubscribed (string eventName);
    Type GetEventTypeByName (string eventName);
    void Clear ();
    IEnumerable<Type> GetHandlersForEvent<T> () where T : EventBase;
    IEnumerable<Type> GetHandlersForEvent (string eventName);
    string GetEventKey<T> () where T : EventBase;;
}
```
`IEventBusSubscriptionManager`接口主要提供了维护事件(Event)和事件处理器(EventHnadler)两者关系的一系列方法，我个人认为理解起来相对容易一点，实际上看 [eShopOnContainers](https://github.com/dotnet-architecture/eShopOnContainers) 的时候，我每次都是从其中的一个微服务开始研究的，因为这样你才能发现其中的神秘之处，不得不说，平时看那种流水账代码看惯了，看到这样清晰、优雅的代码，内心还是觉得幸福啊，对技术的热爱再度被燃起。

# 基于RabbitMQ的实现
## Publish
好了，下面我们来看如何基于`RabbitMQ`实现上面定义的`IEventBus`接口，首当其冲的是`Publish()`方法的实现：
```CSharp
public void Publish<TEvent> (TEvent @event)
    where TEvent : EventBase 
{
    if (!_persistentConnection.IsConnected) _persistentConnection.TryConnect ();
    using (var channel = _persistentConnection.CreateModel ()) 
    {
        channel.ExchangeDeclare (_exchangeName, "direct", true, false, null);

        var eventName = @event.GetType ().FullName;
        var message = JsonConvert.SerializeObject (@event);
        var body = Encoding.UTF8.GetBytes (message);

        var properties = channel.CreateBasicProperties ();
        properties.DeliveryMode = 2;
        channel.BasicPublish (exchange: _exchangeName, routingKey: eventName, mandatory: true, basicProperties: properties, body: body);
        _logger.LogDebug ($"Publish message with RabbmitMQ BasicPublish: {message}");
    }
}
```
这里首先介绍下`RabbitMQ`中的两个概念，即`Connection`和`Channel`。其中，`Connection`是操作`RabbitMQ`的基础，就像我们操作数据库的时候，需要首先建立数据库连接一样。那么，`Channel`又是什么东西呢？它是真正去操作`RabbitMQ`的东西。继续以数据库作为例子，那么`Channel`可以理解为`ADO.NET`中的`Command`，即，那个真正负责执行SQL语句的家伙。一个典型的使用`RabbitMQ`的过程，大概是下面这个样子：
```CSharp
var connectionFactory = new ConnectionFactory() { HostName = "Your IP", UserName = "You User", Password = "Your Pass" };
var connection = connectionFactory.CreateConnection();
var channel = connection..CreateModel();
```
回到我们的EventBus中，因为`RabbitMQ`的链接可能会在一段时间后自动关闭，所以，在微软的 [eShopOnContainers](https://github.com/dotnet-architecture/eShopOnContainers) 项目，它设计了一个支持自动重连的链接持久化类，我们这里同样有这个机制，当发现链接断开的时候，自动尝试重连，而接下来就由我们熟悉的`Channel`登场啦！这个时候，我们发现又出现了一个新面孔——交换器(**Exchange**)，好吧，这又要引出RabbitMQ中消息投递的原理，即RabbitMQ中消息并非由发布者直接发送给消费者，而是需要经过交换器这个中介者，虽然你可以直接去读写队列，但是实际应用中通常都不会这么做。其实，在某种意义上，我们的EventBus一样承担着中介者的角色，我们只需要关注怎么发布消息，这个消息将由哪一个订阅者来消费完全不需要我来关心，一个典型的消息投递过程如下图所示：

![RabbitMQ消息投递示意图](https://i.loli.net/2020/07/31/geWGI6M39fcw2S1.png)

在这里，我们对消息进行序列化以后，按照事件的类型信息生成`routingKey`，并指定交换器的类型为` direct`，这是一个RabbitMQ中自带的`发布-订阅`实现，因为交换器会根据` routingKey`投递消息到对应的队列中，关于RabbitMQ中四种交换器的说明，可以在下一节找到答案。注意到在声明交换器的时候，第二个参数被设为true，这是在RabbitMQ需要对这个交换器进行持久化；而第三个参数被设为false，这是在告诉RabbitMQ这个交换器内的消息不允许自动删除；DeliveryMode设为2则表示消息需要持久化到磁盘上，这样即使RabbitMQ发生意外宕机，依然可以从磁盘上恢复消息。最终，我们调用`BasicPublish()`将消息投递到指定的交换机中，这样就完成了事件的发布功能。

## Subscribe/Unsubscribe
接下来，我们来看`Subscribe()`和`Unsubscribe()`两个方法的实现过程。这里实际上需要实现两部分的功能，一个是管理事件(**EventBase**)与事件处理器(**EventHandler**)间的关系，一个是管理消费者、消费者队列与交换器间的关系。因为考虑到后续可能需要实现类似`MediatR`的进程内通信的功能，所以，我们考虑将这两部分剥离开来，这样方便对`EventBus`进行扩展。为此，我们定义了`IEventSubscriptionManager`这个接口，它的定义我们在前面已经见过，最终我们会在`EventBus`里引用这个中间层，这样可以让`EventBus`显得更加清爽一点，一起来看它的具体实现：
```CSharp
public void Subscribe<T, TH> ()
    where T : EventBase
    where TH : IEventHandler<T> 
{
    var eventName = GetEventKey<T> ();
    if (_eventHandlers.ContainsKey (eventName) && !_eventHandlers[eventName].Any (x => x == typeof (TH))) {
        _eventHandlers[eventName].Add (typeof (TH));
    } else {
        _eventHandlers[eventName] = new List<Type> () { typeof (TH) };
        _eventTypes.Add (typeof (T));
    }
    if (OnSubscribe != null)
        OnSubscribe (this, new EventBusSubscriptionEventArgs () { EvenType = typeof (T), HandlerType = typeof (TH) });
}
public void Unsubscribe<T, TH> ()
    where T : EventBase
    where TH : IEventHandler<T>
{
        var eventName = GetEventKey<T> ();
        if (_eventHandlers.ContainsKey (eventName) && _eventHandlers[eventName].Any (x => x == typeof (TH))) {
            _eventHandlers[eventName].Remove (typeof (TH));
        }
        if (_eventHandlers.ContainsKey (eventName) && !_eventHandlers[eventName].Any ()) {
            _eventHandlers.Remove (eventName);
            _eventTypes.RemoveAll (x => x.FullName == eventName);
        }
        if (OnUnsubscribe != null && !GetHandlersForEvent<T> ().Any ())
            OnSubscribe (this, new EventBusSubscriptionEventArgs () { EvenType = typeof (T), HandlerType = typeof (TH) });
}
```
可以注意到，**订阅就是注册EventHandler到对应的键的过程，而取消订阅就是从对应的键里移除EventHandler的过程**。为了确保在订阅或者退订的时候，可以通知到具体的EventBus实现者，譬如RabbitMQ、Kafka等，我们定义了`OnSubscribe`和`OnUnsubscribe`两个委托，实际设计中，我们会在EventBus初始化的时候，将这两个委托指向EventBus内部订阅和退订的方法。对于订阅，我们需要用到RabbitMQ的`BasicConsume()`方法；而对于取消订阅，我们需要用到RabbitMQ的`UnbindQueue()`方法。下面给出关键部分的代码实现：
```CSharp
//RabbitMQ中订阅指定的routingKey
private void StartBasicConsume (string routingKey)
{
    _logger.LogTrace ("Starting RabbitMQ BasicConsume...");

    if (!_persistentConnection.IsConnected) _persistentConnection.TryConnect ();

    var queueName = GetQueueName (routingKey);

    var channel = _persistentConnection.CreateModel ();
    channel.ExchangeDeclare (_exchangeName, "direct", true, false, null);
    channel.QueueDeclare (queueName, true, false, false, null);
    channel.QueueBind (queueName, _exchangeName, routingKey, null);

    var consumer = new EventingBasicConsumer (channel);
    consumer.Received += async (s, e) => {
        var routingKey = e.RoutingKey;
        var message = Encoding.UTF8.GetString (e.Body.ToArray ());
        var tasks = ProcessEvent (routingKey, message);
        await Task.WhenAll (tasks);
        channel.BasicAck (e.DeliveryTag, false);
    };

    channel.BasicConsume (queue: $"Q:{routingKey}", autoAck : false, consumer : consumer);
}

//调用EventHandler处理事件
private IEnumerable<Task> ProcessEvent (string eventName, string message) 
{
    if (_subscriptionManager.IsEventSubscribed (eventName)) {
       //基于Polly构建超时合重试策略
        var policy = BuildProcessEventPolicy ();
        using (var serviceScope = _serviceProvider.CreateScope ()) 
        {
            foreach (var handlerType in _subscriptionManager.GetHandlersForEvent (eventName)) 
            {
                var handler = serviceScope.ServiceProvider.GetRequiredService (handlerType);
                if (handler == null) continue;

                var eventType = _subscriptionManager.GetEventTypeByName (eventName);
                var integrationEvent = JsonConvert.DeserializeObject (message, eventType);
                var concreteType = typeof(IEventHandler<>).MakeGenericType (eventType);

                _logger.LogInformation ($"Process event \"{eventName}\" with \"{handler.GetType().Name}\"...");
                yield return (Task)policy.Execute(() => concreteType.GetMethod ("Handle").Invoke (handler, new object[] { integrationEvent }));
            }
        }
    }
}
//RabbitMQ中退订某个事件
private void UnbindQueue (string routingKey) {
    if (!_persistentConnection.IsConnected) _persistentConnection.TryConnect ();
    var channel = _persistentConnection.CreateModel ();
    var queueName = GetQueueName (routingKey);
    channel.QueueUnbind (queueName, _exchangeName, routingKey, null);
}
```
其中，`ProcessEvent()`方法是EventBus通过一个或多个EventHandler处理业务的核心方法。当从RabbitMQ中接收到消息时，首先检查当前事件是否已注册。如果已注册，则获取当前事件对应的EventHandler集合，然后通过IoC容器逐个地取得对应实例，因为在定义EventHandler的时候，我们让`Handle()`方法返回了一个Task，所以，我们可以顺利成章地使用`Task.WhenAll()`，而当所有的EventHandler都处理完成的时候，我们就可以认为这条消息被处理完了，此时，我们可以手动进行ACK，这样这条消息就会从队列中移除，至此，我们已经实现了一个完整的EventBus。

# RabbitMQ进阶与释疑
我在写这篇博客的时候，周围有很多人都劝我不要用RabbitMQ，而主要的理由则是RabbitMQ的吞吐量不如Kafka。我怀疑我们有时候会严重地高估自己，“面试造火箭，入职拧螺丝”，这种事情难道还少吗？与其一张嘴就是高并发、高可用，不如诚实一点结合实际来选择，我相信RabbitMQ里遇到的问题，可能有一些同样会在Kafka里遇到，因为这个世界上就没有最完美的解决方案，对于我写这篇博客的初心而言，我是为了把Binlog发布到RabbitMQ上，方便第三方来订阅这些数据的“变化”，所以，可靠性是不是要比吞吐量更重要一点呢？好了，下面，我们来看一些“杞人忧天”式的RabbitMQ的进阶话题，就是当你熟悉了RabbitMQ的API以后，需要去着重考虑的东西。

## RabbitMQ丢消息怎么办？
第一个问题是最普遍的一个问题，按照“**生产者 -> 交换器 -> 队列 -> 消费者**”的模式，一旦发生丢消息的情况，无非有三种情况：**生产者丢消息**、**消息队列丢消息**、**消费者丢消息**。下面我们逐个进行分析：

1、对于生产者丢消息，RabbitMQ提供的`transaction`和`confirm`机制可以保证生产者不丢消息，` transaction`机制类似数据库的事务，只有当消息发送成功，事物才会被提交，否则事务被被回滚。因为每次发消息都必须开启事物，所以`transaction`机制会导致RabbitMQ吞吐量降低，一般建议使用`confirm`机制，即消息被正确投递则发送ACK给生产者，否则发送NACK给生产者。

2、对于消息队列丢消息，解决方案我们在前面有提到过，主要有两点，**第一，声明队列的时候设置durable为true，这表示这是一个支持持久化的队列。第二，发送消息的时候，设置DeliveryMode为2**，这表示消息支持持久化的磁盘，如果有一天RabbitMQ遭遇不幸，消息会被持久化到磁盘上，所以说，习惯性保存是个好习惯啊……

3、对于消费者丢消息，解决方案是手动ACK，因为只有队列收到ACK时，它才会从队列中删除这条消息，否则，这条消息会重新回到队列中，只要它能重新回到队列、重新处理，它怎么会丢呢？你说对吧？

## RabbitMQ重试与超时
先说结论，关于重试与超时这个话题，我们有两种实现思路，一种是像博主这样，采用Polly定义超时+重试的组合策略，然后将这个策略附加到每一个Handle()方法上，通过程序来实现重试与超时。而第二种思路，则是利用消息/队列的TTL实现超时，利用死信实现重试，消息TTL和队列TTL的不同在于，一个队列超时则队列内的消息会被全部清空，而一个消息超时则可以在清空前决定是否要清空。

重试与超时最大的问题其实在于幂等性，因为在以往的实践中，当我们的消费者变成一个第三方的API接口的时候，我们很难知道，一个消息到底需要处理多久，我一直不明白，为什么宝洁这样的公司，它一个API接口居然能等将近30分钟，而更加令人难以忍受的，是大量只能调用一次的接口，这类接口既无法保证能100%调用成功，同样无法保证，第二次调和第一次调效果完全一样，所以，关于重试与超时这部分，其实应该结合实际业务去设计，因为每个人的诉求可能都不一样。

## RabbitMQ的四种模式
在实现EventBus的过程中，博主用到了`direct`类型的交换器，并说这是RabbitMQ内置的发布-订阅实现，实际上，这里应该有`direct`、` fanout`、` topic`和` head`四种类型的交换器，下面我们来逐个地进行说明。

1、`fanout`相当于广播，所有绑定了该交换器的队列都会收到消息。如下图所示：

![RabbitMQ-fanout模式](https://i.loli.net/2020/07/30/I6Ape3W5C1nOvxV.gif)

2、`direct`相当于发布订阅，只有绑定了该交换器且routingKey完全匹配的队列会收到消息。如下图所示：

![RabbitMQ-driect模式](https://i.loli.net/2020/07/31/xcNezCmHov3UL5D.gif)

3、`topic`相当于`direct` + 模糊匹配，所有绑定了该交换器的队列，且routingKey符合给定的模式，就会收到消息。如下图所示：

![RabbitMQ-topic模式](https://i.loli.net/2020/07/31/j6H5dOX4FsJPgxC.gif)


4、`header`相当于给每条消息定义了一个“头”，只有当头中的一个键值对(Any)或者全部键值对(All)匹配的时候，才会收到消息，这种实际应用中非常少，如下图所示：

![RabbitMQ-header模式](https://i.loli.net/2020/07/31/Q7CkMVsL4jFRtNT.png)

## RaabitMQ的死信机制
RabbitMQ中的死信(Dead Letter)机制，我认为是一个非常有意思的东西，因为从实用性的角度来讲，它可以帮助我们实现“延时队列"，虽然在更多的场景下，我们希望消息能被立即处理，因为这样看起来更像一个“实时”的行为。可在实际应用过程中，我们难免会遇到这样一种情况，一条消息经过手动ACK以后从队列中移除，结果消费者端问你能不能再消费一次这条消息，所以，Kafka里就提供了两种策略，即最多一次和至少一次，最多一次保证的是消息不会被重复消费，而至少一次保证的是消息100%被成功消费。所以，简单来说，在为RabbitMQ配置了死信的情况下，可以让部分消息有机会重新进入队列、重新被消费。那么，什么情况下会产生死信呢？主要有下面三种情况：
* 消息被否定确认，使用`channel.basicNack`或`channel.basicReject`，并且此时`requeue`属性被设置为false。
* 消息在队列的存活时间超过设置的TTL时间。
* 消息队列的消息数量已经超过最大队列长度。

接下来，为了配合死信机制，我们必须要声明死信队列，建议为每一个需要配置死信的事件单独定义一个死信队列，声明方法如下：
```CSharp
//声明死信交换器
channel.ExchangeDeclare("exchange.with.dlx", "direct", true, false);

//声明死信队列
var args = new Dictionary<string, object>();
//该队列中所有消息都进入死信交换器
args.Add("x-dead-letter-exchange", "exchange.with.dlx");
//该队列中指定routingKey的消息进入死信交换器
args.Add("x-dead-letter-routing-key", "foo.bar");
channel.QueueDeclare("queue.with.dlx", true, false, false, args);
```
# 本文小结
本文参考微软的 [eShopOnContainers](https://github.com/dotnet-architecture/eShopOnContainers) 项目，实现一个基于RabbitMQ的事件总线，事件总线是发布-订阅模式的一种延伸，可以在分布式的环境中令消息的发布者、订阅者完美地解耦，是领域驱动设计(DDD)中重要的基础设施之一，对于实现业务上的“事件驱动”非常有帮助。而实现EventBus最关键的三个方法，即Publish()、Subscribe()和Unsubscribe()，这其中需要了解一部分RabbitMQ的知识，所以，在这篇博客中，你可以了解到RabbitMQ的四种交换器、死信机制、重试超时机制等等，在此基础上，我们将在下一篇博客中，通过 [Python-Mysql-Replication](https://github.com/noplay/python-mysql-replication) 实现Binlog的发布，而一旦我们将Binlog发布到消息队列中，本文实现的EventBus就可以作为消息的中介者而登场啦，欢迎大家继续关注我的博客，我们下一篇见！