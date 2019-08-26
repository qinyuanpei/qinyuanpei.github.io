---
abbrlink: 3603924376
categories:
- 编程语言
date: 2016-06-11 15:01:35
description: 其次，我们在设计HTTP服务器的时候，每次在向客户端返回响应报文以后，我们就关闭了Socket连接，这意味着每次的请求和响应完全都是独立的，那么这样是不是就和聊天机器人不能理解上下文非常相似了呢
tags:
- HTTP
- 服务器
- C#
title: 使用C#开发HTTP服务器系列之更简单的实现方式
---

&emsp;&emsp;各位朋友大家好，我是秦元培，欢迎大家关注我的博客，我的博客地址是[http://qinyuanpei.com](http://qinyuanpei.com)。到目前为止，我已经发布了3篇HTTP服务器开发的系列文章。对我个人而言，我非常享受这个从无到有的过程，或许我现在写的这个Web服务器有各种不完美的因素，可是当有一天我需要一个轻量级的服务器的时候，我在无形中是不是比别人多了一种选择呢？我们常常提到“不要重复造轮子”，可事实上这并不能成为我们“不造轮子”的理由，虽然我们有各种各样的服务器软件、有各种各样的服务端框架可以供我们选择，可是在动手写这个系列文章前，我对Web服务器的印象无非是因为我是用LAWP(Linux + Apache + MySQL + PHP)搭建过Wordpress博客而已。虽然在对动态页面(如.aspx、.jsp、.php等)的处理上，可能会和静态页面有所不同，但是我庆幸我了解了这个过程以及它的内部原理，这种跨语言、跨平台的设计思路是任何框架或者标准都无法告诉我的。或许有人会问我，为什么不在最开始的时候就选择更简单的实现方法，那么在这篇文章中你将会找到答案。

<!--more-->
# 从原理说起
&emsp;&emsp;我们知道HTTP服务器其实是一个“服务端循环监听客户端请求然后响应客户端请求”的请求/响应模型，在这个模型中请求通常是由浏览器来发起的，而服务端负责响应客户端的请求。这是我们通常意义上的认识，可是当我们了解到HTTP协议的实质以后就会明白，不管是客户端还是服务端，从本质上来讲都是Socket通信，只要我们能够发送符合HTTP协议规范的报文就可以啦。

&emsp;&emsp;所以我们立刻就能够想到无论是Unity引擎中的WWW还是.NET平台下的WebClient，它们之所以能够向服务器发起请求，无一例外地是它们都遵循了HTTP协议的规范。从这个角度来讲，人类社会存在各种各样的问题，本质上都是存在游离于规范以外的不公平的现象。还记得我们在这个系列中提到的请求报文和响应报文的结构是什么样的吗？此时此刻我们发自内心地向创造HTTP协议的先驱们致敬，因为这个协议我们构建起了连接人与人的社交网络，可是同样因为这个协议我们和人越来越远、和手机越来越近。


&emsp;&emsp;HTTP协议是一种无状态的应用层协议，这个无状态该怎么理解呢？我这里想借助聊天机器人这个实例来解释这个问题，我们都知道聊天机器人是一种问答型的程序，程序每次都可以根据提问者的问题给出，一个从人类角度来看完全合理的答案。然而从目前我了解到的聊天机器人的技术现状来看，具备自然语言理解的机器人程序基本没有，所以在这样的大背景下，机器人程序实际上是没有上下文理解的能力的。

&emsp;&emsp;好了，现在我们回到HTTP协议，首先聊天机器人的问答模式是不是和HTTP协议中的请求/响应模式非常相似呢？其次，我们在设计HTTP服务器的时候，每次在向客户端返回响应报文以后，我们就关闭了Socket连接，这意味着每次的请求和响应完全都是独立的，那么这样是不是就和聊天机器人不能理解上下文非常相似了呢？所以综合下来，我们理解的无状态其实就是说HTTP请求和响应完全独立，即在客户端中不会存储服务端的响应，在服务端中同样不会存储客户端的请求。

&emsp;&emsp;这样难免引发一个问题，如果我需要在不同请求和响应中保持状态该怎么做呢？这个在不同的服务器软件中有不同的技术实现，这里我们说一种最通用的Cookie。Cookie是存储在客户端中的一个数据，在发起下一轮请求时这个参数会被加入到参数列表中然后传递给服务器，服务器会对客户端传递的参数进行验证，以此来判断本轮请求和上轮请求间是否存在上下文联系。

# 两种不同的实现
&emsp;&emsp;到目前为止我们了解的HTTP服务器开发，实际上由两部分组成，即Socket通信和请求-响应模型。基于这两点考虑，我们这里提供两种快速实现Web服务器的具体思路，这是在我们理解了HTTP协议实质以后，从原理出发想到的解决方案，为什么我不建议在刚开始就学习这些东西呢？因为我觉得学习有时候其实就是一个不断开阔视野和思路的过程吧。好了，下面我们来说说这两种不同实现方式的具体思路吧！

## 基于TcpListener/TcpClienr改进Socket

&emsp;&emsp;如果说使用Socket从头开始编写HTTP服务器是一个“刀耕火种”时代的缩影，那么使用TcpListener/TcpClient则是让我们开始进入“青铜铸犁”的农耕时代。和Sokcet相比，TcpListener/TcpClient是.NET对Socket的进一步封装，在这个体系下，TcpListener负责监听和接收传入的连接请求，在该类中仅需要传入一个网络终端信息就可以完成服务端的初始化，而无需设置网络通信协议等细节性的内容。调用Start方法后即可以开始监听，这里我们使用AcceptTcpClient方法来阻塞进程直到接受到一个客户端请求为止，该方法将返回一个TcpClient对象，我们可以借助它完成和客户端的通信。下面我们来一起看基本的代码实现：
```
public void Start()
{
    if(isRunning)
        return;

    //创建TcpListener
    serverListener = new TcpListener(IPAddress.Parse(ServerIP), ServerPort);
    //开始监听
    serverListener.Start(10);
    isRunning = true;

    //输出服务器状态
    Console.WriteLine("Sever is running at http://{0}:{1}/.", ServerIP, ServerPort);

    while(isRunning)
    {
        //获取客户端连接
        TcpClient acceptClient = serverListener.AcceptTcpClient();

        //获取请求报文
        NetworkStream netstream = acceptClient.GetStream();

        //解析请求报文
        byte[] bytes = new byte[1024];
        int length = netstream.Read(bytes, 0, bytes.Length);
        string requestString = Encoding.UTF8.GetString(bytes, 0, length);

        //以下为响应报文(略)
    }
}
```
我个人感觉这种形式和原生的Socket在实现上区别不是非常大，按照这种思路继续往下设计，我的HttpRequest和HttpResponse可能都需要进行改进，因为在我的设计中，我是在尽可能地隐藏Socket通信的细节，因为我不想让使用者觉察到他这是在使用Socket进行通信，这里细心的朋友可能会发现，这里的TcpListener/TcpClient都保留了常见的Socket用法如同步通信和异步通信的支持等，所以在使用cpListener/TcpClient其实没有必要纠结它的这套流程，如果你喜欢继续使用Socket通信的经验和方法就可以了。这里我们仅提供一种延伸思路。具体的代码实现大家顺着这个思路继续下去就好啦。

## 基于HttpListener实现请求-响应模型

&emsp;&emsp;下面我们再来说说基于HttpListener实现请求-响应模型，它和改进Socket不同，它对我们编写一个Web服务器的意义主要体现在它提供了一个非常规范的接口，类似我这里的HttpResponse和HttpRequest以及OnPost、OnGet等接口这些设计。这个让我不喜欢的一点是它在设置服务器IP地址和端口的时候非常别扭，其思路和我的设计是非常相似的，下面我们来一起看代码：

```
public void Listen()
{
    if(!HttpListener.IsSupported)
        throw new InvalidOperationException(
            "请确保使用WindowsXP以上版本的Windows!");

    //初始化Http监听器
    listener = new HttpListener();

    //初始化服务器URL
    string[] prefixes = new string[] { address };
    foreach(string prefix in prefixes)
    {
        listener.Prefixes.Add(prefix);
    }

    //开启服务器
    listener.Start();

    //监听服务器
    while(isActive)
    {
        HttpListenerContext context = listener.GetContext();
        HttpListenerRequest request = context.Request;
        HttpListenerResponse response = context.Response;
        if(request.HttpMethod == "GET"){
            OnGetRequest(request, response);
        }else{
            OnPostRequest(request, response);
        }
    }
}
```
好了，现在这个东西就非常简单了，因为我们只需要继承HttpServerBase这个类然后重写相关方法就可以了，而请求报文和响应报文中的相关属性都在HttpListenerRequest和HttpListenerResponse这两个类中封装好了，我们直接使用就好了。在没有写这个系列文章前，可能我会对这种方案充满好奇，可是当我了解到这一切的实质以后，我反而更加喜欢使用我设计的HTTP服务器了，因为这些东西在我看来区别真的可以忽略。

# One More Thing
&emsp;&emsp;关于今天本文中提到的两种方案，我都是作为HTTP服务器开发延伸出来的内容来写出来给大家看,所以这块儿内容我都是点到为止不打算给出完整的实现，如果有兴趣的朋友可以顺着我这个思路区继续改进。这个系列文章中的示例代码主要来自我的项目[HttpServer](https://github.com/qinyuanpei/HttpServer)，大家到我的GIthub上去了解更多细节。到目前为止我觉得HTTP服务器快发这块儿我能写的内容都基本上写完了，因为是一边写代码一边写博客，所以有时候博客中如果有写得不好或者写的不明白的地方，希望大家能够谅解，同时希望大家在博客中给我积极留言，下一篇我想简单写一下RESTful API的相关问题，写完这一篇整个系列就结束了，我还是想说写文章真的很累啊，希望大家继续支持，下期见。