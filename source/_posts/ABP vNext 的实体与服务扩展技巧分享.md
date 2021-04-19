---
toc: true
title: ABP vNext 的实体与服务扩展技巧分享
categories:
  - 编程语言
tags:
  - ABP
  - 扩展
  - 实体
  - 服务
copyright: true
abbrlink: 3619320289
date: 2021-04-18 20:42:47
---
使用 [ABP vNext](https://github.com/abpframework/abp) 有一个月左右啦，这中间最大的一个收获是：ABP vNext 的开发效率真的是非常好，只要你愿意取遵循它模块化、DDD 的设计思想。因为官方默认实现了身份、审计、权限、定时任务等等的模块，所以，ABP vNext 是一个开箱即用的解决方案。通过脚手架创建的项目，基本具备了一个专业项目该有的“**五脏六腑**”，而这可以让我们专注于业务原型的探索。例如，博主是尝试结合 [Ant Design Vue](https://www.antdv.com/docs/vue/introduce-cn/) 来做一个通用的后台管理系统。话虽如此，我们在使用 ABP vNext 的过程中，还是希望可以针对性地对 ABP vNext 进行扩展，毕竟 ABP vNext 无法 100% 满足我们的使用要求。所以，在今天这篇博客中，我们就来说说 ABP vNext 中的扩展技巧，这里主要是指实体扩展和服务扩展这两个方面。我们经常在讲“**开闭原则**”，可扪心自问，我们每次修改代码的时候，是否真正做到了“**对扩展开放，对修改关闭**”呢？ 所以，在面对扩展这个话题时，我们不妨来一起看看 ABP vNext 中是如何实践“**开闭原则**”。

# 扩展实体

首先，我们要说的是扩展实体，什么是实体呢？这其实是领域驱动设计(**DDD**)中的概念，相信对于实体、聚合根和值对象，大家早就耳熟能详了。在 ABP vNext 中，实体对应的类型为`Entity`，聚合根对应的类型为`AggregateRoot`。所以，你可以片面地认为，只要继承自`Entity`基类的类都是实体。通常，实体都会有一个唯一的标识(**Id**)，所以，订单、商品或者是用户，都属于实体的范畴。不过，按照业务边界上的不同，它们会在核心域、支撑域和通用域三者间频繁切换。而对于大多数系统而言，用户都将是一个通用的域。在 ABP vNext 中，其用户信息由`AbpUsers`表承载，它在架构上定义了`IUser`接口，借助于EF Core的表映射支持，我们所使用的`AppUser`本质上是映射到了`AbpUsers`表中。针对实体的扩展，在面向数据库编程的业务系统中，一个最典型的问题就是，我怎么样可以给`AppUser`添加字段。所以，下面我们以`AppUser`为例，来展示如何对实体进行扩展。

![DDD 中的实体、聚合根与值对象](https://i.loli.net/2021/04/19/dtANSYQqyDz9blw.jpg)

实际上，ABP vNext 中提供了2种方式，来解决实体扩展的问题，它们分别是：**Extra Properties** 和 **基于 EF Core 的表映射**。在 [官方文档](https://docs.abp.io/zh-Hans/abp/latest/Customizing-Application-Modules-Extending-Entities) 中，我们会得到更加详细的信息，这里简单介绍一下就好：

## Extra Properties

对于第1种方式，它要求我们必须实现`IHasExtraProperties`接口，这样我们就可以使用`GetProperty()`和`SetProperty()`两个方法，其原理是，将这些扩展字段以`JSON`格式存储在`ExtraProperties`这个字段上。如果使用`MongoDB`这样的非关系型数据库，则这些扩展字段可以单独存储。参考示例如下：

```csharp
// 设置扩展字段
var user = await _identityUserRepository.GetAsync(userId);
user.SetProperty("Title", "起风了，唯有努力生存");
await _identityUserRepository.UpdateAsync(user);

// 读取扩展字段
var user = await _identityUserRepository.GetAsync(userId);
return user.GetProperty<string>("Title");
```

可以想象得到，这种方式使用起来没有心智方面的困扰，主要问题是，这些扩展字段不利于关系型数据库的查询。其次，完全以字符串形式存在的键值对，难免存在数据类型的安全性问题。博主的上家公司，在面对这个问题时，采用的方案就是往数据库里加备用字段，从起初的5个，变成后来的10个，最后甚至变成20个，先不说这没完没了的加字段，代码中一直避不开的，其实是各种字符串的**Parse**/**Convert**，所以，大家可以自己去体会这其中的痛苦。

## 基于 EF Core 的表映射

对于第2种方式，主要指 EF Core 里的“**表拆分**”或者“**表共享**”，譬如，当我们希望单独创建一个实体`SysUser`来替代默认的`AppUser`时，这就是表拆分，因为同一张表中的数据，实际上是被`AppUser`和`SysUser`共享啦，或者，你可以将其理解为，EF Core配置两个不同的实体时，它们的`ToTable()`方法都指向了同一张表。这里唯一不同的是，ABP vNext 中提供了一部分方法用来处理问题，因为牵扯到数据库，所以，还是需要“迁移”。下面，我们以给`AppUser`扩展两个自定义字段为例：

首先，我们给`AppUser`类增加两个新属性，`Avatar` 和 `Profile`:

```csharp
public class AppUser : FullAuditedAggregateRoot<Guid>, IUser
{
    // ...

    public virtual string Profile { get; private set; }
    public virtual string Avatar { get; private set; }

    //  ...

```

接下来，按照 EF Core 的“**套路**”，我们需要配置下这两个新加的字段：

```csharp
builder.Entity<AppUser>(b =>
{
    // AbpUsers
    // Sharing the same table "AbpUsers" with the IdentityUser
    b.ToTable(AbpIdentityDbProperties.DbTablePrefix + "Users"); 

    b.ConfigureByConvention();
    b.ConfigureAbpUser();

    // Profile
    b.Property(x => x.Profile)
      .HasMaxLength(AppUserConsts.MaxProfileLength)
      .HasColumnName("Profile");
    
    // Avatar
    b.Property(x => x.Avatar)
      .HasMaxLength(AppUserConsts.MaxAvatarLength)
      .HasColumnName("Avatar");
});
```
接下来，通过`MapEfCoreProperty()`方法，将新字段映射到`IdentityUser`实体，你可以理解为，`AppUser`和`IdentityUser`同时映射到了`AbpUsers`这张表：

```csharp
// Avatar
ObjectExtensionManager.Instance.MapEfCoreProperty<IdentityUser, string>(
    nameof(AppUser.Avatar),
    (entityBuilder, propertyBuilder) => {
    propertyBuilder.HasMaxLength(AppUserConsts.MaxAvatarLength);
});

// Profile
ObjectExtensionManager.Instance.MapEfCoreProperty<IdentityUser, string>(
      nameof(AppUser.Profile),
      (entityBuilder, propertyBuilder) => {
      propertyBuilder.HasMaxLength(AppUserConsts.MaxProfileLength);
});
```
既然，连数据库实体都做了扩展，那么，数据传输对象(**DTO**)有什么理由拒绝呢？

```csharp
ObjectExtensionManager.Instance
    .AddOrUpdateProperty<string>(
        new[]
        {
            typeof(IdentityUserDto),
            typeof(IdentityUserCreateDto),
            typeof(IdentityUserUpdateDto),
            typeof(ProfileDto),
            typeof(UpdateProfileDto),
        },
        "Avatar"
    )
    .AddOrUpdateProperty<string>(
        new[]
        {
            typeof(IdentityUserDto),
            typeof(IdentityUserCreateDto),
            typeof(IdentityUserUpdateDto),
            typeof(ProfileDto),
            typeof(UpdateProfileDto)
        },
        "Profile"
    );
});
```
经过这一系列的“**套路**”，此时，我们会发现，新的字段已经生效：

![ABP vNext 实体扩展效果展示](https://i.loli.net/2021/04/19/WExbQrs61ltcqzy.png)

# 扩展服务

在 ABP vNext 中，我们还可以对服务进行扩展，得益于依赖注入的深入人心，我们可以非常容易地实现或者替换某一个接口，这里则指 ABP vNext 中的应用服务(ApplicationService)，例如，CrudAppService类可以帮助我们快速实现枯燥的增删改查，而我们唯一要做的，则是定义好实体的主键(**Primary Key**)、定义好实体的数据传输对象(**DTO**)。当我们发现 ABP vNext 中内置的模块或者服务，无法满足我们的使用要求时，我们就可以考虑对原有服务进行替换，或者是注入新的应用服务来扩展原有服务，这就是服务的扩展。在 ABP vNext 中，我们可以使用下面两种方法来对一个服务进行替换：

```csharp
// 通过[Dependency]和[ExposeServices]实现服务替换
[Dependency(ReplaceServices = true)]
[ExposeServices(typeof(IIdentityUserAppService))]
public class YourIdentityUserAppService : IIdentityUserAppService, ITransientDependency
{
  //...
}

// 通过ReplaceService实现服务替换
context.Services.Replace(
    ServiceDescriptor.Transient<IIdentityUserAppService, YourIdentityUserAppService>()
);
```

这里，博主准备的一个示例是，默认的用户查询接口，其返回信息中只有用户相关的字段，我们希望在其中增加角色、组织单元等关联信息，此时。我们可以考虑实现下面的应用服务：

```csharp
public interface IUserManageAppService
{
    Task<PagedResultDto<UserDetailQueryDto>> GetUsersWithDetails(
      GetIdentityUsersInput input
    );
}
```

首先，我们定义了`IUserManageAppService`接口，它含有一个分页查询的方法`GetUsersWithDetails()`。接下来，我们来考虑如何实现这个接口。需要说明的是，在 ABP vNext 中，仓储模式的支持由通用仓储接口`IRepository<TEntity, TKey>`提供，ABP vNext 会在`AddDefaultRepositories()`方法中为每一个聚合根注入对应的仓储。同样地，你可以按照个人喜好为指定的实体注入对应的仓储。由于ABP vNext 同时支持 `EF Core`、`Dapper` 和 `MongoDB`，所以，我们还可以使用`EfCoreRepository`、`DapperRepository` 以及 `MongoDbRepository`，它们都是`IRepository`的具体实现类。在下面的例子中，我们使用的是`EfCoreRepository`这个类。

事实上，这里注入的`EfCoreIdentityUserRepository`、`EfCoreIdentityRoleRepository` 以及 `EfCoreOrganizationUnitRepository`，都是`EfCoreRepository`的子类，这使得我们可以复用 ABP vNext 中关于身份标识的一切基础设施，来实现不同于官方的业务逻辑，而这就是我们所说的服务的扩展。

```csharp
[Authorize(IdentityPermissions.Users.Default)]
public class UserManageAppService : ApplicationService, IUserManageAppService
{
    private readonly IdentityUserManager _userManager;
    private readonly IOptions<IdentityOptions> _identityOptions;
    private readonly EfCoreIdentityUserRepository _userRepository;
    private readonly EfCoreIdentityRoleRepository _roleRepository;
    private readonly EfCoreOrganizationUnitRepository _orgRepository;

    public UserManageAppService(
        IdentityUserManager userManager,
        EfCoreIdentityRoleRepository roleRepository,
        EfCoreIdentityUserRepository userRepository,
        EfCoreOrganizationUnitRepository orgRepository,
        IOptions<IdentityOptions> identityOptions
    )
    {
        _userManager = userManager;
        _orgRepository = orgRepository;
        _userRepository = userRepository;
        _roleRepository = roleRepository;
        _identityOptions = identityOptions;
    }

    [Authorize(IdentityPermissions.Users.Default)]
    public async Task<PagedResultDto<UserDetailQueryDto>> GetUsersWithDetails(
      GetIdentityUsersInput input
    )
    {
        //Users
        var total = await _userRepository.GetCountAsync(input.Filter);
        var users = await _userRepository.GetListAsync(
          input.Sorting, 
          input.MaxResultCount, 
          input.SkipCount, 
          input.Filter, 
          includeDetails: true
        );

        //Roles
        var roleIds = users
          .SelectMany(x => x.Roles)
          .Select(x => x.RoleId)
          .Distinct()
          .ToList();
        var roles = await _roleRepository
          .WhereIf(roleIds.Any(), x => roleIds.Contains(x.Id))
          .ToListAsync();

        //OrganizationUnits
        var orgIds = users
          .SelectMany(x => x.OrganizationUnits)
          .Select(x => x.OrganizationUnitId)
          .Distinct()
          .ToList();
        var orgs = await _orgRepository
          .WhereIf(orgIds.Any(), x => orgIds.Contains(x.Id))
          .ToListAsync();

        var items = ObjectMapper.Map<List<Volo.Abp.Identity.IdentityUser>, List<UserDetailQueryDto>>(users);

        foreach (var item in items)
        {
            foreach (var role in item.Roles)
            {
                var roleInfo = roles.FirstOrDefault(x => x.Id == role.RoleId);
                if (roleInfo != null)
                    ObjectMapper.Map(roleInfo, role);
            }

            foreach (var org in item.OrganizationUnits)
            {
                var orgInfo = orgs.FirstOrDefault(x => x.Id == org.OrganizationUnitId);
                if (orgInfo != null)
                    ObjectMapper.Map(orgInfo, org);
            }
        }

        return new PagedResultDto<UserDetailQueryDto>(total, items);
    }
}
```

这里做一点补充说明，应用服务，即`ApplicationService`类，它集成了诸如`ObjectMapper`、`LoggerFactory`、`GuidGenerator`、国际化、`AsyncExecuter`等等的特性，继承该类可以让我们更加得心应手地编写代码。曾经，博主写过一篇关于“**动态API**”的[博客](https://blog.yuanpei.me/posts/4236649/)，它可以为我们免去从 Service 到 Controller 的这一层封装，当时正是受到了ABP 框架的启发。当博主再次在 ABP vNext 中看到这个功能时，不免会感慨逝者如斯，而事实上，这个功能真的好用，真香！下面是经过改造以后的用户列表。考虑到，在上一篇博客里，博主已经同大家分享过分页查询方面的实现技巧，这里就不再展开讲啦！

![对“用户服务”进行扩展](https://i.loli.net/2021/04/19/B6SO8Wk4EVh3Pcx.png)

# 本文小结

我们时常说，"**对修改关闭，对扩展开放**"，"**单一职责**"，可惜这些原则最多就出现在面试环节。当你接触了真实的代码，你会发现"**修改**"永远比"**扩展**"多，博主曾经就见到过，一个简单的方法因为频繁地"**打补丁**"，最后变得面目全非。其实，有时候并不是维护代码的人，不愿意去"**扩展**"，而是写出可"**扩展**"的代码会更困难一点，尤其是当所有人都不愿意去思考，一味地追求短平快，这无疑只会加速代码的腐烂。在这一点上，ABP vNext 提供了一种优秀的范例，这篇文章主要分享了 ABP vNext 中实体和服务的扩展技巧，**实体扩展解决了如何为数据库表添加扩展字段的问题，服务扩展解决了如何为默认服务扩展功能的问题**，尤其是后者，依赖注入在其中扮演着无比重要的角色。果然，这世上的事情，只有你真正在乎的时候，你才会愿意去承认，那些你曾经轻视过的东西，也许，它们是对的吧！好了，以上就是这篇博客的全部内容，欢迎大家在评论区留言，喜欢的话请记得点赞、收藏、一键三连。