---
abbrlink: 927393529
categories:
- 游戏开发
date: 2015-09-07 10:59:13
description: 1、三个不同的物体使用同一种材质，不做静态批处理，不做动态批处理：**DrawCall为4、面数为584、顶点数为641**;2、三个不同的物体使用同一种材质，只做静态批处理，不做动态批处理：**DrawCall为2、面数为584、顶点数为641**;3、三个不同的物体使用不同的材质，不做静态批处理，不做动态批处理：**DrawCall为4、面数为584、顶点数为641**
tags:
- 游戏
- Unity3D
- 优化
title: Unity3D游戏场景优化系列之批处理
---

&emsp;&emsp;各位朋友大家好，我是**秦元培**，欢迎大家关注我的博客，我的博客地址是[http://qinyuanpei.com](http://qinyuanpei.com)。最近开始研究Unity3D游戏场景优化，每次提及游戏优化这个话题的时候，我的脑海中都会浮现出《仙剑奇侠传六》这个让四路泰坦都光荣陨落的神奇游戏，作为一个使用Unity3D引擎进行游戏开发的仙剑玩家，我曾经天真的以为，这款使用Unity3D引擎打造的仙剑二十周年献礼之作，会让我对《仙剑奇侠传》这个系列游戏的未来充满更多期待，然而当游戏真正呈现在我眼前的时候，我感受到了在历代仙剑游戏中从未有过的尴尬和失望，我尴尬的是Unity3D这样一个比较强大的游戏引擎硬生生地被北软玩成了这个鬼样子，我失望的是这部游戏除了剧情和跳跳乐以外并没有什么让人看到希望的东西。

<!--more-->

![仙剑奇侠传六](https://ww1.sinaimg.cn/large/None.jpg)

![不到20帧的优化](https://ww1.sinaimg.cn/large/None.jpg)

&emsp;&emsp;我知道我这样说会有一堆仙剑玩家指责我说，仙剑本来就是玩剧情的嘛，所以只要剧情好其它的都可以原谅啦。然而我们每一个人都清楚《仙剑奇侠传》是一个RPG游戏，它不是每隔三年出一次新番的GAL动漫、不是每隔三年更新一次的言情小说、更不是每隔三年播放一次的偶像电影。两年前的今天我可以耐着性子玩通关《仙剑奇侠传五》，但是这一次我真的玩不下去了。当一个游戏因为优化问题而获得《仙剑奇侠传六：泰坦陨落》称号的时候，作为一个玩家我真的不想再为这个游戏洗白什么，虽然我曾经深爱过这个游戏。所以言归正传，作为一个程序员，我们还是来做点程序员该做的事情，那么我们今天说什么呢，我们来说说Unity3D里的[批处理](http://docs.unity3d.com/Manual/DrawCallBatching.html)！

###一、什么是批处理？
&emsp;&emsp;我们知道Unity3D在屏幕上绘制一个图形本质上调用**OpneGL**或者**DirectX**这样的API，因此在这个过程中会产生一定程度上的性能消耗。DrawCall是OpenGL中描述绘制次数的一个量，例如一个基本的OpenGL绘制流程是**设置颜色**->**绘图方式**->**顶点坐标**->**绘制**->**结束**，在绘制的过程中每帧都会重复这个过程，这就是一次DrawCall，所以当游戏中的绘制过程变得复杂的时候，就会带来DrawCall的急剧增加，进而带来游戏的性能问题，反映到游戏表现上就变成了优化问题。那么在Unity3D中采取了什么样的措施来降低DrawCall呢？这就是我们今天要说的批处理，换句话说Unity3D使用了批处理来达到降低DrawCall的目的，批处理希望通过对物体网格的重组来获得更高的绘制效率，试想以下如果将多个物体合并为一个物体，那么在绘制的时候只需要绘制一次就够了，因此从这个角度上来讲这样做肯定是可以降低DrawCall的，更深刻的一种理解是这里体现了一种资源循环调用的思想，接触过Android开发的朋友们一定知道ListView控件可以对其元素进行“缓存”从而提高效率，因为我们可以发现其实ListView是对列表项进行某种程度上的“复用”从而提高了效率，在Unity3D这里同样遵循了这个原理。在Unity3D中进行批处理的一个前提是相同材质的物体可以被合并，如果这些物体使用不同的材质，那么当我们把这些材质对应的纹理打成“图集”以后可以对其进行合并，并且在合并的时候应该是用**Renderer.sharedMaterial** 而非 **Renderer.material**以保证材质是可以共享的。关于DrawCall的相关细节大家从[这里](http://www.zhihu.com/question/29730328)来了解,博主并未对图形学领域有过深入的研究，因此就不在这里班门弄斧了啊，哈哈！

###二、Unity3D中批处理的两种方式
&emsp;&emsp;在Unity3D中有静态批处理和动态批处理两种方式，下面我们就来分别说说这两种不同的批处理方式！
####**静态批处理**
&emsp;&emsp;静态批处理其实大家都是知道的。为什么这样说呢？因为我们在使用Unity3D的过程中无形中培养了这样一个习惯，那就是将场景中相对来说“静态”的物体都勾选Static选项，这在Unity3D中称为**Static GameObjects**，并且因为这一特性和[Lightmapping](http://docs.unity3d.com/Manual/GIIntro.html)、[Navigation](http://docs.unity3d.com/Manual/Navigation.html)、[Off-meshLinks](http://docs.unity3d.com/Manual/class-OffMeshLink.html)、[ReflectionProbe](http://docs.unity3d.com/Manual/class-ReflectionProbe.html)、[Occluder and Occludee](http://docs.unity3d.com/Manual/OcclusionCulling.html)等内容均有着密切的联系，因此说静态批处理大家都是知道的其实一点都为过，和场景优化相关的内容博主会在后续的博客中涉及，希望大家能及时关注我的博客更新。静态批处理允许游戏引擎尽可能多的去降低绘制任意大小的物体所产生的DrawCall，它会占用更多的内存资源和更少的CPU资源，因为它需要额外的内存资源来存储合并后的几何结构，如果在静态批处理之前，如果有几个对象共享相同的几何结构，那么将为每个对象创建一个几何图形，无论是在编辑器还是在运行时。这看起来是个艰难的选择，你需要在内存性能和渲染性能间做出最为正确的选择。在内部，静态批处理是通过将静态对象转换为世界空间，并为它们构建一个大的顶点+索引缓冲区。然后，在同一批中，一系列的“便宜”画调用，一系列的“便宜”，几乎没有任何状态变化之间的。所以在技术上它并不保存“三维的调用”，但它可以节省它们之间的状态变化（这是昂贵的部分）。使用静态批处理非常简单啦，只要勾选物体的Static选项即可！

####**动态批处理**
&emsp;&emsp;相对静态批处理而言，动态批处理的要求更为严格一些，它要求批处理的动态对象具有一定的顶点，所以动态批处理只适用于包含小于900个顶点属性的网格。如果你的着色器使用顶点位置，法线和单光，然后你可以批处理300个顶点的动态对象；而如果你的着色器使用顶点位置，法线，uv0，UV1和切线，那么只能处理180个顶点的动态对象。接下来最为重要的一点，**如果动态对象使用的是不同的材质，那么即使进行了动态批处理从效率上来讲并不会有太大的提升。**如果动态对象采用的是多维子材质，那么批处理是无效的。如果动态对象接收实时光影，同样批处理是无效的。下面展示的是一个将多个物体合并为一个物体的脚本示例：
```C#
[MenuItem("ModelTools/将多个物体合并为一个物体")]
    static void CombineMeshs2()
    {
        //在编辑器下选中的所有物体
        object[] objs=Selection.gameObjects;
        if(objs.Length<=0) return;

        //网格信息数组
        MeshFilter[] meshFilters =new MeshFilter[objs.Length];
        //渲染器数组
        MeshRenderer[] meshRenderers = new MeshRenderer[objs.Length];
        //合并实例数组
        CombineInstance[] combines = new CombineInstance[objs.Length];
        //材质数组
        Material[] mats = new Material[objs.Length];

        for (int i = 0; i < objs.Length; i++)
        {
            //获取网格信息
            meshFilters[i]=((GameObject)objs[i]).GetComponent<MeshFilter>();
            //获取渲染器
            meshRenderers[i]=((GameObject)objs[i]).GetComponent<MeshRenderer>();

            //获取材质
            mats[i] = meshRenderers[i].sharedMaterial;   
            //合并实例           
            combines[i].mesh = meshFilters[i].sharedMesh;
            combines[i].transform = meshFilters[i].transform.localToWorldMatrix;
        }

        //创建新物体
        GameObject go = new GameObject();
        go.name = "CombinedMesh_" + ((GameObject)objs[0]).name;

        //设置网格信息
        MeshFilter filter = go.transform.GetComponent<MeshFilter>();
        if (filter == null)
            filter = go.AddComponent<MeshFilter>();
       filter.sharedMesh = new Mesh();
       filter.sharedMesh.CombineMeshes(combines,false);

       //设置渲染器
       MeshRenderer render = go.transform.GetComponent<MeshRenderer>();
       if (render == null)
           render = go.AddComponent<MeshRenderer>();
        //设置材质
        render.sharedMaterials = mats;
    }
```
&emsp;&emsp;这段脚本的核心是CombineMeshes()方法，该方法有三个参数，第一个参数是合并实例的数组，第二个参数是是否对子物体的网格进行合并，第三个参数是是否共享材质，如果希望物体共享材质则第三个参数为true，否则为false。在我测试的过程中发现，如果选择了对子物体的网格进行合并，那么每个子物体都不能再使用单独的材质，默认会以第一个材质作为合并后物体的材质，下面演示的是合并前的多个物体和合并后的一个物体的对比：

![合并前](https://ww1.sinaimg.cn/large/None.jpg)

![合并后](https://ww1.sinaimg.cn/large/4c36074fly1fz68ji32fwj214b0qfada.jpg)

###三、批处理效率分析
&emsp;&emsp;那么批处理对游戏效率提升究竟有怎样的作用呢？我们来看下面几组测试对比：

&emsp;&emsp;1、三个不同的物体使用同一种材质，不做静态批处理，不做动态批处理：**DrawCall为4、面数为584、顶点数为641**

&emsp;&emsp;2、三个不同的物体使用同一种材质，只做静态批处理，不做动态批处理：**DrawCall为2、面数为584、顶点数为641**

&emsp;&emsp;3、三个不同的物体使用不同的材质，不做静态批处理，不做动态批处理：**DrawCall为4、面数为584、顶点数为641**

&emsp;&emsp;4、三个不同的物体使用不同的材质，只做静态批处理，不做动态批处理：**DrawCall为4、面数为584、顶点数为641**

&emsp;&emsp;5、三个不同的物体使用不同的材质，不做静态批处理，只做动态批处理：**DrawCall为4、面数为584、顶点数为641**

&emsp;&emsp;6、三个不同的物体使用不同的材质，做静态批处理，做动态批处理：**DrawCall为4、面数为584、顶点数为641**

&emsp;&emsp;7、三个不同的物体使用同一种材质，不做静态批处理，只做动态批处理：：**DrawCall为4、面数为584、顶点数为641**

&emsp;&emsp;大家可以注意到各组测试结果中，只有第二组的DrawCall降低，这说明只有当不同的物体使用同一种材质时通过批处理可以从一定程度上降低DrawCall，即我们在文章开始提到的尽可能地保证材质共享。昨天下午兴冲冲地将游戏场景里的某些物体进行了动态批处理，但是实际测试的过程中发现DrawCall非常地不稳定，但是在场景中的某些地方DrawCall却可以降得非常低，如果静态批处理和动态批处理都不能对场景产生较好的优化，那么Unity3D游戏场景的优化究竟要从哪里抓起呢？我觉得这是我们每一个人都该用心去探索的地方，毕竟游戏做出来首先要保证能让玩家流畅的玩下去吧，一味的强调引擎、强调画面，却时常忽略引擎使用者的主观能动性，希望把一切问题都交给引擎去解决，这样的思路是错误而落后的，仙剑六的问题完全是用不用心的问题，我常常看到有人在公开场合说仙剑以后要换虚幻三，其实按照北软现在这样的状态，给他们一个虚幻四也不过是然并卵。我在[知乎](http://www.zhihu.com/question/29403861)上看到了号称15岁就开发次时代游戏的高中生妹子，做出个能称为DEMO的游戏就觉得自己可以搞引擎了，更有甚者随便用DirectX或者OpenGL封装若干函数就敢说自己会做游戏引擎了，呵呵，你确定你的游戏能在别人的电脑或者手机上运行起来吗？优化的重要性可见一斑。

###四、小结
&emsp;&emsp;好了，通过今天这篇文章，我们可以整理出以下观点：
&emsp;&emsp;**1、如果不同的物体间共享材质，则可以直接通过静态批处理降低DrawCall**
&emsp;&emsp;**2、动态批处理并不能降低DrawCall、面数和顶点数（我不会告诉你我昨天傻呵呵地合并了好多场景中的模型，结果面数和顶点数并没有降下来，23333）**
&emsp;&emsp;**3、不管是静态批处理还是动态批处理都会影响Culiing，这同样是涉及到场景优化的一个概念，好吧，为了让场景的DrawCall降下来我最近可能要研究好多涉及的优化的内容......**
&emsp;&emsp;那么今天的内容就是这样子了，希望对大家学习Unity3D有所帮助，欢迎大家和我交流这些问题来相互促进，毕竟这才是我写博客最初的目的嘛，哈哈！