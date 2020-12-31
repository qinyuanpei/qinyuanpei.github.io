---
toc: true
title: 温故而知新，由ADO.NET与Dapper所联想到的
categories:
  - 编程语言
tags:
  - ADO.NET
  - Dapper
  - Dynamic
  - 技巧
copyright: true
abbrlink: 2621074915
date: 2020-12-30 12:49:47
---
 这段时间在维护一个“遗产项目”，体验可以说是相当地难受，因为它的数据持久化层完全由ADO.NET纯手工打造，所以，你可以在项目中看到无所不在的DataTable，不论是读操作还是写操作。这个DataTable让我这个习惯了Entity Framework的人感到非常别扭，我并不排斥写手写SQL语句，我只是拥有某种自觉并且清醒地知道，自己写的SQL语句未必就比ORM生成的SQL语句要好。可至少应该是像Dapper这种程度的封装啊，因为关系型数据库天生就和面向对象编程存在隔离，所以，频繁地使用DataTable无疑意味着你要写很多的转换的代码，当我看到`DbConnection`、`DbCommand`、`DbDataReader`、`DbDataAdapter`这些熟悉的“底层”的时候，我意识到我可以结合着Dapper的实现，从中梳理出一点改善的思路，所以，这篇博客想聊一聊**ADO.NET**、**Dapper**和**Dynamic**这三者间交叉的部分，希望能给大家带来新的启发。

# 重温ADO.NET
相信大家都知道，我这里提到的`DbConnection`、`DbCommand`、`DbDataReader`、`DbDataAdapte`以及`DataTable`、`DataSet`，实际上就是ADO.NET中核心的组成部分，譬如`DbConnection`负责管理数据库连接，`DbCommand`负责SQL语句的执行，`DbDataReader`和`DbDataAdapter`负责数据库结果集的读取。需要注意的是，这些类型都是抽象类，而各个数据库的具体实现，则是由对应的厂商来完成，即我们称之为“驱动”的部分，它们都遵循同一套接口规范，而`DataTable`和`DataSet`则是“装”数据库结果集的容器。关于ADO.NET的设计理念，可以从下图中得到更清晰的答案：

