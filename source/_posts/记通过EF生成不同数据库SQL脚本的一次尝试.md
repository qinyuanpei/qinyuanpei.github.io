---
title: 记通过EF生成不同数据库SQL脚本的一次尝试
categories:
  - 编程语言
tags:
  - EF
  - .NET Core
  - Logger
abbrlink: 795474045
date: 2018-09-17 09:42:23
---
&emsp;&emsp;接触新项目有段时间了，如果让我用一句话来形容此刻的感受，大概就是**“痛并快乐着”**。痛苦之一是面对TFS，因为它的分支管理实在是一言难尽，无时无刻不在体验着人肉合代码的“趣味”。而痛苦之二是同时维护三套数据库的脚本，这让我想到一个梗，在讲到设计模式的时候，一个常常被提到的场景是，怎么样从设计上支持不同数据库的切换。我想，这个问题是非常容易回答的，真正的问题是我们真的需要切换数据库吗？原谅我的年少无知，我们的产品因为要同时支持公有云和私有化部署，所以在数据库的选择上，覆盖到了主流MySQL、Oracle和SQL Server，这直接导致我们要维护三套数据库的脚本，你说这样子能不痛苦吗？而快乐的地方在于，终于有机会在一个有一定用户体量的产品上参与研发，以及从下周开始我们将从TFS切换到Git。好了，今天这篇文章的主题是，**通过EF来生成不同数据库的SQL脚本**，这是痛苦中的一次尝试，所谓**“痛并快乐着”**。

# 基本原理
&emsp;&emsp;我们知道数据库和面向对象这两者间存在着天然阻抗，这是因为两者在事物的认知上存在差异，数据库关注的是二维表、是集合间的关系，而面向对象关注的是封装、是细节的隐藏，所以，不管到什么时候，这两者都只能以某种尴尬的方式共存，SQL执行效率高，这是以牺牲可读性为代价的； ORM迎合了面向对象，这是以牺牲性能为代价的，所以，即使到了今天，关于SQL和ORM的争论从来没有停止过，甚至写SQL的人不知不觉间“造”出了ORM，而使用ORM的人有时需要SQL。所以，面对这样一个需要同时维护三套数据库脚本的工作，我个人倾向于用工具去生成，或许是出于程序员对“懒”这种美德的极致追求，或许是出于我对SQL这种“方言”天生的排斥，总而言之，我不是很喜欢手写SQL除非特别必要，因为它和正则一样，只有写得人懂它真正的含义。

&emsp;&emsp;那么，说到这里，我们就知道了一件事情，ORM可以帮助我们生成SQL，所以，我们为什么不让它帮我们生成不同数据库的SQL脚本呢？虽然ORM的性能总是为人所诟病，因为它严格遵循某种规则，所以注定做不到像人类一样“灵活”。我们始终认为不“灵活”的就是“笨拙”的，可即便如此ORM生成的SQL依然比人类写得要好看。故而，我们的思路是，**在ORM生成SQL语句的时候将其记录下来，然后按照一定规则生成不同数据库的脚本**。毕竟SQL语言更接近“方言”，每一种数据库的SQL脚本都存在着细微的差别。所以，后来人们不得不发明T-SQL，可任何东西归根结底不都是权力和利益带来的附属品吗？人类为了互相竞争而形成差异化，可当一切差异都不甚明显时，最终又不得不花费精力来解决这些差异。可一个只有垄断存在的世界，除了让人想起1984里的Big Brother以外，还能想起什么呢？

# 尝试过程
&emsp;&emsp;好了，顺着这个思路，我们就会想到在ORM中添加拦截器或者是日志的方式，来获得由ORM生成的SQL语句，这里我们以Entity Framework(以下简称EF)为例，这是.NET中最常见的ORM，因为目前官方的Web开发框架有ASP.NET和ASP.NET Core两个版本，所以这里我们分别以ASP.NET和ASP.NET Core为例来说明具体的实现过程，相应地，我们分别使用了EF6和EF Core 作为各自的ORM。 

