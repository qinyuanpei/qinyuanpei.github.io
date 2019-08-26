---
abbrlink: 1254783039
categories:
- 编程语言
date: 2016-10-25 20:16:13
description: 而这种情况常常是因为用户在设计需求的时候忽略了某些细节，所以对我而言我生气、我愤怒，并非是我觉得这个需求无法实现，而是它在某种程度上是冗余的，即它可能破坏了一致性原则，灵活的人类是比呆板的计算机有趣，可和人相处得久了，你难免会觉得人显得不靠谱，这就是我厌恶的理由，在这个世界上所有一切计算机可以处理的问题，在某种程度上都可以转化为数学问题，一旦我们将设定突破这个规则，就会让代码因为妥协而变得丑陋不堪，我显然不允许这样的事情发生
tags:
- 日志
- Trace
- 调试
title: 基于C#中的Trace实现一个简单的日志系统
---

&emsp;&emsp;最近在做的项目进入中期阶段，因为在基本框架结构确定以后，现阶段工作重心开始转变为具体业务逻辑的实现，在这个过程中我认为主要有两点，即保证逻辑代码的正确性和容错性、确定需求文档中隐性需求和逻辑缺陷。为什么我说的这两点都和用户需求这个层面息息相关呢？或许这和我这段时间的感受有些关系吧，我觉得当我们在面对用户提出的需求的时候，一个非常让我们不爽的一个地方是，我们总是需要花费大量的时间来和用户确定某些细节，而这些细节无论在BRD或者PRD中都无从体现。固然从用户层面上来讲，我们无法要求用户提供，详尽到每一个细节的需求文档。可我觉得这是一个修养的问题，我们习惯于宽以律己、严以待人，可是如果我们连自己都说服不了，我们该如何尝试去说服别人呢？我不认为我们就应该被用户限制自由，我们共同的目的都是想要好做一件事情，所以我们的关系应该是平等的伙伴的关系，这种上下级的、命令式的主仆关系让我感觉受到了侮辱。

<!--more-->

# 关于最近的碎碎念

&emsp;&emsp;其实对我而言，我更希望在工作中能找到一种释放天性的氛围，因为我觉得我们这个世界每天都有新的技术诞生。可是当我发现，我们的用户依然在使用着20多年前的技术的时候，我常常感觉到一种难以言表的紧迫感，或许对银行这类用户而言，它对安全和可靠的需要远远超过对新技术和新工具的需要，可是当我看到身边的同龄人甚至是人到中年的时候，我忽然间发现，原来这一切离我是如此的近，当你看到身边的同龄人对代码开始厌烦，继而将其当作糊口的工具的时候，我有时候就常常在想，我离这种状态会有多远，我讨厌自己不像期望中那样好，因为我曾错失过一个我爱的人，所以我有时候会像强迫症晚期一样，刻意地去追求完美。或许接受平庸会更像一个正常人，可我怕我再没有勇气去轻易喜欢一个人。我承认，我在这件事情上偏执是因为我在某种程度上自卑，可是如果我们能做得更好，为什么不去尝试做得更好呢？

&emsp;&emsp;这段时间，我喜怒无常的性格，或许让我身边的同事受到了伤害，其实我从来都不是针对任何人，我只是对这种无法掌控的现实的一种愤怒，我们常常被用户要求，为他们开发某种自动化的工具，可是我们所有的工具流，都是建立在一套尚未健全的设计上的，甚至用户内部使用的相关系统存在各种各样的设计缺陷，而这些完全不适合做自动化的特性，常常面临被设计到需求文档中的尴尬。虽然工程师喜欢解决问题，可解决问题并不代表要以牺牲技术上的先进性为代价，就像今天我们同样可以使用汇编语言来开发应用程序，可是有谁会选择这样做呢？这是因为汇编作为工具本身就是一种相对低级的编程语言，所以在这种情况下，我不认为花费精力来为落后的工具填坑，是一种值得称赞的事情，我们早已告别了石器时代，可有人因为学会了钻木取火而沾沾自喜，这是一种悲哀。我们既然让计算机来替人们做事情，所以就应该明确告诉计算机到底想做什么。一切没有任何规则可言，同时妄图实现自动化的过程，都是在赤裸裸的耍流氓，而规则和约束常常让人性的缺点暴露无疑。