![ADO.NET架构](https://i.loli.net/2020/12/31/dEN2tajehboDiTl.png)

在这种理念的指引，使用ADO.NET访问数据库通常会是下面的画风。博主相信，大家在各种各样的`DbHelper`或者`DbUtils`中都见过类似的代码片段，在更复杂的场景中，我们会使用`DbParameter`来辅助`DbCommand`，而这就是所谓的**SQL参数化查询**。

```CSharp
var fileName = Path.Combine(Directory.GetCurrentDirectory(), "Chinook.db");
using (var connection = new SQLiteConnection($"Data Source={fileName}"))
{
    if (connection.State != ConnectionState.Open) connection.Open();
    using (var command = connection.CreateCommand())
    {
        command.CommandText = "SELECT AlbumId, Title, ArtistId FROM [Album]";
        command.CommandType = CommandType.Text;

        //套路1：使用DbDataReader读取数据
        using (var reader = command.ExecuteReader())
        {
            while (reader.Read())
            {
                //各种眼花缭乱的写法:)
                Console.WriteLine($"AlbumId={reader.GetValue(0)}");
                Console.WriteLine($"Title={reader.GetFieldValue<string>("Title")}");
                Console.WriteLine($"ArtistId={reader.GetInt32("ArtistId")}");
            }
        }

        //套路2：使用DbDataAdapter读取数据
        using (var adapter = new SQLiteDataAdapter(command))
        {
            var dataTable = new DataTable();
            adapter.Fill(dataTable);
        }
    }
}
```
这里经常会引发的讨论是，`DbDataReader`和`DbDataAdapter`的区别以及各自的使用场景是什么？简单来说，前者是按需读取/只读，数据库连接会一直保持；而后者是一次读取，数据全部加载到内存，数据库连接用完就会关掉。从资源释放的角度，听起来后者更友好一点，可显然结果集越大占用的内存就会越多。而如果从易用性上来考虑，后者可以直接填充数据到`DataSet`或者`DataTable`，前者则需要费一点周折，你看这段代码是不是有点秀操作的意思：

```CSharp
//各种眼花缭乱的写法:)
Console.WriteLine($"AlbumId={reader.GetValue(0)}");
Console.WriteLine($"Title={reader.GetFieldValue<string>("Title")}");
Console.WriteLine($"ArtistId={reader.GetInt32("ArtistId")}");
```

在这个“遗产项目”中，`DbDataReader`和`DbDataAdapter`都有所涉猎，后者在结果集不大的情况下还是可以的，唯一的遗憾就是`DataTable`和`LINQ`的违和感实在太强烈了，虽然可以勉强使用`AsEnumerable()`拯救一下，而前者就有一点魔幻了，你能看到各种`GetValue(1)`、`GetValue(2)`这样的写法，这简直就是成心不想让后面维护的人好过，因为加字段的时候要小心翼翼地，确保字段顺序不会被修改。明明这个世界上有[Dapper](https://github.com/StackExchange/Dapper)、[SqlSugar](https://github.com/donet5/SqlSugar)、[SmartSql](https://smartsql.net/)这样优秀的ORM存在，为什么就要如此执著地写这种代码呢？是觉得MyBatis在XML里写SQL语句很时尚吗？

所以，我开始尝试改进这些代码，我希望它可以像Dapper一样，提供`Query<T>()`和`Execute()`两个方法足矣！如果要把结果集映射到一个具体的类型上，大家都能想到使用反射，我更想实现的是Dapper里的`DapperRow`，它可以通过“·”或者字典的形式来访问字段，现在的问题来了，你能实现类似Dapper里DapperRow的效果吗？因为想偷懒的时候，dynamic不比DataRow更省事儿吗？那玩意儿光转换类型就要烦死人了，更不用说要映射到某个DTO啦！

# 实现DynamicRow

通过阅读Dapper的源代码，我们知道，Dapper中用[DapperTable](https://github.com/StackExchange/Dapper/blob/main/Dapper/SqlMapper.DapperTable.cs)和[DapperRow](https://github.com/StackExchange/Dapper/blob/main/Dapper/SqlMapper.DapperRowMetaObject.cs)替换掉了DataTable和DataRow，可见这两个玩意儿有多不好用，果然，英雄所见略同啊，哈哈哈！其实，这背后的一切的功臣是[IDynamicMetaObjectProvider](https://docs.microsoft.com/zh-cn/dotnet/api/system.dynamic.idynamicmetaobjectprovider?view=net-5.0)，通过这个接口我们就能实现类似的功能，我们熟悉的`ExpendoObject`就是最好的例子：

```CSharp
dynamic person = new ExpandoObject(); 
person.FirstName = "Sherlock"; 
person.LastName = "Holmes";

//等价形式
(person as IDctionary<string, object>)["FirstName"] = "Sherlock";
(person as IDctionary<string, object>)["LastName"] = "Holmes";
```

这里，我们用一种简单的方式，让DynamicRow继承者DynamicObject，下面一起来看具体的代码：

```CSharp
public class DynamicRow : DynamicObject
{
    private readonly IDataRecord _record;
    public DynamicRow(IDataRecord record)
    {
        _record = record;
    }

    public override bool TryGetMember(GetMemberBinder binder, out object result)
    {
        var index = _record.GetOrdinal(binder.Name);
        result = index > 0 ? _record[binder.Name] : null;
        return index > 0;
    }
        
    //支持像字典一样使用
    public object this[string field] =>
       _record.GetOrdinal(field) > 0 ? _record[field] : null;
}
```
对于`DynamicObject`这个类型而言，里面最重要的两个方法其实是`TryGetMember()`和`TrySetMember()`，因为这决定了这个动态对象的读和写两个操作。因为我们这里不需要反向地去操作数据库，所以，我们只需要关注`TryGetMember()`即可，一旦实现这个方法，我们就可以使用类似`foo.bar`这种形式访问字段，而提供一个所引起，则是为了提供类似`foo["bar"]`的访问方式，这一点同样是为了像Dapper看齐，无非是Dapper的DynamicRow本来就是一个字典！

现在，我们来着手实现一个简化版的Dapper，给`IDbConnection`这个接口扩展出`Query<T>()`和`Execute()`两个方法，我们注意到`Query<T>()`需要用到`DbDataReader`或者`DbDataAdapter`其一，对于`DbDataAdapter`而言，它的实现完全由具体的子类决定，所以，对于`IDbConnection`接口而言，它完全不知道对应的子类是什么，此时，我们只能通过判断`IDbConnection`的类型来返回对应的DbDataAdapter。读过我之前[博客](https://blog.yuanpei.me/posts/3086300103/)的朋友，应该对Dapper里的数据库类型的字典有印象，不好意思，这里历史要再次上演啦！

```CSharp
public static IEnumerable<dynamic> Query(this IDbConnection connection, string sql, 
  object param = null, IDbTransaction trans = null)
{
    var reader = connection.CreateDataReader(sql);
    while (reader.Read())
        yield return new DynamicRow(reader as IDataRecord);
}

public static IEnumerable<T> Query<T>(this IDbConnection connection, string sql,
  object param = null, IDbTransaction trans = null) 
  where T : class, new()
{
    var reader = connection.CreateDataReader(sql);
    while (reader.Read())
        yield return (reader as IDataRecord).Cast<T>();
}
```

这里的`CreateDataReader()`和`Cast()`都是博主自定义的扩展方法：

```CSharp
private static IDataReader CreateDataReader(this IDbConnection connection, string sql)
{
    var command = connection.CreateCommand();
    command.CommandText = sql;
    command.CommandType = CommandType.Text;
    return command.ExecuteReader();
}

private static T Cast<T>(this IDataRecord record) where T:class, new()
{
    var instance = new T();
    foreach(var property in typeof(T).GetProperties())
    {
        var index = record.GetOrdinal(property.Name);
        if (index < 0) continue;
        var propertyType = property.PropertyType;
        if (propertyType.IsGenericType && 
          propertyType.GetGenericTypeDefinition() == typeof(Nullable<>))
            propertyType = Nullable.GetUnderlyingType(propertyType);
        property.SetValue(instance, 
          Convert.ChangeType(record[property.Name], propertyType));
    } 

    return instance;  
}
```

而`Execute()`方法则要简单的多，因为从`IDbConnection`到`IDbCommand`的这条线，可以直接通过`CreateCommand()`来实现：

```CSharp
public static int Execute(this IDbConnection connection, string sql, 
  object param = null, IDbTransaction trans = null)
{
    var command = connection.CreateCommand();
    command.CommandText = sql;
    command.CommandType = CommandType.Text;
    return command.ExecuteNonQuery();
}
```
# 实现参数化查询

大家可以注意到，我这里的参数param完全没有用上，这是因为`IDbCommand`的`Paraneters`属性显然是一个抽象类的集合。所以，从`IDbConnection`的角度来看这个问题的时候，它又不知道这个参数要如何来给了，而且像Dapper里的参数，涉及到集合类型会存在`IN`和`NOT IN`以及批量操作的问题，比普通的字符串替换还要稍微复杂一点。如果我们只考虑最简单的情况，它还是可以尝试一番的：

```CSharp
private static void SetDbParameter(this IDbCommand command, object param = null)
{
    if (param == null) return;
    if (param is IDictionary<string, object>)
    {
        //使用字典作为参数
        foreach (var arg in param as IDictionary<string, object>)
        {
              var newParam = command.CreateParameter();
              newParam.ParameterName = $"@{arg.Key}";
              newParam.Value = arg.Value;
              command.Parameters.Add(newParam);
        }
    }
    else 
    {
        //使用匿名对象作为参数
        foreach (var property in param.GetType().GetProperties())
        {
              var propVal = property.GetValue(param);
              if (propVal == null) continue;
              var newParam = command.CreateParameter();
              newParam.ParameterName = $"@{property.Name}";
              newParam.Value = propVal;
              command.Parameters.Add(newParam);
        }
    }
}
```
相应地，为了能在`Query<T>()`和`Execute()`两个方法中使用参数，我们需要修改相关的方法：

```CSharp
public static int Execute(this IDbConnection connection, string sql, 
  object param = null, IDbTransaction trans = null)
{
    var command = connection.CreateCommand();
    command.CommandText = sql;
    command.CommandType = CommandType.Text;
    command.SetDbParameter(param);
    return command.ExecuteNonQuery();
}

private static IDataReader CreateDataReader(this IDbConnection connection, string sql, 
  object param = null)
{
    var command = connection.CreateCommand();
    command.CommandText = sql;
    command.CommandType = CommandType.Text;
    command.SetDbParameter(param);
    return command.ExecuteReader();
}
```

现在，唯一的问题就剩下`DbType`和`@`啦，前者在不同的数据库中可能对应不同的类型，后者则要面临Oracle这朵奇葩的兼容性问题，相关内容可以参考在这篇博客：[Dapper.Contrib在Oracle环境下引发ORA-00928异常问题的解决](https://blog.yuanpei.me/posts/3086300103/)。到这一步，我们基本上可以实现类似Dapper的效果。当然，我并不是为了重复制造轮子，只是像从Dapper这样一个结果反推出相关的技术细节，从而可以串联起整个ASO.NET甚至是Entity Framework的知识体系，工作中解决类似的问题非常简单，直接通过NuGet安装Dapper即可，可如果你想深入了解某一个事物，最好的方法就是亲自去探寻其中的原理。现在基础设施越来越完善了，可有时候我们再找不回编程的那种快乐，大概是我们内心深处放弃了什么.....

考虑到，从微软的角度，它鼓励我们为每一家数据库去实现数据库驱动，所以，它定义了很多的抽象类。而从ORM的角度来考虑，它要抹平不同数据库的差异，Dapper的做法是给`IDbConnection`写扩展方法，而针对每个数据库的“方言”，实际上不管什么ORM都要去做这部分“脏活儿”，以前是分给数据库厂商去做，现在是交给ORM设计者去做，我觉得ADO.NET里似乎缺少了一部分东西，它需要提供一个IDbAdapterProvider的接口，返回IDbAdapter接口，这样就可以不用关心它是被如何创建出来的。你看，同样是设计接口，可微软和ServiceStack俨然是两种不同的思路，这其中的差异，足可窥见一斑矣！实际上，Entity Framework就是在以ADO.NET为基础发展而来的，在这个过程中，还是由厂商来实现对应的Provider。此时此刻，你悟到了我所说的“温故而知新”了嘛？

# 本文小结

本文实则由针对DataSet/DataTable的吐槽而引出，在这个过程中，我们重新温习了ADO.NET中`DbConnection`、`DbCommand`、`DbDataReader`、`DbDataAdapter`这些关键的组成部分，而为了解决DataTable在使用上的种种不变，我们想到了借鉴Dapper中的DapperRow来实现“动态查询”，由此引出了.NET中实现dynamic最重要的一个接口：`IDynamicMetaObjectProvide`，这使得我们可以在查询数据库的时候返回一个dynamic的集合。而为了更接近Dapper一点，我们基于扩展方法的形式为`IDbConnection`编写了`Query<T>()`和`Execute()`方法，在数据库读写层面上彻底终结了DataSet/DataTable的生命。最后，我们实现了一个简化版本的参数化查询，同样是借鉴Dapper的思路。这说明一件什么事情呢？**当你在一个看似合理、结局固定的现状中无法摆脱的时候，“平躺”虽然能让你获得一丝喘息的机会，但与此同时，你永远失去了跳出这个层级去看待事物的机会**，就像我以前吐槽同事天天用`StringBuider`拼接字符串一样，一味地吐槽是没有什么用的，重要的是你会选择怎么做，所以，后来我向大家推荐了[Linquid](https://github.com/dotliquid/dotliquid)，**2021年已经来了，希望你不只是增长了年龄和皱纹**，晚安！



 