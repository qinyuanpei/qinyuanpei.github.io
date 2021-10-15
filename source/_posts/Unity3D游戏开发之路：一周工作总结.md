---
abbrlink: 719322223
categories:
- 生活感悟
date: 2015-06-11 08:02:45
description: 我不知道公司领导当初是怎么样确定使用Unity3D来做这个项目，因为考虑到虚拟展示的需要，这个项目最终展示给用户的是一个网页，这样就更需要考虑资源组织的问题，就这样在工作的第一周时间内我想到了以前在学校做游戏的时候都没"舍得"使用的技术方案，基本的思路是本地的游戏文件最终仅仅保留一个主场景文件(MainMenu.cs)，主场景负责维护从楼盘到户型再到家装的所有逻辑，各个场景中的动态的部分则是通过Resource.Load()和AssetBundle来实现，将这些场景放到服务器上，主场景将决定具体加载哪一个场景;然而现实是残酷的，在这个项目中，因为楼盘、户型、家装等等因素的不可控性，所以在设计UI的时候全部都是以动态加载的形式来处理的，因为你并不能确定这些UI里显示的元素到底有多少个，这样我在设计这个框架的时候是这样考虑的，就是把所有需要人力来调整、控制的部分(如模型摆放、场景设计等等)都手动完成，所以和UI相关的部分(如UI元素的动态加载、模型的加载、本地配置文件等等)都通过动态加载来实现，因为在整个项目中第三部分的家装会涉及到大量的模型，所以这部分考虑的是将模型文件打包成AssetBundle文件从服务器加载;具体使用的时候需要将*号部分分别替换成允许跨域访问的地址和端口，因为我是用WAMP这个软件搭建的本地服务器，所以这里都采用的是默认值，具体怎么去设置这里的内容还需要大家自己去探索，不过这里就是像告诉大家使用Unity3D做网页游戏或者是从服务器上下载文件是一定要考虑这个问题的啊
tags:
- 游戏开发
- 工作
- Unity3D
title: Unity3D游戏开发之路：一周工作总结
---

&emsp;&emsp;大家好，欢迎大家关注我的博客，我是秦元培，我的博客地址是[http://blog.csdn.net/qinyuanpei](http://blog.csdn.net/qinyuanpei)。到公司上班已经一周了，趁着今天周末休息的时间，想将最近在工作和生活中的感受和想法写下来，因为生命就是一个不断积累、厚积薄发，最终实现自我超越的一个过程。作为第一份工作，尽管没有想象中那样理想，可我还是在很努力的工作。工作后接手的第一个项目是一个房地产的漫游展示项目，因为这家公司之前是做影视后期的，所以在决定做这个项目后，公司领导层对这个项目具体要做到什么样的效果并没有一个明确的认识，所以在项目开展前期无论是在对项目所使用的技术的熟悉程度上还是项目整体的策划上，都没有一个具体的的可操作的方案。因为公司领导是美术出身，所以从我进了公司以后，整个公司上下一直沉浸在一种加班加点赶制模型的压抑氛围当中。

<!--more-->

&emsp;&emsp;我进公司的第一天，公司负责技术的人向我演示了一个视频，告诉我项目做出来大概就是这样一个样子，然后就让我开始写所谓的"框架"，因为他对Unity3D的技术并不熟悉，所以基本上从我上班开始，所有和Unity3D相关的工作都由我一个人来完成，让我这样一个新入职的人来担当"主程"，我感到受宠若惊而压力山大，不过因为他和我年龄相差不大，一直都比较尊重我的想法，所以Unity3D这块整个项目就比较放心地交给了我来做，这样的结果就是我大概花了一周时间就写好了整体的框架[偷笑：)]。可是在设计整个项目的过程中，因为美术都忙着建模，所以UI设计这块儿基本上都是空白，作为一个刚进公司不久没有什么话语权的新人，在这种情况下我只能自己先大致做出来一个DEMO，然后再听取领导的意见反复进行修改，可是如果这样，到了项目后期如果因为项目需求发生变动，可能UI设计就需要重新制作，我个人是比较讨厌做UI，因为UI有时候会因为参数设置不合理等等的原因造成无法调试的错误，这样你折腾了大半天找了可能出现的各种错误，最终却发现是因为一个参数设置不合理，这该有多蛋疼啊！我比较喜欢Cocos Studio这种制作UI的方式，就是让美术直接在UI编辑器里做好UI然后导出为程序可以解析的数据类型，这样程序只需要负责将这些数据解析出来为它们绑定相关的UI事件就好了。然而现实是残酷的，在这个项目中，因为楼盘、户型、家装等等因素的不可控性，所以在设计UI的时候全部都是以动态加载的形式来处理的，因为你并不能确定这些UI里显示的元素到底有多少个，这样我在设计这个框架的时候是这样考虑的，就是把所有需要人力来调整、控制的部分(如模型摆放、场景设计等等)都手动完成，所以和UI相关的部分(如UI元素的动态加载、模型的加载、本地配置文件等等)都通过动态加载来实现，因为在整个项目中第三部分的家装会涉及到大量的模型，所以这部分考虑的是将模型文件打包成AssetBundle文件从服务器加载。

