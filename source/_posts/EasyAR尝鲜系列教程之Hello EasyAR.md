﻿---
abbrlink: 3120185261
categories:
- Unity3D
date: 2015-10-30 09:44:18
description: 从今天起博主将为大家带来EasyAR尝鲜系列教程，本教程适用的对象是增强现实应用开发者和Unity3D游戏开发者，在阅读本教程前请确保具备增强现实应用开发及Unity3D游戏开发的相关基础知识;在本节及后续内容中，博主将以国产增强现实引擎EasyAR为主要开发平台来带领大家一起走进增强现实应用开发的世界，希望大家能够喜欢;[增强现实概念图](https://ww1.sinaimg.cn/large/4c36074fly1fziy7k2yssj20m80b4tad.jpg)
tags:
- 增强现实
- AR
- Unity3D
- 教程
title: EasyAR尝鲜系列教程之Hello EasyAR
---

&emsp;&emsp;各位朋友，大家好，我是秦元培，欢迎大家关注我的博客，我的博客地址是[http://qinyuanpei.com](http://qinyuanpei.com)。从今天起博主将为大家带来EasyAR尝鲜系列教程，本教程适用的对象是增强现实应用开发者和Unity3D游戏开发者，在阅读本教程前请确保具备增强现实应用开发及Unity3D游戏开发的相关基础知识。在本节及后续内容中，博主将以国产增强现实引擎EasyAR为主要开发平台来带领大家一起走进增强现实应用开发的世界，希望大家能够喜欢！

<!--more-->

# 什么是增强现实？
&emsp;&emsp;为了让更多的人了解增强现实，所以在开始本文教程前，我们首先来了解下什么是增强现实。增强现实(Augmented Reality，简称 AR)，它是一种将真实世界信息和虚拟世界信息进行融合和集成的新技术，这种技术的目标是在屏幕上把虚拟世界和现实世界进行叠加并在此基础上进行互动。增强现实是真实世界和虚拟世界的信息集成，具有实时交互性，是在三维尺度空间中增添定位虚拟物体。增强现实技术可广泛应用到军事、医疗、建筑、教育、工程、影视、娱乐等领域。增强现实是新型的人机交互和三维仿真工具，目前已发挥出了重要的作用，具有巨大的应用潜力。

![增强现实概念图](https://ww1.sinaimg.cn/large/4c36074fly1fziy7k2yssj20m80b4tad.jpg)

# 增强现实应用现状
&emsp;&emsp;目前，增强现实在国内尚处在起步阶段。2012年4月Google发布的Google Class是全球唯一一款真正意义上实现增强现实技术的硬件设备。随着移动设备的普及和相关技术的成熟，增强现实开始逐渐地走进人们的生活。如国内首款聚合了目前移动互联最新增强现实技术的智能手机应用《城市镜头》以及中视典数字科技研发的VRP系统等。AR技术在人工智能、CAD、图形仿真、虚拟通讯、遥感、娱乐、模拟训练等许多领域带来了革命性的变化。
目前增强现实相关技术主要有开源社区的[ARToolkit](http://www.hitl.washington.edu/artoolkit/)、面向商业化解决方案的[Metaio](http://www.metaio.com/)和[Vuforia](http://developer.vuforia.com/)等。

# 国产增强现实引擎EasyAR
&emsp;&emsp;EasyAR(Easy Augmented Reality)是视辰信息科技（上海）有限公司的增强现实解决方案系列的子品牌，其含义是希望让增强现实变得简单易实施。EasyAR提供了诸如手机APP互动营销、户外大屏幕互动活动、网络营销互动等形式在内的增强现实互动营销技术和解决方案。著作权归作者所有。EasyAR无需授权、无水印、无识别次数的限制，开放后可免费下载，无需任何费用，是一款完全免费的AR引擎。EasyAR具有强大的跨平台特性可支持Windows、 Mac OS、 Android和iOS等主流平台。从目前的情况来看，EasyAR的SDK是目前市场上同类产品中最为简单易用的，唯一的不足是产品刚发布不久尚未能提供完整的技术文档。

# Hello EasyAR
&emsp;&emsp;好了，下面我们以[EasyAR](http://www.easyar.cn/view/index.html)提供的Unity3D版本SDK为例来学习EasySDK的使用。在开始前请确保你的计算机上正确安装了以下开发工具或者硬件：

* Unity3D(必选)：主要的开发环境
* JDK相关工具(必选)：编译Android应用所需环境
* Android SDK(必选)：编译Android应用所需环境
* 摄像头(可选)：如使用手机进行调试则不需要

在完成以上准备工作后：

* 打开[EasyAR官网](http://www.easyar.cn/view/index.html)并登录官网，我们将在登陆后创建应用以获得开发所需的密钥以及SDK。如果尚未注册可以在注册后完成这一步骤。

![创建应用](https://ww1.sinaimg.cn/large/4c36074fly1fziy4rryipj20b60aj3zh.jpg)

* 点击创建应用，并在这里填入应用的名称和包的名称，此处以“EasyAR测试”和“com.easyar.first”为例，在创建完应用后可以在应用列表中找到当前创建的应用，点击显示可以查看当前应用对应的密钥。
* 点击“下载EasyAR SDK v1.0.1”完成SDK的下载。

![下载SDK](https://ww1.sinaimg.cn/large/4c36074fly1fzixy15c8yj20rd06tac3.jpg)

* 解压下载的SDK压缩包，找到vc_redist目录安装对应平台的VC++运行库。请注意，即使在你的计算机上安装了VC++运行库，这里依然需要安装。Win8及Win8.1请先使用磁盘清理工具清理系统垃圾，否则可能会出现无法安装的问题。建议使用64位操作系统且安装x86和x64的VC++运行库。
*  找到SDK压缩包内的package/unity目录下的EasyAR.unitypackage文件并将其导入到Unity3D中。
* 在Unity3D中找到Scenes目录下的easyar场景并打开该场景，然后找到EasyAR节点名称，在右侧属性窗口中填入应用对应的密钥。

![填入应用程序密钥](https://ww1.sinaimg.cn/large/4c36074fly1fzixb6r81jj20gt0i70u6.jpg)

* 打开BuildSetting->PlayerSetting在右侧属性窗口中填入应用对应的包名。

![填入应用程序包名](https://ww1.sinaimg.cn/large/4c36074fly1fzix80mo33j208z0ewjrt.jpg)

* SDK默认提供了三张识别图片，我们选择每个人都有的身份证照片作为识别目标，在场景中找到ImageTargetDataSet-idback这个物体，找到它的子节点Cube。这意味着如果我们识别到了身份证照片，那么就会在身份证照片上显示一个Cube。如果大家手头上有自己喜欢的模型，可以将Cube隐藏，然后将模型添加进来，并为其添加VideoPlayerBehaviour.cs脚本。如手头上没有模型，这一步可以忽略。如图是我现在的场景效果：

![加入自定义模型后的效果](https://ww1.sinaimg.cn/large/4c36074fly1fzix17ov4dj20dl0c7js5.jpg)

&emsp;&emsp;好了，现在编译程序，将其导出为APK安装包，这样我们就可以在手机上测试EasyAR的效果啦。假如一切顺利的话，在手机上将会看到这样的画面。下面放点运行情况截图供大家参考：

![截图1](https://ww1.sinaimg.cn/large/None.jpg)

![截图2](https://ww1.sinaimg.cn/large/None.jpg)


# 问题汇总
&emsp;&emsp;作为一款国产的增强现实引擎，目前EasyAR的表现我还是比较满意的，虽然在识别的准确度上无法和国外的同类产品相比，但是它的简单易用确实是做得不错。作为一个程序员尝鲜更像是吃螃蟹，目前发现的问题及解决方案有：

*  编辑器提示DllNotFoundException错误，请安装SDK中对应的VC++运行库。
*  视频导入失败，Unity3D导入视频需要依赖苹果公司的QuickTime播放器，所以请安装最新版的QuickTime后重试。
* 在64位计算机上编译的Android应用可以正常运行，在32位计算机上编译的Android应用无法正常运行。具体表现如图

![32位计算机下的问题](https://ww1.sinaimg.cn/large/4c36074fly1fz68j0wjkcj20dc0m8tb0.jpg)

&emsp;&emsp;好了，作为整个系列的第一篇文章，我们至此对EasyAR有了一个较为直观的印象。在接下来的内容中，我们将对SDK中的内容进行更加深入的了解，因此希望大家继续关注我的博客，谢谢大家！