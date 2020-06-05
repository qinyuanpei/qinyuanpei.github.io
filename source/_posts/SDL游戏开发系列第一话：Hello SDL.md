---
abbrlink: 183718218
categories:
- 游戏开发
date: 2015-07-25 15:19:01
description: '###什么是SDL;在以上代码中我们基本遵循了SDL游戏开发的一般流程，即首先对SDL进行初始化，当SDL初始化完成后，我们创建一个标题为"SDL学习示例1",窗口对齐方式为居中对齐，窗口大小为640*480的窗口，然后创建了模式为软件渲染的SDL渲染器，并设置渲染器的背景色为黑色;作为第一个项目，它简单到纯粹，当我们运行项目，会发现一个黑色的窗口一闪而过，这是因为我们这里在渲染了一次后就使用SDL_Quit()方法退出了，第一篇文章并不会有太复杂的内容，因为它的意义在于让我们对SDL游戏开发有个基本的认识和了解'
tags:
- SDL
- 游戏
- 图形
- 引擎
title: SDL游戏开发系列第一话：Hello SDL
---

&emsp;&emsp;各位读者朋友大家好，我是秦元培，欢迎大家关注我的博客，我的博客地址是[http://qinyuanpei.com](http://qinyuanpei.com)。从今天起博主将带领大家一起走进SDL游戏开发的世界，如果说此前的Unity3D游戏开发系列文章让大家感受到的是游戏引擎工具化开发的方便与快捷，那么这一次就让我们以SDL库为基础，通过了解游戏开发中的底层图形渲染、输入事件响应等内容来全面认识游戏引擎，博主为SDL游戏开发系列文章建立了专栏，大家可以通过[这里](http://blog.csdn.net/column/details/sdlgame.html)获取所有的系列文章，希望大家能够喜欢！好了，作为[SDL游戏开发系列](http://blog.csdn.net/column/details/sdlgame.html)的第一篇文章，按照技术性文章写作的国际惯例这将是一篇介绍SDL入门内容的文章，因此这篇文章叫做：Hello SDL。

<!--more-->

###什么是SDL
&emsp;&emsp;[SDL](http://www.libsdl.org/)（Simple DirectMedia Layer）是一套开放源代码的跨平台多媒体开发库，使用C语言写成。SDL提供了数种控制图像、声音、输出入的函数，让开发者只要用相同或是相似的代码就可以开发出跨多个平台如Linux、Windows、Mac OS X等的应用软件。目前SDL可用于游戏、模拟器、媒体播放器等多媒体应用领域的开发，SDL最为著名的案例是曾赢得Linux组游戏开发大奖的游戏[《文明：权利的召唤》](https://en.wikipedia.org/wiki/Civilization:_Call_to_Power)。或许大家对这个游戏会感到陌生吧，可是如果我提到一个Linux下经典单机游戏《仙剑奇侠传》的开源实现[SDLPal](http://sdlpal.codeplex.com/)相信大家就没有不知道的了吧？这款经典的单机游戏所以能够移植到Linux平台下就是因为使用SDL。好了，在对SDL有了大概的认识后，我们来看看SDL有哪些值得我们去研究的优良特性吧！
*  SDL提供了从图像、视频、音频、事件、线程、计时器的API，功能特别强大。
*  SDL具有良好的跨平台性能，支持Windows、Linux及Android和IOS，是开发跨平台多媒体应用的神兵利器。
*  SDL内置了OpenGL相关函数，使SDL开发3D应用成为可能，因此SDL是一个同时支持2D和3D开发的强力工具。
*  通过使用SDL_image、SDL_ttf、SDL_mixer、SDL_net等外部扩展库，可以轻松实现JPG、PNG、TIFF图像的加载使用，TrueType字体的使用，MP3文件的使用、网络相关的使用等。
*  SDL支持C++、C#、Java、 Lisp、Lua、Objective C、Pascal、Perl、 PHP、Python、Ruby等近20种编程语言。
*  SDL是GNU LGPL 2开源协议下发布的开源软件，该协议允许用户将SDL以动态链接库的形式免费地用于商业游戏软件的开发。

###SDL的下载、安装和配置
&emsp;&emsp;SDL开发相关的资源都可以从[http://www.libsdl.org/](http://www.libsdl.org/)来获取。目前SDL存在1.2和2.0两个版本，从效率上来说SDL2.0支持硬件加速效率较SDL1.2有了较好的提升，从稳定性上来讲SDL2.0尚处于发展阶段，因此可能其中的Bug较SDL1.2可能会多些。博主这里选择的SDL2.0，下面是相关的下载链接：
* SDL源代码——[下载](http://www.libsdl.org/release/SDL2-2.0.3.zip)
* SDL二进制库——[Win_x86](http://www.libsdl.org/release/SDL2-2.0.3-win32-x86.zip)、[Win_x64](http://www.libsdl.org/release/SDL2-2.0.3-win32-x64.zip)、[Mac](http://www.libsdl.org/release/SDL2-2.0.3.dmg)
* SDL开发包——[VC++](http://www.libsdl.org/release/SDL2-devel-2.0.3-VC.zip)、[GCC](http://www.libsdl.org/release/SDL2-devel-2.0.3-mingw.tar.gz)、[Mac](http://www.libsdl.org/release/SDL2-2.0.3.dmg)

&emsp;&emsp;博主选择的开发环境是Visual Studio2012，因此下载VC++的SDL开发包。我们将下载得到的SDL开发包解压到本地，可以发现SDL开发包中已经为我们准备好了相关的include文件夹和lib文件夹。其中include文件夹下存放的是SDL的各种头文件，lib文件夹下存放的是编译好的动态链接库（.dll）和依赖库（.lib），如果读者朋友有能力或是希望自行编译SDL源代码的，请先去编译源代码。这里我们为了节省时间，就直接使用编译好的文件了,请大家不要鄙视我啊，哈哈。好了，下面我们来以一个VC++项目为例来讲解SDL的配置：
*  1、使用Visual Studio创建一个空的VC++项目
*  2、右键单击项目【属性】打开项目属性页找到【配置属性】->【VC++目录】然后将包含目录和库目录分别定位到SDL开发包中的include目录和lib目（x86和x64视系统情况而定）
* 3、在【配置属性】->【链接器】->【输入】->【附加依赖项】中增加SDL2.lib和SDL2main.lib
* 4、将【配置属性】->【链接器】->【系统】->【子系统】设置为窗口 (/SUBSYSTEM:WINDOWS)
* 5、将SDL2.dll复制到项目的Debug目录中

###SDL游戏开发的基本流程
&emsp;&emsp;SDL游戏开发的一般流程是：
*  1、使用SDL_Init()方法对SDL进行初始化。其中该初始化方法的参数类型为int类型，可以从SDL_INIT_HAPTIC、SDL_INIT_AUDIO、SDL_INIT_VIDEO、SDL_INIT_TIMER、SDL_INIT_JOYSTICK、
SDL_INIT_EVERYTHING、SDL_INIT_NOPARACHUTE七个类型中选择，分别表示力反馈子系统、音频子系统、视频子系统、计时器子系统、摇杆子系统、全部和忽略致命信号。
*  2、在SDL初始化成功后使用SDL_CreateWindow()方法创建一个SDL窗口（SDL_Window）。在这里我们可以设置窗口的名称、对齐方式、窗口宽度和窗口高度。
*  3、在SDL窗口创建成功后使用SDL_CreateRenderer()方法创建一个SDL渲染器（SDL_Renderer）。其中SDL渲染器有SDL_RENDERER_SOFTWARE、SDL_RENDERER_ACCELERATED、SDL_RENDERER_PRESENTVSYNC、SDL_RENDERER_TARGETTEXTURE四种类型分别表示软件渲染、硬件加速、屏幕同步刷新渲染和支持渲染纹理。
*  4、使用SDL_RenderClear()方法清空SDL渲染器、使用SDL_RenderPresent()方法将渲染的结果显示出来

###工程示例
&emsp;&emsp;下面以一个简单的示例来向大家演示SDL游戏开发的一般流程：
```C++
/* 添加对SDL的引用*/
#include<SDL.h>

/* 声明SDL_Window */
SDL_Window *g_pWindow;

/* 声明SDL_Renderer */
SDL_Renderer *g_pRenderer;

/* 定义入口函数main */
int main(int argc,char *args[])
{
	/* SDL三部曲——1:初始化SDL */
	int sdlInit=SDL_Init(SDL_INIT_EVERYTHING);
	if(sdlInit>=0){
		/* 当SDL初始化完成后创建一个标题为"SDL Game Development——01" */
		/* 窗口对齐方式为居中对齐，窗口大小为640*480的窗口 */
		g_pWindow=SDL_CreateWindow("SDL Game Development——01",
			SDL_WINDOWPOS_CENTERED,SDL_WINDOWPOS_CENTERED,
			640,480,SDL_WINDOW_SHOWN);
		/* SDL三部曲——2:初始化SDL渲染 */
		if(g_pWindow!=0){
			g_pRenderer=SDL_CreateRenderer(g_pWindow,-1,0);
		}
	}

	/* SDL三部曲——3:绘制窗口 */
	SDL_SetRenderDrawColor(g_pRenderer,0,0,0,255);
	SDL_RenderClear(g_pRenderer);
	SDL_RenderPresent(g_pRenderer);
	
	SDL_Quit();
	return 0;
}
```
&emsp;&emsp;在以上代码中我们基本遵循了SDL游戏开发的一般流程，即首先对SDL进行初始化，当SDL初始化完成后，我们创建一个标题为"SDL学习示例1",窗口对齐方式为居中对齐，窗口大小为640*480的窗口，然后创建了模式为软件渲染的SDL渲染器，并设置渲染器的背景色为黑色。作为第一个项目，它简单到纯粹，当我们运行项目，会发现一个黑色的窗口一闪而过，这是因为我们这里在渲染了一次后就使用SDL_Quit()方法退出了，第一篇文章并不会有太复杂的内容，因为它的意义在于让我们对SDL游戏开发有个基本的认识和了解。关于SDL绘制图片、文字以及处理渲染循环等问题我们放到后面的文章中去讲，这篇文章的内容就是这样啦，谢谢大家！