## EF6 
&emsp;&emsp;对于EF6，我们可以通过继承**DbCommandInterecptor**类来编写一个拦截器。而在拦截器中重写相应的方法，就可以对数据库中的常见操作(CURD)进行拦截。所以，根据这个思路，我们会联想到，通常数据库迁移都是针对“写”这个操作，因此，我们的想法是记录INSERT和UPDATE两种SQL语句。这里我们通过下面的示例来验证这个想法，需要说明的是，本文中所有数据库相关的示例，均采用Code First的方式来创建。
```CSharp
public class SQLGenInterceptor : DbCommandInterceptor
{
    public override void NonQueryExecuting(DbCommand command, DbCommandInterceptionContext<int> interceptionContext)
    {
        var sqlText = FormatSQL(command);
        Log.Info(sqlText);
    }

    public override void ReaderExecuting(DbCommand command, DbCommandInterceptionContext<DbDataReader> interceptionContext)
    {
        var sqlText = FormatSQL(command);
        Log.Info(sqlText);
    }

    public override void ScalarExecuting(DbCommand command, DbCommandInterceptionContext<object> interceptionContext)
    {
        var sqlText = FormatSQL(command);
        Log.Info(sqlText);
    }

    private string FormatSQL(DbCommand command)
    {
        var sqlText = command.CommandText;
        foreach (DbParameter sqlParam in command.Parameters)
        {
            sqlText = sqlText.Replace(sqlParam.ParameterName,            sqlParam.Value.ToString());
        }

        return sqlText;
    }
}
```

