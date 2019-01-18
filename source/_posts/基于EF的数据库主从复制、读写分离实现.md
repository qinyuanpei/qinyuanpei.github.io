---
title: 基于EF的数据库主从复制、读写分离实现
categories:
  - 数据存储
tags:
  - EF
  - 读写分离
  - 主从复制
abbrlink: 2418566449
date: 2018-10-18 08:41:08
---
&emsp;&emsp;各位朋友，大家好，欢迎大家关注我的博客，我是Psyne，我的博客地址是[https://blog.yuanpei.me](https://blog.yuanpei.me)。在上一篇博客中，我们提到了通过DbCommandInterceptor来实现EF中SQL针对SQL的“日志”功能。我们注意到，在这个拦截器中，我们可以获得当前数据库的上下文，可以获得SQL语句中的参数，更一般地，它具备“AOP”特性的扩展能力，可以在执行SQL的前后插入相应的动作，这就有点类似数据库中触发器的概念了。今天，我们主要来说一说，基于EF实现数据库主从复制和读写分离，希望这个内容对大家有所帮助。

# 主从复制 ＆ 读写分离
&emsp;&emsp;首先，我们先来了解一个概念：主从复制。那么，什么是主从复制呢？通常，在只有一个数据库的情况下，这个数据库会被称为**主数据库**。所以，当有多个数据库存在的时候，数据库之间就会有主从之分，而那些和主数据库完全一样的数据库就被称为**从数据库**，所以，**主从复制其实就是指建立一个和主库完全一样的数据库环境**。

&emsp;&emsp;那么，我们为什么需要主从复制这种设计呢？我们知道，主数据库一般用来存储实时的业务数据，因此如果主数据库服务器发生故障，从数据库可以继续提供数据服务，这就是主从复制的优势之一，**即作为数据提供灾备能力**。其次，从业务扩展性上来讲，互联网应用的业务增长速度普遍较高，随着业务量越来越大，I/O的访问频率越来越高，在单机磁盘无法满足性能要求的情况下，**通过设置多个从数据库服务器，可以降低磁盘的I/O访问频率，进而提高单机磁盘的读写性能**。从业务场景上来讲，数据库的性能瓶颈主要在读即查询上，**因此将读和写分离，能够让数据库支持更大的并发，这对优化前端用户体验很有意义**。

&emsp;&emsp;通常来讲，不同的数据库都在数据库层面上实现了主从复制，各自的实现细节上可能会存在差异，譬如SQLServer中可以通过“发布订阅”来配置主从复制的策略，而Oracle中可以通过DataGurd来实现主从复制，甚至你可以直接把主库Dump出来再导入到从库。博主没有能力详细地向大家介绍它们的相关细节，可博主相信“万变不离其宗”的道理，这里我们以MySQL为例，因为它在互联网应用中更为普遍，虽然坑会相应地多一点:)……

&emsp;&emsp;MySQL中有一种最为重要的日志binlog，即二进制日志，它记录了所有的DDL和DML(除查询以外)语句，通过这些日志，不仅可以作为灾备时的数据恢复，同样可以传递给从数据库来达到数据一致的目的。具体来讲，对于每一个主从复制的连接，都有三个线程，即拥有多个从库的主库为每一个从库创建的**binlog输出线程**，从库自身的**IO线程**和**SQL线程**：
* 当从库连接到主库时，主库就会创建一个线程然后把binlog发送到从库，这是binlog输出线程。
* 当从库执行START SLAVER以后，从库会创建一个I/O线程，该线程连接到主库并请求主库发送binlog里面的更新记录到从库上。从库I/O线程读取主库的binlog输出线程发送的更新并拷贝这些更新到本地文件(其中包括relay log文件)。
* 从库创建一个SQL线程，这个线程读取从库I/O线程写到relay log的更新事件并执行。

# EF中主从复制的实现
&emsp;&emsp;虽然从数据库层面上做主从复制会更简单一点，可在很多时候，这些东西其实更贴近DBA的工作，而且不同数据库在操作流程上还都不一样，搞这种东西注定不能成为“通用”的知识领悟。对开发人员来说，EF和Dapper这样的ORM更友好一点，如果可以在ORM层面上做触发器和存储过程，可能SQL看起来就没有那么讨厌了吧！博主的公司因为要兼顾主流的数据库，所以，不可能在数据库层面上去做主从复制，最终我们是通过EF来实现主从复制。

