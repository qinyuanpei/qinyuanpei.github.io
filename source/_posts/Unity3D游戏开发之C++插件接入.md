---
abbrlink: 2527231326
categories:
- Unity3D
date: 2015-11-21 14:47:26
description: 目前主要有C++ CLR和C++ Native两种实现方法，其中C++ CLR可以理解为运行在.Net CLR即公共语言运行库上的C++代码，这种代码是托管的C++代码，目前并没有被C++标准承认，因为它更像是C++和C#两种语言的混合代码，这种代码的优势是可以像普通的.NET库一样被C#调用，考虑到Unity3D建立在和.Net类似的Mono上，因此这种方式应该是我们的最佳实践方案
tags:
- Unity3D
- C++
- 插件
title: Unity3D游戏开发之C++插件接入
---

&emsp;&emsp;各位朋友大家好，我是**秦元培**，欢迎大家关注我的博客，我的博客地址是[http://qinyuanpei.com](http://qinyuanpei.com)。虽然Unity3D引擎依靠强大的跨平台能力睥睨高手林立的游戏引擎世界，我们在使用Unity3D游戏引擎的时候基本上不会去接触底层的东西，可是有时候面对某些奇葩的要求的时候，我们就不得不考虑使用C++这样的语言来为其编写相关的插件。你如果问我是什么样的奇葩要求，比如接入蓝牙手柄来控制游戏、接入类似街机的设备来控制游戏、接入同一个游戏到两个不同的设备上并响应不同的控制......诸如此类的种种问题，可能目前在Unity3D引擎中找不到解决方案，这个时候写C++插件就变成了一种刚性需求，这就是我们今天要来一起探讨的问题。

<!--more-->

&emsp;&emsp;Unity3D主要使用C#进行开发，所以为Unity3D编写插件本质上就是让C#调用C++代码。目前主要有C++ CLR和C++ Native两种实现方法，其中C++ CLR可以理解为运行在.Net CLR即公共语言运行库上的C++代码，这种代码是托管的C++代码，目前并没有被C++标准承认，因为它更像是C++和C#两种语言的混合代码，这种代码的优势是可以像普通的.NET库一样被C#调用，考虑到Unity3D建立在和.Net类似的Mono上，因此这种方式应该是我们的最佳实践方案；C++ Native则是指传统的C++ 动态链接库，通过DllImport在C#中进行包装后在C#中进行调用，相对地这种方式调用的是非托管的C++代码，这种方式相信接触过Windows开发的朋友应该不会感到陌生啦，它是一种更为普遍的方法，例如我们要接入苹果官方SDK的时候，需要对Object C的代码进行封装后交给C#去调用，而这里使用的方法就是DllImport了。

&emsp;&emsp;好了，下面我们来看看两种方式各自是如何实现的吧！这里博主使用的开发环境是Windows 8.1 32bit 和 Visual Studio 2012，Unity3D的版本为4.6版本。
#C++ CLR
##创建一个C++ CLR类库项目
&emsp;&emsp;首先我们按照下图中的步骤创建一个C++ CLR项目：

![截图是件讨厌的事情，虽然懒惰的人们都喜欢](https://ww1.sinaimg.cn/large/4c36074fly1fzix18bmvyj20qi0gwdgh.jpg)

请注意.Net版本问题，重要的事情说三遍，不认真看这里的人出现问题就不要到我这里来评论了，我最讨厌连文章都没有看明白就来和你纠缠不清的人，谢谢。创建好项目后请打开项目属性窗口设置【公共语言运行时支持】节点的值为【安全 MSIL 公共语言运行时支持(/clr:safe)】好了，下面我们找到CLR4Unity.h文件，添加ExampleClass声明：

```
/// <summary>
/// 一个简单的托管C++示例类
/// </summary>
public  ref  class ExampleClass
{
	public:

	/// <summary>
	/// 产生一个介于min和max之间的整型随机数
	/// <returns>整型随机数</returns>
	/// <param name="min">最小值</param>
	/// <param name="max">最大值</param>
	/// </summary>
	static int  Random(int min,int max)
	{
		//注意在托管的C++中使用gcnew来代替new
		//我承认C++写CLR代码略显奇葩像是C++和C#语法的混合
		return (gcnew System::Random)->Next(min,max);
	}

	/// <summary>
	/// 计算一个整数的平方
	/// <returns>整型数值</returns>
	/// <param name="a">需要平方的数值</param>
	/// </summary>
	static int Square(int a)
	{
		return a * a;
	}

	/// <summary>
	/// 返回两个数中的最大值
    /// <returns>整型数值</returns>
	/// <param name="a">参数1</param>
	/// <param name="b">参数2</param>
	/// </summary>
	static int Max(int a,int b)
	{
		if(a<=b){
			return b;
		}else{
			return a;
		}
	}
};
```

显然我们这里定义了三个简单的方法，注意到第一个方法Random依赖于System.Rnadom类，而在托管的C++中是使用gcnew来代替new这个关键字的，所以请尽情感受C#和C++的混搭语法风格吧！这样我们就可以编译得到CLR4Unity.dll这个类库，将这个文件复制到Unity3D项目中的Plugins目录下下，然后将其加入项目引用列表。如果你以为引用就是：
```
using CLR4Unity;
```
呵呵，我严重怀疑你对.Net的熟悉程度。你没有添加对CLR4Unity.dll的引用，你到底在using什么啊？

![先添加引用然后using](https://ww1.sinaimg.cn/large/None.jpg)

如果你对.NET熟悉到足以无视这里的一切，请闭上眼接着往下看，哈哈！

##在C#中添加引用及方法调用
&emsp;&emsp;接下来我们在Unity3D中创建一个脚本PluginTest.cs，然后在OnGUI方法增加下列代码。可是你要以为这些代码就应该写在OnGUI方法中，抱歉请你先去了解MonoBehaviour这个类。什么？添加了这些代码报错？没有using的请自行面壁：
```
//调用C++ CLR中的方法
if(GUILayout.Button("调用C++ CLR中的方法", GUILayout.Height (30))) 
{
	Debug.Log("调用C++ CLR中的方法Random(0,10):" + ExampleClass.Random(0,10));
	Debug.Log("调用C++ CLR中的方法Max(5,10):" + ExampleClass.Max(5,10));
	Debug.Log("调用C++ CLR中的方法Square(5):" + ExampleClass.Square(5));
}
```
#C++ Native
##创建一个C++动态链接库项目
&emsp;&emsp;首先我们按照下图中的步骤来创建一个C++ Win32项目：

![不要问我从哪里来](https://ww1.sinaimg.cn/large/None.jpg)

![我的故乡在远方](https://ww1.sinaimg.cn/large/None.jpg)

好了，接下来我们找到Native4Unity.cpp写入下列代码：

```
// Native4Unity.cpp : 定义 DLL 应用程序的导出函数。
//

#include "stdafx.h"
//为了使用rand()函数引入C++标准库
#include "stdlib.h"

/// <summary>
/// 产生一个介于min和max之间的整型随机数
/// <returns>整型随机数</returns>
/// <param name="min">最小值</param>
/// <param name="max">最大值</param>
/// </summary>
extern "C" __declspec(dllexport) int Random(int min,int max)
{
	return rand() % (max - min + 1) + min;
}

/// <summary>
/// 返回两个数中的最大值
/// <returns>整型数值</returns>
/// <param name="a">参数1</param>
/// <param name="b">参数2</param>
/// </summary>
extern "C" __declspec(dllexport) int Max(int a ,int b)
{
	if(a<=b){
	   return b;
    }else{
	   return a;
	}
}

/// <summary>
/// 计算一个整数的平方
/// <returns>整型数值</returns>
/// <param name="a">需要平方的数值</param>
/// </summary>
extern "C" __declspec(dllexport) int Square(int a)
{
	return a * a;
}
```
和C++ CLR类似，我们使用标准的C++语言来实现同样的功能。注意到rand()这个函数是C++标准库里的内容，所以我们在文件开头增加了对stdlib.h这个头文件的引用。这里需要注意的一点是：**所有希望使用DllImport引入C#的C++方法都应该在方法声明中增加__declspec(dllexport)关键字，除非它在.def文件中对这些方法进行显示声明**。关于.def文件的相关定义大家可以到MSDN上检索，这些都是属于C++编译器的内容，这里不再详细说了。

##在C#中使用DllImport封装方法

&emsp;&emsp;将编译好的Native4Unity.dll复制到Plugins目录中后，下面我们要做的事情就是在C#里对这些方法进行封装或者说是声明：

```
 [DllImport("Native4Unity")]
 private extern static int Random(int min, int max);

 [DllImport("Native4Unity")]
 private extern static int Max(int a, int b);

 [DllImport("Native4Unity")]
 private extern static int Square(int a);
```

然后就是简单地调用啦：

```
//调用C++ Native中的方法
if(GUILayout.Button("调用C++ Native中的方法", GUILayout.Height (30))) 
{
    Debug.Log("调用C++ Native中的方法Random(0,10):" + Random(0, 10));
    Debug.Log("调用C++ Native的方法Max(5,10):" + Max(5, 10));
    Debug.Log("调用C++ Native中的方法Square(5):" + Square(5));
}
```

最终程序的运行效果如图：

![这个结果来之不易请大家珍惜](https://ww1.sinaimg.cn/large/4c36074fly1fz68jlzlyqj20kr08edfr.jpg)