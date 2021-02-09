---
abbrlink: 887585917
categories:
- 游戏开发
date: 2015-08-20 08:57:10
description: 因为我们这里要做的是一个游戏存档的方案设计，因为考虑到存档数据的安全性，我们可以考虑采用相关的加密/解密算法来实现对序列化后的明文数据进行加密，这样可以从一定程度上保证游戏存档数据的安全性;public
  static void SetData(string fileName,object pObject);public static object GetData(string
  fileName,Type pType)
tags:
- 游戏开发
- JSON
- 加密
title: Unity3D游戏开发游戏读/存档在Unity3D中的实现
---

&emsp;&emsp;大家好，我是秦元培，欢迎大家关注我的博客。近期博客的更新频率基本直降到冰点，因为这段时间实在是忙得没有时间来写博客了。今天想和大家分享的内容是RPG游戏中游戏存档的实现，因为最近在做一个RPG游戏的项目，所以遇到这个问题就随时记录下来，在对知识进行总结的同时可以将这种思路或者想法分享给大家，这是一件快乐而幸运的事情。我讨厌写按部就班的技术教程，因为我觉得学习是一种自我的探索行为，如果一切都告诉你了，探索的过程便会变得没有意义了。

<!--more-->

&emsp;&emsp;游戏存档是一种在单机游戏中特别常见的机制，这种机制是你在玩网络游戏的时候无法体验到的，你知道每次玩完一款单机游戏都会把游戏存档保存起来是一种怎样的感觉吗？它就像是一个征战沙场的将军将陪伴自己一生金戈铁马的宝剑静静地收入剑匣，然而每一次打开它的时候都会不由自主的热泪盈眶。人的本性其实就是游戏，我们每一天发生的故事何尝不是一个游戏？有时候让我们怀念的可能并不是游戏本身，而只是搁浅在时光里的那时的我们。好了，游戏存档是我们在游戏世界里雪泥鸿爪，它代表了我们曾经来到过这个世界。以RPG游戏为例，一个一般化的游戏存档应该囊括以下内容：

*   角色信息：指一切表征虚拟角色成长路线的信息，如生命值、魔法值、经验值等等。
*   道具信息：指一切表征虚拟道具数量或者作用的信息，如药品、道具、装备等等。
*   场景信息：指一切和游戏场景相关的信息，如场景名称、角色在当前场景中的位置坐标等等。
*   事件信息：指一切和游戏事件相关的信息，如主线任务、支线任务、触发性事件等等。

&emsp;&emsp;从以上信息划分的层次来看，我们可以发现在游戏存档中要储存的信息相对是比较复杂的，那么我们这里不得不说说Unity3D中的数据持久化方案PlayerPrefs。该方案采用的是一种键值型的数据存储方案，支持int、string、float三种基本数据类型，通过键名来获取相对应的数值，当值不存在时将返回一个默认值。这种数据存储方案本质上是将数据写入到一个Xml文件。这种方案如果用来存储简单的信息是没有问题的，可是如果用它来存储游戏存档这样负责的数据结构就显得力不从心了。一个更为重要的问题是在数据持久化的过程中我们希望得到是一个结构化的【游戏存档】实例，显然此时松散的PlayerPrefs是不能满足我们的要求的。因此我们想到了将游戏数据序列化的思路，常见的数据序列化思路主要有Xml和JSON两种形式，在使用Xml的数据序列化方案的时候通常有两种思路，即**手动建立数据实体和数据字符间的对应关系**和**基于XmlSerializer的数据序列化**。其中基于XmlSerializer的数据序列化是利用了[Serializable]这样的语法特性来帮助.NET完成数据实体和数据字符间的对应关系，两种思路本质上一样的。可是我们知道Xml的优点是可读性强，缺点是冗余信息多，因此在权衡了两种方案的利弊后，我决定采用JSON来作为数据序列化的方案，而且JSON在数据实体和数据字符间的对应关系上有着天然的优势，JSON所做的事情不就是将数据实体转化为字符串和从一个字符串中解析出数据实体吗？所以整个方案基本一气呵成。好了，下面我们来看具体的代码实现过程吧！

