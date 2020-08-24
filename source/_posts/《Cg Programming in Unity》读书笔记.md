---
abbrlink: 1670305415
categories:
- 读书笔记
date: 2015-12-25 12:29:20
description: 在这里子着色器使用Tags标签来告诉渲染引擎期望何时和如何渲染对象，其语法是：;在通道中可以定义其名称和任意数目的标签，通过使用tags来告诉渲染引擎在什么时候该如何渲染他们所期望的效果，其语法和Tags标签完全相同，即采用键值对来定义标签的名称和其对应的值;Properties是由多条标签组成的Shader属性定义，这些属性能够在Unity3D中的编辑器中显示出来，以此来确定这段Shader代码由哪些输入
tags:
- Shader
- CG
- Unity
title: 《Cg Programming in Unity》读书笔记
---

&emsp;&emsp;最近开始着手Shader语言的学习，因为Unity3D没有提供类似虚幻四引擎的材质编辑器功能，所以当在Unity3D中碰到需要提供引擎默认材质以外的效果的时候，就需要我们来编写Shader以实现各种特效，本文主要是结合《Cg Programming in Unity》这本书和[浅墨](http://blog.csdn.net/poem_qianmo/article/details/49405909)博客中关于Shader的这部分内容来学习和整理，目的是帮助博主快速掌握Shader语言。

<!--more-->

# Unity3D中的Shader概述
&emsp;&emsp;为Unity3D编写Sahder代码相对OpenGL和DirectX要简单。Unity3D没有刻意地区分Cg语言和HLSL语言，因为这两者是非常相似的，这意味着使用HLSL编写的代码可以直接在Cg中使用，更为深入地探索HLSL和Cg的渊源你会戏剧性地发现Cg是Microsoft和NVIDIA联手推出并试图从硬件和软件上和GLSL相抗衡的一种产物。

&emsp;&emsp;其中[Cg](http://http.developer.nvidia.com/Cg/Cg_language.html)是[Nvidia](http://http.developer.nvidia.com/CgTutorial/cg_tutorial_chapter01.html)提供的一种Shader编写语言，HLSL是DirectX提供的一种Shader编写语言，这意味着大部分的Cg代码同样可以被HLSL支持。Unity3D中使用的Shader编写语言是ShaderLab，其本质是对Cg进行了封装，因此在Unity3D中编写Shader本质上在给DirectX或者OpenGL写Shader，因为我猜测在引擎内部存在HLSL和GLSL的相互转换使得Unity3D能够在不同的平台都有较好的图形表现。

&emsp;&emsp;Unity3D中Shader程序的编写可以参考[这里](http://unity3d.com/support/documentation/Components/SL-Reference.html)。我们知道计算机图形学的中渲染管线一般可以分为两种类型，即固定功能渲染管线和可编程渲染管线。因此从这个角度来看，Unity3D中主要有三种着色器，即固定功能着色器（Fixed Function Shader）、表面着色器（Surface Shader）和 顶点着色器&片段着色器 （Vertex Shader & Fragment Shader）。

# Unity3D中Shader的基本结构
&emsp;&emsp;首先，Unity3D中Shader的基本结构是：
```
Shader 
{ 
    //------【属性】------//
    Properties
    {

    } 

    //------【子着色器】------//
    SubShaders
    {
    }
       
    //------【回滚】------//
    Fallback
}
```
对这个结构我们的理解是，Shader代码首先是一些属性定义，用来指定这段代码将有哪些输入。接下来是一个或者多个的子着色器，在实际运行中，哪一个子着色器被使用是由运行的平台所决定的。子着色器是代码的主体，每一个子着色器中包含一个或者多个的Pass。在计算着色时，平台先选择最优先可以使用的着色器，然后依次运行其中的Pass，然后得到输出的结果。最后指定一个Fallback，用来处理所有SubShader都不能运行的情况称为回滚。下面来分别介绍Shader基本结构中的各个部分：

## Shader中的Properties
Properties是由多条标签组成的Shader属性定义，这些属性能够在Unity3D中的编辑器中显示出来，以此来确定这段Shader代码由哪些输入。常见的标签定义有：
```
name("display name", Range(min, max)) = number
```
定义一个在编辑器中可通过滑动条修改的浮点数属性
```
name("display name", Color) = (number,number,number,number)
```
定义一个在编辑器中可通过拾色器来设置RGBA的颜色值属性
```
name("display name", 2D) = "name" {options }
```
定义一个在编辑器中可编辑的2D纹理属性，其中options可选表示即纹理自动生成纹理坐标时的模式，通常是ObjectLinear、EyeLinear、SphereMap、 CubeReflect、CubeNormal其中之一。
```
name("display name", Rect) = "name"{ options }
```
定义一个在编辑器中可编辑的非二次方2D纹理属性
```
name("display name", Cube) = "name"{ options }
```
定义一个在编辑器中可编辑的立方贴图纹理属性

```
name("display name", Float) = number
```
定义一个在编辑器中可通过输入框修改的浮点数值属性
```
name("display name", Vector) =(number,number,number,number)
```
定义一个在编辑器中可通过输入框修改的Vector4属性

## Shader中的SubShader
&emsp;&emsp;SubShader，即子着色器。子着色器是代码的主体，每一个子着色器中包含一个或者多个的Pass。在计算着色时，平台先选择最优先可以使用的着色器，然后依次运行其中的Pass，然后得到输出的结果。子着色器的基本结构是：
```
Subshader
{ 
    //------【Tags标签】------//
    Tags{}

    //------【Pass通道】------//
    Pass
    {

    }
}
```
### Tags标签
在这里子着色器使用Tags标签来告诉渲染引擎期望何时和如何渲染对象，其语法是：
```
Tags { "TagName1" = "Value1" "TagName2" = "Value2" }
```
即采用一个键值对来表示标签的名称及其对应的值，通常由三种标签可以在这里使用：
```
"Queue" = "Transparent"
```
表示决定渲染次序的队列标签，其取值定义如下：
* Background在所有队列渲染之前被渲染，如天空盒等。
* Geometry默认渲染大部分的对象，如不透明的几何体等。
* Transparent在所有队列渲染之后被渲染采用由后到前的次序，如玻璃、粒子效果等。
* Overlay主要实现叠加效果的渲染，如镜头光晕等。

```
Tags { "Queue" = "Geometry+1" }
```
表示自定义中间渲染队列，当默认的渲染队列不能满足要求时可选用当前渲染队列。在Unity实现中每一个队列都被一个整数的索引值所代表。Background为1000、Geometry为2000、Transparent为3000、Overlay为4000.

```
Tags { "IgnoreProjector" ="True" }
```
表示忽略投影标签，其值为True表示忽略投影反之表示受投影影响。

### Pass通道
Pass通道块控制被渲染的对象的几何体。其结构定义如下：
```
Pass 
{ 
    //------【名称与标签】------//
    [Name and Tags] 
    //------【渲染设置】------//
    [RenderSetup]
    //------【纹理设置】------//
    [TextureSetup] 
}
```
### 名称与标签
在通道中可以定义其名称和任意数目的标签，通过使用tags来告诉渲染引擎在什么时候该如何渲染他们所期望的效果，其语法和Tags标签完全相同，即采用键值对来定义标签的名称和其对应的值。常用的标签有：
```
Tags { "LightMode" = "Always" }
```
表示一个光照模式标签，该标签的取值可以是：
* Always总是渲染。没有运用光照。
* ForwardBase用于正向渲染,环境光、方向光和顶点光等
* ForwardAdd用于正向渲染，用于设定附加的像素光，每个光照对应一个pass
* PrepassBase用于延迟光照，渲染法线/镜面光。
* PrepassFinal用于延迟光照，通过结合纹理，光照和自发光渲染最终颜色
* Vertex用于顶点光照渲染，当物体没有光照映射时，应用所有的顶点光照
* VertexLMRGBM用于顶点光照渲染，当物体有光照映射的时候使用顶点光照渲染。在平台上光照映射是RGBM 编码
* VertexLM用于顶点光照渲染，当物体有光照映射的时候使用顶点光照渲染。在平台上光照映射是double-LDR 编码（移动平台，及老式台式CPU）
* ShadowCaster使物体投射阴影。
* ShadowCollector为正向渲染对象的路径，将对象的阴影收集到屏幕空间缓冲区中。

#### 渲染设置
渲染设置设定显示硬件的各种状态，常用的命令如下：
```
Material 
{ 
    Diffuse Color(R,G,B,A)
    //漫反射颜色构成，即对象的基本颜色。

    Ambient Color(R,G,B,A)
    //环境色颜色构成，即当对象被RenderSettings中设定的环境色所照射时对象所表现的颜色。

    Specular Color(R,G,B,A)
    //对象反射高光的颜色。
    //(R,G,B,A)四个分量分别代表红绿蓝和Alpha，取值为0到1之间。

    Shininess Number
    //加亮时的光泽度，在0和1之间。

    Emission Color
    //自发光颜色，即当不被任何光照所照到时对象的颜色。
    //(R,G,B,A)四个分量分别代表红绿蓝和Alpha，取值为0到1之间。


    //【备注】对象上的完整光照颜色最终是：
    //FinalColor = Ambient * RenderSettings ambientsetting + 
    //(Light Color * Diffuse + Light Color *Specular) + Emission
}
```
定义一个使用顶点光照管线的材质
```
Lighting On | Off
```
开启或关闭顶点光照
```
Cull Back | Front | Off
```
设置多边形剔除模式
```
ZTest (Less | Greater | LEqual | GEqual |Equal | NotEqual | Always)
```
设置深度测试模式
```
ZWrite On | Off
```
设置深度写模式
```
Fog { Fog Block }
```
设置雾参数
```
AlphaTest (Less | Greater | LEqual | GEqual| Equal | NotEqual | Always) CutoffValue
```
开启alpha测试
```
Blend SourceBlendMode | DestBlendMode
```
设置alpha混合模式

```
Color Color value
```
设置当顶点光照关闭时所使用的颜色
```
ColorMask RGB | A | 0 | any combination of R, G, B, A
```
设置颜色写遮罩。设置为0将关闭所有颜色通道的渲染
```
Offset OffsetFactor , OffsetUnits
```
设置深度偏移
```
SeparateSpecular On | Off
```
开启或关闭顶点光照相关的平行高光颜色
```
ColorMaterial AmbientAndDiffuse | Emission
```
当计算顶点光照时使用每顶点的颜色

#### 纹理设置
纹理设置的作用是在完成渲染设定后指定一定数目的纹理及其混合模式：
```
SetTexture [texture property]{ [Combineoptions] }
```


## Shader中的Fallback
Fallback就像switch-case结构中的default，其作用是定义当处理所有SubShader都不能运行时采取的一个补救方案，这个主要是为了解决不同的显卡对Shader支持的差异问题。

# Unity3D中Shader的语法
Unity3D中Shader的语法主要针对Cg代码而言，Cg代码是可编程着色器和表面着色器中的核心内容，Cg代码从CGPROGRAM开始到ENDCG结束

# Unity3D中的三种着色器