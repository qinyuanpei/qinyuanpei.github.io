---
abbrlink: 2950334112
categories:
- 独立博客
date: 2015-11-15 13:12:22
description: 大家可以看到这里就是一段HTML代码，因为我们要引入的这个模板和article.ejs在同一个页面中，所以我们可以直接在这里调用item这个变量，而item这个变量里是封装了当前文章的标题和链接的，因此我们可以顺利成章的构造这样一段HTML代码，因为博主不会写CSS样式，所以使用了一个默认的代码样式来完成这个工作，如果大家懂CSS，请自行发挥你的创意将它做得更好
tags:
- Hexo
- 版权
- 知识共享
title: 在Hexo中为文章自动添加版权信息声明模块
---

&emsp;&emsp;各位朋友，大家好，欢迎大家关注我的博客，我是秦元培，我的博客地址是[http://qinyuanpei.com](http://qinyuanpei.com)。今天想和大家说说博客文章版权这件事情。每当提到版权的时候，我知道大家内心深处都是对此不以为然的，因为国内版权意识薄弱，所以版权在我们的眼中就变成了这样一件可有可无的东西，可是事实真的是这样的吗？首先我们必须承认一件事情，即你从互联网上获得的知识都是有价值的，即使这些知识的创造者并未因此而获得利益。<!--more-->相对其它的行业，因为程序员这个职业本身需要其通过不断地学习新知识来适应新变化，因此程序员这个群体更喜欢在互联网上分享知识和经验，而这些知识的受众面窄、技术门槛高则决定了程序员们无法像普通的博客作者一样有更多的机会来获得收入。大部分的程序员都是从分享知识、记录学习和技术交流这样的角度来撰写博客的。那么这样就会造成一个问题，在国内版权意识薄弱和技术博客变现困难的双重夹缝中，博客作者该如何寻求新的突破呢？

#一、为什么要说博客文章版权这件事儿
&emsp;&emsp;首先，我们为什么要说博客文章版权这件事情呢？因为博客是文字创造的产物，是知识共享的一种形式。当我们无视版权的时候，这意味着知识是没有价值的，创造是无关痛痒的，脑力劳动和创意活动的价值在现实中被无情地扼杀。当你引用一个人的观点却不加以注明的时候，当你盗用一个人的创意却不给予报酬的时候，试问谁还会愿意为这个社会贡献创意和想法呢？引用[许锡良](http://blog.caijing.com.cn/expert_article-151317-41037.shtml)的观点，尊重版权更深层次的含义在于对人权的尊重：

>从人权的角度看，人与动物的区别在于知识与思想，因此，人类最根本的财富也应该是知识与思想上的财富，一切社会财富都来源于知识与思想，这是从自然界获得生活资料，以及改造社会的根本。没有知识与思想的人类将与动物世界没有什么区别。尊重人权，首先就要学会尊重人的劳动成果，特别是创造性劳动成果，只有人，才能创造出来的知识产权与发明专利。尊重人权，首先就要学会尊重一个人的思想与创意。只有人，才能创造出来的知识产权与发明专利。因为每个人都是一个独立的个体，每个人头脑里的想法都是独一无二的，无人能替代的。在没有说出来，或者写出来之前，也无人能盗取的，这种思想就是个人独有，就是只属于个人的专利。 

&emsp;&emsp;我常常遇到在博客评论中和我直接要源代码的人，我不明白从什么时候起对知识的分享变成了某些人懒惰的借口。我选择将我知道的某个分享出来，当然我同样有权利可以选择沉默。你不能因为习惯了做伸手党就认为我应该理所当然地把源代码给你，这是对我的不尊重。我写博客的目的在于和别人交流技术、互相学习，如果你根本没有看懂我博客写了什么，只是希望可以找到可以“抄”来就能用的代码。抱歉!这违背了我的初衷我更没有道理要将源代码分享给你,况且如果我的代码都清清楚楚（命名规范、注释清晰）地写在博客里，如果这样的代码你都不能看懂，就算把完整的工程分享给你又有什么用呢？我本来不情愿论坛来转载我的文章，因为论坛盖楼的这种互动模式实在难以产生较为良好的互动效果，可是人家来诚心诚意地询问你的态度，如此拒绝难免有点却之不恭吧！当然最让人讨厌的是网络爬虫和网站编辑，这种让人讨厌是因为它"简单粗暴"，完全不考虑博客作者的感受，文章的原始链接被删除、文章的作者署名被删除。或许大家都觉得一个署名、一个原始链接都是无足轻重的东西，可是在我看来这恰恰是体现责任的地方。作者的责任在于对文章的真实性和客观性负责，转发者的责任在于帮助读者找到作者当他们之间需要某种交流的时候，这就是我为什么强调署名和原始链接的理由！

#二、谈谈如何保护博客文章版权
&emsp;&emsp;在保护博客文章版权这个问题上，我们可以采取的方式固然很多，但是这件事情的根本原因在于人们普遍不重视知识产权的保护，所以我们这里提到的这些方式都是外家功夫，真正要根除这等沉疴痼疾需要人们不断提升自我、勤修内功。
* 第一种方式，我们称为通过技术方式提醒，比如通过编写JavaScript脚本，实现当对方复制你的博客内容的时候，程序可以自动在这段复制的内容中增加署名和连接。当然我们可以通过修改文章的模板来在文章中加入版权信息，这个我们留到最后会说，因为实际上这个是我们今天要重点研究的内容，博主是个程序员，我们当然要用技术的方式来实现了，前面的这些大家看完心里有个数就是了，哈哈！
* 第二种方式，我们称为增加文章内链的方式，就是在文章中尽可能地使用指向这个博客的连接，这样可以保证在文章转载后为博客带来一定的反向访客。
* 第三种方式，在图片上增加水印，这样读者在看到图片的时候就可以很容易地找到原始出处，可是如果你不能保证拥有所引用的图片得版权，建议不要轻易地使用这种方式。
* 第四种方式，逐渐形成个性化的写作风格，这样当读者读到这些文字的时候，可以通过文章的风格知道文章的作者和出处。
* 第五种方式，努力提高自己博客的文章质量，让更多的读者从中受益，形成有独立风格的博客品牌。一个博客有了高质量的内容和品牌，那么在搜索引擎中的权重就会很高，网民通过搜索引擎进行查找的时候，博客原文都会排在第一位。

博主之所以要使用[http://qinyuanpei.com](http://qinyuanpei.com)这个独立博客的原因正是基于这个原因。博主目前采用的[知识共享](http://baike.baidu.com/link?url=jcl0t2y3iwHPETIXjXM5yhQtujk2iUJE9Fy7dCoti7xtNDMxHYlUlXcW0GsorpaAWGq_Y1OSduIXVEpHlpSm1qHhV7mkGnU56J6JSRUuCRlwnWHNJL6K913N5mm9sMqiw1BXlmSprfhmwc1sxsjU3X7gMRd7z9OfBR446a__T3Gp90js_NnS6Dq-TkbmBeWB)许可是署名(BY)-非商业性使用(NC)-相同方式共享(SA)，请各位在转载文章的时候注意保留作者署名和文章出处，谢谢！

#三、保护博客文章版权，独立博客在行动
&emsp;&emsp;我的博客是采用[Hexo](http://hexo.io/)这个博客系统来搭建的，说到底程序员是天生爱折腾的命吧，都有对掌控事物的欲望，不喜欢受到条件制约。CSDN的博客虽然还不错，可是“限制因素 + 服务器奔溃”这样的强效组合实在让我很难有继续坚持下去的动力，所以果断就自己搭了博客买了域名，老老实实地开始管理起独立博客。好了，废话少说，放码过来，我们下面来看看怎么在Hexo中的文章中增加一个展示版权信息的模块，这里以[Jacman](https://github.com/wuchong/jacman)主题为例，我们首先定位到该主题文件夹下的\layout\_partial\post\article.ejs文件：

```
<div id="main" class="<%= item.layout %>" itemscope itemprop="blogPost">
  <% if (page.layout=='photo' && item.photos && item.photos.length){ %>
    <%- partial('gallery') %>
  <% } %>
	<article itemprop="articleBody"> 
		<%- partial('header') %>
	<div class="article-content">
		<% if( table&&(item.toc !== false) && theme.toc.article){ %>
		<div id="toc" class="toc-article">
			<strong class="toc-title"><%= __('contents') %></strong>
		<% if(item.list_number == false) {%>
		<%- toc(item.content,{list_number:false}) %>
		<% }else{ %>
			<%- toc(item.content) %>
		<% } %>
		</div>
		<% } %>
		<%- item.content %> 
	</div>
		<%- partial('footer') %>  	       
	</article>
	<%- partial('pagination') %>
	<%- partial('comment') %>
</div>  
```
我们可以注意到文章的内容是在<%- item.content %>这个标签里，因此我们如果要在文章中增加内容，只需要在<%- item.content %>的后面引入一个ejs模板文件即可，所以我们接下在article.ejs的同级目录下创建一个declare.ejs文件：

```
<pre><code><b>    版权声明</b>:本文由<b><a href="<%= config.root %>about" target="_blank" title="<%= config.author %>"><%= config.author %></a></b>创作和发表,采用<b>署名(BY)</b>-<b>非商业性使用(NC)</b>-<b>相同方式共享(SA)</b>国际许可协议进行许可,转载请注明作者及出处,本文作者为<b><a href="<%= config.root %>about" target="_blank" title="<%= config.author %>"><%= config.author %></a></b>,本文标题为<b><a href="<%- config.root %><%- item.path %>" target="_blank" title="<%= item.title %>"><%= item.title %></a></b>,本文链接为<b><a href="<%- config.root %><%- item.path %>" target="_blank" title="<%= item.title %>"><%- config.url %>/<%- item.path %></a></b>.</code></pre>
```
大家可以看到这里就是一段HTML代码，因为我们要引入的这个模板和article.ejs在同一个页面中，所以我们可以直接在这里调用item这个变量，而item这个变量里是封装了当前文章的标题和链接的，因此我们可以顺利成章的构造这样一段HTML代码，因为博主不会写CSS样式，所以使用了一个默认的代码样式来完成这个工作，如果大家懂CSS，请自行发挥你的创意将它做得更好。好了，下面我们要做的工作就是将这个模版引用到article.ejs文件中，类似地我们可以使用<%- partial('footer') %>这样的结构来引入这个模板，这里给出完整的article.ejs文件内容：

```
<div id="main" class="<%= item.layout %>" itemscope itemprop="blogPost">
  <% if (page.layout=='photo' && item.photos && item.photos.length){ %>
    <%- partial('gallery') %>
  <% } %>
	<article itemprop="articleBody"> 
		<%- partial('header') %>
	<div class="article-content">

	    <% if(theme.show_declare) { %>
			<%- partial('declare') %>
		<% } %>

		<% if( table&&(item.toc !== false) && theme.toc.article){ %>
		<div id="toc" class="toc-article">
			<strong class="toc-title"><%= __('contents') %></strong>
		<% if(item.list_number == false) {%>
		<%- toc(item.content,{list_number:false}) %>
		<% }else{ %>
			<%- toc(item.content) %>
		<% } %>
		</div>
		<% } %>
		<%- item.content %> 

	    <% if(theme.show_declare) { %>
			<%- partial('declare') %>
		<% } %>
	</div>
		<%- partial('footer') %>  	       
	</article>
	<%- partial('pagination') %>
	<%- partial('comment') %>
</div>  
```
这里博主在文章的开头和结尾处插入了这个模板，同时在主题文件夹中设置了一个是否显示版权声明的开关变量，这样我们就可以在主题中设置是否开启版权声明模块了。好啦，相信你在看到这边文章的时候你已经看到了它的版权声明了，这就是我们今天的内容啦，谢谢大家！