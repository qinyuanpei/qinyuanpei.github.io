---
abbrlink: 582264328
categories:
- 游戏开发
date: 2015-07-09 09:47:06
description: '* 三、在使用InsertValues方法时请参考SQLite中字段类型与C#中数据类型的对应关系，博主目前测试了int类型和string类型都没有什么问题，更多类型的数据请大家自行测试然后告诉博主测试的结果，如果大家有兴趣扩展这个辅助类的话可以自行去扩展哦，嘿嘿;int
  fieldCount=ReadFullTable(tableName).FieldCount;在Unity3D中使用的SQLite以Mono.Data.Sqlite.dll即动态链接库的形式给出，因此我们需要将这个文件放置在项目目录下的Plugins文件夹中，此外我们需要System.Data.dll或者Mono.Data.dll这两个文件添加到Plugins目录中，因为我们需要的部分数据相关的API或者类都定义在这两个文件当中，这些文件可以从[这里](http://pan.baidu.com/s/1sjLZyrj)直接下载'
tags:
- Unity3D
- SQLite
- 数据库
title: Unity3D游戏开发之SQLite让数据库开发更简单
---

&emsp;&emsp;各位朋友大家好，欢迎大家关注我的博客，我是秦元培，我是博客地址是[http://blog.csdn.net/qinyuanpei](http://blog.csdn.net/qinyuanpei)。在经历了一段时间的忙碌后，博主终于有时间来研究新的东西啦，今天博客向和大家一起交流的内容是在Unity3D游戏开发中使用SQLite进行数据库开发，坦白来讲，在我的技术体系中Web和数据库是相对薄弱的两个部分，因此正好这段时间项目需要和服务器、数据库进行交互，因此在接下来的文章中博主可能会更加倾向于讲解这方面的内容，希望大家能够喜欢啊！

<!--more-->

# 一、什么是SQLite？
&emsp;&emsp;[SQLite](http://www.sqlite.org/)是一款轻型的数据库，是遵守ACID的关系型数据库管理系统，它包含在一个相对小的C库中，以嵌入式作为它的设计目标，它占用资源非常的低，因此适合在嵌入式设备如Android、Ruby on Rails等中使用。它能够支持Windows/Linux/Unix等等主流的操作系统，同时能够跟和C、C++、Ruby、Python、C#、PHP、Java等编程语言相结合。SQLite是一个以文件形式存在的关系型数据库，尽管无法实现分布式和横向扩展，可是作为一个轻量级的嵌入式数据库，它不需要系统提供服务支持，通过SDK直接操作文件避免了对数据库维护的相关事务，从这个角度来讲它是一个出色的数据库。

# 二、为什么要选择SQLite
&emsp;&emsp;好了，在了解了SQLite后，我们来了解下SQLite有哪些让我们心动的特性，或者说我们为什么要选择SQLite，因为在这个世界上我们有太多的数据库可以选择，诸如Oracle、MySQL、SQLServer、DB2、NoSQL、MongoDB等等：

>*  ACID事务
>* 零配置 – 无需安装和管理配置
>* 储存在单一磁盘文件中的一个完整的数据库
>* 数据库文件可以在不同字节顺序的机器间自由的共享
>* 支持数据库大小至2TB
>* 足够小, 大致13万行C代码, 4.43M
* 比一些流行的数据库在大部分普通数据库操作要快---[SQLite读写效率如此之高，会使用其他数据库的理由是？](http://www.zhihu.com/question/31417262)
* 简单, 轻松的API
* 包含TCL绑定, 同时通过Wrapper支持其他语言的绑定
* 良好注释的源代码, 并且有着90%以上的测试覆盖率
* 独立: 没有额外依赖
* 源码完全的开源, 你可以用于任何用途, 包括出售它
* 支持多种开发语言，C, C++, PHP, Perl, Java, C#,Python, Ruby等

# 三、Unity3D中的SQLite
&emsp;&emsp;在Unity3D中使用SQLite，我们首先要明白这样一件事情，即我们这里的使用的SQLite并非是通常意义上的SQLite.NET,而是经过移植后的Mono.Data.Sqlite。因为Unity3D基于Mono，因此使用移植后的Mono.Data.Sqlite能够减少我们的项目在不同平台上出现各种各样的问题。在Unity3D中使用的SQLite以Mono.Data.Sqlite.dll即动态链接库的形式给出，因此我们需要将这个文件放置在项目目录下的Plugins文件夹中，此外我们需要System.Data.dll或者Mono.Data.dll这两个文件添加到Plugins目录中，因为我们需要的部分数据相关的API或者类都定义在这两个文件当中，这些文件可以从[这里](http://pan.baidu.com/s/1sjLZyrj)直接下载。

>PS：博主注意到在网上有使用Mono.Data.SQLiteClient.dll这个库实现在Unity3D操作SQLite数据库的相关文章，博主大概看了下，感觉和使用Mono.Data.Sqlite.dll这个库大同小异，大家喜欢哪个就用哪个吧！哈哈！博主在开源社区找到一个版本库，据说可以同时支持.NET和Mono，如果大家感兴趣欢迎大家去测试啊，哈哈!


&emsp;&emsp;在正式开始写代码前，我们首先来回顾下通常情况下数据库读写的基本流程吧！

>* 定义数据库连接字符串(ConnectionString)完成数据库连接的构造，建立或者打开一个数据库。
>* 定义相关的SQL命令(Command)通过这些命令实现对数据库的增加、删除、更新、读取四种基本功能。
>* 在完成各种数据库操作后及时关闭数据库连接，解除对数据库的连接和引用。

&emsp;&emsp;SQLite作为一款优秀的数据库，在为其编写数据库相关代码时同样遵循这样的流程，考虑到对数据库的增加、删除、更新、读取四种操作具有类似性和统一性，因此在动手写Unity3D脚本前，首先让我们来编写一个SQLite的辅助类SQLiteHelper.cs。该类代码定义如下：
```C#
using UnityEngine;
using System.Collections;
using Mono.Data.Sqlite;
using System;

public class SQLiteHelper
{
	/// <summary>
	/// 数据库连接定义
	/// </summary>
	private SqliteConnection dbConnection;

	/// <summary>
	/// SQL命令定义
	/// </summary>
	private SqliteCommand dbCommand;

	/// <summary>
	/// 数据读取定义
	/// </summary>
	private SqliteDataReader dataReader;

	/// <summary>
	/// 构造函数	
	/// </summary>
	/// <param name="connectionString">数据库连接字符串</param>
	public SQLiteHelper(string connectionString)
	{
		try{
			//构造数据库连接
			dbConnection=new SqliteConnection(connectionString);
			//打开数据库
			dbConnection.Open();
		}catch(Exception e)
		{
			Debug.Log(e.Message);
		}
	}

	/// <summary>
	/// 执行SQL命令
	/// </summary>
	/// <returns>The query.</returns>
	/// <param name="queryString">SQL命令字符串</param>
	public SqliteDataReader ExecuteQuery(string queryString)
	{
		dbCommand = dbConnection.CreateCommand();
		dbCommand.CommandText = queryString;
		dataReader = dbCommand.ExecuteReader();
		return dataReader;
	}

	/// <summary>
	/// 关闭数据库连接
	/// </summary>
	public void CloseConnection()
	{
		//销毁Command
		if(dbCommand != null){
			dbCommand.Cancel();
		}
		dbCommand = null;

		//销毁Reader
		if(dataReader != null){
			dataReader.Close();
		}
		dataReader = null;

		//销毁Connection
		if(dbConnection != null){
			dbConnection.Close();
		}
		dbConnection = null;
	}

	/// <summary>
	/// 读取整张数据表
	/// </summary>
	/// <returns>The full table.</returns>
	/// <param name="tableName">数据表名称</param>
	public SqliteDataReader ReadFullTable(string tableName)
	{
		string queryString = "SELECT * FROM " + tableName;
		return ExecuteQuery (queryString);
	}

	/// <summary>
	/// 向指定数据表中插入数据
	/// </summary>
	/// <returns>The values.</returns>
	/// <param name="tableName">数据表名称</param>
	/// <param name="values">插入的数值</param>
	public SqliteDataReader InsertValues(string tableName,string[] values)
	{
		//获取数据表中字段数目
		int fieldCount=ReadFullTable(tableName).FieldCount;
		//当插入的数据长度不等于字段数目时引发异常
		if(values.Length!=fieldCount){
			throw new SqliteException("values.Length!=fieldCount");
		}

		string queryString = "INSERT INTO " + tableName + " VALUES (" + values[0];
		for(int i=1; i<values.Length; i++)
		{
			queryString+=", " + values[i];
		}
		queryString += " )";
		return ExecuteQuery(queryString);
	}

	/// <summary>
	/// 更新指定数据表内的数据
	/// </summary>
	/// <returns>The values.</returns>
	/// <param name="tableName">数据表名称</param>
	/// <param name="colNames">字段名</param>
	/// <param name="colValues">字段名对应的数据</param>
	/// <param name="key">关键字</param>
	/// <param name="value">关键字对应的值</param>
	public SqliteDataReader UpdateValues(string tableName,string[] colNames,string[] colValues,string key,string operation,string value)
	{
		//当字段名称和字段数值不对应时引发异常
		if(colNames.Length!=colValues.Length) {
			throw new SqliteException("colNames.Length!=colValues.Length");
		}

		string queryString = "UPDATE " + tableName + " SET " + colNames[0] + "=" + colValues[0];
		for(int i=1; i<colValues.Length; i++) 
		{
			queryString+=", " + colNames[i] + "=" + colValues[i];
		}
		queryString += " WHERE " + key + operation + value;
		return ExecuteQuery(queryString);
	}

	/// <summary>
	/// 删除指定数据表内的数据
	/// </summary>
	/// <returns>The values.</returns>
	/// <param name="tableName">数据表名称</param>
	/// <param name="colNames">字段名</param>
	/// <param name="colValues">字段名对应的数据</param>
	public SqliteDataReader DeleteValuesOR(string tableName,string[] colNames,string[] operations,string[] colValues)
	{
		//当字段名称和字段数值不对应时引发异常
		if(colNames.Length!=colValues.Length || operations.Length!=colNames.Length || operations.Length!=colValues.Length) {
			throw new SqliteException("colNames.Length!=colValues.Length || operations.Length!=colNames.Length || operations.Length!=colValues.Length");
		}

		string queryString = "DELETE FROM " + tableName + " WHERE " + colNames[0] + operations[0] + colValues[0];
		for(int i=1; i<colValues.Length; i++) 
		{
			queryString+="OR " + colNames[i] + operations[0] + colValues[i];
		}
		return ExecuteQuery(queryString);
	}

	/// <summary>
	/// 删除指定数据表内的数据
	/// </summary>
	/// <returns>The values.</returns>
	/// <param name="tableName">数据表名称</param>
	/// <param name="colNames">字段名</param>
	/// <param name="colValues">字段名对应的数据</param>
	public SqliteDataReader DeleteValuesAND(string tableName,string[] colNames,string[] operations,string[] colValues)
	{
		//当字段名称和字段数值不对应时引发异常
		if(colNames.Length!=colValues.Length || operations.Length!=colNames.Length || operations.Length!=colValues.Length) {
			throw new SqliteException("colNames.Length!=colValues.Length || operations.Length!=colNames.Length || operations.Length!=colValues.Length");
		}

		string queryString = "DELETE FROM " + tableName + " WHERE " + colNames[0] + operations[0] + colValues[0];
		for(int i=1; i<colValues.Length; i++) 
		{
			queryString+=" AND " + colNames[i] + operations[i] + colValues[i];
		}
		return ExecuteQuery(queryString);
	}

	/// <summary>
	/// 创建数据表
	/// </summary> +
	/// <returns>The table.</returns>
	/// <param name="tableName">数据表名</param>
	/// <param name="colNames">字段名</param>
	/// <param name="colTypes">字段名类型</param>
	public SqliteDataReader CreateTable(string tableName,string[] colNames,string[] colTypes)
	{
		string queryString = "CREATE TABLE " + tableName + "( " + colNames [0] + " " + colTypes [0];
		for (int i=1; i<colNames.Length; i++) 
		{
			queryString+=", " + colNames[i] + " " + colTypes[i];
		}
		queryString+= "  ) ";
		return ExecuteQuery(queryString);
	}

	/// <summary>
	/// Reads the table.
	/// </summary>
	/// <returns>The table.</returns>
	/// <param name="tableName">Table name.</param>
	/// <param name="items">Items.</param>
	/// <param name="colNames">Col names.</param>
	/// <param name="operations">Operations.</param>
	/// <param name="colValues">Col values.</param>
	public SqliteDataReader ReadTable(string tableName,string[] items,string[] colNames,string[] operations, string[] colValues)
	{
		string queryString = "SELECT " + items [0];
		for (int i=1; i<items.Length; i++) 
		{
			queryString+=", " + items[i];
		}
		queryString += " FROM " + tableName + " WHERE " + colNames[0] + " " +  operations[0] + " " + colValues[0];
		for (int i=0; i<colNames.Length; i++) 
		{
			queryString+=" AND " + colNames[i] + " " + operations[i] + " " + colValues[0] + " ";
		}
		return ExecuteQuery(queryString);
	}
}
```

&emsp;&emsp;SQLiteHelper类主要实现了数据库、数据表的创建以及数据表中记录的增加、删除、更新、读取四种基本功能。该类最初由国外的Unity3D开发者发布在[Unity3D官方论坛](http://forum.unity3d.com/threads/28500-SQLite-Class-Easier-Database-Stuff),后来经[宣雨松](http://www.xuanyusong.com/archives/831)使用C#进行重写，我在此基础上进行了完善，再此对两位大神的无私付出表示感谢。这里要说明的有三点：

*  一、在Unity3D编辑器下生成数据库文件(.db)默认位于和Assets目录同级的位置，即项目的工程文件夹中。我们可以通过修改路径在改变数据库文件的存储位置，具体来讲：
Windows平台：data source=Application.dataPath/数据库名称.db
IOS平台：data source=Application.persistentDataPath/数据库名称.db
Android平台：URL=file:Application.persistentDataPath/数据库名称.db(我想说Android平台就是个奇葩，搞什么特殊化嘛)

* 二、确保Unity3D编辑器中的.NET版本和MonoDevelop中的.NET版本都为2.0版本，在Unity3D中打包导出的程序可能不会保留数据库文件，因此需要手动将数据库文件拷贝到相应的位置，当然更加合理的方案是将数据库文件存放到StreamingAssets文件夹下，然后在第一次加载游戏的时候将数据库文件复制到对应平台上的存放位置。

* 三、在使用InsertValues方法时请参考SQLite中字段类型与C#中数据类型的对应关系，博主目前测试了int类型和string类型都没有什么问题，更多类型的数据请大家自行测试然后告诉博主测试的结果，如果大家有兴趣扩展这个辅助类的话可以自行去扩展哦，嘿嘿！

&emsp;&emsp;好了，千呼万唤始出来的时候到了，下面我们以一个实例来完成今天的项目讲解，因为我们已经定义好了SQLite的辅助类，因此我们可以快速地编写出下面的脚本代码：
```C#
using UnityEngine;
using System.Collections;
using System.IO;
using Mono.Data.Sqlite;

public class SQLiteDemo : MonoBehaviour 
{
	/// <summary>
	/// SQLite数据库辅助类
	/// </summary>
	private SQLiteHelper sql;

	void Start () 
	{
		//创建名为sqlite4unity的数据库
		sql = new SQLiteHelper("data source=sqlite4unity.db");

		//创建名为table1的数据表
		sql.CreateTable("table1",new string[]{"ID","Name","Age","Email"},new string[]{"INTEGER","TEXT","INTEGER","TEXT"});

		//插入两条数据
		sql.InsertValues("table1",new string[]{"'1'","'张三'","'22'","'Zhang3@163.com'"});
		sql.InsertValues("table1",new string[]{"'2'","'李四'","'25'","'Li4@163.com'"});

		//更新数据，将Name="张三"的记录中的Name改为"Zhang3"
		sql.UpdateValues("table1", new string[]{"Name"}, new string[]{"'Zhang3'"}, "Name", "=", "'张三'");

		//插入3条数据
		sql.InsertValues("table1",new string[]{"3","'王五'","25","'Wang5@163.com'"});
		sql.InsertValues("table1",new string[]{"4","'王五'","26","'Wang5@163.com'"});
		sql.InsertValues("table1",new string[]{"5","'王五'","27","'Wang5@163.com'"});

		//删除Name="王五"且Age=26的记录,DeleteValuesOR方法类似
		sql.DeleteValuesAND("table1", new string[]{"Name","Age"}, new string[]{"=","="}, new string[]{"'王五'","'26'"});

		//读取整张表
		SqliteDataReader reader = sql.ReadFullTable ("table1");
		while(reader.Read()) 
		{
			//读取ID
			Debug.Log(reader.GetInt32(reader.GetOrdinal("ID")));
			//读取Name
			Debug.Log(reader.GetString(reader.GetOrdinal("Name")));
			//读取Age
			Debug.Log(reader.GetInt32(reader.GetOrdinal("Age")));
			//读取Email
			Debug.Log(reader.GetString(reader.GetOrdinal("Email")));
		}

		//读取数据表中Age>=25的所有记录的ID和Name
		reader = sql.ReadTable ("table1", new string[]{"ID","Name"}, new string[]{"Age"}, new string[]{">="}, new string[]{"'25'"});
		while(reader.Read()) 
		{
			//读取ID
			Debug.Log(reader.GetInt32(reader.GetOrdinal("ID")));
			//读取Name
			Debug.Log(reader.GetString(reader.GetOrdinal("Name")));
		}

		//自定义SQL,删除数据表中所有Name="王五"的记录
		sql.ExecuteQuery("DELETE FROM table1 WHERE NAME='王五'");

		//关闭数据库连接
		sql.CloseConnection();
	}
}

```
&emsp;&emsp;在上面的代码中我们是在Start方法中创建了数据库和数据表，然而在实际使用中我们需要判断数据库和数据表是否存在，因此如果你使用这段脚本提示错误信息，请确保数据库和数据表是否已经存在。好了，下面的截图展示了程序运行的结果：

![数据库效果演示](https://ww1.sinaimg.cn/large/None.jpg)

![Unity3D效果展示](https://ww1.sinaimg.cn/large/None.jpg)

&emsp;&emsp;作为一个强大的数据库怎么能没有图形化的数据库管理工具呢？所以这里博主向大家推荐一个免安装的小工具SqliteStudio，使用这个工具可以帮助我们方便地管理Sqlite数据库里的数据，这样是不是比较方便呢？哈哈！这个工具可以从[这里](http://pan.baidu.com/s/1hqldZ3A)下载哦！

![SQLiteStudio界面演示](https://ww1.sinaimg.cn/large/4c36074fly1fz68jpgvl4j20s00ibdik.jpg)

&emsp;&emsp;好了，今天的内容就是这样了，为了写这篇文章花了三个晚上准备，希望大家喜欢啊！如果大家觉得这篇文章有用，请继续关注我的博客，我是秦元培，我的博客地址是[http://blog.csdn.net/qinyuanpei](http://blog.csdn.net/qinyuanpei)。

&emsp;&emsp;**2015年11月3日更新内容如下**：不同平台上的数据库存储路径
```
        //各平台下数据库存储的绝对路径(通用)
        //PC：sql = new SQLiteHelper("data source=" + Application.dataPath + "/sqlite4unity.db");
        //Mac：sql = new SQLiteHelper("data source=" + Application.dataPath + "/sqlite4unity.db");
        //Android：sql = new SQLiteHelper("URI=file:" + Application.persistentDataPath + "/sqlite4unity.db");
        //iOS：sql = new SQLiteHelper("data source=" + Application.persistentDataPath + "/sqlite4unity.db");

        //PC平台下的相对路径
        //sql = new SQLiteHelper("data source="sqlite4unity.db");
        //编辑器：Assets/sqlite4unity.db
        //编译后：和AppName.exe同级的目录下，这里比较奇葩
        //当然可以用更随意的方式sql = new SQLiteHelper("data source="D://SQLite//sqlite4unity.db");
        //确保路径存在即可否则会发生错误

        //如果是事先创建了一份数据库
        //可以将这个数据库放置在StreamingAssets目录下然后再拷贝到
        //Application.persistentDataPath + "/sqlite4unity.db"路径即可

```