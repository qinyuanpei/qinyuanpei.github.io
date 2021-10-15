---
abbrlink: 906436376
categories:
- 游戏开发
date: 2015-01-25 19:41:57
description: 尽管我们可以使用 Xml、Json、ini、数据库等存储形式来存储这些数据，可是毫无疑问的是，Excel 是 Window 平台上最好的数据处理软件，因此数值策划更倾向于使用 Excel 来设计游戏中的数据，面对如此重要的数值策划工作，我们自然希望在解析 Excel 文件时不会出现错误，可是我们总不能指望着策划把 Excel 数据转换成我们能处理的数据类型吧，因此就有了博主今天的这篇文章，所以在今天的文章中我们主要的内容就是如何通过程序来解析 Excel 文件;既然今天的主题是 Unity3D 游戏开发，所以无论我们在前面提出了什么样的解决方案，最后我们都要落实到游戏开发上，所以最后和大家分享的是一个 Unity3D 配合 ExcelReader 实现 Excel 解析的简单案例;因为平时经常与技术圈子里的朋友聊天，所以在博主印象里 Excel 的解析在游戏开发中还是较为常见的，而且博主知道对于微软的 Office 办公软件是可以通过 VBA 编程来实现某些功能的，可是因为博主一直在用国产的 WPS，所以对于 Excel 的解析基本上是停留在一个概念性的认识上，可是朋友的忙不能不帮不是，所以博主决定借着这个机会好好研究下 Excel 文件的解析
tags:
- Unity3D
- 游戏
- Excel
title: 当 Unity3D 游戏开发遇上 Excel
---

