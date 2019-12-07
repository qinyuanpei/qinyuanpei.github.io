---
title: Referrer还是Referer? 一个迷人的错误
categories:
  - 编程语言
tags:
  - HTTP
  - 历史
  - Referrer
abbrlink: 2015300310
date: 2019-12-04 17:22:33
---
诗人郑愁予曾经在一首诗中写道：**我达达的马蹄是个美丽的错误，我不是归人，是个过客**。而对我来说，十九岁之前的我，一样是个沉浸在诗歌中的文艺少年。十九岁之后的我，作为一名程序员，更多的是邂逅各种错误。可偏偏人类世界对待错误从来都不宽容，所以，**错误本身既不美丽，亦不浪漫**。接近中年的我，无论如何，都写不出年轻时令人惊艳的句子，这或许和我们面对错误时的不同心境，有着莫大的关联，而今天这篇博客，同样要从一个历史上的错误说起。

# 因拼写而怀疑人生

话说，博主这天做了一个非常“简单”的功能，它允许用户通过富文本编辑器来编写HTML，而这些HTML会被插入到页面的特定位置，譬如用户可以为页脚的备案号添加一个超链接，当用户点击备案号的时候，就可以调转到工信部备案号查询的网站上。这个功能非常简单吧，因为这就是HTML中a标签的作用。博主快速了引入UEditor，虽然这个项目百度都不再继续维护了，虽然它直接把跨域问题甩锅给使用者，可我还是完成了这个功能。相信你能感受到我的不情愿吧，显然这不是重点，因为剧情的反转才是……

结果没高兴多久，测试同事就同我讲，客户提供的地址填进去以后，点击链接浏览器直接返回4XX，可明明这个地址敲到浏览器里就能打开啊……我脑海中快速地浮现出那道经典的面试题，浏览器里敲完地址按下回车的瞬间到底发生了什么？习惯性怀疑人生后，我发现居然是因为Referer的问题，从我们站点调转到客户站点的时候携带了Referer，虽然有很多种方法可以让浏览器禁止携带Referer，但我还是被这种历史性的错误搞得怀疑人生。因为人生最难的事情，就是“揣着明白装糊涂”和“揣着糊涂装明白”，所谓“假作真时真亦假”。

