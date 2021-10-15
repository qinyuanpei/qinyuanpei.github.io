---
toc: true
title: 原生JavaScript实现Hexo博客推荐功能
categories:
  - 独立博客
tags:
  - Hexo
  - 推荐
  - 插件
copyright: true
abbrlink: 478946932
date: 2020-06-08 12:30:54
---
有时候，我不禁在想，我们到底处在一个什么样的时代呢？而之所以会有这样的疑问，则是因为我们的习惯在不断地被这个时代向前推进，就像我用了两年多的魅蓝Note6屏幕出现了问题，扫视了一圈新手机，居然再找不出一款带实体键的手机，刘海屏、水滴屏、破孔屏、异形屏、曲面屏等等简直令人眼花缭乱，唯独没有一款让我感到熟悉的非全面屏手机。做软件的时候，会不明白那些似是而非的定制需求的差异，可为什么偏偏到了硬件的时候，大家就能被迫适应这些越来越同质化的东西呢？也许有和我一样怀念非全面屏的人，可对于这个时代而言，一切都好像无足轻重，喜欢魅族对产品的设计，喜欢小而美的不妥协，可当大家都越来越相似的时候，`也许，是因为我们终于都长大了吧，而怀念则是一种可有可无、甚至有一点多余的东西`。在被告知一切向前看的路上，我们能拥有、用留住的东西本就不多，可偏偏我们就在给世间一切东西，努力地刻上时间的温度，经历着花繁叶茂，经历着落叶归根。

写博客，曾经是件很有意思的事情，透过网页去读每条留言背后的人，常常令你产生神交已久的感觉，即便网络如此发达的今天，让一个人失散，无非是动动手指拉黑、删除。`陈星汉`先生有一款游戏作品叫做`《风之旅人》`，游戏里的玩家依靠某种微弱的信号相互联系，而一旦失散彼此，将永远迷失在浩瀚无际的沙海里，你说，这是不是有人生本身的意味在里面呢？再后来140个字符的微博开始流行，而这些沉迷在博客时代里的人们，或固执地继续在博客这一方天地里挥洒，或搭乘移动互联网的“高铁”通往新的彼岸。有人这样比喻朋友圈和微博，说朋友圈装饰别人梦境的月亮，而微博则是装饰自己梦境的镜子。其实呢，在隐私问题基本荡然无存的今天，我们都只是在装饰资本的“窗户”吧！

曾经运营过一段时间的微信公众号，最后发觉还是博客的载体更适合自己，虽然这些年没少为博客投入“钱财”，在博客时代一去不复返的时间禁锢里，通过博客来盈利的想法堪堪聊以自慰，更不必说后来流行起来的“在线教育”和Vlog。有人说，靠工资是没有办法挣到钱的，挣钱要靠这些“睡后收入”，可当一件事物风头正盛的时候，彼时的你不足以追逐这一切的时候，这种感觉该如何言明呢？大概就像你在最落魄的时候，遇到一生中最想要保护的那个人一样，这听起来多少有点讽刺，人在不成熟的时候，总是后知后觉，可有一天真成熟了，再难有那时的运气或是豪气。所以呢，继续写下去吧，也许有一天，当你看着从前写的幼稚的文字，或哭或笑皆可入题，这不就是“嬉笑怒骂，皆成文章”了吗？

果然，一不小心又扯远了。虽然说博客平时没什么流量，可像搜索引擎优化(`SEO`)、前端构建(`CI/CD`)、`PWA`等等这些东西倒是有所钻研，提高博客访问量的方式除了增加搜索引擎里的权重和曝光率以外，其实，还有一种方式就是减少跳出时间。换句话说，访客在你博客里停留的时间越长，这意味着你有更多的内容可以被对方访问到，所以，增加内链是一个不错的思路。最直接的方式，就是在每篇博客结束以后推荐相关的博客供访客继续阅读。之前曾经尝试过像 [hexo-recommended-posts](https://github.com/huiwang/hexo-recommended-posts) 这样的插件，坦白说效果不是特别好，因为有时候加载这些站外的内容，导致博客页面打开的时候异常卡顿，所以，我们今天将采用原生的JavaScript来为Hexo实现博客推理功能，希望对大家有所启发。

首先，我们来说说原理，推荐系统一般是需要一部分量化的指标来表征不同内容的相关性的。譬如通过`TF-IDF`来计算文本的相似度，通过公共词袋中的词频构造向量再配合余弦公式来计算，通过`TextRank`这类借鉴`PageRank`思想的方法来计算等等。这里呢，我们不采用这些方法来实现，主要是考虑到200篇左右的博客，两两计算相似度特别耗费时间，对于Hexo这种静态博客而言，我们还是应该节省生成静态页面的时间，虽然这部分时间都是`Travis CI`去跑的(逃……。我们采用的方案是基于标签和日期的推荐方式，即根据当前文章的标签筛选相同标签的文章，根据当前文章的日期筛选相同日期的文章。有了这两种策略，配合Hexo中提供的全局变量，我们可以很容易地编写出下面的代码：
```JavaScript
<%
    function shuffle(a) {
        for (let i = a.length; i; i--) {
            let j = Math.floor(Math.random() * i);
            [a[i - 1], a[j]] = [a[j], a[i - 1]];
        }
        return a;
    }

    function recommended_posts(page, site, limit = 5) {
        page.tags = page.tags || []
        if (page.tags.length == 0) return [];
        let pageTags = page.tags.map(x=>x.name);
        let sitePosts = site.posts.toArray().map(x=> {
            return {tags:x.tags.toArray().map(y=>y.name), title:x.title, permalink:x.permalink, date:x.date}
        });
        let relatedPosts = pageTags.map(x=>sitePosts.filter(y=>y.title != page.title  && (y.tags.indexOf(x) != -1 || y.date.format('MM/DD') == page.date.format('MM/DD')))).reduce((prev,next)=>{
            return prev.concat(next);
        },[]);
        return shuffle(Array.from(new Set(relatedPosts))).slice(0, limit);
    }
%>
<% var post_list = recommended_posts(page, site, config.recommended_posts.limit) %>
<% if(post_list.length > 0 && config.recommended_posts.enable) { %>
<div class="recommended_posts">
    <h1><%= config.recommended_posts.title %></h1>
    <ul>
        <% post_list.forEach(function(link) { %>
        <li><a href="<%= link.permalink %>"><%= link.title %></a></li>
        <% }) %>
    </ul>
</div>
<% } %>
```
代码非常直白，按照标签和日期两种策略筛选出文章，打乱顺序后从中提取出若干个返回，而剩下的工作，就是将其渲染到页面中。在这里，博主单独定义了一个模板文件，所以，我们在博客的适当位置引入即可，博主是放在博客结束以后的位置：
```HTML
<div class="post-content" id="post-content" itemprop="postContent">
    <%- post.content %>
    <%- partial('post/recommended_posts') %>
</div>
```
最终实现的效果如下图所示：

![本文实现的相关文章推荐功能](https://s1.ax1x.com/2020/06/16/NibBjJ.png)

当然，当你看到这篇博客的时候，你已经看到博主为你推荐的内容了，是否有兴趣继续读下去呢？如果这样的话，就说明这两个内容是相关的。而基于日期的推荐，即所谓的“去年今日”，它本身的相关性可能并不强，但可以让你产生一种强烈的对比感，原来，这一天我是这样度过的啊。好了，这就是这篇博客的内容啦，晚安～
