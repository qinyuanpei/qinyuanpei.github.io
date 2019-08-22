---
title: 在WSL中使用Linux桌面环境的尝试与总结
categories:
  - 开发工具
tags:
  - WSL
  - Linux
  - 桌面
abbrlink: 3972610476
date: 2019-08-17 21:09:46
---

最近忙里偷闲的博主，再次迷恋上折腾Linux。话说自从微软推出WSL以后，我就彻底地停止了Windows + Linux 的双系统组合。回想起从前使用过的各种Linux发行版，基本上每隔一段时间就会崩溃一次，所以，面对WSL这种近乎`应用`级别的方案，我个人是非常愿意去接受的。因为一不小心玩坏了的话，可以直接对应用程序进行重置，或者重新从应用商店下载，相比重装系统，我觉得这种方式要更友好一点。虽然说Windows10是有史以来最好的Linux发行版:smile:，可面对只有命令行的Linux，果然还是有一丝丝的失望啊:beetle:。所以，在这篇博客里，主要想和大家分享下，关于在WSL下使用Linux桌面系统的一点点尝试和体会。虽然目前应用商店里已经提供了Ubuntu、Debian、Kail Linux、OpenSUSE这些常见的发行版，可当你熟悉了Linux的世界以后，就会明白这个世界对多元化的追求是永无止境的，我不想去Judge这些多元化间优劣，我只想自由地使用我喜欢的技术，比如Linux Deepin、Elementary OS。这是我想要使用Linux桌面环境的理由。

我们知道，目前应用商店里提供的Linux发行版都是`"命令行"`版本。因为Windows本身就提供了非常出色的桌面环境，虽然每一次设计都给人一种相当前卫的感觉。平时我们使用`SSH`登录远程服务器的时候，其实是使用它的终端环境即CLI。Linux和Windows最大的不同在于，Linux 的桌面环境并不是Linux本身的一部分，它和所有的Linux应用程序并没有什么区别，因为脱离桌面环境的Linux的单独运行，而脱离桌面环境的Windows则未必可以。那么，我们怎么样在Windows里使用Linux的桌面环境呢？常见的思路主要有`XServer`和`远程桌面`两种。这里我们主要介绍第一种方式，即`XServer`。什么是XServer呢？Linux的GUI架构其实是C/S模式的，其中XServer负责显示，XClient负责请求。所以，我们只要在宿主机上安装XServer就可以啦。在这里，常见的XServer主要有：`VcXsrv`、`X410`和`MobaXterm`。理论上，我们只需要在WSL里安装桌面环境，在Windows上安装XServer，然后通过命令行启动相应桌面环境即可。

作为一个最流行的Linux发行版，微软非常贴心地给出了16.04和18.04两个版本。不过随着博主不甘寂寞地一通升级以后，最终还是稳定在了18.04这个版本。既然选择从Ubuntu这个发行版开始折腾，不如从它默认的桌面环境Gnome开始折腾吧！虽然我个人一直不太喜欢这个风格，不然就不会有接下来针对`Pantheon`和`Deepin`两个桌面环境的作死啦。这个过程最有意思的事情，居然是发现了一个更轻量级的桌面环境，可能真的是`"无心插柳柳成荫"`吧。好了，关于如何开启WSL及安装Linux发行版的过程不再多说。首先，让我们把系统默认的源切换到阿里云，因为这样能节省博主和大家的时间。:slightly_smiling_face:

```Shell
sudo cp /etc/apt/sources.list /etc/apt/sources.list.2019016
sudo vim /etc/apt/sources.list
```

接下来，我们使用下面的命令对文件内容进行替换, 或者你可以手动逐行去编辑。

```shell
:%s/security.ubuntu/mirrors.aliyun/g
:%s/archive.ubuntu/mirrors.aliyun/g
```

除此以外，还推荐大家使用以下国内的镜像源：

清华大学镜像源：<https://mirrors.tuna.tsinghua.edu.cn/help/ubuntu/>

网易开源镜像站：<http://mirrors.163.com/.help/ubuntu.html>

完成镜像源的切换以后，我们就可以愉快地使用`apt-get update`刷一波存在感啦，话说最近看到一条微博，建议给`sudo`起一个别名`plz`或者`pls`。除了调侃以外，可能更多是想把冰冷的命令行变得充满人情味吧。Windows下安装`VcXsrv`大家都轻车熟路啦，这个不再过多的说明。下面，我们来安装以下Ubuntu桌面环境：

```shell
echo "y"|sudo apt-get install ubuntu-desktop unity compizconfig-settings-manager
sudo dpkg-reconfigure dbus && service dbus restart
```

接下来配置`XLaunch`，这是我们安装完`VcXsrv`后自带一个应用程序：

