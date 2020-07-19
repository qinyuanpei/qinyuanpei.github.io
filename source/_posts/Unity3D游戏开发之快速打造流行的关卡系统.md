---
abbrlink: 1424645834
categories:
- 游戏开发
date: 2015-06-11 08:11:01
description: 这里我们首先将关卡配置文件levels.xml放置在Resources目录下，这是因为我们可以使用Resources.Load()这种方式来加载本地资源，这种方式对于Unity3D来说有着得天独厚的优势：;总之呢，我们把握住一点，这个路径是可以在移动平台上使用的一个可以读写的路径，当然在路径这块儿可能同样会碰到和Application.dataPath类似的问题，因为博主写这篇文章的时候并没有对移动平台进行测试，这一点希望大家能够注意啊，这并不是我偷懒，实在是公司最近的事情比较多，没有时间做进一步的测试，不过除了路径的问题以外，我可以向大家保证，这个路径是可以读写的，所以如果我们在开发Unity3D游戏过程中需要在本地存储某些文件的话，这个路径是个不错的选择;从关卡的基本结构Level可以定义出如下的配置文件，这里使用Xml作为配置文件的存储形式：
tags:
- 关卡系统
- Unity3D
- 游戏
title: Unity3D游戏开发之快速打造流行的关卡系统
---

&emsp;&emsp;各位朋友，大家好，欢迎大家关注我的博客，我是秦元培，我的博客地址是[blog.csdn.net/qinyuanpei](blog.csdn.net/qinyuanpei)。
今天想和大家分享的是目前在移动平台上较为流行的关卡系统，关卡系统通常是单机手机游戏如《愤怒的小鸟》、《保卫萝卜》中对游戏内容的组织形式，玩家可通过已解锁的关卡(默认第一关是已解锁的)获取分数进而解锁新的关卡，或者是通过付费购买解锁新的关卡。那么好了，在今天的文章中博主将带领大家快速实现一个可扩展的关卡系统，这个实例的灵感来自博主最近的工作经历，希望对大家学习Unity3D游戏起到一定帮助性的作用。

<!--more-->

# 原理
&emsp;&emsp;在本地配置一个Xml文件，在这个文件中定义当前游戏中关卡的相关信息，通过解析该文件并和UI绑定最终实现一个完整的关卡系统。

##  1、定义关卡
&emsp;&emsp;首先我们来定义一个关卡的基本结构：
```C#
public class Level
{
	/// <summary>
	/// 关卡ID
	/// </summary>
	public string ID;

	/// <summary>
	/// 关卡名称
	/// </summary>
	public string Name;

	/// <summary>
	/// 关卡是否解锁	
	/// </summary>
	public bool UnLock = false;
}
```
&emsp;&emsp;在这里，我们假定关卡的名称和该关卡在Unity3D中场景名称一致。其中最为重要的一个属性是UnLock，该值是一个布尔型变量，表明该关卡是否解锁，因为在游戏中，只有解锁的场景是可以访问的。

##  2、定义关卡配置文件
&emsp;&emsp;从关卡的基本结构Level可以定义出如下的配置文件，这里使用Xml作为配置文件的存储形式：
```C#
<?xml version="1.0" encoding="utf-8"?>
<levels>
  <level id="0" name="level0" unlock="1" />
  <level id="1" name="level1" unlock="0" />
  <level id="2" name="level2" unlock="0" />
  <level id="3" name="level3" unlock="0" />
  <level id="4" name="level4" unlock="0" />
  <level id="5" name="level5" unlock="0" />
  <level id="6" name="level6" unlock="0" />
  <level id="7" name="level7" unlock="0" />
  <level id="8" name="level8" unlock="0" />
  <level id="9" name="level9" unlock="0" />
</levels>
```
&emsp;&emsp;和关卡结构定义类似，这里使用0和1来表示关卡的解锁情况，0表示未解锁，1表示解锁，可以注意到默认情况下第一个关卡是解锁的，这符合我们在玩《愤怒的小鸟》这类游戏时的直观感受。那么好了，在完成了关卡的结构定义和配置文件定义后，接下来我们开始思考如何来实现一个关卡系统，因为此处并不涉及到Unity3D场景中的具体逻辑，因此我们在关卡系统中主要的工作就是维护好主界面场景和各个游戏场景的跳转关系，我们可以注意到这里要完成两件事情，即第一要将配置文件中的关卡以一定形式加载到主界面中，并告诉玩家哪些关卡是已解锁的、哪些关卡是未解锁的，当玩家点击不同的关卡时可以得到不同的响应，已解锁的关卡可以访问并进入游戏环节，未解锁的关卡则需要获得更多的分数或者是通过付费来解锁关卡；第二是要对关卡进行编辑，当玩家获得了分数或者是支付一定的费用后可以解锁关卡进入游戏环节。这两点综合起来就是我们需要对关卡的配置文件进行读写，因为我们注意到一个关卡是否解锁仅仅取决于unlock属性，那么好了，明白了这一点后我们来动手编写一个维护关卡的类。

