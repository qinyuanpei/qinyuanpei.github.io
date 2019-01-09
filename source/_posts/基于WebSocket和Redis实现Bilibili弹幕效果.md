---
title: 基于WebSocket和Redis实现Bilibili弹幕效果
categories:
  - 编程语言
tags:
  - Redis
  - WebSocket
  - .NET Core
abbrlink: 3269605707
date: 2018-08-22 14:07:23

---

&emsp;&emsp;嗨，大家好，欢迎大家关注我的博客，我是Payne，我的博客地址是[https://qinyuanpei.github.io](https://qinyuanpei.github.io)。在上一篇博客中，我们使用了.NET Core和Vue搭建了一个基于WebSocket的聊天室。在今天这篇文章中，我们会继续深入这个话题。博主研究WebSocket的初衷是，我们的项目上有需要实时去推送数据来完成图表展示的业务，而博主本人对这个内容比较感兴趣，因为博主有对爬虫抓取的内容进行数据可视化(**ECharts**)的想法。可遗憾的是，这些数据量都不算太大，因为难以支持实时推送这个想法，当然更遗憾的是，我无法在项目中验证以上脑洞，所以，最终退而求其次，博主打算用Redis和WebSocket做一个弹幕的Demo，之所以用Redis，是因为博主懒到不想折腾RabbitMQ。的确，这世界上有很多事情都是没有道理的啊……

&emsp;&emsp;其实，作为一个业余的数据分析爱好者，我是非常乐意看到炫酷的ECharts图表呈现在我的面前的，可当你无法从一个项目中收获到什么的时候，你唯一的选择就是项目以外的地方啦，所以，在今天这样一个精细化分工的时代，即使你没有机会独立地完成一个项目，我依然鼓励大家去了解项目的“上下文”，因为单单了解一个点并不足以了解事物的全貌。好了，下面我们来简单说明下这个Demo整体的设计思路，即我们通过Redis来“模拟”一个简单的消息队列，客户端发送的弹幕会被推送到消息队列中。当WebSocket完成握手以后，我们定时从消息队列中取出弹幕，并推送到所有客户端。当客户端接收到服务端推送的消息后，我们通过Canvas API完成对弹幕的绘制，这样就可以实现一个基本的弹幕系统啦！

# 编写消息推送中间件

&emsp;&emsp;首先，我们来实现服务端的消息推送，其基本原理是：在客户端和服务端完成“握手”后，我们循环地从消息队列中取出消息，并将消息群发至每一个客户端，这样就完成了消息的推送。同上一篇文章一样，我们继续基于“中间件”的形式，来编写消息推送相关的服务。这样，两个WebSocket服务可以独立运行而不受到相互的干扰，因为我们将采用两个不同的路由。在上一篇文章中，我们给“聊天”中间件WebSocketChat配置的路由为**/ws**ws。这里，我们将“消息推送”中间件WebSocketPush配置的路由为**/push**。这块儿我们做了简化，不再对所有WebSocket的连接状态进行维护，因为对一个弹幕系统而言，它不需要让别人了解某个用户的状态是否发生了变化。所以，这里我们给出关键的代码。

```CSharp
public async Task Invoke(HttpContext context)
{
    if (!IsWebSocket(context))
    {
        await _next.Invoke(context);
        return;
    }

    var webSocket = await context.WebSockets.AcceptWebSocketAsync();
    _socketList.Add(webSocket);
    while (webSocket.State == WebSocketState.Open)
    {
        var message = _messageQueue.Pull("barrage",TimeSpan.FromMilliseconds(2));
        foreach(var socket in _socketList)
        {
            await SendMessage(socket,message);
        }
    }

    await webSocket.CloseAsync(WebSocketCloseStatus.NormalClosure, "Close", default(CancellationToken));
}
```

同样地，我们需要在Startup类中添加WebSocketPush中间件。按照ASP.NET Core中的惯例，我们为IAppBuilder接口增加一个名为UseWebSocketPush的扩展方法。这样，可以让我们直接使用该方法完成中间件的注册。

```CSharp
public static void UseWebSocketPush(this IApplicationBuilder app)
{
    app.UseMiddleware<WebSocketPush>();
}
```

# Redis打造的消息队列

&emsp;&emsp;OK，在编写“消息推送”中间件的时候，我们会注意到，我们使用了一个名为SimpleMessageQueue的类来取得消息，而服务端会负责将该消息群发到所有的客户端。这个其实就是博主写的一个简单的消息队列啦，如此简洁直白的命名证明它的确非常简单。有多简单呢？我想一会儿大家就会找到答案。在此之前，我想和大家讨论这样一个问题。其实，聊天室和弹幕挺像的吧，理论上服务端接收到客户端发的消息，就可以直接群发过去啊，为什么要搞一个消息队列在这里呢？而且更扯的一点是，既然博主你选择用Redis啦，你难道不知道Redis天生就支持发布订阅(**Pub-Sub**)吗？为什么要搞一个消息队列在这里呢？

&emsp;&emsp;对这个问题，我的想法其实是这样的，我最初想做的是：后端定期推送数据到前端，再由前端通过这些数据来绘制图表。此时，无论后端还是前端，其实都是数据的消费者，这些数据当然不能一股脑儿全给它们啊，这吃撑着了可怎么办，所以，为了避免它们消化不良，我得有一个东西帮助它维持秩序啊，这就是消息队列啊。简单来说，如果数据量超过程序的处理能力，这个时候我们就需要消息队列在前面帮忙“挡”一下。想象一下，如果去银行办理业务的人，都不排队一股脑儿涌向柜台，银行柜员大概会感到崩溃。我们的程序模拟的是现实生活，所以，我们需要消息队列。

![为什么需要消息队列](http://7wy477.com1.z0.glb.clouddn.com/mq01.png)

&emsp;&emsp;那么，有朋友要问啦，就算你要用消息队列，那博主你为什么不用RibbitMQ，再不济可以考虑微软自带的MQ啊，为什么要用Redis做一个MQ呢？就算你坚持要用Redis做MQ，为什么不考虑用的Redis的发布-订阅(**Pub-Sub**)呢？对于第一个问题，你可以理解为我穷或者懒(**穷个什么鬼啊，你特么就是懒_(:з」∠)_**)。我就是懒得去搞RabbitMQ，谁让我电脑C盘都快爆炸了呢，自从我把玩了几次**Docker for Windows**以后，而且我们项目上还真有不被允许用MQ的情况。所以，基于以上原因，我选择了Redis。

![Redis中的Pub-Sub](http://7wy477.com1.z0.glb.clouddn.com/mq02.png)

&emsp;&emsp;那么，为什么不用发布-订阅(**Pub-Sub**)呢，因为观察者模式的一个前提是，订阅者和主题必须在同一个上下文，即消息的发送方和接受方都必须同时“在线”。可Bilibili的弹幕和用户的在线与否无关，这意味着发弹幕与接收弹幕可以不在同一个时刻，所以，在设计上我们是提供了一个API接口来发送弹幕，而不是直接通过WebSocket来发送。否则，消息都到达服务端了，再通过一个消息队列来取消息，这就真的有点奇怪了不是吗？

&emsp;&emsp;下面给出这个消息队列的实现，原理上是这样的，每一个消息所在的Channel，实际上都是一个列表，我们使用Channel的名称作为这个列表的键。接下来，ServiceStack提供的Redis客户端中，提供了名为BlockingListItem()的方法，它可以提供类似消息队列的功能，我们在这个基础上实现了一个简单的消息队列。

```CSharp
public class SimpleMessageQueue
{
    private string _connectionString;
    private readonly BasicRedisClientManager _clientManager;
    public SimpleMessageQueue(string connectionString)
    {
        _connectionString = connectionString;
        _clientManager = new BasicRedisClientManager(_connectionString);
    }

    public void Push(string channel, string messsage)
    {
        using (var client = _clientManager.GetClient())
        {
            client.PushItemToList(channel, messsage);
        }
    }

    public void Push(string channel, IEnumerable<string> messages)
    {
        using (var client = _clientManager.GetClient())
        {
            client.AddRangeToList(channel, messages.ToList());
        }
    }

    public string Pull(string channel,TimeSpan interval)
    {
        using (var client = _clientManager.GetClient())
        {
            return client.BlockingDequeueItemFromList(channel,interval);
        }
    }
}
```

相应地，在WebSocketPush中间件中，我们通过Pull()方法来取得消息，时间间隔为2s。在MessageController中，我们提供了用以发送弹幕的API接口，它实际上调用了Push()方法，这个非常简单啦，我们不再做详细说明。

```CSharp
[HttpPost]
[Route("/api/message/publish/barrage")]
public IActionResult Publish()
{
    Stream stream = HttpContext.Request.Body;
    byte[] buffer = new byte[HttpContext.Request.ContentLength.Value];
    stream.Read(buffer, 0, buffer.Length);
    string message = System.Text.Encoding.UTF8.GetString(buffer);
    _redisPublisher.Push("barrage", message);
    Response.Headers.Add("Access-Control-Allow-Origin", "*");
    return Ok();
}
```

# 使用Canvas绘制弹幕

&emsp;&emsp;好啦，截止到目前为止，我们所有后端的开发已基本就绪。现在，我们来关注下前端的实现。关于WebSocket原生API的使用，在上一篇文章中，我们已经讲过啦，这里我们重点放在客户端提交弹幕以及绘制弹幕。

&emsp;&emsp;首先来说，客户端提交弹幕到服务器，因为我们已经编写了相应的Web API，所以这里我们简单调用下它就好。和上一篇文章一样，我们继续使用Vue作为我们的前端框架，这对一个不会写ES6和CSS的伪前端来说，是非常友好的一种体验。因为现在是2018年，所以，我们要坚决地放弃jQuery，虽然它的ajax的确很好用，可这里我们还是要使用Axios：

```JavaScript
axios.post("http://localhost:8002/api/message/publish/barrage",{
    value: self.value,
    color: self.color,
    time: self.video.currentTime
}).then(function (response) {
    console.log(response);
})
.catch(function (error) {
    console.log(error);
});
```

&emsp;&emsp;接下来，说说弹幕绘制。我们知道，HTML5中提供了基于Canvas的绘图API，所以，我们这里可以用它来完成弹幕的绘制。基本思路是：根据video标签计算出弹幕出现的范围，然后让弹幕从右侧向左逐渐移动，而弹幕的垂直位置则可以是顶部/底部/随机，当弹幕移动到屏幕左侧时，我们从弹幕集合中移除掉这个元素即可。下面给出基本代码，绘图相关的接口可以参考[这里](http://www.w3school.com.cn/tags/html_ref_canvas.asp)，弹幕相关参考了这篇[文章](https://www.zhangxinxu.com/wordpress/2017/09/html5-canvas-video-barrage/)：

```JavaScript
var context = canvas.getContext('2d');
context.shadowColor = 'rgba(0,0,0,' + this.opacity + ')';
context.shadowBlur = 2;
context.font = this.fontSize + 'px "microsoft yahei", sans-serif';
if (/rgb\(/.test(this.color)) {
 context.fillStyle = 'rgba(' + this.color.split('(')[1].split(')')[0] + ',' + this.opacity + ')';
} else {
 context.fillStyle = this.color;
}
context.fillText(this.value, this.x, this.y);
```

# 翻滚吧，弹幕！

&emsp;&emsp;OK，现在我们来一起看看最终的效果，如你所见，在视频播放过程中，我们可以通过视频下方的输入框发送弹幕，弹幕会首先经由Redis缓存起来，当到达一定的时间间隔以后，我们就会将消息推送到客户端，这样所有的客户端都会看到这条弹幕，而对于客户端来说，它在和服务端建立WebSocket连接以后，唯一要做的事情就是在onmessage回调中取得弹幕数据，并将其追加到弹幕数组中，关于弹幕绘制的细节，我们在本文的第三节已经做了相关说明，在此不再赘述。
![弹幕效果展示](https://ws1.sinaimg.cn/large/4c36074fly1fz0206huayg20jo0h3npj.gif)
&emsp;&emsp;这里，我们采用了前后端分离的设计，即使我们没有并使用主流的ES6去实现客户端。因此，这是客户端实际上是一个静态页面，在本地开发阶段，我们可以通过打开多个浏览器窗口来模拟多用户。那么，如果我们希望让更多人来访问这个页面该怎么做呢？这就要说到ASP.NET Core中的静态文件中间件。无论是IIS还是Apache，对静态页面进行展示，是一个Web服务器最基本的能力。在ASP.NET Core中，我们是通过静态文件中间件来实现这个功能，简而言之，通过这个功能，我们就可以让别人通过IP或者域名来访问wwwroot目录下的内容。具体代码如下：

```JavaScript
app.UseDirectoryBrowser();
app.UseStaticFiles(); 
```

&emsp;&emsp;当然，这里有一个细节是为了让别人可以通过IP或者域名来访问你的服务，你需要修改下WebHostBuilder中URL。此外，因为我们在前端界面中使用了绝对的URL去访问WebAPI，因此，当前端页面和WebAPI不在一个域中时，就会出现所谓垮域的问题，这方面的内容非常丰富，因为这是一个再常见不过的问题，身处在这个时代，80%的问题都已经被解决过了，这到底是我们的幸运还是不幸呢？

```JavaScript
WebHost.CreateDefaultBuilder(args)
   .UseStartup<Startup>()
   .UseUrls("http://*:8002"); 
```

# 本文小结

&emsp;&emsp;本文在[上一篇](https://qinyuanpei.github.io/posts/1989654282/)的基础上，借助Redis和WebSocket实现了一个简单的弹幕系统。博主的初衷是想一个数据可视化的小项目，可以通过WebSocket实时地刷新图表，因为在博主看来，数据分析同样是有趣的事情。这篇文章选取博主在工作中遇到的实际场景作为切入点，试图发掘出WebSocket在实时应用方面更多的可能性。

&emsp;&emsp;首先，我们编写了“消息推送”中间件，并通过不同的路由来处理各自的业务，实现了模块间的相互独立。接下来，我们讨论了Redis作为消息队列的可行性，并基于Redis编写了一个简单的消息队列。最终，通Canvas API完成客户端弹幕的绘制，实现了从后端到前端的方案整合。藉由这个小项目，可以引出ASP.NET Core相关的话题，譬如静态文件中间件、部署、跨域等等的话题，感兴趣的朋友可以自己去做进一步的了解，以上就是这篇博客的全部内容啦，谢谢大家！