&emsp;&emsp;在这个示例中，我们使用NLog来记录由EF生成的SQL语句，可以注意到它比我们想象中的要稍微复杂些，所以，人们说ORM性能差并不是没有道理。可当你见过那些由人手写出的天书一般的SQL语句后，也许两者在可读性上来说不过是五十步笑百步。实际上EF生成的SQL是一种叫做T-SQL的东西，你可以把它理解为一种标准的SQL语言。譬如在PowerBuilder这个数据库建模软件中，我们可以通过T-SQL转换出主流数据库的SQL语句。博主在工作中需要维护三套SQL脚本，而这些脚本间细小的语法差异，就变成了这个过程中最难忘的记忆，这里我们不考虑去做语法转换的事情，因为实际上通过传入不同的连接字符串，我们就能得到不同数据库的SQL脚本，所以接下来的工作就交给各位了(逃……

```CSharp
//注入SQLGen拦截器
DbInterception.Add(new SQLGenInterceptor());
using (var context = new DataContext())
{
    context.Users.Add(new User()
    {
        UserName = "PayneQin",
        UserRole = "Administrator"
    });

    context.SaveChanges();
}
```

&emsp;&emsp;现在，我们需要将这个拦截器注册到EF中，注册过程非常简单，一旦拦截器注册完成，当我们在EF中执行相应操作的时候，就可以在日志中看到相对应的SQ语句了，这样我们就达到了用EF生成SQL语句的目的，虽然说这样可能还没手写来快，可它至少让你知道了，这个世界上有一种不需要手写SQL的可能性啊，你说对吗？

![EF生成SQL语句比想象中更为复杂](https://ws1.sinaimg.cn/large/4c36074fly1fz05glt2tij20j306x74e.jpg)

## EF Core
&emsp;&emsp;对于EF Core来说，它并没有提供像EF6那样的拦截器，虽然官方曾经说过后续会做这方面的工作[摊手]……不过办法终究是人想出来的，对于EF Core我们可以通过注入日志的方式来实现。我们知道，微软在.NET Core中大力地发展了依赖注入、中间件等一系列特性，所以，这对于我们这种喜欢搞事情的人来说，简直太方便了有木有啊！.NET Core中日志注入主要集中在ILogger、ILoggerFactory和ILoggerProvider三个接口，简单来说，ILoggerFactory是日志工厂，负责返回具体的Logger；而ILoggerProvider，则决定在什么情况下应该提供什么样的Logger。最常见的两种LoggerProvider是Console和Debug，它们分别通过AddConsole()和AddDebug()来注入。具体到这里，我们通过下面的方式实现：

```CSharp
public class SQLGenLogger : ILogger
{
    private readonly string categoryName;
    public SQLGenLogger(string categoryName) => this.categoryName = categoryName;
    public IDisposable BeginScope<TState>(TState state) => null;
    public bool IsEnabled(LogLevel logLevel) => true;
    public void Log<TState>(LogLevel logLevel, EventId eventId, TState state, Exception exception, Func<TState, Exception, string> formatter)
    {
        Log.Info(state)
    }
}
```

&emsp;&emsp;首先定义SQLGenLogger，顾名思义，它是用来记录生成的SQL语句的，同样，我们选择了NLog。这里有一点要说明，平时我们在控制器中使用ILogger的时候，通常会在控制器的构造函数中注入ILogger<FooController>，一旦我们使用泛型的ILogger接口，Log()方法中的参数state实际上就是当前类型，这里和SQL语句相关的类型DbCommandData，实际上是博主试出来的，因为如果不限定ILogger<T>中的参数T，我们将得到所有的执行日志，显然，这不是我们想要的结果。

```CSharp
public class SQLGenLoggerProvider : ILoggerProvider
{
    public ILogger CreateLogger(string categoryName)
    {
        if(categoryName  == "Microsoft.EntityFrameworkCore.Database.Command")
            return new SQLGenLogger(categoryName);
        return NullLogger.Instance;
    }

    public void Dispose()
    {

    }
}
```

&emsp;&emsp;接下来来看，ILoggerProvider接口的实现。我们说过，ILoggerProvider接口决定在什么情况下应该提供什么样的Logger，我们注意到它提供了一个CreateLogger()的方法，它会根据categoryName来返回不同的Logger，而参数categoryName实际上等价与nameof(FooController)，所以，到这里我们就会明白，为什么这里要判断categoryName了，它实际上起一个过滤的作用，因为我们只需要SQL相关的日志，它和SQLGenLogger中的state相对应，我们已经说过，这是博主试出来的。

```CSharp
public class DataContext : DbContext
{
    public virtual DbSet<User> Users { get; set; }
    protected override void OnConfiguring(DbContextOptionsBuilder optionsBuilder)
    {
        var loggerFactory = new LoggerFactory();
        loggerFactory.AddProvider(new SQLGenLoggerProvider());
        //在这里注入日志工厂
        optionsBuilder.UseLoggerFactory(loggerFactory)
            .EnableSensitiveDataLogging()
            .UseSqlServer(@"Data Source=(LocalDb)\MSSQLLocalDB;Initial Catalog=SQLGen.DataContext;Integrated Security=True;MultipleActiveResultSets=True;App=EntityFramework"); 
  }

  protected override void OnModelCreating(ModelBuilder modelBuilder)
  {
  		modelBuilder.ApplyConfiguration(new UserTypeMap());
  		modelBuilder.Entity<User>().ToTable("Users");
  }
}
```

&emsp;&emsp;好啦，接下来就非常简单啦，我们在DbContext里对EF的Logger进行配置，把我们定义的SQLGenLoggerProvider注入到EF里，可以注意到，它可以如我们期望得那样，输出由EF生成的SQL脚本，这实在是有趣，Ok，打完收工！

![通过注入日志获取EF生成的SQL](https://ws1.sinaimg.cn/large/4c36074fly1fz02250ixxj20u904w74c.jpg)


# 本文小结
&emsp;&emsp;我一直相信，懒惰是工程师的一种美德，因为为了让自己有机会懒惰，你就必须要先让自己勤奋起来。我一直怕自己在舒适区里温水煮青蛙，明明一直在重复做一件事情，还要安慰自己说：“做好这一件事情一样是成功“，有时候，一味地重复自己并不见得会有太多收获，所以，就像这篇文章一样，我本来像偷懒少写一点SQL，结果意外地发现了给数据库记录日志的方法。当有了意外收获以后，曾经的初衷到底是什么可能就没那么重要了，如“雨血”中左殇所说，当你赢了的时候，你说曾经有十成把握亦不为过。

&emsp;&emsp;这篇文章主要介绍如何利用EF来生成不同数据库的SQL脚本，对EF6来说，需要继承DbCommandInterecptor类编写拦截器；对于EF Core来说，需要注入ILogger来记录日志。本文的延伸之一是记录SQL执行日志，这一点在本文已经有所体现。本文更深层次的延伸是，在这个基础上实现数据库的主从复制、读写分离，这一点我会在下一篇博客中讲解，欢迎大家继续关注我的博客，好啦，以上就是这篇文章的全部内容啦，晚安！

