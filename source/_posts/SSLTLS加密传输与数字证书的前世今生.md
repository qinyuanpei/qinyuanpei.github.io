---
toc: true
title: SSL/TLS加密传输与数字证书的前世今生
categories:
  - 编程语言
tags:
  - 证书
  - 加密
  - 签名
  - HTTPS
copyright: true
abbrlink: 3163397596
date: 2021-09-05 14:13:32
---
Hi，大家好，我是飞鸿踏雪，欢迎大家关注我的博客。近来，博主经历了一次服务器迁移，本以为有 Docker-Compose 加持，一切应该会非常顺利，没想到最终还是在证书上栽了跟头，因为它的证书是和IP地址绑定的。对，你没听错，这个世界上还真就有这么别扭的设定，尤其是你折腾了一整天，发现你需要到一个 CA 服务器上去申请证书的时候，那种绝望你晓得吧？数字证书、HTTPS、SSL/TLS、加密……无数的词汇在脑海中席卷而来，这都是些啥啊？为了解答这些困惑，经历了写字、画图、查资料的无数次轮回，终于在周末两天淅淅沥沥的雨声中，有了今天这篇文章，我将借此带大家走进SSL/TLS加密传输与数字证书的前世今生，希望从此刻开始，令人眼花缭乱的证书格式不会再成为你的困扰。

# 证书与加密

对于数字证书的第一印象，通常来自于 HTTPS 协议。因为地球人都知道，HTTP 协议是不需要数字证书的。对于 HTTPS 协议的理解，可以简单粗暴的认为它约等于 HTTP + SSL，所以，从这个协议诞生的那一刻起，加密算法与数字证书就密不可分，因为从本质上来讲，HTTPS 协议就是为了解决如何在不安全的网络上、安全地传输数据的问题。事实上，HTTPS 协议的实现，背后依托SSL/TLS、数字签名、对称/非对称加密等一系列的知识。也许，在读到这篇文章以前，你就像博主一样，对于 HTTPS 的理解，永远止步于 HTTP + SSL。那么，我希望下面的解释可以帮助到你，通常，HTTPS 认证可以分为 单向认证 和 双向认证 两种，这里我们以为以单向认证为例，来说明数字证书与加密算法两者间的联系：

