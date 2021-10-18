﻿---
abbrlink: 2038378679
categories:
- 读书笔记
date: 2015-03-08 19:14:44
description: '## JavaScript 中的面向对象编程;如果直接使用 JavaScript 代码;### 在 JavaScript 中函数(function)就是就是一个类(class)'
tags:
- 游戏
- HTML5
- 技术
- 笔记
title: HTML5 游戏开发技术基础整理
---

随着 HTML5 标准最终敲定，HTML5 将有望成为游戏开发领域的的热门平台。HTML5 游戏能够运行于包括 iPhone 系列和 iPad 系列在内的计算机、智能手机以及平板电脑上，是目前跨平台应用开发的最佳实施方案。本文系根据 《HML5 Canvas 游戏开发实战》 一书中的内容整理而成，是了解和学习 HTML5 游戏开发的基础内容，希望能够帮助到那些和博主一样致力于游戏开发的朋友们！
<!--more-->

## JavaScript 中的面向对象编程
对于游戏开发来说，面向对象编程(OOP)是一种重要而且必要的方法，所以在了解 HTML5 游戏开发前，首先应该了解 JavaScript 中的面向对象编程。JavaScript 是一种基于对象的语言，可它并不是一种真正的面向对象的编程语言，因为在 JavaScript 的语法中不存在类(Class)的概念。下面我们将分析和解决在 JavaScript 中实现封装、继承等面向对象的问题。
### 在 JavaScript 中函数(function)就是就是一个类(class)
```JavaScript
//声明一个函数
function MyClass(){}
//实例化一个对象
var cls1 = new MyClass();
```
### 使用 this 关键字就可以为类增加属性
```JavaScript
//声明一个类并定义其构造函数
function MyClass(name,age)
{
    this.name = name;
    this.age  = age;
};
//实例化一个对象
var cls1 = new MyClass("张三",20)
//输出cls1的两个属性值
alert("name=" + cls1.name + "&" + cls1.age)
```
### 使用 prototype 属性可以为类添加方法
```JavaScript
//声明一个类并定义其构造函数
function MyClass(name,age)
{
    this.name = name;
    this.age  = age;
};
//为MyClass增加方法
MyClass.prototype=
{
    toString:function()
    {
        alert("name=" + this.name + "&" + this.age)
    },
    getName:function()
    {
        alert("name=" + this.name)
    },
    getAge:function()
    {
        alert("age=" + this.age)
    }
};
```
### 使用 apply 方法实现属性和方法的继承
```JavaScript
//定义一个父类People
function People()
{
    this.type="人"
};
//为父类定义一个方法
People.prototype=
{
    getType:function()
    {
        alert("type=" + this.type)
    }
};

//定义一个子类Student
function Student(name,age,sex)
{
   //继承父类的属性type
   People.apply(this,arguments);
   this.name = name;
   this.age = age;
   this.sex = sex;
};

//声明一个Student实例
var stu = new Student("张三",20,"男")；
//输出type
alert(stu.type)

//下面我们来了解下如何继承父类的方法，继承父类方法主要通过循环使用父对象的prototype进行复制来实现，如
//重新定义子类Student
function Student(name,age,sex)
{
    //继承父类的属性type
   People.apply(this,arguments);
   //继承父类的方法，略显抽象
   var prop;
   for(prop in People.prototype)
   {
        var proto = this.constructor.prototype;
        if(!proto[prop])
        {
            proto[prop] = People.prototype[prop];
        }
        proto[prop]["super"] = People.prototype;
   }
   //属性定义
   this.name = name;
   this.age = age;
   this.sex = sex;
};

//实例化Student对象
var stu = new Student("张三",20,"男");
stu.getType();
```
### 静态类的实现
```plain
function staticClass()
{
    staticClass.name = "张三";
    staticClass.toString=function
    {
        alert("name=" + staticClass.name )
    };
};

alert(staticClass.name);
staticClass.toString();
```


## Canvas 绘图基础
HTML5 提供了图像、视频、音频、表单、位置、本地数据库、离线存储、websocket 等各种全新的特性，对于 HTML 游戏开发而言，我们主要关注图像、音频、本地数据库以及 websocket 等，首先我们来了解下 Canavs 绘图的基础内容。

