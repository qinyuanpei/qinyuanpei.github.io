title: Unity3D游戏开发之从Unity3D项目版本控制说起
date: 2015-07-02 09:35:42
categories: [Unity3D]
tags: [版本控制,Unity3D,SVN,Github]
---

&emsp;&emsp;各位朋友，大家好，欢迎大家关注我的博客，我是秦元培，我的独立博客地址是[http://qinyuanpei.com](http://qinyuanpei.com)、CSDN博客地址是[http://blog.csdn.net/qinyuanpei](http://blog.csdn.net/qinyuanpei)。今天我想和大家聊聊Unity3D游戏项目的版本控制。

<!--more-->

##1、为什么要进行版本控制？

&emsp;&emsp;当我一个人写代码的时候，在我的脑海中是不存在版本控制这个概念的，因为我对整个项目的代码如数家珍。可是当我和一群人在一起写代码的时候，我可能并不会清楚团队中有谁修改了哪一行代码，即使是一个变量的名称或者是一个函数的名称，在我毫不知情的情况下，可能这样的修改会使得程序无法运行，这个时候我需要版本控制；尽管Unity3D是一个适合小团队开发的游戏引擎，可是即使再小的团队同样会有不同的分工，当大家需要将各自的工作合并到一个完整的项目中的时候，这个时候我需要版本控制；当我需要了解团队成员实际的编程能力的时候，最好的方法是让他们参与到一个项目的开发中，这样我可以从他提交代码的情况了解他的工作能力，这个时候我需要版本控制；当我希望时时刻刻对项目进行备份，并在某一个关键的时刻将项目恢复到一个正确的状态的时候，复制、黏贴不会让这个工作变得简单，这个时候我需要版本控制。

##2、怎样在Unity3D中进行版本控制？

&emsp;&emsp;在Unity3D中进行版本控制主要针对Assets和ProjectSetting这两个文件夹，因为除此以外的文件和文件夹都是Unity3D在运行过程中产生的临时文件，这些文件会在使用Unity3D打开项目后重新生成，因此无需对这些文件或文件夹进行版本控制。好了，在了解了Unity3D版本控制中需要关注的主要内容后，接下来我们要关注的是怎样让版本控制的软件对我们提交的内容进行差异化识别，我们知道版本控制的一个核心任务就是将服务器上的文件和本地的文件进行比对，找出哪些文件是最新生成的、哪些文件是被修改过的等等。因此为了方便版本控制软件对文件进行比对，常常需要项目变动的这些因素转化为文本形式，如果熟悉Github的朋友应该知道，Github中判断两个文件的差异就是根据文本(代码)来比较的，因此在Unity3D中使用版本控制同样需要遵循这个原则，好在Unity3D在管理Unity3D项目时已经考虑到了这一点，通常在对Unity3D项目进行版本控制的时候，我们需要做这样的事情：

* 通过Edit->Project Settings->Editor菜单打开编辑器设置选项，将Version Control选项下的Mode设为Visual Meta Files，这样Unity3D将为项目中的每个文件或者每个文件夹生成对应的.Meta文件。该文件是一个文本文件，记录了对应文件的相关信息，版本控制软件可以以此来对文件版本进行对比和合并操作。

* Unity3D中的资源默认是以二进制的形式进行组织的，这种组织方式对版本控制来说是不合适的，因此需要通过通过Edit->Project Settings->Editor菜单打开编辑器设置选项，将Asset Serialization下的Mode设为Force Text。

* 通过Edit->Prefences->External Tools找到Revision Control Diff/Merge选项，在安装了版本控制软件后可以在这里找到相关的选项，以博主为例，博主使用的是TortoiseSVN，这里的选项是TortoiseMegre。目前Unity3D支持的版本控制软件有SourceGear DiffMerge、TKDiff、P4Megre、TortoiseMegre、WinMegre、PlasticSCM Megre。

![编辑器设置](http://img.blog.csdn.net/20150702094529611)      ![编辑器设置](http://img.blog.csdn.net/20150702094714776)


&emsp;&emsp;好了，在完成以上准备工作后，我们就可以开始进行Unity3D项目的版本控制了，目前在Unity3D中我们主要有以下三种方式来对Unity3D项目进行版本控制：

###2.1、使用Asset Server进行版本控制

&emsp;&emsp;Unity3D的[Asset Server](http://unity3d.com/unity/team/assetserver/)是一个Unity3D内部集成的版本控制软件，它和我们熟知的SVN类似，适合在小团队内进行版本控制，这是一个收费软件，尽管在某些方面它甚至比SVN还要方便，不过在实际的项目中使用这个的还是比较少的，所以如果大家对这个感兴趣，可以从这里了解它的具体情况，这里我们不打算介绍这个软件的使用。

[Unity3D游戏制作（四）——Asset Server搭建](http://blog.csdn.net/amazonzx/article/details/7980117)

[【教程】Asset Server（联合开发）](http://tieba.baidu.com/p/2419391804)

###2.2、使用Github进行版本控制

&emsp;&emsp;使用Github进行版本控制时可以在Git仓库中添加一个.gitignore文件来对项目中需要同步的文件进行过滤，在文章开始我们已经知道Unity3D项目的版本控制主要针对Assets和ProjectSetting这两个文件，因此.gitignore的内容可以这样填写:
```
Library/
Temp/
*.sln
*.csproj
*.sln
*.userprefs
*.unityproj
*.DS_Store
```

&emsp;&emsp;这样每次提交文件的时候Github将忽略这些文件的更改。关于Github的使用及其相关命令可以查看这里：

[总结自己的Git常用命令](http://www.cnblogs.com/lwzz/archive/2013/02/23/2921426.html)

[Git远程操作详解](http://www.ruanyifeng.com/blog/2014/06/git_remote.html)


&emsp;&emsp;Github中每个仓库的容量限制为1G，适合小项目的版本控制，对于大型项目的版本控制应该考虑使用SVN。

###2.3、使用SVN进行版本控制

&emsp;&emsp;使用SVN进行版本控制时可以通过右键菜单将某些文件和文件夹添加到忽略的文件列表中，这样SVN在每次提交文件的时候将忽略这些文件的更改。这块儿其实和Github的.gitignore是相同的。SVN常用的软件组合是 TortoiseSVN(客户端)+VisualSVN Server(服务端)，具体内容请参考这2篇文章：[SVN使用教程总结](http://www.cnblogs.com/armyfai/p/3985660.html)和[客户端TortoiseSVN的安装及使用方法 ](http://blog.chinaunix.net/uid-27004869-id-4112057.html)

##3、小结

&emsp;&emsp;不管使用什么版本控制软件，建立相关的代码提交规范和流程控制规范都是必要的，因此在团队中应该有一个人负责对团队成员提交的代码进行审核和规范化，这样可以减少因为因为代码提交而产生的各种问题。好了，今天这篇文章先写到这里了，希望大家喜欢！
