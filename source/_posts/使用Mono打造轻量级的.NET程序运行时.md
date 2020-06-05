---
abbrlink: 907824546
categories:
- 编程语言
date: 2016-03-25 12:47:58
description: 我们将编译好的程序命名为Launcher.exe，放置我们前面定义的Mono运行时目录结构的根目录下，这个文件将作为启动文件暴露给用户，当用户点击这个程序后就可以打开主文件Main.exe;因为Mono和.NET都可以执行IL代码，所以我用Mono来作为.NET程序的运行时是一个顺理成章的想法;本文通过Mono实现了一个轻量级的.NET程序运行环境，从某种程度上来说，它间接地实现了.NET程序脱离.NET
  Framework运行
tags:
- .NET
- Mono
- 跨平台
title: 使用Mono打造轻量级的.NET程序运行时
---

&emsp;&emsp;在[使用Mono让.NET程序跨平台运行]()这篇文章中，我们已经对Mono以及.NET程序的运行机制有了初步的理解。今天我想来谈谈"使用Mono打造轻量级的.NET运行时"这样一个话题。为什么我会有这样一种想法呢？因为Mono和.NET都可以执行IL代码，所以我用Mono来作为.NET程序的运行时是一个顺理成章的想法。由于.NET程序需要.NET Framework提供运行支持，所以当目标设备没有安装.NET Framework或者.NET Framework版本不对的时候，我们的程序都无法顺利运行。强迫用户安装.NET框架无疑会影响用户体验，在Windows XP尚未停止服务前，国内软件厂商为了兼容这些用户，通常会选择C++这类语言来编写原生应用，这就造成了国内.NET技术长期不被重视的现状。

<!--more-->
# 考虑.NET版本的兼容
&emsp;&emsp;在考虑使用Mono来作为.NET应用程序的运行时前，首先我们来考虑.NET版本的兼容问题。假设我们使用.NET Framework 3.5版本生成了一个应用程序，那么这个应用程序将在安装了.NET Framework v3.5的计算机上运行，如果目标计算机上没有安装.NET Framework v3.5，这个应用程序将无法正常运行。这个时候，我们可以有两种解决方案：第一种，强迫用户安装.NET Framework v3.5，无论是将该框架集成到安装包中，还是在安装软件的时候自动从网上下载安装，显然这种方式都会影响用户的使用体验让用户对应用程序的印象大打折扣；第二种，尝试让应用程序和.NET版本兼容。我们知道Android程序有一个最低API版本的设置，这样能够保证应用程序在不低于该API版本的设备上运行。这里我们选择这种思路，在.NET程序中，我们可以通过应用程序配置文件中的supportedRuntime节点来指定应用程序运行的.NET Framework版本。例如下面的配置文件能够保证应用程序在.NET Framework v2.0到v3.5间的版本上运行。

```
<?xml version="1.0"?>
<configuration>
    <startup> 
    <supportedRuntime version="v2.0.50727"/>
    <supportedRuntime version="v3.0"/>
    <supportedRuntime version="v3.5"/>
    </startup>
</configuration>
```
虽然说这样能够保证应用程序的兼容性，可是你这个应用程序的命运却是掌握在.NET Framework手里的，如果用户的计算机上没有安装.NET Framework我们一样还是没辙儿，那么怎么办呢？我们来搭建Mono运行时。

# Mono运行时的搭建
&emsp;&emsp;我们在前面说过，Mono主要由三部分组成，即C#编译器(mcs.exe)、Mono运行时(mono.exe)和基础类库。因为我们这里是为了让编写的.NET应用程序运行在Mono运行时中，所以我们这里需要的是Mono运行时(mono.exe)和基础类库。我们建立如下的目录结构：

