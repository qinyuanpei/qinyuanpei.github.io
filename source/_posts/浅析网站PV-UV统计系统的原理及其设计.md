---
abbrlink: 3494408209
categories:
- 数据存储
date: 2019-10-22 12:50:49
description: 至此，我们就达到了基于 Nginx 访问日志实现 PV/UV 统计的目的;考虑到“不蒜子”里因为更换域名而导致的访问统计重置的问题，我增加了一个初始化站点 UV/PV 的功能，满足了像博主这样虚荣心爆棚的人的需要;实际上这里整个站点的 UV 统计是不严谨的，因为严格地来讲，同一个 IP 访问了同一个站点下的 N 篇文章，它的 UV 严格地来说应该算 1 次，可我们这个方案本身就是向 LeanCloud 妥协的一种做法，就像我这里直接使用了`location.href`和`document.title`，它带来的问题就是，一个网站的域名或者链接发生变化的时候，访问统计就会被重置从 0 开始
tags:
- 访问量
- Nginx
- Hyperlog
title: 浅析网站 PV/UV 统计系统的原理及其设计
---

国庆节前有段时间，新浪的“图床”一直不大稳定，因为新浪开启了防盗链，果然免费的永远是最贵的啊。为了不影响使用，我非常粗暴地禁止了浏览器发送 Referer，然后我就发现了一件尴尬的事情，“不蒜子”统计服务无法使用了。这是一件用脚后跟想都能想明白的事情，我禁止了浏览器发送 Referer，而“不蒜子”正好使用 Referer 来识别每个页面，所以，这是一个再明显不过的因为需求变更而引入的 Bug。这个世界最离谱的事情，就是大家都认为程序员是一本“十万个为什么”，每次一出问题就找到程序员这里。其实，程序员是再普通不过的芸芸众生里的一员，人们喜欢听/看到自己愿意去听/看到的事物，而程序员同样喜欢解决自己想去解决的问题。所以，今天的话题是关于如何设计一个 PV/UV 统计系统。OK，Let's Hacking Begin。

# PV/UV 的概念

