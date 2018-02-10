title: 深入浅出理解Python装饰器
date: 2018-01-23 15:55:13
categories: [编程语言]
tags: [装饰器,Python,AOP]

---

各位朋友，大家好，我是Payne，欢迎大家关注我的博客，我的博客地址是[https://qinyuanpei.github.io](https://qinyuanpei.github.io)。今天我想和大家一起探讨的话题是Python中的装饰器。因为工作关系最近这段时间在频繁地使用Python，而我渐渐意识到这是一个非常有趣的话题。无论是在Python标准库还是第三方库中，我们越来越频繁地看到装饰器的身影，从某种程度上而言，Python中的装饰器是Python进阶者的一条必由之路，正确合理地使用装饰器可以让我们的开发如虎添翼。装饰器天然地和函数式编程、设计模式、AOP等概念产生联系，这更加让我对Python中的这个特性产生兴趣。所以，在这篇文章中我将带领大家一起来剖析Python中的装饰器，希望对大家学习Python有所帮助。

# 什么是装饰器
什么是装饰器？这是一个问题。在我的认知中，装饰器是一种语法糖，其本质就是函数。我们注意到Python具备函数式编程的特征，譬如lambda演算，map、filter和reduce等高阶函数。在函数式编程中，函数是一等公民，即“一切皆函数”。Python的函数式编程特性由早期版本通过渐进式开发而来，所以对“一切皆对象”的Python来说，函数像普通对象一样使用，这是自然而然的结果。为了验证这个想法，我们一起来看下面的示例。

## 函数对象

```Python
def square(n):
	return n * n

func = square
print func    #<function square at 0x01FF9FB0>
print func(5) #25
```
可以注意到，我们将一个函数直接赋值给一个变量，此时该变量表示的是一个函数对象的实例，什么叫做函数对象呢？就是说你可以将这个对象像函数一样使用，所以当它带括号和参数时，表示立即调用一个函数；当它不带括号和参数时，表示一个函数。在C#中我们有一个相近的概念被称为委托，而委托本质上是一个函数指针，即表示指向一个方法的引用，从这个角度来看，C#中的委托类似于这里的函数对象，因为Python是一个动态语言，所以我们可以直接将一个函数赋值给一个对象，而无需借助Delegate这样的特殊类型。
```Python
def sum_square(f,m,n):
    return f(m) + f(n)
    
print sum_square(square,3,4) #25
```
```Python
def square_wrapper():
    def square(n):
        return n * n
    return square
    
wrapper = square_wrapper()
print wrapper(5) #25
```
既然在Python中存在函数对象这样的类型，可以让我们像使用普通对象一样使用函数。那么，我们自然可以将函数推广到普通对象适用的所有场合，即考虑让函数作为参数和返回值，因为普通对象都都具备这样的能力。为什么要提到这两点呢？因为让函数作为参数和返回值，这不仅是函数式编程中高阶函数的基本概念，而且是闭包、匿名方法和lambda等特性的理论基础。从ES6中的箭头函数、Promise、React等可以看出，函数式编程在前端开发中越来越流行，而这些概念在原理上是相通的，这或许为我们学习函数式编程提供了一种新的思路。在这个示例中，**sum_square()**和**square_wrapper()**两个函数，分别为我们展示了使用函数作为参数和返回值的可行性。

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
对Python这门语言来说，这里的outer()函数和inner()函数分别被称为外函数和内函数，变量n的定义不在inner()函数内部，因此变量n称为inner()函数的环境变量。在Python中，一个函数及其环境变量就构成了闭包(**Closure**)。要理解闭包我认为我们可以把握这三点：第一，外函数返回了内函数的引用，即我们调用outer()函数时返回的是inner()函数的引用；第二，外函数将自己的局部变量绑定到内函数，其中变量b的目的是展示如何在内函数中修改环境变量；第三，调用内函数意味着发生出、入栈，不同的是每次调用都共享同一个闭包变量，请参考第二个示例。好了，现在讲完闭包以后，我们就可以开始说Python中的装饰器啦。

## 装饰器

装饰器是一种高级Python语法，装饰器可以对一个函数、方法或者类进行加工。所以，装饰器就像女孩子的梳妆盒，经过一番打扮后，可以让女孩子更漂亮。装饰器使用起来是非常简单的，其难点主要在如何去写一个装饰器。带着这个问题，我们来一起看看Python中的装饰器是如何工作的，以及为什么我们说装饰器的本质就是函数。早期的Python中并没有装饰器这一语法，最早出在Python 2.5版本中且仅仅支持函数的装饰，在Python 2.6及以后版本中装饰器被进一步用于类。

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
我们注意到装饰器可以使用def来定义，装饰器接收一个函数对象作为参数，并返回一个新的函数对象。装饰器通过名称绑定，让同一个变量名指向一个新返回的函数对象，这样就达到修改函数对象的目的。在使用装饰器时，我们通常会在新函数内部调用旧函数，以保留旧函数的功能，这正是“装饰”一词的由来。在定义好装饰器以后，就可以使用@语法了，其实际意义时，将被修饰对象作为参数传递给装饰器函数，然后将装饰器函数返回的函数对象赋给原来的被修饰对象。装饰器可以实现代码的可复用性，即我们可以用同一个装饰器修饰多个函数，以便实现相同的附加功能。在这个示例中，我们定义了一个decorator_print的装饰器函数，它负责对一个函数func进行修饰，在调用函数func以前执行print语句，进而可以帮助我们调试函数中的参数，通过@语法可以让我们使用一个名称去绑定一个函数对象。在这里，它的调用过程可以被分解为：
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
除此以外，Python标准库中提供了诸如classmethod、staticmethod、property等类装饰器，感兴趣的读者朋友可以自行前去研究，这里不再赘述。

# 装饰器与设计模式
装饰器可以对函数、方法和类进行修改，同时保证原有功能不受影响。这自然而然地让我想到面向切面编程(**AOP**)，其核心思想是，以非侵入的方式，在方法执行前后插入代码片段，以此来增强原有代码的功能。面向切面编程(**AOP**)通常通过代理模式(静态/动态)来实现，而与此同时，在Gof提出的“设计模式”中有一种设计模式被称为装饰器模式，这两种模式的相似性，让我意识到这会是一个有趣的话题，所以在接下来的部分，我们将讨论这两种设计模式与装饰器的内在联系。

## 代理模式

## 装饰器模式

##区别和联系

# 装饰器与面向切面
# 本文小结


