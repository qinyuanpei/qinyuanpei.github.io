---
abbrlink: 2829333122
categories:
- 编程语言
date: 2018-01-23 15:55:13
description: Java是典型的面向对象编程的语言，所以不存在任何游离于Class以外的函数，代理模式对类型的要求更为强烈些，因为我必须限制或者说要求Proxy实现里面的方法，而装饰器模式相对更为宽松些，遇到Python这样的动态类型语言，自然会显得事半功倍;在这个示例中，我们定义了一个decorator_print的装饰器函数，它负责对一个函数func进行修饰，在调用函数func以前执行print语句，进而可以帮助我们调试函数中的参数，通过@语法可以让我们使用一个名称去绑定一个函数对象;然后我们讨论了两种和装饰器有关的设计模式，即代理模式和装饰器模式，选择这两种模式来讨论，是因为我们在Java/C#和Python中看到了两种截然不同的实现AOP的思路，这部分需要花功夫去精心雕琢
tags:
- 装饰器
- Python
- AOP
title: 深入浅出理解Python装饰器
---

&emsp;&emsp;各位朋友，大家好，我是Payne，欢迎大家关注我的博客，我的博客地址是[https://qinyuanpei.github.io](https://qinyuanpei.github.io)。今天我想和大家一起探讨的话题是Python中的装饰器。因为工作关系最近这段时间在频繁地使用Python，而我渐渐意识到这是一个非常有趣的话题。无论是在Python标准库还是第三方库中，我们越来越频繁地看到装饰器的身影，从某种程度上而言，Python中的装饰器是Python进阶者的一条必由之路，正确合理地使用装饰器可以让我们的开发如虎添翼。装饰器天然地和函数式编程、设计模式、AOP等概念产生联系，这更加让我对Python中的这个特性产生兴趣。所以，在这篇文章中我将带领大家一起来剖析Python中的装饰器，希望对大家学习Python有所帮助。

# 什么是装饰器
&emsp;&emsp;什么是装饰器？这是一个问题。在我的认知中，装饰器是一种语法糖，其本质就是函数。我们注意到Python具备函数式编程的特征，譬如lambda演算，map、filter和reduce等高阶函数。在函数式编程中，函数是一等公民，即“一切皆函数”。Python的函数式编程特性由早期版本通过渐进式开发而来，所以对“一切皆对象”的Python来说，函数像普通对象一样使用，这是自然而然的结果。为了验证这个想法，我们一起来看下面的示例。

## 函数对象

```Python
def square(n):
    return n * n

func = square
print func    #<function square at 0x01FF9FB0>
print func(5) #25
```
可以注意到，我们将一个函数直接赋值给一个变量，此时该变量表示的是一个函数对象的实例，什么叫做函数对象呢？就是说你可以将这个对象像函数一样使用，所以当它带括号和参数时，表示立即调用一个函数；当它不带括号和参数时，表示一个函数。在C#中我们有一个相近的概念被称为委托，而委托本质上是一个函数指针，即表示指向一个方法的引用，从这个角度来看，C#中的委托类似于这里的函数对象，因为Python是一个动态语言，所以我们可以直接将一个函数赋值给一个对象，而无需借助Delegate这样的特殊类型。
* 使用函数作为参数
```Python
def sum_square(f,m,n):
    return f(m) + f(n)
    
print sum_square(square,3,4) #25
```
* 使用函数作为返回值
```Python
def square_wrapper():
    def square(n):
        return n * n
    return square
    
wrapper = square_wrapper()
print wrapper(5) #25
```
&emsp;&emsp;既然在Python中存在函数对象这样的类型，可以让我们像使用普通对象一样使用函数。那么，我们自然可以将函数推广到普通对象适用的所有场合，即考虑让函数作为参数和返回值，因为普通对象都都具备这样的能力。为什么要提到这两点呢？因为让函数作为参数和返回值，这不仅是函数式编程中高阶函数的基本概念，而且是闭包、匿名方法和lambda等特性的理论基础。从ES6中的箭头函数、Promise、React等可以看出，函数式编程在前端开发中越来越流行，而这些概念在原理上是相通的，这或许为我们学习函数式编程提供了一种新的思路。在这个示例中，**sum_square()**和**square_wrapper()**两个函数，分别为我们展示了使用函数作为参数和返回值的可行性。

```Python
def outer(m):
    n = 10
    def inner():
        return m + n
    return outer

func = outer(5)
print func() #15
```

```Python
#内函数修改外函数局部变量
def outer(a):
    b = [10]
    def inner():
        b[0] += 1
        return a + b[0]
    return inner

func = outer(5)
print func() #16
print func() #17
```
&emsp;&emsp;对Python这门语言来说，这里的outer()函数和inner()函数分别被称为外函数和内函数，变量n的定义不在inner()函数内部，因此变量n称为inner()函数的环境变量。在Python中，一个函数及其环境变量就构成了闭包(**Closure**)。要理解闭包我认为我们可以把握这三点：第一，外函数返回了内函数的引用，即我们调用outer()函数时返回的是inner()函数的引用；第二，外函数将自己的局部变量绑定到内函数，其中变量b的目的是展示如何在内函数中修改环境变量；第三，调用内函数意味着发生出、入栈，不同的是每次调用都共享同一个闭包变量，请参考第二个示例。好了，现在讲完闭包以后，我们就可以开始说Python中的装饰器啦。

## 装饰器

&emsp;&emsp;装饰器是一种高级Python语法，装饰器可以对一个函数、方法或者类进行加工。所以，装饰器就像女孩子的梳妆盒，经过一番打扮后，可以让女孩子更漂亮。装饰器使用起来是非常简单的，其难点主要在如何去写一个装饰器。带着这个问题，我们来一起看看Python中的装饰器是如何工作的，以及为什么我们说装饰器的本质就是函数。早期的Python中并没有装饰器这一语法，最早出在Python 2.5版本中且仅仅支持函数的装饰，在Python 2.6及以后版本中装饰器被进一步用于类。

```Python
def decorator_print(func):
    def wrapper(*arg):
        print arg
        return func(*arg)
    return wrapper

@decorator_print
def sum(array):
    return reduce(lambda x,y:x+y,array)

data = [1,3,5,7,9]
print sum(data)
```
&emsp;&emsp;我们注意到装饰器可以使用def来定义，装饰器接收一个函数对象作为参数，并返回一个新的函数对象。装饰器通过名称绑定，让同一个变量名指向一个新返回的函数对象，这样就达到修改函数对象的目的。在使用装饰器时，我们通常会在新函数内部调用旧函数，以保留旧函数的功能，这正是“装饰”一词的由来。在定义好装饰器以后，就可以使用@语法了，其实际意义时，将被修饰对象作为参数传递给装饰器函数，然后将装饰器函数返回的函数对象赋给原来的被修饰对象。装饰器可以实现代码的可复用性，即我们可以用同一个装饰器修饰多个函数，以便实现相同的附加功能。在这个示例中，我们定义了一个decorator_print的装饰器函数，它负责对一个函数func进行修饰，在调用函数func以前执行print语句，进而可以帮助我们调试函数中的参数，通过@语法可以让我们使用一个名称去绑定一个函数对象。在这里，它的调用过程可以被分解为：
```Python
sum = decorator_print(sum)
print sum()
```
接下来，我们再来写一个统计代码执行时长的装饰器decorator_watcher:
```Python
def decorator_watcher(func):
    def wrapper(*arg):
        t1 = time.time()
        result = func(*arg)
        t2 = time.time()
        print('time:',t2-t1)
        return result
    return wrapper
```
此时我们可以使用该装饰器来统计sum()函数执行时长：
```Python
@decorator_watcher
def sum(array):
    return reduce(lambda x,y:x+y,array)

data = [1,3,5,7,9]
print sum(data)
```
现在，这个装饰器打印出来的信息格式都是一样的，我们无法从终端中分辨它对应哪一个函数，因此考虑给它增加参数以提高辨识度：
```Python
def decorator_watcher(funcName=''):
    def decorator(func):
        def wrapper(*arg):
            t1 = time.time()
            result = func(*arg)
            t2 = time.time()
            print('%s time:' % funcName,t2-t1)
            return result
        return wrapper
    return decorator

@decorator_watcher('sum')
def sum(array):
    return reduce(lambda x,y:x+y,array)

data = [1,3,5,7,9]
print sum(data)
```
装饰器同样可以对类进行修饰，譬如我们希望某一个类支持单例模式，在C#中我们定义泛型类Singleton<T>。下面演示如何通过装饰器来实现这一功能：
```Python
instances = {}
def getInstance(aClass, *args):
    if aClass not in instances:
        instances[aClass] = aClass(*args)
    return instances[aClass]

def singleton(aClass):
    def onCall(*args):
        return getInstance(aClass,*args)
    return onCall

@singleton
class Person:
    def __init__(self,name,hours,rate):
        self.name = name
        self.hours = hours
        self.rate = rate
    def pay(self):
        return self.hours * self.rate
```
&emsp;&emsp;除此以外，Python标准库中提供了诸如classmethod、staticmethod、property等类装饰器，感兴趣的读者朋友可以自行前去研究，这里不再赘述。

# 装饰器与设计模式
&emsp;&emsp;装饰器可以对函数、方法和类进行修改，同时保证原有功能不受影响。这自然而然地让我想到面向切面编程(**AOP**)，其核心思想是，以非侵入的方式，在方法执行前后插入代码片段，以此来增强原有代码的功能。面向切面编程(**AOP**)通常通过代理模式(静态/动态)来实现，而与此同时，在Gof提出的“设计模式”中有一种设计模式被称为装饰器模式，这两种模式的相似性，让我意识到这会是一个有趣的话题，所以在接下来的部分，我们将讨论这两种设计模式与装饰器的内在联系。

## 代理模式

&emsp;&emsp;**代理模式**，属于23种设计模式中的结构型模式，其核心是为真实对象提供一种代理来控制对该对象的访问。在这里我们提到了**真实对象**，这就要首先引出代理模式中的三种角色，即**抽象对象**、**代理对象**和**真实对象**。其中：
* **抽象对象**：通过接口或抽象类声明真实角色实现的业务方法。
* **代理对象**：实现抽象角色，是真实角色的代理，通过真实角色的业务逻辑方法来实现抽象方法。
* **真实对象**：实现抽象角色，定义真实角色所要实现的业务逻辑，供代理角色调用。

&emsp;&emsp;下面是一个典型的代理模式UML图示：
![代理模式](https://ww1.sinaimg.cn/large/4c36074fly1fzixzb3188j20ev06a74f.jpg)

&emsp;&emsp;通过UML图我们可以发现，代理模式通过代理对象隐藏了真实对象，实现了调用者对真实对象的访问控制，即调用者无法直接接触到真实对象。“代理”这个词汇是一个非常生活化的词汇，因为我们可以非常容易地联系到生活种的中介这种角色，譬如租赁房屋时会存在房屋中介这种角色，租客(**调用者**)通过中介(**代理对象**)来联系房东(**真实对象**)，这种模式有什么好处呢？中介(**代理对象**)的存在隔离了租客(**调用者**)与房东(**真实对象**)，有效地保护了房东(**真实对象**)的个人隐私，使其免除了频繁被租客(调用者)骚扰的困惑，所以代理模式的强调的是**控制**。

&emsp;&emsp;按照代理机制上的不同来划分，代理模式可以分为**静态代理**和**动态代理**。前者是将**抽象对象**、**代理对象**和**真实对象**这三种角色在编译时就确定下来。对于C#这样的静态强类型语言而言，这意味着我们需要手动定义出这些类型；而后者则是指在运行时期间动态地创建代理类，譬如Unity、Ca'stle、Aspect Core以及ASP.NET中都可以看到这种技术的身影，即所谓的“动态编织”技术，通过反射机制和修改IL代码来达到动态代理的目的。通常意义上的代理模式，都是指静态代理，下面我们一起来看代码示例：

```CSharp
public class RealSubject : ISubject
{
    public void Request()
    {
        Console.WriteLine("我是RealSubject");
    }
}

public class ProxySubject : ISubject
{
    private ISubject subject;

    public ProxySubject(ISubject subject)
    {
        this.subject = subject;
    }

    public void Request()
    {
        this.subject.Request();
    }
}
```
&emsp;&emsp;通过示例代码，我们可以注意到，在代理对象ProxySubject中持有对ISubject接口的引用，因此它可以代理任何实现了ISubject接口的类，即真实对象。在Request()方法中我们调用了真实对象的Request()方法，实际上我们可以在代理对象中增加更多的细节，譬如在Request()方法执行前后插入指定的代码，这就是面向切面编程(**AOP**)的最基本的原理。在实际应用中，主要以动态代理最为常见，Java中提供了InvocationHandler接口来实现这一接口，在.NET中则有远程调用(**Remoting Proxies**)、**ContextBoundObject**和**IL织入**等多种实现方式。从整体而言，生成代理类和子类化是常见的两种思路。相比静态代理，动态代理机制相对复杂，不适合在这里展开来说，感兴趣的朋友可以去做进一步的了解。

## 装饰器模式
&emsp;&emsp;**装饰器模式**，同样是一种结构型模式，其核心是为了解决由继承引发的“类型爆炸”问题。我们知道，通过继承增加子类就可以扩展父类的功能，可随着业务复杂性的不断增加，子类变得越来越多，这就会引发“类型爆炸”问题。**装饰器模式**就是一种用以代替继承的技术，即无需通过继承增加子类就可以扩展父类的功能，同时不改变原有的结构。在《西游记》中孙悟空和二郎神斗法，孙悟空变成了一座庙宇，这是对原有功能的一种扩展，因为孙悟空的本质依然是只猴子，不同的是此刻具备了庙宇的功能。这就是装饰器模式。下面，我们一起来看一个生活中的例子。

![咖啡种类](https://ww1.sinaimg.cn/large/4c36074fly1fzixbtfyr6j20c80gr0ul.jpg)

&emsp;&emsp;喜欢喝咖啡的朋友，看到这张图应该感到特别亲切，因为咖啡的种类的确是太多啦。在开始喝咖啡以前，我完全不知道咖啡会有这么多的种类，而且咖啡作为一种略显小资的饮品，其名称更是令人目不暇接，一如街头出现的各种女孩子喜欢的茶品饮料，有些当真是教人叫不出来名字。这是一个典型的“类型爆炸”问题，人们在吃喝上坚持不懈的追求，让咖啡的种类越来越多，这个时候继承反而变成了一种沉重的包袱，那么该如何解决这个问题呢？装饰器模式应运而生，首先来看装饰器模式的UML图示：
![装饰器模式](https://ww1.sinaimg.cn/large/4c36074fly1fzix9bb7jvj20it089wf4.jpg)

&emsp;&emsp;从这个图示中可以看出，装饰器和被装饰者都派生自同一个抽象类Component，而不同的Decorator具备不同的功能，DecoratorA可以为被装饰者扩展状态，DecoratorB可以为被装饰者扩展行为，可无论如何，被装饰者的本质不会发生变化，它还是一个Component。回到咖啡这个问题，我们发现这些咖啡都是由浓缩咖啡、水、牛奶、奶泡等组成，所以我们可以从一杯浓缩咖啡开始，对咖啡反复进行调配，直至搭配出我们喜欢的咖啡，这个过程就是反复使用装饰器进行装饰的过程，因此我们可以写出下面的代码：

```CSharp
//饮料抽象类
abstract class Drink
{
    public abstract Drink Mix(Drink drink);
}

//牛奶装饰器
class MilkDecorator : Drink
{
    private Drink milk;
    MilkDecorator(Drink milk)
    {
        this.milk = milk;
    }

    public override Drink Mix(Drink coffee)
    {
        return coffee.Mix(this.milk);
    }
}

//热水装饰器
class WaterDecorator : Drink
{
    private Drink water;
    WaterDecorator(Drink water)
    {
        this.water = water;
    }

    public override Drink Mix(Drink coffee)
    {
        return coffee.Mix(this.water);
    }
}

//一杯浓缩咖啡
var coffee = new Coffee()
//咖啡里混入水
coffee = new WaterDecorator(new Water()).Mix(coffee)
//咖啡里混入牛奶
coffee = new MilkDecorator(new Milk()).Mix(coffee)
```
&emsp;&emsp;在这里我们演示了如何通过装饰器模式来调配出一杯咖啡，这里我没有写出具体的Coffee类。在实际场景中，我们还会遇到在咖啡里加糖或者配料来收费的问题，此时装饰器模式就可以帮助我们解决问题，不同的装饰器会对咖啡的价格进行修改，因此在应用完所有装饰器以后，我们就可以计算出最终这杯咖啡的价格。由此我们可以看出，装饰器模式强调的是**扩展**。什么是扩展呢，就是在不影响原来功能的基础上增加新的功能。

## 区别和联系
&emsp;&emsp;代理模式和装饰器模式都是结构型的设计模式，两者在实现上是非常相似的。不同的地方在于，代理模式下调用者无法直接接触到真实对象，因此代理模式强调的是**控制**，即向调用者隐藏真实对象的信息，控制真实对象可以访问的范围；装饰器模式下，扩展功能的职责由子类转向装饰器，且装饰器与被装饰者通常是**"同源"**的，即派生自同一个父类或者是实现了同一个接口，装饰器关注的是增加被装饰者的功能，即**扩展**。两者的联系在于都需要持有一个**"同源"**对象的引用，譬如代理对象与真实对象同源，装饰器与被装饰者同源。从调用的层面上来讲，调用者无法接触到真实对象，它调用的始终是代理对象，对真实对象的内部细节一无所知，这是代理模式；调用者可以接触到装饰器和被装饰者，并且知道装饰器会对被装饰者产生什么样的影响，通常是从一个默认的对象开始"加工"，这是装饰器模式。

# 装饰器与面向切面
&emsp;&emsp;这篇文章写到现在，我发觉我挖了一个非常大的坑，因为这篇文章中涉及到的概念实在太多，务求每一个概念都能讲得清楚透彻，有时候就像莫名立起来的flag，时间一长连我自己都觉得荒唐。有时候感觉内容越来越难写，道理越来越难同别人讲清楚。写作从一开始坚持到现在，就如同某些固执的喜欢一样，大概连我都不记得最初是为了什么吧。好了，现在来说说装饰器与面向切面。我接触Python装饰器的时候，自然而然想到的是.NET中的Attribute。我在越来越多的项目中使用Attribute，譬如ORM中字段与实体的映射规则、数据模型(**Data Model**)中字段的校验规则、RESTful API/Web API设计中的路由配置等，因为我非常不喜欢Java中近乎滥用的配置文件。

&emsp;&emsp;C#中的Attribute实际上是一种依附在目标(**AttributeTargets**)上的特殊类型，它无法通过new关键字进行实例化，它的实例化必须依赖所依附的目标，通过分析IL代码我们可以知道，Attribute并非是一种修饰符而是一种特殊的类，其方括号必须紧紧挨着所依赖的目标，构造函数以及对属性赋值均在圆括号内完成。相比较而言，Python中的装饰器就显得更为顺理成章些，因为Python中的装饰器本质就是函数，装饰器等价于用装饰器函数去修饰一个函数。函数修饰函数，听起来感觉不可思议，可当你理解了函数和普通对象一样，就不会觉得这个想法不可思议。有时回想起人生会觉得充满玄学的意味，大概是因为我们还没有学会把自己看得普通。

&emsp;&emsp;通过这篇文章的梳理，我们会发现一个奇妙的现象，Java的Spring框架采用了动态代理了实现AOP，而Python的装饰器简直就是天生的AOP利器，从原理上来讲，这两门语言会选择什么样的方案都说得通。Java是典型的面向对象编程的语言，所以不存在任何游离于Class以外的函数，代理模式对类型的要求更为强烈些，因为我必须限制或者说要求Proxy实现里面的方法，而装饰器模式相对更为宽松些，遇到Python这样的动态类型语言，自然会显得事半功倍。这说明一个道理，通往山顶的道路会有无数条，从中找出最为优雅的一条，是数学家毕生的心愿。AOP是一种思想，和语言无关，我常常听到Java的同学们宣称AOP和IOC在Java社区里如何流行，其实这些东西本来就是可以使用不同的方式去实现的，有些重要的东西，需要你剥离开偏见去认知。

&emsp;&emsp;关于C#中的Attribute和AOP如何去集成，在Unity和Aspect Core这两个框架中都有涉及，主流的AOP都在努力向这个方向去靠拢，Java中的注解同样不会跳出这个设定，因为编程技术到了今天，语言间的差别微乎其微，我至今依然可以听到，换一种语言就能让问题得到解决的声音，我想说，软件工程是没有银弹的，人类社会的复杂性会永远持续地存在下去，你看微信这样一个社交软件，其对朋友圈权限的粒度之细足以令人叹服。有朋友尝试在C#中借鉴Python的装饰器，并在一组文章中记录了其中的心得，这里分享给大家，希望对这个问题有兴趣的朋友，可以继续努力研究下去，AOP采用哪种方式实现重要吗？有人用它做权限控制，有人用它做日志记录......允许差异的存在，或许才是我们真正需要从这个世界里汲取的力量。

* [轻量级AOP框架-移植python的装饰器(Decorator)到C#(思考篇) ](https://www.cnblogs.com/leven/archive/2009/12/28/decorator-csharp-1.html)

* [轻量级AOP框架-移植python的装饰器(Decorator)到C#(编码篇) ](http://www.cnblogs.com/leven/archive/2009/12/28/decorator-csharp-2.html)


# 本文小结
&emsp;&emsp;本文是博主学习Python时临时起意的想法，因为曾经有在项目中使用过AOP的经验，所以在学习Python中的装饰器的时候，自然而然地对这个特性产生了兴趣。有人说，装饰器是Python进阶的重要知识点。在今天这篇文章中，我们首先从Python中的函数引出"函数对象"这一概念，在阐述这个概念的过程中，穿插了函数式编程、高阶函数、lambda等等的概念，"函数是一等公民"，这句话在Python中出现时就是指装饰器，因为装饰器的本质就是函数。然后我们讨论了两种和装饰器有关的设计模式，即代理模式和装饰器模式，选择这两种模式来讨论，是因为我们在Java/C#和Python中看到了两种截然不同的实现AOP的思路，这部分需要花功夫去精心雕琢。博主有时候觉得力不从心，所以写作中有不周到的地方希望大家谅解，同时积极欢迎大家留言，这篇文章就先写到这里吧，谢谢大家！