## 3、编写一个维护关卡的类
&emsp;&emsp;这里直接给出代码，因为从严格的意义上来说，这段代码并非我们此刻关注的重点，可能这让大家感到难以适应，因为文章明明就是在教我们实现一个关卡系统，可是此刻博主却说这部分不重要了，请大家稍安勿躁，因为这里有比代码更为深刻的东西。
```C#
using UnityEngine;
using System.Collections;
using System.Collections.Generic;
using System.Xml;

public static class LevelSystem 
{
	/// <summary>
	/// 加载Xml文件	
	/// </summary>
	/// <returns>The levels.</returns>
	public static List<Level> LoadLevels()
	{
		//创建Xml对象
		XmlDocument xmlDoc = new XmlDocument();
		//如果本地存在配置文件则读取配置文件
		//否则在本地创建配置文件的副本
		//为了跨平台及可读可写，需要使用Application.persistentDataPath
		string filePath = Application.persistentDataPath + "/levels.xml";
		if (!IOUntility.isFileExists (filePath)) {
			xmlDoc.LoadXml (((TextAsset)Resources.Load ("levels")).text);
			IOUntility.CreateFile (filePath, xmlDoc.InnerXml);
		} else {
			xmlDoc.Load(filePath);
		}
		XmlElement root = xmlDoc.DocumentElement;
		XmlNodeList levelsNode = root.SelectNodes("/levels/level");
		//初始化关卡列表
		List<Level> levels = new List<Level>();
		foreach (XmlElement xe in levelsNode) 
		{
			Level l=new Level();
			l.ID=xe.GetAttribute("id");
			l.Name=xe.GetAttribute("name");
			//使用unlock属性来标识当前关卡是否解锁
			if(xe.GetAttribute("unlock")=="1"){
				l.UnLock=true;
			}else{
				l.UnLock=false;
			}

			levels.Add(l);
		}

		return levels;
	}

	/// <summary>
	/// 设置某一关卡的状态
	/// </summary>
	/// <param name="name">关卡名称</param>
	/// <param name="locked">是否解锁</param>
	public static void SetLevels(string name,bool unlock)
	{
		//创建Xml对象
		XmlDocument xmlDoc = new XmlDocument();
		string filePath=Application.persistentDataPath + "/levels.xml";
		xmlDoc.Load(filePath);
		XmlElement root = xmlDoc.DocumentElement;
		XmlNodeList levelsNode = root.SelectNodes("/levels/level");
		foreach (XmlElement xe in levelsNode) 
		{
			//根据名称找到对应的关卡
			if(xe.GetAttribute("name")==name)
			{
				//根据unlock重新为关卡赋值
				if(unlock){
					xe.SetAttribute("unlock","1");
				}else{
					xe.SetAttribute("unlock","0");
				}
			}
		}

		//保存文件
		xmlDoc.Save (filePath);
	}
}
```
&emsp;&emsp;这里我们首先将关卡配置文件levels.xml放置在Resources目录下，这是因为我们可以使用Resources.Load()这种方式来加载本地资源，这种方式对于Unity3D来说有着得天独厚的优势：
* 它使用相对于Resources目录的相对路径，所以在使用的时候不用考虑是相对路径还是绝对路径的问题
* 它使用名称来查找一个本地资源，所以在使用的时候不用考虑扩展名和文件格式的问题
* 它可以是Unity3D支持的任意类型，从贴图到预制体再到文本文件等等，可以和Unity3D的API完美地结合

