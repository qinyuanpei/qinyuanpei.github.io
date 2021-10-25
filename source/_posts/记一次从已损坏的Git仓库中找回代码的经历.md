---
toc: true
title: 记一次从已损坏的 Git 仓库中找回代码的经历
categories:
  - 开发工具
tags:
  - Git
  - 工具
  - 软件
copyright: true
abbrlink: 686567367
date: 2020-06-23 17:08:17
---
突然发觉，古人其实特别有趣，譬如有古语云：『常在河边走，哪有不湿鞋』，实在是富有生活气息的一句俗语，可古人又有言语：『光脚的不怕穿鞋的』，更是朴实无华的一句话。上周下班适逢天降大雨，我撑伞送一位同事到地铁站，结果走到半路人家来一句，“你快点走吧，我穿着凉鞋”，一时竟无语凝噎。常在河边走，固然会有湿鞋的顾虑，可真正的气度绝不是光着脚满地跑，如何做到湿了鞋子而不慌呢？答案是脚上无凉鞋而心中有凉鞋。今天，我将为大家我在使用`Git`过程中如何“湿鞋”、如何不怕“湿鞋”的一个故事(逃

# 蓝屏重启后 Git 居然坏了

中国传统小说喜欢从神话讲起，端的是汪洋恣肆、纵横捭阖。而国外小说则喜欢从一片常青藤叶这种不显眼的事物写起，足可见二者见天地众生视角之不同。而我这个故事，是再普通不过的一次蓝屏。重启后 Visual Studio 提示恢复了未保存的代码，此时，我并未注意到 Git 仓库损坏的情况，就这样，我在一个“游离态”的版本上编写代码，直到我打开 SourceTree 的时候(作者注：**我就是那个命令行和 GUI 混合使用的奇葩**)，发现左侧本地分支全部消失，在命令行里`git status`，发现根本没有这个分支，而`.git/refs/`对应分支指向了一个错误的 Hash，我意识到我的 Git 仓库文件可能损坏了，这意味着我写的新 feature 可能丢失了，此时，Git 中提示的类似的错误信息：
```bash
$ error: refs/remotes/origin/HEAD: invalid sha1 pointer 0000000000000000000000000000000000000000
```
在此之前，其实博主已经经历过类似的事情，在没有未提交的代码的情况下，其实可以暴力删除`. git`目录，然后在`git init`即可，这相当于重新初始化仓库啦，在这种情况下，本地的分支会被删掉，你需要重新建新分支。可是这次不一样啊，在做的是一个即将发版的新 feature，不允许我出这样的选择啊！博主双掌合一，像夏洛克一样冷静思考，缓缓地在命令行下敲出`git reflog`，这条命令相当于你在 Git 中的监控日志，你对 Git 所做的一切都会成为呈堂证供。此时，你会得到下面的信息——沉默是今晚的康桥……
```bash
$ fatal: You are on a branch yet to be born
```
这是什么意思呢？意思就是这个分支还是一个“新生儿“的状态，新生儿怎么可能又活动记录呢？所以，使用 Git 的准则之一，只要仓库没有坏，通过`git reflog`找到对应的 Hash ，`git checkout`就可以找回代码，哪怕你刚刚手滑删除了一个未提交的分支，这种情况下都可以找回来。But 现在这种状况下，这条路显然是走不通啦。继续双掌合一，像夏洛克一样冷静思考，每个分支里其实是记录着一个 hash ，对应着最后的一次提交，现在是这个 hash 不对，那就要找到正确的 hash 啊。命令行已经非常明确地告诉你，是因为某些 object 丢失或者损坏了，那不妨先用`git fsck`试试。
```bash
$ git fsck
notice: HEAD points to an unborn branch (master)
Checking object directories: 100% (256/256), done.
Checking objects: 100% (589/589), done.
error: refs/remotes/origin/HEAD: invalid sha1 pointer 0000000000000000000000000000000000000000
notice: No default references
dangling tag 92d0fe18f9a55177d955edf58048b49db7987d5b
dangling commit aa7856977e80d11833e97b4151f400a516316179
dangling commit 16e449da82ec8bb51aed56c0c4c05473442db90a
dangling commit 864c345397fcb3bdb902402e17148e19b3f263a8
dangling tag be9471e1263a78fd765d4c72925c0425c90d3d64
```
此时，我们就会得到这样的信息。我天，这简直太良心了好吧，连哪一个 object 丢了都明明白白地告诉你。既然是提示解包(unpack)的时候失败，不妨先手动解包看看呗，好吧，果然程序是不会欺骗人的。这个时候，我注意到这些里面有一些提交(commit)，我在想这些有没有可能是残留的有效分支，于是使用下面的命令创建临时分支，一番折腾发现这些分支都离我的分支比较远，所以，基本可以排除了。
```bash
//尝试手动解包
$ mv .git/objects/pack/pack-0672bd01813664b80248dbe8330bf52da9c02b9f.pack .
$ git unpack-objects -r < pack-0672bd01813664b80248dbe8330bf52da9c02b9f.pack
//从某个commit新建临时分支
$ git update-ref refs/heads/recovery-1 aa7856977e80d11833e97b4151f400a516316179
```
我又不甘心地看了看`git fsck`命令，发现它居然有一个`--lost-found`的参数可以用，这样子，我居然就得到一个名为`lost-found`的文件夹，它里面有一些以 hash 命名的文件，我挑选了一个离我蓝屏时间最近的文件，直接`git checkout`过去，发现这正是我需要的内容，赶紧`git checkout –b`存档，这实在是太珍贵了！
```bash
$ git fsck --lost-found
error: inflate: data stream error (unknown compression method)
error: unable to unpack header of .git/objects/67/781ba4991aee01c0bc0d640ae9ee8b674b2f47
error: 67781ba4991aee01c0bc0d640ae9ee8b674b2f47: object corrupt or missing: .git/objects/67/781ba4991aee01c0bc0d640ae9ee8b674b2f47
error: inflate: data stream error (unknown compression method)
error: unable to unpack header of .git/objects/6f/34f2bbde304619622f77f9ca159ed97b6ddafd
error: 6f34f2bbde304619622f77f9ca159ed97b6ddafd: object corrupt or missing: .git/objects/6f/34f2bbde304619622f77f9ca159ed97b6ddafd
error: inflate: data stream error (unknown compression method)
error: unable to unpack header of .git/objects/89/6e969a25c2238ebbb41e895753e82da1cdc7af
error: 896e969a25c2238ebbb41e895753e82da1cdc7af: object corrupt or missing: .git/objects/89/6e969a25c2238ebbb41e895753e82da1cdc7af
error: inflate: data stream error (unknown compression method)
error: unable to unpack header of .git/objects/d8/a180969f6cf8047def4b50c7c920dcd2b6f5cd
error: d8a180969f6cf8047def4b50c7c920dcd2b6f5cd: object corrupt or missing: .git/objects/d8/a180969f6cf8047def4b50c7c920dcd2b6f5cd
```
其实，接触 Git 的这些年里，使用命令行并没有让我觉得 Git 难以接近，相反它让我对 GUI 理解更深一点，就像好多人分不清`pull`和`fetch`，因为你不看命令行的输出啊；有好多人每次 SourceTree 一报错就不知道该怎么办 ，其实 Git 给的提示真的相当清晰了；我之前一直不知道什么叫`cherry-pick`，后来发现这玩意儿就是我们所说的“补丁”。平时这种问题可能就放过去了，可这次“扶大厦于将顷”，让代码失而复得的经历，的确令人难忘，所以，我更想把它写下来，当你都能真正驾驭它了，是用命令行还是用 GUI 就真的不在重要啦！这次的一个例外是索引没有坏，如果索引坏了，可以试试下面的命令：`git reset --mixed`。我还是坚持一个观点，**Git 仓库坏了，能修复尽量去修复，不到万不得已，千万不要去删`. git`目录**。

# 各种场景下的 Git 恢复/撤销

在这篇文章刚开始的时候，我问大家，如何做到湿了鞋子而不慌呢？答案是脚上无凉鞋而心中有凉鞋。虽然 Git 本身是一款非常复杂的软件，可我们依然有很多的策略去应对各种“失误”，正如这篇文章 [Undoing all kinds of mistakes](https://git.seveas.net/undoing-all-kinds-of-mistakes.html#undoing-all-kinds-of-mistakes) 所言，Git 深知人类都是不完美的，面对平时使用 Git 过程中的各种失误，我们可以尝试使用下面的思路来解决。

## 更改未提交到暂存区
```Shell
//放弃所有文件的更改
$ git reset --hard
//放弃指定文件的更新
$ git checkout -- <path/to/file>
```

## 更改已提交到暂存区
```Shell
//回到最近的一次提交(改变指针)
$ git reset --hard HEAD^
//回到某一次提交(改变指针)
$ git reset --hard <commitId>
//全部放弃=回到最近的一次提交(改变指针)
$ git reset --hard 全部放弃
//放弃提交指定文件
$ git reset HEAD <path/to/file>
//修改提交信息
$ git commit --amend
```

## 更改已推送到远程服务器
```Shell
//撤销前一次提交(产生新的提交)
$ git revert HEAD 
//撤销前前一次提交(产生新的提交) 
$ git revert HEAD^
//撤销某一个提交(产生新的提交)
$ git revert commit  
```

## 万能公式
```Shell
//万能公式
$ git reflog
$ git checkout <commitId>
//退而求其次
$ git fsck --lost-found
```

除了 SourceTree，我想安利第二个 Git GUI 工具：[Fork](https://git-fork.com/)，大家感兴趣的话可以安装试用。

# 参考链接
* [Repairing and recovering broken git repositories](https://git.seveas.net/repairing-and-recovering-broken-git-repositories.html)
* [Git 撤销&回滚操作](https://zhuanlan.zhihu.com/p/72091550?utm_source=cn.wiz.note&utm_medium=social&utm_oi=53182268964864)
* [Git 撤销合并](http://blog.psjay.com/posts/git-revert-merge-commit/)
* [How to get the parents of a merge commit in git?](https://stackoverflow.com/questions/9059335/get-parents-of-a-merge-commit-in-git)







