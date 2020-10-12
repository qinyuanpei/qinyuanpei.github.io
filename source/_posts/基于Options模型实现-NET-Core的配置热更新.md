---
toc: true
title: 基于选项模式实现.NET Core的配置热更新
categories:
  - 数据存储
tags:
  - .NET Core
  - 配置中心
  - 配置
copyright: true
abbrlink: 835719605
date: 2020-10-11 12:19:02
---
最近在面试的时候，遇到了一个关于 .NET Core 配置热更新的问题，顾名思义，就是在应用程序的配置发生变化时，如何在不重启应用的情况下使用当前配置。从 .NET Framework 一路走来，对于 Web.Config 以及 App.Config 这两个配置文件，我们应该是非常熟悉了，通常情况下， IIS 会检测这两个配置文件的变化，并自动完成配置的加载，可以说它天然支持热更新，可当我们的视野伸向分布式环境的时候，这种配置方式就变得繁琐起来，因为你需要修改一个又一个配置文件，更不用说这些配置文件可能都是放在容器内部。而有经验的朋友，可能会想到，利用 Redis 的发布-订阅来实现配置的下发，这的确是一个非常好的思路。总而言之，我们希望应用可以随时感知配置的变化，所以，在今天这篇博客里，我们来一起聊聊 .NET Core 中配置热更新相关的话题，这里特制全新的选项模型(**Options**)。