##一、JSON的序列化和反序列化
&emsp;&emsp;这里我使用的是Newtonsoft.Json这个类库，相信大家都是知道的了！因此，序列化和反序列化特别简单。
```csharp
/// <summary>
	/// 将一个对象序列化为字符串
	/// </summary>
	/// <returns>The object.</returns>
	/// <param name="pObject">对象</param>
	/// <param name="pType">对象类型</param>
	private static string SerializeObject(object pObject)
	{
		//序列化后的字符串
		string serializedString = string.Empty;
		//使用Json.Net进行序列化
		serializedString = JsonConvert.SerializeObject(pObject);
		return serializedString;
	}

	/// <summary>
	/// 将一个字符串反序列化为对象
	/// </summary>
	/// <returns>The object.</returns>
	/// <param name="pString">字符串</param>
	/// <param name="pType">对象类型</param>
	private static object DeserializeObject(string pString,Type pType)
	{
		//反序列化后的对象
		object deserializedObject = null;
		//使用Json.Net进行反序列化
		deserializedObject=JsonConvert.DeserializeObject(pString,pType);
		return deserializedObject;
	}
```
##二、Rijandel加密/解密算法
&emsp;&emsp;因为我们这里要做的是一个游戏存档的方案设计，因为考虑到存档数据的安全性，我们可以考虑采用相关的加密/解密算法来实现对序列化后的明文数据进行加密，这样可以从一定程度上保证游戏存档数据的安全性。因为博主并没有深入地研究过加密/解密方面的内容，所以这里仅仅提供一个从MSDN上获取的Rijandel算法，大家感兴趣的话可以自行去研究。
```C#
/// <summary>
    /// Rijndael加密算法
    /// </summary>
    /// <param name="pString">待加密的明文</param>
    /// <param name="pKey">密钥,长度可以为:64位(byte[8]),128位(byte[16]),192位(byte[24]),256位(byte[32])</param>
    /// <param name="iv">iv向量,长度为128（byte[16])</param>
    /// <returns></returns>
    private static string RijndaelEncrypt(string pString, string pKey)
	{
        //密钥
        byte[] keyArray = UTF8Encoding.UTF8.GetBytes(pKey);
        //待加密明文数组
        byte[] toEncryptArray = UTF8Encoding.UTF8.GetBytes(pString);

        //Rijndael解密算法
        RijndaelManaged rDel = new RijndaelManaged();
        rDel.Key = keyArray;
        rDel.Mode = CipherMode.ECB;
        rDel.Padding = PaddingMode.PKCS7;
        ICryptoTransform cTransform = rDel.CreateEncryptor();

        //返回加密后的密文
        byte[] resultArray = cTransform.TransformFinalBlock(toEncryptArray, 0, toEncryptArray.Length);
        return Convert.ToBase64String(resultArray, 0, resultArray.Length);
	}

    /// <summary>
    /// ijndael解密算法
    /// </summary>
    /// <param name="pString">待解密的密文</param>
    /// <param name="pKey">密钥,长度可以为:64位(byte[8]),128位(byte[16]),192位(byte[24]),256位(byte[32])</param>
    /// <param name="iv">iv向量,长度为128（byte[16])</param>
    /// <returns></returns>
    private static String RijndaelDecrypt(string pString, string pKey)
	{
        //解密密钥
        byte[] keyArray = UTF8Encoding.UTF8.GetBytes(pKey);
        //待解密密文数组
        byte[] toEncryptArray = Convert.FromBase64String(pString);

        //Rijndael解密算法
        RijndaelManaged rDel = new RijndaelManaged();
        rDel.Key = keyArray;
        rDel.Mode = CipherMode.ECB;
        rDel.Padding = PaddingMode.PKCS7;
        ICryptoTransform cTransform = rDel.CreateDecryptor();
        
        //返回解密后的明文
        byte[] resultArray = cTransform.TransformFinalBlock(toEncryptArray, 0, toEncryptArray.Length);
        return UTF8Encoding.UTF8.GetString(resultArray);
	}
```
##三、完整代码
&emsp;&emsp;好了，下面给出完整代码，我们这里提供了两个公开的方法GetData()和SetData()以及IO相关的辅助方法，我们在实际使用的时候只需要关注这些方法就可以了！
```C#
/**
 * Unity3D数据持久化辅助类
 * 作者:秦元培
 * 时间:2015年8月14日
 **/

using UnityEngine;
using System.Collections;
using System;
using System.IO;
using System.Text;
using System.Security.Cryptography;
using Newtonsoft.Json;

public static class IOHelper
{
	/// <summary>
	/// 判断文件是否存在
	/// </summary>
	public static bool IsFileExists(string fileName)
	{
		return File.Exists(fileName);
	}

	/// <summary>
	/// 判断文件夹是否存在
	/// </summary>
	public static bool IsDirectoryExists(string fileName)
	{
		return Directory.Exists(fileName);
	}

	/// <summary>
	/// 创建一个文本文件	
	/// </summary>
	/// <param name="fileName">文件路径</param>
	/// <param name="content">文件内容</param>
	public static void CreateFile(string fileName,string content)
	{
		StreamWriter streamWriter = File.CreateText(fileName);
		streamWriter.Write(content);
		streamWriter.Close();
	}

	/// <summary>
	/// 创建一个文件夹
	/// </summary>
	public static void CreateDirectory(string fileName)
	{
		//文件夹存在则返回
		if(IsDirectoryExists (fileName))
			return;
		Directory.CreateDirectory(fileName);
	}

	public static void SetData(string fileName,object pObject)
	{
		//将对象序列化为字符串
		string toSave = SerializeObject(pObject);
		//对字符串进行加密,32位加密密钥
        toSave = RijndaelEncrypt(toSave, "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx");
		StreamWriter streamWriter = File.CreateText(fileName);
		streamWriter.Write(toSave);
		streamWriter.Close();
	}

	public static object GetData(string fileName,Type pType)
	{
        StreamReader streamReader = File.OpenText(fileName);
		string data = streamReader.ReadToEnd();
		//对数据进行解密，32位解密密钥
        data = RijndaelDecrypt(data, "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx");
		streamReader.Close();
		return DeserializeObject(data,pType);
	}
	
    /// <summary>
    /// Rijndael加密算法
    /// </summary>
    /// <param name="pString">待加密的明文</param>
    /// <param name="pKey">密钥,长度可以为:64位(byte[8]),128位(byte[16]),192位(byte[24]),256位(byte[32])</param>
    /// <param name="iv">iv向量,长度为128（byte[16])</param>
    /// <returns></returns>
    private static string RijndaelEncrypt(string pString, string pKey)
	{
        //密钥
        byte[] keyArray = UTF8Encoding.UTF8.GetBytes(pKey);
        //待加密明文数组
        byte[] toEncryptArray = UTF8Encoding.UTF8.GetBytes(pString);

        //Rijndael解密算法
        RijndaelManaged rDel = new RijndaelManaged();
        rDel.Key = keyArray;
        rDel.Mode = CipherMode.ECB;
        rDel.Padding = PaddingMode.PKCS7;
        ICryptoTransform cTransform = rDel.CreateEncryptor();

        //返回加密后的密文
        byte[] resultArray = cTransform.TransformFinalBlock(toEncryptArray, 0, toEncryptArray.Length);
        return Convert.ToBase64String(resultArray, 0, resultArray.Length);
	}

    /// <summary>
    /// ijndael解密算法
    /// </summary>
    /// <param name="pString">待解密的密文</param>
    /// <param name="pKey">密钥,长度可以为:64位(byte[8]),128位(byte[16]),192位(byte[24]),256位(byte[32])</param>
    /// <param name="iv">iv向量,长度为128（byte[16])</param>
    /// <returns></returns>
    private static String RijndaelDecrypt(string pString, string pKey)
	{
        //解密密钥
        byte[] keyArray = UTF8Encoding.UTF8.GetBytes(pKey);
        //待解密密文数组
        byte[] toEncryptArray = Convert.FromBase64String(pString);

        //Rijndael解密算法
        RijndaelManaged rDel = new RijndaelManaged();
        rDel.Key = keyArray;
        rDel.Mode = CipherMode.ECB;
        rDel.Padding = PaddingMode.PKCS7;
        ICryptoTransform cTransform = rDel.CreateDecryptor();
        
        //返回解密后的明文
        byte[] resultArray = cTransform.TransformFinalBlock(toEncryptArray, 0, toEncryptArray.Length);
        return UTF8Encoding.UTF8.GetString(resultArray);
	}


	/// <summary>
	/// 将一个对象序列化为字符串
	/// </summary>
	/// <returns>The object.</returns>
	/// <param name="pObject">对象</param>
	/// <param name="pType">对象类型</param>
	private static string SerializeObject(object pObject)
	{
		//序列化后的字符串
		string serializedString = string.Empty;
		//使用Json.Net进行序列化
		serializedString = JsonConvert.SerializeObject(pObject);
		return serializedString;
	}

	/// <summary>
	/// 将一个字符串反序列化为对象
	/// </summary>
	/// <returns>The object.</returns>
	/// <param name="pString">字符串</param>
	/// <param name="pType">对象类型</param>
	private static object DeserializeObject(string pString,Type pType)
	{
		//反序列化后的对象
		object deserializedObject = null;
		//使用Json.Net进行反序列化
		deserializedObject=JsonConvert.DeserializeObject(pString,pType);
		return deserializedObject;
	}
}
```
&emsp;&emsp;这里我们的密钥是直接写在代码中的，这样做其实是有风险的，因为一旦我们的项目被反编译，我们这里的密钥就变得很不安全了。这里有两种方法，一种是把密钥暴露给外部方法，即在读取数据和写入数据的时候使用同一个密钥即可，而密钥可以采取由机器MAC值生成的方法，这样每台机器上的密钥都是不同的可以防止数据被破解；其次可以采用DLL混淆的方法让反编译者无法看到代码中的内容，这样就无法获得正确的密钥从而无法获得存档里的内容了。
##四、最终效果
好了，最后我们来写一个简单的测试脚本：
```C#
using UnityEngine;
using System.Collections;
using System.Collections.Generic;

public class TestSave : MonoBehaviour {


    /// <summary>
    /// 定义一个测试类
    /// </summary>
	public class TestClass
	{
        public string Name = "张三";
		public float Age = 23.0f;
		public int Sex = 1;

		public List<int> Ints = new List<int> ()
		{
			1,
			2,
			3
		};
	}

	void Start () 
	{
        //定义存档路径
		string dirpath = Application.persistentDataPath + "/Save";
        //创建存档文件夹
		IOHelper.CreateDirectory (dirpath);
        //定义存档文件路径
		string filename = dirpath + "/GameData.sav";
		TestClass t = new TestClass ();
        //保存数据
		IOHelper.SetData (filename,t);
        //读取数据
		TestClass t1 = (TestClass)IOHelper.GetData(filename,typeof(TestClass));

        Debug.Log(t1.Name);
        Debug.Log(t1.Age);
        Debug.Log(t1.Ints);
	}
	

}
```
&emsp;&emsp;脚本执行结果：

![p1](https://ww1.sinaimg.cn/large/None.jpg)

&emsp;&emsp;加密后游戏存档：

![p2](https://ww1.sinaimg.cn/large/4c36074fly1fz68k767w3j20l2033t8j.jpg)

&emsp;&emsp;好了，这就是今天的内容了，希望大家能够喜欢，有什么问题可以给我留言，谢谢！
&emsp;&emsp;感谢风宇冲[Unity3D教程宝典之两步实现超实用的XML存档](http://blog.sina.com.cn/s/blog_471132920101d3kh.html)一文提供相关思路！

>喜欢我的博客请记住我的名字：**秦元培**，我的博客地址是：[http://qinyuanpei.com](http://qinyuanpei.com)
转载请注明出处，本文作者：**秦元培**， 本文出处：[http://blog.csdn.net/qinyuanpei/article/details/39717795](http://blog.csdn.net/qinyuanpei/article/details/39717795)