&emsp;&emsp;我不知道公司领导当初是怎么样确定使用Unity3D来做这个项目，因为考虑到虚拟展示的需要，这个项目最终展示给用户的是一个网页，这样就更需要考虑资源组织的问题，就这样在工作的第一周时间内我想到了以前在学校做游戏的时候都没"舍得"使用的技术方案，基本的思路是本地的游戏文件最终仅仅保留一个主场景文件(MainMenu.cs)，主场景负责维护从楼盘到户型再到家装的所有逻辑，各个场景中的动态的部分则是通过Resource.Load()和AssetBundle来实现，将这些场景放到服务器上，主场景将决定具体加载哪一个场景。因为整个项目主要分成楼盘、户型、家装这三个部分，这些场景除了模型以外逻辑都是一样的，因此将这部分的逻辑都写成公用的脚本，在制作这些场景时只需要将脚本拖拽到某些物体上就可以了。因为需要从服务器上获取符合筛选要求的楼盘信息，因此还需要编写服务器端的相关逻辑，目前项目组中还没有服务器端的程序，这部分我表示无能为力啊，哈哈。如果希望将最终的网页做得漂亮些，可能还需要前端工程师的加入吧，目前这块同样是空白！好吧，做项目的时候即使是程序员都会有分身乏术的时候，成为全栈工程师是我的梦想，可是目前做不到啊！我不知道在游戏开发中程序和美术的关系怎么样，反正在我目前的项目组里我这个程序的存在感实在是太弱了啊，可能是项目组程序的比例太低，可能是我和大家还不熟悉吧，不过昨天居然有个美术跑过来问我能不能教他Unity3D，因为他觉得建模做得再好做出来的模型终究是死的，哈哈，瞬间感觉有种相见恨晚的感觉啊。好了，这些闲话先聊到这里吧，今天想和大家分享的是我在开发过程中遇到的某些坑，因为我是一个程序员，归根到底我和大家要聊的还是程序嘛！

## 一、下载AssetBundle时遇到"跨域"的问题
&emsp;&emsp;这个问题主要是因为服务器上缺少一个叫做crossdomain.xml的文件，这是由Adobe提出的以保证Flash能够跨域访问文件的一种策略，当发生这个错误时具体的表现就是你可以通过浏览器从服务器上下载AssetBundle文件，可是当你试图在Unity里使用WWW访问该文件时就会报错，具体的错误信息我已经不记得了，不过错误信息中特别明确的指出了是因为缺少crossdomain.xml这个文件，所以解决的方案就是在服务器根目录里增加这样一个文件，文件的内容如下：
```Xml
<?xml version="1.0" encoding="UTF-8"?>
<cross-domain-policy>
 <site-control permitted-cross-domain-policies="master-only" />
 <allow-access-from domain="*" to-ports="*"/>
</cross-domain-policy>
```
&emsp;&emsp;具体使用的时候需要将*号部分分别替换成允许跨域访问的地址和端口，因为我是用WAMP这个软件搭建的本地服务器，所以这里都采用的是默认值，具体怎么去设置这里的内容还需要大家自己去探索，不过这里就是像告诉大家使用Unity3D做网页游戏或者是从服务器上下载文件是一定要考虑这个问题的啊！

