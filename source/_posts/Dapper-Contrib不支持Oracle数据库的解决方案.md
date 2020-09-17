---
toc: true
title: Dapper.Contrib在Oracle环境下引发ORA-00928异常问题的解决
categories:
  - 数据存储
tags:
  - Dapper
  - ORM
  - 数据库
copyright: true
abbrlink: 3086300103
date: 2020-09-05 14:28:20
---
话说最近这两周里，被迫官宣**996**的生活实在是无趣，在两周时间里安排三周的工作量，倘若用丞相的口吻来说，那便是: **我从未见过有如此厚颜无耻之人**。无法为工作的紧急程度排出优先级，这便是身为肉食者们的**鄙**。古人云：**肉食者鄙，未能远谋**，诚不欺我也。一味地追求快速迭代，“屎”山越滚越高没有人在乎；一味地追求功能叠加，技术债务越来越多没有人在乎。所以，本着“多一事不如少一事”的原则，直接通过 Dapper 写 SQL 语句一样没有问题，因为被压榨完以后的时间只能写这个。在今天的这篇博客里，我想和大家分享的是，`Dapper.Contrib`在操作 Oracle 数据库时引发 **ORA-00928: 缺失 SELECT 关键字** 这一错误背后的根本原因，以及 Dapper 作为一个轻量级 ORM 在设计上做出的取舍。

# 问题回顾
在使用 `Dapper.Contrib` 操作 Oracle 数据库的时候，通过 Insert() 方法来插入一个实体对象，此时，会引发 **ORA-00928: 缺失 SELECT 关键字** 这种典型的 Oracle 数据库错误，对于经常使用 Dapper 的博主而言，对于 `@` 还是 `:` 这种无聊的语法还是有一点经验的，在尝试手写 SQL 语句后，发现使用 Dapper 提供的 `Execute()` 扩展方法一点问题都没有，初步判定应该是 `Dapper.Contrib` 这个扩展库的问题，在翻阅 `Dapper` 的源代码以后，终于找到了问题的根源所在，所以，下面请跟随博主的目光，来一起解读解读 `Dapper.Contrib` 这个扩展库，相信你看完以后就会明白，为什么这里会被 Oracle 数据库摆上一道，以及为什么它至今都不考虑合并 Oracle 数据库相关的PR。

# 原因分析
众所周知，`Dapper` 的核心其实就是一个 SqlMapper ，它提供的 Query() 和 Execute() 接口本身都是附加在 `IDbConnection` 接口上的扩展方法，所以，最基础的 `Dapper` 用法其实是伴随着 SQL 语句和以匿名对象为主的参数化查询，这可以说是 Dapper 的核心，而 `Dapper.Contrib` 在这个基础上提供了 Get()、Insert()、Delete() 和 Update() 等等常见的 CRUD 方法，这些方法都针对的是单主键的表，让 `Dapper`有了一点 ORM 的感觉，可惜的是 `Dapper.Contrib` 的实现是不完整的，主要是指下面两个方面，即：第一，官方未能提供 Oracle 版本的 `ISqlAdapter`。第二，兼容不同数据库自增ID的实现，让官方在处理Id的参数化查询时束手束脚，对 `ISqlAdapter` 的设计并不全面。

## Oracle版本的ISqlAdapter
首先，第一个结论，`Dapper.Contrib` 没有实现 Oracle 版本的 `ISqlAdapter` 。关于这个接口，我们可以在 `SqlMapperExtensions` 这个类中找到定义，而 `Dapper.Contrib` 内部实际上是维护了一个字典 `AdapterDictionary` ，在 `SqlMapperExtensions.cs` 文件的第 62 行 ~ 第 73 行，我们可以注意到，其内部提供了6种 `ISqlAdapter` 的实现，且默认为 `SqlServerAdapter` ：

