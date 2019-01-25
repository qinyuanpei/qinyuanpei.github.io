---
title: 基于特性(Attribute)的实体属性验证方案设计
categories:
  - 编程语言
tags:
  - 'C#'
  - 校验
  - 特性
abbrlink: 3873710624
date: 2017-08-21 14:25:41
---
&emsp;&emsp;各位朋友，我是Payne，大家好，欢迎大家关注我的博客，我的博客地址是[https://qinyuanpei.github.io](https://qinyuanpei.github.io)。在这篇文章中，我想和大家探讨下数据校验的相关问题，为什么我会对这个问题感兴趣呢？这其实是来自最近工作中相关需求场景，而这篇文章其实是我在去年就准备要写的一篇文章，这篇文章一直存放在草稿箱里没有发布出来，所以结合这段时间项目上的思考，对当初的设计方案进行了改进，所有就有了大家现在看到的这篇文章，我始终认为思考是一个持久的过程，就像我们对这个世界的理解，是会随着阅历的变化而变化的。我们知道现实通常都会很残酷，不会给我们太充裕的时间去重构。可是思考会是人生永远的功课，当你忙碌到无暇顾影自怜的时候，不妨尝试慢下来抬头看看前方的路，或许原本就是我们选择了错误的方向呢，因为有时候作出一个正确的选择，实在是要比埋头苦干要重要得多啊。

&emsp;&emsp;好啦，既然我们提到了思考，那么我们来一起看一个实际项目中的业务场景，在某自动化项目中，用户会将大量数据以某种方式组织起来，然后藉由自动化工具将这些数据批量上传到一个系统中，该系统实际上是一个由各种表单组成的Web页面，并且这些Web表单中的控件都有着严格的验证规则，当数据无法满足这些验证规则时将无法上传，因此为了提高自动化工具上传的成功率，我们必须保证用户组织的这些数据是合法的，假设我们的用户是一个仅仅会使用Office三件套的普通人，他们可以想到的最好的方式是将这些数据录入到Excel中，而Excel中的数据有效性验证依附在单元格上，一旦验证规则发生变化，我们就不得不去维护这个Excel文件，这绝对不是一个软件工程师该做的事情好吗？我们当然是需要在提交数据前做验证啦，然而我看到Excel中100多列的字段时，我瞬间就不淡定了，这么多的字段难道我们要逐个写if-else吗？不，作为一个提倡少写if-else的程序员，我怎么可能会去做这种无聊的事情呢？下面隆重推出本文的主角——Attribute。

# 你的名字是？
&emsp;&emsp;如你所见，本文的主角是Attribute，那么当它出现在你面前的时候，你是否会像《你的名字。》里的泷和三叶一样，互相问候对方一句：你的名字是？因为我们实在不知道应该叫它特性还是属性。可事实上这篇文章的标题暴露了这个问题的答案，这里我们应该叫它特性。好了，按照数学理论中的观点，任何问题都可以通过引入一个中间层来解决，现在我们有了一个新的问题，Attribute和Property到底有什么区别？虽然这两者都可以翻译为"属性"，可实际上它们表达的是两个不同层面上的概念，一般我们倾向于将Attribute理解为编程语言文法上的概念，而将Property理解为面向对象编程里的概念。

## Attribute/特性
&emsp;&emsp;我们将Attribute称为特性，那么我们在什么地方会用到特性呢？两个个非常典型的例子是超文本标记语言(HTML)和可扩展标记语言(XML)。首先这两种标记语言都是结构化、描述性的标记语言。结构化表现在节点间可通过父子或者兄弟的关系来表示结构，描述性表现在每个节点都可以附加不同的描述来丰富节点。例如下面的XML文件中，我们使用了描述性的特性来提高元素间的辨识度，即特性为元素定义了更多的额外信息，而这些额外信息并不作为元素数据结构的一部分：

```
<bookstore>
<book category="COOKING">
  <title lang="en">Everyday Italian</title> 
  <author>Giada De Laurentiis</author> 
  <year>2005</year> 
  <price>30.00</price> 
</book>
<book category="CHILDREN">
  <title lang="en">Harry Potter</title> 
  <author>J K. Rowling</author> 
  <year>2005</year> 
  <price>29.99</price> 
</book>
</bookstore>
```
&emsp;&emsp;在这个例子中，bookstore节点由两个book节点组成，而每个book节点则由title、author、year和price四个节点组成，显然这些节点描述的是一种结构化的数据，而这些数据同时附加了相关描述性的信息，例如book节点有category信息，title节点有lang信息。在XML中最基本的一个内容单元我们称之为元素，即Element，而描述这些元素的最基本内容单元我们称之为特性。所以，这种在语言层面上进行描述而与实际抽象出的对象无关的概念就称为"特性”，人们认知和描述一个事物的方式会有所不同，所以在XML中会有这样一个历史遗留问题，我们应该使用Element还是Attribute，而产生这个问题的根源在于我们认识这个世界，是通过语言描述还是通过概念抽象。

&emsp;&emsp;如果我们了解GUI相关技术的演进过程，就会发现历史总是如此的相似。为什么微软会在XML的基础上扩展出XAML这种专门为WPF而设计的界面设计语言呢？因为历史告诉我们GUI中的大量特性都应该使用声明式的、描述式的语法来实现，从苹果的Cocoa、微软的XAML、Qt的QML、Android的XML等无一不证明了这个观点，而采用过程式的MFC、WinForm、Swing等，我们常常需要为它们编写大量的交互性的逻辑代码，今天我们会发现前端领域的声明式编程、MVVM、组件化等技术点，其实都是这种思想的无限延伸，我们可以使用jQuery去直接操作DOM，但面向过程的命令式代码一定不如声明式容易理解。虽然在面向对象编程的世界里，我们最终还是需要将这些描述性的语法结构，转化为面向对象里的类和属性，可这已然是一种进步了不是吗？

## Property/属性
&emsp;&emsp;我们认识这个世界的过程，恰恰折射出这两者截然不同的风格，从孩提时代理解的“天空是蓝色的”到学生时代认识到“大气是由氮气、氧气和稀有气体组成”，这种转变从本质上来看其实是因为我们认识世界的角度发生了变化。《西游降魔篇》里玄奘寻找五行山，第一次是风尘仆仆“看山是山”，第二次是由“镜花水月”启发“看山不是山”，第三次借“儿歌三百首”降伏孙悟空后“看山还是山”。面向对象编程(OOP)的一个重要思想是抽象，而抽象即是我们从描述性的语言中对事物属性进行构建的一个过程。例如现实生活中的汽车会有各种各样的数据信息：长度、宽度、高度、重量、速度等等，而与此同时汽车会有启动、刹车、减速、加速等等的行为，所以将事物的“数据”和“行为”提取出来进行抽象和模拟的过程，就是面向对象编程，我们在这个过程中可以注意到一点，所有的这一切都是针对对象而言的，所以Property是针对对象而言的。

&emsp;&emsp;这里提到的一个重要概念是抽象，什么是抽象呢？我认为它恰好和具体相对的一个概念。所谓具体，即相由心生，你看到什么就是什么，与此同时通过一组描述性的语言将其描述出来，我以为这就是具体。例如"火辣辣的太阳挂在天上"，这是具体到太阳颜色和温度的一种描述；所谓抽象，即返璞归真，我们看到的并非世间阴晴圆缺的月亮，而是这浩瀚宇宙中国一颗遥远的行星，此时此刻我们将行星具备的特点概括出来，推而光之，我以为这就是抽象，所以对我们而言，属性是事物抽象后普遍具有的一种特征，它首先要达到一种抽象的层次，其次它要能表现出事物的特性，我更喜欢将Property称之为属性，它和我们在面向对象编程中的概念是完全统一的。

# 方案设计及其实现

## 设计目标
* 免除配置开箱即用：无需任何配置文件，直接在实体上添加Attribute即可实现验证
* 非侵入式验证设计：验证与否对实体结构无任何副作用，可以随时添加验证或卸载验证
* 扩展灵活高度复用：可以自由派生自定义特性，通过泛型来支持不同实体类型的验证

## 设计思路
&emsp;&emsp;所有校验相关的Attribute都派生自ValidationAttribute这个父类，其核心方法是Validate()方法，该方法被声明为一个虚方法，因此所有的子类都必须对这个方法进行重写，它将返回一个叫做ValidationResult的结构，这是一个非常简单的数据结构，它仅仅包含Success和Message两个属性，前者表示当前校验是否成功，后者表示验证失败时的错误信息。显然，一个实体结构中将包含若干个不同的属性，所以在对一个实体结构进行验证的时候，会通过反射遍历每一个属性上的ValidationAttribute并调用其Validate()方法，所以最终返回给调用者的应该是由一组ValidationResult组成的集合，为此我们设计了ValidationResultCollection这个类，该类实现了ICollection接口，在此基础上我们增加了一个Success属性，当集合中所有ValidationResult的Success属性为true时，该属性为true反之为false。我们将数据校验的入口类EntityValidation设计成了一个静态类，它提供了一个泛型方法Validate<T>()方法，所以对整体设计而言，它的灵活性和扩展性主要体现在：(1)通过派生自定义特性来增加验证规则；(2)通过泛型方法来支持不同类型的校验。下面给出UML类图供大家参考，最近刚刚开始学习UML，有不足之处请大家轻喷哈：

![UML类图](https://ws1.sinaimg.cn/large/4c36074fly1fzix8rbidrj20ph0akdgz.jpg)

## 技术要点

&emsp;&emsp;首先，在.NET中特性的基类是Attribute，Attribute从表现形式上来讲类似Java中的注解，可以像标签一样添加在类、属性、字段和方法上，并在运行时期间产生各种不同的效果。例如[Serializable]标签表示一个实体类可以序列化，[NonSerializable]标签则可以指定某些属性或者字段在序列化的时候被忽略。而从本质上来讲，Attribute是一个类，通常我们会将派生类以Attribute结尾，而在具体使用的时候可以省略Attribute，所以[Serializable]标签其实是对应.NET中定义的SerializableAttribute这个类。在我们定义Attribute的时候，一个需要考虑的问题是Attribute的作用范围，在.NET中定义了AttributeUsageAttribute这个类，它可以是Class、Property、Field、Method等，所以Attribute本质上是在运行时期间为元素提供附加信息的一种机制，即Attribute可以添加元数据。我们知道元数据是(MetaData)实际上是程序集(Assembly)中的一部分，显然这一切都是在编译时期间定义好的，所以Attribute的一个重要特征是在运行时期间只读(Readonly)。Attribute必须依附在指定目标上，当当前目标与AttributeUsage定义不符时，将无法通过编译。Attribute的实例化依赖于目标实例的实例化，无法直接通过new完成实例化。通常我们需要配合反射来使用Attribute，在运行时期间做些有意义的事情，例如ORM中实体字段与数据库字段的绑定、Unity中配合AOP使用的ExceptionHnadler等等，都是非常典型的Attribute的应用。

&emsp;&emsp;了解了Attribute是什么东西，接下来我们要考虑的就是如何访问Attribute，在.NET中主要有两种方式来获取Attribute，即通过Attribute类提供的静态方法获取Attribute和通过Attribute依附的对象实例的元数据来获取Attribute。下面我们来看一段简单的代码实例：
```
public static T GetAttribute<T>(this PropertyInfo propertyInfo)
{
  var attrs = propertyInfo.GetCustomAttributes(typeof(T), false);
  if(attrs == null || attrs.Length<=0) return null;
  return atts[0] as T;
}
```
&emsp;&emsp;这段代码展示了如何通过反射访问附加在属性上的Attribute，事实上除了PropertyInfo以外，它还可以从任何支持附加Attribute的元素，例如MethodInfo、FieldInfo、ConstructorInfo等。Attribute类提供了类似的静态方法，第一个参数可以是这些元素中的任何一个，第二个参数和第三个参数和这里的示例代码一致，分别是返回的Attribute的类型，以及是否要搜索父类的Attribute，它的返回值类型为Attribute[]。在这个方案中，我们通过下面的方式来对实体属性进行验证：
```
public static ValidationResultCollection Validate<T>(T entity)
{
  var type = entity.GetType();
  var properties = type.GetProperties();
  var results = new ValidationResultsCollection();
  foreach(var property in properties)
  {
    var propertyValue = property.GetValue(entity,null);
    var validationAttributes = property.GetCustomAttributes(typeof(ValudationAttribute),fasle);
    if(propertyValue == null && (validationAttributes == null || valudationAttributs.Length <= 0)) continue
    
    //优先验证RequiredAttribute
    var requiredAttributes = property.GetCustomAttributes(typeof(RequiredAttribute),false);
    if(requiredAttributes.Length > 0)
    {
      var requiredResult = (requiredAttributes[0] as ValidationAttribute).Validate(propertyValue);
      results.Add(requiredResult);
      if(propertyValue == null) continue;
    }
    
    //其次验证ValidationAttribute
    foreach(var validationAttribute in validationAttributes)
    {
      if(propertyValue != null && !validationAttribute.GetType().Equals(typeof(RequiredAttribute)))
      {
        var validationResult = (validateAttribute as ValidationAttribute).Validate(propertyValue);
        results.Add(validationResult);
      }
    }
  }
  
  return results;
}
```
&emsp;&emsp;在这里我们注意到在对ValidationAttribute进行处理的时候，优先验证了RequiredAttribute，因为如果它验证失败意味着下面的验证都不需要了，所以当一个Property上附加了RequiredAttribute并且它的值为null的时候，我们将不会进行下面的验证，这是在设计过程中发现ValidationAttribute的优先级不同而做出的一个简单地调整。关于ValidationAttribute，我们提到这是所有自定义特性的基类，实际在使用中我们会有各种各样的派生类，我们这里以RegexAttribute为例来看看它具体怎么实现：
```
public class RegexAttribute : ValidationAttribute
{
  private string regexText;
  private string defaultMessage = "value is required to match a Regex rule {$regex};
  
  public RegexAttribute(string regexText,string message = null)
  {
    this.regexText = regexText;
    this.message = message == null ? defaultMessage : message;
  }
  
  public VelidationResult Validate(object value)
  {
  	var regex = new Regex(regexText);
  	var match = regex.match(value.ToString());
  	var success = match.Success;
  	if(!success)
  	{
      message = message.Replace("{$regex}",regexText);
      return new ValidationResult(){Success = success, Message = message};
  	}
  	
  	return new ValidationResult(){Success = success};
  }
}
```
&emsp;&emsp;好了，以上就是整个校验设计中关键的技术点啦，我认为整体上没有多少难点，因为这是我在项目上造的一个简单的轮子，相比ASP.NET  MVC 中的校验要简单很多，相信大家可以根据这些内容轻松地实现一个自己的版本，虽然不主张"重复造轮子"，可博主在很多时候都是通过"造轮子"来学习的啊，哈哈。

# 数据校验示例
&emsp;&emsp;下面我们来通过一个简单的示例来了解，如何在实际项目中使用这个验证方案：
```
public class Foo
{
  [Required]
  [Regex("(\d+){3}-(\d+){1}-(\d+){6}")]
  public string CardNumber {get; set;}
  
  [Required]
  [MaxLength(20,"AccountNumber is required within 20 characters")]
  public string AccountNumber {get; set;}
  
  [Values("FCY,DCP,ATM")]
  public string TransactionType{get；set;}
}
```
&emsp;&emsp;这里使用了三种验证规则，Required表示该字段不可以为空，Regex表示字段值要匹配指定的正则表达式，MaxLength表示字段长度不能超过指定长度，Values表示字段允许的取值范围，在实际使用中我们可以通过派生定义更多的验证规则，每一种验证规则都可以设置一个验证失败的信息，例如当AccountNumber的长度超过20时，将会返回指定的错误信息。我们可以通过下面的代码来验证Foo这个实体中的属性：
```
var foo = new Foo();
foo.CardNumber = "234-7-4567";
foo.AccountNumber = "12345678900";
foo.TransactionType = "DCP"

var results = EntityValidation.Validate<Foo>(foo);
if(!result.Success) results.ToList().Foreach(r => 
{
  Console.WriteLine(r.Message);
});
```

#本文小结
&emsp;&emsp;本文首先讲述了特性和属性两者在概念上的不同，即特性是编程语言文法上的概念，而属性是面向对象编程里的概念。接下来，我们针对.NET中的Attribute的表象和具象进行了讨论，Attribute从表象上看是和Java中的注解类似，可以像使用标签一样附加在类、方法、属性或者字段等元素上，而从具象上看Attribute提供了一种在运行时期间通过元数据访问附加信息的能力，Attribute是附加在类、方法、属性或者字段等元素上的一个类，需要继承自Attribute，它的实例化必须依赖这些附加对象的实例化，并且Attribute在运行时期间是Readonly的，Attribute通常需要配合反射来使用。在具备这些基础知识以后，我们开始和大家分享这个验证方案的设计思路及其技术要点，所谓抛砖引玉，本文的目的是想让大家借鉴这种思路，努力让业务代码更干净些，因为只有我们在乎这件事情，我们才会努力去将它做好。好了，今天这篇文章就是这样啦，谢谢大家关注！

