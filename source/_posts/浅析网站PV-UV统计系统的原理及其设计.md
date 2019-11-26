---
title: 浅析网站PV/UV统计系统的原理及其设计
categories:
  - 数据存储
tags:
  - 访问量
  - Nginx
  - Hyperlog
abbrlink: 3494408209
date: 2019-10-22 12:50:49
---
国庆节前有段时间，新浪的“图床”一直不大稳定，因为新浪开启了防盗链，果然免费的永远是最贵的啊。为了不影响使用，我非常粗暴地禁止了浏览器发送Referer，然后我就发现了一件尴尬的事情，“不蒜子”统计服务无法使用了。这是一件用脚后跟想都能想明白的事情，我禁止了浏览器发送Referer，而“不蒜子”正好使用Referer来识别每个页面，所以，这是一个再明显不过的因为需求变更而引入的Bug。这个世界最离谱的事情，就是大家都认为程序员是一本“十万个为什么”，每次一出问题就找到程序员这里。其实，程序员是再普通不过的芸芸众生里的一员，人们喜欢听/看到自己愿意去听/看到的事物，而程序员同样喜欢解决自己想去解决的问题。所以，今天的话题是关于如何设计一个PV/UV统计系统。OK，Let's Hacking Begin。

# PV/UV的概念