```CSharp
private static readonly ISqlAdapter DefaultAdapter = new SqlServerAdapter();
private static readonly Dictionary<string, ISqlAdapter> AdapterDictionary
    = new Dictionary<string, ISqlAdapter>(6)
      {
          ["sqlconnection"] = new SqlServerAdapter(),
          ["sqlceconnection"] = new SqlCeServerAdapter(),
          ["npgsqlconnection"] = new PostgresAdapter(),
          ["sqliteconnection"] = new SQLiteAdapter(),
          ["mysqlconnection"] = new MySqlAdapter(),
          ["fbconnection"] = new FbAdapter()
    };
```

一个自然而然的问题是，这个 `ISqlAdapter` 接口是做什么的呢？为什么说 `Dapper.Contrib` 没有实现 Oracle 版本的 ISqlAdapter 呢？如果我们看一下 `ISqlAdapter` 的定义，就可以了解到其作用是告诉 Dapper ，应该怎么样处理数据库里的自增ID、怎么样表示 `Column = Value` 这样的结构，以及怎么样处理列名：

```CSharp
public partial interface ISqlAdapter
{
    int Insert(IDbConnection connection, IDbTransaction transaction, 
        int? commandTimeout, string tableName, string columnList, 
        string parameterList, IEnumerable<PropertyInfo> keyProperties, 
        object entityToInsert
    );
    void AppendColumnName(StringBuilder sb, string columnName);
    void AppendColumnNameEqualsValue(StringBuilder sb, string columnName);
}
```

这里以 `MySqlAdapter` 的实现为例：

```CSharp
public partial class MySqlAdapter : ISqlAdapter
{
    public int Insert(IDbConnection connection, IDbTransaction transaction, 
        int? commandTimeout, string tableName, string columnList, 
        string parameterList, IEnumerable<PropertyInfo> keyProperties, 
        object entityToInsert
    )
    {
        var cmd = $"insert into {tableName} ({columnList}) values ({parameterList})";
        connection.Execute(cmd, entityToInsert, transaction, commandTimeout);
        var r = connection.Query("Select LAST_INSERT_ID() id", transaction: transaction, commandTimeout: commandTimeout);

        var id = r.First().id;
        if (id == null) return 0;
        var propertyInfos = keyProperties as PropertyInfo[] ?? keyProperties.ToArray();
        if (propertyInfos.Length == 0) return Convert.ToInt32(id);

        var idp = propertyInfos[0];
        idp.SetValue(entityToInsert, Convert.ChangeType(id, idp.PropertyType), null);

        return Convert.ToInt32(id);
    }

    public void AppendColumnName(StringBuilder sb, string columnName)
    {
        sb.AppendFormat("`{0}`", columnName);
    ｝

    public void AppendColumnNameEqualsValue(StringBuilder sb, string columnName)
    {
        sb.AppendFormat("`{0}` = @{1}", columnName, columnName);
    }
}
```

相信看到这里的时候，大家会和我一样感到失望，因为 Dapper 的底层依然是在拼 SQL ，尤其是看到 `AppendColumnNameEqualsValue()` 这个方法的时候，会有一种恍然大明白的感觉，因为 @ 这个符号对于 Dapper 的参数化查询而言，实在是熟悉得不能再熟悉了。我们都知道为 Dapper 写 SQL 语句的时候，要对 Oracle 区别对待，因为这个奇葩非要用 `:` 这个奇怪的符号。回到我们一开始的问题，为啥 `Dapper.Contrib` 在 Oracle 环境下会提示 `ORA-XXXXX` 这种鬼都看不明白的错误，因为它在处理 SQL 的语句的时候依然使用的是 `@` 这个符号。这又是为什么呢？因为当指定的 `IDbConnection` 在 `AdapterDictionary` 中不存在的时候，它会使用默认的 `SqlServerAdapter` ，显然，全世界只有 Oracle 这个奇葩会用 `:` 这个奇怪的符号。我们不是在调用 Insert() 方法的时候提示这个错误吗？那么 `Dapper.Contrib` 是怎么实现 `Insert()` 方法的呢？这个部分实现主要在第 352 行 ~ 第 360 行：