![配置XLaunch](https://ws1.sinaimg.cn/large/4c36074fly1g633ck83tij20ek0bpwfg.jpg)

按照默认配置直至完成后我，我们会发现桌面上出现了一个黑色的窗口，如下图所示：

![XLaunch经典黑屏](https://ws1.sinaimg.cn/large/4c36074fly1g633jddpbcj21200lcabq.jpg)

此时，我们在Ubuntu的Bash窗口中输入`sudo compiz`命令并切回`XLaunch`界面。接下来，就是见证奇迹的时刻：

![经典的Ubuntu桌面](https://ws1.sinaimg.cn/large/4c36074fly1g67nqmov1yj21410p0qdr.jpg)

如你所见，这是Ubuntu默认的Unity桌面，博主一开始是在Ubuntu16.04上研(折)究(腾)的，当时安装完以后桌面其实是黑色的，因为当时并没有保留下这历史性的一刻，所以，从网上找了张图来这里充数啦，这张图片出自：[Run any Desktop Environment in WSL](https://github.com/microsoft/WSL/issues/637)。

OK，既然Ubuntu可以装桌面，那么，衍生自Ubuntu的Elementary OS和Linux Deepin应该同样可以吧，虽然目前应用商店里还有这两个发行版。本着不折腾就不会死的选择，先装个Elementary OS的桌面环境试试呗！我个人挺喜欢这个发行版的，理由是默认主题样式就很好看，同理，Linux Deepin除了好看以外，本身就带有大量优秀的软件。所以说，人类果然还是始于颜值的啊！Elementary OS使用的桌面环境是Pantheon，我们可以通过下面的命令行快速安装：
```Shell
sudo add-apt-repository ppa:elementary-os/stable
sudo apt update
sudo apt install elementary-desktop
```
通常，每个桌面环境都会自带一部分“最佳”适配的应用程序，考虑到WSL并不是一个完整的Linux实现，我们在这里卸载掉一部分WSL下不支持的应用程序。而微软新推出的WSL2，则是基于VM的实现，两种方式完全没有可比性，这里不做无意义的争论：
```Shell
sudo apt purge gnome-screensaver \
switchboard-plug-power switchboard-plug-bluetooth switchboard-plug-networking \
wingpanel-indicator-bluetooth wingpanel
```
参考[Installing Pantheon Desktop On Ubuntu](https://token2shell.com/howto/x410/installing-pantheon-desktop-on-ubuntu-wsl/)这篇文章中的建议，为了启动Pantheon桌面环境，我们需要 `gala`、 `plank`和`wingpanel`三个软件，它们的作用有点像前面的`compiz`。而关于`X410`，你可以把它理解为和`VcXsrv`类似的软件，不同的是这是一个付费软件，作者写了一系列的博客来推广它。接下来，在安装`gala`的过程中，你大概会遇到这个错误：
```Shell
The following packages have unmet dependencies:
gala : Depends: libmutter-2-0 (>= 3.28.4-0ubuntu18.04.1+elementary4~ubuntu5.0.1) but 3.28.4-0ubuntu18.04.1 is to be installed
E: Unable to correct problems, you have held broken packages.
```
我向作者发邮件寻求帮助，作者非常热心地回复了我三次邮件，对方表示应该是Elementary OS团队正在基于Ubuntu19.04开发新版本，所以可能没有意识到`elementary-desktop`这个包已经broken了，并且他们在18.04版本上复现了这个问题，建议我直接联系官方。好吧，博主的英语表示受宠若惊，邮件在此为证：

![来自国外网友的热心指导](https://ws1.sinaimg.cn/large/4c36074fly1g6877vhqhcj20io0hut9u.jpg)


总而言之，博主试图在WSL上体验Elementary OS的想法彻底失败，既然这个最美的Linux发行版已失败告终，并不打算就此罢手的博主，决定继续在命令行终端里折腾Linux Deepin。这个发行版是我从大学时开始接触的Linux发行版，那时有个小学弟第一次给我介绍了Linux Mint，不过我对这个版本实在爱不起来，因为太像Windows了啊，可谁能想到若干年后，Windows反而变成了最好的Linux发行版呢(:smile:)，果真是`“人生不相见，动如参与商”`啊……

好啦，继续敲命令。Linux Deepin的桌面环境是Deepin Desktop Environment，简称dde：
```Shell 
sudo add-apt-repository ppa:leaeasy/dde
sudo apt-get update
sudo apt install dde dde-file-manager
```
Linux Deepin安装是非常顺畅的，但即便安装完这个桌面环境，博主还是不知道怎么启动这个环境，因为你常规使用Ubuntu的话，安装完切换桌面管理器就可以了，可当你用WSL这种方式使用Ubuntu的时候，可能你就会感到非常困惑。相比之下，`xfce`就让人感觉友好得多，因为它只有一个命令`startxfce4`，而安装只需要安装`xfce4`和`xfce4-terminal`就可以了。在对比了Gnome、KDE、Unity、Mint、xfce等等的桌面环境以后，我觉得Linux在桌面市场输给Windows是理所当然的，因为实在太混乱了，WSL下需要的应该是一个轻量级的桌面，因为越是华而不实东西，越会消耗大量资源。我最初想要折腾桌面环境，无非是为了下面这个结果，撒花完结，以上！

![简洁/简陋的xfce桌面](https://ws1.sinaimg.cn/large/4c36074fly1g67nrxqcm4j21hc0u0nat.jpg)