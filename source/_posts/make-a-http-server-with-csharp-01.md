title: 使用C#开发HTTP服务器系列之Hello World
date: 2016-06-11 12:38:03
categories: [编程语言]
tags: [HTTP,服务器,C#]
---
&emsp;&emsp;各位朋友大家好，我是秦元培，欢迎大家关注我的博客。从今天起，我将开始撰写一组关于HTTP服务器开发的系列文章。我为什么会有这样的想法呢？因为人们对Web技术存在误解，认为网站开发是Web技术的全部。其实在今天这样一个时代，Web技术可谓是无处不在，无论是传统软件开发还是移动应用开发都离不开Web技术，所以在我的认识中，任何使用了HTTP协议实现数据交互都可以认为是Web技术的一种体现，而且当我们提及服务器开发的时候，我们常常提及Java或者PHP。可是这些重要吗？不，在我看来服务器开发和语言无关，和IIS、Tomcat、Apache、Ngnix等等我们熟知的服务器软件无关。Web技术可以像一个网站一样通过浏览器来访问，同样可以像一个服务一样通过程序来调用，所以在接下来的时间里，我将和大家一起见证如何使用C#开发一个基本的HTTP服务器，希望通过这些能够让大家更好的认识Web技术。

<!--more-->
# 至繁至简的HTTP
&emsp;&emsp;我们对HTTP协议最直观的认识应该是来自浏览器，因为在互联网时代我们都是通过浏览器这个入口来接触互联网的，而到了移动互联网时代我们开始思考新的互联网入口。在这个过程中我们有创新的模式不断涌现出来，同样有并购、捆绑、垄断等形式的恶性竞争此起彼伏，所谓“痛并快乐着”。我想说的是，HTTP是一个简单与复杂并存的东西，那么什么是HTTP呢？我们在浏览器中输入URL的时候，早已任性地连“http”和“www”都省略了吧，所以我相信HTTP对人们来说依然是一个陌生的东西。

&emsp;&emsp;HTTP是超文本传输协议(HyperText Transfer Protocol)的简称，它建立在C/S架构的应用层协议，熟悉这部分内容的朋友应该清楚，TCP/IP协议是协议层的内容，它定义了计算机间通信的基础协议，我们熟悉的HTTP、FTP、Telnet等协议都是建立在TCP/IP协议基础上的。在HTTP协议中，客户端负责发起一个Request，该Request中含有请求方法、URL、协议版本等信息，服务端在接受到该Request后会返回一个Response，该Response中含有状态码、响应内容等信息，这一模型称为请求/响应模型。HTTP协议迄今为止发展出3个版本：

* 0.9版本：已过时。该版本仅支持GET一种请求方法，不支持请求头。因为不支持POST方法，所以客户端无法向服务器传递太多信息。
* HTTP/1.0版本：这是第一个在通讯中指定版本号的HTTP协议版本，至今依然被广泛采用，特别是在代理服务器中。
* HTTP/1.1版本：目前采用的版本。持久连接被默认采用，并能很好地配合代理服务器工作。相对1.0版本，该版本在缓存处理、带宽优化及网络连接地使用、错误通知地管理、消息在网络中的发送等方面都有显著的区别。

&emsp;&emsp;HTTP协议通信的核心是HTTP报文，根据报文发送者的不同，我们将其分为请求报文和响应报文。其中，由客户端发出的HTTP报文称为请求报文，由服务端发出的报文称为响应报文。下面我们来着重了解和认识这两种不同的报文：

* 请求报文：请求报文通常由浏览器来发起，当我们访问一个网页或者请求一个资源的时候都会产生请求报文。请求报文通常由HTTP请求行、请求头、消息体(可选)三部分组成，服务端在接收到请求报文后根据请求报文请求返回数据给客户端，所以我们通常讲的服务端开发实际上是指在服务端接收到信息以后处理的这个阶段。下面是一个基本的请求报文示例：
```
/* HTTP请求行 */
GET / HTTP/1.1
/* 请求头部 */
Accept: text/html, application/xhtml+xml, image/jxr, */*
Accept-Encoding: gzip, deflate
Accept-Language: zh-Hans-CN, zh-Hans; q=0.5
Connection: Keep-Alive
Host: localhost:4000
User-Agent: Mozilla/5.0 (Windows NT 10.0; Trident/7.0; rv:11.0) like Gecko

/* 消息体 */
```

* 响应报文：响应报文是指在服务端接收并处理了客户端的请求信息以后，服务端发送给客户端的HTTP报文，服务端开发的重要工作就是处理来自客户端的请求，所以这是我们开发一个HTTP服务器的核心工作。和请求报文类似，响应报文由HTTP状态行、响应头、消息体(可选)三部分组成。例如我们通常熟悉的200和404分别表示连接正常和无法访问资源这两种响应状态。下面是一个基本的响应报文示例：
```
/* HTTP状态行 */
HTTP/1.1 200 OK
/* 响应头部 */
Content-Type: text/html;charset=utf-8
Connection: keep-alive
Server: Microsoft-IIS/7.0
Date: Sun, 12 Jun 2016 11:00:42 GMT
X-Powered-By: Hexo

/* 消息体 */
```

&emsp;&emsp;这里需要说明的是，实际的请求报文和响应报文会因为服务端设计的不同，和这里的报文示例略有不同，报文中头部信息参数种类比较多，我不打算在这里详细解释每个参数的含义，我们只需要对报文格式有一个基本的认识即可，想了解这些内容的朋友可以阅读[这里](http://www.cnblogs.com/xly1208/archive/2011/10/12/2208468.html)。在请求报文中我们注意到第一行，即HTTP请求行指明当前请求的方法。所以下面我们来说说HTTP协议的基本请求方法。常见的方法有GET、POST、HEAD、DELETE、OPTIONS、TRACE、CONNECT，我们这里选取最常用的两种方式，即GET和PSOT来讲解：

* GET：最为常见的一种请示方式。当客户端从服务器读取文档或者通过一个链接来访问页面的时候，都是采用GET方式来请求的。GET请求的一个显著标志是其请求参数附加在URL后，例如"/index.jsp?id=100&option=bind"这种形式即为GET方式请求。GET方式对用户而言，传递参数过程是透明的，因为用户可以通过浏览器地址栏直接看到参数，所以这种方式更适合用来设计API，即在不需要验证身份或者对安全性要求不高的场合，需要注意的是GET方式请求对参数长度由一定限制。
* POST：POST克服了GET方式对参数长度存在限制的缺点，以键-值形式将参数封装在HTTP请求中，所以从理论上讲它对参数长度没有限制(实际上会因为浏览器和操作系统的限制而大打折扣)，而且对用户来讲参数传递过程是不可见的，所以它是一种相对安全的参数传递方式。通常用户登录都会采取这种方式，我们在编写爬虫的时候遇到需要登录的情况通常都需要使用POST方式进行模拟登录。

#Socket与HTTP的紧密联系
&emsp;&emsp;到目前为止，我们基本上搞清楚了HTTP是如何运作的，这恰恰符合普通人对技术的认知水平，或许在普通人看起来非常简单的东西，对技术人员来讲永远都是复杂而深奥的，所以从这个角度来讲，我觉的我们更应该向技术人员致敬，因为是技术人员让这些经过其简化以后的复杂流程以一种产品的形态走进了你我的生活，感谢有技术和技术人员的存在，让我们这个世界更加美好。好了，现在我们来思考这样一个问题，Socket和HTTP有一种怎样的关联？这是因为我们目前所有对HTTP的理解都是一种形而上学上的理解，它现在仅仅是一种协议，可是协议离真正的应用很遥远不是吗？所以我们需要考虑如何去实现这样一种协议。我们注意到HTTP是建立在TCP/IP协议上的，所以HTTP的协议应该考虑用TCP/IP协议的实现来实现，考虑到Socket是TCP/IP协议的一种实现，所以我们非常容易地想到应该用Socket来构建一个HTTP服务器，由此我们找到了Socket和HTTP的紧密联系。

&emsp;&emsp;在找到Socket和HTTP的紧密联系以后，我们现在就可以开始着手来设计一个HTTP服务器了。我们的思路是这样的，首先我们在服务端创建一个Socket来负责监听客户端连接。每次客户端发出请求后，我们根据请问报文来判断客户端的请求类型，然后根据不同的请求类型进行相应的处理，这样我们就设计了一个基本的HTTP服务器。

# 从头开始设计HTTP服务器
&emsp;&emsp;好了，现在我们要开始从头设计一个HTTP服务器了，在此之前，我们首先来为整个项目设计下面的基本约束。我一直非常好奇为什么有的开发者会如此强烈地依赖框架。尤其是在Web开发领域，MVC和MVVM基本上是耳熟能详到烂俗的词汇。我个人更加认同这是一种思想。什么是思想呢？思想是你知道其绝妙处而绝口不提，却在潜移默化中心领神会的运行它。可事实上是什么样呢？无数开发者被框架所禁锢，因为我们缺少了犯错的机会。所以我在这里不想再提及Java、PHP、.NET在Web开发领域里那些广为人知的框架，因为我认为忘掉这些框架可以帮助我们更好的理解框架，下面我就来用我的这种方法告诉大家什么叫做MVC？

&emsp;&emsp;什么叫做MVC？我们都知道MVC由模型、视图、控制器三部分组成，可是它们的实质是什么呢？我想这个问题可能没有人想过，因为我们的时间都浪费在配置XML文档节点上。(我说的就是Java里的配置狂魔)

&emsp;&emsp;首先，模型是什么呢？模型对程序员而言可以是一个实体类，亦可以是一张数据表，而这两种认知仅仅是因为我们看待问题的角度不同而已，为了让这两种认知模型统一，我们想到了ORM、想到了根据数据表生成实体类、想到了在实体类中使用各种语法糖，而这些在我看来非常无聊的东西，竟然可以让我们不厌其烦地制造出各种框架，对程序员而言我还是喜欢理解为实体类。

&emsp;&emsp;其次，视图是什么呢？视图在我看来是一个函数，它返回的是一个HTML结构的文本，而它的参数是一个模型，一个经过我们实例化以后的对象，所以控制器所做的工作无非是从数据库中获取数据，然后将其转化为实体对象，再传递给视图进行绑定而已。这样听起来，我们对MVC的理解是不是就清晰了？而现在前端领域兴起的Vue.js和React，从本质上来讲是在纠结控制器的这部分工作该有前端来完成还是该有后端来完成而已。

&emsp;&emsp;MVC中有一个路由的概念，这个概念我们可以和HTTP中请求行来对应起来，我们知道发出一个HTTP请求的时候，我们能够从请求报文中获得请求方法、请求地址、请求参数等一系列信息，服务器正是根据这些信息来处理客户端请求的。那么，路由到底是什么呢？路由就是这里的请求地址，它可以是实际的文件目录、可以是虚拟化的Web API、可以是项目中的文件目录，而一切的一切都在于我们如何定义路由，例如我们定义的路由是"[http://www.zhihu.com/people/vczh](http://www.zhihu.com/people/vczh)"，从某种意义上来讲，它和"[http://www.zhihu.com/people/?id=vczh](http://www.zhihu.com/people/?id=vczh)"是一样的，因为服务器总是能够一眼看出这些语法糖的区别。

&emsp;&emsp;虽然我在竭尽全力地避免形成对框架的依赖，可是在设计一个项目的时候，我们依然需要做些宏观上的规划，我设计的一个原则就是简单、轻量，我不喜欢重度产品，我喜欢小而美的东西，就像我喜欢C#这门语言而不喜欢ASP.NET一样，因为我喜欢Nancy这个名字挺起来文艺而使用起来简单、开心的东西。我不会像某语言一样丧心病狂地使用接口和抽象类的，在我这里整体设计是非常简单的：
* IServer.cs：定义服务器接口，该接口定义了OnGet()、OnPost()、OnDefault()、OnListFiles()四个方法，分别用来响应GET请求、响应POST请求、响应默认请求、列取目录，我们这里的服务器类HttpServer需要实现该接口。
* Request.cs：封装来自客户端的请求报文继承自BaseHeader。
* Response.cs：封装来自服务端的响应报文继承自BaseHeader。
* BaseHeader.cs: 封装通用头部和实体头部。
* HttpServer.cs: HTTP服务器基类需实现IServer接口。

&emsp;&emsp;因为我这里希望实现的是一种全局上由我来控制，细节上由你来决定的面向开发者的设计思路，这和通常的面向大众的产品思路是完全不同的。例如委托或者事件的一个重要意义就是，它可以让程序按照设计者的思路来运行，同时满足使用着在细节上的控制权。所以，在写完这个项目以后，我们就可以无需再关注客户端和服务端如何通信这些细节，而将更多的精力放在服务器接收到了什么、如何处理、怎样返回这样的问题上来，这和框架希望我们将精力放在业务上的初衷是一样的，可是事实上关注业务对开发者来讲是趋害的，对公司来讲则是趋利的。当你发现你因为熟悉了业务而逐渐沦落为框架填充者的时候，你有足够的理由来唤起内心想要控制一切的欲望。世界很大、人生很短，这本来就是一个矛盾的存在，当我们习惯在框架中填充代码的时候，你是否会想到人生本来没有这样的一个框架？

&emsp;&emsp;好了，现在我们来开始编写这个Web服务器中通信的基础部分。首先我们需要创建一个服务端Socket来监听客户端的请求。如果你熟悉Socket开发，你将期望看到下面这样的代码：

```
/// <summary>
/// 开启服务器
/// </summary>
public void Start()
{
    if(isRunning)
        return;

    //创建服务端Socket
    serverSocket = new Socket(AddressFamily.InterNetwork, SocketType.Stream, ProtocolType.Tcp);
    serverSocket.Bind(new IPEndPoint(IPAddress.Parse(ServerIP), ServerPort));
    serverSocket.Listen(10);
    isRunning = true;

    //输出服务器状态
    Console.WriteLine("Sever is running at http://{0}:{1}/.", ServerIP, ServerPort);

    //连接客户端
    while(isRunning)
    {
        Socket clientSocket = serverSocket.Accept();
        Thread requestThread = new Thread(() =>{ ProcessRequest(clientSocket);});
        requestThread.Start();
    }
}
```
这里我们使用isRunning来表示服务器是否运行，显然当服务器处在运行状态时，它应该返回。我们这里使用ServerIP和ServerPort分别表示服务端IP和端口，创建服务端Socket这里就不再赘述了，因为这是非常简单而基础的东西。当服务器处在运行状态时我们接受一个客户端请求，并使用一个独立的线程来处理请求，客户端请求的处理我们这里提供了一个叫做ProcessRequest的方法，它具体都做了什么工作呢？我们继续往下看：

```
/// <summary>
/// 处理客户端请求
/// </summary>
/// <param name="handler">客户端Socket</param>
private void ProcessRequest(Socket handler)
{
    //构造请求报文
    HttpRequest request = new HttpRequest(handler);

    //根据请求类型进行处理
    if(request.Method == "GET"){
        OnGet(request);
    }else if(request.Method == "POST"){
        OnPost(request);
    }else{
        OnDefault();
    }
}
```

接下来我们可以注意到我们这里根据客户端Soket构造了一个请求报文，其实就是在请求报文的构造函数中通过解析客户端发来的消息，然后将其和我们这里定义的HttpRequest类对应起来。我们这里可以看到，根据请求方法的不同，我们这里分别采用OnGet、OnPost和OnDefault三个方法进行处理，而这些是定义在IServer接口中并在HttpServer类中声明为虚方法。严格来讲，这里应该有更多的请求方法类型，可是因为我这里写系列文章的关系，我想目前暂时就实现Get和Post两种方法，所以这里大家如果感兴趣的话可以做更深层次的研究。所以，现在我们就明白了，因为这些方法都被声明为虚方法，所以我们只需要HttpServer类的子类中重写这些方法就可以了嘛，这好像离我最初的设想越来越近了呢。关于请求报文的构造，大家可以到[http://github.com/qinyuanpei/HttpServer/](http://github.com/qinyuanpei/HttpServer/)中来了解，实际的工作就是解析字符串而已，这些微小的工作实在不值得在这里单独来讲。

&emsp;&emsp;我们今天的正事儿是什么呢？是Hello World啊，所以我们需要想办法让这个服务器给我们返回点什么啊，接下来我们继承HttpServer类来写一个具体的类MyServer，和期望的一样，我们仅仅需要重写相关方法就可以写一个基本的Web服务器，需要注意的是子类需要继承父类的构造函数。我们一起来看代码：

```
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.IO;

namespace HttpServerLib
{
    public class MyServer : HttpServer
    {
        public MyServer(string ipAddress, int port)
            : base(ipAddress, port)
        {

        }

        public override void OnGet(HttpRequest request)
        {
            HttpResponse response = new HttpResponse("<html><body><h1>Hello World</h1></body></html>", Encoding.UTF8);
            response.StatusCode = "200";
            response.Server = "A Simple HTTP Server";
            response.Content_Type = "text/html";
            ProcessResponse(request.Handler, response);
        }
    }
}
```


可以注意到我们这里构造了一个HttpResponse，这是我这里定义的HTTP响应报文，我们这里响应的内容是一段简单的HTML采用UTF-8编码。在构造完HttpResponse以后我们设定了它的相关状态，熟悉Web开发的朋友应该可以想到这是抓包工具抓包时得到的服务端报文信息，最近博主最喜欢的某个妹子写真集网站开始反爬虫了，因此博主以前写的Python脚本现在执行会被告知403，这是一个禁止访问的状态码。解决方案其实非常简单地，将HTTP请求伪装成一个“浏览器”即可，思路就是在HTTP请求报文中增加相关字段，这样就可以“骗”过服务器，当然更深层次的“欺骗”就是Cookie和Session级别的伪装了，这个话题我们有时间再说。这里我们设定状态码为200，这是一个正常的请求，其次ContentType等字段可以自行阅读HTTP协议中头部字段的相关资料，最后我们通过ProcessResponse这个方法来处理响应，其内部是一个使用Socket发送消息的基本实现，详细的设计细节大家可以看项目代码。

&emsp;&emsp;现在让我们怀着无比激动的心情运行我们的服务器，此时服务器运行情况是：

![服务器运行情况](http://img.blog.csdn.net/20160625090711324)

这样是不是有一种恍若隔世的感觉啊，每次打开Hexo的时候看到它自带的本地服务器，感觉非常高大上啊，结果万万没想到有朝一日你就自己实现了它，这叫做“长大以后我就成了你吗”？哈哈，现在是见证奇迹的时刻：

![浏览器运行情况](http://img.blog.csdn.net/20160625090740106)

浏览器怀着对未来无限的憧憬，自豪地写下“Hello World”，正如很多年前诗人北岛在绝望中写下的《相信未来》一样，或许生活中眼前都是苟且，可是只要心中有诗和远方，我们就永远不会迷茫。好了，至此这个系列第一篇Hello World终于写完了，简直如释重负啊，第一篇需要理解和学习的东西实在太多了，本来打算在文章后附一份详细的HTTP头部字段说明，可是因为这些概念实在太枯燥，而使用Markdown编写表格时表格内容过多是写作者的无尽痛苦。关于这个问题，大家可以从[这里](http://www.cnblogs.com/xly1208/archive/2011/10/12/2208468.html)找到答案。下期再见！
