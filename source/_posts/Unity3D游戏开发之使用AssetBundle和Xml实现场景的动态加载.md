---
abbrlink: 1467630055
categories:
- 游戏开发
date: 2015-06-15 07:24:17
description: 可是因为这种打包方式仅仅是保证了场景中的 GameObject 与本地资源的引用关系而非是将本地资源打包，因此从减少游戏容量的角度来说并不是十分实用，而且当我们使用 WWW 下载完 AssetBundle 后，需要使用 Application.Load()方法来加载场景，我们知道在 Unity3D 中加载一个关卡(场景)是需要在 BuildSetting 中注册关卡的，因此在使用这种方式动态加载的时候请注意到这一点;这种思路是考虑到需要在一个场景中动态替换 GameObject 或者是动态生成 GameObject 的情形，使用这种方法首先要满足一个条件，即：场景内所有的物体都是预制件(Prefab);既然今天的题目已然告诉大家是使用 AssetBundle 和 Xml 文件实现场景的动态加载，我相信大家已经明白我要使用那种方式了
tags:
- Unity3D
- 动态加载
- AssetBundle
title: Unity3D 游戏开发之使用 AssetBundle 和 Xml 实现场景的动态加载
---

&emsp;&emsp;各位朋友，大家好，我是秦元培，欢迎大家关注我的博客，我的博客地址是[http://qinyuanpei.com](http://qinyuanpei.com)。 今天我想和大家聊聊在 Unity3D 中关于场景的动态加载的问题。众所周知在 Unity3D 游戏开发过程中，因为受到游戏容量、平台性能和热更新等诸多因素的限制，我们可能无法将所有的游戏场景打包到项目中然后相对"静态"地加载，那么这个时候就需要我们使用动态加载的方式来将游戏场景加载到场景中。博主在研究了 Unity3D 动态加载的相关资料后发现，目前 Unity3D 中实现动态加载场景的方式主要有以下两种方式：<!--more-->

* 使用 BuildStreamedSceneAssetBundle()方法将场景打包为 AssetBundle：这种方法将生成一个流式的.unity3d 文件，从而实现按需下载和加载，因此这种方式特别适合 Web 环境下游戏场景的加载，因为在 Web 环境下我们可以希望的是玩家可以在玩游戏的同时加载游戏。可是因为这种打包方式仅仅是保证了场景中的 GameObject 与本地资源的引用关系而非是将本地资源打包，因此从减少游戏容量的角度来说并不是十分实用，而且当我们使用 WWW 下载完 AssetBundle 后，需要使用 Application.Load()方法来加载场景，我们知道在 Unity3D 中加载一个关卡(场景)是需要在 BuildSetting 中注册关卡的，因此在使用这种方式动态加载的时候请注意到这一点。


* 将场景内的所有物体打包为 AssetBundle 配合相关配置文件动态生成场景：这种方法的思路是使用一个配置文件来记录下当前场景中所有物体的位置、旋转和缩放信息，然后再根据配置文件使用 Instantiate 方法逐个生成即可。这种思路是考虑到需要在一个场景中动态替换 GameObject 或者是动态生成 GameObject 的情形，使用这种方法首先要满足一个条件，即：场景内所有的物体都是预制件(Prefab)。这是由 Unity3D 的机制决定的，因为 Prefab 是一个模板，当你需要动态生成一个物体的时候就需要为其提供一个模板(Prefab)。

&emsp;&emsp;如果你对这两种方式没有什么疑问的话，那么我觉得我们可以正式开始今天的内容了。既然今天的题目已然告诉大家是使用 AssetBundle 和 Xml 文件实现场景的动态加载，我相信大家已经明白我要使用那种方式了。好了，下面我们正式开始吧！

##准备工作
&emsp;&emsp;在实现场景的动态加载前，我们首先要在本地准备好一个游戏场景，然后做两件事情：
* 将场景内的所有 GameObject 打包为 AssetBundle
* 将场景内所有的 GameObject 的信息导出为 Xml 文件
做这两件事情的时候，相当于我们是在准备食材和菜谱，有了食材和菜谱我们就可以烹制出美味佳肴了。可是在做着两件事情前，我们还有一件更为重要的事情要做，那就是我们需要将场景中使用到的 GameObject 制作成预制体(Prefab)。因为在博主的印象中，Unity3D 打包的最小粒度应该是 Prefab，所以为了保险起见，我还是建议大家将场景中使用到的 GameObject 制作成预制体(Prefab)。那么问题来了，当我们将这些 Prefab 打包成 AssetBundle 后是否还需要本地的 Prefab 文件？这里博主一直迷惑，因为理论上当我们将这些 Prefab 打包成 AssetBundle 后，我们实例化一个物体的时候实际上是在使用 AssetBundle 的 Load 方法来获取该物体的一个模板，这个模板应该是存储在 AssetBundle 中的啊！因为我的笔记本使用的是免费版的 Unity3D 无法对此进行测试，所以如果想知道这个问题结果的朋友可以等我下周到公司以后测试了再做讨论(我不会告诉你公司无耻地使用了破解版)，当然如果有知道这个问题的答案的朋友欢迎给我留言啊，哈哈！这里就是想告诉大家要准备好场景中物体的预设体(Prefab),重要的事情说三遍!!!

##将场景内物体打包为 AssetBundle
&emsp;&emsp;Unity3D 打包的相关内容这里就不展开说了，因为在官方 API 文档中都能找到详细的说明，虽然说 Unity5.0 中 AssetBundle 打包的方式发生了变化，不过考虑到大家都还在使用 4.X 的版本，所以等以后我用上了 Unity5.0 再说吧，哈哈！好了，下面直接给出代码：
```C#
	[MenuItem("Export/ExportTotal----对物体整体打包")]
	static void ExportAll()
	{
		//获取保存路径
		string savePath=EditorUtility.SaveFilePanel("输出为AssetBundle","","New Resource","unity3d");
		if(string.IsNullOrEmpty(savePath)) return;
		//获取选择的物体
		Object[] objs=Selection.GetFiltered(typeof(Object),SelectionMode.DeepAssets);
		if(objs.Length<0) return;
		//打包
		BuildPipeline.BuildAssetBundle(null,objs,savePath,BuildAssetBundleOptions.CollectDependencies|BuildAssetBundleOptions.CompleteAssets);
		AssetDatabase.Refresh();
	}
```

##将场景内物体信息导出为 Xml 文件
&emsp;&emsp;导出场景内物体信息需要遍历场景中的每个游戏物体，因为我们在制作场景的时候通常会用一个空的 GameObject 作为父物体来组织场景中的各种物体，因此我们在导出 Xml 文件的时候仅仅考虑导出这些父物体，因为如果考虑子物体的话，可能会涉及到递归，整个问题将变得特别复杂。为了简化问题，我们这里仅仅考虑场景中的父物体。好了，开始写代码：
```C#
	[MenuItem("Export/ExportScene----将当前场景导出为Xml")]
	static void ExportGameObjects()
	{
		//获取当前场景完整路径
		string scenePath=EditorApplication.currentScene;
		//获取当前场景名称
		string sceneName=scenePath.Substring(scenePath.LastIndexOf("/")+1,scenePath.Length-scenePath.LastIndexOf("/")-1);
		sceneName=sceneName.Substring(0,sceneName.LastIndexOf("."));
		//获取保存路径
		string savePath=EditorUtility.SaveFilePanel("输出场景内物体","",sceneName,"xml");
		//创建Xml文件
		XmlDocument xmlDoc=new XmlDocument();
		//创建根节点
		XmlElement scene=xmlDoc.CreateElement("Scene");
		scene.SetAttribute("Name",sceneName);
		scene.SetAttribute("Asset",scenePath);
		xmlDoc.AppendChild(scene);
		//遍历场景中的所有物体
		foreach(GameObject go in Object.FindObjectsOfType(typeof(GameObject)))
		{
			//仅导出场景中的父物体
			if(go.transform.parent==null)
			{
				//创建每个物体
				XmlElement gameObject=xmlDoc.CreateElement("GameObject");
				gameObject.SetAttribute("Name",go.name);
				gameObject.SetAttribute("Asset","Prefabs/"+ go.name + ".prefab");
				//创建Transform
				XmlElement transform=xmlDoc.CreateElement("Transform");
				transform.SetAttribute("x",go.transform.position.x.ToString());
				transform.SetAttribute("y",go.transform.position.y.ToString());
				transform.SetAttribute("z",go.transform.position.z.ToString());
				gameObject.AppendChild(transform);
				//创建Rotation
				XmlElement rotation=xmlDoc.CreateElement("Rotation");
				rotation.SetAttribute("x",go.transform.eulerAngles.x.ToString());
				rotation.SetAttribute("y",go.transform.eulerAngles.y.ToString());
				rotation.SetAttribute("z",go.transform.eulerAngles.z.ToString());
				gameObject.AppendChild(rotation);
				//创建Scale
				XmlElement scale=xmlDoc.CreateElement("Scale");
				scale.SetAttribute("x",go.transform.localScale.x.ToString());
				scale.SetAttribute("y",go.transform.localScale.y.ToString());
				scale.SetAttribute("z",go.transform.localScale.z.ToString());
				gameObject.AppendChild(scale);
				//添加物体到根节点
				scene.AppendChild(gameObject);
			}
		} 

		xmlDoc.Save(savePath);
	}

```
&emsp;&emsp;好了，在这段代码中我们以 Scene 作为根节点，然后以每个 GameObject 作为 Scene 的子节点，重点在 Xml 文件中记录了每个 GameObject 的名称、Prefab、坐标、旋转和缩放等信息。下面是一个导出场景的 Xml 文件的部分内容：
```Xml
<Scene Name="DoneStealth" Asset="Assets/Done/DoneScenes/DoneStealth.unity">
  <GameObject Name="char_robotGuard_002" Asset="Prefabs/char_robotGuard_002.prefab">
    <Transform x="-18.99746" y="0" z="37.2443" />
    <Rotation x="0" y="0" z="0" />
    <Scale x="1" y="1" z="1" />
  </GameObject>
  <GameObject Name="fx_laserFence_lasers_003" Asset="Prefabs/fx_laserFence_lasers_003.prefab">
    <Transform x="-17.90294" y="1.213998" z="24.07678" />
    <Rotation x="0" y="90.00001" z="0" />
    <Scale x="1" y="1" z="3.735847" />
  </GameObject>
  <GameObject Name="door_generic_slide_001" Asset="Prefabs/door_generic_slide_001.prefab">
    <Transform x="-15.91264" y="-0.001293659" z="7.006886" />
    <Rotation x="0" y="90.00001" z="0" />
    <Scale x="1" y="1" z="1" />
  </GameObject>
  <GameObject Name="door_generic_slide_003" Asset="Prefabs/door_generic_slide_003.prefab">
    <Transform x="-7.910765" y="-0.001293659" z="37.01304" />
    <Rotation x="0" y="90.00001" z="0" />
    <Scale x="1" y="1" z="1" />
  </GameObject>
```
&emsp;&emsp;在这里我们假设所有的 Prefab 是放置在 Resources/Prefabs 目录中的，那么此时我们便有了两种动态加载场景的方式
* 通过每个 GameObject 的 Asset 属性，配合 Resources.Load()方法实现动态加载
* 通过每个 GameObject 的 Name 属性，配合 AssetBundle 的 Load()方法实现动态加载
这两种方法大同小异，区别仅仅在于是否需要从服务器下载相关资源。因此本文的主题是使用 AssetBundle 和 Xml 实现场景的动态加载，因此，接下来我们主要以第二种方式为主，第一种方式请大家自行实现吧！

##动态加载物体到场景中
&emsp;&emsp;首先我们来定义一个根据配置文件动态加载 AssetBundle 中场景的方法 LoadDynamicScene
```C#
	/// <summary>
	/// 根据配置文件动态加载AssetBundle中的场景
	/// </summary>
	/// <param name="bundle">从服务器上下载的AssetBundle文件</param>
	/// <param name="xmlFile">AssetBundle文件对应的场景配置文件</param>
	public static void LoadDynamicScene(AssetBundle bundle,string xmlFile)
	{
		//加载本地配置文件
		XmlDocument xmlDoc=new XmlDocument();
		xmlDoc.LoadXml(((TextAsset)Resources.Load(xmlFile)).text);
		//读取根节点
		XmlElement root=xmlDoc.DocumentElement;
		if(root.Name=="Scene")
		{
			XmlNodeList nodes=root.SelectNodes("/Scene/GameObject");
			//定义物体位置、旋转和缩放
			Vector3 position=Vector3.zero;
			Vector3 rotation=Vector3.zero;
			Vector3 scale=Vector3.zero;
			//遍历每一个物体
			foreach(XmlElement xe1 in nodes)
			{
				//遍历每一个物体的属性节点
				foreach(XmlElement xe2 in xe1.ChildNodes)
				{
					//根据节点名称为相应的变量赋值
					if(xe2.Name=="Transform")
					{
						position=new Vector3(float.Parse(xe2.GetAttribute("x")),float.Parse(xe2.GetAttribute("y")),float.Parse(xe2.GetAttribute("z")));
					}else if(xe2.Name=="Rotation")
					{
						rotation=new Vector3(float.Parse(xe2.GetAttribute("x")),float.Parse(xe2.GetAttribute("y")),float.Parse(xe2.GetAttribute("z")));
					}else{
						scale=new Vector3(float.Parse(xe2.GetAttribute("x")),float.Parse(xe2.GetAttribute("y")),float.Parse(xe2.GetAttribute("z")));
					}
				}
				//生成物体
				GameObject go=(GameObject)GameObject.Instantiate(bundle.Load(xe1.GetAttribute("Name")),position,Quaternion.Euler(rotation));
				go.transform.localScale=scale;
			}
		}
	}
```
&emsp;&emsp;因为该方法中的 AssetBundle 是需要从服务器下载下来的，因此我们需要使用协程来下载 AssetBundle：
```C#
	IEnumerator Download()
	{
		WWW _www = new WWW ("http://localhost/DoneStealth.unity3d");
		yield return _www;
		//检查是否发生错误
		if (string.IsNullOrEmpty (_www.error)) 
		{
			//检查AssetBundle是否为空
			if(_www.assetBundle!=null)
			{
				LoadDynamicScene(_www.assetBundle,"DoneStealth.xml");
			}
		}
	}
```
&emsp;&emsp;好了，现在运行程序，可以发现场景将被动态地加载到当前场景中:)，哈哈

![null](.)

##小结
* 使用这种方式来加载场景主要是为了提高游戏的性能，如果存在大量重复性的场景的时候，可以使用这种方式来减小游戏的体积，可是这种方式本质上是一种用时间换效率的方式，因为在使用这种方法前，我们首先要做好游戏场景，然后再导出相关的配置文件和 AssetBundle，从根本上来讲，工作量其实没有减少。
* 当场景导出的 Xml 文件中的内容较多时，建议使用内存池来管理物体的生成和销毁，因为频繁的生成和销毁是会带来较大的内存消耗的。说到这里的时候，我不得不吐槽下公司最近的项目，在将近 300 个场景中只有 30 个场景是最终发布游戏时需要打包的场景，然后剩余场景将被用来动态地加载到场景中，因为领导希望可以实现动态改变场景的目的，更为郁闷的是整个场景要高度 DIY,模型要能够随用户拖拽移动、旋转，模型和材质要能够让用户自由替换。从整体上来讲，频繁地销毁和生成物体会耗费大量资源，因此如果遇到这种情况建议还是使用内存池进行管理吧！

&emsp;&emsp;好了，今天的内容就是这样子了，如果大家对此有什么疑问，欢迎给我留言，谢谢大家！