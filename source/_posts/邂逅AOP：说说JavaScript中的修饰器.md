---
title: 邂逅AOP：说说JavaScript中的修饰器
categories:
  - 编程语言
tags:
  - AOP
  - ES6
  - JS
abbrlink: 3668933172
date: 2018-04-15 21:20:03
---
&emsp;&emsp;Hi，各位朋友，大家好，欢迎大家关注我的博客，我是Payne，我的博客地址是[https://qinyuanpei.github.io](https://qinyuanpei.github.io)。这个月基本上没怎么更新博客和公众号，所以今天想写一篇科普性质的文章，主题是JavaScript中的修饰器。 为什么使用了"邂逅"这样一个词汇呢？因为当你知道无法再邂逅爱情的时候，你只能去期待邂逅爱情以外的事物；当你意识到爱情不过是生命里的小插曲，你只能去努力弥补生命的完整性。在过往的博客中，我曾向大家介绍过譬如Spring.NET、Unity、AspectCore等AOP相关的框架，亦曾向大家介绍过譬如Python中的装饰器、.NET中的Attribute、Java中的注解等等。再我看来，这些都是非常相近的概念，所以今天这篇文章我们又双叒叕要说AOP啦！什么？你说JavaScript里居然AOP！这简直比任何特性都要开心好吗？而这就要从本文的主角——JavaScript中的修饰器说起。

# 什么是修饰器？
&emsp;&emsp;JavaScript中的修饰器(**Decorator**)，是ES7的一个提案。目前的浏览器版本均不支持这一特性，所以主流的技术方案是采用Babel进行转译，事实上前端的工具链有相当多的工具都是这样，当然这些都是我们以后的话题啦！修饰器的出现，主要解决了下面这两个问题：

* 不同类间共享方法
* 在**编译时**期间对类及其方法进行修改

&emsp;&emsp;这里第一点看起来意义并不显著啊，因为JavaScript里有了模块化以后，在不同间共享方法只需要将其按模块导出即可。当然，在模块化这个问题上，JavaScript社区发扬了一贯的混乱传统，CommonJS、AMD、CMD等等不同的规范层出不穷，幸运的是ES6中使用了import和export实现了模块功能，这是目前事实上的模块化标准。这里需要关注的第二点，在**编译时**期间对类及其方法进行修改，这可以对类及其方法进行修改，这就非常有趣了呀！再注意到这里的修饰器即**Decorator**，我们立刻想Python中的装饰器，想到装饰器模式，想到代理模式，所以相信到这里大家不难理解我所说的，我们又双叒叕要说AOP啦！

&emsp;&emsp;那么说了这么多，JavaScript中的修饰器到底长什么样子呢？其实，它没有什么好神秘的，我们在Python和Java中都曾见过它，前者称为**装饰器**，后者称为**注解**，即在类或者方法的上面增加一个@符号，联想一下Spring中的Controller，我们大概知道它长下面这样：
```JavaScript
/* 修饰类 */
@bar
class foo {}

/* 修饰方法 */
@bar
foo(){}
```
&emsp;&emsp;OK，现在大家一定觉得，这TM简直就是抄袭了Python好吗？为了避免大家变成一个肤浅的人，我们一起来看看下面具体的例子：

## 修饰类
```
@setProp
class User {}

function setProp(target) {
    target.age = 30
}

console.log(User.age)
```
&emsp;&emsp;这个例子展示的是，我们如何通过修饰器函数setProp()来为User对象赋值，为什么叫做修饰器函数呢？因为这就是个函数啊，而且JavaScript和Python一样都是支持函数式编程的编程语言，所以大家看到这个大可不必感到吃惊，因为大道至简殊途同归。好了，注意到SetProp()方法有一个参数target，因为该方法修饰User类，所以它的参数就是User类，显然它为User类扩展了一个属性age，并给它赋值为30。相信有朋友一定会奇怪这个age是哪里定义的，我只能说JavaScript是个神奇的语言，一切都是对象，一切都是函数。现在，当我们执行到最后一句时，会输出30，这是因为修饰器对类进行修改。

&emsp;&emsp;现在我们尝试修改下这个方法，我们希望可以通过修饰器修改age属性的值，而不是让它成为一个固定数值30，这样就涉及到带参数的修饰器函数。修饰器函数本身会接收三个参数，第一个参数是被修饰的对象，因此为了增加一个新的参数，我们需要对原来的函数进行一层包装，你知道吗？此时我感到非常兴奋，因为这TM真的和Python一模一样啊。好了，遵从这个策略，我们修改原来的代码，并将其调整如下：
```JavaScript
@setProp(20)
class User {}

function setProp(value) {
    return function (target) {
        target.age = value
    }
}

console.log(User.age)
```
此种差别，大家可以非常明显地看出来，我们在使用修饰器函数setProp()的时候，现在允许传入一个参数20，此时的结果是非常地显而易见的，这段代码将如你所愿地输出20。

## 修饰方法
&emsp;&emsp;既然修饰器可以修饰类，那么可不可以修饰方法呢？答案自然是可以的。因为当修饰器修饰类的时候，修饰器函数的参数是一个对象，即target，而当修饰器修饰方法的时候，修饰器函数的参数是一个函数。可函数难道就不是对象吗？.NET里的委托最终不是同样会生成一个类吗？Python中不是有函数对象这一概念吗？那么，我们继续看一个例子 ：
```JavaScript
class User {
    @readonly
    getName() {
        return 'Hello World'
    }
}

// readonly修饰函数，对方法进行只读操作
function readonly(target, name, descriptor) {
    descriptor.writable = false
    return descriptor
}

let u = new User()
// 尝试修改函数，在控制台会报错
u.getName = () => {
    return 'I will override'
}
```
在这个例子中，我们通过修饰器函数readonly()对getName()方法进行修饰，使其变成一个readonly的方法。我们提到修饰器函数有三个参数，target指被修饰的对象，name指被修饰器对象的名称，descriptor指被修饰对象的defineProperty。因为设置descriptor的writable属性为false以后，这个函数就无法被覆盖重写，所以代码中尝试重写该方法时就会报错；同理，如果我们对descriptor的value属性进行修改，则可以对该函数进行重写。

## 总结
&emsp;&emsp;相信熟悉Python中的朋友，应该会知道在Python中内置了大量的装饰器，譬如@property可以让一个方法像属性一样被调用、@staticmethod可以让一个方法变成静态方法、@classmethod可以让一个方法变成类方法等。那么，作为Python的追随者，JavaSript中是否存在相类似的概念呢？答案还是肯定的啊！哈哈。具体大家可以参考这里：[ES6  Decorator](http://es6.ruanyifeng.com/#docs/decorator)

# AOP与修饰器
&emsp;&emsp;熟悉我写作风格的朋友，应该可以猜到我接下来要做什么了。的确，作为一个在某些方面有强迫症的人，我一直在不遗余力地向大家推广AOP，因为我相信AOP真的可以帮大家去做很多事情。比如最简单的记录日志，或许在前端项目中大家更习惯用console.log()来记录日志，甚至是使用alert()，毕竟这些东西不会在界面上展示出来，所以写一写这些东西好像无可厚非。可当你有了AOP以后，为什么还要做如此出力不讨好的事情呢？我写这篇文章的一个重要原因，正是我看到在前端同事的代码中，使用修饰器做了一个简单的AOP，这非常符合我的品味。具体怎么样去做呢？我们一起来看这段代码：
```JavaScript
class Bussiness {
    @log
    step1() {}
    
    @log
    step2() {}
}

function log(target,name,decriptor){
    var origin = descriptor.value;
    descriptor.value = function(){
      console.log('Calling function "${name}" with ', argumants);
      return origin.apply(null, arguments);
    };
    
    return descriptor;
}
```
&emsp;&emsp;我们刚刚提到通过修改descriptor的value属性可以达到重写方法的目的，那么这里就是利用这种方式对原来的方法进行了修改，在调用原来的方法前调用console.log()写了一行日志。的确，就是这样一行平淡无奇的代码，将我们从泥潭中解救出来。试想看到一段日志记录和业务流程掺杂的代码，谁会有心情去解读代码背后真实的含义，更不必说将来有一天要去删除这些日志有多么艰难啦。AOP的基本思想是在代码执行前后插入代码片段，因为根据JavaScript中的原型继承，我们可以非常容易地为Function类型扩展出before和after两个函数：
```JavaScript
Function.prototype.before = function(beforefunc){
  var self = this;
  var outerArgs = Array.prototype.slice.call(arguments,1);
  return function{
    var innerArgs = Array.prototype.slice.call(arguments);
    beforefunc.apply(this,innerArgs);
    self.apply(this,outerArgs)
  };
};

Function.prototype.after = function(afterfunc){
  var self = this;
  var outerArgs = Array.prototype.slice.call(arguments,1);
  return function{
    var innerArgs = Array.prototype.slice.call(arguments);
    self.apply(this,outerArgs)
    afterfunc.apply(this,innerArgs);
  };
};
```
&emsp;&emsp;想象一下，现在我们在重写descriptor的value属性的时候，可以同时指定它的before()方法和after()方法，所以最初的这段代码可以继续被改写为：
```JavaScript
var func = function(){
    console.log('Calling function "${name}" with ', argumants);
    return origin.apply(null, arguments);
};

func.before(function(){
  console.log('Start calling function ${name}');
})();

func.after(function(){
  console.log('End calling function ${name}');
})();
```
&emsp;&emsp;所以，所有让你觉得会增加风险的东西，都是源于你内心的恐惧，因为你不愿意去尝试改变，这是真正的复用，如果Ctrl + C和Ctrl + V可以被称为复用的话，我觉得每一个人都可以说自己是网红啦！这并不是一个笑话，还有什么比写一个@log更简单的吗？同样，我们可以使用修饰器去统计代码运行的时间，而不是在所有地方用两个Date()对象去相减。遵从简洁，从心开始：
```JavaScript
function time(){
  return function log(target,name,decriptor){
    var origin = descriptor.value;
    descriptor.value = function(){
      let beginTime = new Date();
      let result = origin.apply(null, arguments);
      let endTime = new Date();
      let time = endTime.getTime() - beginTime.getTime();
      console.log("Calling function '${name}' used '${time}' ms"); 
      return result;
    };
    
    return descriptor;
  };
}

@time
foo()
```
&emsp;&emsp;再比如，我们的业务中要求：用户在访问相关资源或者是执行相关操作时，需要确保用户的状态是登录着的，因此，我们不可避免地在代码中，使用if语句去判断用户是否登录，试想如果所有的业务代码都这样写，两个模块间就存在了直接耦合，当然我们可以说这是最简单的做法，因为它照顾了大部分人的思维和情绪，可你看Angular/Redux/TypeScript等项目中无一不遍布着修饰器的身影，当一种框架逐渐流行并成为一种趋势的时候，好像大家立刻就忘记了一件事情：原本我们都是非常排斥这些奇技淫巧的，可因为框架的流行你就默认接受了这种设定。那么，这个逻辑如何使用修饰器来编写会怎么样呢？
```JavaScript
class User {
    @checkLogin
    getUserInfo() {
        console.log('获取已登录用户的用户信息')
    }

    @checkLogin
    sendMsg() {
        console.log('发送消息')
    }
}

// 检查用户是否登录，如果没有登录，就跳转到登录页面
function checkLogin(target, name, descriptor) {
    let method = descriptor.value
    descriptor.value = function (...args) {
        //假想的校验方法，假设这里可以获取到用户名/密码
        if (validate(args)) {
            method.apply(this, args)
        } else {
            console.log('没有登录，即将跳转到登录页面...')
        }
    }
}
let u = new User()
u.getUserInfo()
u.sendMsg()
```
&emsp;&emsp;显然，现在我们可以避免模块间的直接耦合，无需在每个业务方法中重复去写if语句，更重要的是通过JavaScript中的模块化规范，我们可以把checkLogin这个方法，扩展到更多的业务类及其方法中去，而唯一的代价就是在方法上增加@checkLogin修饰，你说，有这样优雅的策略，你为什么就不愿意去使用呢？在ASP.NET中我们通过Authorize特性就可以为API和页面授权，现在看来这是不是有点异曲同工之妙呢？你现在还觉得这样麻烦吗？

# 本文小结
&emsp;&emsp;这篇文章从一个前端项目中的日志拦截器(InterceptLog)为引子，引出了ES7提案中的一个特性：修饰器。修饰器的出现，解决了两个问题：第一、不同类间共享方法；第二、在**编译时**期间对类及其方法进行修改。虽然目前修饰器不能直接在浏览器中使用，可是通过Babel这样的转译工具，我们已经可以在项目中提前感受这一特性，这里表扬下前端组的同事们。JavaScript中的修饰器同Python中的修饰器类似，可以修饰类及其方法。JavaScript中的修饰器不建议修饰函数，因为存在一个函数提升的问题，如果一定要修饰函数，按照高阶函数的概念直接包装函数即可。通过修饰器可以简化我们的代码，在本文中我们例举了日志记录、运行时间记录、登录检查三个AOP相关的实例，希望大家可以从这篇文章中有所收获。

&emsp;&emsp;最后，请允许博主爆一个料，因为要写一个简单的修饰器，需要安装若干Babel甚至是Webpack插件，我这篇文章中的代码，截止到写这篇文章时都没能在实际环境中运行，这不能怪我啊，因为前端的工具链实在是太长太多啦，这当然不能和直接内置装饰器的Python相比啊，这真的不是吐槽诶，我需要一个开箱即用的特性就这么难吗？人生苦短，我用Python！(逃

# 参考文章
* [读懂ES7中JavaScript修饰器 ](https://segmentfault.com/a/1190000011479378)
* [ES7 Decorator 入门解析](https://segmentfault.com/a/1190000010019412)
* [ES7 Decorator 装饰者模式](http://web.jobbole.com/84247/)
* [ECMAScript 6 入门](http://es6.ruanyifeng.com/#docs/decorator)
