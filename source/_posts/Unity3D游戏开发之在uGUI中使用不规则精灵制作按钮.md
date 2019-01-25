---
title: Unity3D游戏开发之在uGUI中使用不规则精灵制作按钮
categories:
  - Unity3D
tags:
  - Unity3D
  - uGUI
  - 游戏开发
abbrlink: 1190622881
date: 2016-07-08 21:58:39
---
&emsp;&emsp;各位朋友大家好，欢迎关注我的博客，我的博客地址是[http://www.qinyuanpei.com](http://www.qinyuanpei.com)。最近因为受到工作上业务因素影响，所以博主在Unity引擎上的研究有所停滞。虽然目前的工作内容和Unity3D没有直接的关联，可是我觉得工程师应该有这样一种情怀，即工作和兴趣是完全不同的两个概念。编程对我而言，首先是一种兴趣，其次是一份工作。所以我宁愿在每天下班以后继续研究自己感兴趣的东西，而非为了取悦这个世界、为了加班而加班。最近广电总局让整个游戏行业都坐立不安了，因为其新发布的一系列规定，让中国的独立游戏开发者怨声载道。可是我们更应该看到积极的一面是，无数的小游戏公司会在最近数月内大量消失，或许对中国野蛮生长的游戏行业这是一次“形式”上的整顿，可对我们开发者来说，在这个过程中努力提升自我、巩固基础永远比追求时髦、流行的技术或者框架有意义的多，因为热闹的从来都是昙花一现般的璀璨，而永恒的永远都是历久弥新的真理。好了，闲言少叙，今天我们的话题是在uGUI中使用不规则精灵制作按钮。

<!--more-->
# 从用户体验说起
&emsp;&emsp;我们都知道在现代应用程序设计中，用户体验(UX)和用户界面(UI)是两个非常重要的内容。为什么用户体验(UX)和用户界面(UI)会显得如此重要呢？这是因为从普通用户的角度来讲，用户界面(UI)是其接触到一个产品时最先看到的最直观的东西，而在这个过程中产生的直观感受就是用户体验(UX)，所以说到底这是一个产品给用户的“第一印象”。

![UX和UI](http://img.blog.csdn.net/20160709212447055)

&emsp;&emsp;最近百度UE总监刘超在IXDC峰会上的演讲引起了大家的关注，抛开百度在人才选拔机制中存在的问题以及刘超本人在设计领域是否具备专业能力这两个问题，这件事情真正让大家吐槽的是什么呢？答案是用户体验。虽然IXDC并非国际级别的大型会议，但是我相信大家组织这样的活动，其本意是为了探讨交互、设计领域内的新方法和新思维，因为随着互联网行业的发展，交互和设计这个领域越来越被人们所关注，所以在这样一个场合下，当与会嘉宾都在试图向人们输出干货的时候，刘超以一个非常糟糕的“用户体验”来给大家讲什么是用户体验，这件事情起源自刘超的一个个人行为，结果牵一发而动全身，最终升级为百度继“魏则西事件”以后的又一次公关危机。

![什么叫设计](http://img.blog.csdn.net/20160709212751060)

&emsp;&emsp;我到底想说什么呢？我说的本质上就是用户体验的问题，在这个事件中，刘超穿着上的不得体(短裤搭配拖鞋?)、PPT制作的粗制滥造(校招时所用修改)、演讲过程的敷衍糊弄(说相声、猜谜语)等因素，让刘超在与会者心目中的地位瞬间滑落到冰点，进而引发人们对百度在交互设计领域内的能力的怀疑，联想到百度最近这些年内出现的问题，这件事情难免会被人作为指责百度这家企业价值观问题，我想这是这个事情为什么会让大家如此关注的一个原因吧。

![WTF!](http://img.blog.csdn.net/20160709212618558)

&emsp;&emsp;那么，我们说这些到底和今天的主题有什么关系呢？我想说这当然有关系啊，因为我们提出的这个问题就是一个用户体验的问题。我们知道游戏行业对美术资源高度依赖，不管是2D游戏还是3D游戏，一个项目组中前期主要的工作量其实都在美术这边，虽然不同的游戏引擎、GUI框架都为我们提供了标准的控件样式，然而在这样一个注重多样性的时代，默认样式、系统字体都会让人觉得这个产品缺乏新意，因此这种要求体现在游戏项目中就变成了，我们使用大量的图片资源来解决界面和字体的问题。

&emsp;&emsp;例如，我们通常使用BMFont来制作位图字体，这是为了同时满足字体的多样性和资源的容量这两个要求。再比如我们在使用cocos2d-x和Unity3D引擎开发游戏的时候，我们将大量的时间花费在了UI的制作上，这一切的一切从本质上来讲都是为了提升产品的童虎体验。这样我们就会遇到一个问题，UI中的按钮默认情况下都是规则的矩形，而实际上美术提供的素材常常是不规则的，因此如果继续使用以矩形为标准的这套机制，在实际使用中可能出现“用户点击在不该响应的区域结果程序响应了用户操作”这样的问题，为了解决这个问题，提升这一点点细微的用户体验，我们需要花费时间和精力来了解下面这些内容。

# 两种不同的方案
&emsp;&emsp;目前，关于这个问题如何，解决通过搜索引擎我们能找到两种不同的方案：
* 多边形碰撞器: 该方法是指给精灵(Sprite)添加一个多边形碰撞器(Rolygon Collider)组件，利用该组件来标记精灵的边界，这样通过比较鼠标位置和边界可以判断点击是否发生在精灵内部。这种方法的详细说明可以参考宣雨松的这篇文章：[UGUI研究院之不规则按钮的响应区域（十四）](http://www.xuanyusong.com/archives/3492)
* 精灵像素检测: 该方法是指通过读取精灵(Sprite)在某一点的像素值(RGBA)，如果该点的像素值中的Alpha<0.5则表示该点处是透明的，即用户点击的位置在精灵边界以外，否则用户点击的位置在精灵边界内部。这种方法的详细说明可以参考[这里](http://m.manew.com/forum.php?mod=viewthread&tid=45046&highlight=uGUI%2B%E4%B8%8D%E8%A7%84%E5%88%99&mobile=2)

## 多边形碰撞器
&emsp;&emsp;多边形碰撞器这种方案从本质上来讲，其核心思路是验证某一点是否在任意多边形内部，因为在这里RolygonCollider2D组件的作用体现在：第一，它可以在编辑器下进行可视化编辑对用户友好；第二，它可以在帮助我们标记精灵边界的同时保留顶点信息。所以在这里RolygonCollider2D组件相当于为我们提供任意多边形的顶点信息，而接下来我们要做是将鼠标位置转化为屏幕坐标，这样我们就获得了某一点的坐标。整体思路看起来是没有问题的，但我个人以及网友[AwayMe](http://m.manew.com/forum.php?mod=viewthread&tid=41050&highlight=uGUI%2B%E4%B8%8D%E8%A7%84%E5%88%99&mobile=2)都认为宣雨松这个算法存在问题，具体的理由如下：

* 1、uGUI中的元素采用的是以屏幕中心为原点(0,0)的平面直角坐标系，而普通屏幕坐标采用的是以左下角为原点(0,0)的平面直角坐标系，所以多边形顶点数组和鼠标位置不在一个坐标系内，使用AABBB这样的碰撞检测算法存在问题。

* 2、RolygonCollider2D中的points属性即多边形顶点数组存储的是相对于UI元素的相对坐标，在进行计算的时候应该统一转化为绝对坐标，这个过程在宣雨松的代码中有所涉及，但我认为对UI元素来讲，应该使用transform.GetComponent<RectTransform>().position而非transform.position，因为transform.position最初是给3D物体使用的，而实际上这里是存在误差的。

* 3、我怀疑宣雨松提供的这个ContainsPoint方法的正确性，因为按照我的理解修改这个方法以后，发现界面响应的情况和实际情况是有所出入的，如下图所示，在整个区域内该方法都返回false。为了排除因为我的方法而对结果产生的影响，我使用宣雨松的代码进行了测试，结论是这个方法不管进行坐标系的转换与否，它在整个区域内的返回值都是false，因此我认为这个方法是错误的，虽然从理解算法的角度来看，它应该是根据线性差值来判断点在多边形中每条边的哪一侧的。

![响应区域说明](https://ws1.sinaimg.cn/large/4c36074fly1fzix19xqm8j206n06ndfv.jpg)

&emsp;&emsp;在评论中网友[AwayMe](http://m.manew.com/forum.php?mod=viewthread&tid=41050&highlight=uGUI%2B%E4%B8%8D%E8%A7%84%E5%88%99&mobile=2)指出可以使用多边形碰撞器的OverlapPoint方法来判断一个点是否在多边形内部，可是经过我测试，这种方式和宣雨松提供的方法有着类似地问题，无论是否对坐标系进行转换，这个方法都返回false，响应区域与上图完全一致。

&emsp;&emsp;所以不管网络上有没有高质量的内容，一个核心的问题是你能否从中找到答案。如果你可以直接找到解决方案这可能是最好的结局；如果找不到直接的解决方案，却能够有所启发并独立解决问题，这是我们希望看到的结果。可是有时候人们并不这样想啊，人们想得到的是可以运行的代码而非解决问题的思路，因为可能人们并不想解决这个问题。

&emsp;&emsp;好了，经过知乎上相关[答案](http://www.zhihu.com/question/26551754?f3fb8ead20=b6b9d1289bcc893ff2fa0abd1e65fc52)我找到了这篇[文章](http://geomalgorithms.com/a03-_inclusion.html)，文章中提到了判断一个点是否在任意多边形内部的两种方法，分别为Corssing Number和Winding Number。这两种方法在理论层面的相关细节请大家自行阅读这篇[文章](http://geomalgorithms.com/a03-_inclusion.html)，我们这里选择的是前者，其基本思想是计算从该点引出的射线与多边形边界橡胶的次数，当其为奇数时表示该点在多边形内部，当其为偶数时表示在多边形外部。这里有一个有意思的事情是宣雨松选择的方法应该是著名的[Ray-Crossing](https://www.baidu.com/s?ie=UTF-8&wd=Ray-Crossing)算法，可是为什么在这里会出现这样的问题呢？

&emsp;&emsp;孰是孰非，一切都交给实践来证明吧！下面是我根据[文章](http://geomalgorithms.com/a03-_inclusion.html)中提供的算法改写的一段C#代码：
```
bool ContainsPoint2(Vector2[] polyPoints,Vector2 p)
{
	//统计射线和多边形交叉次数
	int cn = 0;

	//遍历多边形顶点数组中的每条边
	for(int i=0; i<polyPoints.Length-1; i++) 
	{
		//正常情况下这一步骤可以忽略这里是为了统一坐标系
		polyPoints [i].x += transform.GetComponent<RectTransform> ().position.x;
		polyPoints [i].y += transform.GetComponent<RectTransform> ().position.y;

		//从当前位置发射向上向下两条射线
		if(((polyPoints [i].y <= p.y) && (polyPoints [i + 1].y > p.y)) 
			|| ((polyPoints [i].y > p.y) && (polyPoints [i + 1].y <= p.y)))
		{
			//compute the actual edge-ray intersect x-coordinate
			float vt = (float)(p.y - polyPoints [i].y) / (polyPoints [i + 1].y - polyPoints [i].y);

			//p.x < intersect
			if(p.x < polyPoints [i].x + vt * (polyPoints [i + 1].x - polyPoints [i].x))
				++cn;
		}
	}

	//实际测试发现cn为0的情况即为宣雨松算法中存在的问题
	//所以在这里进行屏蔽直接返回false这样就可以让透明区域不再响应
	if(cn == 0)
		return false;

    //返回true表示在多边形外部否则表示在多边形内部
	return cn % 2 == 0;
}
```
这段代码说实话我理解的不是很透彻，而且令人费解的是实际结论和算法结论完全相反，因为按照我现在这样的设计，当cn为偶数时返回为true，此时应该表示该点再多边形外部啊，可是事实上我测试这段代码的时候，它居然是可以正常工作的，即当该方法返回true的时候我的点击确实是在多边形内部，所以这是一段可以正常工作同时让我感到费解的代码，而且当我屏蔽了cn为0的这种情况以后，现在它已经可以完美的工作了

![正五边形精灵](https://ws1.sinaimg.cn/large/None.jpg)

同样的，我们这里使用一张正五边形的精灵图片，然后编写下面的代码：
```
/*
 * 基于多边形碰撞器实现的不规则按钮 
 * 作者：PayneQin
 * 日期：2016年7月9日
 */

using UnityEngine;
using System.Collections;
using UnityEngine.UI;
using UnityEngine.EventSystems;

public class UnregularButtonWithCollider : MonoBehaviour,IPointerClickHandler
{
	/// <summary>
	/// 多边形碰撞器
	/// </summary>
	PolygonCollider2D polygonCollider;

	void Start()
	{
		//获取多边形碰撞器
		polygonCollider = transform.GetComponent<PolygonCollider2D>();
	}


	public void OnPointerClick(PointerEventData eventData)
	{
		//对2D屏幕坐标系进行转换
		Vector2 local;
		local.x = eventData.position.x - (float)Screen.width / 2.0f;
		local.y = eventData.position.y - (float)Screen.height / 2.0f;
		if(ContainsPoint(polygonCollider.points,local))
		{

			Debug.Log ("这是一个正五边形!");
		}

	}

	/// <summary>
	/// 判断指定点是否在给定的任意多边形内
	/// </summary>
	bool ContainsPoint(Vector2[] polyPoints,Vector2 p)
	{
		//统计射线和多边形交叉次数
		int cn = 0;
		
		//遍历多边形顶点数组中的每条边
		for(int i=0; i<polyPoints.Length-1; i++) 
		{
			//正常情况下这一步骤可以忽略这里是为了统一坐标系
			polyPoints [i].x += transform.GetComponent<RectTransform> ().position.x;
			polyPoints [i].y += transform.GetComponent<RectTransform> ().position.y;
			
			//从当前位置发射向上向下两条射线
			if(((polyPoints [i].y <= p.y) && (polyPoints [i + 1].y > p.y)) 
			   || ((polyPoints [i].y > p.y) && (polyPoints [i + 1].y <= p.y)))
			{
				//compute the actual edge-ray intersect x-coordinate
				float vt = (float)(p.y - polyPoints [i].y) / (polyPoints [i + 1].y - polyPoints [i].y);
				
				//p.x < intersect
				if(p.x < polyPoints [i].x + vt * (polyPoints [i + 1].x - polyPoints [i].x))
					++cn;
			}

		}

		//实际测试发现cn为0的情况即为宣雨松算法中存在的问题
		//所以在这里进行屏蔽直接返回false这样就可以让透明区域不再响应
		if(cn == 0)
			return false;

		//返回true表示在多边形外部否则表示在多边形内部
		return cn % 2 == 0;
	}
}

```
我们可以发现现在它可以正常工作啦！我们必须意识到的一点是，这个方法的空间复杂度为O(n-1)，所以随着多边形顶点数目的增加，这个方法的执行效率会越来越低，如果对不规则精灵的边界没有十分苛刻的要求的话，我的建议是我们使用多边形碰撞器标记出一个相对模糊的边界即可，因为现在我们这个方法主要依靠数学计算，没有涉及到摄像机相关计算，所以宣雨松[博客](http://www.xuanyusong.com/archives/3492)中有朋友指出他的方法仅仅适用于Canvas的模式为Screen-Space Camera这种情况，而我目前这个方法对除了World Space以外都是可以使用的，我最大的疑虑来自对鼠标位置进行转化的时候是否应该使用Screen.width和Screen.height，因为我担心可能会出现屏幕适配这种需求。

![演示效果1](https://ws1.sinaimg.cn/large/None.jpg)

## 精灵像素检测
&emsp;&emsp;精灵像素检测这个方案的灵感来自Image组件，我们在MonoDevelop或者Visual Studio中通过"转到定义"这个功能可以获得Image组件的内部细节。我们发现uGUI在处理控件是否被点击的时候，主要是根据IsRaycastLocationValid这个方法的返回值来进行判断的，而这个方法用到的基本原理则是判断指定点对应像素的RGBA数值中的Alpha是否大于某个指定临界值。例如，我们知道半透明通常是指Alpha=0.5，而对一个.png格式的图片来说半透明甚至完全透明的区域理论上不应该被响应的，所以根据这个原理我们只需要设定一个透明度的临界值然后对当前鼠标位置对应的像素进行判断就可以了，因此这种方法叫做精灵像素检测。

&emsp;&emsp;下面我们来一起看这段uGUI的代码，这段代码通过MonoDevelop或者Visual Studio的"转到定义"功能可以找到，这里我做了简单的注释帮助大家理解代码：
```
public virtual bool IsRaycastLocationValid(Vector2 screenPoint, Camera eventCamera)
{
	//当透明度>=1.0时，表示点击在可响应区域返回true
	if(this.m_EventAlphaThreshold >= 1f){
		return true;
	}

	//当没有指定精灵时为什么要返回true?
	Sprite overrideSprite = this.overrideSprite;
	if(overrideSprite == null){
		return true;
	}
		
	//坐标系转换	
	Vector2 local;
	RectTransformUtility.ScreenPointToLocalPointInRectangle(base.rectTransform, screenPoint, eventCamera, ref local);
	Rect pixelAdjustedRect = base.GetPixelAdjustedRect ();
	local.x += base.rectTransform.get_pivot ().x * pixelAdjustedRect.get_width ();
	local.y += base.rectTransform.get_pivot ().y * pixelAdjustedRect.get_height ();
	local = this.MapCoordinate(local, pixelAdjustedRect);
	Rect textureRect = overrideSprite.get_textureRect ();
	Vector2 vector = new Vector2(local.x / textureRect.get_width (), local.y / textureRect.get_height ());

	//计算屏幕坐标对应的UV坐标
	float num = Mathf.Lerp(textureRect.get_x (), textureRect.get_xMax (), vector.x) / (float)overrideSprite.get_texture().get_width();
	float num2 = Mathf.Lerp(textureRect.get_y (), textureRect.get_yMax (), vector.y) / (float)overrideSprite.get_texture().get_height();
	bool result;

	//核心方法：像素检测
	try{
		result = (overrideSprite.get_texture().GetPixelBilinear(num, num2).a >= this.m_EventAlphaThreshold);
	}catch(UnityException ex){
		Debug.LogError("Using clickAlphaThreshold lower than 1 on Image whose sprite texture cannot be read. " + ex.Message + " Also make sure to disable sprite packing for this sprite.", this);
		result = true;
	}
		
	//返回结果	
	return result;
}
```
从这段代码中我们可以看出，这个方法核心在第31行代码，即传入一个UV坐标返回一个RGBA数值并将其和临界值相比较。可是在此之前，我们看到在引入uGUI及其专属组件RectTransform以后，现在Unity中的坐标系转换变得更加复杂了，我个人看到这部分代码是相当凌乱的，或许我应该找时间补习下矩阵变换了吧。所以现在我们就有思路啦，我们有两种方式，第一种基于这个思路重新定制一个Image组件;第二种直接修改Image组件的eventAlphaThreshold属性。考虑到坐标系转换这里非常复杂，显然第二种方式更容易接受，为什么这里可以直接修改eventAlphaThreshold属性呢，因为它在Image组件内部和代码中的m_EventAlphaThreshold相关联，这就是这篇[文章](http://m.manew.com/forum.php?mod=viewthread&tid=45046&highlight=uGUI%2B%E4%B8%8D%E8%A7%84%E5%88%99&mobile=2)的完整解释啦！

![圆形精灵图片](https://ws1.sinaimg.cn/large/None.jpg)

&emsp;&emsp;好了，现在我们来一个简单的测试，我们这里准备一张圆形的精灵图片(如上图)，然后编写下面的代码：
```
/*
 * 基于精灵像素检测实现的不规则按钮 
 * 作者：PayneQin
 * 日期：2016年7月9日
 */

using UnityEngine;
using System.Collections;
using UnityEngine.UI;
using UnityEngine.EventSystems;

public class UnregularButtonWithPixel : MonoBehaviour,IPointerClickHandler
{
	/// <summary>
	/// Image组件
	/// </summary>
	private Image image;

	/// <summary>
	/// 透明度临界值
	/// </summary>
	[Range(0.0f,0.5f)]
	public float Alpha;

	public void Start()
	{
		//获取Image组件
		image = transform.GetComponent<Image>();
		//设定透明度临界值
		image.eventAlphaThreshold = Alpha;
	}


	public void OnPointerClick(PointerEventData eventData)
	{
		Debug.Log("这是一个圆形!");
	}
}

```
这里我为了让大家在学(复)习(制)的时候更容易理解，我在Click事件的响应上，使用的是实现IPointerClickHandler接口这种方法，希望通过动态绑定这种方式添加事件响应的可以自己解决，我是不会为了满足你们的好(懒)奇(惰)而奉献出我的EventTriggerListener的代码的。好了，现在我们要做的就是为需要响应点击的不规则精灵附加该脚本，这样就可以解决不规则精灵响应的问题了。这种方法使用起来非常简单，需要注意的是：图片的类型必须是Advance且保证可读可写。因为我们在脚本中访问了像素，而简单伴随着的代价就是我们无法使用图集、该图片在内存中会复制一份，所以在项目性能上允许的情况下这种方法还是可以考虑使用的。

![演示效果2](https://ws1.sinaimg.cn/large/4c36074fly1fz68k3znzij20p1061dfv.jpg)


# 小结
&emsp;&emsp;本文通过对网络上两种比较通用的不规则按钮制作方案进行对比和研究，解决了基于多边形碰撞器实现不规则按钮这个过程中存在的问题，剖析了基于精灵像素检测实现不规则按钮 这个过程的内部原理，从易用性角度来讲，后者要优于前者，而这种方法的缺陷主要来自于它对图片类型的限制以及允许像素可读写这两个方面，它必须是Advance类型，所以普通的Texture或者Sprite拥有的特性在这里它都无法享受，比如我们无法为其做颜色渐变这类Tween动画、无法使用精灵特有的图集特性等等，于此同时它必须允许像素可读写，因此在实际使用中它会在内存中复制一份，在执行效率上可能会受到影响。而从技术性角度来讲，我个人更推推崇前者，因为在这个过程中我们学到了新的知识，明白了如何利用一个算法来解决实际的问题，而且它不会限制我们对精灵的使用，所有精灵拥有的特性在这里我们都可以使用，无非是在寻找算法、解决问题的过程中我们耗费了大量精力，可是这是值得的啊，不是吗？这就是我们做这件事情的意义所在。从昨天开始研究这两个问题到今天写完整篇文章，整个人是非常疲惫的，欢迎大家继续关注我的博客，今天的内容就是这样啦，谢谢大家！