&emsp;&emsp;所以，这种向现实妥协的做法，常常会让我们编写出肮脏的代码。我们总是想要编写出优雅、通用的代码，可因为工具流的落后、需求频繁变动、设计缺陷等等的原因，我们在面对这些东西的时候，常常感觉被人类的愚蠢的打败，人们说是人类发明了计算机，可是这是否就意味着我们一定会比计算机聪明，难道计算机无法通过深度学习超越人类吗？Google的AlphaGo凭借当今火热的深度学习理论以4:1的战绩打败了韩国棋手李世乭，可是不愿意去学习新知识的人类居然可以自信到能够驾驭计算机，我说将来会有越来越多的工作被计算机代替，我的一位长辈不以为然的说，不管计算机如何智能它总需要人类来控制它吧，我真的很想问一句，如果计算机真的超越了人类它为什么还需要人类来管理，而人类依靠什么样的技术来管理这些计算机。我认为在这个世界上，总是存在某种永恒的规则，它可以超越生与死的界限，而这些规则永远不会被打破，人类就像一个任性的孩子一样，可真理不就是用来敬畏的吗？我们对这个世界了解的越多，发现自己越来越渺小，此时此刻，你是否还有信心说我们可以驾驭计算机？

&emsp;&emsp;写这些碎碎念，其实是想反映我这段时间的心理状态，有人说，摆脱失恋最好的方法就是投入一段新的感情，可是其实你永远都清楚地知道，在你心里最看重什么，所以我对代码有一种特殊地感情，你可以清楚地从代码中读出一个人的所思所悟，因为那就是你独特个性的一种写照，所以每一次或许Alex让我改代码的时候，我都是在和我自己赌气吧，我不愿意让那些奇怪的逻辑破坏它的纯粹性，它必须是统一的、简洁的、纯粹的，它不能掺杂丝毫的丑陋的设计。而这种情况常常是因为用户在设计需求的时候忽略了某些细节，所以对我而言我生气、我愤怒，并非是我觉得这个需求无法实现，而是它在某种程度上是冗余的，即它可能破坏了一致性原则，灵活的人类是比呆板的计算机有趣，可和人相处得久了，你难免会觉得人显得不靠谱，这就是我厌恶的理由，在这个世界上所有一切计算机可以处理的问题，在某种程度上都可以转化为数学问题，一旦我们将设定突破这个规则，就会让代码因为妥协而变得丑陋不堪，我显然不允许这样的事情发生。

# 花十分钟解锁新技能

&emsp;&emsp;好了，现在我们来回到这篇文章的主题，基于C#中的Trace来实现一个简单地日志系统。我们的项目上存在大量和用户内部系统关联的特性，所以我们会在远程计算机上耗费大量的时间来测试代码，这个时候我们会遇到两个问题，第一，我们开发环境中的Visual Studio版本和生产环境中的Visual Studio版本不一致，所以如果直接远程调试，因为项目中使用的相关语法在低版本Visual Studio中不被支持，如果修改代码会非常痛苦，我们实在没有精力去兼容两个版本的开发环境。第二，项目中默认使用的日志系统Log4Net，默认是在指定用户的我的文档目录中产生日志信息，而我们在远程调试时因为权限问题无法访问日志文件，所以虽然我们可以根据界面上反馈的信息，来粗略判断异常发生在什么时候，但这对我们追踪和定位问题来说是非常不利的。我们在研究了Log4Net的文档后，认为这个库的配置文件非常复杂，所以我们在想有没有一种更为简单地方案可以帮助我们解决这个问题。

