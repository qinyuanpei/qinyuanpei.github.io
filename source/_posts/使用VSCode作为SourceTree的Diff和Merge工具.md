---
abbrlink: 3222622531
categories:
- 开发工具
date: 2018-09-30 08:43:44
description: 既然，作为Git可视化工具的SourceTree可以使用VSCode作为Diff和Merge的工具，那么，我们干脆一鼓作气，将VSCode作为Git默认的Diff和Merge的工具吧;现在，使用SourceTree的时候，周围同事大部分都习惯GUI操作，所以，就想能不能把SourceTree和VSCode结合着来用，因为我发现SourceTree可以支持外部的Diff和Merge工具;然后，我们在SourceTree里做如下配置，这里我们直接让VSCode作为我们的Diff和Merge工具，具体参数如图所示：
tags:
- Git
- VSCode
- SourceTree
title: 使用VSCode作为SourceTree的Diff和Merge工具
---

&emsp;&emsp;使用SourceTree有一段时间啦，从界面舒适度和易用性两个方面来看，的确要比小乌龟更好一点，日常配合命令行来使用，基本能覆盖到各种使用场景，譬如分支、版本、变基、合并等等。我本人在工作中接触到的Git工作流，大体上可以分为两类，从最早是官方所推崇的5个分支的Git Workflow，到如今在Github上更为流行的PR(Pull Request)。这两种方式，实际使用中各有优劣吧，而且这个话题似乎更适合专门写一篇文章来说。

&emsp;我真正想说的是，我需要一个优雅的Diff和Merge工具。虽然，对一个使用命令行的人来说，使用git diff来展示差异对比已经完全足够啦，可在某些需要解决冲突的场合，命令行就显得有点力不从心。我个人一直不习惯小乌龟的合并工具，因为使用起来总觉得相当别扭。直到我发现，VSCode可以在打开冲突文件的时候，自动提示解决冲突的选项，我觉得我开始喜欢上这个工具啦。所以，平时我解决冲突的做法是，在命令行里找到冲突的文件，然后逐一用VSCode打开来解决冲突。

&emsp;现在，使用SourceTree的时候，周围同事大部分都习惯GUI操作，所以，就想能不能把SourceTree和VSCode结合着来用，因为我发现SourceTree可以支持外部的Diff和Merge工具。其实，小乌龟一样是支持的，关键是配置太难用啦！SourceTree支持的Merge工具里有鼎鼎大名的P4Merge，不过我发现一来官网完全打不开(需要翻墙)，二来界面相当复古我不喜欢，而SourceTree默认的Merge工具其实就是小乌龟里的，所以，请允许我如此任性的折腾吧！

&emsp;首先，确保你安装了VSCode，这显然是一句废话，可对于博主来说，这是唯一可以替代Sublime Text的代码编辑器，想想可以写Markdown、写Python、写JS、写.NET Core，简直不能更美好了好嘛？然后，我们在SourceTree里做如下配置，这里我们直接让VSCode作为我们的Diff和Merge工具，具体参数如图所示：

![SourceTree配置图示](http://ww1.sinaimg.cn/large/4c36074fly1fymku875hdj20ix0got97.jpg)

&emsp;好了，现在我们就可以在SourceTree里愉快地使用VSCode啦，感受一下这如德芙一般的纵想丝毫，从现在开始，彻底忘掉小乌龟那丑陋的合并工具吧！

![VSCode解决冲突](http://img-blog.csdn.net/20180930171206711)

![VSCode差异比较](https://img-blog.csdn.net/2018093017130972)

&emsp;既然，作为Git可视化工具的SourceTree可以使用VSCode作为Diff和Merge的工具，那么，我们干脆一鼓作气，将VSCode作为Git默认的Diff和Merge的工具吧！熟悉Git命令行的朋友一定遇到过这样的场景，有时候，我们执行完git merge以后，命令行会采用Vim的方式来进行交互，这是因为Git默认的编辑器就是Vim，为什么是Vim呢？因为Git和Linux一样，都出自Linus大神之手啊！所以，这句话的意思是，我们可以给Git配置外部工具，譬如小乌龟、P4Merge等等，这里直接给出相关命令：
```Shell
//Merge时不创建备份文件
git config --global al mergetool.keepBackup fap false

//配置Diff工具
git config --global al diff.tool cod code
git config --global al difftool.prompt mpt false
git config --global al difftool.code.cmd '"C '"C:\Program Files\Microsoft VS Code\de\Code.exe" "-" "--wait --diff" "$LOCAL" "$REMOTE"'

//配置Merge工具
git config --global al merge.tool cod code
git config --global al mergetool.prompt mpt false
git config --global al mergetool.code.cmd '"C '"C:\Program Files\Microsoft VS Code\de\Code.exe" "-" "--wait" "$MERGED"'
git config --global al mergetool.code.trustexitcodecode true

```

&emsp;OK，配置完Git以后，遇到用到需要Diff的场景，我们只需要执行git difftool；而需要用到Merge的场景，我们只需要执行git mergetool。直接合理搭配工具，Git一样可以变得非常可爱，而不是一堆枯燥乏味的命令行，好啦，Enjoy it，难得写一篇不那么技术向的博客，以后记得早点睡觉~zZ，晚安！