---
title: 使用C#开发HTTP服务器系列之构建RESTful API
categories:
  - 编程语言
tags:
  - HTTP
  - 服务器
  - 'C#'
abbrlink: 3637847962
date: 2016-06-11 15:01:35
---
&emsp;&emsp;各位朋友大家好，我是秦元培，欢迎大家关注我的博客，我的博客地址是[http://qinyuanpei.com](http://qinyuanpei.com)。到目前为止，“使用C#开发HTTP服务器”这个系列系列文章目前已经接近尾声了，虽然我们在服务器功能的完整性(如支持并发、缓存、异步、Htts等)上没有再继续深入下去，可是我们现在已经具备了一个基本的服务器框架啦，所以更多深层次的问题就需要大家根据自己的需要来扩展了，因为写博客更多的是一种“记录-输出-反馈”的一个过程，所以我更希望大家在看完我的博客后能对我有所反馈，因为抄博客上的代码实在是太无聊啦！好了，保持愉悦的心情我们下面来引出今天的话题：构建RESTful API。RESTful API，这个概念或许你曾经听说过，可能它和我们所熟悉的各种Web息息相关，甚至在某种意义上来讲它并不是一种新的技术，而这一切的一切归根到底都是在问一个问题，即网站真的是Web的唯一形态吗？

<!--more-->

# 什么是RESTful API
&emsp;&emsp;什么是RESTful API?首先，REST即REpresentational State Transfer，通常被翻译为“表述性状态传输”或者“表述性状态转移”，它最早出自Roy Fielding的《Archltectural Styles and the Design of Network-based Software Arcltechures》这篇论文，作者曾经参与HTTP协议和Apache Web Server的设计，所以REST实际上是一个和HTTP协议联系非常紧密的一种设计思想。而从这个题目中我们可以找到三个关键词：

* 架构样式——(Archltectural Styles)
* 软件架构——(Software Arcltechures)
* 网络为基础——(Network-based)

所以从我个人角度来理解REST，我更倾向于将REST理解为一种以网络为基础的设计风格，因此REST从本质上来讲解决的是如何正确地使用Web标准的问题。

&emsp;&emsp;以国内为例，当Google的Chrome浏览器选择以Chormium这种形式开源以后，国内厂商纷纷表示跟进以双核为主要特点进行了新一轮的互联网入口争夺战，虽然从技术角度来讲这让Chorme浏览器更加流行，可我们更应该注意到不同的厂商纷纷建立起自己的护城河，以牺牲Web的统一性和标准性来满足其商业竞争的需要，所以我们看到了即使在HTML5定稿以后，在不同浏览器对HTML5的支持区别依然非常大。微信带动了大量可以在朋友圈内流传的“H5”媒介，可是这个东西从来就不是HTML5，而微信内置的QQ浏览器内核更是以各种不兼容让开发者为此殚精竭虑，所以你问我REST是什么的时候，我会回答它是一种风格上统一的Web API，而根据百科中的描述REST通常被这样定义：
* REST是一组架构约束条件和原则，而满足这些约束条件和原则的应用程序就是RESTful。
* REST的目标是构建可扩展的Web Service，它是一种更简单的SOAP协议以及以WSDL为基础的WebService的替代。
* REST采用的是HTTP协议并通过HTTP中的GET、POST、PUT、DELETE等动词收发数据。
* REST希望通过HTTP来完成对数据的元操作，即传统的CRUD(Create、Read、Update、Delete)分别对应GET、POST、PUT、DELETE，这样就统一了数据操作的接口，实现在不同平台上提供一套相同的服务。
* REST是一种面向服务的、分布式的API设计风格。


## 从WebService看REST
&emsp;&emsp;在这里我们提到了SOAP、WSDL、RPC等概念，这是因为从某种意义上来讲，REST是这些概念的一种延伸。以我们熟悉的WebService为例，当我们需要从网络上获取天气预报信息时，我们可以采取两种思路，第一种是通过抓包分析相关天气预报网站来获取信息，第二种是通过调用互联网上提供的WebService来获得信息。虽然这两种方法在技术上具有相似性和可行性，可是我觉得对开发者来讲，除了技术层面的突破以外在道德层面的坚守更为重要，我们说"人无德不立，国无德不兴"正是如此，所以我们这里强烈推荐第二种思路。WebService能够让我们像调用一个方法一样获取信息，那么对我们来讲WebService到底是什么呢？


&emsp;&emsp;WebService首先是一种服务，它不需要客户端提供额外的软件支持，只要客户端支持HTTP协议和XML这样两个特性就可以了。而对WebService自身来讲，它本身就是一种自我描述型的设计，所以服务端和客户端可以通过它来了解响应和请求的内容及格式，因为XML是一种平台无关、语言无关的文档结构，所以WebService是一种可以跨平台的Web API。WebService能够让客户端像调用本地代码一样调用服务端代码，所以WebService是一种分布式计算的Web应用程序组件。我们对WebService下了如此多的定义，其实核心是什么呢？核心是WebService是一种基于HTTP协议和XML的Web API。

&emsp;&emsp;好了，现在我们再来说说什么是SOAP和WSDL。事实上，这些概念听起来都非常地学术，可是我保证这对我们理解REST会有所帮助。首先，SOAP即简单访问对象协议(Simple Object Access Protocol)，听起来感觉非常高大上吗？然而这是一个“唯一没有发明任何新技术的技术”。因为它是一个访问Web服务的协议，如同HTTP协议定义了访问Web的协议一样，SOAP在HTTP协议的基础上，采用XML定义了消息协议，所以SOAP本质上是使用XML进行通信的HTTP协议，这样听起来是不是非常熟悉啦，因为我们熟悉的AJAX同样是采用XML进行通信，所不同的是AJAX是运行在浏览器中的且其主要目的是实现页面的无刷新更新。需要说明的是，虽然SOAP的基础HTTP协议是基于TCP/IP协议的，可是SOAP是具有穿透防火墙的能力的，对此有兴趣的朋友可以自行了解，我们这里因为篇幅有限所以就不做详细说明啦！

&emsp;&emsp;接下来，WSDL即Web服务描述语言(Web Service Description Language)，我对它的理解是提供了一个WebService的文档，因为从定义可以看出，它是一个基于XML的用于描述Web服务以及如何访问Web服务的语言，Web服务提供者通过它可以告知使用者当前Web服务访问的规范和说明，而Web使用者通过它可以在满足平台无关性和语言无关性的情况下快速进行开发，所以综合下来看，WebService和REST都能为我们提供类似地服务需求，关于两者或者说REST能为我们带来哪些不一样的体验，我们将在本文的第二部分说明。

## 从WCF看REST
&emsp;&emsp;我觉得对技术而言，我们每个人都应该试图去发现技术背后真正美的东西，就像我们在了解了WebService，并发现它和REST从本质上来讲都是一个东西的时候，这个时候我们应该直接去了解REST给我们带来了哪些不一样的东西。可是事实上因为开发者使用的平台和语言的多样性，让开发者再这个过程中不得不去对平台或者语言造成依赖，而当每个厂商都试图建立一套自己的标准或者框架的时候，它对开发者造成的这种依赖感就越发地强烈。虽然我目前的工作是做.NET开发，可是事实上我最喜欢的只有微软的C#语言而已。这里我们简单介绍下WCF，WCF即Windows Communication Foundation是由微软发展的一组数据通信的应用程序开发接口，它是.NET框架的一部分，从.NET Framework 3.0开始引入，其设计目标是整合不同进程的通信、不同系统间的通信、C/S架构通信等等通信目标，所以对.NET开发者而言它是一个“全家桶”般的存在，我们到底需要“小而美”还是“大而全”，这是一个问题。

&emsp;&emsp;回到我们关注本身，WCF整合了Web服务、.NET Remoting、消息队列和Enterprise Services的功能并将其整合在Visual Studio中，显然对我们而言，我们关注的核心依然在Web服务。首先，我们要明确的是WebService这个是行业标准，即WebService规范，这是一个和平台、和语言无关的标准，而微软的ASP.NET WebService是ASP.NET框架的组成部分，我不喜欢ASP.NET的一个原因就是我们常常认为网站是Web技术的核心而Web服务不是，更离谱的是我们认为开发一个Web服务器或者一个WebService一定要采用XXX框架，虽然使用Web框架、写业务代码都是技术能力的一种体现，可是不求甚解真的无法让我安心。那么WCF呢？其实WCF本质上是将ASP.NET WebService和微软的相关技术如Enterprise Services(COM+)、.NET Remoting、MSMQ消息队列等进行了整合，为什么要整合在一起呢？因为从宏观上来讲，跨进程、跨机器、跨网络都属于通信的范畴，所以我们现在回过头来看，这些东西玩来玩去有什么稀奇，归根到底还不是HTTP协议啊，我们追求新的技术并没有错，错误的是我们将希望寄托在技术本身，而不是我们自己。


## 让REST理解起来简单点
&emsp;&emsp;我们从最初接触到REST的云里雾里，到翻来覆去地讲述WebService，其实我的目的只有一个，那就是告诉大家，Web技术发展到今天，从本质上来将变化并没有太大，可是为什么我们会看到前端领域每隔一段时间就会有新的框架产生呢？回答这个问题非常简单，所有的框架的提出都是因为某种业务的背景需要，而所有的业务无一不是因为人类增加了其复杂性，所以当你下来看待这一切的时候，你发现从WebService到REST其实变化都是非常细微的东西，与其在新技术里疲于奔命不如静下心来学习好HTML、CSS和JavaScript，虽然JavaScript是一个垃圾的语言，可是有时候它会让我们这些后端程序开发者都懵逼呢，哈哈，所以现在是时候给REST一个简单的定义：
> REST是一种使用URL来定位资源，使用HTTP请求描述操作的Web服务规范。

# REST的约束条件和原则
&emsp;&emsp;我们说REST本质上是Web服务的一种规范，一种思想，所以单独来说REST是没有意义的，这意味着，如果我们要深入了解REST，就需要了解它的约束条件和原则，下面我们就来说说这个问题。

## 资源(Resources)
&emsp;&emsp;在REST中资源是整个架构或者说整个网络处理的核心，那么什么是资源呢？在我们传统的观念中，资源是指服务器上的一个文件，而在REST里资源则是指一个URL。URL即统一资源定位，而我们都知道通过URL可以访问互联网上的资源，所以在REST里这种对资源的指向性更加强烈，并且在这里资源的范畴会被无限放大而并非局限在文件本身，例如：

```
http://api.qc.com/v1/feed 表示获取某人的最新Feed
http://api.qc.com/v1/friends 表示获取某人的好友列表
http://api.qc.com/v1/profile 表示获取某人的详细信息
```
由此我们注意到REST在形式上更加趋向API设计，而我们获取的资源则通过一定的形式进行统一而规范化的表达，因此REST实现了让不同的平台共享一套API这样的愿望，这是一件非常美好的事情，这个世界上的技术阵营举不胜数，而它们为了各自的利益建立一套封闭、臃肿的体系框架，很多时候当我们不需要这样的“全家桶”并且希望“跨平台”的时候，REST将会是一个不错的选择。

## 表现形式(Representational)
&emsp;&emsp;在REST中表现形式作为我们对资源请求的一个结果的呈现，通过对HTTP协议的学习我们已经知道，服务器会给客户端返回什么形式的信息，这一点取决于服务器响应报文中相关头部字段，而对REST来讲，它通常会采用XML或者JSON来告诉请求者请求的结果，因为JSON相比XML所含的冗余信息较少，所以目前更加倾向于或者说流行使用JSON作为请求结果的表现形式。

##状态变化(State Transfer)
&emsp;&emsp;虽然我们一再强调HTTP协议是无状态，这主要体现在HTTP请求与请求、HTTP响应与响应的上下文无关性上。在REST中，我们所说状态变化更多是指HTTP中的GET、POST、DELETE等动词实现。具体来讲，虽然这一点我们在前面有所提及我们来看下面的简单示例：

```
GET http://someurl/tasks 表示获取全部的tasks
POST http://someurl/tasks 表示创建一个新的task
GET http://someurl/tasks/{id} 表示获取一个指定id的task
PET http://someurl/tasks/{id} 表示更新一个指定id的task
DELETE http://someurl/tasks/{id} 表示删除一个指定id的task
```
除此之外，我们注意到REST基于HTTP协议，所以HTTP协议中的状态码对它来讲同样适用，例如最常用的200表示成功、500表示服务器内部错误、404表示无法找到请求资源等等。

# 如何构建REST风格的API
&emsp;&emsp;如何构建REST风格的API?这是这篇文章的最后一个问题，相信大家在阅读这篇文章的时候会感到疲惫吧，我想说写作者的疲惫不一定会比阅读者的疲惫要轻，现在到了这篇文章里最难的部分啦，这可比我们花费大量篇幅来讲什么是REST要更有意义，这是真正的说起来容易做起来难，在正式开始实践以前，我们首先提出下面的最佳实践：

* URLRoot采用下面这样的结构：

```
http://example.com/api/v1/
http://api.example.com/v1/
```

* API版本可以放在URL或者HTTP的Header里

* URL使用名词而非动词：

```
http://example.com/api/v1/getProducts 这是一个糟糕的设计
GET http://example.com/api/v1/products 这是一个优雅的设计
```

* 保证方法时安全的不会对资源状态有所改变。例如：

```
GET http://example.com/api/v1/deleteProduct?id=1 这是一个危险的信号
```

* 资源的地址推荐使用嵌套结构

```
GET http://example.com/api/v1/friends/10375923/profile
```

* 使用正确的HTTP状态码表示访问状态

* 返回含义明确的结果(这是我为什么推荐使用JSON的理由)

&emsp;&emsp;好了，这篇文章我目前能够理解并输出给大家的只有这些啦，关于具体在Web开发中我们如何去实现RESTful API，这个我觉得并没有一个固定的方法吧，而且我现在编写的这个服务器只支持Get和Post两种类型，如果要实现一个完整的RESTful API架构，还需要很长的时间去探索，这篇文章写得我的确有些疲惫，所以有不周的地方希望大家谅解，后续更新关注我的项目[HttpServer](https://github.com/qinyuanpei/HttpServer)就好啦，谢谢大家！