&emsp;&emsp;我们了解到.NET中实际上提供了两个类Trace和Debug来满足类似的需求，而这两个类位于System.Diagnostics空间下，所以我们完全有理由相信基于这两个类，我们同样可以构建出一个相对简单的日志系统。首先我们通过MSDN了解到官方对它们各自用途的定义：

> **Trace**：提供了一组方法和属性，可以帮助您追踪您的代码执行，该类无法被继承。

> **Debug**: 提供了一组帮助调试代码的方法和属性，该类无法被继承。

&emsp;&emsp;显然，我们通过这里给出的定义，可以非常容易的理解这两个类都可以用来追踪和调试代码，那么它们本质的区别在什么地方呢？如果我们的解决方案配置类型为Release，则会忽略Debug类的输出。换句话说，当我们处在开发调试阶段时，使用Debug类能够帮助我们在控制台或者是文件以及任意自定义的输出位置输出相关的调试信息，而当产品上线发布以后这些调试信息则不会输出。而Trace无论是在Debug还是Release模式下都会输出相关的追踪信息。通常我们会在发布以后的产品中部署日志生成模块，这样可以方便开发者定位问题、维护产品，那么在这种情况下，我们采用Trace这种方式来追踪程序的执行情况是非常适合的，而这正是我想写这篇博客的一个原因。

&emsp;&emsp;现在，在确定了使用Trace来开发一个简单的日志系统这样一个技术路线以后，现在我们来了解下Trace都提供了那些东西吧！对Debug和Trace这两个类来说，.NET为它们提供了下面这些相同的方法：

* **WriteLine:** 该方法会在输出设备中写入一条调试信息，而通过实现不同的监听器(Listener)并对其中的方法进行重写(OverWrite)，就可以将调试信息以不同的形式输出。例如Debug类产生的调试信息默认输出在Visual Studio中的输出窗口，我们可以通过自定义监听器将调试信息输出到文件或者控制台中。同样地，对Trace类来说，它同样遵循这个原则，这体现出了一种宏观上的统一。所谓“和而不同”，我们可以尊重这个世界的规则、尊重宇宙苍生，可是我们每一个人都是一个完全独立的个体，人可以被打倒，但决不会被打败。
```
Trace.WriteLine("This is a Debug message!");
Trace.WriteLine("This is a Debug message!","Debug");
```
* **WriteLineIf:** 该方法是WriteLine的增强版，仅当条件满足时会在输出设备中写入一条调试信息，同样，它支持通过实现不同的监听器(Listener)来完成重写，进而将调试信息以不同的形式输出，该方法在需要根据条件处理不同响应的场景下会非常有用。例如在项目中我们会通过一个窗口来输出程序执行过程中的细节信息，这些信息对我们开发人员来讲是非常重要的，因为我们可以通过这些信息来快速地定位问题。可是这些信息对用户而言是可以完全忽略的啊，难道肤浅的我们要在这里处理这两种情况吗？不，我们只需要定义一个全局开关，从此整个世界都变得安静了。
```
Trace.WriteLineIf(i>10,"This message will only output when i>10");
```
* **Indent/Unindent:** Log4Net中提供了对日志输出样式的支持，它被定义在一个Xml形式的配置文件当中，我们发现一件有趣的事情，复杂和简单是矛盾而统一的，就像我对编辑器这类工具，我会喜欢它提供的各种强大的扩展能力，而对集成开发环境这类工具，我会喜欢它提供的简单上手、零配置、开箱即用这种良好特性。当你发现你提供的功能越来越多的时候，就应该停下来思考这种做是否是正确的举动，一个东西的灵活性越强，它的复杂性就会越高，因为这意味着你需要去兼顾各种各样可能的组合。在这里Indent方法可以为输出提供缩进样式，相反Unindent方法可以为输出清除缩进样式。

