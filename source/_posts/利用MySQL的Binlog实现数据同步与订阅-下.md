---
toc: true
title: 利用MySQL的Binlog实现数据同步与订阅(下)
categories:
  - 数据存储
tags:
  - Binlog
  - RabbitMQ
  - MySQL
copyright: true
abbrlink: 3424138425
date: 2020-07-31 12:01:14
---
终于到这个系列的最后一篇，在前两篇博客中，我们分别了介绍了**Binlog**的概念和事件总线(**EventBus**)的实现，在完成前面这将近好几千字的铺垫以后，我们终于可以进入正题，即通过EventBus发布Binlog，再通过编写对应的EventHandler来订阅这些Binlog，这样就实现了我们“最初的梦想”。坦白说，这个过程实在有一点漫长，庆幸的是，它终于还是来了。

# Binlog读取与解析
首先，我们通过 [Python-Mysql-Replication](https://github.com/noplay/python-mysql-replication) 这个项目来读取Binlog，直接通过`pip install mysql-replication`安装即可。接下来，我们编写一个简单的脚本文件，这再次印证那句名言——人生苦短，我用Python：
``` Python
def readBinLog():
    stream = BinLogStreamReader(
        # 填写IP、账号、密码即可
        connection_settings = {
            'host': '',
            'port': 3306, 
            'user': '', 
            'passwd': ''
        },
        # 每台服务器唯一
        server_id = 3, 
        # 主库Binlog读写完毕时是否阻塞连接
        blocking = True, 
        # 筛选指定的表
        only_tables = ['order_info', 'log_info'], 
        # 筛选指定的事件
        only_events = [DeleteRowsEvent, WriteRowsEvent, UpdateRowsEvent]) 

    for binlogevent in stream:
        for row in binlogevent.rows:
            event = {
                "schema": binlogevent.schema,
                "table": binlogevent.table,
                "log_pos": binlogevent.packet.log_pos
            }
            if isinstance(binlogevent, DeleteRowsEvent):
                event["action"] = "delete"
                event["origin"] = dict(row["values"].items())
                event["current"] = None
                event = dict(event.items())
            elif isinstance(binlogevent, UpdateRowsEvent):
                event["action"] = "update"
                event["origin"] = dict(row["before_values"].items())
                event["current"] = dict(row["after_values"].items())
                event = dict(event.items())
            elif isinstance(binlogevent, WriteRowsEvent):
                event["action"] = "insert"
                event["origin"] = None
                event["current"] = dict(row["values"].items())
                event = dict(event.items())
    stream.close()
```

# 发布Binlog
在读取到Binlog以后，我们需要将其发布到EventBus里，为此，在.NET Core这边提供一个Web API接口，只需要注入` IEventBus`然后调用` Publish()`即可：
``` CSharp
// Post: /<controller>/Publish
[HttpPost]
[Route ("PublishBinLog")]
public Task PublishBinLog (BinLogEventModel<dynamic> eventModel) 
{
    if (eventModel.action == "insert" && eventModel.table.StartsWith ("log_"))
        _eventBus.Publish (eventModel.MapTo<WriteLogEvent> ());
    if (eventModel.action == "insert" && eventModel.table == "order_info")
        _eventBus.Publish (eventModel.MapTo<OrderInfoCreateEvent> ());
    return Task.CompletedTask;
}
```
相应地，我们需要在脚本中添加调用Web API的逻辑代码，使用我们最熟悉的`requests`库即可：
```  Python
def sendBinLog(event):
    url = "https://localhost:44348/EventBus/PublishBinLog"
    headers = {
        'Content-Type': "application/json",
    }
    try:
        payload = json.dumps(event,cls=ComplexEncoder)
        response = session.request("POST", url, data=payload, headers=headers, verify=False)
    except Exception:
        pass
```
在这里，在处理Binlog的序列化的问题时，我们可能会遇到默认的JSON序列化器无法对event进行序列化的问题，此时，我们可以编写一个自定义的序列化器，下面是博主目前在使用的序列化器：
```Python
class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, date):
            return obj.strftime('%Y-%m-%d')
        elif isinstance(obj, decimal.Decimal):
            return str(obj)
        elif isinstance(obj, bytes):
            return obj.decode('utf-8')  
        else:
            return json.JSONEncoder.default(self, obj)
```

# 订阅Binlog
现在，为了订阅这些Binlog，我们来编写对应的EventHandler，这里我们定义两个EventHandler，一个用于打印日志编号、日志内容、日志级别等信息，一个用于统计不同级别的日志的数目。代码实现如下：
``` CSharp
//打印日志的EventHandler
public class WriteLogEventHandler : IEventHandler<WriteLogEvent> {
    private ILogger<WriteLogEventHandler> _logger;
    public WriteLogEventHandler (ILogger<WriteLogEventHandler> logger) {
        _logger = logger;
    }
    public Task Handle (WriteLogEvent @event) {
        _logger.LogInformation ($"日志编号：{@event.TRANSACTION_ID}，日志级别：{@event.LOG_LEVEL}，主机：{@event.HOST_NAME}，IP：{@event.HOST_IP}，内容：{@event.CONTENT}");
        return Task.CompletedTask;
    }
}

//分析日志的EventHandler
public class AnalyseLogEventHandler : IEventHandler<WriteLogEvent> {
    private readonly ILogger<AnalyseLogEventHandler> _logger;
    private readonly IDistributedCache _cache;
    public AnalyseLogEventHandler (ILogger<AnalyseLogEventHandler> logger, IDistributedCache cache) {
        _logger = logger;
        _cache = cache;
    }
    public Task Handle (WriteLogEvent @event) {
        var cacheCount = _cache.GetString (@event.LOG_LEVEL);
        if (string.IsNullOrEmpty (cacheCount))
            cacheCount = "1";
        else
            cacheCount = (int.Parse (cacheCount) + 1).ToString ();
        _cache.SetString (@event.LOG_LEVEL, cacheCount);;
        return Task.CompletedTask;
    }
}
```
注意，这里需要在`Startup`中注入`EventHandler`、`EventBus`以及各种必要的依赖项，你可以手动注册，或者参考下面的代码，实现扫描注册：
``` CSharp
services.AddSingleton<IRabbitMQPersistentConnection, DefaultRabbitMQPersistentConnection> ();
services.AddSingleton<IEventBusSubscriptionManager, EventBusSubscriptionManager> (sp => new EventBusSubscriptionManager ());
services.AddSingleton<IConnectionFactory, ConnectionFactory> (sp => new ConnectionFactory () { HostName = "localhost", UserName = "guest", Password = "guest" });
services.AddSingleton<ObjectPoolProvider, DefaultObjectPoolProvider> ();
services.AddControllers ().AddNewtonsoftJson ();
services.AddDistributedMemoryCache (options => {
    options.ExpirationScanFrequency = TimeSpan.FromMinutes (5);
    options.SizeLimit = 10;
});

//自动注册
services.AddEventBus();

//手动注册
services.AddSingleton<IEventBus, RabbitMQEventBus> (sp => {
    var eventBus = new RabbitMQEventBus (sp.GetRequiredService<IRabbitMQPersistentConnection> (), sp.GetRequiredService<IEventBusSubscriptionManager> (), sp.GetRequiredService<ILogger<RabbitMQEventBus>> (), sp, "eventbus-exchange", "eventbus-queue");
    eventBus.Subscribe<WriteLogEvent, WriteLogEventHandler>():
    eventBus.Subscribe<WriteLogEvent, AnalyseLogEventHandler>();
    return eventBus;
});

services.AddTransient<WriteLogEventHandler>();
services.AddTransient<AnalyseLogEventHandler>();

```
一起来看看效果，简直太完美了，我就是不想写中间表啊，这样多好！！！
![Python 读取 Binlog 演示](https://i.loli.net/2020/07/31/PRjfiYpWNqHxI7Z.gif)
![.NET Core 消费 Binlog演示](https://i.loli.net/2020/07/31/yVZgIn9NifpxTXa.gif)
![RabbitMQ Dashboard 演示](https://i.loli.net/2020/07/31/iMX5PFCoak7VDv9.png)

# 本文小结
通过三篇博客的篇幅，我们实现了“利用MySQL的Binlog实现数据同步与订阅”的想法。在这个过程中，我们了解了Binlog的相关概念，参考微软的 [eShopOnContainers](https://github.com/dotnet-architecture/eShopOnContainers) 项目实现了一个基于RabbitMQ的EventBus，而这一切都在这篇博客中完成了最终的“拼合”，通过 [Python-Mysql-Replication](https://github.com/noplay/python-mysql-replication) 实现了Binlog解析，而EventBus则作为整个事件系统的“上帝”对所有事件处理器(**EventHandler**)进行统一调度，最终我们不需要关心这些事件是如何被发布到EventBus中的，只需要知道它对应哪一个Event并为它编写对应的EventHandler即可，除了这篇博客中提到的Binlog以外，实际上它还可以作为系统内的“领域事件”来实现业务上的事件驱动，譬如`OrderInfoCreateEvent`这个事件可以表示一个订单被创建，而关心订单状态的人则可以通过EventHandler来实现订阅，实现类似发短信、发邮件、发微信等等的功能，或者可以让第三方的Web API来消费事件中携带的信息。同理，第三方的数据在流入系统时，可以先发布到消息队列中，再通过对应的EventHandler来进行异步处理，极大地改善系统接口的吞吐性能，而如果在这中间抽象出来一个数据交换层出来，那么就能收获更多不一样的东西，就在写这篇博客的时候，我在Github上的代码被收入了微软的"北极冰川火种计划"，虽然数字世界远比现实世界宽广得多，可能为这个世界减少一点“无用”的数据或者代码，应该一样可以算作是环保行为吧！