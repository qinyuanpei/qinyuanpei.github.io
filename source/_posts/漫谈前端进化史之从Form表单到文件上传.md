---
title:  漫谈前端进化史之从Form表单到文件上传
categories:
  - 编程语言
tags:
  - HTTP
  - Form
  - RFC
abbrlink: 345410188
date: 2018-09-05 12:57:36
---
&emsp;&emsp;Hi，大家好，欢迎大家关注我的博客，我是Payne，我的博客地址是[https://qinyuanpei.github.io](https://qinyuanpei.github.io)。今天这篇博客，我们来说说文件上传相关的内容。看到这里，大家一定觉得博主在技术上越来越没追求了吧，文件上传这种再简单不过的东西，真的值得博主你专门写篇博客吗？在介绍声明式RESTful客户端WebApiClient的这篇[文章]()中，博主曾经提到，HTTP协议中对文件上传的支持，主要是通过multipart/form-data来实现。因为这种方式是将文件视为一种特殊的键值对，所以对这种方式我本人不太喜欢。可作为标准的意义就是要忽略个人的情感因素，所以，在今天这篇文章中，博主更多的是想从HTTP协议(**RFC2388**)的角度来看待这个问题，即为什么它选择了multipart/form-data来实现上传，以及伴随着前端技术的发展它经历了哪些变化。

# 从Form表单说起
&emsp;&emsp;圣经上开篇就点明主旨，“起初神创造天地。地是空虚混沌。渊面黑暗”。一切的一切，都要从神创造天地开始，神说，要有光，这世上便有了光。那么，对于HTTP协议我们要从哪里开始说起呢。HTTP的全称是超文本传输协议，所以，它设计的初衷是传输超文本类型的数据。什么是超文本类型的数据呢？从现代网页的组成，我们就可以知道，它不单单是指文本类信息，同时指图片、音频、视频等等一切可能的信息形式。可神奇的地方就在于，HTTP协议是基于文本的协议，这意味着我们在网页中的信息交换，是借助某种文本类型的通信协议。顺着这个思路，最早我们在网页中交换信息的方式是什么呢？我认为是Form表单。想想看，我们在Form表单中输入信息，然后通过一个按钮将数据提交到服务器，服务器会对我们的请求做出响应。事实上，直到今天，我们的前端依然在采用这一机制。所不同的是，我们今天用各种组件替代了Form表单。

&emsp;&emsp;如果我们讲各种语言的"打印"理解为Hello World，那么对前端而言最浅显的Hello World是什么呢？我个人以为是登录，想象一下，这是任何一个Web应用里都有的功能，我们输入用户名和密码以后，点击“登录”按钮就可以登录到系统。虽然，此时此刻的你我，都知道这是一个简单的POST请求，甚至对于用户名和密码这两个字段，我们有多种方法可以将其传递到服务器上。那么，各位是否知道，我们通过Form表单来登录时，这个过程中到底发生了什么呢？既然提到了登录，那么我们这里通过下面的例子来分析。

&emsp;&emsp;如你所见，这是一个相当“简陋”的Web页面。对一名后端开发人员而言，精致的Web页面就是一段被套在华丽外壳里的代码(不知道这样会不会被前端网红们打死)。所以，排除了样式相关的CSS，可以让我们更加专注于核心原理。同样地，我们编写了一个简单的Web API，来处理前端发送来的HTTP请求，这不是本文的重点，我们假设它存在且可以工作就好。

![HTML结构/界面](http://7wy477.com1.z0.glb.clouddn.com/HTTP_Upload_01.png)

&emsp;&emsp;这里已经说过，比起炫酷的Web页面和后端接口，我们这里更关心的是，登录时到底发生了什么。所以，大家都猜对了，通过Chrome自带的开发人员工具，我们可以捕捉到点击“登录”按钮时发出的HTTP请求，我们一起来看看它的报文内容是什么吧，相信大家都会有一种恍然大悟的感觉，让我们拭目以待吧！
![encrypt为x-www-form-urlencode时的请求报文](http://7wy477.com1.z0.glb.clouddn.com/HTTP_Upload_02.png)


&emsp;&emsp;通过这个报文内容，我们可以发现，“登录”实际上是一个POST请求，这是因为我们在HTML结构中声明了，Form表单用什么样的方式去提交数据。而实际上呢，Form表单默认的行为是GET。我们同样会注意到报文中的Content-Type为application/x-www-form-urlencode，它的特点是采用类似key1=value1&key2=value2……的形式来提交数据，并且每一个value都会被编码。这样，我们就不得不提到Form表单的encrypt属性，它有三种基本取值：text/plain、application/x-www-form-urlencode和multipart/form-data。其中，text/plain这种不必再说，因为它传递的是纯文本数据。而对于multipart/form-data来说，它的特点是采用一系列的boundary来分割不同的值，如果我们将示例中Form表单的encrypt属性设为multipart/form-data，就会得到下面的报文内容，可以注意到，它和我们预期是一致的。
![encrypt为multipart/form-data时的请求报文](http://7wy477.com1.z0.glb.clouddn.com/HTTP_Upload_03.png)

&emsp;&emsp;或许大家会说，现在我们用AJAX来请求RESTful风格的API时，不都是用JSON作为数据交换的格式吗？对于这一点，或许我们可以理解为，Form表单是封装了有限的3种Content-Type的XHR对象，所以，Form表单足以让我们一窥AJAX最初的样子。虽然，我们今天已经不再主张使用jQuery，但是熟悉jQuery的朋友一定知道这一点，即jQuery中默认的Content-Type示例上是application/x-www-form-urlencoded。所以，即使我们今天有了全新的Fetch API，可它依然脱离不了HTTP协议的范畴。可或许正因为如此，HTTP中的文件上传多少像是某种妥协的产物。

# 神奇的Input控件
&emsp;&emsp;OK，在本文的第一节，我们使用的是最简单的Input控件，即它的type属性为“text”。事实上，Input控件是一个神奇的控件，因为不同的type会有不同的作用。例如，type为password对应密码域；type为checkbox对应复选；type为radio对应单选域；type为button对应按钮域等等……有很多朋友可能会问，你说的这个和这篇文章有什么关系吗？我想说的是，当然有关系而且关系密切，因为我们下面要提到的这种Input控件，和本文想要说明的HTTP上传，在本质上有着千丝万缕的联系。具体是什么样的联系呢？我们来一起看下面的这个例子。

![HTTP_Upload_06](http://7wy477.com1.z0.glb.clouddn.com/HTTP_Upload_06.png)

![HTTP_Upload_05](http://7wy477.com1.z0.glb.clouddn.com/HTTP_Upload_05.png)

&emsp;&emsp;通过这个例子，我们很容易发现的一点是，当我们采用type为file的Input控件上传一个文件时，它会采用multipart/form-data来传递数据，报文中使用了和第二个示例类似的结构，即第一部分负责描述文件信息，譬如文件的名称、扩展名类型等等；第二部分表示文件数据流，可以理解为二进制形式的内容。既然它采用multipart/form-data来传递数据，那么这是否意味着，我们可以在这个结构中携带更多的信息呢？譬如，有时候我们需要将文件和用户提交的信息关联起来，这个时候就需要将这些信息一切提交到服务器端，如果我们将其拆分为两个API来实现，那么就需要去花精力维护这个关联的id啦。答案自然是可以的，只要把文件视为一种特殊的键值对即可。

# HTTP与文件上传
&emsp;&emsp;好了，说了这多么内容，是时候来说说HTTP与文件上传啦！现在大家都知道了，HTTP上传实际上是在multipart/form-data基础上扩展而来的。早期人们在制定HTTP协议的时候，并没有想到用它来作为文件上传的协议，因为事实上TPC/IP或者FTP都可以提供更好的上传支持。当我们回顾Form表单中关于HTTP的部分，我们就会发现，HTTP中具备上传文件可能性的方式只有两种，即multipart/form-data和x-www-form-urlencode。这里为什么不考虑text/plain呢？尽管从理论上来讲，它可以作为文件上传的一种方式，此时，它相当于把整个文件的内容全部放在请求体(body)中。从实用性角度来讲，text/pain在实际应用中并不多见，因为采用纯文本意味着客户端与服务端必须按照某种规则去解析报文。而从功能性角度来讲，把整个文件的内容全部放在请求体中，则会造成文件信息的不完整，因为此时文件名等信息是没有办法传输到服务器端的，所以，这样综合下来再看的话，HTTP协议本身留给我们的选择的空间并不大，我们能够选择的就只有multipart/form-data和x-www-form-urlencode这两种啦，下面着重来分析下这种数据加密方式。

![HTTP_Upload_07](http://7wy477.com1.z0.glb.clouddn.com/HTTP_Upload_07.png)

&emsp;&emsp;对于Content-Type为multipart/form-data而言，首先，它会在请求头部的Content-Type字段中，声明当前的内容类型为multipart/form-data，并指定一个名为boundary的随机字符串，它的含义是说，从现在开始，请求中的每一个“字段”都会用这个名为boundary的随机字符串进行分割。而对于每一个“字段”而言，它可以拥有部分子头部字段，一个最为常见的头部字段是Content-Disposition，其取值为form-data。除此之外，每一个“字段”可以在**Content-Disposition: form-data;**后追加若干个字段，譬如name、filename以及用以指定文件类型的Content-Type(假如这个“字段”是一个文件的话)。HTTP协议中还规定这里可以支持扩展字段。我们通过type为file 的Input控件进行上传时，默认的name为multipartfile，当服务器端接受到类似的字段时，就会根据报文对文件进行拼接，所以，对于HTTP上传来说，它可以支持多个文件并发上传，但并不直接支持断点续传。注意这里我说的是，不直接支持断点续传，实际上它可以通过请求头部中的Range字段来实现，当然这已经超出了这篇文章的范畴。

![HTTP_Upload_08](http://7wy477.com1.z0.glb.clouddn.com/HTTP_Upload_08.png)

&emsp;&emsp;对于Content-Type为x-www-form-urlencode而言，它会将请求中的每一个字段以key1=value1&key2=value2……的形式串联起来，并对每一个value进行编程，这种传值方式我们一般称为QueryString，而更为一般的场景是，我们在通过GET方式请求数据的时候，QueryString是唯一的传参方式，不同之处是GET请求的参数是附加在URL上，而POST请求的参数是附加在body里。如果我们用这种方式来上传文件会怎么样呢？答案是，当我们试图将一个文件以x-www-form-urlencode方式进行传输时，文件流会被彻底忽略，它实际传输的是对应文件的名称。所以，从这个角度来讲，它不能用于文件的上传。事实上，它是被设计用来传输非二进制数据的，那么可能有人要问啦，那我如果有JSON来传输文件可不可以呢？理论上应该没有问题，曾经我们在一个项目中用JSON描述图片，当然这是经过Base64编码以后的图片。回过头来看text/plain，我们把JSON字符串直接放到body里可不可以呢？当然没有问题，因为问题全部转移到服务器端。所以，官方建议用它来作为调试的一种选择。

&emsp;&emsp;现在，我们可以来总结下Form表单和HTTP协议间的关系啦！首先，Form表单可以提交非二进制数据和二进制数据。非二进制数据，比如一般表单中提交的各种文本信息，用户名、密码这一类等等。二进制数据，主要指各种不同类型的文件等等。对于非二进制数据，可以通过x-www-form-urlencode或者multipart/form-data两种编码方式来提交。对于二进制数据，只能通过multipart/form-data这种方式来提交。所以，当我们需要混合提交二进制数据和非二进制数据的时候，我们就只有multipart/form-data这一种选择啦！更一般的结论是，只要我们的Form表单里有一个type为file的Input控件，对应POST请求的Content-Type就会变为multipart/form-data。我不喜欢这种方式的原因之一，就是构造它的HTTP报文非常难受。如果用HttpClient，痛苦会降低很多；而如果用HttpWebRequest，我会感到绝望。当然，你此时已明白了这个原理，相信Postman可以帮到你的忙。

# Form表单消失以后
&emsp;&emsp;熟悉前端演变历程的朋友，应该对我下面要说的历史表示怀念。在很久很久以前，我们的网页三剑客分别是Dreamwave、Fireworks和Flash。那个时候我们用Dreamwave制作的网页充斥着大量的Form表单，通过JS实现对数据的校验，就像这篇文章里描述的一样，我们做几个type为submit的按钮，就可以把数据提交到服务器端。按理说，这样子很没完美啊，我们可以提交用户输入的信息，可以上传用户选择的文件，何乐而不为呢？为什么大家要用Div + CSS淘汰Form表单呢？我认为主要有两点，传统的基于表格的布局无法满足现代Web程序的布局要求，RESTful风格Web API的出现让开发者希望前后端交互可控。换言之，开发者希望通过FormData这样的对象，精细地控制整个请求的细节，而不是交给一个由浏览器发出的POST请求。所以，我们看到了前端文件上传的新思路。

&emsp;&emsp;首先，最常见的方式，是通过监听Input控件的onchange方法，通过files属性即可获得当前用户选择的文件。我们知道，在大多数情况下，前端是无法和本地文件系统进行交互的。因此通过这种方式获得文件路径，实际上是一个指向本地数据的blob，前端将文件相关的type和size组织到一个FormData对象的实际中，即可完成对文件的上传。其次，可以利用HTML5中的“拖拽”和“粘贴”，其核心依然是监听相关的事件，然后从中获取File对象或者blob对象的实例，一旦获得了这些实例，就可以将其添加到FormData中。到了这一步，接下来的就和第一种方法完全一样啦！最后，是类似百度出品的WebUploader这类HTML5和Flash混合的插件，主打兼容性，不过随着大家对IE8以下版本兼容问题的逐步放弃，这类产品的使用场景会越来越少，我们大概知道就可以啦！归根到底一句话，Form表单和FormData对象，其实是可以相互转化的，Form表单里每一个Input控件的name，其实就是FormData里的key啦，到了这一步，我想HTTP上传就没有什么好神秘了的吧！

# 本文小结
&emsp;&emsp;本文从Form表单说起，首先探讨了Form表单和HTTP之间的关系，即Form表单在提交数据的时候，背后的本质其实是一条HTTP请求，相对应地，Form表单默认的请求方式是GET，在第一个示例中，我们分别展示了使用x-www-form-urlencode和multipart/form-data时请求报文实际的内容。接下来，我们提到了HTML中的Input控件，它可以通过指定不同的type达到不同的效果，作为第一个示例的延伸，我们尝试通过Form表单上传文件并重点关注其报文的结构。接下来，我们从协议的角度分析了为什么要选用multipart/form-data来上传文件以及它的原理是什么。最后，我们从前端常见的文件上传方式入手，简要分析了Form表单和FormData对象间的内在联系，即Form表单和FormData对象，其实是可以相互转化的，Form表单里每一个Input控件的name，其实就是FormData里的key。好啦，又是一个难以入眠的夜晚，这篇博客先写到这里，大家晚安！
