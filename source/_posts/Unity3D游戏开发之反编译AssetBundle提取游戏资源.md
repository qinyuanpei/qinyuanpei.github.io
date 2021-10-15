---
abbrlink: 2799263488
categories:
- 游戏开发
date: 2015-04-02 20:37:52
description: 具体来说呢，AssetBundle 在 Unity3D 中是一种用于资源打包盒资源动态加载的解决方法，比如我们平时玩的单机游戏容量一般都比较大，这是因为制作人员在制作游戏的时候将所有的项目资源都整合到了一起;第五个参数是平台的选择，因为 Unity3D 是一个跨平台的游戏引擎，而各个平台现在的情况又不尽相同，因此现在 Unity3D 采取的方案是各个平台只能使用自己平台对应的 AssetBundle，这一点希望大家在使用的时候注意啊;这是一个简单的导出 AssetBundle 资源包的方法，它有两个参数，第一个参数表示是一个枚举类型，定义为 ExportType，取 Single 时表示打包一个特定的激活物体，比如说一个模型、一个场景等等
tags:
- Unity3D
- 游戏开发
- AssetBundle
- 资源提取
title: Unity3D 游戏开发之反编译 AssetBundle 提取游戏资源
---

&emsp;&emsp;各位朋友，大家好，欢迎大家关注我的博客，我是秦元培，我的博客地址是[http://www.qinyuanpei.com](http://www.qinyuanpei.com)。今天我们来说说通过反编译 Unity3D 的 AssetBundle 来提取游戏资源，博主写这篇文章的目的并非是要教大家如何去破解一款基于 Unity3D 引擎开发的游戏，而是想通过今天这篇文章来告诉大家如何在开发 Unity3D 游戏的过程中保护自己的游戏资源。

<!--more-->

# 漫话 Unity3D 的 AssetBundle
&emsp;&emsp;对于 AssetBundle，其实博主是在以前的文章中是有提到的。不知道大家还记不记得，博主曾经在写游戏开发和 Lua 的不解之缘这个系列文章的时候，提到并且使用过 AssetBundle 这种技术。具体来说呢，AssetBundle 在 Unity3D 中是一种用于资源打包盒资源动态加载的解决方法，比如我们平时玩的单机游戏容量一般都比较大，这是因为制作人员在制作游戏的时候将所有的项目资源都整合到了一起。可是如果我们用 AssetBundle 来做这个游戏的话，我们就可以只在发布的游戏中提供支持游戏功能的核心部分，而将游戏当中的场景、模型等资源以 AssetBundle 的形式打包然后放到服务器上，这样当游戏客户端处于联网的时候就可以从服务器上下载这些资源，从而实现游戏资源的动态加载，由此可见 AssetBundle 可以帮助我们减少游戏的容量。如果是在需要安装包的场合下，那么游戏包容量的大小无疑会为游戏加些印象分。

![为什么这幅图总让我想起仙剑四里四人在即墨那晚的时光呢？](https://ww1.sinaimg.cn/large/4c36074fly1fz05d2nsnpj20rs0fn457.jpg)

&emsp;&emsp;比如最近《轩辕剑 6 外传穹之扉》这部单机游戏发布了，从各大游戏网站的评测到和一样我喜欢单机游戏的各位朋友们的亲身体验，大家一致的认为这部游戏整体表现还不错，应该考虑玩一玩。这样难免让博主有些心动，可是看到 17 个 G 的游戏容量时还是犹豫了下。DOMO 小组从《轩辕剑 6》就开始使用 Unity3D 引擎，在经历了第一部游戏的失败后，或许此次 DOMO 小组会将游戏优化的比较好吧。这里如果有喜欢单机游戏的朋友不妨去玩玩看，毕竟我们学习游戏开发的初衷就是做出好游戏，如果不热爱游戏又怎么能做出好游戏呢？好了，扯得有点远了，这里我们注意到一个重要的因素就是游戏容量，如果 DOMO 采用 AeestBundle 的话，游戏的容量肯定会减少很多。可是这样一来，它就不是单机游戏了嘛，对吧！

&emsp;&emsp;在 Unity3D 中 AssetBundle 是专业版中的一个功能，在免费版的 Unity3D 中是无法使用这个功能的，不知道在 Unity5 中这个功能是不是划分到了个人版中。好了，下面我们来看看如何使用 AssetBundle。我们主要从使用 AssetBundle 打包和加载 AssetBundle 这两个方面来说：

## 使用 Assetbundle 打包
&emsp;&emsp;使用 AssetBundle 打包主要通过 BuildPipeline.BuildAssetBundle()这个方法来实现，该方法原型为：
```C#
bool BuildAssetBundle (Object mainAsset,Object[] assets,string pathName, BuildAssetBundleOptions 
optionsBuildAssetBundleOptions.CollectDependencies | BuildAssetBundleOptions.CompleteAssets,
BuildTarget targetPlatform= BuildTarget.WebPlayer)  
```
&emsp;&emsp;在这个方法中，第一个参数是一个 Object 类型，表示一个激活的物体;第二个参数是一个 Object[]类型，表示所有选中的物体;第三个参数是一个 string 类型，表示要导出的资源包的路径，资源包的扩展名可以是 assetbundle 或者 unity3d;第四个参数表示的是打包选项，默认是完全打包和依赖打包。这里重点解释下这两个概念，完全打包是指所有资源都参与打包，比如说一个模型带有贴图和动画，那么打包模型的时候贴图和动画都会被作为资源打包。而依赖打包是相对于 Prefab 来说的，比如说 PrefabA 中引用了 PrefabB 这个对象，那么打包的时候这两个对象都会被打包，并且它们之间的这种依赖关系会在打包后继续保持；第五个参数是平台的选择，因为 Unity3D 是一个跨平台的游戏引擎，而各个平台现在的情况又不尽相同，因此现在 Unity3D 采取的方案是各个平台只能使用自己平台对应的 AssetBundle，这一点希望大家在使用的时候注意啊。好了，现在我们来看一个简单的例子：
```C#
    /// <summary>
    /// 输出AssetBundle
    /// </summary>
    /// <param name="type">平台类型</param>
    static void ExportToAssetBundle(ExportType type,BuildTarget target)
    {
        //获取存储路径
        string savePath=EditorUtility.SaveFilePanel("输出为AssetBundle","","New Resource","unity3d");
        if(savePath==string.Empty) return;
        //获取选中的对象
        Object[] selection=Selection.GetFiltered(typeof(Object),SelectionMode.DeepAssets);
        if(selection.Length==0) return;
        //打包
        if(type==ExportType.All){
          BuildPipeline.BuildAssetBundle(null,selection,savePath,BuildAssetBundleOptions.CollectDependencies,target);
        }else{
            BuildPipeline.BuildAssetBundle(obj,null,savePath,BuildAssetBundleOptions.CollectDependencies,target);
        }
    }
```
&emsp;&emsp;这是一个简单的导出 AssetBundle 资源包的方法，它有两个参数，第一个参数表示是一个枚举类型，定义为 ExportType，取 Single 时表示打包一个特定的激活物体，比如说一个模型、一个场景等等;取 All 时表示打包所有选中的物体，比如一个场景。第二个参数表示打包的平台，这个不用多说了。因为博主的免费版的 Unity3D 不支持 AssetBundle，所以这里没法给大家演示了，具体效果请自行测试，有问题的话给博主留言就是了。

## 加载 AssetBundle
&emsp;&emsp;加载 AssetBundle 是一个从网络中下载资源的过程，因此需要使用 Unity3D 的 WWW 功能，这是一个简单的网络协议的封装，可以像浏览器一样访问某个 URL 地址或者是本地地址，访问 WEB 地址需要使用 HTTP 协议，访问本地地址需要使用 File 协议。我们来看一个具体的例子：
```C#
    /// <summary>
    /// 加载一个unity3d格式的文件
    /// WEB地址——http://server.com/xxx.unity3d
    /// 本地地址——file://.unity3d文件的绝对路径
    /// </summary>
    IEnumerator LoadUnity3DFile(string url)
    {
        WWW www=new WWW(url);
        yield return www;
        if(www.error!=null){
            Debug.Log(www.error);
        }else{
           AssetBundle bundle=www.assetBundle;
          Instantiate(bundle.mainAsset,Vector3.zero,Quaternion.identity);
        }
    }
```
&emsp;&emsp;在这里我们直接使用 bundle.assetBundle 获取了全部的资源，如果只需要获取资源中的一部分，则只需要通过 bundle.Load()方法就可以了，这里需要传入资源的名称。当我们使用完资源后可以通过 bundle.Unload()方法来卸载资源，达到释放内存的目的。

#从反编译《新仙剑 OL》看 AssetBundle 打包
&emsp;&emsp;好了，下面我们以《新仙剑 OL》这款游戏的 AssetBundle 的反编译来探索下在使用 AssetBundle 打包应该注意哪些问题。《新仙剑 OL》这款游戏呢，是采用 Unity3D 引擎开发的一款横跨客户端游戏和网页游戏的网络游戏，游戏以《仙剑奇侠传》初代游戏剧情为主，玩家将第三人称视角再次跟随主人公展开一段荡气回肠的感人故事。这款游戏总体来说还不错吧，因为毕竟是网游，我们不能用单机游戏的视角去评价，具体的原因大家都是知道的。

&emsp;&emsp;好了，为什么我们要选择这款游戏呢？
* 第一，这款游戏的客户端只有 30 余 M,体积小适合拿来研究(这就是 AssetBundle 的好处啊)* 第二，博主是一位仙剑玩家，一直希望有一天《仙剑奇侠传 1》能够用 3D 技术重现，这个游戏满足了博主的好奇心
* 第三，网络上已经有朋友对这个游戏的打包进行了研究，这里感谢网友朋友提供部分.unity3d 文件及相关文件。

&emsp;&emsp;我们选择的解包工具是一款叫做[disunity](https://github.com/ata4/disunity)的命令行工具，经过博主的尝试，这个工具真心强悍啊，可以解开.unity3d 文件和.assets 文件，可以拿到的数据形式有贴图、声音、模型等。具体的情况大家可以在稍后看到。

&emsp;&emsp;首先我们找到《新仙剑 OL》的安装目录，然后我们就能发现一个叫做 assetbundles 的文件夹，这是怕大家不知道吗？这太明显了吧！我们打开文件夹会发现 Charachers、NPC、Scene 等等文件夹，继续往下找我们发现了好多的.unity3d 文件，不过这些文件都是以.unity3d 然后跟些随机字符串的形式存在的。根据网友朋友们的提示，这些文件就是.unity3d 文件，不过游戏制作组为了干扰我们故意接了下随机字符在后面(呵呵，还有比这更弱的加密方式吗？)。博主看到这里的第一感觉就是想先用加载 AssetBundle 的方式来看看能不能将这些 AssetBundle 读取出来，因此果断改了文件扩展名，然后开始在 Unity3D 中读取，结果程序报错看来是我们想的简单了啊。没办法的办法，强行解包吧！在命令行中输入：
```Sheel
disunity extract C:\Users\Robin\Desktop\s049.unity3d
```
&emsp;&emsp;接下来程序会在桌面上生成一个上 s049 的文件夹，打开文件夹一看，尼玛，竟然直接拿到了模型的网格数据(.obj)和贴图数据(.dds)以及相关的 Shader。这让我突然间有点不能接受啊，马上打开 Blender 将网格数据导入，结果童年的林月如就出现在了我们的面前：

![林月如灰模](https://ww1.sinaimg.cn/large/4c36074fly1fz01ykrzepj20l70dpwfe.jpg)

&emsp;&emsp;因为博主不会在 Blender 中给模型贴图，所以我们到 Unity3D 中完成贴图，首先需要将模型导出为 FBX 格式。好了，将模型导入 Unity3D 后，将贴图赋给模型，童年的林月如就闪亮登场了，哈哈！

![林月如贴图效果](https://ww1.sinaimg.cn/large/4c36074fly1fyzcuaxphej20k10h70vr.jpg)

&emsp;&emsp;好了，再来一张，不过这张没有贴图，需要大家自己来辨别这是谁啊，哈哈！

![柳梦璃灰模](https://ww1.sinaimg.cn/large/4c36074fly1fyzcu53oytj20hj0fdmyd.jpg)

&emsp;&emsp;通过 disunity 这个工具我们还能获取更多的资源，剩下的内容就由大家自己去探索吧。通过这部分的研究，我们可以总结出以下观点，希望大家在使用 AsssetBundle 这项技术时注意：
* 尽量在一个 AssetBundle 中打包多个资源，这样做的好处是别人没法通过加载 AssetBundle 拿到你做好的 Prefab。
* 尽量将一个预制件分割成不同的部分分别存放，这样做的好处是即使别人拿到了你的预制件却是不完整的。
* 尽量利用动态脚本来加载场景而不是将整个场景打包，即使将整个场景打包，要把贴图和模型分开放置(因此如此，我虽然拿到了游戏的场景贴图，可是没有用啊)
* 尽量利用加密的方法来隐藏本地的 AssetBundle 或者使用不易察觉的存储位置作为 AssetBundle 的存储位置，不要用明文数据进行存储。

&emsp;&emsp;好了，今天的内容就是这样了，希望大家喜欢，AssetBundle 打包是一个值得去深入研究的问题，今天博主提出的这些观点不过是对《新仙剑 OL》这个游戏的打包提出 de 一些看法，如果大家有不同的看法，欢迎一起来交流！