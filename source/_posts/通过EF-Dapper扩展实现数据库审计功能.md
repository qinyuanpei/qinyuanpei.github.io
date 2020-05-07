---
toc: true
title: 通过EF/Dapper扩展实现数据库审计功能
categories:
  - 数据存储
tags:
  - EF
  - Dapper
  - 审计
copyright: true
abbrlink: 1289244227
date: 2020-04-24 08:20:32
---
相信大家都有过周末被电话“吵醒”的经历，这个时候，客服同事会火急火燎地告诉你，客户反馈生产环境上某某数据“异常”，然后你花费大量时间去排查这些错误数据，发现这是客户使用某一种“骚”操作搞出来的“人祸”。可更多的时候，你不会这么顺利，因为你缺乏有力的证据去支持你的结论。最终，你不情愿地去处理了这些错误数据。你开始反思，为什么没有一种流程去记录客户对数据的变更呢？为什么你总要花时间去和客户解释这些数据产生的原因呢？好了，这就要说到我们今天这篇博客的主题——审计。

# 什么是审计？
结合本文引言中的描述的场景，当我们需要知道某条数据被什么人修改过的时候，或者是希望在数据变更的时候去通知某个人，亦或者是我们需要追溯一条数据的变更历史的时候，我们需要一种机制去记录数据表中的数据变更，这就是所谓的审计。而实际的业务中，可能会有类似，查询某一个员工一天内审批了多少单据的需求。你不要笑，人类常常如此无聊，就像我们有一个异常复杂的计费逻辑，虽然审计日志里记录了某个费用是怎么计算出来的，可花时间最多的地方，无一例外是需要开发去排查和解释的，对于这一点，我时常感觉疲于应对，这是我这篇文章里想要写审计的一个重要原因。

# EF/EF Core实体跟踪
EF和EF Core里都提供了实体跟踪的功能，我的领导经常吐槽我，在操作数据库的时候，喜欢显式地调用`repository.Update()`方法，因为他觉得项目中的实体跟踪是默认打开的。可当你学习了`Vue`以后，你了解到`Vue`中是检测不到数组的某些变化的，所以，这个事情我持保留意见，显式调用就显式调用呗，万一哪天人家把实体跟踪给关闭了呢？不过，话说回来，实体跟踪确实可以帮我们做一点工作的，其中，就包括我们今天要说的审计功能。

