title: 使用WebClient实现迅雷队列下载
date: 2016-06-06 13:32:44
categories: [编程语言]
tags: [迅雷,队列,下载]
---
&emsp;&emsp;因为一直想为Unity3D编写一套以资源热更新为主的框架，考虑到Unity3D提供的WWW是一个针对HTTP协议的简单封装，无法满足更加复杂和深入的定制化需求，所以我们需要一个更好的方案。在对.NET平台下提供的相关功能进行评估后发现，WebClient是一个非常不错的选择，因为它基本满足了我们文件下载这样朴素的需求。虽然我们可以选择更为朴素的WebRequest和WebResponse，然后通过读写流的形式来实现文件下载，可是因为WebClient提供了同步和异步两种形式的下载方式，而且可以通过委托的形式来监听下载过程，这对我们来说是非常好的设计，所以我们最终选择了使用WebClient来实现这个热更新框架。

<!--more-->

# 使用WebClient下载文件
&emsp;&emsp;WebClient是一个.NET中提供的组件，我们可以将其理解为对WebRequest和WebResponse的一种良好封装，因为WebRequest和WebResponse在使用的时候从流程上来讲相对复杂，我们需要在其内部对Request和Response进行操作和控制，所以我们需要一个可以让我们专注于远程服务器上获取数据、下载文件的工具类，WebClient自此应运而生。从MSDN中对WebClient的描述可知：我们可以WebClient这个类去访问和获取网络上的资源文件。因为我们无法WebClient进行内部控制，所以WebClient在处理Cookie、Session、重定向和代理等问题时会显得力不从心。然而在这里，我们更关注从远程服务器上获取数据和下载文件，对这些需求而言WebClient完全足够了。

&emsp;&emsp;WebClient相对HttpWebRequest和HttpWebResponse这两个类来说，使用起来是非常简单的。WebClient从功能性上而言，可以分为上传和下载两个大类：

##上传功能
* OpenWrite：返回一个用于将数据发送到指定URL的Stream。
* UploadData：将字节数组发送到指定URL并返回包含任何响应的字节数组。
* UploadValues：将NameValueCollection发送到指定URL并返回包含任何响应的字节数组。
* UploadFile：将本地文件发送到指定URL并返回包含任何响应的字节数组。
* UploadString：将字符串发送到指定URL并返回包含任何响应的字符串。

##下载功能
* DownloadData：从资源下载数据并返回字节数组。
* DownloadFile：从资源下载文件到本地。
* DownloadString：从远程服务器下载数据并返回字符串。
* OpenRead：从资源以Stream形式返回数据。

&emsp;&emsp;现在我们非常笼统地在描述WebClient能够帮助我们做哪些事情，实际上根据同步还是异步来区分，在上述这些功能中我们都可以找到它对应的同步方法实现和异步方法实现。而更重要的一个地方时，WebClient是基于事件异步的，相反地，HttpWebRequest则是基于代理异步的。为了理解这个概念，我们使用下面的简短代码示例来说明：

* 使用WebClient下载一个指定URL的资源
```
WebClient webClient = new WebClient();
webClient.OpenReadAsync(new Uri ("http://localhost:4000/iamges/csharp.jpg"));
webClient.OpenReadCompleted += (sender,e) =>{
    //获取图片Stream信息
    Stream stream = e.Result;
    //执行后续操作
};
```