Canvas 是 HTML5 为我们提供的一张画布，可以让我们在 HTML 上直接绘制图形，因此 Canvas 可以作为 HTML5 游戏开发的基本元素，即 HTML5 游戏引擎的底层都是以 Canvas 元素来驱动的。Canvas 本身没有绘图的能力，需要借助于 JavaScript 来实现绘图的功能。使用 Canvas 元素只需要在网页中添加 canvas 标记即可，如
```HTML
<canvas id="myCanavs" width="800" height="480"></canvas>
```
接下来我们通过 JavaScript 来获取这个 Canvas 并通过相关 API 实现绘图环境的初始化
```JavaScript
//获取Canvas元素
var canvas = document.getElementById('myCanvas');
//检查canvas合法性
if(canvas && canvas.getContext)
{
    //获取当前上下文
    var ctx = canvas.getContext('2d')    
}
```
因为目前 Canvas 只支持 2D 绘图，因此，这里的参数暂时只能为 2d。因为 Cnavas 绘图的 API 都封装在 ctx 这个实例中，因此下面的所有操作都是基于 ctx 来实现的：
### 使用 Canvas 绘制线
```JavaScript
//设置线宽
ctx.lineWidth = 10;
//设置画笔颜色
ctx.strokeStyle = "red";
//创建一个路径
ctx.beginPath();
//路径起点
ctx.moveTo(10,10);
//路径终点
ctx.lineTo(150,50);
//绘制路径
ctx.stroke();
```
### 使用 Cnavas 绘制矩形
```JavaScript
//设置线宽
ctx.lineWidth=5;
//设置画笔颜色
ctx.strokeStyle-"red"
//创建路径
ctx.beginPath();
//绘制矩形
ctx.strokeRect(10,10,70,40);
```
或者
```JavaScript
//定义矩形
ctx.rect(10,10,70,40);
//绘制矩形
ctx.stroke();
```
如果需要对矩形进行填充
```JavaScript
//创建路径
ctx.beginPath()
//绘制矩形
ctx.fillRect(10,10,70,40)
```
### 使用 Canvas 绘制圆
```JavaScript
//创建路径
ctx.beginPath();
//定义圆
ctx.arc(100,100,50,0,360*Math.PI/180,true);
//绘制圆
ctx.stroke();
```
同样地，可以使用 fill 进行填充绘制
```JavaScript
//创建路径
ctx.beginPath();
//定义圆
ctx.arc(100,100,50,0,360*Math.PI/180,true);
//绘制圆
ctx.fill();
```
### 使用 Canvas 绘制圆角矩形
绘制圆角矩形需要 arcTo 函数配合 lineTo 来完成
```JavaScript
//创建路径
ctx.beginPath();
ctx.moveTo(40,20);
ctx.lineTo(100,20);
ctx.arcTo(100,20,120,40,20);
ctx.lineTo(120,70);
ctx.arcTo(120,90,100,90,20);
ctx.lineTo(40,90);
ctx.arcTo(20,90,100,70,20);
ctx.lineTo(20,40);
ctx.arcTo(20,20,40,20,20);
//绘制圆角矩形
ctx.stroke();
```
### 使用 Canvas 绘制复杂图形
在 HTML5 中可以通过 quadraticCurveTo 函数绘制二次贝塞尔曲线，通过 bezierCurveTo 函数绘制三次贝塞尔曲线,具体代码请参考 API 文档。

### 使用 Canvas 绘制文字
```JavaScript
//设置字体
ctx.font="30px Arial";
//绘制文字
ctx.strokeText("Hello HTML5",100,50);
```
### 使用 Canvas 绘制图片
绘制图片使用 drawImage 函数，其函数原型如下：
```JavaScript
drawImage(image,dx,dy);
```
其中 image 可以是 HTML 中的<img/>标签或者是 JavaScript 中的 Image 对象。如
```HTML
//定义一个img标签
<img id="img_source" src="source.jpg" width="240" height="240"/>
```
接下来通过 getElementById 来取得图像数据，并将其绘制出来
```JavaScript
var img=document.getElementById("img_source");
ctx.draw(img,200,200);
```
如果直接使用 JavaScript 代码
```JavaScript
var img=new Image();
img.src="source.jpg";
ctx.draw(img,200,200)
```
### 图形的平移操作
使用 translate 函数实现在水平和垂直方向上的平移
### 图形的旋转操作
使用 rotate 函数实现旋转，需要注意的是传入的参数是弧度
### 图形的伸缩操作
使用 scale 函数实现伸缩，当参数为负值时表示在该方向上翻转
### 图形高级特效
这里主要介绍线性渐变、径向渐变、颜色反转、灰度。
* 线性渐变
```JavaScript
//创建一个线性渐变容器
var grd=ctx.createLinearGradient(0,0,200,0);
//添加颜色
grd.addColorStop(0.2,"#00ff00");
grd.addColorStop(0.8,"#ff0000");
//应用渐变
ctx.fillStyle=grd;
```
* 径向渐变
```JavaScript
//创建一个径向渐变容器
var grd=ctx.createRadialGradient(100,100,10,100,100,50);
//添加颜色
grd.addColorStop(0,"#00ff00");
grd.addColorStop(,"#ff0000");
//应用渐变
ctx.fillStyle=grd;
```
* 颜色反转
遍历每个像素并对 RGB 值进行取反
* 灰度
灰度计算公式：gary = red * 0.3 + green * 0.59 + blue * 0.11

基础的内容就是这些了，以后如果碰到需要 HTML5 的地方可以回过头来看看。