&emsp;&emsp;说了这么多它的优点，我们自然要痛心疾首地说说它的缺点，它的缺点是什么呢？那就是不支持写入操作，这当然不能责怪Unity3D，因为当Unity3D导出游戏的时候会将Rsources目录下的内容压缩后再导出，我们当然不能要求在一个压缩后的文件里支持写入操作啦，所以我们是时候来总结下Unity3D中资源读写的常见方案了，那么Unity3D中常见的资源读写方案由哪些呢？

1、Resources.Load:只读，当我们的资源不需要更新且对本地存储无容量要求的时候可以采用这种方式
2、AssetBundle：只读，当我们的资源需要更新且对本地存储有容量要求的时候可以采用这种方式
3、WWW:只读，WWW支持http协议和file协议，因此可以WWW来加载一个网络资源或者本地资源
4、PlayerPrefs：可读可写，Unity3D提供的一种的简单的键-值型存储结构，可以用来读写float、int和string三种简单的数据类型，是一种较为松散的数据存储方案
5、序列化和反序列化：可读可写，可以使用Protobuf、序列化为Xml、二进制或者JSON等形式实现资源读写。
6、数据库：可读可写，可以使用MySQL或者SQLite等数据库对数据进行存储实现资源读写。

&emsp;&emsp;好了，在了解了Unity3D中资源读写的常见方案后，我们接下来来讨论下Unity3D中的路径问题：
1、Application.dataPath：这个路径是我们经常使用的一个路径，可是我们真的了解这个路径吗？我看这里要打个大大的问号，为什么这么说呢？因为这个路径在不同的平台下是不一样的，从官方API文档中可以了解到这个值依赖于运行的平台：
* Unity 编辑器：<工程文件夹的路径>/Assets 
* Mac：<到播放器应用的路径>/Contents 
* IOS: <到播放器应用的路径>/<AppName.app>/Data 
* Win：<.exe文件目录>\Data 
* Web：<.unity3d文件的绝对路径>
&emsp;&emsp;这个路径是在PC上支持读写的，可是因为到了不同的平台上文件的路径发生变动，因此我们在程序中设置的路径可能就变成了一个错误的路径。在网上大家找到类似的内容，这一点是网上说的最多、坑最多的一块儿，希望大家在以后遇到这个问题的时候能够留心点，尽量能不用这个路径就不用这个路径吧！什么?不用这个路径，那该用什么路径呢？呵呵，不要着急啊，下面隆重向大家推荐Application.persistentDataPath这个路径。
2、Application.persistentDataPath：这个路径是Unity3D中的一个数据持久化路径，呵呵，千万不要问我什么叫做数据持久化路径，我不会告诉你我今天这篇文章的关键就是数据持久化啊！总之呢，我们把握住一点，这个路径是可以在移动平台上使用的一个可以读写的路径，当然在路径这块儿可能同样会碰到和Application.dataPath类似的问题，因为博主写这篇文章的时候并没有对移动平台进行测试，这一点希望大家能够注意啊，这并不是我偷懒，实在是公司最近的事情比较多，没有时间做进一步的测试，不过除了路径的问题以外，我可以向大家保证，这个路径是可以读写的，所以如果我们在开发Unity3D游戏过程中需要在本地存储某些文件的话，这个路径是个不错的选择。

&emsp;&emsp;好了，现在我们回到维护关卡的这个类中，大家可以注意到我在加载配置文件的时候做了这样一个处理：
如果本地(指游戏外部)存在配置文件则直接读取配置文件，否则使用Resources.Load()方法加载Resources目录下的配置文件，并在本地创建一个配置文件的副本。这样做的目的是为了方便对配置文件进行修改，因为Resources目录下的配置文件在导出游戏后是没有路径的，我们没有办法用常规的访问文件的方式来读取这个文件，这个时候我们就用到Application.persistentDataPath这个路径，因为我们在本地创建了副本，所以只要读取副本文件就可以对其进行读取和修改了。那么，接下来，我们来写一个Main文件作为项目的入口文件吧！

