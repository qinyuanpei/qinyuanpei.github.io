---
abbrlink: 828223375
categories:
- 独立博客
date: 2015-03-24 10:32:39
description: 这段代码博主在本地使用NodeJS测试了没有不过什么问题，大家可以在截图中清楚地看到[music:29713754]已经被替换称了网易云音乐的Flash组件，这样在网页中就会显示出网易云音乐的播放器，我们就能听到这熟悉而温暖的旋律了
tags:
- 网易
- 云音乐
- 插件
- Hexo
title: 为Hexo开发一个网易云音乐的文章插件
---

&emsp;&emsp;当你打开这篇文章的时候，你听到一首熟悉的旋律，那是因为在你的心里始终装着一张泛黄的CD，你从来不愿意打开它，即使外表早已积满了灰尘，你依然视它如新的一般，我们喜欢把它叫做时光或者说是青春。

<!--more-->


&emsp;&emsp;正如你所看到的，我在博客文章中插入了网易云音乐的播放器。这是一个基于Flash技术实现的组件。因为博主特别喜欢网易云音乐这个音乐产品，所以博主想将这个播放器带入到我的博客。在博客中使用这个播放器，只要在文章中添加如下代码：
```HTML
<embed src="http://music.163.com/style/swf/widget.swf?sid=29713754&type=2&auto=1&width=278&height=32" 
width="298" height="52"  allowNetworking="all"></embed>
```
&emsp;&emsp;可是这样的结构对于一个写博客的人来说还是显得臃肿了，能不能让这个结构更简单写呢？简单到这样：
```
[music:29713754]
```
&emsp;&emsp;因为在这段代码中真正和音乐有关的只有sid这个参数，所以我们我们只需要关注这个参数就好了。那么，现在我们其实就是在做这样一件事情，我们在文章中插入这样一个[key:value]的结构，然后通过程序将它替换成相应的HTML结构，这样就实现了在Hexo的文章中使用[key:value]结构来编写简单插件的功能，如果经历过使用wordpress建站的朋友一定知道，在wordpress中存在许多这样的类似插件，可以帮助写作者简化某些输入内容。好了，那么今天我们就来试着为hexo编写这样一个小插件吧！为了避免将插件写到网页里的时候出现错误，我们首先在NodeJS中测试，测试程序如下：
```JavaScript
   //定义测试内容
   var str="这是一条测试内容以测试这个程序是否能够正确运行,现在让我们来听一首《匆匆那年》[music:29713754]";
   //获得匹配内容
   var dicts=str.match(/\[(.*?):(.*?)\]/g);
   if(dicts.length==0) return;
   //对每一个匹配项进行处理
   for(var i=0;i<dicts.length;i++)
   {
         //对匹配项进行分割,拆分结果为'[music'和'29713754]'
         //我TM就郁闷了，在这里写成'/:/'报错
         //可是写成/:/就顺利通过
         var dict=dicts[i].split(/:/);
         //获得键名
         var key=dict[0].substring(1,dict[0].length);
         //获得ID
         var id=dict[1].substring(0,dict[1].indexOf(']'));
         //判断键名的类型
         if(key=='music')
         {
            str=str.replace(dicts[i],'<embed src="http://music.163.com/style/swf/widget.swf?sid='+ id +
            '&type=2&auto=1&width=278&height=32" width="298" height="52"  allowNetworking="all"></embed>');
         }
    }
    //输出结果
    console.log(str);
```
&emsp;&emsp;这段代码主要就是通过正则表达式来匹配文章正文中所有的[key:value]结构，然后根据key来确定当前结构表什么类型，根据id来确定当前类型的参数，尽管这里只提到了一个music的类型，不过我相信只要大家开动脑筋、发挥想像相信会有更好的想法产生吧！这段代码博主在本地使用NodeJS测试了没有不过什么问题，大家可以在截图中清楚地看到[music:29713754]已经被替换称了网易云音乐的Flash组件，这样在网页中就会显示出网易云音乐的播放器，我们就能听到这熟悉而温暖的旋律了。