![Mono运行时目录结构](https://ww1.sinaimg.cn/large/4c36074fly1fzixya9n45j20dz047t9c.jpg)

下面来说说这些目录各自的结构和功能：
* bin目录：放置Mono运行时的目录，主要放置mono.exe、mono-2.0.dll、libgio-2.0-0.dll、libglib-2.0-0.dll、libgthread-2.0-0.dll共5个文件。
* lib目录：放置Mono依赖库的目录，主要放置.NET库目录(此处以4.0为例)、Gac库目录。其中Gac库目录下的Accessibility、Mono.Posix、System、System.Drawing、System.Windows.Forms共5个子目录是我们开发WindowsForm需要使用到的依赖库。
* etc目录：放置我们编写的程序及其相关文件，主程序的文件名为Main.exe。

&emsp;&emsp;好了，现在我们就具备了一个非常轻量级的.NET程序运行环境(其实整个环境的大小在40M左右)，注意以上文件都可以在安装Mono在其安装目录内找到。根据博主目前了解到的资料来看，通过Mono运行时来运行文件主要有命令行和一种被称为Mono Embedding的方案。特别地，第二种方案可以直接将运行时嵌入到程序内，我们熟悉的Unity3D引擎就是将整个脚本的运行时嵌入到了C++程序中，但是这种方式比较复杂，暂时博主还没有弄清楚它的内部机制，所以我们这里选择第一种方案。可是它要用命令行啊，迫使普通用户来使用命令行工具是件痛苦的事情，就像我们常常被Git搞得晕头转向一样。那么，我们就用程序来模拟命令行好了！什么？用程序来模拟命令行？这个用C#来写简直不能更简单了好吗？请注意我们这里是不能使用.NET Framework里的功能的，因为它就是一个引导程序嘛，如果引导程序都需要依赖.NET，那我们这个程序怎么搞啊。

&emsp;&emsp;好嘛，那就写C++原生应用吧，它是无需任何依赖的。而在C++中模拟命令行主要有WinExec、ShellExecute和CreateProcess三种方法，关于这三种方法的异同大家可以自行了解，这里我们选择最简单的WinExec。代码如下：
```
#include <Windows.h>

int main(int agrc,char *args[])
{

    /* 执行命令 */
    WinExec("bin\\mono.exe etc\\Main.exe",SW_NORMAL);
    return 0;
}
```
我们将编译好的程序命名为Launcher.exe，放置我们前面定义的Mono运行时目录结构的根目录下，这个文件将作为启动文件暴露给用户，当用户点击这个程序后就可以打开主文件Main.exe。好了，现在我们来验证下我们的想法：

![运行在Mono运行时下的程序](https://ww1.sinaimg.cn/large/4c36074fly1fzixbbzwmij20kb0dz0vk.jpg)

作为对比，我们给出正常情况下程序的运行截图：

![运行在.NET框架下的程序](https://ww1.sinaimg.cn/large/4c36074fly1fzix8asiluj20kv0gngoo.jpg)

这样我们现在这个程序就基本实现了脱离.NET框架运行，为什么说是基本呢？因为.NET中的基础类库是作为.NET框架中的一部分存在的，即它并非是CLR的内容。所以我们现在使用到的大部分的基础类库都是Mono重新实现的版本，如果我们使用的某一个库在Mono中没有相应的实现，那么我们就需要自己想办法来解决依赖问题了。现在这个方案每次运行的时候都会闪出命令行窗口，虽然不影响使用，但对一个追求完美的人来说就是瑕疵啦，怎么解决呢？答案就是Mono Embedding。

#  本文小结
&emsp;&emsp;本文通过Mono实现了一个轻量级的.NET程序运行环境，从某种程度上来说，它间接地实现了.NET程序脱离.NET Framework运行。这个方案目前看起来存在的主要问题是库依赖的问题，我们现在这个环境有将近40M左右的体积，这是因为我们将常用的库都放在了lib目录中，可是在实际运行中，这些库并非完全都会用到，因此如何根据程序来生成合适的lib目录，是解决运行时环境体积的有效方法。如果靠手动来解决这个问题，这显得困难重重，因为在平时微软将这些库都给我们了，它就在我们的计算机上，所以我们从来没有关注过这个问题。现在当我们面对这个问题的时候，反射可能是种不错的想法，但这种想法的验证就要等到以后啦！