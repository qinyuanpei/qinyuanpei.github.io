---
abbrlink: 2527231326
categories:
- Unity3D
date: 2015-11-21 14:47:26
description: 目前主要有 C++ CLR 和 C++ Native 两种实现方法，其中 C++ CLR 可以理解为运行在.Net CLR 即公共语言运行库上的 C++代码，这种代码是托管的 C++代码，目前并没有被 C++标准承认，因为它更像是 C++和 C#两种语言的混合代码，这种代码的优势是可以像普通的.NET 库一样被 C#调用，考虑到 Unity3D 建立在和.Net 类似的 Mono 上，因此这种方式应该是我们的最佳实践方案;Debug.Log("调用 C++
  CLR 中的方法 Max(5,10):" + ExampleClass.Max(5,10));C++ Native 则是指传统的 C++ 动态链接库，通过 DllImport 在 C#中进行包装后在 C#中进行调用，相对地这种方式调用的是非托管的 C++代码，这种方式相信接触过 Windows 开发的朋友应该不会感到陌生啦，它是一种更为普遍的方法，例如我们要接入苹果官方 SDK 的时候，需要对 Object
  C 的代码进行封装后交给 C#去调用，而这里使用的方法就是 DllImport 了
tags:
- Unity3D
- C++
- 插件
title: Unity3D 游戏开发之 C++ 插件接入
---

各位朋友大家好，我是**秦元培**，欢迎大家关注我的博客，我的博客地址是[http://qinyuanpei.com](http://qinyuanpei.com)。虽然 Unity3D 引擎依靠强大的跨平台能力睥睨高手林立的游戏引擎世界，我们在使用 Unity3D 游戏引擎的时候基本上不会去接触底层的东西，可是有时候面对某些奇葩的要求的时候，我们就不得不考虑使用 C++这样的语言来为其编写相关的插件。你如果问我是什么样的奇葩要求，比如接入蓝牙手柄来控制游戏、接入类似街机的设备来控制游戏、接入同一个游戏到两个不同的设备上并响应不同的控制……诸如此类的种种问题，可能目前在 Unity3D 引擎中找不到解决方案，这个时候写 C++插件就变成了一种刚性需求，这就是我们今天要来一起探讨的问题。

<!--more-->

Unity3D 主要使用 C#进行开发，所以为 Unity3D 编写插件本质上就是让 C#调用 C++代码。目前主要有 C++ CLR 和 C++ Native 两种实现方法，其中 C++ CLR 可以理解为运行在.Net CLR 即公共语言运行库上的 C++代码，这种代码是托管的 C++代码，目前并没有被 C++标准承认，因为它更像是 C++和 C#两种语言的混合代码，这种代码的优势是可以像普通的.NET 库一样被 C#调用，考虑到 Unity3D 建立在和.Net 类似的 Mono 上，因此这种方式应该是我们的最佳实践方案；C++ Native 则是指传统的 C++ 动态链接库，通过 DllImport 在 C#中进行包装后在 C#中进行调用，相对地这种方式调用的是非托管的 C++代码，这种方式相信接触过 Windows 开发的朋友应该不会感到陌生啦，它是一种更为普遍的方法，例如我们要接入苹果官方 SDK 的时候，需要对 Object C 的代码进行封装后交给 C#去调用，而这里使用的方法就是 DllImport 了。

好了，下面我们来看看两种方式各自是如何实现的吧！这里博主使用的开发环境是 Windows 8.1 32bit 和 Visual Studio 2012，Unity3D 的版本为 4.6 版本。

# C++ CLR

## 创建一个 C++ CLR 类库项目
首先我们按照下图中的步骤创建一个 C++ CLR 项目：

![截图是件讨厌的事情，虽然懒惰的人们都喜欢](https://ww1.sinaimg.cn/large/4c36074fly1fzix18bmvyj20qi0gwdgh.jpg)

请注意.Net 版本问题，重要的事情说三遍，不认真看这里的人出现问题就不要到我这里来评论了，我最讨厌连文章都没有看明白就来和你纠缠不清的人，谢谢。创建好项目后请打开项目属性窗口设置【公共语言运行时支持】节点的值为【安全 MSIL 公共语言运行时支持(/clr:safe)】好了，下面我们找到 CLR4Unity.h 文件，添加 ExampleClass 声明：

```csharp
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

显然我们这里定义了三个简单的方法，注意到第一个方法 Random 依赖于 System.Rnadom 类，而在托管的 C++中是使用 gcnew 来代替 new 这个关键字的，所以请尽情感受 C#和 C++的混搭语法风格吧！这样我们就可以编译得到 CLR4Unity.dll 这个类库，将这个文件复制到 Unity3D 项目中的 Plugins 目录下下，然后将其加入项目引用列表。如果你以为引用就是：
```csharp
using CLR4Unity;
```
呵呵，我严重怀疑你对.Net 的熟悉程度。你没有添加对 CLR4Unity.dll 的引用，你到底在 using 什么啊？

![先添加引用然后using](https://i.loli.net/2021/10/18/3SysYW9aBcwZRud.png)

如果你对.NET 熟悉到足以无视这里的一切，请闭上眼接着往下看，哈哈！

## 在 C#中添加引用及方法调用
接下来我们在 Unity3D 中创建一个脚本 PluginTest.cs，然后在 OnGUI 方法增加下列代码。可是你要以为这些代码就应该写在 OnGUI 方法中，抱歉请你先去了解 MonoBehaviour 这个类。什么？添加了这些代码报错？没有 using 的请自行面壁：
```csharp
//调用C++ CLR中的方法
if(GUILayout.Button("调用C++ CLR中的方法", GUILayout.Height (30))) 
{
	Debug.Log("调用C++ CLR中的方法Random(0,10):" + ExampleClass.Random(0,10));
	Debug.Log("调用C++ CLR中的方法Max(5,10):" + ExampleClass.Max(5,10));
	Debug.Log("调用C++ CLR中的方法Square(5):" + ExampleClass.Square(5));
}
```
# C++ Native
## 创建一个 C++动态链接库项目
首先我们按照下图中的步骤来创建一个 C++ Win32 项目：

![不要问我从哪里来](https://i.loli.net/2021/10/18/9Y8ti5QBdyJzwnF.png)

![我的故乡在远方](https://i.loli.net/2021/10/18/98qiKJletoV7vfg.png)

好了，接下来我们找到 Native4Unity.cpp 写入下列代码：

```cpp
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
和 C++ CLR 类似，我们使用标准的 C++语言来实现同样的功能。注意到 rand()这个函数是 C++标准库里的内容，所以我们在文件开头增加了对 stdlib.h 这个头文件的引用。这里需要注意的一点是：**所有希望使用 DllImport 引入 C#的 C++方法都应该在方法声明中增加__declspec(dllexport)关键字，除非它在.def 文件中对这些方法进行显示声明**。关于.def 文件的相关定义大家可以到 MSDN 上检索，这些都是属于 C++编译器的内容，这里不再详细说了。

## 在 C#中使用 DllImport 封装方法

将编译好的 Native4Unity.dll 复制到 Plugins 目录中后，下面我们要做的事情就是在 C#里对这些方法进行封装或者说是声明：

```csharp
 [DllImport("Native4Unity")]
 private extern static int Random(int min, int max);

 [DllImport("Native4Unity")]
 private extern static int Max(int a, int b);

 [DllImport("Native4Unity")]
 private extern static int Square(int a);
```

然后就是简单地调用啦：

```csharp
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