EF和EF Core中的实体追踪主要指DbContext类的ChangeTracker，而通过DetachChanges()方法，则可以获得那些变化了的实体的集合。所以，使用实体追踪来实现审计功能，本质上就是在SaveChanges()方法调用前后，记录实体中每一个字段的变化情况。为此，我们考虑编写下面的类——AuditDbContextBase，顾名思义，这是一个审计相关的DbContext基类，所以，希望实现审计功能的DbContext都会继承这个类。这里，我们重写其SaveChanges()方法，其基本定义如下：
```CSharp
public class AuditDbContextBase : DbContext, IAuditStorage
{
    public DbSet<AuditLog> AuditLog { get; set; }
    public AuditDbContextBase(DbContextOptions options, AuditConfig auditConfig) : base(options) { }
    public virtual Task BeforeSaveChanges() { }
    public virtual Task AfterSaveChanges() { }

    public override async Task<int> SaveChangesAsync(bool acceptAllChangesOnSuccess,
         CancellationToken cancellationToken = default)
    {
        await BeforeSaveChanges();
        var result = await base.SaveChangesAsync(acceptAllChangesOnSuccess, cancellationToken);
        await AfterSaveChanges();
        return result;
    }

    public void SaveAuditLogs(params AuditLog[] auditLogs)
    {
        AuditLog.AddRange(auditLogs);
        base.SaveChangesAsync();
    }
}
```
接下来，就是去实现`BeforeSaveChanges()`和`AfterSaveChanges()`两个方法：
```CSharp
//BeforeSaveChanges
public virtual Task BeforeSaveChanges()
{
    ChangeTracker.DetectChanges();
    _auditEntries = new List<AuditEntry>();
    foreach (var entityEntry in ChangeTracker.Entries())
    {
        if (entityEntry.State == EntityState.Detached 
            || entityEntry.State == EntityState.Unchanged)
            continue;
        if (entityEntry.Entity.GetType() == typeof(AuditLog))
            continue;
        if (_auditConfig.EntityFilters.Any(x => x(entityEntry)))
            continue;

        var auditEntry = new AuditEntry(entityEntry, _auditConfig);
        _auditEntries.Add(auditEntry);
    }

    return Task.CompletedTask;
}

//AfterSaveChanges
public virtual Task AfterSaveChanges()
{
    if (_auditEntries == null || !_auditEntries.Any())
        return Task.CompletedTask;

    _auditEntries.ForEach(auditEntry => auditEntry.UpdateTemporaryProperties());

    var auditLogs = _auditEntries.Select(x => x.AsAuditLog()).ToArray();
    if (!_auditConfig.AuditStorages.Any())
        _auditConfig.AuditStorages.Add(this);
    _auditConfig.AuditStorages.ForEach(
        auditStorage => auditStorage.SaveAuditLogs(auditLogs)
    );

    return Task.CompletedTask;
}
```
可以注意到，我们会在`SaveChanges()`方法执行前，通过`ChangeTracker.DetectChanges()`方法显式地捕获“变化"，这些“变化”会被存储到一个临时的列表中。而在`SaveChanges()`方法执行后，则会更新那些只有在数据提交后才可以获得的“临时”数据，最典型的例子是自增的ID，在数据提交前，我们是无法获得真正的ID的。这个列表中的内容最终会通过`AsAuditLog()`方法进行转化。下面是`AuditEntry`中的部分代码片段：
```CSharp
//SetValuesCollection
private void SetValuesCollection(List<PropertyEntry> properties)
{
    foreach (var property in properties)
    {
        var propertyName = property.Metadata.GetColumnName();
        if (_auditConfig.PropertyFilters.Any(x => x(_entityEntry, property)))
            continue;

        switch (OperationType)
        {
            case OperationType.Created:
                NewValues[propertyName] = property.CurrentValue;
            break;
            case OperationType.Updated:
                if (_auditConfig.IsIgnoreSameValue 
                    && property.OriginalValue.ToString() == property.CurrentValue.ToString())
                    continue;
                OldValues[propertyName] = property.OriginalValue;
                NewValues[propertyName] = property.CurrentValue;
            break;
            case OperationType.Deleted:
                OldValues[propertyName] = property.OriginalValue;
            break;
        }
    };
}

//AsAuditLog
public AuditLog AsAuditLog()
{
    return new AuditLog()
    {
        Id = Guid.NewGuid().ToString("N"),
        TableName = TableName,
        CreatedBy = string.Empty,
        CreatedDate = DateTime.Now,
        NewValues = NewValues.Any() ? JsonConvert.SerializeObject(NewValues) : null,
        OldValues = OldValues.Any() ? JsonConvert.SerializeObject(OldValues) : null,
        ExtraData = ExtraData.Any() ? JsonConvert.SerializeObject(ExtraData) : null,
        OperationType = (int)OperationType
    };
}
```
在此基础上，我们可以编写我们实际的DbContext，这里以CustomerContext为例，当我们向其中添加、修改和删除Customer的时候，就会触发审计相关的逻辑，默认情况下，审计产生的数据AuditLog和Customer在同一个数据库上下文中，当然，我们可以通过注入IAuditStore来实现更精细的控制，例如，可以将审计日志输入到文本文件，甚至是Mongodb这样的非关系型数据库里，因为有依赖注入的存在，这些实现起来会非常的简单！
```
//注入AuditLog配置
services.AddAuditLog(config => 
    config
    .IgnoreTable<AuditLog>()
    .IgnoreProperty<AuditLog>(x => x.CreatedDate)
    .WithExtraData("Tags", ".NET Core")
    .WithStorage<FileAuditStorage>()
    .WithStorage<MongoAuditStorage>()
);

//注入DbContext
services.AddDbContext<CustomerContext>(options =>
    options.UseSqlServer(Configuration.GetConnectionString("DefaultConnection")));

//像平时一样使用EF
var entity = _context.Customer.Where(x => x.Id == customer.Id).FirstOrDefault();
entity.Name = customer.Name;
entity.Email = customer.Email;
entity.Address = customer.Address;
entity.Tel = customer.Tel;
_context.Customer.Update(entity);
await _context.SaveChangesAsync();
```
下面是最终生成的审计日志信息：

