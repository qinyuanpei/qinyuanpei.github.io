---
title: 《C#多线程编程实战》读书笔记
categories:
  - 读书笔记
tags:
  - 读书
  - 多线程
  - 笔记
abbrlink: 345410188
date: 2018-01-07 21:34:36
---
本文是一篇读书笔记，由[《C#多线程编程实战》](https://book.douban.com/subject/26574917/)一书中的内容整理而来，主要梳理了.NET中多线程编程相关的知识脉络，从Thread、ThreadPool、Task、async/await、并发集合、Parallel、PLINQ到Rx及异步I/O等内容，均有所覆盖。为了帮助大家理解本文内容，首先给出博主在阅读该书过程中绘制的思维导图，大家可以根据个人需要针对性的查漏补缺。

![《多线程编程实战》思维导图](http://img.blog.csdn.net/20180112234912008)

# 线程基础
* Tips1：暂停线程，即通过Thread.Sleep()方法让线程等待一段时间而不用消耗操作系统资源。当线程处于休眠状态时，它会占用尽可能少的CPU时间。
* Tips2：线程等待，即通过Join()方法等待另一个线程结束，因为不知道执行所需要花费的时间，此时Thread.Sleep()方法无效，并且第一个线程等待时是处于阻塞状态的。
* Tips3：终止线程，调用Abort()方法会给线程注入ThreadAbortException异常，该异常会导致程序崩溃，且该方法不一定总是能终止线程，目标线程可以通过处理该异常并调用Thread.ResetAbort()方法来拒绝被终止，因此不推荐使用Abort()方法来终止线程，理想的方式是通过CancellationToken来实现线程终止。
* Tips4：线程优先级，线程优先级决定了该线程可占用多少CPU时间，通过设置IsBackground属性可以指定一个线程是否为后台线程，默认情况下，显式创建的线程都是前台线程。其主要区别是：进程会等待所有的前台线程完成后再结束工作，但是如果只剩下后台线程，则会直接结束工作。需要注意的是，如果程序定义了一个不会赞成的前台线程，主程序并不会正常结束。
* Tips5：向线程传递参数，可以通过ThreadStart或者lambda表达式来向一个线程传递参数，需要注意的是，由lambda表达式带来的闭包问题
* Tips6：竞争条件是多线程环境中非常常见的导致错误的原因，通过lock关键字锁定一个静态对象(static&readonly)时，需要访问该对象的所有其它线程都会处于阻塞状态，并等待直到该对象解除锁定，这可能会导致严重的性能问题，
* Tips7：发生死锁的原因是锁定的静态对象永远无法解除锁定，通常Monitor类用以解除死锁，而lock关键字用以创建死锁，Monitor类的TryEnter()方法可以用以检测静态对象是否可以解锁，lock关键字本质上是Monitor类的语法糖。
```
bool acquiredLock = false;
try
{
  Monitor.Enter(lockObject, ref acquiredLock)
}
finally
{
  if(acquiredLock)
  {
    Monitor.Exit(lockObject)
  }
}
```
* Tips8：不要在线程中抛出异常，而是在线程代码中使用try…catch代码块。
# 线程同步
* Tips9：无须共享对象，则无须进行线程同步，通过重新设计程序来移除共享状态，从而避免复杂的同步构造；使用原子操作，这意味着一个操作只占用一个量子的时间，一次就可以完成，并且只有当前操作完成后，其它线程方可执行其它操作，因此，无须实现其它线程等待当前操作完成，进而避免了使用锁，排除了死锁。
* Tips10：为了实现线程同步，我们不得不使用不同的方式来协调线程，方式之一是将等待的线程设为阻塞，当线程处于阻塞状态时，会占用尽可能少的CPU时间，然而这意味着会引入至少一次的上下文切换。上下文切换，是指操作系统的线程调度器，该调度器会保存等待的线程状态，并切换到另一个线程，依次恢复等待的线程状态，而这需要消耗更多的资源。
* Tips11：线程调度模式，当线程挂起很长时间时，需要操作系统内核来阻止线程使用CPU时间，这种模式被称为内核模式；当线程只需要等待一小段时间，而不需要将线程切换到阻塞状态，这种模式被称为用户模式；先尝试按照用户模式进行等待，如线程等待足够长时间，则切换到阻塞状态以节省CPU资源，这种模式被称为混合模式。
* Tips12：Mutex是一种原始的同步方法，其只对一个线程授予对共享资源的独占访问，Mutex可以在不同的程序中同步线程。
* Tips13：SemaphoreSlim是Semaphore的轻量级版本，用以限制同时访问同一个资源的线程数量，超过该数量的线程需要等待，直到之前的线程中某一个完成工作，并调用Release()方法发出信号，其使用了混合模式，而Semaphore则使用内核模式，可以在跨程序同步的场景下使用。
* Tips14：AutoResetEvent类用以从一个线程向另一个线程发送通知，该类可以通知等待的线程有某个事件发生，其实例在默认情况下初始状态为unsignaled，调用WaitOne()方法时将会被阻塞，直到我们调用了Set方法；相反地，如果初始状态为signaled，调用WaitOne()方法时将会被立即处理，需要我们再调用一次Set方法，以便向其它线程发出信号。
* Tips15：ManualResetEventSlim类是使用混合模式的线程信号量，相比使用内核模式的AutoResetEvent类更好(因为等待时间不能太长)，AutoResetEvent像一个旋转门，一次仅允许一个人通过，而ManualResetEventSlim是ManualResetEvent的混合版本，一直保持大门开启直到手动屌用Reset方法。
* Tips16：EventWaitHandle类是AutoResetEvent和ManualResetEvent的基类，可以通过调用其WaitOne()方法来阻塞线程，直到Set()方法被调用，它有两种状态，即终止态和非终止态，这两种状态可以相互转换，调用Set()方法可将其实例设为终止态，调用Reset()方法可以将其实例设为非终止态。
* Tips17：CountdownEvent类可以用以等到直到一定数量的操作完成，需要注意的是，如果其实例方法Signal()没有达到指定的次数，则其实例方法Wait()将一直等待。所以，请确保使用CountdownEvent时，所有线程完成后都要调用Signal()方法。
* Tips18：ReaderWriterLockSlim用以创建一个线程安全的机制，在多线程中对一个集合进行读写操作，ReaderWriterLockSlim代表了一个管理资源访问的锁，允许多个线程同时读取，以及独占写。其中，读锁允许多线程读取数据，写锁在被释放前会阻塞其它线程的所有操作。
* Tips19：SpinWait类是一个混合同步构造，被设计为使用用户模式等待一段时间，然后切换到内核模式以节省CPU时间。
# 使用线程池
* Tips20：volatile关键字指出一个字段可能会被同时执行的多个线程修改，声明为volatile的字段不会被编译器和处理器优化为只能被单线程访问。
* Tips21：创建线程是昂贵的操作，所以为每个短暂的异步操作创建线程会产生显著的开销。线程池的用途是执行运行时间短的操作，使用线程池可以减少并行度耗费及节省操作系统资源。在ASP.NET应用程序中使用线程池时要相当小心，ASP.NET基础切实使用自己的线程池，如果在线程池中浪费所有的工作者线程，Web服务器将不能够服务新的请求，在ASP.NET中只推荐使用I/O密集型的异步操作，因为其使用了一个不同的方式，叫做I/O线程。
* Tips22：APM，即异步编程模型，是指使用BeginXXX/EndXXX和IAsyncResult对象等方式，其通过调用BeginInvoke方法返回IAsyncResult对象，然后通过调用EndInvoke方法返回结果，我们可通过轮询IAsyncResult对象的IsCompleted或者调用IAsyncResult对象的AsyncWaitHandle属性的WaitOne()方法来等待直到操作完成。
* Tips23：ThreadPool.RegisterWaitForSingleObject()方法允许我们将回调函数放入线程池中的队列中，当提供的等待事件处理器收到信号或发生超时时，该回调函数将被调用，这做鱼我们为线程池中的操作实现超时功能。具体思路是：ManualResetEvent + CancellationToken，当接收到ManualResetEvent对象的信号时处理超时，或者是使用CancellationToken来处理超时。
* Tips24：CancellationToken是.NET4.0中被引入的实现异步操作的取消操作的事实标准，我们可以使用三种方式来实现取消过程，即轮询IsCancellationRequested属性、抛出OperationCanceledException异常、为CancellationToken注册一个回调函数。
* Tips25：Timer对象用以在线程池中创建周期性调用的异步操作。
* Tips26：BackgroundWorker组件，是典型的基于事件的异步模式，即EAP，当通过RunWorkerAsync启动一个异步操作时，DoWork事件所订阅的事件处理器，将会运行在线程池中，如果需要需要取消异步操作，则可以调用CancelAsync()方法。
# 使用任务并行库
* Tips27：TPL即任务并行库，在.NET 4.0中被引入，目的是解决APM和EAP中获取结果和传播异常的问题，TPL在.NET4.5中进行了调整，使其在使用上更简单，它可以理解为线程池之上的又一个抽象层，对程序员隐藏了与线程池交互的底层代码，并提供了更方便的细粒度的API。TPL的核心概念是任务，一个任务代表了一个异步操作，该操作可以通过多种方式运行，可以使用或者不使用独立线程运行。TPL相比之前的模式，一个关键优势是其具有用于组合任务的便利的API。
* Tips28：Task.Run是Task.Factory.StartNew的一个快捷方式，后者有附加的选项，在无特殊需求的情况下，可以直接使用Task.Run，通过TaskScheduler，我们可以控制任务的运行方式。
* Tips29：使用Task实例的Start方法启动任务并等待结果，该任务会被放置在线程池中并且主线程会等待，直到任务返回前一直处于阻塞状态；使用Task实例的RunSynchronously方法启动任务，该任务是运行在主线程中，这是一个非常好的优化，可以避免使用线程池来执行非常短暂的操作；我们可以通过轮询Task实例的状态信息来判断一个任务是否执行结束。
* Tips30：通过Task实例的ContinueWith方法可以为任务设置一个后续操作，通过TaskContinuationOptions选项来指定后续任务以什么样的方式执行。
* Tips31：通过Task实例的FromAsync可以实现APM到Task的转换
* Tips32：通过TaskCompletionSource可以实现EAP到Task的转换
* Tips33：TaskScheduler是一个非常重要的抽象，该组件实际上负责如何执行任务，默认的任务调度程序将任务放置在线程池的工作线程中。为了避免死锁，绝对不要通过任务调度程序在UI线程中使用同步操作，请使用ContinueWith或async/await方法。
# 使用C# 6.0
* Tips34：异步函数是C# 5.0引入的语言特性，它是基于TPL之上的更高级别抽象，真正简化了异步编程。要创建一个异步函数，首先需要使用async关键字标注一个方法，其次异步函数必须返回Task或Task类型，可以使用async void的方法，但是更推荐async Task的方法，使用async void的方法的唯一合理的地方就是在程序中使用顶层UI控制器事件处理器的时候，在使用async关键字标注的方法内部，可以使用await操作符，该操作符可与TPL任务一起工作，并获取该任务中异步操作的结果，在async方法外部不能使用await关键字，否则会有编译错误，异步函数代码中至少要拥有一个await关键字。
* Tips35：在Windows GUI或ASP.NET等环境中不推荐使用Task.Wait和Task.Result，因为非常有可能会造成死锁。
  async可以和lambda表达式联用，在表达式体中应该至少含有一个await关键字标示，因为lambda表达式的类型无法通过自身推断，所以必须显式地向C#编译器指定类型。
* Tips36：异步并不总是意味着并行执行
* Tips37：单个异步操作可以使用try…catch来捕获异常，而对于一个以上的异步操作，使用try…catch仅仅可以从底层的AggregateException对象中获得第一个异常，为了获得所有的异常，可以使用AggregateException的Flatten()方法将层级异常放入一个列表，并从中提取出所有的底层异常。
* Tips38：通过Task实例的ConfigureAwait()方法，可以设置使用await时同步上下文的行为，默认情况下，await操作符会尝试捕捉同步上下文，并在其中执行代码，即调度器会向UI线程投入成千上百个后续操作任务，这会使用它的消息循环来异步地执行这些任务，当我们不需要在UI线程中运行这些代码时，向ConfigureAwait方法传入false将会是一个更高效的方案。
* Tips39：async void方法会导致异常处理方法，会放置到当前的同步上下文中，因此线程池中未被处理的异常会终结整个进程，使用AppDomain.UnhandledException事件可以拦截未处理的异常，但不能从拦截的地方恢复进程，async void的lambda表达式，同Action类型是兼容的，强烈建议仅仅在UI事件处理器中使用async void方法，在其他情况下，请使用返回Task或者Task的方法。
# 使用并行集合
* Tips40：ConcurrentQueue使用了原子的比较和交换(CAS)，以及SpinWait来保证线程安全，它实现了一个先进先出(FIFO)的集合，这意味着元素出队列的顺序与加速队列的顺序是一致的，可以调用Enqueue方法向对接中加入元素，调用TryDequeue方法试图取出队列中第一个元素，调用TryPeek方法试图得到第一个元素但并不从队列中删除该元素。
* Tips41：ConcurrentStack的实现同样没有使用锁，仅采用了CAS操作，它是一个后进先出(LIFO)的集合，这意味着最后添加的元素会先返回，可以调用Push和PushRange方法添加元素，使用TryPop和TryPopRange方法获取元素，使用TryPeek方法检查元素。
* Tips42：ConcurrentBag是一个支持重复元素的无序集合，它针对以下情况进行了优化，即多个线程以这样的方式工作：每个线程产生和消费其自身的任务，极少发生线程间的交互(因为要交互就要使用锁)。可以调用Add方法添加元素，调用TryPeek方法检查元素，调用TryTake方法获取元素。
* Tips43：ConcurrentDictionary是一个线程安全的字典集合的实现，对于读操作无需使用锁，对于写操作则需要使用锁，该并发字典使用多个锁，在字典桶之上实现了一个细粒度的锁模型(使用锁的常规字典称为粗粒度锁)，参数concurrentLevel可以在构造函数中定义锁的数量。这意味着预估的线程数量将并发地更新该字典。由于并发字典使用锁，如无必要请避免使用以下操作：Count、IsEmpty、Keys、Values、CopyTo及ToArray，因为需要获取该字典中的所有锁。
* Tips44：BlockingCollection是一个针对IProducerConsumerCollection泛型接口实现的高级封装，它有很多先进的功能来实现管道场景，即当你有一些步骤需要使用之前步骤运行的结果时。BlockingCollection类支持分块、调整内部集合容量、取消集合操作、从多个块集合中获取元素等。
* Tips45：对BlockingCollection进行迭代时，需要注意的是，使用GetConsumingEnumerable()进行迭代，因为虽然BlockingCollection实现了IEnumerable接口，但是它默认的行为是表示集合的“快照”，这不是我们期望的行为。
# 使用PLINQ
* Tips46：将程序分割成一组任务并使用不同的线程来运行不同的任务，这种方式被称为任务并行
  将数据分割成较小的数据块，对这些数据进行并行计算，然后聚合这些计算结果，这种编程模型称为数据并行
* Tips47：结构并行确实更易维护，应该尽可能地使用，但它并不是万能的。通常有很多情况我们是不能简单地使用结构并行，那么以非结构化的方式使用TPL任务并行也是完全可以的。
  Parallel类中的Invoke方法是最简单的实现多任务并行的方法，Invoke方法会阻塞其它线程直到所有线程都完成。
* Tips48：Parallel类中的For和ForEach方法可以定义并行循环，通过传入一个委托来定义每个循环项的行为，并得到一个结果来说明循环是否成功完成，ParallelOptions类可以为并行循环定义最大并行数，使用CollectionToken取消任务，使用TaskScheduler类调度任务。
* Tips49：ParallelLoopState可以用于从循环中跳出或者检查循环状态，它有两种方式：Break和Stop，Stop是指循环停止处理任何工作，而Break是指停止其之后的迭代，继续保持其之前的迭代工作。
* Tips50：同Task类似，当使用AsParallel()方法并行查询时，我们将得到AggregateException，它将包含运行PLINQ期间发生的所有异常，我们可以使用Flatten()方法和Handle()方法来处理这些异常。
* Tips51：ParallelEnumerable类含有PLINQ的全部逻辑，并且作为IEnumerable集合功能的一组扩展方法，默认情况下结果会被合并单个线程中，我们可以通过ForAll方法来指定处理逻辑，此时它们使用的是同一个线程，将跳过合并结果的过程，除了AsParallel()方法，我们同样可以使用AsSequential()方法，来使得PLINQ查询以顺序方式执行(相对于并行)
* Tips52：PLINQ中提供了丰富用以PLINQ查询的选项，例如WithCancellation()方法用以取消查询，这将导致引发OperationCanceledException异常，并取消剩余的工作；例如WithDegreeOfParallelism()方法用以指定执行查询时实际并行分割数，可以决定并行执行会占用多少资源及其性能如何；例如WithExecutionMode()可以重载查询执行的模式，即我们可以决定选择以顺序执行还是并行执行的方式去执行查询；例如WithMergeOptions()方法可以用以调整对查询结果的处理，默认PLINQ会将结果合并到单个线程中，因此在查询结果返回前，会缓存一定数量的结果，当发现查询花费大量时间时，更合理的方式是关闭结果缓存从而尽可能快地得到结果；例如AsOrdered()方法，用以告诉PLINQ我们希望按照集合中的顺序进行处理(并行条件下，集合中的项有可能不是按顺序被处理的)
# 使用异步I/O
* Tips53：异步I/O，对服务器而言，可伸缩性是最高优先级，这意味着单个用户消耗的资源越少越好，如果为每个用户创建多个线程，则可伸缩性并不好，在I/O密集型的场景中需要使用异步，因为不需要CPU工作，其瓶颈在磁盘上，这种执行I/O任务的方式成为I/O线程。
  在异步文件读写中，FileOptions.Asynchronous是一个非常重要的选项，无论有无此参数都可以，以异步的方式使用该文件，区别是前者仅仅是在线程池中异步委托调用，而后者可以对FileStream垒使用异步I/O。
* Tips54：对HttpListener类，我们可以通过GetContextasync()方法来异步地获取上下文。
* Tips55：对数据库而言，我们可以通过OpenAsync()、ExecuteNonQueryAsync()等方法异步地执行SQL语句。

好了，以上就是这篇读书笔记的主要内容啦，听说掌握了这55条Tips的人，都敢在简历上写”精通多线程编程“，哈哈，晚安啦，各位！