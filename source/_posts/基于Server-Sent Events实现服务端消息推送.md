---
title: 基于Server-Sent Events实现服务端消息推送
categories:
  - 编程语言
tags:
  - WebSocket
  - SSE
  - 后端
abbrlink: 3175881014
date: 2019-01-18 13:46:44
---
前段时间，为客户定制了一个类似看板的东西，用户可以通过看板了解任务的处理情况，通过APP扫面页面上的二维码就可以领取任务，而当任务被领取以后需要通知当前页面刷新。原本这是一个相对简单的需求，可是因为APP端和PC端是两个不同的Team在维护，换句话说，两个Team各自有一套自己的API接口，前端页面永远无法知道APP到底什么时候扫描了二维码，为此前端页面不得不通过轮询的方式去判断状态是否发生了变化。这种方式会发送大量无用的HTTP请求，因此在最初的版本里，无论是效率还是性能都不能满足业务要求，最终博主采用一种称为服务器推送事件(**Server-Sent Events**)的技术，所以，在今天这篇文章里，博主相和大家分享下关于服务器推送事件(**Server-Sent Events**)相关的内容。

# 什么是Server-Sent Events
我们知道，严格地来讲，HTTP协议是无法做到服务端主动推送消息的，因为HTTP协议是一种**请求-响应**模型，这意味着在服务器返回响应信息以后，本次请求就已经结束了。可是，我们有一种变通的做法，即首先是服务器端向客户端声明，然后接下来发送的是流信息。换句话说，此时发送的不是一个一次性的数据包，而是以数据流的形式不断地发送过来，在这种情况下，客户端不会关闭连接，会一直等着服务器端发送新的数据过来，一个非常相似而直观的例子是视频播放，它其实就是在利用流信息完成一次长时间的下载。那么，**Server-Sent Events**(以下简称**SSE**)，就是利用这种机制，使用流信息像客户端推送信息。

说到这里，可能大家会感到疑惑：WebSocket不是同样可以实现服务端向客户端推送信息吗？那么这两种技术有什么不一样呢？首先，WebSocket和SSE都是在建立一种浏览器与服务器间的通信通道，然后由服务器向浏览器推送信息。两者最为不同的地方在于，WebSocket建立的是一个全双工通道，而SSE建立的是一个单工通道。所谓单工和双工，是指数据流动的方向上的不同，对WebSocket而言，客户端和服务端都可以发送信息，所以它是双向通信；而对于SSE而言，只有服务端可以发送消息，故而它是单向通信。从下面的图中我们可以看得更为直观，在WebSocket中数据"有来有往"，客户端既可以接受信息亦可发送信息，而在SSE中数据是单向的，客户端只能被动地接收来自服务器的信息。所以，这两者在通信机制上不同到这里已经非常清晰啦！