&emsp;&emsp;各位朋友，大家好，我是秦元培，欢迎大家关注我的博客，我的博客地址是[http://blog.csdn.net/qinyuanpei](http://blog.csdn.net/qinyuanpei)。今天我们来聊聊常用办公软件 Excel 和游戏开发那不为人知的秘密。今天的内容将涉及到 Excel 在游戏开发中的应用以及如何利用程序解析 Excel 中的数据。

<!--more-->

&emsp;&emsp;作为常用的办公软件的 Excel 相信大家都不陌生啦。可是如果我们认为 Excel 只是办公软件的话，那么这就不只是天真而是 Out 了。事实上 Excel 和游戏开发有着密切的联系，不知道大家还记不记得那款利用 Excel 开发出来的三国杀，这可能是 Excel 第一次以游戏开发的身份出现在大家面前吧。我们知道在游戏开发领域有一种工作叫做策划，就像在软件开发领域有一种工作叫做产品经理一样。而在诸多的策划工作中，数值策划是一个可以直接影响游戏进程的工作，因为数值策划体现了一个游戏在整体数值上的平衡，设计者需要维护好这样一个平衡，确保游戏外的玩家和游戏里的敌人面对的是同一个公平的虚拟世界。

&emsp;&emsp;例如《仙剑奇侠传四》这款游戏中，韩菱纱在游戏后期的速度可以说是完全打破了游戏的平衡性，因为韩菱纱本身的速度就比较快，再加上仙风云体术的加速效果完全对玄霄产生了戏剧性压制，导致在游戏结尾的 Boss 战中经常是韩菱纱出手 N 次后才挨到玄霄出手，我们知道韩菱纱的乾坤一掷每次消耗气 15，可是因为韩菱纱的速度足够快，所以韩菱纱完全可以通过普通物理攻击快速地积满气进而施展乾坤一掷，这就是游戏的平衡性被打破了呀，更不要说这部游戏里最为经典的千方残光剑 Bug 了，这同样是游戏平衡性的问题，归根到底是紫英的这个技能在配置数据时出现了错误，这充分说明数据的正确合理与否是会对游戏产生重要影响的。
<img src="http://img.blog.csdn.net/20150303100456547" alt="慕容紫英千方残光剑"/>
<img src="http://img.blog.csdn.net/20150303100419825" alt="韩菱纱乾坤一掷"/>
尽管我们可以使用 Xml、Json、ini、数据库等存储形式来存储这些数据，可是毫无疑问的是，Excel 是 Window 平台上最好的数据处理软件，因此数值策划更倾向于使用 Excel 来设计游戏中的数据，面对如此重要的数值策划工作，我们自然希望在解析 Excel 文件时不会出现错误，可是我们总不能指望着策划把 Excel 数据转换成我们能处理的数据类型吧，因此就有了博主今天的这篇文章，所以在今天的文章中我们主要的内容就是如何通过程序来解析 Excel 文件。

###1、项目需求
&emsp;&emsp;最近博主一个朋友向我抱怨，说手头上有好几百个 Excel 工作表要处理，大概几十万条数据吧。原因是当时公司分配任务时交待不清，等到了向公司交接数据的时候，朋友忽然发现这些 Excel 文件的表格格式和公司规定的不一样啊。这可急坏了博主的这位朋友，博主的朋友只好不断地的复制、黏贴，因为这些数据是分布在不同的数据表里，朋友整天都忙得焦头烂额，可是即使这样效率还是得不到保证啊，朋友最后找到了博主这里，问我能不能编写程序帮他解决这个问题。因为平时经常与技术圈子里的朋友聊天，所以在博主印象里 Excel 的解析在游戏开发中还是较为常见的，而且博主知道对于微软的 Office 办公软件是可以通过 VBA 编程来实现某些功能的，可是因为博主一直在用国产的 WPS，所以对于 Excel 的解析基本上是停留在一个概念性的认识上，可是朋友的忙不能不帮不是，所以博主决定借着这个机会好好研究下 Excel 文件的解析。

###2、解决方案
&emsp;&emsp;因为博主在之前并没有过解析 Excel 文件的经历，所以博主就到 Github 上淘了些开源项目。和很多人爱逛天猫、淘宝的经历类似，如果你发现有一个人经常喜欢到 Github 上晃荡、喜欢关注技术类的博客或者资讯、经常再看 PDF 版的技术文档或书籍，请千万不要怀疑，这个人绝对是程序员。哈哈，好了，玩笑就此打住啊。经过博主对这些开源项目的简单分析和整理，目前，对 Excel 文件解析的解决方案主要有以下三种：

####1、Microsoft.Office.Interop.Excel
&emsp;&emsp;第一种解决方案是基于微软提供的 Office API,这组 API 以 COM 组件的形式给出，我们可以通过调用该 API 实现对 Excel 文件的解析。使用这组 API 非常简单,博主稍后会为大家给出一个示例代码。微软的 Office API 特点是使用起来方便，可以使用 C#、Visual Basic 等语言进行相关开发。可是这种解决方案的的缺点同样很明显，因为 COM 组件主要依赖于系统，因此使用 COM 组件需要在系统中注册，这将对代码的可移植性产生影响，而且受制于 COM 技术，这种解决方案只能运行在 Windows 平台上，无法实现跨平台，加之解析速度较慢，因此这种方案通常只适合在解析速度要求不高，运行环境为 Windows 平台的应用场景。

####2、ExcelReader
&emsp;&emsp;第二种解决方案得益于 OpenOffice 标准,OpenOffice 标准可以让我们使用一种标准来解析和处理 Excel 文件而无需关注 Excel 文件是来自微软的 Misrosoft Office、金山的 WPS 还是其它的办公软件。如果说第一种解决方案是 Windows 平台上解析 Excel 文件的选择之一，那么 ExcelRead 就是跨平台目标下解析 Excel 文件的首选方案。尤其像 Unity3D 这样的跨平台解决方案下，选择一个跨平台的类库或者组件能够保证我们的游戏在各种平台下稳定地运行，所以 ExcelRead 是博主向大家推荐的一个跨平台的 Excel 解析方案。

####3、FastExcel
&emsp;&emsp;第三种解决方案 FastExcel 是博主在解决博主的这位朋友的问题时所采取的方案。FastExcel 是一个在开源世界里比较著名的 Excel 读写的类库，因此使用这个类库可以得到较为广泛的社区支持，而且在 FastExcel 这个项目的源代码中，作者为我们提供了使用 FastExel 进行 Excel 解析的相关示例，具有较高的参考价值，基本上可以在这个示例的基础上写出可以运行的代码。根据示例代码的运行结果使用 FastExcel 单独读写 100000 行数据基本上维持在 3~4 秒，读写速度还是蛮快的。不过 FastExcel 使用的是迭代器和 Linq to Xml 来读取 Excel 文件的，所以当数据表中存在空白单元格时，读写的时候会比较诡异，这一点希望大家注意。

###3、工程案例
&emsp;&emsp;既然今天的主题是 Unity3D 游戏开发，所以无论我们在前面提出了什么样的解决方案，最后我们都要落实到游戏开发上，所以最后和大家分享的是一个 Unity3D 配合 ExcelReader 实现 Excel 解析的简单案例。为什么要选择 ExcelReader 呢？因为 ExcelReader 是一个跨平台的解决方案。好了，下面我们一起来学习这个案例：
```plain
using UnityEngine;
using System.Collections;
using System.IO;
using Excel;
using System.Data;


public class ExcelScripts : MonoBehaviour 
{

	void Start () 
	{
		FileStream m_Stream=File.Open(Application.dataPath + 
			"\\Excel\\UserLevel.xlsx",FileMode.Open,FileAccess.Read);
		//使用OpenXml读取Excel文件
		IExcelDataReader mExcelReader=ExcelReaderFactory.CreateOpenXmlReader(m_Stream);
		//将Excel数据转化为DataSet
		DataSet mResultSets=mExcelReader.AsDataSet();
		//读取行数
		int rowCount=mResultSets.Tables[0].Rows.Count;
		//逐行读取,从第一行读以跳过表头
		for(int i=1;i<rowCount;i++)
		{
			//将读取的Excel数据转化成数据实体
			UserLevel mUser=new UserLevel();
			mUser.Name=mResultSets.Tables[0].Rows[i][0].ToString();
			mUser.Level=mResultSets.Tables[0].Rows[i][1].ToString();
			mUser.Description=mResultSets.Tables[0].Rows[i][2].ToString();
			mUser.Skill=mResultSets.Tables[0].Rows[i][3].ToString();
			//输出Debug信息
			Debug.Log(mUser.ToString());
			//ADD:更多逻辑
		}
	}

	//定义一个数据实体类UserLevel
	private class UserLevel
	{
		private string m_Name;
		public string Name 
		{
		  get { return m_Name;}
		  set { m_Name = value;}
		}

		private string m_Level;
		public string Level 
		{
		  get {	return m_Level;}
		  set {	m_Level = value;}
		}

		private string m_Description;
		public string Description 
		{
		  get { return m_Description;}
		  set { m_Description = value;}
		}

		private string m_Skill;
		public string Skill 
		{
		  get {	return m_Skill;}		
		  set {	m_Skill = value;}
		}

		public override string ToString()
		{
			return string.Format("Name={0}&Level={1}&Description={2}&Skill={3}",
			               m_Name,m_Level,m_Description,m_Skill);
		}
	}
}

```
&emsp;&emsp;好了，这就是今天这篇文章的全部内容了，希望大家喜欢！