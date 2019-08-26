---
abbrlink: 569337285
categories:
- 编程语言
date: 2016-07-21 14:27:07
description: 在这篇文章里我们讨论了MVC、MVP、MVVM各自架构变迁的前因后果，由此我们知道了软件设计中，一个典型的设计目标是让视图和模型分离，可我们同样发现，带着这个目标去设计软件的时候，我们基本鲜有更换视图的时候，虽然从理论上来讲，所有的业务逻辑都是在ViewModel中，视图和模型应该是可以进行更换的，可是你告诉我，有谁会为同一个软件制作不同的界面呢
tags:
- MVVM
- 委托
- 命令
title: 浅析WPF中MVVM模式下命令与委托的关系
---

&emsp;&emsp;各位朋友大家好，我是Payne，欢迎大家关注我的博客，我的博客地址是[http://qinyuanpei.com](http://qinyuanpei.com)。最近因为项目上的原因开始接触WPF，或许这样一个在现在来讲显得过时的东西，我猜大家不会有兴趣去了解，可是你不会明白对某些保守的项目来讲，安全性比先进性更为重要，所以当你发现银行这类机构还在使用各种“复古”的软件系统的时候，你应该相信这类东西的确有它们存在的意义。与此同时，你会更加深刻地明白一个道理：技术是否先进性和其流行程度本身并无直接联系。由此我们可以推论出：一项不流行的技术不一定是因为它本身技术不先进，或许仅仅是因为它无法满足商业化的需求而已。我这里的确是在说WPF,MVVM思想最早由WPF提出，然而其发扬光大却是因为前端领域近年来比较热的AngularJS和Vue.js，我们这里表达的一个观点是：很多你以为非常新潮的概念，或许仅仅是被人们重新赋予了新的名字，当你理清这一切的来龙去脉以后，你会发现这一切并没有什么不同。这符合我一贯的主张：去发现问题的实质、不要被框架束缚、通过共性来消除差异，所以在今天这篇文章里，我想说说WPF中MVVM模式下命令与委托的关系。

<!--more-->

# 什么是MVVM?
&emsp;&emsp;既然提及MVVM，那么我们就无可避免的需要知道什么是MVVM。我们在本文开篇已经提到，MVVM这个概念最早由微软提出，具体来讲是由微软架构师John Gossman提出的。我个人更喜欢通过将MVC、MVP和MVVM这三者横向对比的方式来加强理解，因为这从某种意义上来讲，这是一个逐步改进和演化的过程。我们常常谈及软件的三层架构，我们常常对MVC耳濡目染以致将其神化，可事实上它们是某种在思想上无限接近的理念而已。

![MVC模式示意图](https://ws1.sinaimg.cn/large/4c36074fly1fzixzarx7ij20ll0bt0sx.jpg)

&emsp;&emsp;首先，我们从最简单的MVC开始说起，作为最常用的软件架构之一，我们可以从上面的图示中看到，MVC其实是非常简单的一个概念，它由模型(Model)、视图(View)和控制器(Controller)三部分组成，建立在一个单向流动的通信基础上，即View通知Controller响应用户请求，Controller在接到View的通知后会更新Model内的数据，然后Model会将新的数据反馈给View。我们发现这个设计可以使软件工程中的关注点分离，我们注意到通过MVC模式，我们实现了视图和模型的分离，通过控制器这个胶水层让两者间接联系起来，所以MVC的优点是让各个模块更好的协作。那么，它的缺点是什么呢？显然，视图和控制器是高度耦合的，因为控制器中无可避免地要访问视图内的元素，所以控制器注定无法在这尘世间独善其身。要知道最早的MVC架构是基于观察者模式实现的，即当Model发生变化时会同时通知View和Controller，所以我们很快就可以认识到：我们从古至今的所有努力，都是为了让视图和模型彼此分离，我们在这条路上越走越远，幸运的是一直都不忘初心。

![MVP模式示意图](https://ws1.sinaimg.cn/large/4c36074fly1fzixbsy01jj20n90bfjrl.jpg)

&emsp;&emsp;接下来，我们为了彻底地让视图和模型分离，我们发明了新的软件架构：MVP。虽然从感性的认识上来讲，它是将Controller改名为Presenter，然而从理性的认识上来讲，它在让视图和模型分离这件事情上做得更为决绝果断。通过图示我们可以发现，视图和模型不再发生直接联系，它们都通过Presenter相互联系，而且各个部分间的通信都变成了双向流动。我们可以很快意识到，现在全新的控制器即Presenter会变得越来越“重”，因为所有的逻辑都在这里，而视图会变得越来越“轻”，它不再需要主动去获取模型提供的数据，它将被动地接拥抱变化，因为现在在视图里基本上没有任何业务逻辑。现在我们可以预见，人类会在隔绝视图和模型这件事情上乘胜追击，人们会尝试让Controller/Presenter/ViewModel变得越来越臃肿，我想说的是，求它们在得知这一切真相时的心理阴影面积，我们试图让每一个模块各司其职、通力协作，结果脏活累活儿都交给了Controller/Presenter/ViewModel，我想说这件事情做的真是漂亮。

![MVVM模式示意图](https://ws1.sinaimg.cn/large/4c36074fly1fzix99unr9j20on0bvweo.jpg)

&emsp;&emsp;历史总是如此的相似，人类在作死的道路上匍匐前进，继续发扬改名的优良传统，这一次是Presenter被改名为ViewModel，在命名这件事情上，我认为程序员都是有某种强迫症因素在里面的，所以当你发现一个事物以一个新的名字出现在你的视野中的时候，通常它会有两种不同的结局，第一，陈酒换新瓶，我们贩卖的不是酒是情怀；第二，看今天的你我怎样重复昨天的故事，我这张旧船票还能否登上你的客船。幸运的是，MVVM相对MVP的确发生了些许改变，一个重要的特性是双向绑定，View的变化将自动反映在ViewModel中，而显然ViewModel是一个为View打造的Model，它可以容纳更多的普通的Model，因此从某种意义上来说，ViewModel依然作为连接View和Model的桥梁而出现，它是对View的一种抽象，而抽象有两层含义，即数据(Property)和行为(Command)，一旦你明白了这一点，ViewModel无非是一个特殊而普通的类而已，特殊是因为它需要实现INotifyPropertyChanged接口，普通是因为它继承了面向对象编程(OOP)的基本思想。

# 更像MVC的MVVM
&emsp;&emsp;到现在为止，我们基本上理解了MVC、MVP和MVVM这三者间的联系和区别，可是这样真的就是最好的结果吗？我们首先来思考一个问题，即什么样的代码应该写在控制器里。比如我们在对项目进行分层的时候，到底应该让控制器负责哪些任务？我们可以让Controller处理单独的路由，同样可以让Controller参与视图逻辑，甚至我们在编写Model的时候，我们可以有两种不同的选择，第一，编写一个简单的数据聚合实体，具体逻辑都交给控制器来处理，我们将这种方式称为贫血模型；第二，编写一个持有行为的数据聚合实体，控制器在业务逻辑中调用这些方法，我们将这种方式称为充血模型。所以，在这里我们纠结的地方，其实是选择让控制器更“重”还是让模型更“重”，我曾经接触过1年左右的Android开发，我认为Android工程是一个相对符合MVC架构的设计，可是我们难免会发现，作为控制器的Activity中的代码非常臃肿，因为我们在这里需要和视图、模型关联起来，所以综合现有的这些软件架构思想，我们发现模型和视图相对来讲都是可以复用的，可是作为连接这两者的Controller/Presenter/ViewModel是非常臃肿而且难以复用的，所以我怀疑我们是否是在真正的使用MVVM。

&emsp;&emsp;我不知道MVVM架构正确的使用方法是什么样的，因为这是我第一次接触到这样一个新的概念，就如同很多年前，我在学校图书馆里看到的一本讲Web开发的书中描写的那样：当我们不了解MVC的时候，我们理所当然地认为通过文件夹将项目划分为Model、View、Controller，这样好像就是MVC啦。可是事实真的是这样吗？以我目前公司项目的情况而已，我认为它更像是使用了双向绑定的MVC，因为你经常可以在ViewModel中看到，某个属性的Get访问器中各种被if-else折磨的“脏”代码，而在ViewModel中我基本上看不到Model的身影，并且因为使用了Binding的概念严重弱化了ViewModel作为类的基本属性，因此它没有构造函数、没有初始化，我们可以在Get访问器中看到各种硬编码，因为视图上的需求经常变动，所以当整个项目结束的时候，我本人是非常不愿意去看ViewModel这部分的代码的，因为项目上要求避免写Code-Behind代码，所以大量的事件被Command和UIEventToCommand代替，这样让ViewModel变得更“重”了。原本我们希望的是让这三者各司其职，结果现在脏活累活儿全部变成了ViewModel一个人的。虽然双向绑定可以避免去写大量赋值语句，可是我知道ViewModel内心深处会表示：宝宝心里苦。

&emsp;&emsp;如果说WPF对技术圈最大的贡献，我认为这个贡献不在双向绑定，而是它真正意义上实现了设计和编程分离，我们必须承认设计和编程都是一项创造性活动，前者趋向感性，而后者趋向理想，在没有实现这两者分离的时候，程序员需要花费大量时间去还原设计师的设计，可是对程序员来讲，一段程序有没有界面设计在某些场合下是完全不重要的，在没有界面设计的情况下，我们可以通过单元测试来测试代码的可靠程度，相反地在有了界面设计以后我们反而不容易做到这一点，所以你问我WPF对技术圈最大的贡献是什么，我会回答它解放了程序员，可以让理性思维去做理性思维更适合的事情。我不太喜欢声明式编程，这里是指WPF中XAML这种继承自XML的标记语言，因为Visual Studio对XAML没有提供调试的支持，所以当你发现视图显示出现问题的时候，你很难分清楚是前台视图绑定出现错误还是后台ViewModel出现错误，只要你输入符合XML规范的内容程序都会编译通过而非引发异常，因为它是用反射所以性能问题广为人所诟病，其次ViewModel中通知前台属性发生变化时需要使用OnPropertyChanged，该方法需要传入一个字符串类型的值，通常是指属性的名称，可是如果你定义了一个字符串类型的属性，当你在这里传入这个属性的时候，因为它是字符串类型所以不会引发编译错误，可是我觉得这个东西还是比较坑。

# 委托与命令
&emsp;&emsp;好了，现在我想说说WPF中的命令和委托，事实上在我计划写这篇文章前，我对这里无比好奇，可当我发现这东西的实质以后，我忽然觉得花费如此大的篇幅来讲解这样一个概念，这是不是会显得特别无聊。我们的项目上使用的是一个叫做MVVM light的框架，当然我们没有使用它的全部功能，公司的前辈们非常猥琐地从这个开源项目中挑了些源代码出来，这里我不想提及关于这个框架本身地相关细节，因为我认为理解问题的实质比学会一个框架更加重要。首先，WPF为每一个控件都提供了一个Command的依赖属性，因为任何实现了ICommand接口的类都可以通过绑定的方式和前台关联起来，我们这里对比下命令和路由事件的区别可以发现，路由事件必须写在Code-Behind代码中，而命令可以写在ViewModel里，所以直观上来讲命令更加自由灵活。下面我们以一个简单的例子来剖析这两者间的关系。

&emsp;&emsp;我们知道使用Command需要实现ICommand接口，所以实现起来是相对容易的，我们这里继续沿用MVVM light中的RelayCommand这个名字：
```
public class RelayCommand : ICommand
{
    private readonly Action<object> m_execute;
    private readonly Predicate<object> m_canExecute;

    public RelayCommand(Action<object> execute)
    {
        this.m_execute = execute;
    }

    public RelayCommand(Action<object> execute, Predicate<object> canExecute)
    {
        this.m_execute = execute;
        this.m_canExecute = canExecute;
    }

    public bool CanExecute(object parameter)
    {
        if (m_canExecute == null)
            return true;

        return m_canExecute(parameter);
    }

    public event EventHandler CanExecuteChanged
    {
        add { CommandManager.RequerySuggested += value; }
        remove { CommandManager.RequerySuggested -= value; }
    }

    public void Execute(object parameter)
    {
        this.m_execute(parameter);
    }
}

```
我们可以看到这里有两个重要的方法，Execute和CanExecute，前者是一个void类型的方法，后者是一个bool类型的方法。当我们需要判断控件是否应该执行某一个过程的时候，CanExecute这个方法就可以帮助我们完成判断，而Execute方法显然是执行某一个过程的方法，可以注意到通过委托我们让调用者更加自由和灵活地传入一个方法，这是我喜欢这种设计的一个地方，因为我的一位同事就对普通的路由事件表示无法理解。

&emsp;&emsp;这里需要说明的是CanExecuteChanged这个事件，这个和INotifyPropertyChanged接口中的PropertyChanged成员类似，是在当CanExecute发生变化的时候通知视图的，我对这里的理解是CanExecute本身就具备对某一个过程是否应该被执行的支持，可是遗憾的是在，在我参与的项目中，人们更喜欢声明大量的布尔类型变量来处理这里的相关逻辑，因此无论是对Property还是Command而言，在ViewModel里都是看起来非常丑陋的代码实现。

&emsp;&emsp;好了，现在对我们而言，这是一个非常愉快的旅程，因为在完成对RelayCommand的定义以后，我们绑定命令和定义命令的过程是非常简单的。除此以外，WPF提供了一个RoutedCommand类，该类实现了ICommand接口，我怀疑MVVM light中的EventToCommand正是通过这种思路实现了路由事件到命令的转换，因为只有RoutedCommand具备访问UI事件的能力，这里我们仅仅提出问题，进一步的思考和验证我们可以留到以后去做。下面我们来看看如何声明和绑定命令：

```
public RelayCommand ClickCommand
{
    get
    {
        return new RelayCommand((arg)=>
        {
            MessageBox.Show("Click");
        });
    }
}
```

显然这个ClickCommand将作为一个属性出现在ViewModel中，我选择了一个我最喜欢用的方法，或许这样看起来非常低端。可是在调试界面的过程中，它要比断点调试更为直接和直观。当我们的ViewModel中出现这样的只读属性的时候，直接在Get访问器中定义它的返回值似乎是最直接有效的方案，可问题是Get访问器应该是非常“轻”的，因为大量业务逻辑的渗透，现在连这里都不能保留其纯粹性了吗？这让我表示非常郁闷啊。

```
<Window x:Class="WPFLearning.Window1"
        xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
        Title="Window" Height="300" Width="300">
    <Grid>
        <Button Content="Button" HorizontalAlignment="Center" 
        	VerticalAlignment="Center" Command="{Binding ClickCommand }"/>  
    </Grid>
</Window>

```
现在你可以发现，委托和命令结合得非常好，当你发现这一切如此美妙的时候，回归本质或许是我们最喜欢的事情，就像纯粹的你我一样，在这个世界上，我们彼此装点着各自生命里美好的风景，执著而勇敢、温暖而明媚，那些周而复始的日子里，总能听到梦想开花的声音。

# 小结
&emsp;&emsp;在这篇文章里我们讨论了MVC、MVP、MVVM各自架构变迁的前因后果，由此我们知道了软件设计中，一个典型的设计目标是让视图和模型分离，可我们同样发现，带着这个目标去设计软件的时候，我们基本鲜有更换视图的时候，虽然从理论上来讲，所有的业务逻辑都是在ViewModel中，视图和模型应该是可以进行更换的，可是你告诉我，有谁会为同一个软件制作不同的界面呢？难道我们还能期望通过一个静态工厂，来为不同的平台返回不同的视图，然后理论上只要适配正确的控制器就可以实现软件对不同平台的“自适应”，可是软件开发领域发展至今，最有可能提供完整跨平台方案的Web技术目前都无法满足这个需求，所以我们是否应该去怀疑这个设计的正确性呢？同样的，以Java的SSH三大框架为代表的“配置文件”流派，认为应该将数据库的相关信息写在配置文件里，这样可以满足我们随时切换到不同数据库产品上的需要，可是你告诉我，这样的应用场景多吗？所以，技术本身的设计并没有问题，我们需要思考的是，是否应该被框架和架构束缚，说到底我们是为了设计出更棒的软件产品，以此为目标，其实框架和架构更应该衍生为一种哲学意义上的思想，我们想让每一行代码都充满智慧的光芒，它骄傲却不孤独，因为总有人理解它、懂它。