&emsp;&emsp;其实，讲了这么多主从复制的原理，对我们来说，这篇文章的实现则是非常简单的。因为通过DbCommandInterceptor我们能拦截到SQL命令，所以，只要是Select命令全部走从库，Insert/Update/Delete全部走主库，这样就实现了读写分离。怎么样，是不是感觉相当简单啊！当然，前提是要准备好主从库的屋里环境，这些就让DBA去折腾吧(逃。好了，下面一起来看具体代码，首先我们定义一个主从库管理类MasterSlaveManager：
```CSharp
public static class MasterSlaveManager
{
    private static MasterSalveConfig _config => LoadConfig();

    /// <summary>
    /// 加载主从配置
    /// </summary>
    /// <param name="fileName">配置文件</param>
    /// <returns></returns>
    public static MasterSalveConfig LoadConfig(string fileName = "masterslave.config.json")
    {
        if (!File.Exists(fileName)) throw new Exception(string.Format("配置文件{0}不存在", fileName));
        return JsonConvert.DeserializeObject<MasterSalveConfig>(File.ReadAllText(fileName));
    }

    /// <summary>
    /// 切换到主库
    /// </summary>
    /// <param name="command">DbCommand</param>
    public static void SwitchToMaster(DbCommand command, string serverName = "")
    {
        var masterServer = string.IsNullOrEmpty(serverName) ? 
            _config.Masters.FirstOrDefault() : _config.Masters.FirstOrDefault(e => e.ServerName == serverName);
        if (masterServer == null) throw new Exception("未配置主库服务器或者服务器名称不正确");
        //切换数据库连接
        ChangeDbConnection(command, masterServer);
    }

    /// <summary>
    /// 切换到从库
    /// </summary>
    /// <param name="command">DbCommand</param>
    public static void SwitchToSlave(DbCommand command, string serverName = "")
    {
        var salveServer = string.IsNullOrEmpty(serverName) ?
             _config.Slaves.FirstOrDefault() : _config.Slaves.FirstOrDefault(e => e.ServerName == serverName);
        if (salveServer == null) throw new Exception("未配置从库服务器或者服务器名称不正确");
        //切换数据库连接
        ChangeDbConnection(command, salveServer);
    }

    /// <summary>
    /// 切换数据库连接
    /// </summary>
    /// <param name="command"></param>
    /// <param name="dbServer"></param>
    private static void ChangeDbConnection(DbCommand command, DbServer dbServer)
    {
        var conn = command.Connection;
        if (conn.State == System.Data.ConnectionState.Open) conn.Close();
        conn.ConnectionString = dbServer.ConnectionString;
        conn.Open();
    }
}
```
接下来，和之前关于EF中的SQL拦截器类似，我们定义一个名为MasterSlaveDbInterceptor的拦截器：
```CSharp
public class MasterSlaveDbInterceptor : DbCommandInterceptor
{
    public override void NonQueryExecuting(DbCommand command, DbCommandInterceptionContext<int> interceptionContext)
    {
        //Insert/Update(写操作)走主库
        MasterSlaveManager.SwitchToMaster(command);
        base.NonQueryExecuting(command, interceptionContext);
    }

     public override void ScalarExecuting(DbCommand command, DbCommandInterceptionContext<object> interceptionContext)
    {
        //Select(读操作)走从库
        var sqlText = command.CommandText;
        if (!sqlText.ToUpper().StartsWith("INSERT") || !sqlText.ToUpper().StartsWith("UPDATE"))
            MasterSlaveManager.SwitchToSlave(command);
        base.ScalarExecuting(command, interceptionContext);
    }

    public override void ReaderExecuting(DbCommand command, DbCommandInterceptionContext<DbDataReader> interceptionContext)
    {
        //Select(读操作)走从库
        var sqlText = command.CommandText;
        if (!sqlText.ToUpper().StartsWith("INSERT") || !sqlText.ToUpper().StartsWith("UPDATE"))
            MasterSlaveManager.SwitchToSlave(command);
        base.ReaderExecuting(command, interceptionContext);
    }
}
```
至此，我们就实现了基于EF的数据库主从复制、读写分离。其实，更严谨的说法是，主从复制是在数据层面上完成的，而读写分离则是在代码层面上完成。当然，实际应用中需要考虑事务、数据库连接等因素，这里我们仅仅提供一种思路。这里我们的配置文件中，对主、从数据库进行了简单配置，即一主一从。在实际应用中，可能我们会遇到一注多从的情况，在这个基础上，我们又可以延申出新的话题，譬如在存在多个从库的情况下，通过心跳检测来检查从库服务器的健康状态，以及如何为不同的从库服务器设置权重，实现多个从库服务器的负载均衡等等。我们在微服务中提出的**“健康检查”**和**“负载均衡”**等概念，其实都可以映射到这里来，我想这是真正值得我们去深入研究的地方。

# 本文小结

&emsp;&emsp;并没有，いじょう