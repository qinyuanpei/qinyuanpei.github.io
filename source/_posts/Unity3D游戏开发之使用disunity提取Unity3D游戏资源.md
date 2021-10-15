---
abbrlink: 1082185388
categories:
- 单机游戏
date: 2015-04-03 13:29:18
description: 好了，下面我们再来看看怎么提取这个模型文件对应的贴图，在游戏目录/assetbundles/NPC/Texture/下有一个名为 s049_1.unity3d_1D2446B9 的文件，这就是 s049 这个模型对应的贴图了;下面我们就来尝试解析这个文件，不过游戏制作方对 config 文件夹下的内容进行了加密，因为在这个文件夹下面是两个 AssetBundle 文件，博主尝试用 extract 和 bundle-extract 两个命令进行解析，可是得到的只是些文本文件，对我们继续研究没有什么帮助;这个工具呢，博主在[Unity3D 游戏开发之反编译 AssetBundle 提取游戏资源](http://www.qinyuanpei.com/2015/04/02/unity3d-development-with-assetbundle/)这篇文章中其实已经提到过了，不过因为有些朋友对如何使用这个工具依然存在问题，所以博主决定特地写一篇文章来讲解如何使用 disunity 来提取 Unity3D 游戏中的素材
tags:
- 穹之扉
- Unity3D
- disunity
- 反编译
title: Unity3D 游戏开发之使用 disunity 提取 Unity3D 游戏资源
---

&emsp;&emsp;各位朋友，大家好，我是秦元培。今天博主想和分享的是使用 disunity 提取 Unity3D 游戏素材。这个工具呢，博主在[Unity3D 游戏开发之反编译 AssetBundle 提取游戏资源](http://www.qinyuanpei.com/2015/04/02/unity3d-development-with-assetbundle/)这篇文章中其实已经提到过了，不过因为有些朋友对如何使用这个工具依然存在问题，所以博主决定特地写一篇文章来讲解如何使用 disunity 来提取 Unity3D 游戏中的素材。

<!--more-->

# 准备工作
* [disunity](https://github.com/ata4/disunity):负责对 Unity3D 的数据文件进行解包
* [Unity3D](http://www.unity3d.com):负责将导出的数据文件显示出来
* [Bleander](http://www.blender.org/)或者 3DsMax:负责 Unity3D 数据文件的转换处理，二选一即可。个人推荐 Blender。
* Java:负责为 disunity 提供编译环境

# 测试文件
* 《新仙剑 OL》[下载](http://pan.baidu.com/s/1gd5tSzD)
* 《轩辕剑 6 外传穹之扉》
* 《雨血前传:蜃楼》[下载](http://pan.baidu.com/s/1dDwA6qt)

# 提取流程
&emsp;&emsp;好了，在确定做好所有的准备工作后，我们就可以正式开始今天的内容了！
## 编译 disunity
&emsp;&emsp;虽然我们可以从 disunity 的项目主页中下载 release 版本，不过为了保险起见，博主依然建议大家自行编译 disunity。编译的方法是在命令行中切换到 disunity 的目录，然后执行命令:
```Shell
java -jar disunity.jar
```
&emsp;&emsp;如果大家的 Java 环境没有任何问题的话，那么接下来我们就应该可以看到:
```Sheel
[Info] DisUnity v0.3.4
```
&emsp;&emsp;以及各种关于这个工具的使用方法和参数选项。那么好了，现在我们就来熟悉下 disunity 这个工具的常用命令。disunity 命令的基本形式是:
```plain
disunity [CommandName] [CommandOptions]
```
## disunity 命令
* dump:将一个二进制的对象转化成人类可以阅读的文本信息。
* dump-struct:将一个二进制的对象转化为结构化的信息。
* extract:将 Unity3D 的数据文件转化为常见的文本、声音、图片等信息。
* extract-raw:将 Unity3D 的数据文件转化为可序列化的对象，在 extract 命令不被支持的情况下使用。
* extract-txt:和 dump 命令类似输出转换结果到命令行。
* extract-struct:和 dump-struct 命令类似输出转换结果到命令行。
* info:输出 Unity3D 的数据文件和 AssetBundle 文件的变量信息。
* bundle-extract:释放所有的被打包到 AssetBundle 中的文件。
* bundle-inject:将从 AssetBundle 中打包的文件重新打包

&emsp;&emsp;暂时先介绍这些，因为其它的命令我们基本用不到，如果需要深入研究这些命令，可以参考 disunity 项目中的 README.md 文件。

## 解析《新仙剑 OL 》的 AssetBundle 文件
&emsp;&emsp;这里我们以游戏目录/assetbundles/NPC/Models/下的 s049.unity3d_CC9026FB 为例来讲解游戏模型的提取。
### 模型文件提取
&emsp;&emsp;首先我们将这个文件的扩展名改为 s049.unity3d，因为这是它原始的扩展名，是 Unity3D 中导出 AssetBundle 的一种文件格式。好了，我们将这个文件放在一个无中文路径的目录下，这里以 C:\Users\Robin\Desktop 即桌面为例。注意首先进入 disunity 的目录，然后执行命令：
```Shell
disunity extract C:\Users\Robin\Desktop\s049.unity3d
```
&emsp;&emsp;接下来会在桌面生成一个名为 s049 的文件夹，在这个文件夹中找到 Mesh 的子文件夹，会得到一个 s049.obj 的文件，这个文件就是我们提取到的模型文件。
### 模型贴图提取
好了，下面我们再来看看怎么提取这个模型文件对应的贴图，在游戏目录/assetbundles/NPC/Texture/下有一个名为 s049_1.unity3d_1D2446B9 的文件，这就是 s049 这个模型对应的贴图了。同样地，我们将其重命名为 s049_1.unity3d 然后执行命令：
```Shell
disunity extract C:\Users\Robin\Desktop\s049_1.unity3d
```
&emsp;&emsp;接下来在桌面上生成一个名为 s049_1 的文件夹，在这个文件夹中找到 Texture2D 的子文件夹，会得到一个名为 s049_1.dds 的贴图文件，这就是我们要提取的模型 s049 的贴图文件。
### 将模型和贴图合并
我们打开 Blender 并将 s049.obj 文件导入，然后将场景中默认的灯光和摄像机都删除，因为我们只需要一个模型文件，我们发现在 Blender 中已经可以看到模型了，因为 Unity3D 中使用的是 FBX 模型，所以我们这里将模型文件导出为 FBX 备用。因为 Unity3D 可以识别 dds 类型的贴图，所以对贴图我们不用做任何处理。

![童年林月如的模型](https://ww1.sinaimg.cn/large/4c36074fly1fz05jg3u49j20s50gz0to.jpg)

&emsp;&emsp;打开 Unity3D 将童年林月如的模型和贴图一起导入，将童年林月如的模型拖入到游戏场景中，因为模型的尺寸没有经过调整，所以模型刚开始可能会比较小，我们可以在 Unity3D 进行局部的调整。接下来我们会发现模型没有贴图，只要选择这个模型然后在属性窗口为它附上 s049_1.dds 的贴图文件即可。下面是童年林月如的模型导入 Unity3D 以后的效果:

![童年林月如导入Unity3D后的效果](https://ww1.sinaimg.cn/large/4c36074fly1fz05d13ddij20ax0bpdgo.jpg)

## 解析《新仙剑 OL》的 assets 文件
&emsp;&emsp;和 AssetBundle 不同，assets 文件是整个 Unity3D 项目中项目资源的打包集合，比如说 Asset 文件下的资源都会被打包到这里，所以说解析 assets 文件可能会有更大的收获吧！因为所有的 Unity3D 游戏都会有这样的文件，而 AssetBundle 文件只有在使用了这项技术的游戏项目中才有。比如说在 Unity3D 中有一个重要的 Resource 文件夹，这个文件夹打包后被被打包成 resources.assets 文件。这里我们以 xianjian_Data/resources.assets 文件为例。首先执行命名:
```Shell
disunity extract C:\Users\Robin\Desktop\resources.assets
```
&emsp;&emsp;接下来会在桌面生成一个 resources 的文件夹，打开这个文件夹我们会发现三个子文件夹，分别是 Shader、TextAsset 和 Texture2D。解析的结果似乎有点失望，不过在 TextAsset 文件夹下我们会找到一个叫做 ResourceFiles.txt 的文件，这是一个纯文本文件，我们可以直接打开，打开后我们发现它的内容是一个 Xml 文件，并且在这个 Xml 文件中定义了游戏中使用的各种资源的路径，不过这些资源都是以 AssetBundle 的形式来定义的。这说明什么呢？这说明《新仙剑 OL》的场景和界面资源是通过动态加载的方式加载到游戏当中的，而这些资源则是通过这个 Xml 文件来配置和管理的，这符合我们平时在 Unity3D 游戏开发中的观点和方法。通过这个文件，我们找到了 assetbundles/config/movieconfig.unity3d 这个文件，这是一个负责维护游戏中场景过场动画的文件。下面我们就来尝试解析这个文件，不过游戏制作方对 config 文件夹下的内容进行了加密，因为在这个文件夹下面是两个 AssetBundle 文件，博主尝试用 extract 和 bundle-extract 两个命令进行解析，可是得到的只是些文本文件，对我们继续研究没有什么帮助。那么好了，现在我们能够进行解析的只有 xinjian_Data/sharedassets0.assets 文件了：
```Shell
disunity extract C:\Users\Robin\Desktop\sharedassets0.assets
```
&emsp;&emsp;这个解出来的话是些没有什么用的贴图文件，看来如果要提取音乐或者图片的话，还需要进行更加深入的研究才行啊。

## 解析《雨血前传.蜃楼》的 assets 文件
&emsp;&emsp;因为解析《新仙剑 OL》的 assets 文件没有得到什么有用的东西，所以我们接下来来尝试解析《雨血前传.蜃楼》的 assets 文件。这款游戏是博主比较喜欢的一款游戏，基于 Unity3DY 引擎，而且这款游戏是作为 Unity3D 官方范例来推广的，因此研究这款游戏对我们提高 Unity3D 的资源打包机制会比较有帮助。好了，我们直接上手：
```Shell
disunity extract C:\Users\Robin\Desktop\resources.assets
```
&emsp;&emsp;哈哈，这款游戏果然没有让我们失望，我们得到了什么呢？

![蜃楼中各种Boss的头像](https://ww1.sinaimg.cn/large/4c36074fly1fz01yhmincj20ur0cdqan.jpg)

![蜃楼中游戏连招视频1](https://ww1.sinaimg.cn/large/4c36074fly1fz01tz1bvqj208w050mxb.jpg)

![蜃楼中游戏连招视频2](https://ww1.sinaimg.cn/large/4c36074fly1fyzcu600c0j208w0500sp.jpg)


# 总结
* 不同的游戏采用的资源配置方案都不同，不过一般可以从 resources.assets 这个文件入手作为突破点。
* 如果能拿到游戏中数据配置方案，对于我们提取游戏中的素材会有较大的帮助，因为这样方向性会更强些。
* 通过 AssetBundle 动态加载到场景中最好还是采用一个配置表来进行配置，这样便于我们管理和维护整个游戏项目。
* 如果没有服务器段的干预，理论上只要修改了本地的 AssetBundle 文件就可以实现对游戏内容和数据的更改，换句话说，可以做外挂和修改器。
