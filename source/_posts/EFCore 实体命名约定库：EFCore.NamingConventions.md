---
toc: true
title: EFCore 实体命名约定库：EFCore.NamingConventions
categories:
  - 数据存储
tags:
  - EF
  - 实体
  - .NET
  - 数据库
copyright: true
abbrlink: 3219639636
date: 2021-06-17 16:37:11
---

# 引言

在软件开发过程中，数据库永远都是绕不开的一个话题。有时候，我们甚至会因此而获得一个名字——“**CURD Boy**”。虽然不过是朴实无华的“**增删查改**”，可隐隐然早已分出了无数的流派。在这些不同的流派中，有的人坚持“**我手写我心**”，认为手写`SQL`才是真正的王道，没有读过/写过成百上千行的存储过程，便不足以谈论程序员的人生。而有的人喜欢`ORM`的清晰、整洁，认为数据库和面向对象存在着天然抗阻，`ORM`更有利于推进`DDD`和微服务的落地。相信大家都听说过`Java`里的`SSH`框架，从`Hibernate`到`Mybatis`再到`Spring Data JPA`，可以说这种争论一直没有停止过。这里我们不打算讨论这个问题，我们平时使用`EF`或者`EFCore`的过程中，作为连接数据库和面向对象两个异世界的桥梁，`ORM`需要我们来告诉它，实体数据与数据库表字段的映射关系，所以，经常需要通过`数据注解`或者`Fulent API`来写各种配置。那么，有没有什么方案可以让我们偷这个懒呢？下面隆重请出本文的主角：[EFCore.NamingConventions](https://github.com/efcore/EFCore.NamingConventions)。

# 使用方法

[EFCore. NamingConventions](https://github.com/efcore/EFCore.NamingConventions)，目前由一个非官方的组织进行维护，代码托管在 Github 上，100％的开源项目。

如果你希望直接使用它的话，可以直接通过`NuGet`进行安装：  

```shell
Install-Package EFCore.NamingConventions  
```

接下来，我们只需要在`DbContext`的  `OnConfiguring()`方法中，调用它提供的扩展方法即可： 

```csharp 
protected override void OnConfiguring(DbContextOptionsBuilder optionsBuilder)  
=> optionsBuilder  
.UseSqlite("Data Source=Chinook.db")
.UseSnakeCaseNamingConvention();  
```

或者，你可以使用依赖注入的方式：

```csharp
services.AddDbContext<ChinookContext>(options => 
    options.UseSqlite("Data Source=Chinook.db")
          .UseSnakeCaseNamingConvention()
);
```

这里我以`SQLite`数据库为例，来展示它的具体使用细节。事实上，它提供了 4 种命名约定的策略：

* UseSnakeCaseNamingConvention: `FullName` -> `full_name`
* UseLowerCaseNamingConvention: `FullName` -> `fullname`
* UseCamelCaseNamingConvention: `FullName` -> `fullName`
* UseUpperCaseNamingConvention: `FullName` -> `FULLNAME`

简单来说，就是当我们的实体中存在一个属性`FullName`时，它会告诉`EF`或者`EFCore`，这个属性`FullName`对应的表字段是什么。  

虽然，在大多数的场景中，我们都希望属性名称和表字段一致，可你要知道，像`Oracle`这种对大小写敏感的数据库，特别喜欢自作聪明地帮你全部改成大写。所以，在上家公司工作的时候，为了兼容`Oracle`这病态的癖好，公司里有个不成文的规定，那就是：所有实体的属性名称最好都大写。本来大家用驼峰命名就是为了好认单词，好家伙！这下全部大写了，一眼望过去简直就是灾难，因为没有办法做到“**望文生义**”，如果那个时候知道这个库的存在，是不是就能解决这个问题了呢？

# 第一个例子

下面我们以`UseSnakeCaseNamingConvention`为例，结合`SQLite`来做一个简单的例子。

首先，我们定义必要的实体，并为`DbContext`配置实体命名约束规则：

```csharp
// Album
public class Album
{
    public int AlbumId { get; set; }
    public string Title { get; set; }
    public int ArtistId { get; set; }
    public string TenantId { get; set; }
}

// Artist
public class Artist
{
    public int ArtistId { get; set; }
    public string Name { get; set; }
    public string TenantId { get; set; }
}
```

接下来，通过迁移命令来生成数据库架构：

```shell
Add-Migration "Init-Database" -Context ChinookContext
Update-Database
```

可以注意到，生成的数据库表字段会以小写+下划线的方式命名。这就是所谓的实体命名约束。

![通过实体命名约束生成的 Album 表](https://i.loli.net/2021/06/18/cSVRWrDTbnv29Ze.png)

只要大家都看着这个约定来写实体的属性，这套机制就可以完美工作。它和`MVC`里的默认路由一样，都是属于一种“**约定大于配置**”的方案。在我看来，不管是配置还是约定。当以团队为单位进行协作时，最好还是以文档的形式记录下来，否则会出现两种结局，**其一是没人知道怎么配置，其二是新人不知道有这个约定**。

以上就是`EFCore.NamingConventions`的基本用法，更多的细节大家可以去阅读它的`README`，因为这个库需要结合迁移功能来使用，所以，如果要在已存在的表上应用这套约束规则时，建议大家还是小心谨慎一点，我个人觉得，它可以方便团队去制定一套数据库规范，进而去约束开发人员写出更规范的命名。

# 本文小结

本文主要介绍了可用于`EFCore`的实体命名约束库：`EFCore.NamingConventions`。这是一个由社区维护的、开源的项目，它可以在创建`DbContext`的时候，指定一个实体命名约束规则，即实体属性如何与数据库表字段进行对应，这是一种约定大于配置的方案，一旦团队形成了属于自己的数据库命名风格，那么，研发人员只需要按照规范为实体属性命名，例如开发人员可以使用驼峰风格的命名，而数据库管理员则可以使用下划线风格的命名。这样，就可以省略一部分字段映射的配置代码，从而提高团队研发的效率。值得说明的一点是，不管是配置还是约定。当以团队为单位进行协作时，最好还是以文档的形式记录下来，否则会出现两种结局，**其一是没人知道怎么配置，其二是新人不知道有这个约定**。好了，以上就是这篇博客的全部内容啦，谢谢大家！
