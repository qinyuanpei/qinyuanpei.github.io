---
abbrlink: 3568552646
categories:
- 编程语言
date: 2016-11-18 20:23:44
description: 我们现在按 F5 进行调试，和编译时一样，如果用户没有为当前项目配置“任务调试程序”，VSCode 会提示我们去创建一个配置文件 launch.json，我们这里选择 mono，该选项在安装 Mono-Debug 插件以前是没有的，该配置文件如下，我们注意到这里需要修改 program 属性为 MainClass.exe:;现在，我们应该会得到一个 MainClass.exe 的文件，最初博主尝试直接去配置 launch.json，发现直接填写 type 为 mono 在 VSCode 中是无法识别的，最后决定去安装 mono-debug 的插件，安装插件在 VSCode 中是非常简单的，按下 Ctrl+Shift+X 打开插件界面，可以在这里查看最流行的插件列表、官方推荐的插件列表等等，我们直接搜索 mono-debug 然后安装插件即可;因为博主的计算机上安装了 Mono，所以在一开始使用 VSCode 的时候，就先入为主地认为在不安装插件的情况下，应该就可以直接在 VSCode 中编译和调试代码了
tags:
- Mono
- VSCode
- 跨平台
title: 基于 Mono 和 VSCode 打造轻量级跨平台 IDE
---

&emsp;&emsp;最近 Visual Studio 推出 Mac 版本的消息迅速在技术圈里刷屏，当工程师们最喜欢的笔记本电脑 Mac，邂逅地球上最强大的集成开发环境 Visual Studio 的时候，会碰撞出怎样精彩的火花呢？在微软新任 CEO 纳德拉的“移动为先、云为先”战略下，微软的转变渐渐开始让人欣喜，从.NET Core、VSCode、TypeScript 再到近期的 Visual Studio For Mac，这一系列动作让我们感觉到，微软的技术栈越来越多地向着开源和跨平台两个方向努力。我们曾经固执地认为，微软的技术栈注定永远无法摆脱 Windows 的束缚，而事实上这个世界每天都在发生着变化。或许这次 Visual Studio 推出 Mac 版这件事情，本质上是微软收购的 Xamarin 公司旗下产品 Xamarin Studio 的一次改头换面。可是这件事情说明，微软正在努力让.NET 技术栈融入更多的应用场景。对我而言，我是没有钱去买一台 Mac 的，所以在这篇文章中，我们将在 Linux 下通过 Mono 和 VSCode 来打造一个轻量级的 IDE。而据说 Mono 会和 Xamarin 一样，将来会成为.NET 基金会的一部分。

<!--more-->

&emsp;&emsp;好了，我们首先在 Windows 世界里进行彩排，在开始下面的内容以前，请保证你的计算机上安装了 Mono 和 VSCode。假如你经常关注我的博客，你应该会知道 Mono 在这里的作用是什么？，简而言之，Mono 为我们提供了编译器环境和运行时环境，在这个基础上 VSCode 这个天生带着 Visual Studio 基因的编辑器，则可以为我们提供基础的代码调试功能，这是我们这篇文章写作的关键因素。如果你还对 Mono 一无所知，下面的两篇文章可以帮助你快速了解：

