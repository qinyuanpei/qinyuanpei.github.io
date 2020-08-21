---
abbrlink: 3789971938
categories:
- 游戏开发
date: 2015-07-27 08:48:59
description: SDL_RenderCopy(g_pRenderer,m_pTexture,m_pSrcRect,m_pTargetRect);SDL_RenderCopy(renderer,m_pTexture,m_pSrcRect,m_pTargetRect);SDL_RenderCopy(renderer,m_pTexture,m_pSrcRect,m_pTargetRect)
tags:
- SDL
- 游戏
- 游戏引擎
- 图形
title: SDL游戏开发系列第二话：基本图形的绘制
---

&emsp;&emsp;各位朋友，大家好，我是秦元培，欢迎大家关注我的博客，我的博客地址是：[http://qinyuanpei.com](http://qinyuanpei.com)。话题紧接上回，在上回我们讲到了SDL的下载、安装和配置并对SDL游戏有了初步的了解。我们知道游戏开发中最为基础的内容是图形的绘制，因此在我们学习SDL游戏开发的过程中我们同样要从最简单的图形绘制开始学习。在2D游戏开发中，精灵（Sprite）是一个基础而核心的内容，具体来讲精灵首先是一张2D图片，精灵的绘制从本质上是图片的绘制，所以这是一个基础的内容。因为精灵在2D游戏中承担着GameObject的重要角色，所以一个图形引擎对精灵的支持好坏会决定游戏设计的最终效果。今天这篇文章主要是通过使用SDL中的SDL_LoadBMP()、SDL_CreateTextureFromSurface()和SDL_RenderCopy()这三个方法来实现在SDL中基本图形的绘制，从整体上尚属较为简单的内容。可是从学习SDL游戏开发的角度来看，一切都值得我们深入地去研究。好了，这就开始吧！

<!--more-->
# 使用SDL_loadBMP加载位图
&emsp;&emsp;从SDL_LoadBMP()这个方法的名称，我们就可以看出这是一个读取BMP位图的方法。BMP是Windows操作系统中最早的图形格式，这种图形格式的容量较大，经常出现在Win32 API中。好了，言归正传，我们下面来看看整个绘制过程：
* 1、首先我们使用SDL_LoadBMP()方法来加载一张BMP位图：
	```C++
	//读取一张BMP位图
	SDL_Surface* m_pSurface=SDL_LoadBMP("background.bmp");
	```

* 2、接下来我们使用SDL_CreateTextureFromSurface()方法将SDL_Surface类型转化为SDL_Texture类型
	```C++
	//获取SDL纹理
	SDL_Texture* m_pTexture=SDL_CreateTextureFromSurface(g_pRenderer,m_pSurface);
	//释放m_pBackgroundSurface
	SDL_FreeSurface(m_pSurface);
	```
注意到在这里m_pSurface扮演了一个临时演员的角色。当我们获得了SDL纹理后，它的演员生涯便就此结束了，因此我们需要使用SDL_FreeSurface()方法来释放它的内存。

* 3、接下来是关键性的一个步骤，我们首先来关注SDL_RenderCopy()的方法定义:
	```	C++
	SDL_RenderCopy(SDL_Renderer * renderer,SDL_Texture * texture,const SDL_Rect * srcrect,const SDL_Rect * dstrect);
	```
如你所见，该方法的第一个参数和第二个参数我们已经相当熟悉了，即SDL渲染器和SDL纹理。这里想说的是第三个参数srcrect和第四个参数dstrect，这两个参数都是SDL_Rect类型，表示一个矩形范围，它有四个参数，即矩形左上角横坐标、矩形左上角纵坐标、矩形宽度、矩形高度。那么该如何理解这两个参数呢？

# SDL绘图中的精灵裁剪
&emsp;&emsp;这里我是这样理解的：第一个参数srcrect表示一个裁剪范围，即我们希望绘制图形的一个范围。例如我们现在有一张大小为640*480的图片，当我们使用(0,0,640,480)这样一个矩形对图片进行裁剪时，我们将获得整张图片；当我们使用(320,240,320,240)这个矩形对图片进行裁剪的时，我们将获得整张图片右下角1/4的部分。依次类推。相反地，dstrect则更加类似于一个画布（Canvas）的概念，即我们可以在一个多大的矩形范围内去绘制这样一张图片。

&emsp;&emsp;在这里，我们可以联想到2D图形绘制中的SpriteSheet，即“雪碧图”这个概念。在游戏开发中我们常常会使用TexturePacker这样的工具来将零散的小图打包成一张大图，因为这样可以提高游戏运行的效率，该工具最终导出的文件由.plist文件和合成的大图两部分组成，其中的.plist文件中记录了每张小图的位置信息，因此将这个概念引申到这里来，你就会理解这里提到的精灵裁剪，即srcrect这个矩形的作用是选择“大图”中的“小图”，而dstrect这个矩形的作用是决定将选出的“小图”绘制在一个多大的范围内。

&emsp;&emsp;一个经典的例子是我们现在一个有一张1124x676的图片，我们希望将其绘制到一个800x640的窗口作为背景图片，那么我们的代码可以这样写：
```C++
/* 添加对SDL的引用 */
#include<SDL.h>

/* 声明SDL窗口 */
SDL_Window *g_pWindow;

/* 声明SDL渲染器 */
SDL_Renderer *g_pRenderer;

/* 声明程序入口函数main */
int main(int agrc,char *args[])
{
	//初始化SDL
	int SDLInit=SDL_Init(SDL_INIT_EVERYTHING);
	if(SDLInit>=0)
	{
		//创建一个SDL窗口
		g_pWindow=SDL_CreateWindow("SDL Game Development-02",
			SDL_WINDOWPOS_CENTERED,SDL_WINDOWPOS_CENTERED,
			800,640,
			SDL_WINDOW_SHOWN);


		if(g_pWindow!=0){
			//创建SDL渲染器
			g_pRenderer=SDL_CreateRenderer(g_pWindow,-1,0);
		}	
	}

	//设置背景色
	SDL_SetRenderDrawColor(g_pRenderer,255,255,255,255);
	//渲染器清空
	SDL_RenderClear(g_pRenderer);

	//读取一张BMP位图
	SDL_Surface* m_pSurface=SDL_LoadBMP("background.bmp");
	//获取SDL纹理
	SDL_Texture* m_pTexture=SDL_CreateTextureFromSurface(g_pRenderer,m_pSurface);
	//释放m_pBackgroundSurface
	SDL_FreeSurface(m_pSurface);
	//构造SDL矩形
	SDL_Rect* m_pSrcRect=new SDL_Rect();
	m_pSrcRect->x=0;
	m_pSrcRect->y=0;
	m_pSrcRect->w=1124;
	m_pSrcRect->h=676;

	SDL_Rect* m_pTargetRect=new SDL_Rect();
	m_pTargetRect->x=0;
	m_pTargetRect->y=0;
	m_pTargetRect->w=800;
	m_pTargetRect->h=640;
	//绘制SDL纹理
	SDL_RenderCopy(g_pRenderer,m_pTexture,m_pSrcRect,m_pTargetRect);
	//显示绘制结果
	SDL_RenderPresent(g_pRenderer);

	//注意这里增加秒的延迟是为了看到渲染的结果
	//在实际的开发中不应该出现这样的代码因为在运行期间会导致窗口的卡顿
	//正确的做法是使用循环来处理这样一个渲染的过程
	SDL_Delay(5000);

    //退出
	SDL_Quit();

	return 0;
}
```
&emsp;&emsp;好了，现在运行这段代码，在运行这段代码前请确保完成了SDL的配置、在Debug目录中存放有一张名为background.bmp的位图文件以及SDL2.dll。如果你准确无误地完成以上注意事项，那么你将毫无意外地看到这样一个画面：

![SDL游戏开发](https://ww1.sinaimg.cn/large/None.jpg)

# 工程示例
&emsp;&emsp;现在让我们为这个示例增加点有趣的东西，我们知道在游戏设计中一般背景图片的大小是和游戏设计的窗口大小保持一致的，因为这样能够避免图片拉伸的问题。假定我们目前使用的精灵图片素材都是单个精灵的素材，那么我们可以设计这样一个方法来更加自由地绘制图片：
```C++
/* 实现绘制BMP位图的方法 */
void DrawBMP(SDL_Renderer* renderer,const char* fileName,
int positionX,int positionY,int textureWidth,int textureHeight)
{
	//读取一张BMP位图
	SDL_Surface* m_pSurface=SDL_LoadBMP(fileName);
	//获取SDL纹理
	SDL_Texture* m_pTexture=SDL_CreateTextureFromSurface(renderer,m_pSurface);
	//释放m_pBackgroundSurface
	SDL_FreeSurface(m_pSurface);
	//构造SDL矩形
	SDL_Rect* m_pSrcRect=new SDL_Rect();
	m_pSrcRect->x=0;
	m_pSrcRect->y=0;
	m_pSrcRect->w=textureWidth;
	m_pSrcRect->h=textureHeight;

	SDL_Rect* m_pTargetRect=new SDL_Rect();
	m_pTargetRect->x=positionX;
	m_pTargetRect->y=positionY;
	m_pTargetRect->w=textureWidth;
	m_pTargetRect->h=textureHeight;
	//绘制SDL纹理
	SDL_RenderCopy(renderer,m_pTexture,m_pSrcRect,m_pTargetRect);
```
&emsp;&emsp;在认为背景图片大小和窗口大小一致的前提下，我们修改下代码：
```C++
/* 添加对SDL的引用 */
#include<SDL.h>

/* 声明SDL窗口 */
SDL_Window *g_pWindow;

/* 声明SDL渲染器 */
SDL_Renderer *g_pRenderer;

/* 声明相关方法 */
void DrawBMP(SDL_Renderer* renderer,const char* fileName
,int positionX,int positionY,int textureWidth,int textureHeight);

/* 声明程序入口函数main */
int main(int agrc,char *args[])
{
	//初始化SDL
	int SDLInit=SDL_Init(SDL_INIT_EVERYTHING);
	if(SDLInit>=0)
	{
		//创建一个SDL窗口
		g_pWindow=SDL_CreateWindow("SDL Game Development-02",
			SDL_WINDOWPOS_CENTERED,SDL_WINDOWPOS_CENTERED,
			1124,676,
			SDL_WINDOW_SHOWN);


		if(g_pWindow!=0){
			//创建SDL渲染器
			g_pRenderer=SDL_CreateRenderer(g_pWindow,-1,0);
		}	
	}

	//设置背景色
	SDL_SetRenderDrawColor(g_pRenderer,255,255,255,255);
	//渲染器清空
	SDL_RenderClear(g_pRenderer);

	//在绘制背景图片时因为我们已通过画图软件获得了该图片的大小为1124*676
	//并且保证图片的大小和窗口大小一致因此我们可以直接构造一个(0,0,1024,676)的矩形来绘制
	DrawBMP(g_pRenderer,"background.bmp",0,0,1124,676);

	//接下来我们在窗口中心绘制一个大小为161*400的美少女
	DrawBMP(g_pRenderer,"girl.bmp",1124/2-161/2,676/2-400/2,161,400);

	//显示绘制结果
	SDL_RenderPresent(g_pRenderer);

	SDL_Delay(10000);
	//退出
	SDL_Quit();
	return 0;
}

/* 实现绘制BMP位图的方法 */
void DrawBMP(SDL_Renderer* renderer,const char* fileName,
int positionX,int positionY,int textureWidth,int textureHeight)
{
	//读取一张BMP位图
	SDL_Surface* m_pSurface=SDL_LoadBMP(fileName);
	//获取SDL纹理
	SDL_Texture* m_pTexture=SDL_CreateTextureFromSurface(renderer,m_pSurface);
	//释放m_pBackgroundSurface
	SDL_FreeSurface(m_pSurface);
	//构造SDL矩形
	SDL_Rect* m_pSrcRect=new SDL_Rect();
	m_pSrcRect->x=0;
	m_pSrcRect->y=0;
	m_pSrcRect->w=textureWidth;
	m_pSrcRect->h=textureHeight;

	SDL_Rect* m_pTargetRect=new SDL_Rect();
	m_pTargetRect->x=positionX;
	m_pTargetRect->y=positionY;
	m_pTargetRect->w=textureWidth;
	m_pTargetRect->h=textureHeight;
	//绘制SDL纹理
	SDL_RenderCopy(renderer,m_pTexture,m_pSrcRect,m_pTargetRect);
}
```
![SDL游戏开发](https://ww1.sinaimg.cn/large/4c36074fly1fz68jcze58j20vn0jvhdt.jpg)

&emsp;&emsp;现在我们再来运行程序，可以发现在背景图片上绘制了一个美少女，并且这个美少女处于窗口的中心。好了，通过今天的这部分内容我们可以实现在屏幕任意位置绘制图片，这里要注意一个前提，即图片表示的是单个精灵，在绘制过程中不存在裁切和缩放的问题。作为一个有节操的程序员，我们怎么能为了目前的这点成果而止步不前呢？注意到窗口标题上出现了未响应的字样，这是因为我们这里使用了SDL_Delay()这个方法的缘故，该方法会造成程序在运行过程中的卡顿。那么怎么解决这个问题呢？这里就需要涉及到SDL中的事件机制，可能这里大家会有点迷茫，可是我们暂时只需要用到SDL_PollEvent这个方法，这个方法可以帮助我们判断是否触发了某个事件，比如我们需要判断用户是否点击了窗口右上角的关闭按钮：
```
SDL_Event m_event;
if(SDL_PollEvent(&m_event))
{
	if(m_event.type==SDL_QUIT)
		SDL_Quit();
}
```
&emsp;&emsp;考虑到游戏渲染是一个循环的过程，因此我们只需要在工程示例中增加事件处理的相关代码，就可以解决因为使用SDL_Delay方法而带来的卡顿问题。好了，今天的内容暂时就研究到这里，我们注意到这里的图片都是静态的缺乏某种交互感，而且窗口中心绘制的美少女的有白色背景的，如果我们希望这里透明该怎么做呢？欲知后事如何，且听下回分解，敬请期待SDL游戏开发系列第三话：说说SDL中的扩展库。