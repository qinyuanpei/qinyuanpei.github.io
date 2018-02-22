---
title: SDL游戏开发系列第三话：说说SDL中的扩展库
categories:
  - 游戏开发
tags:
  - SDL
  - 游戏
  - 图形
  - 引擎
abbrlink: 3765250300
date: 2016-02-10 11:28:53
---
&emsp;&emsp;各位朋友，大家好，我是秦元培，欢迎大家关注我的博客，我的博客地址是：[http://qinyuanpei.com](http://qinyuanpei.com)。最近因为在看一本讲解Cocos2d-JS游戏开发相关的书籍，所以就对游戏引擎原理方面的内容进行了学习和研究，我个人非常喜欢Cocos2d-X的以节点（Node）、层（Layer）来组织场景（Scene）的这种方式，而且因为这个引擎使用JavaScript进行开发，所以整体上来说API非常容易入手，对一个经常使用Unity3D这样一个基于组件（Component）的组织形式的人来说，这种设计显得新颖而有趣，而且基于事件驱动的编码同样让人感觉非常舒服，所以我就在学习这个引擎的同时开始重新拾起SDL来编写我自己的引擎：Simple2D。今天想接着这个系列来说说，在编写这套引擎过程中探索到的关于SDL这个库的更多的有趣的东西。

<!--more-->

#为什么需要扩展库？
&emsp;&emsp;为什么需要扩展库？这是一个耐人寻味的问题。扩展库存在的意义在于扩展，因为我们使用扩展库是为了使用更多的功能。在[SDL游戏开发系列第二话：基本图形的绘制](http://qinyuanpei.com/2015/07/25/sdl-game-development-02/)这篇文章中我们使用SDL_LoadBMP这个方法加载了一张位图，熟悉游戏开发的朋友应该都知道我们在游戏开发中一般不会使用.bmp这种格式，因为这种格式的文件体积通常比较大，我们用到游戏里的话无论从效率还是容量上都得不到比较好的优化，我们通常更喜欢用.png这种格式，一个最能称之为理由的理由就是它可以保留图片的Alpha通道信息，在这篇文章中我们提到过透明精灵的问题，所以这意味着SDL_LoadBMP这个方法无法满足我们考虑的这些要求，所以在这种情况下使用扩展库就能帮助我们解决这些问题，下面我们来说说SDL中和游戏相关的扩展库。

#SDL中游戏相关的扩展库
&emsp;&emsp;我个人喜欢SDL这个库的原因有两点，第一，它是一个非常底层的、跨平台的、使用起来非常简单的库，非常适合用来做游戏引擎应用层和图形学底层的一个粘合层；第二，SDL提供了大量的扩展库可以满足我们从图片、字体、音频到网络、计时器等等方面的需求，这些需求和游戏设计息息相关，所以使用这些扩展库能够避免我们从头开始造轮子。在SDL中和游戏相关的扩展库主要有：
* 图片：SDL_image可以支持JPG、PNG、TIFF等多种格式图像的读取和加载。
* 字体：SDL_ttf可以支持TrueType字体的读取和加载；SDL_rtf可以支持富文本格式从而使文字变得丰富多彩起来。
* 音频：SDL_mixer可以支持MIDI、MP3、FLAC、WAV等多种音频格式的加载和播放。
* 网络：SDL_net可以支持TCP/IP、HTTP两种网络协议。

#SDL扩展库工程示例
&emsp;&emsp;下面选取SDL_ttf、SDL_image、SDL_mixer这三个比较重要且常用的扩展库来讲解SDL扩展库的使用。无论使用任何SDL扩展库，通常需要注意下面三点：
* 右键单击项目【属性】打开项目属性页找到【配置属性】->【VC++目录】然后将包含目录和库目录分别定位到SDL开发包中的include目录和lib目（x86和x64视系统情况而定）。
* 在【配置属性】->【链接器】->【输入】->【附加依赖项】增加相应的库依赖。
* 在项目的【Debug】目录中拷贝相应的Runtime下所需要的全部文件如相关的.dll文件。
##SDL_ttf扩展库
&emsp;&emsp;SDL_ttf扩展库可以支持TrueType字体的读取和加载，因此我们可以利用这个扩展库来进行文字的绘制。绘制文字和绘制图片在原理上有所不同，前者由CPU来处理而后者由GPU来处理，反映在SDL中就是前者通过SDL_Surface来实现而后者通过SDL_Renderer来实现。这里可以顺便说点题外话，绘制图片从技术上来说交给CPU来处理并没有什么难度，比如我们在SDL中加载图片时首先获得的是一个SDL_Surface，这个时候直接使用它来绘制同样是可以的，可是因为SDL_Surface中保存的是像素信息，所以直接交给CPU来处理的话实际效率并不会太高，在SDL2.0以前的版本中绘制图片就是通过这种方式来处理的，这一点希望大家注意。我们将话题说回到SDL_ttf，通常来说使用SDL_ttf扩展库的一个基本流程是：
* 1、使用TTF_Init()方法完成对该扩展库的初始化。
* 2、使用TTF_OpenFont()方法来载入一个字体文件，该方法返回一个TTF_Font类型的指针。
* 3、使用TTF_SetFontStyle等Set系列的方法完成对字体相关属性的设置。
* 4、使用TTF_RenderText、TTF_RenderUNICODE、TTF_RenderUTF8这三类Render系列方法分别完成对英文编码、Unicode编码、UTF-8编码的文本的绘制，该方法返回一个SDL_Surface。
* 5、使用SDL_BlitSurface()方法完成对字体表面（SDL_Surface）的绘制，可以理解为将这个SDL_Surface和窗口对应SDL_Surface进行叠加，窗口对应的DL_Surface可以通过SDL_GetWindowSurface()方法来获取。
* 6、使用SDL_UpdateWindowSurface()来对窗口进行更新。
* 7、使用TTF_CloseFont()来结束对字体文件的引用、使用TTF_Quit()方法结束对该扩展库的使用。

### 中文字体相关问题
&emsp;&emsp;SDL对中文字体的支持可能并不是非常地友好，这个问题从本质上来讲是字符编码的问题，我相信有过Python开发经验的朋友一定对Python里的字符编码印象深刻，Unicode编码、UTF-8编码经常会让人在进行Python开发时感到无所适从。这里的问题和这里类似，我们要在SDL中使用本文，就需要将本地码转化为UTF-8编码，在官方的例子中可以找到一个LocalToUTF8的方法，这里给出代码，因为我对C++的确不熟悉，所以代码的理解就交给大家了，哈哈！
```
char* LocalToUTF8(char* text)
{
    static char* buff = NULL;
    if(buff){
        free(buff);
        buff = NULL;
    }

    wchar_t* unicode_buff;

    int nRetLen = MultiByteToWideChar(CP_ACP,0,text,-1,NULL,0);
    unicode_buff = (wchar_t*)malloc((nRetLen + 1) * sizeof(wchar_t));

    MultiByteToWideChar(CP_ACP,0,text,-1,unicode_buff,nRetLen);

    nRetLen = WideCharToMultiByte(CP_UTF8,0,unicode_buff,-1,NULL,0,NULL,NULL);

    buff = (char*)malloc(nRetLen + 1);

    WideCharToMultiByte(CP_UTF8,0,unicode_buff,-1,buff,nRetLen,NULL,NULL);
    
    free(unicode_buff);
    return buff;
}
```
### 工程示例
```
int main(int agrc,char *args[])
{
    //创建窗口
    SDL_Window* pWindow = SDL_CreateWindow(
        "SDL_TTF",
        SDL_WINDOWPOS_CENTERED,
        SDL_WINDOWPOS_CENTERED,
        800,480,
        SDL_WINDOW_SHOWN
    );

    //获取窗口表面
    SDL_Surface* pSurface = SDL_GetWindowSurface(pWindow);

    //初始化TTF
    TTF_Init();

    //加载楷体字体且字号为28
    TTF_Font* pFont= TTF_OpenFont("simkai.ttf",28);

    //定义前景色
    SDL_Color fg;
    fg.r=255;
    fg.b=255;
    fg.g=0;
    fg.a=255;

    //定义背景色
    SDL_Color bg;
    bg.r=0;
    bg.b=0;
    bg.g=0;
    bg.a=255;

    //定义矩形
    SDL_Rect destRect;

    //生成英文字符表面
    SDL_Surface* enSurface = TTF_RenderText(pFont,"abcdeABCDE",fg,bg);
    //计算该字符宽高
    TTF_SizeText(pFont,"abcdeABCDE",&destRect.w, &destRect.h);
    //绘制英文字符且其坐标为(200，200)
    destRect.x=200;
    destRect.y=200;
    SDL_BlitSurface(enSurface,NULL,pSurface,&destRect);

    //设置字体样式为加粗
    TTF_SetFontStyle(pFont,TTF_STYLE_BOLD);

    //生成中文字符表面
    SDL_Surface* cnSurface = TTF_RenderUTF8(pFont,LocalToUTF8("这是一个中文测试"),fg,bg);
    //计算该字符宽高
    TTF_SizeText(pFont,LocalToUTF8("这是一个中文测试"),&destRect.w, &destRect.h);
    //绘制中文字符且其坐标为(250，250)
    destRect.x=250;
    destRect.y=250;
    SDL_BlitSurface(cnSurface,NULL,pSurface,&destRect);

    //更新窗口
    SDL_UpdateWindowSurface(pWindow);

    //结束字体引用
    TTF_CloseFont(pFont);
    //关闭扩展库
    TTF_Quit();

    return 0;
}
```
##SDL_image扩展库
&emsp;&emsp;SDL_image这个扩展库使用起来相对简单，它和SDL_LoadBMP方法类似，提供了一个IMG_Load方法，该方法将返回一个SDL_Surface，所以使用该扩展库只需要将第一个步骤中的SDL_LoadBMP方法替换为IMG_Load就可以了，这样我们就可以使用.png、.jpeg等丰富类型的图片文件，既然可以使用.png格式的文件了，那么在前面我们提及的透明问题就可以解决了，因为图片绘制相关内容我们已经在[SDL游戏开发系列第二话：基本图形的绘制](http://localhost:4000/2015/07/27/sdl-game-development-02/)这篇文章中有所涉及，所以在这里就不再详细展开说了。
##SDL_mixer扩展库
&emsp;&emsp;SDL_mixer这个扩展库可以支持MIDI、MP3、FLAC、WAV等多种音频格式的加载和播放，在使用这个库的时候，我们对音频技术的相关底层技术不做深入探讨，我们以贴合游戏开发实际为主要目的，这里借鉴Cocos2d-JS中的AudioEngine类简单封装一个我们自己的AudioEngine，相关细节请大家自行查阅文档：
```
```