* **Assert:** 断言不一定就出现在单元测试中，就像骑白马的不一定都是唐僧。严格的来讲，这里的断言相对单元测试中的断言会显得相对薄弱，因为它没有Assert这个类的功能丰富。在这里我想说的是，Assert方法会在条件不满足时显示“断言失败”对话框，在对话框中会显示当前程序堆栈调用的详细情况，这是非常有意思的一个功能。有时候我们或许会因为业务而忽略技术，业务是现实规则的一种映射，所以我们可以理解业务本身地复杂性，可我们从古到今所认识的世界难道都是这样子的吗？或许由人类定义出来的这些规则本身就是错误的呢？
```
Trace.Assert(i>10,"This message will only output when i<=10");
```
* **Flush:** Flush方法可以理解为一个通知监听器的方法，因为在调用Flush方法以后，每一个Listener对象将接收到它的所有输出，我们可以理解为，WriteLine方法执行以后，无论Trace还是Debug，其监听器都不会理解响应输出，只有当Flush方法被调用以后调试信息才会被响应和输出。

&emsp;&emsp;好了，再了解了这些以后，现在我们就可以开始设计一个日志系统了。按照国际惯例，我们当然是从设计接口开始，其实在做一项设计的时候，是不是要从接口开始，完全取决于你对接口持怎样的态度，人生或许有各种各样的套路，可是需不需要遵守这些套路完全是取决你的啊，编程同样是这个道理，我的习惯是在没有理解一个东西以前，永远不要尝试去使用它，可能你会说如果永远都不去尝试，那你就永远失去了了解它的机会，我想说的是，请不要滥用：
```
interface ILoger
{
    void Warn(object msg);
    void Info(object msg);
    void Debug(object msg);
    void Error(object msg);
}
```
可以注意到在这里，我定义了四种级别的Log，这自然是模仿Log4Net，更重要的是这些不同的级别，我并不清楚他们之间的区别。这听起来好像挺尴尬啊。定义好接口以后，我们就可以考虑具体的实现啦！日志系统对整个应用程序而言哼，是独立且贯穿整个软件开发的生命周期的，所以将其设计为单例模式会更加友好：
```
public class SimpleLoger : ILoger
{
    /// <summary>
    /// Single Instance
    /// </summary>
    private static SimpleLoger instance;
    public static SimpleLoger Instance
    {
        get 
        {
            if (instance == null)
                instance = new SimpleLoger();
            return instance;
        }

    }
        
    /// <summary>
    /// Constructor
    /// </summary>
    private SimpleLoger()
    {
        Trace.Listeners.Clear();
        Trace.Listeners.Add(new LogerTraceListener());
    }

    public void Debug(object msg)
    {
        Trace.WriteLine(msg, "Debug");
    }

    public void Warn(object msg)
    {
        Trace.WriteLine(msg, "Warn");
    }

    public void Info(object msg)
    {
        Trace.WriteLine(msg, "Info");
    }

    public void Error(object msg)
    {
        Trace.WriteLine(msg, "Error");
    }
}
```

&emsp;&emsp;现在我们来重点关注SimpleLoger的构造函数，显然在这里它应该是私有的，在这里我们首先从Trace类的Listeners中移除所有的监听器，这样做的目的是改变Trace类的输出行为，因为在前面介绍Trace的时候我们了解到，Trace类和Debug类默认将调试信息输出在“输出”窗口中的，而我们现在希望将调试信息输出到日志文件中，所以我们需要改变Trace类的输出行为，改变的方式非常简单啦，移除默认的监听器，然后添加我们自己定义的监听器哇，对对对，就是这样简单粗暴。下面我们来看看如何定义这样一个监听器LogerTraceLitener，它继承自TraceListener这个类，这意味着我们如果要实现一个自定义监听器，只需要继承TraceListener然后重写相关方法即可：