## 4、编写入口文件
```C#
using UnityEngine;
using System.Collections;
using System.Collections.Generic;
using UnityEngine.UI;
using System.Xml.Serialization;

public class Main : MonoBehaviour 
{
	//关卡列表
	private List<Level> m_levels;

	void Start () 
	{
		//获取关卡
		m_levels = LevelSystem.LoadLevels ();
		//动态生成关卡
		foreach (Level l in m_levels) 
		{
			GameObject prefab=(GameObject)Instantiate((Resources.Load("Level") as GameObject));
			//数据绑定
			DataBind(prefab,l);
			//设置父物体
			prefab.transform.SetParent(GameObject.Find("UIRoot/Background/LevelPanel").transform);
			prefab.transform.localPosition=new Vector3(0,0,0);
			prefab.transform.localScale=new Vector3(1,1,1);
			//将关卡信息传给关卡
			prefab.GetComponent<LevelEvent>().level=l;
			prefab.name="Level";
		}

		//人为解锁第二个关卡
		//在实际游戏中玩家需要满足一定条件方可解锁关卡
		//此处仅作为演示
		LevelSystem.SetLevels ("level1", true);

	}
	

	/// <summary>
	/// 数据绑定
	/// </summary>
	void DataBind(GameObject go,Level level)
	{
		//为关卡绑定关卡名称
		go.transform.Find("LevelName").GetComponent<Text>().text=level.Name;
		//为关卡绑定关卡图片
		Texture2D tex2D;
		if(level.UnLock){
			tex2D=Resources.Load("nolocked") as Texture2D;
		}else{
			tex2D=Resources.Load("locked") as Texture2D;
		}
		Sprite sprite=Sprite.Create(tex2D,new Rect(0,0,tex2D.width,tex2D.height),new Vector2(0.5F,0.5F));
		go.transform.GetComponent<Image>().sprite=sprite;
	}
}
```
&emsp;&emsp;在这段脚本中，我们首先加载了关卡信息，然后将关卡信息和界面元素实现绑定，从而实现一个简单的关卡选择界面，并人为地解锁了第二个关卡。好吧，如果这是一个正式游戏的配置关卡配置文件，相信大家都知道怎么免费玩解锁的关卡了吧，哈哈！当然，我不推荐大家这样做，因为作为一个程序员，当你全身心地投入到一个项目中的时候，你就会明白完成一款软件或者游戏需要投入多少精力，所以大家尽量还是不要想破解或者盗版这些这些事情，毕竟作为开发者可能他的出发点是想做出来一个让大家都喜欢的产品，可是更现实的问题是开发者一样要生活，所以请善待他们吧。好了，言归正传，这里的UI都是基于UGUI实现的，不要问我为什么不用NGUI，因为我就是喜欢UGUI！我们知道我们需要为每个关卡的UI元素绑定一个响应的事件，因此我们需要为其编写一个LevelEvent的脚本：
```C#
using UnityEngine;
using System.Collections;
using UnityEngine.UI;
using UnityEngine.EventSystems;

public class LevelEvent : MonoBehaviour
{
	//当前关卡
	public Level level;

	public void OnClick()
	{
		if(level.UnLock){
			//假设关卡的名称即为对应场景的名称
			//Application.LoadLevel(level.Name);
			Debug.Log ("当前选择的关卡是:"+level.Name);
		}else{
			Debug.Log ("抱歉!当前关卡尚未解锁!");
		}

	}

}
```
&emsp;&emsp;记得在本文开始的时候，博主提到了一个假设，就是关卡的名称和其对应的游戏名称一致的假设，相信到此处大家都知道为什么了吧！为了让每个关卡的UI元素知道自己对应于哪个关卡，我们设置了一个level变量，这个变量的值在加载关卡的时候已经完成了初始化，所以此时我们可以在这里知道每个关卡的具体信息，从而完成事件的响应。好了，今天的内容就是这样了，我们来看看最终的效果吧！

![DEMO1](https://i.loli.net/2020/07/13/a8peHhmFA7WfyDR.png)

![DEMO2](https://ww1.sinaimg.cn/large/4c36074fly1fz68k5yr87j20df08xjv1.jpg)

&emsp;&emsp;可以注意到在第二次打开游戏后，第二个关卡已经解锁了，说明我们在最开始设计的两个目标都达到了，那么内容就是这样子啦，如果大家有什么好的想法或者建议，欢迎在文章后面给我留言，谢谢大家！
