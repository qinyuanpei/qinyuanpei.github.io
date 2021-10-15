---
abbrlink: 2041685704
categories:
  - 编程语言
date: 2015-03-22 09:37:04
description: 相信大家还记得我们在《C#中 Socket 通信编程的同步实现》这篇文章中使用多线程来实现简单聊天的案例吧，在这个案例中我们需要开启两个线程来不断监听客户端的连接和客户端的消息，这样的效率肯定是很低的;if
  (socket == null || message == string.Empty) return;在 Socket 的异步编程中，服务端不需要为一个客户端单独创建一个线程来维护其连接，可是这样带来的一个问题就是博主不知道该如何实现一个多客户端的异步编程的实例
tags:
  - Socket
  - 异步
  - 通信
  - 编程
title: C#中 Socket 通信编程的异步实现
---

&emsp;&emsp;本文将在 C#中 Socket 同步通信的基础上，分析和研究 Socket 异步编程的实现方法，目的是深入了解 Socket 编程的基本原理，增强对网络游戏开发相关内容的认识。

<!--more-->

# 什么是 Socket 编程的异步的实现
&emsp;&emsp;所谓 Socket 编程的异步实现是指按照异步过程来实现 Socket 编程，那么什么是异步过程呢，我们把在完成了一次调用后通过状态、通知和回调来告知调用者的方式成为异步过程，换句话说，在异步过程中当调用一个方法时，调用者并不能够立刻得到结果，只有当这个方法调用完毕后调用者才能获得调用结果。这样做的好处是什么呢？答案是高效。相信大家还记得我们在《C#中 Socket 通信编程的同步实现》这篇文章中使用多线程来实现简单聊天的案例吧，在这个案例中我们需要开启两个线程来不断监听客户端的连接和客户端的消息，这样的效率肯定是很低的。那么现在好了，我们可以通过异步过程来解决这个问题，下面我们就来看看如何实现 Socket 的异步通信。
# 如何实现 Socket 异步通信
## 服务端
### 基本流程
* 创建套接字
* 绑定套接字的 IP 和端口号——Bind()
* 使套接字处于监听状态等待客户端的连接请求——Listen()
* 当请求到来后，使用 BeginAccept()和 EndAccept()方法接受请求，返回新的套接字
* 使用 BeginSend()/EndSend 和 BeginReceive()/EndReceive()两组方法与客户端进行收发通信
* 返回，再次等待新的连接请求
* 关闭套接字

### 代码示例
```C#
using System;
using System.Collections.Generic;
using System.Text;
using System.Net;
using System.Net.Sockets;

namespace AsyncServer
{
    public class AsyncTCPServer
    {
        public void Start()
        {
            //创建套接字
            IPEndPoint ipe = new IPEndPoint(IPAddress.Parse("127.0.0.1"), 6065);
            Socket socket = new Socket(AddressFamily.InterNetwork, SocketType.Stream, ProtocolType.Tcp);
            //绑定端口和IP
            socket.Bind(ipe);
            //设置监听
            socket.Listen(10);
            //连接客户端
            AsyncAccept(socket);
        }

        /// <summary>
        /// 连接到客户端
        /// </summary>
        /// <param name="socket"></param>
        private void AsyncAccept(Socket socket)
        {
            socket.BeginAccept(asyncResult =>
            {
                //获取客户端套接字
                Socket client = socket.EndAccept(asyncResult);
                Console.WriteLine(string.Format("客户端{0}请求连接...", client.RemoteEndPoint));
                AsyncSend(client, "服务器收到连接请求");
                AsyncSend(client, string.Format("欢迎你{0}",client.RemoteEndPoint));
                AsyncReveive(client);
            }, null);
        }

        /// <summary>
        /// 接收消息
        /// </summary>
        /// <param name="client"></param>
        private void AsyncReveive(Socket socket)
        {
            byte[] data = new byte[1024];
            try
            {
                //开始接收消息
                socket.BeginReceive(data, 0, data.Length, SocketFlags.None,
                asyncResult =>
                {
                    int length = socket.EndReceive(asyncResult);
                    Console.WriteLine(string.Format("客户端发送消息:{0}", Encoding.UTF8.GetString(data)));
                }, null);
            }
            catch (Exception ex)
            {
                Console.WriteLine(ex.Message);
            }
        }

        /// <summary>
        /// 发送消息
        /// </summary>
        /// <param name="client"></param>
        /// <param name="p"></param>
        private void AsyncSend(Socket client, string p)
        {
            if (client == null || p == string.Empty) return;
            //数据转码
            byte[] data = new byte[1024];
            data = Encoding.UTF8.GetBytes(p);
            try
            {
                //开始发送消息
                client.BeginSend(data, 0, data.Length, SocketFlags.None, asyncResult =>
                {
                    //完成消息发送
                    int length = client.EndSend(asyncResult);
                    //输出消息
                    Console.WriteLine(string.Format("服务器发出消息:{0}", p));
                }, null);
            }
            catch (Exception e)
            {
                Console.WriteLine(e.Message);
            }
        }
    }
}
```
## 客户端
### 基本流程
* 创建套接字并保证与服务器的端口一致
* 使用 BeginConnect()和 EndConnect()这组方法向服务端发送连接请求
* 使用 BeginSend()/EndSend 和 BeginReceive()/EndReceive()两组方法与服务端进行收发通信
* 关闭套接字

