---
abbrlink: 2734896333
categories:
- 编程语言
date: 2017-03-05 14:01:39
description: 这恰恰印证了我们最初的观点，即 HTTPS 协议依然采用 HTTP 协议(三次握手)进行通讯，不同的地方在于中间环节增加了加密处理，例如在客户端和服务器端相互验证的环节采用的是非对称加密，在客户端验证通过以后双方采用随机数作为密钥是对称加密，而三次握手以后验证消息是否被篡改则是采用 HASH 算法;我们可以将其理解为在 HTTP 协议的基础上增加了安全机制，这里的安全机制是指 SSL,简单来讲 HTTPS 协议依然采用 HTTP 协议，不过它在 HTTP 和 TCP 间增加了加密/身份验证层，因此在保证数据传输安全的同时，为服务器提供了身份校验机制;好了，现在我们对 HTTPS 协议有了一个基本的认识：HTTPS 协议相比 HTTP 协议增加了身份验证和消息加密的机制，因此 HTTPS 协议能够保证通讯过程中的数据传输安全
tags:
- HTTP
- 服务器
- C#
title: 使用 C#开发 HTTP 服务器之支持 HTTPS
---

&emsp;&emsp;各位朋友大家好，我是秦元培，欢迎大家关注我的博客，我的博客地址是[http://qinyuanpei.com](http://qinyuanpei.com)。本文是“使用 C#开发 HTTP 服务器”系列的第六篇文章，在这个系列文章中我们实现了一个基础的 Web 服务器，它支持从本地读取静态 HTML 页面，支持 GET 和 POST 两种请求方式。该项目托管在我的[Github](https://github.com/qinyuanpei)上，项目地址为[https://github.com/qinyuanpei/HttpServer](https://github.com/qinyuanpei/HttpServer)，感兴趣的朋友可以前往了解。其间有朋友为我提供了 HTTPS 的 PR，或许这偏离了这个系列开发 HTTP 服务器的初衷，可是我们应该认识到普及 HTTPS 是大势所趋。所以在今天这篇文章中，我将为大家带来 HTTPS 相关知识的普及，以及如何为我们的这个 Web 服务器增加 HTTPS 的支持。

<!--more-->

&emsp;&emsp;2017 年我们听到这样一个声音，苹果将强制实施 ATS，即 App Transport Security。首先我们要了解的是 ATS，它是苹果为了保证应用数据在网络中安全地传输而制定的一种规则，其核心是鼓励开发者使用安全的 HTTPS 协议和服务器进行通讯。在此之前考虑到大量的应用还在使用 HTTP 协议，所以苹果并未强制要求应用遵守这个规范，而此时苹果发出这样一种声音，我们终于意识到苹果这是在推广 HTTPS 啊！无独有偶，同样作为科技巨头之一的 Google，宣布在新发布的 Chrome 56 中会将仅支持 HTTP 协议的网页标记为“不安全”。HTTPS 到底是什么呢？为什么科技巨头纷纷开始对它青眼有加呢？这或许要从 HTTPS 协议说起。

&emsp;&emsp;HTTPS，即 Hyper Text Transfer Protocol Over Secure Socket Layer 的简称，是指以安全为目标的 HTTP 协议。我们可以将其理解为在 HTTP 协议的基础上增加了安全机制，这里的安全机制是指 SSL,简单来讲 HTTPS 协议依然采用 HTTP 协议，不过它在 HTTP 和 TCP 间增加了加密/身份验证层，因此在保证数据传输安全的同时，为服务器提供了身份校验机制。任何采用 HTTPS 协议的网站，均可通过浏览器地址栏中的“锁”标志来查看网站的认证信息，或者是通过 CA 机构颁发的数字证书来查询。下图展示的是 HTTPS 协议中客户端和服务器端通信过程：

![HTTPS协议中客户端和服务器通信过程](https://ww1.sinaimg.cn/large/4c36074fly1fzix85xqd1j20i00fkwg8.jpg)

从图中我们可以看出，在 HTTPS 协议中客户端和服务器端分为六步：

* 客户端请求服务器，发送握手消息给服务器。
* 服务器端返回客户端加密算法、数字证书和公钥。
* 客户端对返回的数字证书进行验证，如果验证通过则产生一个随机数，否则提示验证失败。
* 客户端使用公钥对产生的随机数进行加密，然后将其发送给服务器端。
* 服务器对该随机数进行解密，并以此作为密钥发送握手信息给客户端。
* 客户端收到消息后对消息进行解密，如果解密成功则表示握手结束。

&emsp;&emsp;这恰恰印证了我们最初的观点，即 HTTPS 协议依然采用 HTTP 协议(三次握手)进行通讯，不同的地方在于中间环节增加了加密处理，例如在客户端和服务器端相互验证的环节采用的是非对称加密，在客户端验证通过以后双方采用随机数作为密钥是对称加密，而三次握手以后验证消息是否被篡改则是采用 HASH 算法。所以我们应该可以注意到，HTTP 协议和 HTTPS 协议的一个显著的区别是，前者采用明文来传输消息，而后者采用密文来传输消息，因此 HTTPS 协议比 HTTP 协议在通讯上更为安全。而详细来说，两者的区别主要有：

* HTTPS 需要证书，而 HTTP 则不需要证书，证书由 CA 机构颁发。
* HTTP 采用明文来传输消息，C/S 端无身份验证；HTTPS 采用密文来传输消息，C/S 端有身份验证。
* HTTP 默认采用 80 端口进行通信，而 HTTPS 默认采用 443 端口进行通信。

&emsp;&emsp;好了，现在我们对 HTTPS 协议有了一个基本的认识：HTTPS 协议相比 HTTP 协议增加了身份验证和消息加密的机制，因此 HTTPS 协议能够保证通讯过程中的数据传输安全。在今天这样一个数字时代，当个人隐私安全彻底地暴露在浏览器、应用程序面前，能够提供更安全的互联网服务无疑会让人更有安全感，我想这是苹果和谷歌这样的科技巨头公司，之所以要去努力推广 HTTPS 协议的原因吧！因为客户端需要对服务器的证书进行验证，所以这意味着在客户端拥有访问所有受信证书的能力，例如我们在使用传统网银产品时都需要安装网银证书，这其实就是为了让客户端在向服务器端发起请求时方便对服务器进行验证，因此如果客户端请求的 URL 遭遇劫持，被重定向到某个不被信任的站点上，那么客户端发起的请求就会被拦截。同样的道理，服务器端会对客户端的请求进行验证，所以这里就不再详细展开去说啦。

&emsp;&emsp;我们最初设计这个 HTTP 服务器的时候，没有考虑过要支持 HTTPS 协议。可是当我们了解了 HTTPS 协议后，我们发现，如果要让最初设计的 Web 服务器支持 HTTPS 协议，我们需要关注的是 Security，即身份验证和数据加密，我们知道这里的 Security 指的是 SSL，所以需要了解 SSL 相关的内容。其次，我们需要提供一个数字证书给服务器端，目的是在客户端发起请求的时候，将数字证书、加密算法和公钥返回，保证客户端可以完成证书校验。从这两点可以看出，我们首先需要从 CA 机构购买证书，这一点毋庸置疑。关于证书的购买及服务器的设置，我们通过搜索引擎可以找到相关参考。目前主流的服务器如 Apache、IIS、Tomcat 和 Ngnix 都可以非常方便地支持 HTTPS，这些问题更像是一种基础设施，所以我会在文章末尾列举出相关文章供大家查阅。

&emsp;&emsp;这篇文章的核心是开发一个服务器，所以在保证这些基础设施完备的前提下，让我们将关注点落实到代码上面来。我们提到，HTTPS 除了证书以外关键点是 SSL，而在.NET 中提供 SSL 相关的 API，所以这里我们直接使用这些 API 就可以完成证书的创建、加载等工作。下面是相关的代码示例：

```plain
// 使用OpenSSL.NET生成密钥
RSA rsa = new RSA();
BigNumber number = OpenSSL.Core.Random.Next(10, 10, 1);
rsa.GenerateKeys(1024, number, null, null);
CryptoKey key = new CryptoKey(rsa);

//创建X509证书，Subject和Issuer相同 
X509Certificate x509 = new X509Certificate();
x509.SerialNumber = (int)DateTime.Now.Ticks;
x509.Subject = new X509Name("CN=DOMAIN");        //DOMAIN为站点域名 
x509.Issuer = new X509Name("CN=DOMAIN");
x509.PublicKey = key;                            //指定公钥 
x509.NotBefore = Convert.ToDateTime("2011-1-1"); //起始时间 
x509.NotAfter = Convert.ToDateTime("2050-1-1");  //失效时间 
x509.Version = 2;

//使用私钥签名
x509.Sign(key, MessageDigest.MD5);

//生成CRT证书
BIO x509bio = BIO.File("CA.crt", "w");
x509.Write(x509bio);

//生成PFX证书
var certs = new OpenSSL.Core.Stack<X509Certificate>();
PKCS12 p12 = new PKCS12("PASSWORD", key, x509, certs); //PASSWORD为保护密钥 
BIO p12Bio = BIO.File("CA.pfx", "w");
p12.Write(p12Bio);

//加载证书
var certifiate = X509Certificate.CreateFromCertFile("CA.crt");
```
&emsp;&emsp;在我们获得证书以后，我们就可以通过 SSL 对 Socket 通信过程中传递的消息进行加密了，一个基本的示例代码如下：
```plain
SslStream sslStream = new SslStream(clientStream);
sslStream.AuthenticateAsServer(serverCertificate, false, SslProtocols.Tls, true);
sslStream.ReadTimeout = 10000;
sslStream.WriteTimeout = 10000;
return sslStream;
```
&emsp;&emsp;个人感觉加密相关的问题深奥而晦涩，这篇文章中涉及到的相关概念和技术，都大大地超出了我目前的认知范围。不过既然这位朋友热心地提交了这个 PR，我就将这个过程视为向别人的一次学习吧！我会继续去完善这个项目：[https://github.com/qinyuanpei/HttpServer](https://github.com/qinyuanpei/HttpServer)。这篇博客终于算是写完了，周末开心！

**参考文章**
* [Zery - HTTPS 原理解析](http://www.cnblogs.com/zery/p/5164795.html)
* [阮一峰 - SSL/TLS 协议运行机制的概述](http://www.ruanyifeng.com/blog/2014/02/ssl_tls.html)
* [维基百科 - 超文本传输安全协议](https://zh.wikipedia.org/zh-hans/%E8%B6%85%E6%96%87%E6%9C%AC%E4%BC%A0%E8%BE%93%E5%AE%89%E5%85%A8%E5%8D%8F%E8%AE%AE)
* [猫尾博客 - HTTPS 工作原理](https://cattail.me/tech/2015/11/30/how-https-works.html)
* [MSDN - 如何在 IIS 中设置 HTTPS 服务](https://support.microsoft.com/zh-cn/help/324069/how-to-set-up-an-https-service-in-iis)
* [Dudu - 给 IIS 添加 CA 证书以支持 https](http://www.cnblogs.com/dudu/p/iis_https_ca.html)
* [温柔易淡 - Apache 配置 HTTPS 功能](http://www.cnblogs.com/liaojiafa/p/6028816.html)
* [王浩宇 - 配置 Tomcat 使用 https 协议](http://www.cnblogs.com/wanghaoyuhappy/p/5267702.html)