# Options三剑客
在 .NET Core 中，选项模式(**Options**)使用类来对一组配置信息进行强类型访问，因为按照`接口分隔原则(ISP)`和`关注点分离`这两个工程原则，应用的不同部件的配置应该是各自独立的，这意味着每一个用于访问配置信息的类，应该是只依赖它所需要的配置信息的。举一个简单的例子，虽然 Redis 和 MySQL 都属于数据持久化层的设施，但是两者属于不同类型的部件，它们拥有属于各自的配置信息，而这两套配置信息应该是相互独立的，即 MySQL 不会因为 Redis 的配置存在问题而停止工作。此时，选项模式(**Options**)推荐使用两个不同的类来访问各自的配置。我们从下面这个例子开始：
```JSON
{
  "Learning": {
    "Years": 5,
    "Topic": [ "Hotfix", ".NET Core", "Options" ],
    "Skill": [
      {
        "Lang": "C#",
        "Score": 3.9
      },
      {
        "Lang": "Python",
        "Score": 2.6
      },
      {
        "Lang": "JavaScript",
        "Score": 2.8
      }
    ]
  }
}
```
此时，如果希望访问`Learning`节点下的信息，我们有很多种实现方式：
```CSharp
//方式1
var learningSection = Configuration.GetSection("Learning");
var careerYears = learningSection.GetValue<decimal>("Years");
var topicHotfix = learningSection.GetValue<string>("Topic:0");

//方式2
var careerYears = Configuration["Learning:Years"];
var topicHotfix = Configuration["Learning:Topic:0");
```
而更好的方式是，定义一个类来访问这组配置信息：
```CSharp
 [Serializable]
public class LearningOptions
{
    public decimal Years { get; set; }
    public List<string> Topic { get; set; }
    public List<SkillItem> Skill { get; set; }
}

[Serializable]
public class SkillItem
{
    public string Lang { get; set; }
    public decimal? Score { get; set; }
}
```
同样地，茴香的`茴`字有几种写法，你可知道?
```
//写法1：手动绑定
var leaningOptions = new LearningOptions();
Configuration.GetSection("Learning").Bind(leaningOptions);

//写法2：自动绑定
leaningOptions = Configuration.GetSection("Learning").Get<LearningOptions>();

//写法3：自动绑定 + 依赖注入
services.Configure<LearningOptions>(Configuration.GetSection("Learning"));

//写法4：配置的二次加工
services.PostConfigure<LearningOptions>(options => options.Years += 1);

//写法5：委托绑定
services.Configure<AppInfoOptions>(options =>
{
  options.AppName = "ASP.NET Core";
  options.AppVersion = "1.2.1";
});
```
我们知道，在 .NET Core 里依赖注入被提升到了一等公民的位置，可谓是无处不在。当我们在 IoC 容器中注入`LearningOptions`以后，就可以在服务层或者控制器层直接使用它们，此时，我们就会遇到传说中的Options三剑客，即`IOptions<TOptions>`、`IOptionsSnapshot<TOptions>`和`IOptionsMonitor<TOptions>`。关于它们三个的区别，[官方文档](https://docs.microsoft.com/zh-cn/aspnet/core/fundamentals/configuration/options?view=aspnetcore-3.1)里给出了详细的说明：

* IOptions<TOptions>：生命周期为Singleton，在应用启动时完成初始化。应用启动后，对配置的修改是非响应式的。
* IOptionsSnapshot<TOptions>：生命周期为Scoped，每次请求时会重新计算选项。应用启动后，对配置的修改是响应式的。
* IOptionsMonitor<TOptions>：生命周期为Singleton，可以随时检索当前配置项。应用启动后，对配置的修改是响应式的。

是不是听起来有一点还有一点绕？长话短说就是，如果希望修改完配置立即生效，那么，更推荐使用`IOptionsSnapshot<TOptions>`和`IOptionsMonitor<TOptions>`，前者是在下一次请求时生效，后者则是访问`CurrentValue`的时候生效。而对于像`3.14`或者`0.618`这种运行时期间不会修改的“常量”，更推荐使用`IOptions<TOptions>`。下面是关于它们的一个例子：
```
[ApiController]
[Route("[controller]")]
public class WeatherForecastController : ControllerBase
{
    private readonly ILogger<WeatherForecastController> _logger;
    private readonly IOptions<LearningOptions> _learningOptions;
    private readonly IOptionsSnapshot<LearningOptions> _learningOptionsSnapshot;
    private readonly IOptionsMonitor<LearningOptions> _learningOptionsMonitor;
    private readonly IConfiguration _configuration;

    public WeatherForecastController(ILogger<WeatherForecastController> logger, 
        IOptions<LearningOptions> learningOptions, 
        IOptionsSnapshot<LearningOptions> learningOptionsSnapshot, 
        IOptionsMonitor<LearningOptions> learningOptionsMonitor,
        IConfiguration configuration
        )
    {
        _logger = logger;
        _learningOptions = learningOptions;
        _learningOptionsSnapshot = learningOptionsSnapshot;
        _learningOptionsMonitor = learningOptionsMonitor;
        _configuration = configuration;
        _learningOptionsMonitor.OnChange((options, value) =>
        {
            _logger.LogInformation($"OnChnage => {JsonConvert.SerializeObject(options)}");
        });
    }

    [HttpGet("{action}")]
    public ActionResult GetOptions()
    {
        var builder = new StringBuilder();
        builder.AppendLine("learningOptions:");
        builder.AppendLine(JsonConvert.SerializeObject(_learningOptions.Value));
        builder.AppendLine("learningOptionsSnapshot:");
        builder.AppendLine(JsonConvert.SerializeObject(_learningOptionsSnapshot.Value));
        builder.AppendLine("learningOptionsMonitor:");
        builder.AppendLine(JsonConvert.SerializeObject(_learningOptionsMonitor.CurrentValue));
        return Content(builder.ToString());
    }
}
```
现在我们修改一下配置文件，因为我们为`_learningOptionsMonitor`注册了回调函数，可以在控制台看到对应的日志：

![监听配置文件变化](https://i.loli.net/2020/10/11/s1XFSKvOLZz6Imo.png)

此时，我们通过 Postman 调用接口，我们会得到下面的结果：

![learningOptions的值并未更新](https://i.loli.net/2020/10/11/j5ENWpSCGtQw73O.png)

可以注意到，此时，learningOptions中的值依然是更新前的值，这就是它们三者的区别，清楚了吗？

除了这些以外，选项模式(**Options**)中还有一个需要注意的地方，是所谓的命名选项(**IConfigureNamedOptions**)，主要用在多个Section绑定统一属性时。譬如现在的应用程序都流行深色主题，实际上深色主题和浅色主题具有相同的结构，比如前景色和背景色，两者唯一的区别是这些颜色配置不一样。考虑下面的配置信息：
```JSON
{
  "Themes": {
    "Dark": {
      "Foreground": "#fff",
      "Background": "#000"
    },
    "White": {
      "Foreground": "#000",
      "Background": "#fff"
    }
  }
}
```
此时，我们该如何定义这个主题选项呢？
```CSharp
public class ThemeOptions
{
    public string Foreground { get; set; }
    public string Background { get; set; }
}
```
接下来，我们通过命名的方式来注入两个不同的主题：
```CSharp
services.Configure<ThemeOptions>("DarkTheme", Configuration.GetSection("Themes:Dark"));
services.Configure<ThemeOptions>("WhiteTheme", Configuration.GetSection("Themes:White"));
```
在任何你希望使用它们的地方，注入`IOptionsSnapshot<ThemeOptions>`和`IOptionsMonitor<ThemeOptions>`即可，这两个类型都提供了一个`Get()`方法，传入前面定义好的主题就可以获取到对应的主题了。细心的朋友，应该会发现一件事情，这里三剑客只提到了后面两个，`IOptions<ThemeOptions>`直接被无视了。请记住下面这段话：**命名的选项只能通过IOptionsSnapshot<T>和IOptionsMonitor<T>来访问。所有选项都是命名实例。 IConfigureOptions<TOptions> 实例将被视为面向 Options.DefaultName 实例，即 string.Empty。 IConfigureNamedOptions<TOptions> 还可实现 IConfigureOptions<TOptions>。 IOptionsFactory<TOptions> 的默认实现具有适当地使用每个实例的逻辑。 null 命名选项用于面向所有命名实例，而不是某一特定命名实例。 ConfigureAll 和 PostConfigureAll 使用此约定。**

# IChnageToken
现在，让我们回到本文的主题，博主你不是要说配置热更新这个话题吗？截至到目前为止，我们修改配置文件的时候，ASP.NET Core 应用明明就会更新配置啊，所以，博主你到底想说什么？其实，博主想说的是，的确我们的目的已经达到了，但我们不能永远停留在“知其然”的水平，如果不试图去了解内在的机制，当我们去尝试实现一个自定义配置源的时候，就会遇到一些你没有办法想明白的事情。所以，接下来要讲的`IChnageToken`这个接口可以说是非常重要。

首先，我们把目光聚焦到`CreateDefaultBuilder`这个方法，它通常在入口文件`Program.cs`中被调用，主要作用是构造一个IWebHostBuilder实例并返回，下面是这个方法的内部实现，博主这里对其进行了精简：
```CSharp
public static IWebHostBuilder CreateDefaultBuilder(string[] args)
{
    //以下简化后的代码片段
    builder.ConfigureAppConfiguration((hostingContext, config) =>
    {
        var env = hostingContext.HostingEnvironment;

        config.AddJsonFile("appsettings.json", optional: true, reloadOnChange: true)
            .AddJsonFile($"appsettings.{env.EnvironmentName}.json", optional: true, reloadOnChange: true);

        if (env.IsDevelopment())
        {
            var appAssembly = Assembly.Load(new AssemblyName(env.ApplicationName));
            if (appAssembly != null)
            {
                config.AddUserSecrets(appAssembly, optional: true);
            }
        }

        config.AddEnvironmentVariables();

        if (args != null)
        {
            config.AddCommandLine(args);
        }
      })
}
```
可以注意到，通过`ConfigureAppConfiguration()`方法，框架主要做了下面的工作：
* 从`appsettings.json`和`appsettings.${env.EnvironmentName}.json`两个配置文件中加载配置
* 从`机密管理器`中加载配载
* 从环境变量中加载配置
* 从命令行参数中加载配置

实际上，.NET Core 可以从配置文件、环境变量、Azure Key Vault、Azure 应用程序配置、命令行参数、已安装或已创建的自定义提供程序、目录文件、内存中的 .NET 对象等各种各样的来源中加载配置，这里的`appsettings.json`使用的是`JsonConfigurationProvider`类，位于`Microsoft.Extensions.Configuration.Json`这个命名空间，可以注意到，它继承自`FileConfigurationProvider`类，并重写了`Load()`方法，通过这些关系，我们最终可以找到这样一段代码：
```CSharp
public FileConfigurationProvider(FileConfigurationSource source)
{
    if (source == null)
    {
        throw new ArgumentNullException(nameof(source));
    }
            
    Source = source;
    if (Source.ReloadOnChange && Source.FileProvider != null)
    {
        _changeTokenRegistration = ChangeToken.OnChange(
            () => Source.FileProvider.Watch(Source.Path),
            () => {
                Thread.Sleep(Source.ReloadDelay);
                Load(reload: true);
        });
    }
}
```
所以，真相就是,所有基于文件的配置提供者，都依赖于`FileConfigurationSource`，而通过`FileConfigurationSource`暴露出来的`FileProvider`都具备监视文件变化的能力，更本质上的代码其实应该是下面这样：
```CSharp
//ChangeToken + IFileProvider 实现对文件的监听
var filePath = @"C:\Users\admin\Downloads\孔乙己.txt";
var directory = System.IO.Path.GetDirectoryName(filePath);
var fileProvider = new PhysicalFileProvider(directory);
ChangeToken.OnChange(
    () => fileProvider.Watch("孔乙己.txt"),
    () => {
        _logger.LogInformation("孔乙己，你一定又偷人家书了吧！");
    }
);
```
所以，真相只有一个，真正帮助我们实现配置热更新的，其实是`IChangeToken`这个接口，我们只需要把这样一个实例传入到`ChangeToken.OnChange()`方法中，就可以在特定的时机触发这个回调函数，而显然，对于大多数的`IConfigurationProvider`接口而言，这个回调函数其实就是`Load()`方法，关于微软提供的`ChangeToken`静态类的实现，大家如果有兴趣去了解的话，可以参考这里：[https://github.com/dotnet/extensions/blob/release/3.1/src/Primitives/src/ChangeToken.cs](https://github.com/dotnet/extensions/blob/release/3.1/src/Primitives/src/ChangeToken.cs)。话说回来，我们说`IOptionsSnapshot<T>`和`IOptionsMonitor<T>`是响应式的，当配置发生改变的时候，它们对应的值会跟着改变，从某种意义上来说，是因为`IChangeToken`提供了这样一个可以监听变化的的能力，试想一下，我们只需要给每一个`IConfigurationProvider`对应的`IChangeToken`注册相同的回调函数，那么，当某一个`IConfigurationProvider`需要重新加载的时候，我们就可以针对这个`IConfigurationProvider`里对应的键值对进行处理。事实上，微软官方在实现`IConfigurationRoot`的时候，的确就是这样做的：
```CSharp
public class ConfigurationRoot : IConfigurationRoot
{
    private ConfigurationReloadToken _changeToken = new ConfigurationReloadToken();
    private IList<IConfigurationProvider> _providers;

    public ConfigurationRoot(IList<IConfigurationProvider> providers)
    {
        _providers = providers;
        foreach (var provider in providers)
        {
            provider.Load();
            ChangeToken.OnChange(() => provider.GetReloadToken(), this.RaiseChanged);
        }        
    }    
    
    public IChangeToken GetReloadToken() => return _changeToken;

    private void RaiseChanged()
    {
          Interlocked.Exchange<ConfigurationReloadToken>(ref _changeToken, new ConfigurationReloadToken()).OnReload();
    }
 
    public void Reload()
    {
        foreach (var provider in _providers)
        {
            provider.Load();
        }
        this.RaiseChanged();
    }    
}
```

# 自定义配置源
好了，现在你可以说你了解 .NET Core 的配置热更新这个话题了，因为截至到此时此刻，我们不仅仅达到了一开始的目的，而且深刻地理解了它背后蕴含的原理。这样，我们就可以向着下一个目标：自定义配置源努力了。前面提到过，.NET Core里面支持各种各样的配置源，实际中可能会遇到更多的配置源，比如不同的数据库、YAML格式以及Apollo、Consul、Nacos这些配置中心等等，所以，了解如何去写一个自定义的配置源还是非常有必要的。我们在一开始的时候提到了Redis的发布-订阅，那么，下面我们就来基于发布-订阅实现一个简单的配置中心，当我们需要修改配置时，只需要通过可视化的Redis工具进行修改，然后再给指定的客户端发一条消息即可。

实现自定义配置源，需要实现`IConfigurationSource`和`IConfigurationProvider`两个接口，前者实现起来非常简单，因为只要返回我们定义的`RedisConfigurationProvider`实例即可：
```CSharp
public class RedisConfigurationSource : IConfigurationSource
{
    private readonly RedisConfigurationOptions _options;

    public RedisConfigurationSource(RedisConfigurationOptions options)
    {
        _options = options;
    }

    public IConfigurationProvider Build(IConfigurationBuilder builder)
    {
        return new RedisConfigurationProvider(_options);
    }
}
```
接下来是`RedisConfigurationProvider`类的实现：
```CSharp
public class RedisConfigurationProvider : ConfigurationProvider
{
    private CSRedisClient _redisClient;
    private readonly RedisConfigurationOptions _options;

    public RedisConfigurationProvider(RedisConfigurationOptions options )
    {
        _options = options;
        _redisClient = new CSRedisClient(_options.ConnectionString);
        if (options.AutoReload)
        {
            //利用Redis的发布-订阅重新加载配置
            _redisClient.Subscribe((_options.HashCacheChannel, msg => Load()));
        }
    }

    public override void Load()
    {
        Data = _redisClient.HGetAll<string>(_options.HashCacheKey) ?? new Dictionary<string, string>();
    }
}
```
为了用起来更得心应手，扩展方法是少不了的：
```CSharp
public static class RedisConfigurationExtensions
{
    public static IConfigurationBuilder AddRedisConfiguration(this IConfigurationBuilder builder, RedisConfigurationOptions options)
    {
        return builder.Add(new RedisConfigurationSource(options));
    }
}
```
现在，我们改一下入口类`Program.cs`，因为在这个阶段依赖注入是无法使用的，所以，看起来有一点难受，从命名就可以看出来，内部使用了`Hash`这种结构，理论上每个客户端应该使用不同的Key来进行缓存，应该使用不同的Channel来接收配置更新的通知：
```
public static IHostBuilder CreateHostBuilder(string[] args) =>
    Host.CreateDefaultBuilder(args)
        .ConfigureAppConfiguration(configurationBuilder =>
        {
            configurationBuilder.AddRedisConfiguration(new Models.RedisConfigurationOptions()
            {
                AutoReload = true,
                ConnectionString = "127.0.0.1:6379",
                HashCacheKey = "aspnet:config",
                HashCacheChannel = "aspnet:config:change"
            });
        })
        .ConfigureWebHostDefaults(webBuilder =>
        {
            webBuilder.UseStartup<Startup>();
        });
```
假设现在Redis里存储着下图所示的信息：

![Redis中的存储结构](https://i.loli.net/2020/10/11/MwaYZTmsIRkFWKt.png)

相应地，我们可以在`Startup`中进行绑定：

```CSharp
services.Configure<AppInfoOptions>(Configuration.GetSection("App"));
```
调一下接口看看？完全一致！Yes！

![Redis与客户端的配置一致](https://i.loli.net/2020/10/11/lHxtYwjLp5qFank.png)

# 本文小结
回想起这个面试中“邂逅”的问题，针对对这块内容，其实当时并没有和面试官进行太深的交流，提到了分布式配置、配置中心以及像缓存的雪崩、击穿等等常见的问题，我隐约记得配置文件`appsettings.json`配置的部分有热更新的配置项，但我并没有对选项模式(**Options**)里的三剑客做过深入的挖掘，所以，这篇博客，一方面是系统地了解了一下选项模式(**Options**)的使用，而另一方面是由配置热更新这个话题引申出来的一系列细节，在没有理解`IChangeToken`的时候，实现一个自定义的配置源是有一点困难的，在这篇博客的最后，我们基于Redis的发布-订阅实现了一个简单的配置中心，不得不说，Redis里用`:`来分割Key的方式，实在是太棒了，因为它可以完美地和 .NET Core 里的配置系统整合起来，这一点只能用赏心悦目来形容，好了，国庆节以后的第一篇博客就是这样了，谢谢大家！