```CSharp
var adapter = GetFormatter(connection);

for (var i = 0; i < allPropertiesExceptKeyAndComputed.Count; i++)
 {
    var property = allPropertiesExceptKeyAndComputed[i];
    adapter.AppendColumnName(sbColumnList, property.Name);  //fix for issue #336
    if (i < allPropertiesExceptKeyAndComputed.Count - 1)
       sbColumnList.Append(", ");
 }
```

显然，这部分是按照属性名去组织 `columnList` 和 `parameterList` 的过程，对于 Oracle ，永远是充满吐槽的，比如不加双引号则强制大写的设定，这意味着如果你的表名或者字段名是区分大小写的话，在 Oracle 这里都要加上双引号，这对 `Dapper.Contrib` 有什么影响呢？原本我们只需要给实体添加`[Table]`标签即可，而现在你不得不考虑带上反斜杠转义，甚至当你需要为 `DBeaver` 下载一个JDBC的驱动的时候，甲骨文这家公司居然要强制你去注册，对于一个习惯像`·.NET Core`、`GCC`、`Python`、`Lua` 和 `Node` 这样开箱即用的人来说，这就像强迫你注册一大堆真实信息，然后发现 API 接口完全无法匹配你的需求一样痛苦。关于 `GetFormatter()` 方法，它和我们猜想的完全一致：

```CSharp
private static ISqlAdapter GetFormatter(IDbConnection connection)
{
   var name = GetDatabaseType?.Invoke(connection).ToLower() ?? connection.GetType().Name.ToLower();
   return AdapterDictionary.TryGetValue(name, out var adapter) ? adapter : DefaultAdapter;
}
```

好了，在明白了以上种种因果关系以后，我们现在来考虑如何解决 Oracle 的问题。按照人类最直观的思维，既然它没有实现 Oracle 版本的 `ISqlAdapter` ，我自己实现一个不就好啦：
```CSharp
public class OracleSqlAdapter : ISqlAdapter
{
    public void AppendColumnName(StringBuilder sb, string columnName)
   {
        sb.AppendFormat("{0}", columnName);
   }

   public void AppendColumnNameEqualsValue(StringBuilder sb, string columnName)
   {
        sb.AppendFormat("{0} = :{1}", columnName, columnName);
   }

   public int Insert(IDbConnection connection, IDbTransaction transaction, int? commandTimeout, string tableName, 
            string columnList, string parameterList, IEnumerable<PropertyInfo> keyProperties, object entityToInsert)
   {
        var sql = $"insert into {tableName} ({columnList}) values ({parameterList})";
        return connection.Execute(sql, entityToInsert, transaction, commandTimeout);
    }

    public Task<int> InsertAsync(IDbConnection connection, IDbTransaction transaction, int? commandTimeout, string tableName, 
            string columnList, string parameterList, IEnumerable<PropertyInfo> keyProperties, object entityToInsert)
    {
         var sql = $"insert into {tableName} ({columnList}) values ({parameterList})";
         return connection.ExecuteAsync(sql, entityToInsert, transaction, commandTimeout);
    }
}
```
坦白说， `Dapper.Contrib` 这种纯静态类的设计，完全就不给别人留扩展的口子，为此，扩展方法 + 反射搞一个突破口：

```CSharp
 public static class SqlAdapterrExtensions
 {
        public static void UseSqlAdapter<TSqlAdapter>(this IDbConnection connection, TSqlAdapter sqlAdapter)
            where TSqlAdapter : ISqlAdapter, new()
        {
            var adapters = (Dictionary<string, ISqlAdapter>)
                    typeof(SqlMapperExtensions)
                    .GetField("AdapterDictionary", BindingFlags.NonPublic | BindingFlags.Instance | BindingFlags.Static)
                    ?.GetValue(null);

            var connectionType = connection.GetType().Name.ToLower();
            if (adapters != null && !adapters.ContainsKey(connectionType))
                adapters?.Add(connectionType, sqlAdapter);
        }
}
```