![WebSocket与SSE对比](https://ws1.sinaimg.cn/large/4c36074fly1fzf5w39987j20se0dv77u.jpg)

## SSE服务端

下面我们来看看SSE是如何通信的，因为它是一个单工通道的协议，所以协议定义的都是在服务端完成的，我们就从服务端开始吧！协议规定，服务器向客户端发送的消息，必须是UTF-8编码的，并且提供如下的HTTP头部信息：

```shell
Content-Type: text/event-stream
Cache-Control: no-cache
Connection: keep-alive
```
这里出现了一个一种新的MIME类型，**text/event-stream**。协议规定，第一行的Content-Type必须是**text/event-stream**，这表示服务端的数据是以信息流的方式返回的，Cache-Control和Connection两个字段和常规的HTTP一致，这里就不再展开说啦！OK，现在客户端知道这是一个SSE信息流啦，那么客户端怎么知道服务端发送了什么消息呢？这就要说到SSE的消息格式，在SSE中消息的基本格式是：
```
[field]: value\n
```
其中，field可以取四个值，它们分别是：**data**、**event**、**id**、**retry**，我们来一起看看它们的用法。

**data**字段表示数据内容，下面的例子展示SSE中的一行和多行数据，可以注意到，当数据有多行时，可以用\n作为每一行的结尾，只要保证最后一行以\n\n结尾即可。

```
：这是一行数据内容
data: SSE给你发了一行消息\n\n
：这是多行数据内容
data: {\n
data: "foo": "foolish",\n
data: "bar", 2333\n
data: }\n\n
```
**event**字段表示自定义事件，默认为message，在浏览器中我们可以用**addEventListener()**来监听响应的事件，这正是为什么SSE被称为服务器推送事件，因为我们在这里既可以发送消息，同样可以发送事件。
```
: GameStart事件
event: GameStart\n
data: 敌军还有30秒到达战场\n\n

data: Double Kill\n\n

: GameOver事件
event: GaneOver\n
data: You Win！\n\n
```
**id **字段是一个数据标识符，相当于我们可以给每一条消息一个编号。

```
id: 1\n
data: 敌军还有30秒到达战场\n\n
id: 2\n
data: Double Kill\n\n
id: 3\n
data: You Win！\n\n
```
**retry**字段可以指定浏览器重新发起连接的时间间隔，所以，SSE天生就支持断线重连机制。
```
retry: 10000\n
```
## SSE客户端

SSE目前是HTML5标准之一，所以，目前主流的浏览器(**除了IE和Edge以外**)都天然支持这一特性，这意味着我们不需要依赖**前端娱乐圈**推崇的各种工具链，就可以快速地使用SSE来投入开发。这里需要使用地是[EventSource](https://developer.mozilla.org/zh-CN/Server-sent_events/EventSource)对象，我们从下面这个例子开始了解：
```Javascript
if ('EventSource' in window) {
  var source = new EventSource(url, { withCredentials: true });
  
  /* open事件回调函数 */
  source.onopen = function(){ 
  	console.log('SSE通道已建立...');
  };
  
  /* message事件回调函数 */
  source.onmessage = function(evt){
  	console.log(evt.data);
  }
  
  /* error事件回调函数 */
  source.onerror = function(evt){
  	console.log('SSE通道发生错误');
  }
  
  /* 自定义事件回调 */
  source.addEventListener('foo', function (event) {
  	var data = event.data;
  	// handle message
  },false);
	
  /* 关闭SSE */
  source.close()
}
```
和各种各样的HTML5接口一样，我们需要判断当前的浏览器环境是否支持SSE。建立SSE只需要后端提供一个Url即可，当存在跨域时，我们可以打开第二个参数：**withCredentials**，这样SSE会在建立通道时携带Cookie。我们通过实例化后的source对象来判断通道是否建立，该对象有一个重要的属性：**readyState**。当它的取值为0时，表示连接还未建立，或者断线正在重连；当它的取值为1时，表示连接已经建立，可以接受数据；当它的取值为2时，表示连接已断，且不会重连。

好了，当SSE被成功建立以后，首先会触发open事件。这里介绍下SSE中的关键事件，即open、message和error，我们可以分别通过**onopen**、**onmessage**和**onerror**这三个回调函数来监听相应的事件。对于SSE而言，它是一个单工通道，客户端不能主动向服务端发送信息，所以，一旦建立了SSE通道，客户端唯一需要关注的地方就是**onmessage**这个回调函数，因为客户端只需要负责处理消息即可，甚至我们可以连**onerror**都不用关注，因为SSE自带断线重连机制，当然你可以选择在发生错误的时候关掉连接，此时你需要**close()**方法。

我们在上面提到，SSE在服务端可以定义自定义事件，那么，在浏览器中我们该如何接收这些自定义事件呢？这当然要提到无所不能的**addEventListener**，在人肉操作DOM的jQuery时代，jQuery中提供的大量API在协调不同浏览器间差异的同时，让我们离这些底层的知识越来越远，时至今日，当**erySelector/querySelectorAll**完全可以替换jQuery的选择器的时候，我们是不是可以考虑重新把某些东西捡起来呢？言归正传，在SSE中，我们只需要像注册普通事件一样，就可以完成对自定义事件的监听，只要客户端和服务端定好消息的协议即可。

# 在.NET中集成Server-Sent Events

OK，说了这么多，大家一定感觉有一个鲜活的例子会比较好一点，奈何[官方](https://developer.mozilla.org/zh-CN/docs/Server-sent_events/Using_server-sent_events)提供的示例都是PHP的，难道官方默认PHP是世界上最好的编程语言了吗？所谓**万变不离其宗"**，下面我们以.NET为例来快速集成Server-Sent Events，这里需要说明的是，博主下面的例子采用ASP.NET Core 2.0版本编写，首先，我们建一个名为SSEController的控制器，在默认的Index()方法中，按照SSE规范，我们首先组织HTTP响应头，然后发送了一个名为SSE_Start的自定义事件，接下来，我们每隔10秒钟给客户端发送一条消息，请原谅我如此敷衍的Sleep()：
```CSharp
[Route("api/[controller]")]
[ApiController]
public class SSEController : Controller
{
    [HttpGet]
    public IActionResult Index()
    {
    	//组织HTTP响应头
    	Response.Headers.Add("Connection", "keep-alive");
    	Response.Headers.Add("Cache-Control", "no-cache");
    	Response.Headers.Add("Content-Type", "text/event-stream");

    	//发送自定义事件
        var message = BuildSSE(new { Content = "SSE开始发送消息", Time = DateTime.Now }, "SSE_Start");
        Response.Body.Write(message, 0, message.Length);

        //每隔10秒钟向客户端发送一条消息
        while (true)
        {
            message = BuildSSE(new { Content = $"当前时间为{DateTime.Now}" });
            Response.Body.Write(message, 0, message.Length);
            Thread.Sleep(10000);
       }
    }
}
```
我们提到，SSE的数据是按照一定的格式，由id、event、data和retry四个字段构成的，那么，织消息格式的代码我们放在了**BuildSSE()**方法中，我们来一起看看它的实现：
```CSharp
private byte[] BuildSSE<TMessage>(TMessage message, string eventName = null, int retry = 30000)
{
    var builder = new StringBuilder();
    builder.Append($"id:{Guid.NewGuid().ToString("N")}\n");
    if (!string.IsNullOrEmpty(eventName))
        builder.Append($"event:{eventName}\n");
    builder.Append($"retry:{retry}\n");
    builder.Append($"data:{JsonConvert.SerializeObject(message)}\n\n");
    return Encoding.UTF8.GetBytes(builder.ToString());
} 
```
可以看到，完全按照SSE规范来定义的，这里每次生成一个新的GUID来作为消息的ID，客户端断线后重连的间隔为30秒，默认发送的是**"消息"**，当指定eventName参数时，它就表示一个自定义事件，这里我们使用JSON格式来传递信息。好了，这样我们就完成了服务端的开发，怎么样，是不是感觉非常简单呢？我们先让它跑起来，下面着手来编写客户端，这个就非常简单啦！
```JavaScript
<!DOCTYPE html>
<html>
<body>
<h1>DotNet-SSE</h1>
<div id="result"></div>
<script>
if ('EventSource' in window) {
  var source = new EventSource('http://localhost:5000/api/SSE/');
  
  /* open事件回调函数 */
  source.onopen = function(){ 
  	document.getElementById("result").innerHTML+= "SSE通道已建立...<br/>";
  };
  
  /* message事件回调函数 */
  source.onmessage = function(evt){
  	document.getElementById("result").innerHTML+= "Message: " + event.data + "<br/>";
  }
  
  /* error事件回调函数 */
  source.onerror = function(evt){
      document.getElementById("result").innerHTML+= "SSE通道发生错误<br/>";
  }
  
  /* SSE_Start事件回调 */
  source.addEventListener('SSE_Start', function (event) {
  	document.getElementById("result").innerHTML += "SSE_Start: " + event.data + "<br/>";
  },false);
}
</script>
</body>
</html>
```
此时，不需要任何**现代前端**方面的技术，我们直接打开浏览器，就可以看到：

![SSEDemo](https://ws1.sinaimg.cn/large/4c36074fly1fzfbt5m898g20jk06jdfw.gif)

更为直观的，我们可以通过Chrome开发者工具观察到实际的请求情况，相比普通的HTTP请求，SSE会出现一个名为EventStream的选项卡，这是因为我们在服务端设置的Content-Type为**text/event-stream**的缘故，可以注意到，我们定义的id(GUID)会在这里显示出来：

![有点与众不同的SSE](https://ws1.sinaimg.cn/large/4c36074fly1fzfc3ik2l2j20ww07kgmo.jpg)

# 同类技术优劣对比

OK，这篇文章写到这里，相信大家已经对SSE有了一个比较具体的概念，那么，我们不妨来梳理下相关的同类技术。一路走过来，我们大体上经历了**(短)轮询**、**长轮询/Comet**、**SSE**和**WebSocket**。

**(短)轮询**这个比较容易理解了，它从本质上来讲，就是由客户端定时去发起一个HTTP请求，这种方式是一种相对尴尬的方式，为什么这样说呢？因为时间间隔过长则无法保证数据的时效性，而时间间隔过短则会发送大量无用的请求，尤其是当客户端数量比较多的时候，这种方式很容易耗尽服务器的连接数。

**而长轮询**则是(短)轮询的一个变种，它和(短)轮询最大的不同在于，服务端在接收到请求以后，并非立即进行响应，而是先将这个请求挂起，直到服务器端数据发生变化时再进行响应。所以，一个明显的优势是，它相对地减少了大量不必要的HTTP请求，那么，它是不是就完美无暇了呢？当然不是，因为服务端会将客户端发来的请求挂起，因此在挂起的那些时间里，服务器的资源实际上是被浪费啦！

严格地说，**SSE**并不是一门新技术，为什么这样说呢？因为它和我们基于HTTP长连接的Push非常相似。这里又提到一个新概念，HTTP长连接，其实，这个说法病逝非常严谨，因为我们知道HTTP最早就是一个请求-响应模型，直到HTTP1.1中增加了持久连接，即Connection:keep-alive的支持。所以，我们这里说的长连接、短链接实际上都是指TCP的长连接还是短连接，换句话说，它和客户端没有关系，只要服务端支持长连接，那么在某个时间段内的TCP连接实际上复用的，进而就能提高HTTP请求性能，曾经我们不是还用iframe做过长连接吗？

**WebSocket**作为构建实时交互应用的首选技术，博主曾经在[《基于WebSocket和Redis实现Bilibili弹幕效果》](https://qinyuanpei.github.io/posts/3269605707/)一文中有所提及，WebSocket相比前面这些技术，最大的不同在于它拥有专属的通信通道，一旦这个通道建立，客户端和服务端就可以互相发送消息，它沿用了我们传统的Socket通讯的概念和原理，变被动为主动，无论是客户端还是服务端，都不必再被动地去**"拉"**或者**"推"**。在这个过程中，出现了像SignalR/SocketIO等等的库，它们主打的兼容性和降级策略，曾经一度让我们感到亲切，不过随着WebSocket标准化的推进，相信这些最终都会被原生API所替代吧，也许是有生之年呢？谁知道未来是什么样子呢？

下面给出针对以上内容的**"简洁"**版本：

|              | （短)轮询       | 长轮询/Comet | SSE       | WebSocket  |
| ------------ | --------------- | ------------ | --------- | ---------- |
| 浏览器支持   | 全部            | 全部         | 除IE/Edge | 现代浏览器 |
| 是否独立协议 | HTTP            | HTTP         | HTTP      | WS         |
| 是否轻量     | 是              | 否           | 是        | 否         |
| 断线重连     | 否              | 否           | 是        | 否         |
| 负载压力     | 占用内存/请求数 | 同（短)轮询  | 一般      | 同SSE      |
| 数据延迟     | 取决于请求间隔  | 同（短)轮询  | 实时      | 实时       |

# 本文小结

正如本文一开始所写，博主使用SSE是因为业务上的需要，在经历了轮询带来的性能问题以后，博主需要一款类似WebSocket的东西，来实现服务端主动向客户端推送消息，究其原因，是因为浏览器永远都不知道，App到底什么时候会扫描二维码，所以，从一开始我们试图让网页去轮询的做法，本身就是不太合理的。那么，为什么没有用WebSocket呢？因为WebSocket需要一点点**框架**层面的支持，所以，我选择了更为轻量级的SSE，毕竟，这比让其它Team的同事去调整他们的后端接口要简单的多。我之前参与过一部分WebSocket相关的项目，我深切地感受到，除了在浏览器的兼容性问题以外，因为WebSocket使用的是独有的WS协议，所以，我们常规的API网关其实在这方面支持的都不是很好，更不用说鉴权、加密等等一系列的问题啦，而SSE本身是基于HTTP协议的，我们目前针对HTTP的各种基础设施，都可以直接拿过来用，这应该是我最大的一点感悟了吧，好了，这篇文章就是这样啦，谢谢大家，新的一年注定要重新开始的呢......


# 参考文章

* [IBM - Comet：基于 HTTP 长连接的“服务器推”技术](https://www.ibm.com/developerworks/cn/web/wa-lo-comet/)
* [Mozilla - 使用服务器发送事件](https://developer.mozilla.org/zh-CN/docs/Server-sent_events/Using_server-sent_events)
* [阮一峰 - Server-Sent Events 教程](http://www.ruanyifeng.com/blog/2017/05/server-sent_events.html)
* [呆呆_小茗 - Ajax轮询，Ajax长轮询和Websocket(详细使用)](https://blog.csdn.net/baidu_38990811/article/details/79172163)
* [ hrhguanli - HTTP长连接和短连接](https://www.cnblogs.com/hrhguanli/p/3818452.html)