![HTTPS 数字证书与加密传输间的关系](https://i.loli.net/2021/09/07/nkJFiPNdVc4ShAw.png)

如图所示，HTTPS 单向认证流程主要经历了下面 7 个步骤，它们分别是：

* 客户端发起 HTTPS 请求
* 服务器返回证书信息，本质上是公钥
* 客户端/浏览器通过 CA 根证书验证公钥，如果验证失败，将会收到警告信息
* 客户端随机生成一个对称密钥 Key，并利用公钥对 Key 进行加密
* 服务器使用私钥解密获得对称密钥 Key
* 通过对称密钥 Key 对确认报文进行加密
* 双方开始通信

由此，我们可以看出，整个 HTTPS 单向认证流程，实际上是结合了 对称加密 和 非对称加密 两种加密方式。其中，非对称加密主要用于客户端、服务器双方的“试探”环节，即证书验证部分；对称加密主要用于客户端、服务器双方的“正式会话”阶段，即数据传输部分。关于 对称加密 和 非对称加密 两者的区别，我们可以从下面的图中找到答案：

![对称加密 与 非对称加密](https://i.loli.net/2021/09/08/lBNLu4t9VxkOewn.png)

因为客户端持有服务器端返回的公钥，所以，两者可以使用 非对称加密 对随机密钥 Key 进行加/解密。同理，因为客户/服务器端使用相同的随机密钥，所以，两者可以使用 对称加密 对数据进行加/解密。有朋友可能会问，那照你这样说，任何一个客户端都可以向服务器端发起请求嘛，你这样感觉一点都不安全呢？我承认，大家的担心是有道理的。所以，在此基础上，我们还可以使用双向认证，就是不单单客户端要验证服务器端返回的证书，同样，服务器端要对客户端的证书进行验证。那么，客户端是如何验证服务器端返回的证书的呢？服务器返回的证书里都含有哪些信息呢？带着这些问题，我们来看看知乎这个网站：

![知乎的证书信息](https://i.loli.net/2021/09/07/5vcDPmT14WyCOqE.png)

事实上，浏览器在对服务器端返回的证书进行校验时，主要关心下面这些信息：

* 判断域名、有效期等信息是否正确：这些信息在证书中是公开的，可以非常容易地获得。
* 判断证书是否被篡改：需要由 CA 服务器进行校验。
* 判断证书来源是否合法：每一份签发的证书都可以按照证书链找到对应的根证书，所以，可以通过操作系统中安装的根证书对证书的来源进行验证。
* 判断证书是否被吊销：需要由 CRL（Certificate Revocation List，即 证书注销列表）和 OCSP（Online Certificate Status Protocol, 即 在线证书状态协议） 来实现。

这里引入了一个新的概念，即 CA（Certification Authority）。那么，什么是 CA 呢？ 通俗来讲，CA 就是一个负责签发、认证和管理证书的机构。可能有朋友会想，客户端和服务器端通过非对称加密相互校验证书就好了啊，为什么还需要这样一个第三方的机构呢？事实上，这相当于一种担保/信用体系，因为服务器端的公钥对任何人来说都是可见的，我们来考虑这样一种情形。假设客户端从服务器端获得了某个公钥，并且它认为这个公钥是可信的，此时，有一个不怀好意的中间人截获了这个公钥，它如法炮制伪造了一个相同的公钥并返回，那么，此时客户端会如何看待这个公钥呢？虽然这个中间人不可能伪造出与服务端相同的私钥，可这无疑会让客户端感到困惑，因为它没有办法判断这个证书的真假。

![证书的签发与认证](https://i.loli.net/2021/09/07/renZkROKljmYuoE.png)

其实，写到这里的时候，博主隐隐约约意识到，当下流行的比特币/数字人民币均与数字签名息息相关，因为 CA 使用私钥对证书进行了签名，这样就杜绝了证书被篡改的可能，从而可以为证书的真实性背书，这种基于信任制、拥有权威性的体系，就像现实生活中银行为货币的真实性、价值背书一样。因此，我们会注意到，在现实生活中，想要获得一份权威机构的数字证书，就需要向 CA 进行申请，例如，知乎的证书是从 DigiCert Inc 这个机构中购买的，不同的机构对于证书申请者的审核要求不同，这样就形成了不同价格甚至免费的数字证书。

![CA 组织树形结构](https://i.loli.net/2021/09/07/szYK63b2y4XhNr7.png)

当然，这个世界上有超过1亿个网站，如果每个网站都去向 CA 申请数字证书，那么，CA 一定会忙到崩溃。所以，实际的运行过程是，一个根 CA 会分成多个中间 CA，然后中间 CA 可以继续拆分为更小的中间 CA，这样做的好处是效率更高，同时保证了根 CA 中私钥的安全性。此时，我们会发现一个新的问题，就是当整个数字证书体系中突然多出来这么多“中介”以后，我们如何保证证书的权威性和真实性呢？类似地，数字证书世界里里有证书链的概念。所谓证书链，就是指证书可以追本溯源、在整个链路上都是可信任的，听起来是不是有区块链的味道了？事实上区块链正是利用了数字签名的不可伪造、不可抵赖、不可复制等一系列特性。说回到证书链，由根 CA 签发的证书称为根证书、由中间 CA 签发的证书称为中间证书，其关系如下图所示，假设 A 完全信任 B，B 完全信任 C，则 A 可以完全信任 C:

![证书链示意图](https://i.loli.net/2021/09/07/WilIrjBSwTft2hL.png)

# 证书创建

OK，现在我们已然理清了证书与加密两者间的联系，那么，在实际生活中，我们该如何获得一个证书呢？由上文可知，证书理论上应该由 CA 机构来签发。目前，全球主流的 CA 机构有[Comodo](https://ssl.idcspy.net/comodo/)、[Symantec](https://ssl.idcspy.net/symantec/)、[GeoTrust](https://ssl.idcspy.net/geotrust/)、[DigiCert](https://www.anxinssl.com/digicert/)、[Thawte](https://ssl.idcspy.net/thawte/)、[GlobalSign](https://www.anxinssl.com/globalsign/)、[RapidSSL](https://ssl.idcspy.net/rapidssl/) 等，其中 [Symantec](https://www.anxinssl.com/symantec/)、[GeoTrust](https://www.anxinssl.com/geotrust/) 都是 [DigiCert](https://www.anxinssl.com/digicert/) 机构的子公司，占据数字证书体系中的垄断地位，就连国内的互联网厂商都需要向这些机构来购买证书，所以，推广 HTTPS 并不是完全出于安全的考虑，实际上还有某种利益关系在里面，可以想象得到，假如你的证书信任度不高，不在浏览器的可信任机构列表中，那么，你的网站就会被浏览器认为是不安全的，随之而来的就是用户对网站的信任度的下降。当然，购买数字证书是需要花钱的，所以，实际操作中，通常有自签名证书 和 CA 证书 两种，两者唯一的差别就在于权威性不同，大概相当于一种互联网行业的“保护费”。

## 自签名证书

所谓自签名证书，其实就是自建一个 CA，然后利用这个 CA 对证书进行签名。为什么说它没有权威性呢？大概这就像小时候试卷上要签署大人的名字一样，如果你照着大人的笔迹伪造了签名，那么，此时没有人能保证这份签名的真实性。更深层次的原因在于，由你自建的这个 CA 没有在互联网上备案，它产生的证书无法通过证书链追溯，这是自签名证书没有权威性的原因。我们通常说的创建/生成证书，其实都是指这种自签名证书，创建自签名证书最常见的方式是 [OpenSSL](https://www.openssl.org)：

```bash
// 创建根证书
openssl genrsa -out ca.key 2048
openssl req -new -key ca.key -out ca.csr
openssl x509 -req -days 365 -in ca.csr -signkey ca.key -out ca.crt
```
在这个过程中，OpenSSL 会要求我们提供下列信息：国家、省份、城市、组织 以及 全域名(FQDN)。在此之前，关于知乎的那个例子，实际上证书上的那些信息就是从这里来的。当我们有了这样一个自建的 CA 以后，我们就可以用这个自建的 CA 去签发证书，这就是自签名 CA 证书，如何生成这个证书呢？

```bash
// 环境准备，下列路径在 openssl.conf 文件中定义
mkdir -p ./demoCA/newcerts
cd ./demoCA/
touch index.txt
echo '01' > serial
cd ..
// 签发证书
openssl genrsa -out server.key 2048
openssl req -new -key ca.key -out server.csr
openssl ca -in server.csr -out server.crt -cert ca.crt -keyfile ca.key
```
同样的，我们需要再输入一次下列信息：国家、省份、城市、组织 以及 全域名(FQDN)，然后利用自建的 CA 进行签名。在 OpenSSL 中，它定义了证书申请方需要满足的“门槛”，这决定了你能不能向某个 CA 申请证书，其定义位于`openssl.conf`文件中：

![ OpenSSL 策略配置](https://i.loli.net/2021/09/08/ldIigFrJ8LvYZfP.png)

例如，这里的策略表示，只有当证书申请方的国家、省份、组织相同的时候，CA 才会接受你的证书申请。所以，至此你明白证书为什么收费了吧？因为主流的 CA 机构都在国外，理论上 CA 机构可以去调整这个策略，可如果对方不愿意调整策略，那么你只能找别人帮你来申请，通过不断的调用`openssl ca`命令， 产生新的中间 CA，这样就形成了树状的 CA 组织。是不是觉得看人脸色非常地不舒服？除了这种方式以外，我们还可以按下面这种方式生成证书，这种方式像极了我们小时候模仿大人签字：

```bash
// 签发证书
openssl genrsa -out server.key 4096
openssl req -new -key server.key -out server.csr
openssl x509 -req -days 365 -in server.csr -signkey server.key -out server.crt
```
如果是在 Windows 系统下，我们还可以搭建 CA 服务器，此时，证书申请者需要远程登陆到这台服务器进行操作，请参考：[服务器证书部署](https://docs.microsoft.com/zh-cn/windows-server/networking/core-network-guide/cncg/server-certs/server-certificate-deployment)。

## CA 证书

一旦理解了自签名证书，理解 CA 证书 就变得特别容易，这就是交了“保护费”的证书，过去总以为互联网世界里没有政治，后来发现互联网并不是“法外之地”，一切的自媒体、流量，最终都会转化为某种商品出售，只要人与人形成了某种圈子或者团体，这种政治就一定会存在。所以，你到腾讯云或者阿里云去购买证书，而腾讯和阿里则是某个 CA 机构的代理商，因为数字证书通常会和域名产生联系，所以，在供应商那里，两者往往是捆绑在一起销售，再加上网站备案、虚拟主机这些东西，在由资本绘制的商业版图里，你的钱包被安排得明明白白。或是为了打破这种垄断，或是为了某种利害关系，慢慢地出现了像 [Let's Encrypt](https://letsencrypt.org/zh-cn/) 这样的提供免费证书的机构。所以，下面，我们以此为例来展示如何申请一个 CA 证书：

```bash
git clone https://github.com/acmesh-official/acme.sh.git
cd ./acme.sh
./acme.sh --install

acme.sh --register-account -m <Your E-Mail>
acme.sh --issue -d <Your-Domain> --standalone
```

目前，[Let's Encrypt](https://letsencrypt.org/zh-cn/) 的使用是通过 acme.sh 这个脚本来驱动的，其基本用法如上面脚本所示。不同于自签名证书，Let's Encrypt 目前不支持使用公网 IP 来申请证书，所以，如果在开发阶段，可以使用自签名的证书；在生产阶段，则最好使用 CA 签发的证书。通过阅读 [文档](https://github.com/acmesh-official/acme.sh/wiki/%E8%AF%B4%E6%98%8E) 可知，它支持 HTTP 和 DNS 两种验证方式，可以使用 Apache 、Nginx 和 Standalone 三种模式，个人推荐使用 Docker 来进行部署，因为前两种模式要求你安装对应的软件，第三种模式要求你的 80 端口是空闲的，这对于一名开发人员来说，简直是痴心妄想。如果你有一个域名，而恰好这个域名提供商在其支持的 [列表](https://github.com/acmesh-official/acme.sh/wiki/dnsapi) 内，那么，你就可以使用下面的方式来申请证书。首先，准备一个`docker-compose.yml`文件，博主的域名是从 [GoDaddy](https://www.godaddy.com) 申请的，大家可以结合实际情况进行调整：

```bash
version: "2.1"
services:

  acme.sh:
    image: neilpang/acme.sh
    container_name: "acme.sh"
    volumes:
      - /docker/ssl:/acme.sh
    environment:
      - GD_Key=<GoDaddy Key>
      - GD_Secret=<GoDaddy Secret>
    command: daemon
```
接下来，我们只需要启动容器，然后在容器内部执行命令即可：

```bash
docker-compose up -d
docker exec -it <ContainerId> sh
acme.sh --register-account -m <Your E-Mail>
acme.sh --issue --dns dns_gd -d <Your-Domain>
```
可以注意到，下面即为博主从 Let's Encrypt 申请到的证书文件：

![从 Let‘s Encrypt 申请证书](https://i.loli.net/2021/09/08/FZLKdQ1cBRtjS4y.png)

如果你的域名提供商在这个 [列表](https://github.com/acmesh-official/acme.sh/wiki/dnsapi) 内，此时，你可以手动将其生成的值添加到域名记录中，这些在文档中均有提及，不再赘述。总而言之，你向 CA 机构申请证书需要一个有效的域名，像腾讯云、阿里云这种云服务提供商，早已提供好了完整的一条龙服务，只要你愿意花钱去买对方的产品。

# 证书使用

一旦生成了证书，我们就可以在应用程序中使用这些证书啦，我注意到公司的每个项目都配置了证书文件，其实我一直不明白，为什么不能直接把证书安装到宿主机上？这样只需要折腾一次就好了啊，简直是一劳永逸。如果有小伙伴们知道这个问题的答案，欢迎大家在评论区留言。下面我们来看看，生成的证书如何在不同的环境中配置，这里以 ASP.NET Core 、Envoy 和 Nginx 为例来说明。

## ASP.NET Core

在 ASP.NET Core 中配置 HTTPS 证书，最直接的方案是在通过 Kestrel 中间件来指定证书路径和密码：

```csharp
webBuilder.ConfigureKestrel(options => {
    // 方式 1
    options.ConfigureHttpsDefaults(kestrel => {
        kestrel.ServerCertificate = new X509Certificate2("./path/to/your/example.com.pfx","<证书密码>");
    });

    // 方式 2
    options.Listen(IPAddress.Loopback, 5001, kestrel => {
      kestrel.UseHttps(new X509Certificate2("./path/to/your/example.com.pfx","<证书密码>"));
    });
});
```

如果整个 ASP.NET Core 应用以容器方式运行，则还可以按下面这样的方式来配置证书：

```bash
docker run --rm -it -p 8000:80 -p 8001:443 \
  -e ASPNETCORE_URLS="https://+;http://+" \
  -e ASPNETCORE_HTTPS_PORT=8001 \
  -e ASPNETCORE_ENVIRONMENT=Development \
  -e ASPNETCORE_Kestrel__Certificates__Default__Password="<证书密码>" \
  -e ASPNETCORE_Kestrel__Certificates__Default__Path=/path/to/your/example.com.pfx
  -v /c/path/to/certs/:/https/ 
  <镜像Id>
```
不得不说，这里的双下划线，总是让我不由地想起 Python 里的魔法方法：`__init__`。可能大家会疑惑，为什么博主这里要强调证书的扩展名，因为这实际上是数字证书里最让人迷惑的地方：

![数字证书编码格式与扩展名](https://i.loli.net/2021/09/08/tadr5bEHxR1Cs2y.png)

在整个数字证书体系中，X.509 是作为数字证书标准而存在的，按照编码格式的不同，可以分为 PEM 证书 和 DER 证书两类，前者是文本格式，而后者是二进制格式。不同的操作系统、开发语言，产生了不同的证书文件格式，但这些扩展名本身并不能说明什么，特别是像  .crt 或者 .cre 这种薛定谔的证书，唯一的判断标准，就是用记事本打开它，如果可读，说明它是 PEM 编码的证书，如果不可读，说明它是 DER 编码的证书。如果大家和 Java 系的技术或者产品做过对接，应该会对这种微妙的差别深有体会，此时，我们就需要通过 OpenSSL 来实现不同证书格式间的转换，ASP.NET Core 需要的 .pfx 证书是如何产生的呢？

```bash
// x.509 -> .pfx
openssl pkcs12 -export -in server.crt -inkey server.key -out server.pfx
```

同理，常见的 OpenSSL 转换命令如下：

```bash
// .pem -> .pfx
openssl pkcs12 -export -in cert.pem -out cert.pfx -inkey key.pem 
// .pfx -> .cer
openssl pkcs12 -in server.pfx -out server.cer -nodes
// .cer -> .pem
openssl x509 -inform der -in server.cer -out server.pem
// PEM -> DER
openssl x509 -in server.pem -outform der -out server.der
// DER -> PEM
openssl x509 -in server.der -inform der -outform pem -out server.pem
```

## Envoy

Envoy 中可以直接使用 .crt 文件 以及 .key 文件，这里出现了一个 TLS 协议，这个协议一直没机会来说，这里可以简单说一下，它可以视为 SSL 3.1，因为早期的 SSL 协议是由网景公司(Netscape)提出的，一共经历了 1.0、2.0 和 3.0 三个版本，后来标准化组织 IETE 在此基础上提出了增强版的 TLS 协议，一直沿用至今，所以，TLS 可以看做是 SSL 3.1，换句话讲，HTTPS = HTTP + SSL/TLS。
```yaml
transport_socket:
  name: envoy.transport_sockets.tls
  typed_config:
    "@type": type.googleapis.com/envoy.extensions.transport_sockets.tls.v3.DownstreamTlsContext
    common_tls_context:
      alpn_protocols:
        - "h2"
      tls_certificates:
        certificate_chain:
          filename: "/path/to/your/example.com.crt"
        private_key:
          filename: "/path/to/your/example.com.key"
```
相信到了现在这个地步，大家终于能想明白 通过 HttpClient 调用第三方接口时，为什么要这这样一段堪称魔法的代码了吧？因为在推进 HTTPS 的过程中，大家使用的 SSL/TLS 协议版本都不一样，有时候客户端还提供不了可以通过验证的证书，所以，大家干脆无视协议的版本、证书的验证错误这些问题啦！

```csharp
System.Net.ServicePointManager.SecurityProtocol =
    SecurityProtocolType.Tls | SecurityProtocolType.Tls11 | SecurityProtocolType.Tls12 | SecurityProtocolType.Tls13;
System.Net.ServicePointManager.ServerCertificateValidationCallback += (a, b, c, d) => true;

// RestSharp
var client = new RestClient();
client.RemoteCertificateValidationCallback += (a, b, c, d) => true;
```

## Nginx

Nginx 就更不必说啦，不过我个人现在更喜欢 Envoy 一点，Nginx 可以用 .crt 证书 或者 .pem 证书，我们只需要简单配置一下就可以了：
```
server {  
    listen 443 ssl;
    server_name example.com;

    ssl on;
    ssl_certificate /path/to/example.com.crt;
    ssl_certificate_key /path/to/example.com.key;
}
```

# 本文小结

因为一次服务器迁移时被证书苦虐的经历，决定花点时间研究了一下数字证书，本文从 HTTPS 协议入手，引出了对称加密、非对称加密等加密相关的内容，然后讨论了什么是证书，什么是 CA，以及 为什么需要 CA 等内容，现实世界中需要一个为证书权威性、真实性提供担保的组织，这种组织可以签发证书、验证证书、管理证书，利用数字签名的不可篡改、不可抵赖、不可复制、不可伪造等特性，根 CA 可以授权中间 CA 去签发证书，因为整个证书链都是可以追溯的。有了这些知识作为背景，我们分享了如何获得一份自签名证书和 CA 证书，两者本质上没有什么不同，唯一的区别在于其信任度不同。故事的最后，博主分享了如何为 ASP.NET Core 、Envoy、Nginx 配置 证书，对于数字证书的理解，从道的层面到术的层面，我们全部都串联起来啦，好了，以上就是这篇博客的全部内容，欢迎大家在评论区积极留言、参与讨论，原创不易，写技术博客更不易，大家点个赞吧！

# 参考链接

* [SSL 数字证书的标准、编码以及文件扩展名](https://kangzubin.com/certificate-format/)
* [Docker 使用 acme.sh 申请 SSL 证书](https://www.moeelf.com/archives/281.html)
* [超文本传输安全协议](https://ws.wiki.gaogevip.com/wiki/%E8%B6%85%E6%96%87%E6%9C%AC%E4%BC%A0%E8%BE%93%E5%AE%89%E5%85%A8%E5%8D%8F%E8%AE%AE)
* [RingCentral Tech丨证书，证书链，CA的那些事](https://zhuanlan.zhihu.com/p/100389013)
* [你知道，HTTPS用的是对称加密还是非对称加密](https://zhuanlan.zhihu.com/p/96494976)