---
abbrlink: 187480982
categories:
- 编程语言
date: 2017-04-15 21:10:47
description: async void方法引发异常时，因为它没有Task对象来放置异常，因此它的异常SynchronizationContext上引发，而且因为[AsyncVoidMethodBuilder](http://msdn.microsoft.com/en-us/library/system.runtime.compilerservices.asyncvoidmethodbuilder.aspx)内部并没有使用TaskScheduler，因此对于async
  void方法来说，线程池中未捕获的异常将会一直向上抛并最终导致程序异常终止，虽然我们可以在AppDomain.UnhandledException这个事件中捕捉到这些"未处理的异常"，但这并不能阻止程序异常终止，通过我们可以通过注册这个事件来记录异常日志，以帮助我们快速定位问题
tags:
- Lambda
- 异步
- 编程
title: 异步Lambda表达式问题的探索
---

各位朋友，大家好，欢迎大家关注我的博客，我是Payne，我的博客地址是:[http://qinyuanpei.com](http://qinyuanpei.com)。今天博主想和大家探讨的是，.NET中异步Lambda表达式的问题。为什么要讨论这个问题呢，这或许要从公司首席架构推广内部框架这件事情说起。我其实很久以前就有这种在团队内部做技术演进的想法，即通过公共类库、团队Wiki和技术交流等形式逐步地推进和完善团队整体架构的统一，因为一个团队在业务方向和技术选型上基本是一致的，因此团队内的技术演进对提高开发效率和交付质量意义重大，所以我能理解首席架构在内部推广公共类库这件事情，因为除了KPI这种功利性的目标以外，从长远来看这些东西对一个团队来说是积极而有利的，可是我们都知道工程师是这个世界上最傲慢的人，如果一个东西设计得不好，他们一定会尝试去改进甚至重新设计，所以架构并非是一种虚无缥缈的、凭空想象出来的东西，它的存在必须是为了解决某种问题。

  所以我始终认为，架构设计必须由一线开发人员来提炼和抽象，因为只有真正经历过"坑"的人，才会清楚地知道团队里最需要解决的问题是什么，一个良好的架构绝对不是由某些所谓"专家"闭门造车的结果，你只有真正了解了一个问题，懂得如何去定义一个问题，你才会知道目前这个团队中最迫切需要去解决的问题是什么，虽然说团队里技术层次存在差异，一个技术选型必然会和普通社会学问题一样存在众口难调的情形，可是一个东西设计得不好它就是不好，你不能强迫团队成员必须去使用它，因为这实在有悖于"自由"和"分享"的黑客文化。我相信软件开发没有银弹可言，这意味着它没有一种一劳永逸的解决方案，即使它的抽象层次再高、代码鲁棒性再好，所以团队内部技术演进应该采取"自下而上"的方式，对待工程师最好的方式就是给他们充分的自由，"自上而下"的行政命令不适合工程师文化，自计算机文明诞生以来，那种来自内心深处的"极客思维"决定了我们的基因，所以啊，"请原谅我一生不羁放纵爱自由"。

  好了，现在回到这个问题本身，问题产生的根源来自ICommand接口，而我们都知道该接口主要承担命令绑定作用。通过ICommand接口的定义我们可以知道，ICommand接口的Execute方法是一个同步方法，因此常规的做法如RelayCommand或者DelegateCommand，基本上都是传入一个Action来指向一个具体方法，最终ICommand接口中的Execute方法执行的实际上是这个具体方法。截止到目前为止，这个策略在主流的场景下都实施得非常好，可是我们在引入Task、async/await这些新的概念以后，我们突然发现ICommand接口存在一个亟待解决的问题，即它缺乏一个支持异步机制的Execute方法，显然这是一个历史遗留问题。
  
  我开始关注这个问题是当我在同事John和Charles的项目中看到类似下面的代码，事实上他们都是非常优秀的高级工程师，在对这个问题理解和探讨的过程中，我要特别感谢他们愿意分享他们的想法。我们一起来看看下面的代码：
```
public RelayCommand RunCommand
{
  get
  {
    return new RelayCommand(async ()=>{
      /* await awaitable */
    });
  }
}
```
  请相信你的眼睛，因为你没有看错，让我倍感纠结的的正是这样一段简单的代码。这段代码让我迷惑的地方有两处，第一，RelayCommand实现了ICommand接口，而ICommand接口的Execute方法是一个同步的方法，为什么我们可以在这个里传入一个异步方法，并通过Action这种委托类型来对其进行包装；第二，Action是一个void类型，即无返回值的委托类型，我们这里显然使用async关键字修饰了一个无返回值的方法，因为我们在这个匿名方法内部使用了await语法。可是我们知道微软官方的建议是，使用async关键字来修饰一个返回值类型为Task或者Task<T>的方法。在我了解到async关键字还可以这样使用以后，对第二处疑惑我稍稍有些许释怀，因为事实上Charles就是正式通过这种思路来启发我，可我始终无法理解，为什么我们可以在一个同步的方法里执行一段异步代码，并试图去安慰自己说这段代码是异步的，在执行一个非常耗时的任务时界面不会阻塞。

  我们的项目需要在整个任务执行过程中输出操作日志，这意味着消息会实时地输出到界面上并且不会阻塞界面。我们在为此设计了一个基于观察者模式的消息队列，所有需要发送实时消息的模块被抽象为一个消息主题，而界面模块、日志模块等被抽象为消息观察者，所有订阅过的消息主题都会将消息推送到消息队列中，这一切目前在设计上是符合业务需求的。可是很快我们就会发现一个问题，使用await或者Wait()方法时，消息并不是实时地发送到界面上去的，因为我们知道await或者Wait()方法会一直等待一个异步任务执行完成，所以消息会在任务结束的一瞬间被全部发送到界面上，这显示是不符合我们的期望的，所以Execute()方法里执行的必然是一个同步方法，它不会因为我们传入了一个异步方法而改变，况且同步和异步是相对而言的，如果我们将await语法修改为Task.Run()，我们就会发现在异步任务执行完成前同步方法就开始执行了，而这正是我们想要的结果。

  在这里我更感兴趣的一个问题是，.NET框架中的委托、匿名方法、Lambda表达式和Task是不同时期.NET的产物，那么我们在这里使用一个async关键字来修饰一个匿名方法，编译器在处理它的时候到底会怎么做呢？因为我们知道委托会被编译成一个包装类，那么现在在这篇文章中的提到的这个问题背景下，它会有什么不同呢？我们一起来看下面的代码：

```
static void Main(string[] args)
{
  Action action1 = async () => await DoWorkAsync();
  Action action2 = () => DoWork();
}
```

  我们注意到这里声明了两个Action，即两个没有返回值的委托类型，它们的不同点在于前者使用了async/await这两个关键字，而后者则是一个普通的同步方法，那么这两者生成的IL代码是否有区别呢？我们可以通过IL DASM或者是IL Spy这两个工具来查看IL代码：

![查看IL代码](https://ww1.sinaimg.cn/large/4c36074fly1fzix8rsjiej20sh0g0tav.jpg)

  我们可以注意到两点，第一，两个委托类型生成的中间代码完全一致，都是**CachedAnonymousMethodDelegate**，这在某种程度上说明不管Action里包装的是一个同步方法还是一个异步方法，最终生成的IL代码应该都是相同的。第二，同匿名方法和扩展方法一样，async/await并未引入新的IL指令，async/await内部应该是在维护一个状态机，这一点和yield关键字应该是相似的，并且对于异步的匿名方法(指voild类型)，通过IL代码可知它是由[AsyncVoidMethodBuilder](http://msdn.microsoft.com/en-us/library/system.runtime.compilerservices.asyncvoidmethodbuilder.aspx)类来生成的，而对于异步的方法(指Task和Task<T>类型)，则是由[AsyncTaskMethodBuilder](http://msdn.microsoft.com/en-us/library/system.runtime.compilerservices.asynctaskmethodbuilder.aspx)类来生成，需要说明的是这两者在功能上相差无几，唯一的区别就在于异常处理。

  关于异步编程中异常的处理，老赵在其博客[关于C#中async/await中的异常处理（上）](http://blog.zhaojie.me/2012/04/exception-handling-in-csharp-async-await-1.html)和 [关于C#中async/await中的异常处理（下）](http://blog.zhaojie.me/2012/04/exception-handling-in-csharp-async-await-2.html)这两篇博客中做了非常详细的解释，建议大家有时间的话去阅读这两篇文章，我们在这里关注结论就好。
  
  具体来讲，async Task或者async Task<T>方法引发异常时，会捕获异常并将其放置在Task对象里，并且只有Task对象被await时会引发异常。特别地，在调用Task.WhenAll()方法时，一个Task对象中可能会含有多个异常，此时await仅仅会重新抛出第一个异常，但是在 Task 上使用 Task.Wait 或 Task.Result 同步阻塞时，所有异常都会用 AggregateException 包装后引发。对于嵌套的Task，即含有子任务的Task，应该采用AggregateException来获取和处理所有的异常。Task/Task<T>中未捕获的异常可以通过TaskScheduler.UnobservedTaskException来处理，这些异常不会继续向上抛导致程序异常退出。
  
  async void方法引发异常时，因为它没有Task对象来放置异常，因此它的异常SynchronizationContext上引发，而且因为[AsyncVoidMethodBuilder](http://msdn.microsoft.com/en-us/library/system.runtime.compilerservices.asyncvoidmethodbuilder.aspx)内部并没有使用TaskScheduler，因此对于async void方法来说，线程池中未捕获的异常将会一直向上抛并最终导致程序异常终止，虽然我们可以在AppDomain.UnhandledException这个事件中捕捉到这些"未处理的异常"，但这并不能阻止程序异常终止，通过我们可以通过注册这个事件来记录异常日志，以帮助我们快速定位问题。

  好了，现在我们回到这篇文章开始的问题，我们现在知道async Task和async Task<T>引发的异常，都不会是程序立即终止，除非我们显式地去await一个Task对象会引发异常，可是对async void来讲，一旦它引发异常，常规的try-catch时无法捕捉到异常的，这种"未处理的异常"会一直向上抛并最终导致程序异常终止。我为什么要说这个问题呢，因为我们在文章开始的时候写了一个异步的lambda表达式，最终它会被编译为async void，我们现在应该会了解到，async void非常容易引发未处理的异常并导致程序异常退出，所以这是微软官方最佳实践中不推荐使用async void的原因，因为使用async void就意味着我们要去捕获所有的异常。可是对标记为async的lambda表达式来讲，这个问题是非常隐蔽而且蛋疼的，或许不使用async void就是最为正确的选择了吧！

  最后，其实坦白讲，我自己是不清楚在这篇文章里我到底说什么的，因为这样一个在项目开发中遇到的问题，其实并不是一个特别重要的内容，因为它实在是太容易被我们给忽略啦。我最初关注这个问题完全是因为好奇，因为我从来没有见到过这种lambda表达式的写法，虽然纠结这样一个语法上的问题，和孔乙己讨论茴香豆的"茴"字由几种写法一样，都是一个相当迂腐不堪的表现，可我庆幸这份好奇让我了解到了更多的东西。其实总结下这篇文章中关注的点，主要有：

* 由同步方法和异步方法包装的委托类型在IL层面上是无差别的，委托关注的是参数列表和返回类型，和是否有async关键字修饰没有关系。
* 匿名方法或者lambda最终依然会被编译为一个方法，在有async关键字修饰的情况下，建议使用Func而不是Action，因为前者可以生成async Task或者async Task<T>，而后者仅仅可以生成async void。
* async Task/async Task<T>和async void在异常处理机制上存在差异，前者未处理的异常不会继续向上抛导致程序异常退出，而后者未处理的异常会继续向上抛并导致程序异常退出，因此如果坚持要使用async void，就一定处理各种异常。



---

参考文章：
[Microsoft - async/await - 异步编程中的最佳做法](https://www.baidu.com/link?url=f9umAhHAgIYBz5X8dwyjUnu1g8w9RCPtJohhtnWsxDW8BdwLHKFVP0hA1sg0PwOTBF6zKP7AlEPZKiDYgLGleK&wd=&eqid=e9ff05d4000bd133000000035921a2ab)
[TianFang - C# 5.0 async 函的提示和技巧](http://www.cnblogs.com/TianFang/archive/2012/12/24/2831341.html)