* 使用HttpWebRequest下载一个指定URL的资源
```
HttpWebRequest request = (HttpWebRequest)WebRequest.Create(
    "http://localhost:4000/iamges/csharp.jpg");
request.Method = "GET";
request.BeginGetResponse ((ar) => {
    //获取图片Stream信息
    Stream stream = ((HttpWebRequest)ar.AsyncState).EndGetResponse().GetResponseStream();
    //执行后续操作
}, request);
```
&emsp;&emsp;更为普遍的是，我们可以使用下面这种方式来监听下载进度：
```
WebClient webClient = new WebClient();

//设置"正在下载"回调函数
webClient.DownloadProgressChanged += (sender,e) => {
    Console.WriteLine("已下载{0}%,{1}/{2}",
    e.ProgressPercentage,
    e.BytesReceived,
    e.TotalBytesToReceive);
};

//设置"下载完成"回调函数
webClient.DownloadFileCompleted += (sender, e) => {
    Console.WriteLine("下载完成!");
};

//开始下载
webClient.DownloadFileAsync(
    new Uri("http://localhost:4000/iamges/csharp.jpg"), 
    "D:\\download\\csharp.jpg");
```
# 说说迅雷的队列下载
&emsp;&emsp;好了，现在我们将话题转向迅雷。迅雷这个软件我们应该是非常熟悉了，可是在很多年以前，在中国互联网远远没有现在这样发达的时候，可能我们对下载工具的第一印象并非是迅雷，而是网络蚂蚁或者网际快车。最早的下载软件基本都支持HTTP下载、断点续传和FTP下载这三个特性，这是因为早期国内互联网下载速度非常慢，每次下载失败以后都需要重新下载，这样无疑会浪费用户的大量宽带费用。其次，早期互联网的网络资源都集中在FTP服务器上，所以登录FTP服务器下载资源是一种此时此刻想起来都颇为怀念的体验。这里有一个非常有意思的事情，因为登录FTP服务器以后的界面和Windows资源管理器的界面非常相似，所以很多人完全不理解为什么复制文件操作会涉及到下载。在Windows下制作一个资源管理器最为快捷的方案是什么呢？答案是使用IE浏览器内核访问一个表示File协议的地址，或许这样可以解释这里的这个问题吧！

&emsp;&emsp;迅雷的崛起很大程度上是因为它搭上了互联网这趟快车，如同单机游戏在网络游戏的冲击下颓然失势，网络蚂蚁和网际快车这两个软件在P2P下载这项新技术面前被完全挫败。作为一个工具型产品，迅雷无可避免地需要考虑如何从强大的用户粘性中实现盈利，所以我们看到迅雷在网络游戏、在线视频等领域不断地高歌迈进，在盗版和色情等危险地带不断地打着擦边球，甚至当快播总裁在法庭上以"技术无罪"地观点为快播开脱责任时候，我们就像一个被跌跌撞撞地推向人前的孩子。中国互联网发展到今天，我们常常反思技术到底做错了什么？为什么我们的技术常常被当作洪水猛兽一样遭人指责，难道我们都忘了在写下第一行代码时想要让这世界更加美好的理想？在我看来，技术本身是无害的，因为它就像在这世间存在的真理一样，我们的选择非常重要。

 &emsp;&emsp;迅雷的队列下载是一个非常有意思的话题。首先，它是一个多任务下载软件，这意味着它需要使用有限的线程数目来调度所有的下载任务，因为我们不可能单独为每一个下载任务去创建一个线程。当我们新建一个下载任务的时候，首先需要判断当前是否由空闲的线程来执行这个下载任务。如果由空闲的线程可以使用则直接开始下载，否则该任务应该进入等待队列排队直到轮到处理该任务的时候。这就像我们平时到银行中办理业务取号排队一样，我一直不明白为什么医院不尝试开放挂号的业务，我觉得通过互联网可以为用户节省排队挂号的时间，前提是我们生活在一个良性竞争的社会环境里。迅雷更为有趣的一点是可以对各个下载任务进行管理，这相当于我们可以人为的干预整个排队机制，我对多线程的研究并不深入，所以我无法理解如何让一个线程暂停及恢复，而断点续传从本质上来讲是一个从指定位置开始读写的过程，这部分内容应该是我们的能力范围内的。

# WebClient实现的队列下载
&emsp;&emsp;照应文章开头，本文的目的是为了设计一个基础的Unity3D热更新框架，所以我们这里将需求简化为：编写一个可批量下载资源的、支持队列下载的、多任务下载的下载器。这是因为在做热更新的时候，通常无需对每个下载任务进行控制，而只需要保证所有需要下载的资源都能够成功下载并保存到指定的位置，所以我们这里对需求进行了简化。本文所使用的示例代码可以参照UniAssetsManager项目，这是一个我正在开发中的Unity3D资源热更新框架，而借鉴迅雷队列下载的思路并试图实现一个仿迅雷下载功能，这部分内容可以参照EasyDown项目，这是一个我正在开发中的仿迅雷下载的项目。