这样，我们不但可以满足眼下，还可以着眼未来，虽然未来有时候挺遥远，但梦想还是要有的，开闭原则，我做到了！改进后，我们这样处理即可：

```CSharp
connection = new OracleConnection(ConnectionStrings.Default);
connection.UseSqlAdapter(new OracleSqlAdapter());
```

此时，我们发现，我们解决了 Insert() 的问题，但随之而来的，Get()、Delete()、Update() 这一系列和主键相关的方法，都因为 `Dapper.Contrib` 中的主键设计而出现了问题，而这就是我们接下来要讲的主键Id参数化问题。

## 主键Id参数化问题
当我谈起这个问题的时候，我对于 `Dapper.Contrib` 中支持自增ID的坚持是怀疑的，因为在分布式盛行的今天，有大量的分布式ID生成方案供我们选择，比如基于 `Redis` 的号段策略，基于雪花算法的ID生成等等。大家会注意到我实现的 OracleSqlAdapter 在实现 Insert() 方法的时候简化了大量代码，这是因为我真的不知道，怎么从 Oracle 中获取一个新生成的ID，尤其是这个ID居然还要依赖一个我听都没有听说过的“序列”，而之所以要在 ISqlAdapter 中实现 Insert() 方法，最根本的原因就是，各个数据库对于自增ID的实现是不一样的，比如 MySQL 中使用的是 `SCOPE_IDENTITY()`，而 MSSQL 中使用的则是 `SCOPE_IDENTITY()` ，就因为这一点点差异，我们就必须要去折腾一遍，可以说， Dapper.Contrib 不支持 Oracle 的一个重要原因，就是在 Oracle 下实现自增ID太麻烦了。

既然大家都不用自增ID了，为什么还要在一个通用的ORM里折腾这个呢？说实话，我真担心有一天自增ID会溢出，谁让每个数据库里的上限都不一样呢？另一方面，既然Id在每个数据库的实现都不一样，那么，作为Id本身应该考虑放到 `ISqlAdapter` 接口中由使用者来实现啊，可偏偏 ISqlAdapter 里只定义了一个 Insert() 方法，所以，就算我们实现了 OracleSqlAdapter ，一样无法解决 Insert() 方法以外的其它方法在 Oracle 下面的问题，正因为如此，默认的 @ 符号在 Oracle 环境下下没有被完全替换掉，这就需要修改 Dapper.Contrib 的底层代码，这真的是一个不好的设计，因为使用者完全没有办法通过重写来覆盖某些默认行为，我们一起来看看，需要修改哪些地方：

```CSharp
public static T Get<T>(this IDbConnection connection, dynamic id, 
IDbTransaction transaction = null, int? commandTimeout = null) where T : class
{
    var type = typeof(T);

    if (!GetQueries.TryGetValue(type.TypeHandle, out string sql))
    {
        var key = GetSingleKey<T>(nameof(Get));
        var name = GetTableName(type);

        //第一个坏事儿的地方，为什么不用AppendColumnName()方法?
        sql = $"select * from {name} where {key.Name} = @id";
        GetQueries[type.TypeHandle] = sql;
    }

    var dynParams = new DynamicParameters();
    //第二个坏事的地方，什么不用AppendColumnName()方法??
    dynParams.Add("@id", id);

    //以下代码已省略
}
```

