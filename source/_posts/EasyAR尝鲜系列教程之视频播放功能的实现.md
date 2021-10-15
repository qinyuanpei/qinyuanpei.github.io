---
abbrlink: 316230277
categories:
- Unity3D
date: 2015-12-09 08:40:22
description: 这个增强ImageTarget是指在ImageTarget的基础上融入VideoPlayerBehaviour的功能，因为按照官方的示例来考虑，这两部分功能是独立的，博主希望让大家在制作识别图的时候完全忘记区别ImageTarget和VideoTarget，这样我们可以更为专注地制作识别图，因为视频组件就只是设置参数这一件事情，完全可以一次性搞定，所以我们首先来定义一个VideoTargetBaseBehaviour类，一起来看代码：;博主这里不太理解EasyAR为什么不采用MovieTexture或者Unity3D中针对视频播放提供的相关插件，因为VideoTarget本质上就是把三维模型换成了可以播放的视频而已，所以大家在前面文章的基础上创建一个ImageTarget然后再其下面放置一个附加了VideoPlayerBehaviour的的子物体就可以了;public
  void ShowObjects(Transform trans)
tags:
- 增强现实
- EasyAR
- Unity3D
- 教程
title: EasyAR尝鲜系列教程之视频播放功能的实现
---

&emsp;&emsp;各位朋友大家好，欢迎大家关注我的博客，我是秦元培，我的博客地址是[http://qinyuanpei.com](http://qinyuanpei.com)。到现在为止，我们对EasyAR中的ImageTarget基本上可以说是驾轻就熟了，因此我们这个系列教程可以说是接近尾声了。博主第一次接触AR这个概念是在大学时候读到一本讲解计算机图形视觉的书籍里，相对VR技术目前华而不实的市场现状，AR技术从实用性和成熟度都能得到较好的保证。可是大家都清楚这些技术背后都是建立在复杂而高深的图形学算法的基础上的，如果想学习AR技术请回归计算机图形学的本源，这就和学习游戏技术要追寻可编程渲染管线是一样的，所以这个系列完全是博主个人的兴趣使然，希望了解这个技术的可以进行更加深入的探索。这次我们来说说VideoTarget如何实现吧！

<!--more-->

# EasyAR中对视频的支持
&emsp;&emsp;目前EasyAR对视频的支持主要是通过VideoPlayerBehaviour这个类，这个类继承自一个基类VideoPlayerBaseBehaviour。我们可以将其理解为一个视频播放器组件，只要我们将这个组件添加到一个GameObject上，然后简单填写下参数就可以了。可是这个组件博主在32位操作系统下并没有看到实际的效果，虽然说都到了2015年了64位操作系统相对来说更为普及了，可是我觉得支持不支持32位操作系统更多的体现的是一家公司做产品的态度。既然暂时没有办法看到这里的具体效果，我们本着学习的态度对这个组件有所了解就是了。下面是这个组件的一张截图：

![VideoPlayerBehaviour组件截图](https://ww1.sinaimg.cn/large/None.jpg)

从图中我们可以看到这个组件相关参数的设置，这里选取的视频资源是StreamingAssets目录下的video.mp4这个文件，视频资源的Stroge同样支持App、Assets、Absolute这三种类型，和图片资源的Stroge是一样的，关于这三种类型的资源路径的问题，我这里不想再重复说了，这个看看文档就知道了。其次会涉及到视频播放方式和视频缩放的相关参数，这些基本上没什么理解上的难度，大家对照着文档反复尝试就知道各自的用途了。博主这里不太理解EasyAR为什么不采用MovieTexture或者Unity3D中针对视频播放提供的相关插件，因为VideoTarget本质上就是把三维模型换成了可以播放的视频而已，所以大家在前面文章的基础上创建一个ImageTarget然后再其下面放置一个附加了VideoPlayerBehaviour的的子物体就可以了。官方的示例项目中提供了两种方式的VideoTarget创建方式，即手动创建和动态创建。手动创建即我们这里提到的这种方式，而动态创建则是由程序在运行时期间创建。这两种方式本质上没有什么不同，需要注意的是VideoPlayerBehaviour有一个EnableAutoPlay的选项，该选项被选中后会启用自动播放，即当识别图被识别后自动播放视频、识别图未被识别则暂停播放视频。如果这个选项没有被选中，我们需要在ITargetEventHandle接口中动手来实现。

# 增强ImageTarget
&emsp;&emsp;这个增强ImageTarget是指在ImageTarget的基础上融入VideoPlayerBehaviour的功能，因为按照官方的示例来考虑，这两部分功能是独立的，博主希望让大家在制作识别图的时候完全忘记区别ImageTarget和VideoTarget，这样我们可以更为专注地制作识别图，因为视频组件就只是设置参数这一件事情，完全可以一次性搞定，所以我们首先来定义一个VideoTargetBaseBehaviour类，一起来看代码：

```csharp
using UnityEngine;
using System.Collections;
using EasyAR;

public class VideoTargetBaseBehaviour : ImageTargetBehaviour,ITargetEventHandler
{
    /// <summary>
    /// 视频播放模块
    /// </summary>
    private VideoPlayerBehaviour videoPlayer;

    /// <summary>
    /// 视频文件路径
    /// </summary>
    public string VideoPath;

    /// <summary>
    /// 是否自动播放视频
    /// </summary>
    public bool VideoEnableAutoPlay = true;

    /// <summary>
    /// 是否允许视频循环
    /// </summary>
    public bool VideoEnableLoop = true;

    /// <summary>
    /// 视频类型
    /// </summary>
    public VideoPlayer.VideoType VideoType = VideoPlayer.VideoType.TransparentSideBySide;

    /// <summary>
    /// 视频资源类型
    /// </summary>
    public StorageType VideoStorage = StorageType.Assets;


    /// <summary>
    /// 视频是否加载
    /// </summary>
    private bool isVideoLoaded;

    protected override void Start()
    {
        //在Start方法中加载视频、隐藏模型
        base.Start();
        LoadVideo();
        HideObjects(transform);
    }

    /// <summary>
    /// 加载视频
    /// </summary>
    private void LoadVideo()
    {
        //创建子物体VideoObject并为其添加视频组件
        GameObject VideoObject = new GameObject("VideoObject");
        videoPlayer = VideoObject.AddComponent<VideoPlayerBehaviour>();
        VideoObject.transform.SetParent(transform);
        VideoObject.transform.localPosition = Vector3.zero;
        VideoObject.transform.localRotation = Quaternion.identity;
        VideoObject.transform.localScale = Vector3.one;

        //设置视频组件相关参数
        videoPlayer.Storage = VideoStorage;
        videoPlayer.Path = VideoPath;
        videoPlayer.EnableAutoPlay = VideoEnableAutoPlay;
        videoPlayer.EnableLoop = VideoEnableLoop;
        videoPlayer.Type = VideoType;
        videoPlayer.VideoReadyEvent+=videoPlayer_VideoReadyEvent;
        videoPlayer.VideoReachEndEvent+=videoPlayer_VideoReachEndEvent;
        videoPlayer.VideoErrorEvent+=videoPlayer_VideoErrorEvent;
        videoPlayer.Open();

        videoPlayer.Play();
    }

    #region 视频组件相关事件定义

    public virtual void videoPlayer_VideoErrorEvent(object sender, System.EventArgs e)
    {
        
    }

    public virtual void videoPlayer_VideoReachEndEvent(object sender, System.EventArgs e)
    {
        
    }

    
    public virtual void videoPlayer_VideoReadyEvent(object sender, System.EventArgs e)
    {
        
    }

    #endregion

    /// <summary>
    /// 隐藏模型的方法
    /// </summary>
    /// <param name="trans">要隐藏的Transform</param>
    void HideObjects(Transform trans)
    {
        for (int i = 0; i < trans.childCount; ++i)
            HideObjects(trans.GetChild(i));
        if (transform != trans)
            gameObject.SetActive(false);
    }

    /// <summary>
    /// 显示模型的方法
    /// </summary>
    /// <param name="trans">要显示的Transform</param>
    public void ShowObjects(Transform trans)
    {
        for (int i = 0; i < trans.childCount; ++i)
            ShowObjects(trans.GetChild(i));
        if (transform != trans)
            gameObject.SetActive(true);
    }

    /// <summary>
    /// 实现ITargetEventHandler接口中的OnTargetFound方法
    /// </summary>
    /// <param name="target">识别目标</param>
    void ITargetEventHandler.OnTargetFound(Target target)
    {
        if (videoPlayer)
            videoPlayer.Play();
        ShowObjects(transform);
    }

    /// <summary>
    /// 实现ITargetEventHandler接口中的OnTargetLost方法
    /// </summary>
    /// <param name="target">识别目标</param>
    void ITargetEventHandler.OnTargetLost(Target target)
    {
        if (videoPlayer)
            videoPlayer.Pause();
        HideObjects(transform);
    }

    /// <summary>
    /// 实现ITargetEventHandler接口中的OnTargetLoad方法
    /// </summary>
    /// <param name="target">识别目标</param>
    void ITargetEventHandler.OnTargetLoad(Target target, bool status)
    {

    }

    /// <summary>
    /// 实现ITargetEventHandler接口中的OnTargetUnload方法
    /// </summary>
    /// <param name="target">识别目标</param>
    void ITargetEventHandler.OnTargetUnload(Target target, bool status)
    {

    }
}
```
在这段代码中博主采用了动态创建视频组件的方法，这样我们在制作VideoTarget的时候只需要按照以下步骤即可：
* 在Assets/EasyAR/Prefabs目录下找到EasyAR这个预制体，添加EasyARConfig组件，然后填写KEY。具体请参考系列教程第三篇[EasyAR尝鲜系列教程之ImageTarget千呼万唤始出来](http://qinyuanpei.com/2015/12/09/have-a-taste-of-easyar-03/)。
* 在Assets/EasyAR/Prefabs目录中找到ImageTarget这个预制体，然后使用VideoTargetBaseBehaviour组件替换默认的ImageTargetBehaviour组件。下面是博主这里的参数配置截图

![我制作的VideoTarget](https://ww1.sinaimg.cn/large/4c36074fly1fz68j6clw5j208t075jrn.jpg)

这里博主继续选择idback这张图片，这种方法是博主喜欢的方法，大家可以按照个人喜欢的方式来实现，总而言之万变不离其宗，只需要掌握它的原理就好了。在文章中已经提到过这个组件在32位操作系统下无法正常工作，所以这篇文章就不给大家展示相关的截图了，本文暂时先写到这里等有时间测试成功了再来更新这篇文章。如果像博主这样对Unity3D比较熟悉的朋友，可以考虑使用MovieTexture或者其它的方式来替代官方目前的这个方案，好了，这篇文章就是这样了，希望大家喜欢!