首先，我们从两个最基本的概念 PV 和 UV 开始说起。我们都知道，互联网产品的核心就是流量，前期通过免费的产品吸引目标客户的目的，在积累了一定用户流量以后，再通过广告等增值服务实现盈利，这可以说是互联网产品的典型商业模式啦。而在这个过程中，为了对一个产品的流量进行科学地分析，就产生了譬如访客数(**UV**)、浏览量(**PV**)、访问次数(**VV**)等等的概念，这些概念通常作为衡量流量多少的指标。除此以外，我们还有类似日活跃用户(**DAU**)、月活跃用户(**MAU**)等等这种衡量服务用户粘性的指标，以及平均访问深度、平均访问时间、跳出率等等这种衡量流量质量优劣的指标。如果各位和我一样都写博客的话，对这些概念应该都不会感到陌生，因为我们多多少少会使用到诸如[百度站长](https://ziyuan.baidu.com/site/index)、[站长统计](https://www.umeng.com/)、[腾讯统计](https://ta.qq.com/#/)、[Google Analytics](https://developers.google.cn/analytics/devguides/reporting/?hl=zh-cn)这样的统计服务，这些统计服务可以让我们即时掌握博客的访问情况。博主目前使用了[腾讯统计](https://ta.qq.com/#/)来查看整个博客的流量情况，而每一篇博客的访问量则是通过**[“不蒜子”](http://busuanzi.ibruce.info/)**这个第三方服务，这里再次对作者表示感谢。

![使用腾讯统计来查看网站的流量情况](https://i.loli.net/2019/10/24/VN2ubT71aLK6eZp.png)


回到问题本身，PV，即**Page View**，**表示页面浏览量或者点击量，每当一个页面被打开或者被刷新，都会产生一次 PV，只要这个请求从浏览器端发送到了服务器端**。聪明的各位肯定会想到，如果我写一个爬虫不停地去请求一个页面，那么这个页面的 PV 不就会一直增长下去吗？理论上的确是这样，所以，我们有第二个指标 UV，来作为进一步的参考，所谓 UV，即**Unique Visitor，表示独立访客数**。在上面这个问题中，尽管这个页面的 PV 在不断增长，可是因为这些访客的 IP 都是相同的，所以，这个页面只会产生一次 UV，这就是 PV 和 UV 的区别。所以，我们结合这两个指标，可以非常容易得了解到，这个页面实际的访问情况是什么样的。这让我想起数据分析中的一个例子，虽然以统计学为背景的数学计算不会欺骗人类，可如果人类片面地相信某一个方面的分析结果，数据分析一样是带有欺骗性的。就像有人根据《战狼 2》和《前任 3》两部电影的观众购买冷/热饮的情况，得出下面的结论：**看动作片的观众更喜欢喝冷饮来清凉紧绷着的神经，而看爱情片的观众更喜欢喝热饮来温暖各自的内心**。其实想想就知道这里混淆了因果性和相关性，选择冷饮还是热饮无非是两部电影上映的季节不同而已。

# 如何设计一个访问统计系统
OK，了解了 PV 和 UV 的概念后，我们来思考如何去设计一个访问统计系统，这是今天这篇博客的主题内容。我知道，如果问如何设计一个访问系统，大家可能都会不由自主地想到建两张表。的确，这是最简单的做法。可问题是，我们对于 PV 的认识，其实一直都在不断地变化着。比如 PV 的定义是是一个页面被打开或者被刷新时视为一次有效 PV，所以，我们通常的做法是在页面底部嵌入 JavaScript 脚本，这种方式一直工作得非常好。可在引入 AJAX 以后，用户几乎不会主动去刷新页面，那么，在这个过程中用户点击**更多**或者使用**下拉刷新**时，是否应该算作一次有效 PV 呢？甚至在 PC 端网页逐渐式微以后，越来越多的工作转移到手机等移动设备上来，越来越多的原生+Web 混合 App 或者是单页面应用(**SPA**)或者是渐进式应用(**PWA**)，此时我们又该如何认识 PV 呢？微信公众号里的 PV 甚至更为严格，必须通过微信内置的浏览器访问才能算作一次有效 PV。

可以发现，我们对 PV 的认识其实一直在不断的变化着，更多的时候，我们想追踪的并非页面被加载(**Page Load**)的次数，而是页面被浏览(**Page View**)的次数。这时候，我们可以 Page Visiblity 和 History API 结合的方式。前者在页面的 visibilityState 可见或者由隐藏变为可见时发送一次 Page View，而后者则是在浏览器地址发生变化的时候发送一次 Page View。这听起来非常像单页面应用(**SPA**)里前端路由的那套玩法，的确，当一个地址中的 pathname 或者 search 部分发生变化时，应该发送一次 Page View 请求，而 hash 部分的变化则应该忽略，因为它表示的是应用内部页面的跳转。对于页面的 visibilityState 由隐藏变为可见，不同的人有不同的看法，因为有时我们像合并多次 Page View，而有时候则想通过 Page View 了解所谓的”回头客“，所以，这里面还可以继续引入 Session 的概念，比如 Google Analytics 默认会在 30 分钟内无交互的情况下结束。所以，这个问题要考虑的东西实际上比想象中的要多。

现在，我们至少可以前端部分达成共识，即通过在前端页面上埋点的方式收集 PV 和 UV。就像我们设计一个 Page View 的表结构会非常简单，而一旦要开始考虑 Unique Visitor，可能我们就需要收集诸如 IP、省市、UA 等等的信息，这些信息的数量会非常大，而 Page View 的数据规模实际上取决于一个站点下有多少个页面。所以，这些数据在后端要怎么样处理，这是我们接下来要去考虑的问题。直接去写数据库是万不得已的做法，因为如果你处理不好并发的问题，这些统计数据的正确性就会让人产生怀疑，所以，接下来，我们介绍三种不同的方法来处理这类问题，它们分别是：通过 Nginx 的 access_log 实现统计、通过 Redis 的 Hyperlog 实现统计，以及通过 LeanCloud 的 Hook 实现统计。同大家一样，我是第一次考虑这类问题，如果有什么不周到的地方，希望大家可以谅解。

## 通过 Nginx 的 access_log 实现统计

我们首先来介绍 Nginx 的 access_log，顾名思义，这是 Nginx 的访问日志，由 ngx_http_log_module 模块提供相应功能。Nginx 会把每一个用户访问网站的日志信息记录到指定文件里，从而帮助网站提供者分析用户的浏览行为。而 PV/UV 则是分析用户的浏览行为的最基础指标，所以，通过 Nginx 的访问日志来统计 UV 和 PV 是再合适不过的啦！在 Nginx 里主要使用`log_format`和`access_log` 两条指令来完成相关的配置。这里以博主自己使用的配置为例来说明：
```bash
    log_format main '$remote_addr - $remote_user [$time_iso8601] "$request" '
                      '$status $body_bytes_sent "$http_referer" '
                      '"$http_user_agent" "$http_x_forwarded_for"';
                      
    access_log logs/access.log main;
```
可以注意到，我们在这里首先通过`log_format`命令定义了一个日志格式，而这个日志格式则被定义为 main，这表示我们我们可以在 Nginx 的配置文件中定义多个日志格式。它其实就是一个日志模板，相信大家在使用 NLog、Log4Net 这类日志库的时候，都接触过 Layout 这个概念，这里就是 Nginx 中访问日志的 Layout。那么，在定义了这样一个日志格式以后，我们该怎么使用这个日志格式呢？这就要说到下面的`access_log`指令，它的基本用法就是一个路径 + 一个模板，在这里我们使用了定义好的 main 模板，然后指定了日志路径为：\logs\localhost.access_log.log。当然啦，大家使用 NLog 和 Log4Net 时，日志对应的 Layout 中都会有“变量”这样的概念，同样地，在 Nginx 中我们有一些常用的“变量”：

| Nginx 日志变量 | 说明 |
| ------------------- | :--------------------------- |
| $remote_addr | 记录访问网站的客户端地址 |
| $http_x_forward_for | 当前端有代理服务器时，设置 Web 节点记录客户端地址的配置 |
| $remote_user | 远程客户端用户名称 |
| $time_local | 记录带时区的访问时间 |
| $request | 记录用户 HTTP 请求起始行信息 |
| $status | 记录用户 HTTP 请求状态码 |
| $body_bytes_sents | 记录服务端返回给客户端响应 Body 字节数 |
| $http_referer | 记录本次请求是从哪一个链接访问过来的 |
| $http_user_agent | 记录客户端类型信息，比如 Chrome、微信等等 |

为什么说这些时最常用的“变量”呢？因为通过这些，我们想要统计 PV 和 UV 的想法就能变成现实，关于更多的 Nginx 日志变量，大家可以从这里来了解：[http://nginx.org/en/docs/http/ngx_http_log_module.html](http://nginx.org/en/docs/http/ngx_http_log_module.html)。现在，通过 Nginx 托管一个简单的静态页面，然后在浏览器中访问：localhost:9090，此时，我们应该可以在前面设置的日志路径里找到 Nginx 生成的日志文件，它大概长下面这个样子：

![Nginx日志长什么样子](https://i.loli.net/2019/10/24/sGT7QYRWariKDHz.png)

OK，现在有日志文件啦，这 PV/UV 到底从哪里来呢？其实，到这里已经无所谓用什么方法啦，因为你可以用 ELK 全家桶把给它收集了去，或是选一门你喜欢的语言用正则给它匹配出来，这都完全没有问题，无非就是一个工具选择的问题。为了简单起见，我们直接用 Shell 命令：

```bash
#统计指定页面的PV
grep / localhost.access.log | wc -l
grep /favicon.ico localhost.access.log | wc -l

#统计站点PV
awk '{print $6}' localhost.access.log | wc -l #$6表示模板中的第6个变量，即Referer

#统计访客IP
awk '{print $1}' localhost.access.log | sort -r |uniq -c |wc -l #$1表示模板中第一个变量，即客户端IP

```

至此，我们就达到了基于 Nginx 访问日志实现 PV/UV 统计的目的。我知道有同学要问啦，你不是说要在前端通过埋点的方式来收集访客的信息吗，你这说了半天，完全就是说 Nginx 的事情嘛！的确，我们现在可以统计出自己网站的 PV/UV 了，可如果我们想对外提供一个访问统计的服务，我们又该如何做呢？这里简单分享下博主的思路，因为开发环境一直不是很稳定，所以，一直没有时间动手去实践(逃。
![一种PV/UV统计的思路](https://i.loli.net/2019/11/25/DBj7SxOa8qf1FZH.png)
通过这张图片，我们可以大致梳理出整个流程，即前端页面中通过 JavaScript 来调用后端提供的 Analysis Service，此时这个请求会携带一个 Referer 信息，而这个 Referer 对应被访问的站点。注意到这个后端服务经过了一层 Nginx 转发，显然 Nginx 可以获得客户端的 IP 地址，这两个结合起来，表示的就是某个 IP 访问了某个站点，即 PV。像百度站长和腾讯统计会在页面中注入一个 token 或者 Id，主要用途就是确保请求的确是从当前站点中发出的，这就是这类访问统计产品统计的原理。也许在计算 PV/UV 的算法上存在差异，然而核心的原理应该没多大差别啦！

## 通过 Redis 的 HyperLogLog 实现统计

不知道大家有没有发现，统计 PV 其实蛮简单的，因为它只需要对访问量做更新即可。可统计 UV 就会有点麻烦啦，因为同一个人可以多次访问同一篇文章。有时候我们希望统计一天内的访客数，而有时候我们希望统计一周甚至一个月内的访客数，所以，UV 并不像 PV 那样简单，PV 更多的时候是作为一种“汇总”数据，而 UV 则有“实时”的属性。简而言之，我们需要一张表来记录访客数据，博主在设计这张表的时候，更是引入了地理位置、UserAgent 等等相关的字段设计，因为我们会有了解访客来源、访客设备等等一系列“行为”相关的数据记录。对应到数据库的概念，VisitorRecored 这张表实际上是在不停地写入记录的。那么，面对每一个查看实时访客数的请求，我们真的要每次都要去这张表里统计一遍吗？也许我们会想到使用数据库任务去做定时的汇总，或者是任意形式的定时任务譬如 CORN、Hangfire，在这里，我们有更好的选择——HyperLogLog。

什么是 HyperlLogLog 呢？我们提到的统计 UV 的这个场景，实际上是一个基数计数(Cardinality Counting)的问题，即统计一个集合中不重复的元素个数，例如集合{1,3,5,7,5,7,8}的基数为 5。所以，HyperLogLog 实际上就是一个在误差允许的范围内，快速统计元素数目的算法。为什么说是误差允许范围内呢？因为它来源于一个经典的概率分布——伯努利分布。高中时候，老师讲到这个知识，我们笑称它为“白努力”，因为有一段时间，排列组合属于我怎么学都学不会东西，可不就是白努力吗？HyperLogLog 是在 LogLog 的基础上优化的一种算法，它主要的改进是采用了桶算法作为每一轮伯努利实验的估计值，同时使用调和平均数代替平均数，进而求出最终的估算值。它可以在不存储整个集合的情况下，使用极小的内存统计出集合元素的个数。

对应到 Redis 里，主要体现在 PFADD、PFCOUNT、PFMERGE 三个命令上。
* PFADD：将多个值存入指定的 HyperLogLog。
* PFCOUNT：获取指定 HyperLogLog 的基数。
* PFMERGE：合并多个 HyperLogLog，合并前与合并后的基数一致(取并集)。

博主在写这篇博客的时候，基于 LeanCloud 的访问统计[LeanCloud-Counter](.)已经再线上运行了一段时间。下面，我们就以这些数据为例来展示下 HyperLogLog 的用法。为了方便起见，我选择使用 Python 来读写 Redis：
```Python
# 连接Redis
r = redis.Redis(host='localhost', port=6379, db=0)

# 查询访客记录
VisitorRecord = leancloud.Object.extend('VisitorRecord')
query = VisitorRecord.query
query.limit(1000)
queryResults = query.find()

# 对每个页面使用PFADD
for result in queryResults:
    r.pfadd(result.get('page_url'),result.get('visitor_ip'))

# 使用PFCOUNT返回每个页面的基数
pageUrls = list(set(map(lambda x:(x.get('page_url'),x.get('page_title'),r.pfcount(x.get('page_url'))), queryResults)))
pageUrls = sorted(pageUrls,key=lambda x:x[2],reverse=True)
print(pageUrls[0:10])

```
运行完脚本，我们可以统计出访客数目：

![使用HyperLogLog统计访客数目](https://i.loli.net/2019/11/26/JxUQ9s1EiOlVBCY.png)

## 通过 LeanCloud 的 Hooks 实现统计

像 Hexo、Jekyll 这类静态博客，本质上是非常依赖 Valine、不蒜子等等的第三方服务，而使用 LeanCloud 作为访问量统计的服务提供商，更是早就在博客圈子里流行了。不过我注意到，这些设计都少都会有一点不足，那就是网上的各种设计都没有实现站点的 PV/UV 统计。当我被迫从”不蒜子“上迁移过来以后，我其实非常想实现一个和”不蒜子“一模一样的统计服务，因为这样子的话，我对博客的修改会非常非常小。所以， 我不得不在现有方案上扩展更多的功能，实现单篇文章的 UV、整个站点的 PV/UV、访客 IP/地理位置、客户端 UA 等的统计功能。

在这个过程中，我发现 LeanCloud 不支持传统关系型数据库里的 Sum()操作，而我更不想在客户端通过分页去对表记录做 Sum()操作。官方提供了离线分析和云函数，可这两个东西都是商业版里支持的东西。最终我找到了，通过 Hooks 来实现站点 PV/UV 统计的这样一种方法。所谓 Hooks，你可以理解为传统关系型数据库里的触发器，它可以在你更新或者插入某个对象的时候，去做一点额外的工作。所以，单篇文章会根据文章链接+访客 IP 生成一条 UV，而 PV 则是每次打开文章就视为一条 PV。所以，最终的方案是插入访客记录(**VisitorRecord**)时更新文章的对应的访问次数(**VisitorCounter**)，而单篇文章的更新则会触发站点 UV/PV 的更新。听起来有点绕人，我们直接来看下面的代码：
```JavaScript
//新建访客记录时，更新对应的UV记录
AV.Cloud.afterSave('VisitorRecord', async function(request) {
    var query = new AV.Query('VisitorCounter');
    var page_url = request.object.get('page_url');
    console.log('query page_url: ' + page_url);
    query.equalTo('page_url', page_url);
    return query.find().then(function (counters) {
        if (counters.length > 0){
            counters[0].increment('page_uv');
            console.log('increment UV of page_url: ' + page_url + ", " + counters[0].get('page_pv'));
            return counters[0].save()
        }
    });
});

//页面PV/UV更新时，更新站点PV/UV
AV.Cloud.afterUpdate('VisitorCounter', async function(request) {
    var page_url = request.object.get('page_url');
    if(page_url.indexOf('//') == -1){
        return;
    }
    var site_url = page_url.split('//')[1];
    site_url = site_url.substring(0, site_url.indexOf('/'));
    console.log('now to update site PV/UV with: ' + site_url);
    if (request.object.updatedKeys.indexOf('page_pv') != -1) {
        var query = new AV.Query('VisitorCounter');
        query.equalTo('page_url',site_url);
        query.find().then(function(counters){
            if(counters.length>0){
                counters[0].increment('page_pv');
                console.log('update site PV of ' + site_url + ", " + counters[0].get('page_pv'));
                return counters[0].save();
            }
        });
    } else if (request.object.updatedKeys.indexOf('page_uv') != -1) {
        var query = new AV.Query('VisitorCounter');
        query.equalTo('page_url',site_url);
        query.find().then(function(counters){
            if(counters.length>0){
                counters[0].increment('page_uv');
                console.log('update site PV of ' + site_url + ", " + counters[0].get('page_uv'));
                return counters[0].save();
            }
        });
    }
});
```

实际上这里整个站点的 UV 统计是不严谨的，因为严格地来讲，同一个 IP 访问了同一个站点下的 N 篇文章，它的 UV 严格地来说应该算 1 次，可我们这个方案本身就是向 LeanCloud 妥协的一种做法，就像我这里直接使用了`location.href`和`document.title`，它带来的问题就是，一个网站的域名或者链接发生变化的时候，访问统计就会被重置从 0 开始。“不蒜子”本身就有这个问题。所以，博主这个博客从 15 年到现在，总访问量只有 3 万多，就是因为中间更换过两次域名。从我切换到自己写的统计服务以后，我发现每天来读我博客的人居然不少，我实在不忍心写下这种夸自己的句子啊！

想解决这个问题，并不是没有办法。像博主一开始设计的时候，是打算用每个页面唯一的 Id 来存储的，而这就要通过 HTML5 中的**data-**或者通过 JavaScript 来传参。可当你打算设计一个更通用的东西的时候，这些想法就显得有点多余，我和大部分人一样，喜欢开箱即用的东西，所以，最好它可以像大多数统计服务一样，只需要在页面里加入一行 JavaScript 脚本。所以，最终采用这样的设计是为了最大限度的开箱即用。考虑到“不蒜子”里因为更换域名而导致的访问统计重置的问题，我增加了一个初始化站点 UV/PV 的功能，满足了像博主这样虚荣心爆棚的人的需要。这一刻，我突然觉得，我和产品经理们一样“自信”啊。正如你所看到的这样，博客底部的访问统计已经从“不蒜子”切换到“LeanCloud-Counter”，为此我在博客上增加了[LeanCloud](https://leancloud.cn)的链接，也许下一阶段会加上 Heroku，总之，我已经完成了访问统计的平滑切换。关于这个项目，如果大家感兴趣，可以参考这个地址：[LeanCloud-Counter](https://github.com/qinyuanpei/leancloud-counter)。

# 本文小结
这篇文章写下来，最大的感受或许是，有一台 Linux 环境的服务器是多么的重要。起初，是在 Windows10 下面的 WSL 里搭了 Docker 环境，再通过 Docker 镜像搭建 Nginx，因为之前的 Consul、ELK 几乎都是这样运作的，而且一直运行的相当稳定，唯一的缺点大概就是 Docker 太容易吃硬盘，有时候难免搞出个内存不足。Nginx 搭好以后，发现需要经常改配置文件，Docker 环境里改起来相当痛苦。直接在 WSL 里安装 Nginx 的话，因为和 Windows 共享端口，和 IIS 明显搞不到一起。想通过 Docker 挂载本机分区，突然想起来 WSL 里的 Docker 只是一个客户端，真正的主角是跑在 Windows 上的 Docker for Windows。最后被迫装了 Windows 版本的 Nginx，果然还是会和 IIS 冲突，我想说，心好累有木有啊_(:з」∠)_。好了，这篇博客总算写完了！