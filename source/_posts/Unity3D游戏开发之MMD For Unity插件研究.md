---
title: Unity3D游戏开发之MMD For Unity插件研究
categories:
  - 单机游戏
tags:
  - Unity3D
  - 单机游戏
  - MMD
abbrlink: 4088452183
date: 2015-04-19 23:31:30
---
&emsp;&emsp;今天想来说说MMD。MMD是MikuMikuDance的简称，是由日本人樋口优开发的一组3D动画制作软件。该软件最初希望能够将3D建模软件完成的VOCALOID的初音未来等角色模型制作成可以随着音乐跳舞的动画，因此称为MMD。作者在此基础上开发了能够将歌曲让初音未来等角色歌唱的MikuMikuVoice。2011年9月11日，樋口优宣布停止MMD新版本的开发工作。不过人们对制作MMD的热情丝毫没有减少，在动漫、游戏等领域总是能够不断看到MMD的影子。例如[MMD/宇月](http://www.tudou.com/programs/view/qZtdjlAg34Q/?bid=03&pid=2&resourceId=51473713_03_05_02)和[千本樱/夏侯瑾轩](http://www.tudou.com/programs/view/WxxZZOR3EEc/?resourceId=0_06_02_99)都是较为典型的MMD。

<!--more-->

&emsp;&emsp;好了，相信现在大家都对MMD有了一定的了解了，作为一名单机游戏爱好者，我目前最为遗憾的两件事情：
* 不会制作游戏MV(或者说视频)
* 不会制作MMD(因为我是个程序嘛)

&emsp;&emsp;在我看来以同人形式去发掘一个作品中优秀的东西，这件事情本身就是一件让人觉得快乐的事情，因为可能某一个人和你有相同的想法，当它看到你的东西的时候，发觉你想表达的东西就是它想要表达的。我每次玩完一款游戏以后都会去网上搜集比较好的MV，因为我觉得随着人一天天地慢慢长大，有时候你发觉自己再没有时间去玩游戏的时候，通过看视频能让你想起很多的事情，有时候看着别人做的MV会哭，我便觉得当时的经历其实挺值的去回味的。好了，说了这么多毫不相干的事情，差点忘了今天的正事。首先我们来了解下一个完整的制作MMD的过程：
* 使用Maya、Blender或者3DsMax等3D软件建模(或者从游戏中提取)
* 使用PMDEditor或者PMXEditor对模型进行绑骨、动作和表情制作等操作
* 将处理过的.pmd或者.pmx模型导入MikuMikuDance完成场景、音乐完成动画制作

&emsp;&emsp;从这样一个过程我们了解到，制作MMD还是需要一定的技术门槛的，因为并不是每一个人都能够完成模型的绑骨、动画这些任务的。这篇文章不提供以上软件的下载和使用方法，因为我们接下来的内容基本与以上软件无关，我们的重点依然是Unity3D，因为我是一个游戏开发者嘛，哈哈。好了，下面的内容基于两点假设：
* 你有一个PMD或者PMX模型
* 你有一个VMD的动作文件

&emsp;&emsp;首先，第一步我们需要一个Unity3D插件MMD4Unity,将这个插件导入项目后，为了使整个项目结构较为清晰，我们将这个插件的文件夹命名为MMDPlugins。在MMDFiles文件中我们准备了三个文件:
* 模型文件：初音.pmd
* 动作文件：动作1.vmd和动作2.vmd

&emsp;&emsp;好了，现在我们注意到Unity3D菜单栏上会增加一个Plugin菜单项，我们单击这个菜单项会发现MMD Loader和XFile Importer这两个项目，这里我们选择MMD Loader这个菜单项：

![MMD1](http://7wy477.com1.z0.glb.clouddn.com/imgs_MMD1.png)

&emsp;&emsp;这两个子菜单项的意义十分地明确了，PMD Loader负责加载PMD模型并将其转化为Unity3D可以识别的模型文件，VMD负责将一个动作文件套用到一个模型上。所以：
* 1、通过PMD Loader打开加载PMD文件的窗口，建议这里将ShaderType设置为Default，因为如果使用MMD的Shader的话，待会转换出来的模型可能会存在找不到材质的问题。接下来我们点击Convert，稍等片刻就会在场景中看到一个模型(prefab)文件。

![MMD2](http://7wy477.com1.z0.glb.clouddn.com/imgs_MMD2.png)

![MMD3](http://7wy477.com1.z0.glb.clouddn.com/imgs_MMD3.png)

* 2、接下来通过VMD Loader打开加载VMD文件的窗口，选择场景中的模型文件和项目资源中的XMD动作文件，点击Convert，大概有1分钟多一点的样子就好了。此时我们选择场景中的模型文件，找到它的Animation组件，然后点击Animation右侧的按钮为其指定一个动画文件，因为刚刚我们已经为它添加了一个动作，所以我们可以很容易的在项目资源中找到名为初音_动作2的动画片段(AnimationClip)。

![MMD4](http://7wy477.com1.z0.glb.clouddn.com/imgs_MMD4.png)

&emsp;&emsp;好了，现在我们就来看看这个MMD的效果吧！

![MMD5](https://ws1.sinaimg.cn/large/4c36074fly1fyzctxp079g208506hh78.gif)

&emsp;&emsp;哈哈，感觉效果还不错吧！

&emsp;&emsp;现在来说说我在使用这个插件过程中遇到的问题：
* 在转换PMD模型的时候如果选择Default转换出的模型可以找到对应的材质，可是模型是错误的；如果选择MMDShader，转换出的模型会找不到对应得材质，比如说我在尝试转换下面这个模型的时候，因为MMD对模型的精细程度的要求，所以模型会被分得很细，因此像这个模型当贴图数目较少的时候，就没有办法自动对应贴图，所以这快目前还是个问题吧！
* 如果使用的是PMX模型，可以用PMEditor这个软件转换下格式，转成PMD格式后，后然后再按照本文的方法去做就可以了。
* PMD转换出来的模型没有办法选择其中的某一个部分，因此在操作模型的时候可能会不太方便吧，以前都是选择某一部分然后给模型贴图，现在这招不行了啊。

&emsp;&emsp;好了，今天的内容就是这样了，有什么问题大家给我留言哦！