* [使用 Mono 让.NET 程序跨平台运行](http://qinyuanpei/2016/03/06/make-dotnet-run-in-cross-platform-with-mono.html)
* [使用 Mono 打造轻量级的.NET 运行时](http://qinyuanpei.com/2016/03/25/build-light-weight-runtime-for-dotnet-with-mono.html)

&emsp;&emsp;在我们了解了 Mono 以后，就可以考虑将 Mono 作为 VSCode 的运行时环境，这意味着我们可以在使用 VSCode 的同时直接编译代码。目前在 VSCode 中内建的运行时支持为 Node/Node2，所以如果我们希望在 VSCode 中调试更多的语言，我们就必须要为 VSCode 安装相应的插件。因为事实上在 VSCode 中编译代码我们可以直接通过 Task 来完成编译，但当我们希望在 VSCode 中对代码进行调试的时候，我们就必须借助插件来完成调试任务，这或许从侧面印证了 VSCode 的产品定位就是一个文本编辑器。

&emsp;&emsp;而对于微软推出的这样一款产品，我们或许会疑惑，为什么这个编辑器提供的内建支持居然是 Node，而不是我们所熟悉的.NET 技术体系。这个原因非常容易理解，如果你听说过 Github 出品的编辑器 Atom，或者是使用过 Electron/Node-Webkit 相关技术，那么你一定会深刻地理解，VSCode 本质上和 Atom 一样，都是采用 Web 技术来构建跨平台应用，而 Node 天生就具备 Web 属性加成，所以我们就不难理解为什么 VSCode 内建的支持是 Node 而非.NET 技术体系。同样地，为了实现跨平台的目标，在对 C#语言的支持这个问题上，微软选择了 OminiSharp 这样一个跨平台的代码自动补全工具，而非我们在 Visual Studio 中所熟知的 Intellisense 技术。在.NETCore 推出以后.NET 跨平台不再是梦想，我们对技术的探索就不应该再局限在 Windows 平台上。

&emsp;&emsp;博主关注 Mono 始于 Unity3D 引擎，因为 Mono 真正实现了.NET 技术的跨平台，而 Unity3D 引擎最为人所称道的当属其强悍的跨平台能力，在这一点上 Mono 功不可没。在此之前收费的 Xamarin 让人望而却步，所以 Mono 自然而然地就成为了我的选择。因为博主的计算机上安装了 Mono，所以在一开始使用 VSCode 的时候，就先入为主地认为在不安装插件的情况下，应该就可以直接在 VSCode 中编译和调试代码了。首先我们在 VSCode 中创建一个 C#代码文件，既然在程序世界里万事万物都从 Hello World 说起，那么我们这里依然遵循这个原则。在创建该代码文件以后，我们将其所在的目录在 VSCode 中打开，这是因为：

> 在 VSCode 中仅支持以目录方式打开的文件的编译和调试

所以这个时候我们在 VSCode 中的界面应该是如图所示：

![在VSCode中编写代码](https://ww1.sinaimg.cn/large/4c36074fly1fzixygvqxsj20jg077aac.jpg)

好了，下面我们直接按下 Ctrl+Shift+B 来编译代码，此时 VSCode 将提示我们“配置任务运行程序”，这里需要说明的是，在 VSCode 中你可以感受到微软对命令行和配置文件的偏执，这让适应了 Visual Studio 这样功能强大的我们相当不习惯，按照 VSCode 的提示或者是通过 Ctrl+Shift+P 打开命令面板，VSCode 将在当前工作目录下为我们创建.vscode 目录和 tasks.json 文件，在 VSCode 中任何和项目相关的配置信息都会存储在这里啦。此时我们配置 tasks.json:

```plain
{
    // See https://go.microsoft.com/fwlink/?LinkId=733558
    // for the documentation about the tasks.json format
    
    "version": "0.1.0",
    // 该命令需要在系统变量内定义
    "command": "mcs",
    // 或者使用完整的可执行路径
    // "command: "C:\Program Files\Mono\bin\mcs.exe"
    "isShellCommand": true,
    "args": ["*.cs"],
    "showOutput": "always"
}
```
在这里需要说明的是一个**tasks.json**中可以通过 tasks 属性来配置多个任务运行程序，例如我们的项目中有 Python 和 C#两种代码需要编译，那么我们就可以配置两个 task，VSCode 将在运行程序的时候让用户由哪一个 task 来编译代码。如果你看过我在前面介绍过的两篇文章，就应该知道这里的 mcs.exe 其实是 Mono 提供的 C#编译器，它负责将我们的 C#代码编译为 IL 文件，然后 IL 文件再交由 CLR 来转换为本机代码。Mono 提供的 C#编译器可以将 C#代码编译为.exe 或者是.dll，可是在 VSCode 中好像默认都是编译为.exe，所以如果有知道如何在这里配置编译输出项的朋友，希望可以告诉我怎么去实现。

&emsp;&emsp;现在，我们应该会得到一个 MainClass.exe 的文件，最初博主尝试直接去配置 launch.json，发现直接填写 type 为 mono 在 VSCode 中是无法识别的，最后决定去安装 mono-debug 的插件，安装插件在 VSCode 中是非常简单的，按下 Ctrl+Shift+X 打开插件界面，可以在这里查看最流行的插件列表、官方推荐的插件列表等等，我们直接搜索 mono-debug 然后安装插件即可。可是我不曾想到的是，我猜中故事的开头，却没有猜中故事的结尾，**这个插件是不支持 Window 平台的**，**这个插件是不支持 Windows 平台的**，**这个插件是不支持 Windows 平台的**。

&emsp;&emsp;好吧，现在看起来 Linux 是我唯一可以去尝试的平台了，博主这里选择的是颜值最高的 Elementary OS，这是一个衍生自 Ubuntu 的 Linux 发行版。在 VSCode 正式版发布以后，在 Linux 下用 VSCode 来编程是我一直在尝试的事情，请不要说 Linux 系统使用起来会非常困难，博主在安装这些软件的过程中可以说是相当顺利。建议大家在 Linux 平台下安装 C#、Mono-Debug 和 Python 这 3 个插件，需要说明的是 C#和 Mono-Debug 在第一次使用的时候，需要在网络环境下下载相关依赖。下面是博主目前的插件安装情况：

![VSCode中插件安装界面](https://ww1.sinaimg.cn/large/4c36074fly1fzixbdu00aj20910icq3j.jpg)

&emsp;&emsp;我们现在按 F5 进行调试，和编译时一样，如果用户没有为当前项目配置“任务调试程序”，VSCode 会提示我们去创建一个配置文件 launch.json，我们这里选择 mono，该选项在安装 Mono-Debug 插件以前是没有的，该配置文件如下，我们注意到这里需要修改 program 属性为 MainClass.exe:

```plain
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Launch",
            "type": "mono",
            "request": "launch",
            "program": "${workspaceRoot}/MainClass.exe",
            "args": [],
            "cwd": "${workspaceRoot}",
            "preLaunchTask": "",
            "runtimeExecutable": null,
            "env": {},
            "externalConsole": false
        },
        {
            "name": "Attach",
            "type": "mono",
            "request": "attach",
            "address": "localhost",
            "port": 5085
        }
    ]
}
```

&emsp;&emsp;这里有一个小插曲，在博主运行这个简单的程序的时候，提示 Mono 的版本和 Mono-Debug 插件的版本要求不一致，因为 Mono-Debug 插件使用的是最新版本的 Mono。所以，果断卸载目前的 mono，然后安装最新的 mono，安装方法为：
```plain
sudo apt-get install mono-complete
```
这样我们就可以看到眼前的成果啦，我们成功地在 VSCode 运行了一个 C#程序：

![VSCode中调试代码](https://ww1.sinaimg.cn/large/4c36074fly1fzix8ge8e6j211y0laq4f.jpg)

&emsp;&emsp;虽然我很想在这篇博客中搞点干货出来，但是当我折腾数天以后，我大概就能够写出这样一篇相当零碎的文章，到目前为止我还是没有搞明白，为什么我在调试地过程中，VSCode 不会在我设置了断点地地方停下来，希望知道这个原因的朋友可以告诉我啊。这个过程最有意义的地方在于让我进一步熟悉了 Linux，在不一样的地方，会有不一样的风景，这个世界很大，不要给自己设限。后续我会去研究 VSCode 中的调试技巧以及.NETCore 相关内容，能看到 C#跨平台运行是件幸福的事情，而跨平台开发是我一直在探索的方向之一。夜晚已然来临了，而这篇文章就是这样了，谢谢大家的关注，晚安！