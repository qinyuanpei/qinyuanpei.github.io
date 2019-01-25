---
title: 基于Travis CI实现 Hexo 在 Github 和 Coding 的同步部署
abbrlink: 1113828794
date: 2018-02-27 10:45:04
categories:
  - 独立博客
tags:
  - CI
  - Hexo
  - Travis
---
&emsp;&emsp;各位朋友，大家好，我是Payne，欢迎大家关注我的博客，我的博客地址是 [https://qinyuanpei.github.io](https://qinyuanpei.github.io) .在曾经的一篇博客：[《持续集成在Hexo自动化部署上的实践》](https://qinyuanpei.github.io/posts/3521618732/)中，我为大家分享了在线持续集成服务  [Travis CI](https://www.travis-ci.org/) 的相关内容，在这篇文章中我们通过  [Travis CI](https://www.travis-ci.org/) 为 Hexo 提供了自动部署的支持。其原理是Github为 [Travis CI](https://www.travis-ci.org/) 分配一个token，当我们向 Github 推送新的代码以后，Travis 就会从代码仓库中拉取代码，并通过 [npm](https://www.npmjs.com/) 安装依赖生成静态页面，我们将这些静态页面推送到 master 分支，即可完成对Hexo的部署操作。这个流程从去年10月份建立以来，一直运行得非常稳定，对我个人而言，随着博客里得内容越来越多，在本地生成静态页面需要
20多秒得时间，而有了持续集成服务以后，我可以用这个时间去做更多的事情，当持续集成流程发生异常的时候，微信上会收到 Travis 发送的邮件，整个过程简直令人心情愉悦。

&emsp;&emsp;今天想继续写点这个话题相关的内容，即如何通过 Travis CI 实现 Hexo 在 Github 和 Coding 的同步部署。显然，部署 Hexo 到 [Github Pages](https://pages.github.com/) 我们已经实现，今天我们着重来说 [Coding Pages](https://coding.net/pages/)。为什么我们需要 [Coding Pages](https://coding.net/pages/) 呢？主要从两个方面考虑，首先，因为 [Github Pages](https://pages.github.com/) 屏蔽了百度的爬虫，所以我们托管在 Github 上的博客，无法被搜索引擎正常收录；其次，由于 [Github Pages](https://pages.github.com/) 的服务器在国外，所以在国内博客的速度会受到影响，而且**"防火墙"**的国情决定了 [Github](https://github.com) 是一个不稳定的网站。曾经经历过短时间内无法使用 Github 的情形，故而，为了保证博客可以更加稳定地运行，我们必须为博客提供一个备份镜像，这就是我们今天要提到的 [Coding Pages](https://coding.net/pages/) 服务啦。在正式使用这个服务前，我们首先简单介绍下这个服务。

&emsp;&emsp;我们知道 [Github Pages](https://pages.github.com/) 是 Github 提供的静态页面托管服务，其初衷是为个人项目或者组织项目创建演示或者文档站点，而 [Coding Pages](https://coding.net/pages/) 则是国内的代码托管平台 [Coding](https://coding.net/git) 提供的类似服务，国内类似的代码托管平台还有[码云](https://gitee.com/login)、[Gitlab](https://about.gitlab.com/) 等。[Coding Pages](https://coding.net/pages/) 支持自定义域名、SSL 等基本特性，随着官方不断对这一服务进行升级，目前该服务除支持静态页面部署以外，同时支持 PHP 和 MySQL这类动态页面部署的特性。对 Hexo 来说，静态页面部署的特性完全可以支撑我们这个想法。我的想法是以 [Github](https://github.com/qinyuanpei/qinyuanpei.github.io) 作为代码的主仓库，其上面的 **blog** 分支存放博客的源代码， **master** 分支存放博客的静态页面，在此基础上，我们同时推送静态页面到 Github 和 Coding 的代码仓库，这样就可以实现两个平台的同步部署，这里的部署自然是指由 Travis 完成的自动化部署。整体的流程设想如下图所示：

![博客同步部署流程图](http://img.blog.csdn.net/2018022714101472)

&emsp;&emsp;通过这个流程图，我们可以注意到，新增加的工作量，主要体现在 Travis 向 Coding 的代码仓库推送静态页面，因此我们首先要有一个 Coding 的代码仓库。关于如何注册 Coding 及在 Coding 上创建代码仓库，这里不再详细赘述啦，大家可以自行百度、Google 或者阅读官方文档。Travis CI 的行为主要由 **.travis.yml** 这个文件来决定，要推送静态页面到 Coding 的代码仓库，Travis CI 需要有代码仓库的读写权限。顺着这个思路，尝试让 Coding 授权 给 Travis CI，结果从文档中发现Travis CI 并不支持 Coding，而 Coding 官方支持的持续集成 flow.ci 需要使用者从 Docker 创建镜像，所以看起来这条路无法走通。从搜索引擎中检索相关问题，从 Git 工作机制的角度入手，可以想到三种常见思路，即 SSH Key、Hexo 的 deploy 插件和 HTTPS协议。

&emsp;&emsp;第一种思路是考虑让 Travis CI 的远程服务器共享本机的SSH Key，通过 **ssh-copy-id** 命令即可实现，可问题是 Travis CI 每次创建虚拟机环境是变化的，因此我们无法确定目标主机的 IP 或者计算机名称等信息，这种思路不适合 Travis CI。而 Travis CI 官方同样提供了命令行工具来完成这个工作，因为 Travis CI 是基于 Ruby 开发而来，所以需要 Ruby 的环境支持，作为一个为逃避 Jekyll 而选择 Hexo 的人，我是不会让自己再受到 Ruby 的摧残的，所以这种思路基本放弃。第二种思路是使用 Hexo 提供的 deploy 插件，例如 [hexo-deploy-git](https://github.com/hexojs/hexo-deployer-git) 这个插件支持通过 git 部署，而 Coding 和 Github 都支持 Git 相关的协议，所以可以考虑使用这个插件来完成这个操作，目前网络上可以检索到的资料，都是使用这个插件来完成同步部署。可是经过我一位使用过这个插件的朋友确定，该插件需要再执行 git 命令行期间输入用户名和密码，Travis CI 是不会给你机会输入用户名和密码的，所以这种思路再次放弃。第三种 HTTPS 协议，这个想都不用想是需要输入密码的，所以果断直接放弃。

&emsp;&emsp;正所谓"行至水穷处，坐看云起时"，山重水复之间，柳暗花明之际，我意外发现 Coding 提供了和 Github 类似的"访问令牌"，我们在使用 Travis CI 的时候，实际上做了两步授权操作，第一次是授权 Travis CI 读取我们在 Github 上的仓库列表，这是一个通过 OAuth 授权的过程；第二次授权是授权 Travis CI 向指定仓库推送或者拉取内容，这是一个通过 Token 授权的过程。我们会在 Travis CI 的后台设置中将 Token 作为全局变量导出，这样我们就可以在 .travis.yml 文件中引用这些全局变量。我意识到这是一个值得一试的想法，首先我们在 Coding 的**”个人设置"**页面中找到**访问令牌**，新建一个新的访问令牌，这里我们选第一个权限即可，因为我们只需要为 Travis 提供基本的读写权限，这样我们会生成一个 Token，这里注意保存 Token，因为它在这里只显示这一次，我们将 Token 填写到 Travis CI 的后台，取名为 CO_Token 即可，依次如下图所示：

![在Coding中新建访问令牌](http://img.blog.csdn.net/20180227150043442)

![在Coding中保存访问令牌](http://img.blog.csdn.net/20180227150136197)

![在Travis中新建全局变量](https://ws1.sinaimg.cn/large/4c36074fly1fzixbhjw8vj216909p74i.jpg)

&emsp;&emsp;好了，现在有了Token，就意味着 Travis CI 有权限向 Coding 推送或者拉取内容了，那么怎么让它工作起来呢？我们记得 Travis CI 有一个叫做 .travis.yml 的配置文件对吧？这里我们需要简单修改下这个文件，让 Travis CI 在生成静态页面以后同时推送静态页面到 Coding。修改后的关键配置如下，我已经写好了详细注释，关于这个文件配置可以参考[这里](https://docs.travis-ci.com/)，这里不再详细说明：

```yml
after_script:
  - cd ./public
  - git init
  - git config user.name "qinyuanpei"
  - git config user.email "qinyuanpei@163.com"
  - git add .
  - git commit -m "Update Blog By TravisCI With Build $TRAVIS_BUILD_NUMBER"
  # Github Pages
  - git push --force --quiet "https://${CI_TOKEN}@${GH_REF}" master:master 
  # Coding Pages
  - git push --force --quiet "https://qinyuanpei:${CO_TOKEN}@${CO_REF}" master:master
  - git tag v0.0.$TRAVIS_BUILD_NUMBER -a -m "Auto Taged By TravisCI With Build $TRAVIS_BUILD_NUMBER"
  # Github Pages
  - git push --quiet "https://${CI_TOKEN}@${GH_REF}" master:master --tags
  # Coding Pages
  - git push --quiet "https://qinyuanpei:${CO_TOKEN}@${CO_REF}" master:master --tags

branches:
  only:
    - blog

env:
 global:
   # Github Pages
   - GH_REF: github.com/qinyuanpei/qinyuanpei.github.io
   # Coding Pages
   - CO_REF: git.coding.net/qinyuanpei/qinyuanpei.coding.me.git
```
&emsp;&emsp;好了，现在我们就可以同时部署博客到 Github 和 Coding了，现在大家可以使用下面两种方式来访问我的博客。需要说明的是，使用 Coding Pages 的特性需要开启仓库的 **Pages **服务，并且 Coding 支持免费托管私有项目，虽然目前仓库的容量存在限制，对我们部署 Hexo 来说完全足够啦，下图是 Coding 上展示的提交历史，排版效果棒棒哒，哈哈，好了，以上就是这篇文章的内容啦，希望大家喜欢哦！

![Coding上展示的提交历史](https://ws1.sinaimg.cn/large/4c36074fly1fzix8o2p1ij20t40h4t9n.jpg)

* [Github Pages 镜像](https://qinyuanpei.github.io)
* [Coding Pages 镜像](http://qinyuanpei.coding.me)

&emsp;&emsp;本文使用的 .travis.yml 文件可以从[这里](https://github.com/qinyuanpei/qinyuanpei.github.io/blob/blog/.travis.yml) 获取哦！