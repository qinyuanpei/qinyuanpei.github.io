---
title: 'C#中Socket通信编程的同步实现'
categories:
  - 编程语言
tags:
  - Socket
  - 通信
  - 同步
  - 多线程
abbrlink: 3959327595
date: 2015-03-15 15:05:56
---
&emsp;&emsp;本文通过分析和总结C#中Socket通信编程的关键技术，按照同步实现的方式实现了一个简单的Socket聊天程序，目的是通过这个程序来掌握Socket编程，为进一步开发Unity3D网络游戏打下一个坚实的基础。

<!--more-->

# Socket编程基础
&emsp;&emsp;关于Socket编程基础部分的内容，主要是了解和掌握.NET框架下为Socket编程提供的相关类和接口方法。.NET中常见的网络相关的API都集中在System.Net和System.Net.Socket这两个命名空间下，大家可以通过MSDN去了解这两个命名空间下相关的类和方法。这里援引一位朋友总结的一篇文章[http://www.cnblogs.com/sunev/archive/2012/08/05/2604189.html](http://www.cnblogs.com/sunev/archive/2012/08/05/2604189.html)，大家可以从这里获得更为直观的认识。

# 什么是Socket编程的同步实现
&emsp;&emsp;本文的目的是按照同步实现的方式来实现一个简单的Socket聊天程序，因此在解决这个问题前，我们首先来看看什么是Socket编程的同步实现。所谓Socket编程的同步实现就是指按照同步过程的方法来实现Socket通信。从编程来说，我们常用的方法或者函数都是同步过程。因为当我们调用一个方法或者函数的时候我们能够立即得到它的返回值。可是我们知道在Socket通信中，我们不能保证时时刻刻连接都通畅、更不能够保证时时刻刻都有数据收发，因为我们就需要不断去读取相应的值来确定整个过程的状态。这就是Socket编程的同步实现了，下面我们来看具体的实现过程。

# 如何实现Socket同步通信
## 服务端
&emsp;&emsp;服务端的主要职责是处理各个客户端发送来的数据，因此在客户端的Socket编程中需要使用两个线程来循环处理客户端的请求，一个线程用于监听客户端的连接情况，一个线程用于监听客户端的消息发送，当服务端接收到客户端的消息后需要将消息处理后再分发给各个客户端。
### 基本流程
* 创建套接字
* 绑定套接字的IP和端口号——Bind()
* 将套接字处于监听状态等待客户端的连接请求——Listen()
* 当请求到来后，接受请求并返回本次会话的套接字——Accept()
* 使用返回的套接字和客户端通信——Send()/Receive()
* 返回，再次等待新的连接请求
* 关闭套接字

### 代码示例
```C#
using System;
using System.Collections.Generic;
using System.Text;
using System.Net;
using System.Net.Sockets;
using System.Threading;

namespace TCPLib
{
    public class TCPServer
    {
        private byte[] result = new byte[1024];
        /// <summary>
        /// 最大的监听数量
        /// </summary>
        private int maxClientCount;
        public int MaxClientCount
        {
            get { return maxClientCount; }
            set { maxClientCount = value; }
        }

        /// <summary>
        /// IP地址
        /// </summary>
        private string ip;
        public string IP
        {
            get { return ip; }
            set { ip = value; }
        }

        /// <summary>
        /// 端口号
        /// </summary>
        private int port;
        public int Port
        {
            get { return port; }
            set { port = value; }
        }

        /// <summary>
        /// 客户端列表
        /// </summary>
        private List<Socket> mClientSockets;
        public List<Socket> ClientSockets
        {
            get { return mClientSockets; }
        }

        /// <summary>
        /// IP终端
        /// </summary>
        private IPEndPoint ipEndPoint;

        /// <summary>
        /// 服务端Socket
        /// </summary>
        private Socket mServerSocket;

        /// <summary>
        /// 当前客户端Socket
        /// </summary>
        private Socket mClientSocket;
        public Socket ClientSocket 
        {
            get { return mClientSocket;  }
            set { mClientSocket = value; }
        }

        /// <summary>
        /// 构造函数
        /// </summary>
        /// <param name="port">端口号</param>
        /// <param name="count">监听的最大树目</param>
        public TCPServer(int port, int count)
        {
            this.ip = IPAddress.Any.ToString();
            this.port = port;
            this.maxClientCount=count;

            this.mClientSockets = new List<Socket>();

            //初始化IP终端
            this.ipEndPoint = new IPEndPoint(IPAddress.Any, port);
            //初始化服务端Socket
            this.mServerSocket = new Socket(AddressFamily.InterNetwork, SocketType.Stream, ProtocolType.Tcp);
            //端口绑定
            this.mServerSocket.Bind(this.ipEndPoint);
            //设置监听数目
            this.mServerSocket.Listen(maxClientCount);
        }

        /// <summary>
        /// 构造函数
        /// </summary>
        /// <param name="ip">ip地址</param>
        /// <param name="port">端口号</param>
        /// <param name="count">监听的最大数目</param>
        public TCPServer(string ip,int port,int count)
        {
            this.ip = ip;
            this.port = port;
            this.maxClientCount = count;

            this.mClientSockets = new List<Socket>();

            //初始化IP终端
            this.ipEndPoint = new IPEndPoint(IPAddress.Parse(ip), port);
            //初始化服务端Socket
            this.mServerSocket = new Socket(AddressFamily.InterNetwork, SocketType.Stream, ProtocolType.Tcp);
            //端口绑定
            this.mServerSocket.Bind(this.ipEndPoint);
            //设置监听数目
            this.mServerSocket.Listen(maxClientCount);

        }

        /// <summary>
        /// 定义一个Start方法将构造函数中的方法分离出来
        /// </summary>
        public void Start()
        {
            //创建服务端线程，实现客户端连接请求的循环监听
            var mServerThread = new Thread(this.ListenClientConnect);
            //服务端线程开启
            mServerThread.Start();
        }

        /// <summary>
        /// 监听客户端链接
        /// </summary>
        private void ListenClientConnect()
        {
            //设置循环标志位
            bool flag = true;
            while (flag)
            {
                //获取连接到服务端的客户端
                this.ClientSocket = this.mServerSocket.Accept();
                //将获取到的客户端添加到客户端列表
                this.mClientSockets.Add(this.ClientSocket);
                //向客户端发送一条消息
                this.SendMessage(string.Format("客户端{0}已成功连接到服务器", this.ClientSocket.RemoteEndPoint));
                //创建客户端消息线程，实现客户端消息的循环监听
                var mReveiveThread = new Thread(this.ReceiveClient);
                //注意到ReceiveClient方法传入了一个参数
                //实际上这个参数就是此时连接到服务器的客户端
                //即ClientSocket
                mReveiveThread.Start(this.ClientSocket);
            }
        }

        /// <summary>
        /// 接收客户端消息的方法
        /// </summary>
        private void ReceiveClient(object obj)
        {
            //获取当前客户端
            //因为每次发送消息的可能并不是同一个客户端，所以需要使用var来实例化一个新的对象
            //可是我感觉这里用局部变量更好一点
            var mClientSocket = (Socket)obj;
            // 循环标志位
            bool flag = true;
            while (flag)
            {
                try
                {
                    //获取数据长度
                    int receiveLength = mClientSocket.Receive(result);
                    //获取客户端消息
                    string clientMessage = Encoding.UTF8.GetString(result, 0, receiveLength);
                    //服务端负责将客户端的消息分发给各个客户端
                    this.SendMessage(string.Format("客户端{0}发来消息:{1}",mClientSocket.RemoteEndPoint,clientMessage));

                }
                catch (Exception e)
                {
                    //从客户端列表中移除该客户端
                    this.mClientSockets.Remove(mClientSocket);
                    //向其它客户端告知该客户端下线
                    this.SendMessage(string.Format("服务器发来消息:客户端{0}从服务器断开,断开原因:{1}",mClientSocket.RemoteEndPoint,e.Message));
                    //断开连接
                    mClientSocket.Shutdown(SocketShutdown.Both);
                    mClientSocket.Close();
                    break;
                }
            }
            
        }

        /// <summary>
        /// 向所有的客户端群发消息
        /// </summary>
        /// <param name="msg">message</param>
        public void SendMessage(string msg)
        {
            //确保消息非空以及客户端列表非空
            if (msg == string.Empty || this.mClientSockets.Count <= 0) return;
            //向每一个客户端发送消息
            foreach (Socket s in this.mClientSockets)
            {
                (s as Socket).Send(Encoding.UTF8.GetBytes(msg));
            }
        }

        /// <summary>
        /// 向指定的客户端发送消息
        /// </summary>
        /// <param name="ip">ip</param>
        /// <param name="port">port</param>
        /// <param name="msg">message</param>
        public void SendMessage(string ip,int port,string msg)
        {
            //构造出一个终端地址
            IPEndPoint _IPEndPoint = new IPEndPoint(IPAddress.Parse(ip), port);
            //遍历所有客户端
            foreach (Socket s in mClientSockets)
            {
                if (_IPEndPoint == (IPEndPoint)s.RemoteEndPoint)
                {
                    s.Send(Encoding.UTF8.GetBytes(msg));
                }
            }
        }
    }
}
```
&emsp;&emsp;好了，现在我们已经编写好了一个具备接收和发送数据能力的服务端程序。现在我们来尝试让服务端运行起来：
```C#
using System;
using System.Collections.Generic;
using System.Text;
using TCPLib;
using System.Net;
using System.Net.Sockets;

namespace TCPLib.Test
{
    class Program
    {
        static void Main(string[] args)
        {
            //指定IP和端口号及最大监听数目的方式
            TCPLib.TCPServer s1 = new TCPServer("127.0.0.1", 6001, 10);
            //指定端口号及最大监听数目的方式
            TCPLib.TCPServer s2 = new TCPServer(6001, 10);
           
            //执行Start方法
            s1.Start();
        
        }
    }

}
```

&emsp;&emsp;现在我们来看看编写客户端Socket程序的基本流程
## 客户端
&emsp;&emsp;客户端相对于服务端来说任务要轻许多，因为客户端仅仅需要和服务端通信即可，可是因为在和服务器通信的过程中，需要时刻保持连接通畅，因此同样需要两个线程来分别处理连接情况的监听和消息发送的监听。
### 基本流程
* 创建套接字保证与服务器的端口一致
* 向服务器发出连接请求——Connect()
* 和服务器端进行通信——Send()/Receive()
* 关闭套接字

### 代码示例
```C#
using System;
using System.Collections.Generic;
using System.Text;
using System.Net;
using System.Net.Sockets;
using System.Threading;

namespace TCPLib
{
    public class TCPClient
    {
        /// <summary>
        /// 定义数据
        /// </summary>
        private byte[] result = new byte[1024];

        /// <summary>
        /// 客户端IP
        /// </summary>
        private string ip;
        public string IP
        {
            get { return ip; }
            set { ip = value; }
        }

        /// <summary>
        /// 客户端端口号
        /// </summary>
        private int port;
        public int Port
        {
            get { return port; }
            set { port = value; }
        }

        /// <summary>
        /// IP终端
        /// </summary>
        private IPEndPoint ipEndPoint;

        /// <summary>
        /// 客户端Socket
        /// </summary>
        private Socket mClientSocket;

        /// <summary>
        /// 是否连接到了服务器
        /// 默认为flase
        /// </summary>
        private bool isConnected = false;

        /// <summary>
        /// 构造函数
        /// </summary>
        /// <param name="ip">IP地址</param>
        /// <param name="port">端口号</param>
        public TCPClient(string ip, int port)
        {
            this.ip=ip;
            this.port=port;
            //初始化IP终端
            this.ipEndPoint = new IPEndPoint(IPAddress.Parse(this.ip), this.port);
            //初始化客户端Socket
            mClientSocket = new Socket(AddressFamily.InterNetwork, SocketType.Stream, ProtocolType.Tcp);

        }

        public void Start()
        {
            //创建一个线程以不断连接服务器
            var mConnectThread = new Thread(this.ConnectToServer);
            //开启线程
            mConnectThread.Start();
        }

        /// <summary>
        /// 连接到服务器
        /// </summary>
        private void ConnectToServer()
        {
            //当没有连接到服务器时开始连接
            while (!isConnected)
            {
                try
                {
                    //开始连接
                    mClientSocket.Connect(this.ipEndPoint);
                    this.isConnected = true;
                }
                catch (Exception e)
                {
                    //输出Debug信息
                    Console.WriteLine(string.Format("因为一个错误的发生，暂时无法连接到服务器，错误信息为:{0}",e.Message));
                    this.isConnected = false;
                }

                //等待5秒钟后尝试再次连接
                Thread.Sleep(5000);
                Console.WriteLine("正在尝试重新连接...");
            }

            //连接成功后
            Console.WriteLine("连接服务器成功，现在可以和服务器进行会话了");
            //创建一个线程以监听数据接收
            var mReceiveThread = new Thread(this.ReceiveMessage);
            //开启线程
            mReceiveThread.Start();
        }

        /// <summary>
        /// 因为客户端只接受来自服务器的数据
        /// 因此这个方法中不需要参数
        /// </summary>
        private void ReceiveMessage()
        {
            //设置循环标志位
            bool flag = true;
            while (flag)
            {
                try
                {
                    //获取数据长度
                    int receiveLength = this.mClientSocket.Receive(result);
                    //获取服务器消息
                    string serverMessage = Encoding.UTF8.GetString(result, 0, receiveLength);
                    //输出服务器消息
                    Console.WriteLine(serverMessage);
                }
                catch (Exception e)
                {
                    //停止消息接收
                    flag = false;
                    //断开服务器
                    this.mClientSocket.Shutdown(SocketShutdown.Both);
                    //关闭套接字
                    this.mClientSocket.Close();

                    //重新尝试连接服务器
                    this.isConnected = false;
                    ConnectToServer();
                }
            }
            
        }

        /// <summary>
        /// 发送消息
        /// </summary>
        /// <param name="msg">消息文本</param>
        public void SendMessage(string msg)
        {
            if(msg==string.Empty || this.mClientSocket==null) return;

            mClientSocket.Send(Encoding.UTF8.GetBytes(msg));
        }
    }
}
```
&emsp;&emsp;同样地，我们现在来运行客户端程序，这样客户端就可以和服务端进行通信了：
```C#
using System;
using System.Collections.Generic;
using System.Text;
using TCPLib;
using System.Net;
using System.Net.Sockets;

namespace TCPLib.Test
{
    class Program
    {
        static void Main(string[] args)
        {
            //保证端口号和服务端一致
            TCPLib.TCPClient c = new TCPClient("127.0.0.1",6001);
            //执行Start方法
            c.Start();
            while(true)
            {
                //读取客户端输入的消息
                string msg = Console.ReadLine();
                //发送消息到服务端
                c.SendMessage(msg);
            }
        
        }
    }

}
```
&emsp;&emsp;注意要先运行服务端的程序、再运行客户端的程序，不然程序会报错，嘿嘿！好了，下面是今天的效果演示图：

![聊天窗口效果演示](http://7wy477.com1.z0.glb.clouddn.com/qinyuanpei_imgs_聊天窗口演示.png)

![客户端下线效果演示](http://7wy477.com1.z0.glb.clouddn.com/qinyuanpei_imgs_客户端下线后聊天窗口演示.png)

# 总结
&emsp;&emsp;今天我们基本上写出了一个可以使用的用例，不过这个例子目前还存在以下问题：
* 这里仅仅实现了发送字符串的功能，如何让这个程序支持更多的类型，从基础的int、float、double、string、single等类型到structure、class甚至是二进制文件的类型？
* 如何让这个用例更具有扩展性，我们发现所有的Socket编程流程都是一样的，唯一不同就是在接收到数据以后该如何去处理，因为能不能将核心功能和自定义功能分离开来？

* 在今天的这个用例中，数据传输的缓冲区大小我们人为设定为1024，那么如果碰到比这个设定更大的数据类型，这个用例该怎么来写？

好了，这就是今天的内容了，希望大家喜欢，同时希望大家关注我的博客！

**2016年1月24日更新**：
&emsp;&emsp;要解决“支持更多类型的问题”，可以从两种思路来考虑，即实现所有类型到byte[]类型的转换或者是实现所有类型到string类型的转换，对于第二种思路我们通常称之为序列化，序列化可以解决所有类型到string类型的转换问题，唯一可能需要考量的一个部分就是缓冲区的大小问题。

&emsp;&emsp;要解决“将核心功能和自定义功能分离”这个问题，可以考虑使用委托机制来实现，委托机制可以理解为一个函数的指针，在需要将函数的控制权交给用户来处理的场景中，委托都是一种有效而明智的选择。