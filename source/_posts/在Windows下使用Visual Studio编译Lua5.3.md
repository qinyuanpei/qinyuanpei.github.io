---
abbrlink: 3642630198
categories:
- 编程语言
date: 2015-04-16 14:50:35
description: '```Lua'
tags:
- Lua
- 编译
- Visual Studio
title: 在Windows下使用Visual Studio编译Lua5.3
---

&emsp;&emsp;Lua5.3已经发布好长时间了，可是因为[LuaForWindows](http://files.luaforge.net/releases/luaforwindows/luaforwindows)的Lua版本无法和官方保持一致，所以想尝试下编译Lua5.3的源代码，因为作为一名合格的程序员，是应该要懂得编译原理的相关内容的啊(可是我真的没有学过编译原理啊!.....)。好了，那么今天博主将在文章中和大家分享自己编译Lua5.3的过程，希望能够对大家学习和使用Lua有些帮助吧！

<!--more-->

&emsp;&emsp;我们知道Lua由三部分组成，即
* Lua链接库
* Lua解释器
* Lua编译器

&emsp;&emsp;因此，对于Lua源代码的编译主要就是编译Lua链接库、Lua解释器和Lua编译器

#编译Lua链接库
* 使用Visual Studio创建一个VC++项目，项目命名为Lua53，项目类型为静态库、不设置预编译头。
* 删除Visual Studio自动创建的.cpp文件及其对应的.h文件。
* 将下载的Lua代码解压，将src目录下的全部文件拷贝到项目中，然后删除lua.c、luac.c和lua.hpp这三个文件。
* 编译项目会得到一个Lua53.lib的文件，这就是我们编译得到的Lua链接库。

#编译Lua解释器
&emsp;&emsp;我们知道Lua解释器是一个可以直接运行Lua代码的可执行文件，因此
* 在同一个解决方案下继续创建VC++项目，项目命名为Lua，项目类型为控制台应用程序、需设置预编译头。
* 删除Visual Studio自动创建的.cpp文件及其对应的.h文件。
* 将下载的Lua代码解压，将src目录下的全部文件拷贝到项目中，然后删除luac.c这个文件。
* 设置当前项目依赖于Lua53项目
* 编译项目会得到一个Lua.exe文件，这就是我们编译得到的Lua解释器。

&emsp;&emsp;运行该程序，我们可以看到下面的结果：

![Lua解释器程序](https://ww1.sinaimg.cn/large/4c36074fly1fz01zxszfqj20it0cdt8t.jpg)

&emsp;&emsp;好了，现在我们来写一个简单的Lua程序：
```Lua
io.write("Hello I get a powerful program language called Lua \n")
io.write(string.format("This Lua is %s and now is %s \n",_VERSION,os.date()))
```

&emsp;&emsp;程序运行结果为：
>Hello I get a powerful program language called Lua
>This Lua is Lua5.3 and now is 04/16/15 16:06:43

#编译Lua编译器
&emsp;&emsp;和Lua类似地，
* 在同一个解决方案下继续创建VC++项目，项目命名为Lua，项目类型为控制台应用程序、需设置预编译头。
* 删除Visual Studio自动创建的.cpp文件及其对应的.h文件。
* 将下载的Lua代码解压，将src目录下的全部文件拷贝到项目中，然后删除lua.c这个文件。
* 设置当前项目依赖于Lua53项目
* 编译项目会得到一个Luac.exe文件，这就是我们编译得到的Lua解释器。

&emsp;&emsp;使用Lua编译器需要在环境变量中增加对Lua编译器路径地引用，比如Luac.exe放在D:\Program Files\Lua\build\这个目录下，就在PATH这个变量中增加：
```
D:\Program Files\Lua\build;
```
&emsp;&emsp;因为每个人的Lua编译器存放的位置都不同，所以这个就不再赘述了。

&emsp;&emsp;好了，今天的内容就是这样了。

#链接
* [本文编译的Lua](http://pan.baidu.com/s/1hqs1fX6)
* [官方编译的Lua](http://joedf.users.sourceforge.net/luabuilds/)