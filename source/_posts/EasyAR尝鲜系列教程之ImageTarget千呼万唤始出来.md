---
abbrlink: 3736599391
categories:
- Unity3D
date: 2015-12-09 08:39:54
description: 好了，在了解了 EasyAR 中常用的标准接口以后，我们下面来着手构建第一个 ImageTarget 项目，和我们第一次接触 EasyAR 不同，这次我们会编写些简单地代码，打开场景填入应用程序密钥(Key)然后运行它，这种方式在这里会显得略 LOW;EasyAR 中的识别图相对来说比较简单，因为我们只需要选择一张图片然后为其创建一个材质，再将这个材质附加到 ImageTarget 物体上就可以了;我确信这个类简单到彻底，它需要开发者在编辑器中填入 KEY 然后再 Awake 方法中完成对 EasyAR 的初始化，就是这样简单，我们这里将这个脚本附加到 EasyAR 这个物体上去，这样我们就完成了引擎的初始化工作，下面我们就可以专注于 AR 内容的产生了
tags:
- 增强现实
- EasyAR
- AR
- 教程
title: EasyAR 尝鲜系列教程之 ImageTarget 千呼万唤始出来
---

&emsp;&emsp;各位朋友大家好，欢迎大家关注我的博客，我是秦元培，我的博客地址是[http://qinyuanpei.com](http://qinyuanpei.com)。最近 EasyAR 终于迎来了一次重大的版本更新：v1.10，真可谓是“千呼万唤始出来”啊，所以在官方文档和示例项目基本完善的情况下，博主决定将 EasyAR 尝鲜系列教程继续下去。本次教程主要以官方新发布的 Unity 示例项目为基础来进行讲解，关注 Androis/iOS 原生应用开发的朋友请自行针对官方示例项目进行研究。好了，今天主要的内容是通过 EasyAR SDK 来自行构建一个 ImageTarget 的实例，采用 Unity3D 4.6.4 版本进行开发。

<!--more-->

# EasyAR SDK 的结构
&emsp;&emsp;将 EasyAR SDK 导入 Unity3D 后会在项目的 Assets 根目录下生成 EasyAR 和 Plugins 两个文件夹。其中 EasyAR 文件夹中提供了开发 AR 应用相关的标准接口、材质、Shader 和 Prefab，Plugins 文件夹中提供了针对各个平台的插件。好了，下面我们来介绍 EasyAR SDK 中提供的标准接口：
* ARBuilder: 该类提供了 EasyAR 初始化的相关方法，我们在编写 EasyAR 配置类的时候会用到这个类，这是一个可以直接使用的类。
* ImageTargetBehaviour: 该类是一个抽象类，我们需要对其进行 override，可以将这个类理解为 ImageTarget 生命周期相关的一个类，在实际使用中需要配合 ITargetEventHandle 这个接口来使用。
* VideoPlayerBaseBehaviour: 该类是一个组件，我们可以使用这个组件来播放视频。其原理和 ImageTarget 类似，所不同的地方是 ImageTarget 在识别成功后会显示一个模型，而这里则是使用一个隐藏的物体来播放视频，VideoPlayerBaseBehaviour 负责控制视频的播放、暂停等工作。
* ITargetEventHandle: 这是一个接口，通过该接口可以捕捉到识别过程中的 OnTargetFound、OnTargetLost、OnTargetLoad 和 OnTargetUnload 四个事件，对于一个基本的 AR 应用来说，我们通常需要关注的是 OnTargetFound、OnTargetLost 这两个方法。

# 构建第一个 ImageTarget 项目
&emsp;&emsp;好了，在了解了 EasyAR 中常用的标准接口以后，我们下面来着手构建第一个 ImageTarget 项目，和我们第一次接触 EasyAR 不同，这次我们会编写些简单地代码，打开场景填入应用程序密钥(Key)然后运行它，这种方式在这里会显得略 LOW。
##EasyAR 的初始化
&emsp;&emsp;首先我们在 Assets/EasyAR/Prefabs 目录下找到 EasyAR 这个预制体，然后将其拖放到场景中，这样我们就创建了基本的 EasyAR 应用场景，接下来我们要做的事情就是在这个场景中填入各种各样的识别物。为了让 EasyAR 正常工作，我们首先要编写一个初始化 EasyAR 的脚本：

```csharp
using UnityEngine;
using System.Collections;
using EasyAR;

public class EasyARConfig : MonoBehaviour 
{
    /// <summary>
    /// 应用程序密钥
    /// </summary>
    [TextArea(1,10)]
    public string Key;

    public void Awake()
    {
        //检查KEY是否存在
        if(string.IsNullOrEmpty(Key))
            Debug.Log("请先输入应用程序密钥");

        //初始化EasyAR
        ARBuilder.Instance.InitializeEasyAR(Key);
        ARBuilder.Instance.EasyBuild();
    }
    
}
```
我确信这个类简单到彻底，它需要开发者在编辑器中填入 KEY 然后再 Awake 方法中完成对 EasyAR 的初始化，就是这样简单，我们这里将这个脚本附加到 EasyAR 这个物体上去，这样我们就完成了引擎的初始化工作，下面我们就可以专注于 AR 内容的产生了。

## 制作一个 ImageTarget
&emsp;&emsp;接下来我们在 Assets/EasyAR/Prefabs 目录中找到 ImageTarget 这个预制体，将其拖放到场景中，确保它在摄像机的视野范围内。我们注意到默认情况下它附加了一个 ImageTargetBehaviour 脚本，我们在前面已经说过，这个类是一个抽象类，抽象类通常是不做任何事情的，因此我们需要继承这个类来编写一个具体类，我们将这个具体类命名为 CustomImageTargetBehaviour。下面给出它的代码实现：

```csharp
using UnityEngine;
using System.Collections;
using EasyAR;

public class CustomImageTargetBehaviour :ImageTargetBehaviour,ITargetEventHandler
{

    protected override void Start()
    {
        //在Start方法中隐藏模型
        base.Start();
        HideObjects(transform);
    }

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
    void ShowObjects(Transform trans)
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
        ShowObjects(transform);
    }

    /// <summary>
    /// 实现ITargetEventHandler接口中的OnTargetLost方法
    /// </summary>
    /// <param name="target">识别目标</param>
    void ITargetEventHandler.OnTargetLost(Target target)
    {
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
可以注意到在这个类中我们主要做了两件事情：第一，定义了隐藏和显示识别模型的方法 HideObjects 和 ShowObjects，其作用是在没有识别到 Target 的时候隐藏物体，在识别到 Target 的时候显示物体；第二，实现了 ITargetEventHandler 接口并在 OnTargetFound 和 OnTargetLost 两个方法中实现我们第一步希望达到的目的。至此，我们完成了一个基本的 AR 识别组件，我们下面所有的 AR 识别物体都是通过这个组件来工作的，所以我们从场景中的 ImageTarget 物体上移除默认的 ImageTargetBehaviour 脚本然后为其添加我们定义的 CustomImageTargetBehaviour 脚本。

&emsp;&emsp;编写完脚本以后我们就可以着手制作识别图和 Marker 了，EasyAR 最让人喜欢的一点就是你可以按照自己的意愿来制作识别图和 Marker。虽然 Vuforia 在识别效果上比 EasyAR 更好点，可是对程序员来说选择一个透明的产品方案比面对着黑箱子进行调试要明智得多。EasyAR 中的识别图相对来说比较简单，因为我们只需要选择一张图片然后为其创建一个材质，再将这个材质附加到 ImageTarget 物体上就可以了。此外还会涉及到某些参数的设置，我们下面会提到。好了，我们继续选择官方示例中的 idback 这张图片来作为我们的识别图，因为身份证每个人都有可以随时用来进行测试，而一般的图片则需要打印出来制成硬质卡片来使用。我们在 Assets 目录中创建一个 StreamingAssets 目录，将官方示例中 targets.json 和 idbcak.jpg 两个文件拷贝过来。创建材质就不再说了，这是 Unity3D 中非常非常基础的内容。我们将创建好的材质附加到 ImageTarget 物体上以后，可能在场景中并不会看到对应的识别图，这是因为我们没有为其配置参数。具体的参数配置如下图：

![ImageTarget参数配置](https://ww1.sinaimg.cn/large/None.jpg)

具体这些参数的定义请大家自己去看文档，因为我这里说得再明白如果大家不看等于我没有说。好了，下面我们来创建 Marker，这个就比较简单了，我们直接找一个模型缩放到合适的大小然后拖拽到 ImageTarget 这个物体下面就可以了。如图是博主参照官方示例制作的两个识别图及其 Marker：

![两个ImageTarget及其对应Maker](https://ww1.sinaimg.cn/large/4c36074fly1fz68j2ap8rj20fa09wacy.jpg)

## 走向成功的关键步骤
1、在 EasyAR 物体的 EasyARConfig 组件中填入从官网申请的 KEY。
2、在 BuildSetting 中填写 KEY 对应的 AppID。
3、安装 SDK 中附带的 VC++2015 运行库。
4、如要编译 Android 版本，请确保安装 Java 环境和 Android SDK
更多的问题请自行到官方文档中对照寻找解决办法。

# 截图展示

![截图展示](.)