## 二、动态生成的UI Prefab被拉伸的问题
&emsp;&emsp;这个问题出现在动态生成UI元素的过程中，就是生成物体以后物体的大小和位置会发生变化，这个问题在宣雨松的博客中曾经读到过，不过当时他并没有说清楚产生这个问题的原因，所以当同样的问题发生在我身上的时候我果断选择和他一样，哈哈，解决方法是把物体的localScale设为(1,1,1)、localPosition设为(0,0,0)，当然按照我的传统如果大家知道是为什么的话还是告诉我吧！

## 三、AssetBundle的mainAsset问题
&emsp;&emsp;这个问题产生在最初确定AssetBundle打包是将单个物体打包还是将多个物体一起打包的时候，后来发现mainAsset取决于
bool BuildAssetBundle (Object mainAsset,Object[] assets,string pathName, BuildAssetBundleOptions 
optionsBuildAssetBundleOptions.CollectDependencies | BuildAssetBundleOptions.CompleteAssets,
BuildTarget targetPlatform= BuildTarget.WebPlayer)
这个方法中的第一个参数，就是说指定了一个参数则可以通过mainAsset来获取AssetBundle中的主物体，否则只能通过Load方法传入一个名称来获取指定物体。这里想说一件诡异的事情，比如说我们选中两个物体然后将其打包，但是通过LoadAll方法获取到的物体的数目却不是两个，因为打包的时候GamObject和Transform是分开打包的，父物体下的子物体同样是被分开打包的，因此这个方法使用起来并不是那么地尽如人意，这点希望大家注意！

##四、场景打包为AssetBundle的问题
&emsp;&emsp;我们知道在Unity中可以通过BuildStreamedSceneAssetBundle方法将场景打包为AssetBundle文件，然后按照如下方法加载到游戏中。场景打包的方法如下所示：
```JavaScript
static function MyBuild(){
		var levels : String[] = ["Assets/Level1.unity"];
		BuildPipeline.BuildStreamedSceneAssetBundle( levels, "Streamed-Level1.unity3d", BuildTarget.WebPlayer); 
	}
```
&emsp;&emsp;接下来我们就可以通过WWW方法将其加载到游戏中
```JavaScript
function Start () {
		// Download compressed scene. If version 5 of the file named "Streamed-Level1.unity3d" was previously downloaded and cached.
		// Then Unity will completely skip the download and load the decompressed scene directly from disk.
		var download = WWW.LoadFromCacheOrDownload ("http://myWebSite.com/Streamed-Level1.unity3d", 5);
		yield download;
		
		// Handle error
		if (download.error != null)
		{
			Debug.LogError(download.error);
			return;
		}
		
		// In order to make the scene available from LoadLevel, we have to load the asset bundle.
		// The AssetBundle class also lets you force unload all assets and file storage once it is no longer needed.
		var bundle = download.assetBundle;
		
		// Load the level we have just downloaded
		Application.LoadLevel ("Level1");
```
&emsp;&emsp;注意到最后一行我们是使用LoadLevel方法来加载一个场景的，该方法需要一个参数，它是我们在Unity3D中注册过的关卡，即在编译游戏的时候需要将其加入到关卡列表中。那么现在问题来了，这个Level11到底是本地的场景还是下载的场景啊，既然我们选择了从服务器上加载一个场景，那么本地应该是不会有这个场景了，那么游戏关卡列表中就不会有这个关卡，因此如果调用最后一样代码应该会提示找不到这个关卡。我在这里纠结了好久，最后发现是这样，就是现在本地做好关卡，然后将其加入到关卡列表中，当本地关卡打包成AssetBundle后，从本地删除当前关卡，依然可以从服务器上加载这个场景。这是我自己做实验的结果，不知道对不对，希望有知道这个的朋友能够告诉我这样到底对不对，因为这种方法感觉有些猥琐啊，哈哈。

&emsp;&emsp;好了，今天的内容就是这样了，因为目前项目暂时就发现了这些问题，所以更多的关于Unity3D的内容需要等到项目慢慢推进的过程中去发现了，希望大家能够喜欢啊！