![NodeJS程序演示效果](https://ws1.sinaimg.cn/large/4c36074fly1fyzcv1i1qsj20is0cb74c.jpg)

&emsp;&emsp;不过真的想要吐槽下JavaScript。本来JavaScript就是弱类型了吧，NodeJS再给弄一个除了报错什么都不会的命令行，因此在本地调试JavaScript代码实在是太困难了。昨天为了写出一个正确的正则表达式奋战到三点钟，后来终于给写出来了，实在压抑不住内心的喜悦匆匆忙忙地就往模板里面放，结果刚放进去再重新生成页面地时候博客就华丽地挂了，尝试了若干次无果后，果断放弃然后用备份地主题文件进行了覆盖替换。总之，经过这次事情，我是再不想接触Javacript了，你不让我面向对象我可以容忍，因为JavaScript本来就不是一门面向对象的语言。可是你总得让我知道我写的这个变量是个什么类型吧？因为这个插件的编写涉及到JavaScript、NodeJS、Hexo所以整个过程中编程的效率特别低，因为在没有文档、没有语法提示的情况下来写这样一段代码，在我看来完全就是摸着石头过河啊！

&emsp;&emsp;好了，停止吐槽！我们接下来看看这段代码怎样和Hexo整个到一起。按照博主的理解既然我们要对文章的内容中的[key:value]结构进行替换，我们首先应该知道文章的内容在哪里。经过这么长时间对Hexo的学(zhe)习(teng),我们知道文章的内容是定义在layout\_partial下的article.ejs这个文件中，在这个文件中有一个叫做item的变量,这个item的真实身份其实是Hexo中定义的一个全局变量post。顾名思义，这个post就是我们发表的文章啦，它有一个重要的属性叫做content，就是我们这里要用到的东西了。我们来article.ejs这个文件中定义的一段代码：
```HTML
    <div class="entry">
      <% if (item.excerpt && index){ %>
        <%- item.excerpt %>
      <% } else { %>
      　　　<% if (!index){ %>
                <% if (!index && item.toc){ %>
                   <%- partial('extra/toc') %>
                <% } %>
                <%- item.content %>
        　　<% } else { %>
        　　　　<%- item.content.substring(0,item.content.indexOf('\n')) %>
        　　<% } %>
      <% } %>
    </div>
```
&emsp;&emsp;这段代码是关于文章的内容的，因此我们要对文章内容进行修改的话，就要先读懂这块儿的代码。这块儿代码首先判断文章是不是处于首页位置(index)，接着判断文章中有没有ReadMore标记(excerpt)。如果文章在首页位置(index)且存在ReadMore标记(excerpt)，那么文章显示的是ReadMore标记前的内容(item.excerpt);如果文章没有ReadMore标记(excerpt)且文章在首页位置(index)，那么文章显示的整篇文章(item.content);如果文章在首页(index)可是没有ReadMore标记(excerpt)，那么选取文章的第一段作为文章的摘要来显示。这就是博主的博客目前采用的方案了，如果大家对这部分感兴趣的话，可以看看自己的博客使用的主题是如何定义这部分内容的，然后在此基础上做些调整以满足个性化的需求。

&emsp;&emsp;好了，那么在了解了这部分内容后，我们应该马上就能想到，我们需要掉正的代码应该是在第9行这个位置，即当文章不在首页的时候要显示的内容。好了，按照我们在测试程序中的写法，我们可以写出如下代码：
```NodeJS
<% var dicts=item.content.match(/\[(.*?):(.*?)\]/g); %>
<% if(dicts.length==0){ %>
   <%- item.content %>
<% } else { %>
   <% for(i=0;i<dicts.length;i++) %>
   <% { %>
        <% var dict=dicts[i].split(/:/); %>
        <% var key=dict[0].substring(1,dict[0].length);  %>
        <% var id=dict[1].substring(0,dict[1].length-1); %>
        <% if(key=='music') %>
        <% { %>
             item.content=item.content.replace(dicts[i],'<embed src="http://music.163.com/style/swf/widget.swf?sid='+ id +
             '&type=2&auto=1&width=278&height=32" width="298" height="52" allowNetworking="all"></embed>')
        <% } %>
   <% } %>
   <%- item.content %>
<% } %>
```
&emsp;&emsp;相信经过博主的一番介绍，大家已经对这段代码相当熟悉了吧，这里就是先做判断，判断文章内容中是否有[key:vaule]这样的结构，如果没有就直接输出item.content;如果有就需要对其进行替换后再输出item.content。好了，现在我们用这段代码替换掉第9行代码，然后再次输出网页。可是结果让我们白忙活了一场，因为Hexo在输出网页的时候会报错，可能是因为博主写的JavaScript脚本Hexo无法解析吧！好了，从昨天下午开始差不多都在想着怎样解决这个问题，到现在还是没有一点头绪，文章里讲述的方法可以作为一种尝试，如果有兴趣、有精力、有能力解决这个问题的人，可以去进一步深入地探索这个问题。今天的内容就是这样了，睡觉！

**2015年11月10日更新:**
&emsp;&emsp;昨天抽空研究了下Hexo的[插件](https://hexo.io/docs/plugins.html)机制，发现在Hexo中提供了一种[标签](https://hexo.io/docs/tag-plugins.html)插件，可以帮助我们快速完成这种需求，所以就记录在这里。首先，它的原理是根据这样一个简单的标记来进行处理，当我们输入默认的这样的标记的时候它会被渲染为普通的引用标记，当我们在这个标记内传入参数后就可以利用程序进行处理。例如我们编写这样的简单的JS文件：
```
/**
* hexo-tag-cloudmusic
* https://github.com/qinyuanpei/hexo-tag-cloudmusic.git
* Copyright (c) 2015, qinyuanpei
* Licensed under the MIT license.
*/

hexo.extend.tag.register('cloudmusic', function(args){
  var sid = args[0];
  var config = hexo.config.cloudmusic || {};
  var widgetType = hexo.config.widgetType || 'flash';
  var widgetSize = config.widgetSize || 'small';
  var autoPlay = config.autoPlay || 1;
  var width = config.width || 278;
  var height = config.height || 32;

  if(widgetType == 'iframe'){
  	if(widgetSize=='small'){
  		return '<iframe frameborder="no" border="0" marginwidth="0" marginheight="0" width=298 height=52 src="http://music.163.com/outchain/player?type=2&id=' + sid + '&auto=' + autoPlay +'&height=32"></iframe>';
  	}else if(widgetSize=='big'){
  		return '<iframe frameborder="no" border="0" marginwidth="0" marginheight="0" width=351 height=86 src="http://music.163.com/outchain/player?type=2&id=' + sid + '&auto=' + autoPlay + '&height=66"></iframe>';
  	}else if(widgetSize=='custom'){
  		return '<iframe frameborder="no" border="0" marginwidth="0" marginheight="0" width=' + width +' height=' + height +' src="http://music.163.com/outchain/player?type=2&id=' + sid + '&auto=' + autoPlay + '&height=66"></iframe>';
  	}
  }else{
  	if(widgetSize=='small'){
  		return '<embed src="http://music.163.com/style/swf/widget.swf?sid=' + sid + '&type=2&auto=' + autoPlay + '&width=278&height=32" width="298" height="52"  allowNetworking="all"></embed>';
  	}else{
  		return '<embed src="http://music.163.com/style/swf/widget.swf?sid=' + sid + '&type=2&auto=' + autoPlay + '&width=320&height=66" width="340" height="86"  allowNetworking="all"></embed>';
  	}
  }
});
```
&emsp;&emsp;大家可以看到这个JS文件本质上就是根据传入的sid来拼接生成网易云音乐的widget代码，这样当我们需要在博客中引用网易云音乐的时候只需要采用下面的标记：

&emsp;&emsp;这个项目我目前发布在我的[Github](https://github.com/qinyuanpei/hexo-tag-cloudmusic)上，欢迎大家Start和Fork!