首先，我们从两个最基本的概念PV和UV开始说起。我们都知道，互联网产品的核心就是流量，前期通过免费的产品吸引目标客户的目的，在积累了一定用户流量以后，再通过广告等增值服务实现盈利，这可以说是互联网产品的典型商业模式啦。而在这个过程中，为了对一个产品的流量进行科学地分析，就产生了譬如访客数(**UV**)、浏览量(**PV**)、访问次数(**VV**)等等的概念，这些概念通常作为衡量流量多少的指标。除此以外，我们还有类似日活跃用户(**DAU**)、月活跃用户(**MAU**)等等这种衡量服务用户粘性的指标，以及平均访问深度、平均访问时间、跳出率等等这种衡量流量质量优劣的指标。如果各位和我一样都写博客的话，对这些概念应该都不会感到陌生，因为我们多多少少会使用到诸如[百度站长](https://ziyuan.baidu.com/site/index)、[站长统计](https://www.umeng.com/)、[腾讯统计](https://ta.qq.com/#/)、[Google Analytics](https://developers.google.cn/analytics/devguides/reporting/?hl=zh-cn)这样的统计服务，这些统计服务可以让我们即时掌握博客的访问情况。博主目前使用了[腾讯统计](https://ta.qq.com/#/)来查看整个博客的流量情况，而每一篇博客的访问量则是通过**[“不蒜子”](http://busuanzi.ibruce.info/)**这个第三方服务，这里再次对作者表示感谢。

![使用腾讯统计来查看网站的流量情况](https://i.loli.net/2019/10/24/VN2ubT71aLK6eZp.png)


回到问题本身，PV，即**Page View**，**表示页面浏览量或者点击量，每当一个页面被打开或者被刷新，都会产生一次PV，只要这个请求从浏览器端发送到了服务器端**。聪明的各位肯定会想到，如果我写一个爬虫不停地去请求一个页面，那么这个页面的PV不就会一直增长下去吗？理论上的确是这样，所以，我们有第二个指标UV，来作为进一步的参考，所谓UV，即**Unique Visitor，表示独立访客数**。在上面这个问题中，尽管这个页面的PV在不断增长，可是因为这些访客的IP都是相同的，所以，这个页面只会产生一次UV，这就是PV和UV的区别。所以，我们结合这两个指标，可以非常容易得了解到，这个页面实际的访问情况是什么样的。这让我想起数据分析中的一个例子，虽然以统计学为背景的数学计算不会欺骗人类，可如果人类片面地相信某一个方面的分析结果，数据分析一样是带有欺骗性的。就像有人根据《战狼2》和《前任3》两部电影的观众购买冷/热饮的情况，得出下面的结论：**看动作片的观众更喜欢喝冷饮来清凉紧绷着的神经，而看爱情片的观众更喜欢喝热饮来温暖各自的内心**。其实想想就知道这里混淆了因果性和相关性，选择冷饮还是热饮无非是两部电影上映的季节不同而已。

# 如何设计一个访问统计系统
OK，了解了PV和UV的概念后，我们来思考如何去设计一个访问统计系统，这是今天这篇博客的主题内容。我知道，如果问如何设计一个访问系统，大家可能都会不由自主地想到建两张表。的确，这是最简单的做法。可问题是，我们对于PV的认识，其实一直都在不断地变化着。比如PV的定义是是一个页面被打开或者被刷新时视为一次有效PV，所以，我们通常的做法是在页面底部嵌入JavaScript脚本，这种方式一直工作得非常好。可在引入AJAX以后，用户几乎不会主动去刷新页面，那么，在这个过程中用户点击**更多**或者使用**下拉刷新**时，是否应该算作一次有效PV呢？甚至在PC端网页逐渐式微以后，越来越多的工作转移到手机等移动设备上来，越来越多的原生+Web混合App或者是单页面应用(**SPA**)或者是渐进式应用(**PWA**)，此时我们又该如何认识PV呢？微信公众号里的PV甚至更为严格，必须通过微信内置的浏览器访问才能算作一次有效PV。

可以发现，我们对PV的认识其实一直在不断的变化着，更多的时候，我们想追踪的并非页面被加载(**Page Load**)的次数，而是页面被浏览(**Page View**)的次数。这时候，我们可以Page Visiblity和History API结合的方式。前者在页面的visibilityState可见或者由隐藏变为可见时发送一次Page View，而后者则是在浏览器地址发生变化的时候发送一次Page View。这听起来非常像单页面应用(**SPA**)里前端路由的那套玩法，的确，当一个地址中的pathname或者search部分发生变化时，应该发送一次Page View请求，而hash部分的变化则应该忽略，因为它表示的是应用内部页面的跳转。对于页面的visibilityState由隐藏变为可见，不同的人有不同的看法，因为有时我们像合并多次Page View，而有时候则想通过Page View了解所谓的”回头客“，所以，这里面还可以继续引入Session的概念，比如Google Analytics默认会在30分钟内无交互的情况下结束。所以，这个问题要考虑的东西实际上比想象中的要多。

现在，我们至少可以前端部分达成共识，即通过在前端页面上埋点的方式收集PV和UV。就像我们设计一个Page View的表结构会非常简单，而一旦要开始考虑Unique Visitor，可能我们就需要收集诸如IP、省市、UA等等的信息，这些信息的数量会非常大，而Page View的数据规模实际上取决于一个站点下有多少个页面。所以，这些数据在后端要怎么样处理，这是我们接下来要去考虑的问题。直接去写数据库是万不得已的做法，因为如果你处理不好并发的问题，这些统计数据的正确性就会让人产生怀疑，所以，接下来，我们介绍三种不同的方法来处理这类问题，它们分别是：通过Nginx的access_log实现统计、通过Redis的Hyperlog实现统计，以及通过LeanCloud的Hook实现统计。同大家一样，我是第一次考虑这类问题，如果有什么不周到的地方，希望大家可以谅解。

## 通过Nginx的access_log实现统计

我们首先来介绍Nginx的access_log，顾名思义，这是Nginx的访问日志，由ngx_http_log_module模块提供相应功能。Nginx会把每一个用户访问网站的日志信息记录到指定文件里，从而帮助网站提供者分析用户的浏览行为。而PV/UV则是分析用户的浏览行为的最基础指标，所以，通过Nginx的访问日志来统计UV和PV是再合适不过的啦！在Nginx里主要使用`log_format`和`access_log` 两条指令来完成相关的配置。这里以博主自己使用的配置为例来说明：
```Shell
    log_format main '$remote_addr - $remote_user [$time_iso8601] "$request" '
                      '$status $body_bytes_sent "$http_referer" '
                      '"$http_user_agent" "$http_x_forwarded_for"';
                      
    access_log logs/access.log main;
```
可以注意到，我们在这里首先通过`log_format`命令定义了一个日志格式，而这个日志格式则被定义为main，这表示我们我们可以在Nginx的配置文件中定义多个日志格式。它其实就是一个日志模板，相信大家在使用NLog、Log4Net这类日志库的时候，都接触过Layout这个概念，这里就是Nginx中访问日志的Layout。那么，在定义了这样一个日志格式以后，我们该怎么使用这个日志格式呢？这就要说到下面的`access_log`指令，它的基本用法就是一个路径 + 一个模板，在这里我们使用了定义好的main模板，然后指定了日志路径为：\logs\localhost.access_log.log。当然啦，大家使用NLog和Log4Net时，日志对应的Layout中都会有“变量”这样的概念，同样地，在Nginx中我们有一些常用的“变量”：

| Nginx日志变量 | 说明 |
| ------------------- | :--------------------------- |
| $remote_addr | 记录访问网站的客户端地址 |
| $http_x_forward_for | 当前端有代理服务器时，设置Web节点记录客户端地址的配置 |
| $remote_user | 远程客户端用户名称 |
| $time_local | 记录带时区的访问时间 |
| $request | 记录用户HTTP请求起始行信息 |
| $status | 记录用户HTTP请求状态码 |
| $body_bytes_sents | 记录服务端返回给客户端响应Body字节数 |
| $http_referer | 记录本次请求是从哪一个链接访问过来的 |
| $http_user_agent | 记录客户端类型信息，比如Chrome、微信等等 |

为什么说这些时最常用的“变量”呢？因为通过这些，我们想要统计PV和UV的想法就能变成现实，关于更多的Nginx日志变量，大家可以从这里来了解：[http://nginx.org/en/docs/http/ngx_http_log_module.html](http://nginx.org/en/docs/http/ngx_http_log_module.html)。现在，通过Nginx托管一个简单的静态页面，然后在浏览器中访问：localhost:9090，此时，我们应该可以在前面设置的日志路径里找到Nginx生成的日志文件，它大概长下面这个样子：

![Nginx日志长什么样子](https://i.loli.net/2019/10/24/sGT7QYRWariKDHz.png)

OK，现在有日志文件啦，这PV/UV到底从哪里来呢？其实，到这里已经无所谓用什么方法啦，因为你可以用ELK全家桶把给它收集了去，或是选一门你喜欢的语言用正则给它匹配出来，这都完全没有问题，无非就是一个工具选择的问题。为了简单起见，我们直接用Shell命令：

```shell
#统计指定页面的PV
grep / localhost.access.log | wc -l
grep /favicon.ico localhost.access.log | wc -l

#统计站点PV
awk '{print $6}' localhost.access.log | wc -l #$6表示模板中的第6个变量，即Referer

#统计访客IP
awk '{print $1}' localhost.access.log | sort -r |uniq -c |wc -l #$1表示模板中第一个变量，即客户端IP

```

至此，我们就达到了基于Nginx访问日志实现PV/UV统计的目的。我知道有同学要问啦，你不是说要在前端通过埋点的方式来收集访客的信息吗，你这说了半天，完全就是说Nginx的事情嘛！的确，我们现在可以统计出自己网站的PV/UV了，可如果我们想对外提供一个访问统计的服务，我们又该如何做呢？这里简单分享下博主的思路，因为开发环境一直不是很稳定，所以，一直没有时间动手去实践(逃。
![一种PV/UV统计的思路](https://i.loli.net/2019/11/25/DBj7SxOa8qf1FZH.png)
通过这张图片，我们可以大致梳理出整个流程，即前端页面中通过JavaScript来调用后端提供的Analysis Service，此时这个请求会携带一个Referer信息，而这个Referer对应被访问的站点。注意到这个后端服务经过了一层Nginx转发，显然Nginx可以获得客户端的IP地址，这两个结合起来，表示的就是某个IP访问了某个站点，即PV。像百度站长和腾讯统计会在页面中注入一个token或者Id，主要用途就是确保请求的确是从当前站点中发出的，这就是这类访问统计产品统计的原理。也许在计算PV/UV的算法上存在差异，然而核心的原理应该没多大差别啦！

## 通过Redis的HyperLogLog实现统计

不知道大家有没有发现，统计PV其实蛮简单的，因为它只需要对访问量做更新即可。可统计UV就会有点麻烦啦，因为同一个人可以多次访问同一篇文章。有时候我们希望统计一天内的访客数，而有时候我们希望统计一周甚至一个月内的访客数，所以，UV并不像PV那样简单，PV更多的时候是作为一种“汇总”数据，而UV则有“实时”的属性。简而言之，我们需要一张表来记录访客数据，博主在设计这张表的时候，更是引入了地理位置、UserAgent等等相关的字段设计，因为我们会有了解访客来源、访客设备等等一系列“行为”相关的数据记录。对应到数据库的概念，VisitorRecored这张表实际上是在不停地写入记录的。那么，面对每一个查看实时访客数的请求，我们真的要每次都要去这张表里统计一遍吗？也许我们会想到使用数据库任务去做定时的汇总，或者是任意形式的定时任务譬如CORN、Hangfire，在这里，我们有更好的选择——HyperLogLog。

什么是HyperlLogLog呢？我们提到的统计UV的这个场景，实际上是一个基数计数(Cardinality Counting)的问题，即统计一个集合中不重复的元素个数，例如集合{1,3,5,7,5,7,8}的基数为5。所以，HyperLogLog实际上就是一个在误差允许的范围内，快速统计元素数目的算法。为什么说是误差允许范围内呢？因为它来源于一个经典的概率分布——伯努利分布。高中时候，老师讲到这个知识，我们笑称它为“白努力”，因为有一段时间，排列组合属于我怎么学都学不会东西，可不就是白努力吗？HyperLogLog是在LogLog的基础上优化的一种算法，它主要的改进是采用了桶算法作为每一轮伯努利实验的估计值，同时使用调和平均数代替平均数，进而求出最终的估算值。它可以在不存储整个集合的情况下，使用极小的内存统计出集合元素的个数。

对应到Redis里，主要体现在PFADD、PFCOUNT、PFMERGE三个命令上。
* PFADD：将多个值存入指定的HyperLogLog。
* PFCOUNT：获取指定HyperLogLog的基数。
* PFMERGE：合并多个HyperLogLog，合并前与合并后的基数一致(取并集)。

博主在写这篇博客的时候，基于LeanCloud的访问统计[LeanCloud-Counter]()已经再线上运行了一段时间。下面，我们就以这些数据为例来展示下HyperLogLog的用法。为了方便起见，我选择使用Python来读写Redis：
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

## 通过LeanCloud的Hooks实现统计

像Hexo、Jekyll这类静态博客，本质上是非常依赖Valine、不蒜子等等的第三方服务，而使用LeanCloud作为访问量统计的服务提供商，更是早就在博客圈子里流行了。不过我注意到，这些设计都少都会有一点不足，那就是网上的各种设计都没有实现站点的PV/UV统计。当我被迫从”不蒜子“上迁移过来以后，我其实非常想实现一个和”不蒜子“一模一样的统计服务，因为这样子的话，我对博客的修改会非常非常小。所以， 我不得不在现有方案上扩展更多的功能，实现单篇文章的UV、整个站点的PV/UV、访客IP/地理位置、客户端UA等的统计功能。

在这个过程中，我发现LeanCloud不支持传统关系型数据库里的Sum()操作，而我更不想在客户端通过分页去对表记录做Sum()操作。官方提供了离线分析和云函数，可这两个东西都是商业版里支持的东西。最终我找到了，通过Hooks来实现站点PV/UV统计的这样一种方法。所谓Hooks，你可以理解为传统关系型数据库里的触发器，它可以在你更新或者插入某个对象的时候，去做一点额外的工作。所以，单篇文章会根据文章链接+访客IP生成一条UV，而PV则是每次打开文章就视为一条PV。所以，最终的方案是插入访客记录(**VisitorRecord**)时更新文章的对应的访问次数(**VisitorCounter**)，而单篇文章的更新则会触发站点UV/PV的更新。听起来有点绕人，我们直接来看下面的代码：
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

实际上这里整个站点的UV统计是不严谨的，因为严格地来讲，同一个IP访问了同一个站点下的N篇文章，它的UV严格地来说应该算1次，可我们这个方案本身就是向LeanCloud妥协的一种做法，就像我这里直接使用了`location.href`和`document.title`，它带来的问题就是，一个网站的域名或者链接发生变化的时候，访问统计就会被重置从0开始。“不蒜子”本身就有这个问题。所以，博主这个博客从15年到现在，总访问量只有3万多，就是因为中间更换过两次域名。从我切换到自己写的统计服务以后，我发现每天来读我博客的人居然不少，我实在不忍心写下这种夸自己的句子啊！

想解决这个问题，并不是没有办法。像博主一开始设计的时候，是打算用每个页面唯一的Id来存储的，而这就要通过HTML5中的**data-**或者通过JavaScript来传参。可当你打算设计一个更通用的东西的时候，这些想法就显得有点多余，我和大部分人一样，喜欢开箱即用的东西，所以，最好它可以像大多数统计服务一样，只需要在页面里加入一行JavaScript脚本。所以，最终采用这样的设计是为了最大限度的开箱即用。考虑到“不蒜子”里因为更换域名而导致的访问统计重置的问题，我增加了一个初始化站点UV/PV的功能，满足了像博主这样虚荣心爆棚的人的需要。这一刻，我突然觉得，我和产品经理们一样“自信”啊。正如你所看到的这样，博客底部的访问统计已经从“不蒜子”切换到“LeanCloud-Counter”，为此我在博客上增加了[LeanCloud](https://leancloud.cn)的链接，也许下一阶段会加上Heroku，总之，我已经完成了访问统计的平滑切换。关于这个项目，如果大家感兴趣，可以参考这个地址：[LeanCloud-Counter](https://github.com/qinyuanpei/leancloud-counter)。

# 本文小结
这篇文章写下来，最大的感受或许是，有一台Linux环境的服务器是多么的重要。起初，是在Windows10下面的WSL里搭了Docker环境，再通过Docker镜像搭建Nginx，因为之前的Consul、ELK几乎都是这样运作的，而且一直运行的相当稳定，唯一的缺点大概就是Docker太容易吃硬盘，有时候难免搞出个内存不足。Nginx搭好以后，发现需要经常改配置文件，Docker环境里改起来相当痛苦。直接在WSL里安装Nginx的话，因为和Windows共享端口，和IIS明显搞不到一起。想通过Docker挂载本机分区，突然想起来WSL里的Docker只是一个客户端，真正的主角是跑在Windows上的Docker for Windows。最后被迫装了Windows版本的Nginx，果然还是会和IIS冲突，我想说，心好累有木有啊_(:з」∠)_。好了，这篇博客总算写完了！