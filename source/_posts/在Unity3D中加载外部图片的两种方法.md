---
abbrlink: 821259985
categories:
- Unity3D
date: 2015-10-08 15:03:01
description: 现在我们运行程序可以发现两种方式均可以让图片加载进来，为了对比两种方式在执行效率上的高低，我们在脚本中加入了相关代码，通过对比可以发现使用 IO 方式加载一张 227k 的图片需要的时间为 0s，而使用 WWW 方式加载需要 0.0185s，因此传统的 IO 方式具有更高的效率，建议大家在遇到这类问题时尽可能地使用这种方式;经过博主的研究发现，这种方式加载外部图片相对于使用 WWW 加载外部图片效率更高，所以如果大家遇到类似的需求，博主个人推荐大家使用这种方式进行加载;///
  以 WWW 方式进行加载
tags:
- Unity3D
- 游戏开发
- uGUI
title: 在 Unity3D 中加载外部图片的两种方法
---

&emsp;&emsp;各位朋友大家好，我是秦元培，欢迎大家关注我的博客。最近在做项目的过程中遇到这样的一个需求：玩家可以在游戏过程中进行实时存档，在存档过程中会保存当前游戏进度，同时会截取当前游戏画面并加载到游戏存档界面中。当下一次进入游戏的时候，将读取本地存档图片并加载到游戏界面中。这在单机游戏中是特别常见的一种功能，这里主要有两个关键点。首先是截取游戏画面，这个问题大家可以在[《Unity3D 游戏开发之截屏保存精彩瞬间》](http://blog.csdn.net/qinyuanpei/article/details/39185195)这篇文章中找到答案。其次是从本地加载图片，因为这里要保证可读可写，因此传统的 Resources.Load()方式和 AssetBundle 方式均无法实现这样的功能。那么怎样从外部加载图片到游戏中，这就是我们今天要讨论的内容啦。好了，这里介绍两种方法来实现这一目的。


<!--more-->

# 喜闻乐见的 WWW 方式
&emsp;&emsp;喜闻乐见的 WWW 方式之所以喜闻乐见，这是因为这是我们最为熟悉的一种，我们都知道通过 WWW 可以从网络上加载文本、图片、音频等形式的内容，那么通过 WWW 能否加载本地外部（相对于应用程序）资源呢？答案是肯定的，这是因为 WWW 可以支持 http 和 file 两种协议。我们通常接触到的 WWW 默认都是指 http 协议，现在我们来说说 file 协议，该协议可以用来访问本地资源（绝对路径）。例如我们希望加载文件 D:\TestFile\pic001.png 这个文件，则此时对应的 C#脚本为：

```plain
//请求WWW
WWW www = new WWW("file://D:\\TestFile\\pic001.png);
yield return www;        
if(www != null && string.IsNullOrEmpty(www.error))
{
    //获取Texture
    Texture texture=www.texture;   
    //更多操作...       
}
```
注意到这里出现了 yield return 结构，这表示这里使用到了协程，因此我们需要付出的代价就是需要在项目中使用 StartCoroutine 等协程相关的方法来调用这些协程。虽然在 Unity3D 中使用协程是件简单的事情，可是如果我们随随便便地使用协程而不注意去维护这些协程，那么这些让我们引以为傲的简单代码可能就会变成我们痛苦不堪的无尽深渊。

# 亘古不变的传统 IO 方式
&emsp;&emsp;好了，下面我们隆重推出亘古不变的传统 IO 方式，这种方式相信大家都没有接触过，所以这里将这种方法和大家分享。既然是传统的 IO 方式，那么无非就是各种 IO 流的处理啦。好，我们一起来看下面这段代码：

```plain
//创建文件读取流
FileStream fileStream = new FileStream(screen, FileMode.Open, FileAccess.Read);
fileStream.Seek(0, SeekOrigin.Begin);
//创建文件长度缓冲区
byte[] bytes = new byte[fileStream.Length]; 
//读取文件
fileStream.Read(bytes, 0, (int)fileStream.Length);
//释放文件读取流
fileStream.Close();
fileStream.Dispose();
fileStream = null;

//创建Texture
int width=800;
int height=640;
Texture2D texture = new Texture2D(width, height);
texture.LoadImage(bytes);
```

可以看到在使用这种方式读取图片文件的时候主要是将图片文件转化为 byte[]数组，再利用 Texture2D 的 LoadImage 方法转化为 Unity3D 中的 Texture2D。这种方法需要在创建过程中传入图片的大小，在这里我们创建了一张 800X640 的图片。经过博主的研究发现，这种方式加载外部图片相对于使用 WWW 加载外部图片效率更高，所以如果大家遇到类似的需求，博主个人推荐大家使用这种方式进行加载。

&emsp;&emsp;到目前为止我们解决了如何从外部加载图片到 Unity3D 中，现在我们回到最开始的问题，我们从外部读取到这些图片以后需要将它们加载到游戏界面中。比如当我们使用 UGUI 的时候，UGUI 中的 Image 控件需要一个 Sprite 来作为它的填充内容，那么此时我们就需要将 Texture 转化为 Sprite.号了，下面我们给出一个简单的例子：

```plain
using UnityEngine;
using System.Collections;
using UnityEngine.UI;
using System.IO;

public class TestLoading : MonoBehaviour 
{
    /// <summary>
    /// Image控件
    /// </summary>
    private Image image;

	void Start () 
    {
        image = this.transform.Find("Image").GetComponent<Image>();

        //为不同的按钮绑定不同的事件
        this.transform.Find("LoadByWWW").GetComponent<Button>().onClick.AddListener
        (
           delegate(){LoadByWWW();}
        );

        this.transform.Find("LoadByIO").GetComponent<Button>().onClick.AddListener
        (
          delegate(){LoadByIO();}
        );
	}

    /// <summary>
    /// 以IO方式进行加载
    /// </summary>
    private void LoadByIO()
    {
        double startTime = (double)Time.time;
        //创建文件读取流
        FileStream fileStream = new FileStream("D:\\test.jpg", FileMode.Open, FileAccess.Read);
        fileStream.Seek(0, SeekOrigin.Begin);
        //创建文件长度缓冲区
        byte[] bytes = new byte[fileStream.Length];
        //读取文件
        fileStream.Read(bytes, 0, (int)fileStream.Length);
        //释放文件读取流
        fileStream.Close();
        fileStream.Dispose();
        fileStream = null;

        //创建Texture
        int width = 300;
        int height = 372;
        Texture2D texture = new Texture2D(width, height);
        texture.LoadImage(bytes);

        //创建Sprite
        Sprite sprite = Sprite.Create(texture, new Rect(0, 0, texture.width, texture.height), new Vector2(0.5f, 0.5f));
        image.sprite = sprite;

        startTime=(double)Time.time-startTime;
        Debug.Log("IO加载用时:" + startTime);
    }

    /// <summary>
    /// 以WWW方式进行加载
    /// </summary>
    private void LoadByWWW()
    {
        StartCoroutine(Load());
    }

    IEnumerator Load()
    {
        double startTime = (double)Time.time;
        //请求WWW
        WWW www = new WWW("file://D:\\test.jpg");
        yield return www;        
        if(www != null && string.IsNullOrEmpty(www.error))
        {
            //获取Texture
            Texture2D texture=www.texture;

            //创建Sprite
            Sprite sprite = Sprite.Create(texture, new Rect(0, 0, texture.width, texture.height), new Vector2(0.5f, 0.5f));
            image.sprite = sprite;

            startTime = (double)Time.time - startTime;
            Debug.Log("WWW加载用时:" + startTime);
        }
    }
}

```
&emsp;&emsp;现在我们运行程序可以发现两种方式均可以让图片加载进来，为了对比两种方式在执行效率上的高低，我们在脚本中加入了相关代码，通过对比可以发现使用 IO 方式加载一张 227k 的图片需要的时间为 0s，而使用 WWW 方式加载需要 0.0185s，因此传统的 IO 方式具有更高的效率，建议大家在遇到这类问题时尽可能地使用这种方式。好了，今天的内容就是这样啦，欢迎大家在我的博客中留言、欢迎大家关注和支持我的博客，谢谢大家！

2016 年 6 月 12 日更新：
&emsp;&emsp;针对有朋友指出 WWW 加载和传统 IO 加载方式在效率上的差异，我们这里重新做一个效率测试。