![审计日志表展示](https://i.loli.net/2020/04/26/yefcJ1749L5TiMD.png)

# Castle动态代理
而对于像Dapper这种轻量级的ORM，它本身没有类似EF/EF Core的ChangeTracker的设计，如果我们在项目中使用Dapper，并且希望实现审计的相关功能，直观上看就会有一点困难。其实，平时在混合使用EF/Dapper的过程中，经常遇到的问题就是，如何确保传统的ADO.NET和EF在一个数据库事务中，如何确保Dapper和EF在一个数据库事务中等等。此时，我们就需要一点抽象，首先去实现一个Dapper的仓储模式，然后再借助Castle这类动态代理库实现对接口的拦截。这里以Dapper的扩展库Dapper.Contrib为例。首先，我们定义一个仓储接口IRepository:

```CSharp
public interface  IRepository
{
    TEntity GetByID<TEntity>(object id) where TEntity : class;

    TEntity GetByKeys<TEntity>(object keys) where TEntity : class;

    TEntity QueryFirst<TEntity>(string sql, object param) where TEntity : class;

    TEntity QuerySingle<TEntity>(string sql, object param) where TEntity : class;

    [AuditLog(OperationType.Created)]
    void Insert<TEntity>(params TEntity[] entities) where TEntity : class;

    [AuditLog(OperationType.Updated)]
    void Update<TEntity>(params TEntity[] entities) where TEntity : class;

    [AuditLog(OperationType.Deleted)]
    void Delete<TEntity>(params TEntity[] entities) where TEntity : class;

    void Delete<TEntity>(params object[] ids) where TEntity : class;

    IEnumerable<TEntity> GetByQuery<TEntity>(Expression<Func<TEntity,bool>> exps) where TEntity : class;

    IEnumerable<TEntity> GetByQuery<TEntity>(string sql, object param) where TEntity : class;

    IEnumerable<TEntity> GetAll<TEntity>() where TEntity : class;
}
```

接下来，我们就可以在拦截器中实现数据审计功能，因为Dapper本身没有ChangeTracker，所以，我们必须要在先从数据库中查出来OldValue，所以，实际效率应该并不会特别高，这里权当做为大家扩展思路吧！

```CSharp
public class AuditLogInterceptor : IInterceptor
{
    public void Intercept(IInvocation invocation)
    {
        var repository = invocation.Proxy as IRepository;
        var entityType = GetEntityType(invocation);
        var tableName = GetTableName(entityType);
        var tableIdProperty = entityType.GetProperty("Id");
        var auditLogAttrs = invocation.Method.GetCustomAttributes(typeof(AuditLogAttribute), false);
        if (auditLogAttrs == null || auditLogAttrs.Length == 0 || entityType == typeof(AuditLog))
        {
            invocation.Proceed();
            return;
        }

        var auditLogAttr = (auditLogAttrs as AuditLogAttribute[])[0];
        var auditLogs = new List<AuditLog>();
        switch (auditLogAttr.OperationType)
        {
            case Domain.OperationType.Created:
                auditLogs = GetAddedAuditLogs(invocation, tableName);
            break;
            case Domain.OperationType.Updated:
                auditLogs = GetUpdatedAuditLogs(invocation, tableName, entityType, 
                    tableIdProperty, repository);
            break;
            case Domain.OperationType.Deleted:
                auditLogs = GetDeletedAuditLogs(invocation, tableName);
            break;
        }
            
        invocation.Proceed();
        repository.Insert<AuditLog>(auditLogs.ToArray());
    }
}
```
同样地，这里需要需要使用`Autofac`将其注册到IoC容器中：
```CSharp
builder.RegisterType<DapperRepository>().As<IRepository>()
    .InterceptedBy(typeof(AuditLogInterceptor))
    .EnableInterfaceInterceptors();
builder.RegisterType<AuditLogInterceptor>();
```

# 思路延伸：领域事件
最近这段时间，对于数据同步这类“需求”略有感触，譬如某种单据在两个互为上下游的系统里流转，譬如不同系统间实时地对基础资料进行同步等。这类需求可能会通过`ETL`、`DBLink`这类“数据库”手段实现，亦有可能是通过互相调用API的方式实现，再者无非是通过数据库实现类似消息队列的功能……而我个人，更推崇通过事件来处理，因为它更接近人类思考的本质，希望在适当的时机来“通知”对方，而论询实际上是一种相当低效的沟通方式。一个订单被创建，一条记录被修改，本质上都是一个特定事件，而在业务上对此感兴趣的任何第三方，都可以去订阅这个事件，这就是事件驱动的思想。

![领域事件](https://i.loli.net/2020/04/24/8sgUqxmF5n2CdYO.png)

我拜读了几篇关于“领域驱动设计(DDD)”文章，了解到DDD中有领域事件和集成事件的概念。最直接的体会就是，DDD是主张“充血模型”的，它把事件附加到实体上，最大的好处就是，可以让“发送(Dispatch)”事件的代码，集中地放在一个地方。而我们现在的业务代码，基本是高度耦合的，每次去添加一个事件的时候，最担心地就是遗漏了某个地方。按照DDD的思想，实现领域事件，最常用的伎俩是重写DbContext的SaveChanges()方法，或者在EF中去指定DbContext的Complate事件。这里同样借助了ChangeTracker来实现：
```CSharp
public class OrderContext : DbContext
{
    public async Task<bool> SaveChangesAsync(CancellationToken cancellationToken = default(CancellationToken))
    {
        var aggregateRoots = dbContext.ChangeTracker.Entries().ToList();
        await _eventDispatcher.DispatchAsync(aggregateRoots,cancellationToken);
        var result = await base.SaveChangesAsync();
    }
}
```
其中，`_eventDispatcher`作为事件分发器来分发事件，它实现了`IEventDispatcher`接口。相对应地，事件订阅者需要实现`IDomainEventHandler`接口。如果是最简单的进程内通信，那么你需要一个容器来管理`IDomainEvent`和`IDomainEventHandler`间的关系；而如果是不同微服务间的通信，那么你需要引入`RabbitMQ`或者`kafka`这类消息队列中间件。
```CSharp
public interface IDomainEvent
{

}

public interface IDomainEventHandler<in TDomainEvent>
        where TDomainEvent : IDomainEvent
{
    Task HandleAysnc(TDomainEvent @event, CancellationToken cancellationToken = default);
}

public interface IEventDispatcher
{
    Task DispatchAsync<TDomainEvent>(
        TDomainEvent @event,
        CancellationToken cancellationToken = default) where TDomainEvent :IDomainEvent;
}
```

所以，你现在问我怎么样做数据同步好，我一定会说，通过事件来处理。因为这样，每一条数据的新增、更新、删除，都可以事件的形式发布出去，而关心这些数据的下游系统，则只需要订阅这些事件，该干嘛好嘛，何乐而不为呢？搞什么中间表，打什么标记，用数据库一遍遍地实现消息队列有意思吗？同样地，你会意识到，仓储模式，哪怕ORM换成Dapper，我们一样可以去发布这些事件，增量同步自然是要比全量同步优雅而且高效的。最重要的是，程序员再不需要到处找地方埋点了，你看我博客更新频率这么低，不就是因为这些事情浪费了时间吗(逃？因为，全量 + 实时同步就是一个非常愚蠢的决定。

# 本文小结
本文分别针对`EF Core`和`Dapper`实现了数据库审计的功能。对于前者，主要是通过重写DbContext的`SaveChanges()`方法来实现，而`EF`及`EF Core`中的`ChangeTracker`则提供了一种获取数据库表记录变化前后值的能力。而对于后者，主要是实现了`Dapper`的仓储模式，在此基础上结合`Castle`的动态代理功能，对仓储接口进行拦截，以此实现审计日志的记录功能。整体来看，后者对代码的侵入性要更小一点，理论上我们可以实现`EF`或`EF Core`的仓储模式，这样两者在实现上会更接近一点，当然，更直接的方案是去拦截`SaveChanges()`方法，这和我们使用继承的目的是一样的，由于Dapper本身没有`ChangeTracker`，所以，在处理`Update()`相关的仓储接口时，都需要先查询一次数据库，这一点是这个方案里最大的短板。而顺着这个方案扩展下去，我们同样可以挖掘出一点`DDD`里`领域事件`的意味，这就变得很有意思了，不是吗？这篇博客就先写到这里吧……再见