### 代码示例
```C#
using System;
using System.Collections.Generic;
using System.Text;
using System.Net;
using System.Net.Sockets;

namespace AsyncClient
{
    public class AsyncTCPClient
    {
        /// <summary>
        /// 连接到服务器
        /// </summary>
        public void AsynConnect()
        {
            //端口及IP
            IPEndPoint ipe = new IPEndPoint(IPAddress.Parse("127.0.0.1"), 6065);
            //创建套接字
            Socket client = new Socket(AddressFamily.InterNetwork, SocketType.Stream, ProtocolType.Tcp);
            //开始连接到服务器
            client.BeginConnect(ipe, asyncResult =>
            {
                client.EndConnect(asyncResult);
                //向服务器发送消息
                AsynSend(client,"你好我是客户端");
                AsynSend(client, "第一条消息");
                AsynSend(client, "第二条消息");
                //接受消息
                AsynRecive(client);
            }, null);
        }

        /// <summary>
        /// 发送消息
        /// </summary>
        /// <param name="socket"></param>
        /// <param name="message"></param>
        public void AsynSend(Socket socket, string message)
        {
            if (socket == null || message == string.Empty) return;
            //编码
            byte[] data = Encoding.UTF8.GetBytes(message);
            try
            {
                socket.BeginSend(data, 0, data.Length, SocketFlags.None, asyncResult =>
                {
                    //完成发送消息
                    int length = socket.EndSend(asyncResult);
                    Console.WriteLine(string.Format("客户端发送消息:{0}", message));
                }, null);
            }
            catch (Exception ex)
            {
                Console.WriteLine("异常信息：{0}", ex.Message);
            }
        }

        /// <summary>
        /// 接收消息
        /// </summary>
        /// <param name="socket"></param>
        public void AsynRecive(Socket socket)
        {
            byte[] data = new byte[1024];
            try
            {
                //开始接收数据
                socket.BeginReceive(data, 0, data.Length, SocketFlags.None,
                asyncResult =>
                {
                    int length = socket.EndReceive(asyncResult);
                    Console.WriteLine(string.Format("收到服务器消息:{0}", Encoding.UTF8.GetString(data)));
                    AsynRecive(socket);
                }, null);
            }
            catch (Exception ex)
            {
                Console.WriteLine("异常信息：", ex.Message);
            }
        }
    }
}

```
从总体上来讲 Socket 异步编程的逻辑性更加明确了，因为我们只需要为每一个过程写好回调函数就好了。那么这个示例的效果如何呢？我们来看看它的演示效果：

![Socket异步编程效果演示](https://ww1.sinaimg.cn/large/4c36074fly1fyzctofo6zj211y0lcdi3.jpg)

# 总结
&emsp;&emsp;和 Socket 同步编程的案例相比，今天的这个案例可能只是对 Socket 异步编程内容的一个简单应用，因为博主到现在为止都还没有写出一个可以进行交互聊天的程序来。在 Socket 的异步编程中，服务端不需要为一个客户端单独创建一个线程来维护其连接，可是这样带来的一个问题就是博主不知道该如何实现一个多客户端的异步编程的实例。如果有朋友知道如何实现的话，还希望能够告诉我，毕竟学习就是一个相互促进的过程啊。好了，最后想说的是博主这段时间研究 Socket 异步编程中关于异步方法调用的写法问题。我们知道 Socket 异步编程中的方法是成对出现的，每一个方法都有一个回调函数，对于回调函数，这里有两种写法，以 BeginConnect 方法为例：
```C#
m_Socket.BeginConnect(this.m_ipEndPoint, 
        new AsyncCallback(this.ConnectCallBack), 
        this.m_Socket);//其中ConnectCallBack是一个回调函数
```
或者
```C#
m_Socket.BeginConnect(this.m_ipEndPoint,asyncResult=>
{
    //在这里添加更多代码
},null)
```
&emsp;&emsp;博主为什么要在这里说这两种写法呢，有两个原因：
* 第二种写法更为简洁，无需去构造容器传递 Socket 和消息，因为它们都是局部变量。如果我们使用第一种方法，因为主函数和回调函数是两个不同的函数，因此如果想要共享变量就需要通过 IAsyncResult 接口来访问容器中的值，这样显然增加了我们的工作量。
* 第二种写法更为优雅，这似乎是 C#语言中某种高级语法，具体叫什么我忘了，反正在 Linq 中经常看到这种写法的影子。

&emsp;&emsp;综合以上两个观点，博主还是建议大家使用第二种写法，博主打算有空的话将之前写的程序再重新写一遍，看看能不能找出代码中的问题。好了，今天的内容就是这样了，谢谢大家，希望大家喜欢！