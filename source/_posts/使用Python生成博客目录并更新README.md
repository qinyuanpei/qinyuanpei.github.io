---
abbrlink: 1329254441
categories:
- 独立博客
date: 2018-02-23 09:32:45
description: 我意识到我的博客配置了 [hexo-generator-json-content](https://github.com/alexbruno/hexo-generator-json-content)
  插件，这个插件最初的目的是为博客提供离线的搜索能力，该插件会在博客的根目录里生成一个**content.json**文件，而这个文件中含有我们想要的一切信息，因此我们的思路转变为解析这个文件，人生苦短啊，我果断选择了我最喜欢的 Python，这里我们会提取出所有的文章信息，按照日期由近到远排序后生成列表;现在我们更新博客时的流程将发生变化，首先通过
  **hexo generate 或 hexo g**命令生成博客，这样 Hexo 会为我们生成 **content.json**，然后我们执行这段 Python 脚本，就可以生成 REAMD.md 文件，这里我们将这个文件推送到 blog 分支;关于博客采用
  [TravisCI](https://www.travis-ci.org/)  提供持续集成(CI)服务相关内容，可以参考 [持续集成在 Hexo 自动化部署上的实践](https://qinyuanpei.github.io/posts/3521618732/)
  这篇文章
tags:
- Python
- Github
- Script
title: 使用 Python 生成博客目录并自动更新 README
---

&emsp;&emsp;各位朋友，大家好，我是 Payne，欢迎大家关注我的博客，我的博客地址是：[https://qinyuanpei.github.io](https://qinyuanpei.github.io)。首先在这里祝大家春节快乐，作为过完年以后的第一篇文章，博主想写点内容风格相对轻松的内容。自从博主的博客采用 [TravisCI](https://www.travis-ci.org/) 提供的持续集成(CI)服务以以来，博客的更新部署变得越来越简单，所有的流程都被简化为 Git 工作流下的**提交(commit)**和**推送(push)**操作。考虑到博客是托管在 [Github](https://github.com/qinyuanpei/qinyuanpei.github.io) 上的，一直希望可以自动更新仓库主页的 README 文件，这样可以显示每次提交代码后的变更历史。基于这样一个构想，我想到了为博客生成目录并自动更新 README，其好处是可以为读者建立良好的文档导航，而且 Markdown 是一种简单友好的文档格式，Github 等代码托管平台天生就支持 Markdown 文档的渲染。关于博客采用 [TravisCI](https://www.travis-ci.org/)  提供持续集成(CI)服务相关内容，可以参考 [持续集成在 Hexo 自动化部署上的实践](https://qinyuanpei.github.io/posts/3521618732/) 这篇文章。

&emsp;&emsp;好了，现在考虑如何为博客生成目录，我们这里需要三个要素，即标题、链接和时间。标题和时间可以直接从 **_posts** 目录下的 Markdown 文档中读取出来，链接从何而来呢？我最初想到的办法是读取每个 Markdown 文档的文件名，因为我的使用习惯是采用英文命名，这样当博客的**永久链接(permalink)**采用默认的**:year/:month/:day/:title/**形式时，每个 Markdown 文档的文件名等价于文章链接。事实证明这是一个愚蠢的想法，因为当你改变了**永久链接(permalink)**的形式时，这种明显投机的策略就会彻底的失败。相信你在浏览器种打开这篇文章时，已然注意到链接形式发生了变化，当然这是我们在稍后的文章中讨论的话题啦。至此，我们不得不寻找新的思路，那么这个问题该如何解决呢？

&emsp;&emsp;我意识到我的博客配置了 [hexo-generator-json-content](https://github.com/alexbruno/hexo-generator-json-content) 插件，这个插件最初的目的是为博客提供离线的搜索能力，该插件会在博客的根目录里生成一个**content.json**文件，而这个文件中含有我们想要的一切信息，因此我们的思路转变为解析这个文件，人生苦短啊，我果断选择了我最喜欢的 Python，这里我们会提取出所有的文章信息，按照日期由近到远排序后生成列表。Python 强大到让我觉得这篇文章无法下笔，所以这里直接给出代码啦：
```Python
# -*- coding: utf-8 -*-

import os
import re
import sys
import json
import datetime

# 文档实体结构定义
class Post:

    def __init__(self,date,link,title):
        self.date  = date
        self.link  = link
        self.title = title

    def getTitle(self):
        return self.title

    def getLink(self):
        return 'https://qinyuanpei.github.io/' + self.link

    def getDate(self):
        d = re.findall(r'\d{4}-\d{1,2}-\d{1,2}',self.date)[0]
        t = re.findall(r'\d{2}:\d{2}:\d{2}',self.date)[0]
        dt = '%s %s' % (d,t)
        return datetime.datetime.strptime(dt,'%Y-%m-%d %H:%M:%S')

# 从JSON中加载文档数据
def loadData():
    json_file = open('./public/content.json','rb')
    json_data = json.load(json_file)
    for item in json_data:
        yield Post(item['date'],item['path'],item['title'])

# 从列表生成Markdown文件
def mkMarkdown(items):
    mdfile = open('README.md',mode='wt',encoding='utf-8')
    itemTpl = '* {0} - [{1}]({2})\n'
    for item in items:
        mdfile.write(itemTpl.format(
            datetime.datetime.strftime(item.getDate(),'%Y-%m-%d'),
            item.getTitle(),
            item.getLink()
        ))



if(__name__ == "__main__"):
    items = sorted(loadData(),key=lambda x:x.getDate(),reverse=True)
    mkMarkdown(items)
```
&emsp;&emsp;这里需要注意的有两个地方，第一，从 JSON 中解析出来的日期形式为：**2018-02-23T01:32:45.000Z**。对于这个形式的日期，博主先后尝试了内建的 time 模块和第三方的 datetime 模块，发现均无法直接转换为日期类型，所以首先采用正则匹配出日期和时间，然后再组合为标准的**%Y-%m-%d %H:%M:%S**的格式，这样就可以使用 datetime 模块进行处理啦，我还是想吐槽人类对各种各样 format 的执着，这些通配符在不同的语言中存在差别，就像 SQL 和正则引擎或多或少地存在兼容性问题一样。如果有朋友知道如何对这种日期形式进行转换，欢迎在博客中评论留言，再次谢谢大家。第二，使用内置函数 sorted()对数据进行排序，lambda 表达式使用起来非常棒，因为默认是升序排列地，而我们需要的是日期由近到远，所以这里选择了降序排列。

&emsp;&emsp;现在我们更新博客时的流程将发生变化，首先通过 **hexo generate 或 hexo g**命令生成博客，这样 Hexo 会为我们生成 **content.json**，然后我们执行这段 Python 脚本，就可以生成 REAMD.md 文件，这里我们将这个文件推送到 blog 分支。相对应地，我们修改 [TravisCI](https://www.travis-ci.org/) 的脚本文件 **.travis.yml** 文件如下：
```Shell
script:
  - hexo clean
  - hexo generate
  - cp README.md ./public/README.md
```
&emsp;&emsp;显然，这是告诉 TravisCI 在生成博客以后，将 README.md 文件复制到输出文件，这样当我们推送博客(指生成的静态页面)到 master 分支的时候，它会和 blog 分支同步共享同一份 README 。我想一定有朋友会问我，难道生成 README.md 文件的步骤不能交给 TravisCI 来处理？一定要在推送到 blog 分支以前手动地去执行脚本吗？我最初尝试过让 TravisCI 去执行这个 Python 脚本，可我发现一个残酷的事实时，我们这个虚拟机环境是 nodejs 的，这在我们定义 **.travis.yml** 文件时就指定了，因此这个环境中可能是没有 Python 支持的。起初我以为 Linux 系统自带 Python ， 因此尝试在 **.travis.yml** 文件中使用 pip 安装相关依赖，然后我发现持续集成服务华丽丽地挂了，因为 TravisCI 默认的 Python 版本是 Python2.7 , 除非我们指定的是一个 Python 的语言环境，所以这种想法不得不作罢，暂时就手动更新好啦。

&emsp;&emsp;好了，这篇文章核心的内容就这么多，下面想说些关于 Hexo 的延伸话题。 Hexo 是一个基于 nodejs 的静态博客生成器，按理说使用 nodejs 去扩展功能是最佳的实践方式，所以即使 Python 再强大，我们在这里看到的依然存在着天然的割裂感， 我们能不能将执行 Python 脚本的这个过程合并到 **hexo generate 或者 hexo g**这个步骤中去呢？ 通过官方文档中关于[事件](https://hexo.io/api/events.html)和[生成器](https://hexo.io/api/events.html)的描述，我们获得了两种新的思路，分别是在生成页面以后通过 child_process 模块调用 python 脚本、通过 Locals 变量获取全部文章信息后生成 Markdown。从方案是否优雅的角度上来讲，我个人更倾向于第二种方案。基本的代码如下：
```JavaScript
//方案一
hexo.on('generateAfter', function(post){
  //TODO:通过content.json文件生成markdown文档
});

//方案二
hexo.extend.generator.register("markdown", function(locals){
  var posts = locals.posts;
  //TODO:通过posts属性生成markdown文档
});
```
&emsp;&emsp;显然，我是不会写 nodejs 的，如果有时间和精力的话，我可能会考虑采用第二种方案写一个插件，可是像我这么懒的一个人，还是不要提前立 flag 啦，毕竟人生苦短呐，我都选择使用 Python 这门语言来写啦，我干嘛非要再花时间去迎合它呢？好啦，这篇文章就是这样啦，本文中的脚本可以到 [这里](https://github.com/qinyuanpei/BlogScripts/blob/master/HexoBlog.py) 来获取，本文生成的目录可以到 [这里](https://github.com/qinyuanpei/qinyuanpei.github.io) 来访问，再次谢谢大家！