请注意区分**Referer**和**Referrer**这两个单词，眼尖的人会发现后者多了一个r，这有点像什么呢，大概类似于usr和user。我们总是不情愿地相信这是历史的错误，而固执地想要找到一种能自圆其说的理由。诚然，“前人栽树，后人乘凉”，可我实在不肯承认，这是一群卓越而智慧的先驱们，所创造出的某种高效简写。回顾一下，使用Referer的场合，基本都是在HTTP头部，最常见的场景就是防盗链，Nginx能用Referer判断访问者来源，爬虫就能用Referer和UserAgent伪造访问者身份。那什么时候用Referrer呢？我目前发现是在a标签的rel属性里，例如下面的例子：
```HTML
<a rel="noreferrer" href="https://www.w3school.com.cn/tags/att_a_rel.asp">w3school</a>
```
除此之外，rel属性还支持像nofollow、friend、licence这样的属性，详细地大家可以参考[这里](https://www.w3school.com.cn/tags/att_a_rel.asp)。相信大家想到博主经历了什么了，没错，我就是按照平时的书写习惯写了Referer，然后被Web标准委员会给疯狂地嘲讽了。那么，为什么表达同一个含义的词会有两种写法？为什么有时候要用Referer，而有时候要用Referrer? 这特么到底是怎么一回事儿……带着这些疑问，让我们一起回顾野蛮生长的Web标准，为什么要埋这样一个坑在这里。

# 后世不忘，前世之锅？
故事要追溯到上个世纪90年代，当时HTTP协议中需要有一个用来表示页面或资源来源的请求头部，Philip Hallam-Baker将这个请求头部定义为Referer，并将其写入了[RFC1945](https://datatracker.ietf.org/doc/rfc1945/?include_text=1)，这就是著名的HTTP/1.0协议。

![HTTP/1.0协议中定义的Referer](https://i.loli.net/2019/12/07/GE2WydKMf6HSk5n.png)

然而这里发生一件有趣的事情，这个单词实际上是被作者给拼错了，即正确的拼写应该是`Referrer`。因为发现这个错误时为时已晚，大量的服务端和客户端都采用了这个错误的拼写，谁让它被写到了HTTP协议里呢？这其中就有像Nginx里的`ngx_http_referer_module`、Django里的`HttpRequest.META.HTTP_REFERER`等等。考虑到这个错误波及的范围过大，HTTP标准制定者奉决心将错就错，于是在接下来的[RFC2616](https://datatracker.ietf.org/doc/rfc2616/?include_text=1)，即HTTP/1.1中，HTTP标准制定者追加了针对这个错误的说明:

![HTTP/1.1协议中定义的Referer](https://i.loli.net/2019/12/07/IwMpYPSls485CHx.png)

说到这里，大家至少明白了一件事情，这个错误的`Referer`其实是指`Referrer`。对于标准写错了这件事情，大家其实都能理解，因为只要是人就免不了会出错。可为什么不能一错到底呢？既然要使用`Referer`这个错误的拼写，那就一直这样错下去好了，为什么特么又冒出来个`Referrer`，虽然它的拼写的确是对的，可不统一的写法还是会让人抓狂啊！君不见`main`和`mian`傻傻分不清，君不见C++里`false`与`flase`的神奇宏定义。假如没有今天这个事情，我完全不知道还有`Referrer`的存在啊，可都拼错多少年了，我都把假当作真了，你突然这样搞，我还是会感到手足无措的啊！就像`Configuration`这个单词，虽然博主英语并不算太好，可至少敢拍着胸脯说这个单词没写错，结果有次我写对了反而让测试给我提了Bug，因为特么项目里定义的实际上是`Configuation`。你说，你这样让人崩溃不？

那么，为什么会有`Referrer`这个正确的拼写呢？这就要说到`Referrer-Policy`这个HTTP头部。不错，这次你没有看错，标准制定老爷们这次终于写对了。顾名思义，这是一种用来告诉浏览器应该如何发送Referer的策略。常见的取值有：no-referrer、no-referrer-when-downgrade、origin、origin-when-cross-origin、same-origin、strict-origin、strict-origin-when-cross-origin、unsafe-url，关于它们的含义及用途，大家可以参考[这里](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Referrer-Policy)。虽然我们经常吐槽JavaScript是一门垃圾语言，但是这一次，大家居然都非常齐心地统一了写法，譬如`DOM Level 2 `里定义的 `document.referrer`、`Fetch API`中的`Request`接口的`referrer`属性等，这一次都写对了。而Referrer-Policy除了和JavaScript可以集成以外，同样可以和HTML、CSS集成。博主一开始遇到的问题，实际上就是和HTML集成的一个场景。

```HTML
//meta标签里的'referrer'
<meta name="referrer" content="origin">
//出现在a, area, img, iframe, script, <link>等元素里的'referrer'
<a href="http://example.com" referrerpolicy="origin">
//出现在a, area, link等标签的rel属性里的'referrer'
<a href="http://example.com" rel="noreferrer">
```
而和CSS集成实际上就是style标签中的`referrerpolicy`属性，它默认是no-referrer-when-downgrade，我们可以在返回一个CSS文件的时候设置响应流的`Referrer-Policy`，或者是设置style标签中的`referrerpolicy`属性，这个就不展开讲啦！

# 本文小结

通过这次被标准制定者按在地上摩擦的经历，居然无意中收获了这样一段"迷人"的历史。假如JavaScript这里为了兼容历史错误而使用`Referer`的话，可能博主就不会一边吐槽这个错误，一边又乖乖地滚去读RFC2616。从这里可以得出一个结论：**HTTP 请求中的 Referer 是一个典型的拼写错误，历史悠久，可以预见还会一直错下去，以后 Referer 变成一个专有名词也说不定。所以一般涉及到读取 HTTP 请求头的场景，我们需要用 Referer 这种错误拼写(后端)；除此之外一般都要用 Referrer 这种正确的拼写(前端)**。有人说，使用JavaScript开发同构应用的体验非常好，恐怕从今天这篇博客以后要打个折扣，因为你刚刚在后端写完`referer`，转眼就要在前端写`referrer`，希望像博主这样的`伪全栈工程师`不会因此而精神分裂。实用主义者能用就行的策略，让这个错误在很多年以后还被人提起，假如这些标准制定者尚在人世的话，不知道会不会在浏览网页的时候，想起第一次起草`RFC1945`的那个下午。果然，历史还真是迷人啊！