```
public class LogerTraceListener:TraceListener
{
    /// <summary>
    /// FileName
    /// </summary>
    private string m_fileName;

    /// <summary>
    /// Constructor
    /// </summary>
    public LogerTraceListener()
    {
        string basePath = AppDomain.CurrentDomain.BaseDirectory + "\\Logs\\";
        if(!Directory.Exists(basePath)) 
            Directory.CreateDirectory(basePath);
        this.m_fileName = basePath + 
        	string.Format("Log-{0}.txt", DateTime.Now.ToString("yyyyMMdd"));
    }

    /// <summary>
    /// Write
    /// </summary>
    public override void Write(string message)
    {
        message = Format(message, "");
        File.AppendAllText(m_fileName,message);
    }

    /// <summary>
    /// Write
    /// </summary>
    public override void Write(object obj)
    {
        string message = Format(obj, "");
        File.AppendAllText(m_fileName, message);
    }

    /// <summary>
    /// WriteLine
    /// </summary>
    public override void WriteLine(object obj)
    {
        string message = Format(obj, "");
        File.AppendAllText(m_fileName, message);
    }

    /// <summary>
    /// WriteLine
    /// </summary>
    public override void WriteLine(string message)
    {
        message = Format(message, "");
        File.AppendAllText(m_fileName, message);
    }

    /// <summary>
    /// WriteLine
    /// </summary>
    public override void WriteLine(object obj, string category)
    {
        string message = Format(obj, category);
        File.AppendAllText(m_fileName, message);
    }

    /// <summary>
    /// WriteLine
    /// </summary>
    public override void WriteLine(string message, string category)
    {
        message = Format(message, category);
        File.AppendAllText(m_fileName, message);
    }

    /// <summary>
    /// Format
    /// </summary>
    private string Format(object obj, string category)
    {
        StringBuilder builder = new StringBuilder();
        builder.AppendFormat("{0} ",DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss"));
        if (!string.IsNullOrEmpty(category))
            builder.AppendFormat("[{0}] ", category);
        if (obj is Exception){
            var ex = (Exception)obj;
            builder.Append(ex.Message + "\r\n");
            builder.Append(ex.StackTrace + "\r\n");
        } else{
            builder.Append(obj.ToString() + "\r\n");
        }

        return builder.ToString();
    }
}
```

&emsp;&emsp;在这里我重写了好多好多方法，可是实际上我在SimpleLoger中仅仅用到WriteLine这个方法，大家可以发挥自己的想象力，因为我始终相信编程是一件有趣的事情，我们有时候会感到沮丧，完全是因为这个糟糕的世界里充满了同样糟糕的事情。其实程序员是一个理性与感性并存的职业，如果是操作系统、编译原理和图形学可以并称为程序员的三大浪漫，那么Big Clean Problem将是我们最这个世界最好的敬畏，我们喜欢解决问题本质上是因为我们对这个世界充满好奇，可这并不意味着我们对问题来者不拒，这个世界产生的大部分问题都是因为人类的无知，可人类到此刻依然认为这一切非常合理。

&emsp;&emsp;现在，让我们来检验我们的这个小玩意儿，我们将编写一个非常简单的单元测试案例，我们都知道当除数为0时在数学上是没有任何意义的，所以在计算机中当我们尝试除以0的时候会引发异常，由此我们会写出下面的代码：

```
[TestMethod]
public void Test()
{
    try{
        int i=0;
        Console.WriteLine(5/i);
    }catch (Exception e){
        SimpleLoger.Instance.Debug(e);
    }
}
```
理论上它会在程序根目录下生成一个Logs的文件夹，然后每天会生成一个以日期命名的文本文件。现在，它看起来工作得很好，我没有想要做出一个更好的日志系统的野心，我更喜欢去探索一种全新的可能性，我更在意在这个过程中我们收获了什么，人生本来就充满了各种各样无意义的事情，我们之所以热爱生命，是因为我们希望它变得有趣，这样就足够了，不是吗？

![效果演示](https://ws1.sinaimg.cn/large/4c36074fly1fzix8f21hlj20vb097aac.jpg)