```CSharp        
public static long Insert<T>(this IDbConnection connection, T entityToInsert,
IDbTransaction transaction = null, int? commandTimeout = null) where T : class
{
    //以上代码已省略

    var sbParameterList = new StringBuilder(null);
    for (var i = 0; i < allPropertiesExceptKeyAndComputed.Count; i++)
    {
        //第三个坏事的地方，什么不用AppendColumnName()方法???
        var property = allPropertiesExceptKeyAndComputed[i];
        sbParameterList.AppendFormat("@{0}", property.Name);
        if (i < allPropertiesExceptKeyAndComputed.Count - 1)
            sbParameterList.Append(", ");
    }

    //以下代码已省略
}
```
其实，仔细阅读 Update() 和 Delete() 两个方法的实现，会发现它们都非常完美地避开了这一点，就是不知道为什么只有两个方法采用了不同地方式去拼接 SQL ，当然，这里我们会意识到有个列名的问题，尤其是在需要区分大小写的情况下，为此，我们可能需要去定义一个 ColumnAttribute，还能说什么呢？请和我大声地吐槽：**垃圾 Oracle ！**你看，就为了这一点点差异，我们不得不去额外写一点代码，所以，喊了很多年的去IOE，我表示举双手赞成。

事实上，社区里已经有类似的PR，可因为改动的范围比较大，官方至今都没有考虑过将其合并到主干分支上，所以，这个问题一直没有解决，这是一个悲伤的故事。

# 相关思考
在阅读 Dapper 源码的同时，我查阅了一个和 Dapper.Contrib 类似的项目：DapperExtension，我发现这个项目目前处在“荒废”的状态，因为它遇到了相同的问题，即 SQL 这门看起来统一实则相当不统一的语言，因为每一个数据库厂商几乎都在给标准“添砖加瓦“，就以自增ID为例，MySQL、MSSQL、Oracle 居然是三种不同的实现方式，尤其是 Oracle 这个奇葩，居然还需要定义一个序列来解决这个问题，这个奇葩给数据库加注释都那么另类，这带来的问题是什么？Dapper.Contrib 无力去实现 Oracle 的自增ID而放弃了 Oracle ，所以，即使社区里提交了PR，因为实现方式有点脏，官方一直没有合并到主干上去。

再回过头来看 Dapper.Contrib 支持自增ID的举动，总会觉得有点不合时宜，因为不同数据库自增ID的上限不一样不说，现在都普遍在分布式的环境中，数据库的自增ID其实是非常鸡肋的功能，而实际应用中常常会用 `Redis` 、雪花算法等来实现分布式ID，所以，当你回顾历史发展的趋势的时候，就会感慨有标准化的东西该多好，并不是说这个世界不需要多样性，显然这是一个标准约束性不强的领域，看起来大家都实现了SQL，无一例外地都夹藏了私货，对于商业行为而言，这无可厚非；可对于这个世界而言，这无疑增加了工作量。
有时候，当一个行业没有什么标准的时候，到底是突破勇气去率先制定标准，还是放弃自我去迎合各种不成文的规则，对于企业而言，是战略上的一种选择；而对于个人而言，其实是人生的一种选择。当彼时青春年少的人们，竞相以标新立异为荣的时候，如果想到有一天，终究要活成千篇一律的人生，为了生活而选择跪着的时候，内心又会有什么不一样的举动呢？

# 本文小结
本文分析了 Dapper.Contrib 这个扩展库，在搭配 Oracle 数据库使用时遇到 ORA-XXXXX 系列错误的原因及相应地处理方法，这个问题的表象是 Dapper.Contrib 没有实现 OracleSqlAdapter ，而更深层的原因，实际上是 Dapper.Contrib 选择支持自增ID而带来的 SQL 标准差异化问题。因为不同的数据库在实现自增ID时的机制不同，Oracle 甚至需要引入序列这个概念，这种差异化，增加了 Dapper 各个扩展库维护的工作量，这是官方一直不愿意实现 OracleSqlAdapter 的原因，其次， Dapper.Contrib 底层设计不合理，除了Insert() 方法以外，其它依赖主键的方法都没有提供扩展接口，导致使用者只能通过修改底层代码的方式解决问题，这严重违反开闭原则。好了，这是一篇利用996闲暇(可能是指做梦)写的一篇博客，如果文章中有什么不周到的地方，欢迎大家在博客下面给我留言，谢谢，晚安！