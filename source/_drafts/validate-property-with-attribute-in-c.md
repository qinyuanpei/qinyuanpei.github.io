title: 在C#中使用特性(Attribute)来验证属性值的合法性
date: 2016-07-21 14:25:41
categories: [编程语言]
tags: [C#,校验,特性]
---
&emsp;&emsp;各位朋友，大家好，欢迎大家关注我的博客，我是Payne，我的博客地址是:[http://qinyuanpei.com](http://qinyuanpei.com)。今天想和大家探讨下数据验证这个问题，这个想法来自最近工作中的一个项目。项目背景是这样的，我定义了一个实体类(Model)，我在不清楚上层数据接口会给我返回什么样的数据类型的情况下，将这个实体类中的数据类型定义为字符型和布尔型两类。可是实际上这些字符型的属性都是有一定条件约束的，例如字符串不可以为空、字符串有长度限制、字符串表示一个电子邮件地址、字符串表示时间日期等等。如果按照通常的思路，我们可以在访问属性的Set访问器的时候进行验证，可是这里的实体类是我通过程序生成的，因为在实体类中有将近四十多个属性，难道让我一个一个的去写验证条件和初始值吗？不不不，作为一名有节操的程序员，我们应该从此时此刻就开始减少写if-else这样的代码，我们绝不会做这种效率低下的重复性工作，怎么办呢？这就是本文今天的主角：Attribute。

<!--more-->

# 关于Attribute和Property
&emsp;&emsp;首先，我想说说Attribute和Property这两个概念，虽然从翻译的角度来讲，它们都可以被翻译为“属性”，可是事实上它们想表达其实是两种不同层面的东西。Attribute是编程语言文法层面上的一个概念。

## 特性(Attribute)
&emsp;&emsp;例如我们熟悉的XML是一种结构化的、描述性的标记语言，它采用一种树形结构来组织文档内的内容，在XML中最基本的内容单元是一个元素，即Element，而为了给不同的元素增加不同的描述以示区别，我们就采用了Attribute这种概念，我们注意到这里的核心要素是描述，因此，我们将这种在语言层面上进行描述而与实际抽象出的对象无关的的概念称为“特性”，因此我们就不难理解，为什么在XML中会有这样一个历史遗留问题：使用Element还是使用使用Attribute？而产生这个问题的根源就在于我们认识这个世界，是通过语言描述还是概念抽象？

&emsp;&emsp;理解了这一点，你就会明白为什么WPF里的XAML，这种基于XML扩展而来的语法结构会成为WPF里的界面设计语言，因为历史告诉我们GUI中大量特性都应该使用描述性的、声明式的语言来实现，从苹果的Cocoa、微软的XAML、Qt的QML、Android的XML无一不证明了这个观点，而采用过程式的MFC、WinForm、Swing，我们常常需要为它们编写大量的交互性的逻辑代码，可是声明式语言的一个致命的问题是它一定是强语法、强反射的，因为在面向对象编程的世界里，我们最终还是需要将这些描述性的语法结构转化为面向对象的类和属性，因此我们对前者更为适合的定义是：特性。

## 属性(Property)
&emsp;&emsp;我们认识这个世界的过程，恰恰折射出这两者截然不同的风格，从孩提时代理解的“天空是蓝色的”到学生时代认识到“大气是由氮气、氧气和稀有气体组成”，这种转变从本质上来看其实是因为我们认识世界的角度发生了变化。《西游降魔篇》里玄奘寻找五行山，第一次是风尘仆仆“看山是山”，第二次是由“镜花水月”启发“看山不是山”，第三次借“儿歌三百首”降伏孙悟空后“看山还是山”。面向对象编程(OOP)的第一个思想是抽象，而抽象即是我们从描述性的语言中对事物属性进行构建的一个过程。例如现实生活中的汽车会有各种各样的数据信息：长度、宽度、高度、重量、速度等等，而与此同时汽车会有启动、刹车、减速、加速等等的行为，所以将事物的“数据”和“行为”提取出来进行抽象和模拟的过程，就是面向对象编程，我们在这个过程中可以注意到一点，所有的这一切都是针对对象而言的，所以Property是针对对象而言的，

&emsp;&emsp;WinForm时代我们习惯通过拖拽控件的方式快速实现界面，虽然这种方式让外人觉得.NET技术非常低端，可我们注意到这个过程中实际上是窗体设计器帮我们生成了一部分代码，我们还需要人为地编写大量交互性的代码，所以C#里就有了这样一个神奇的关键字：partial，而到了WPF时代，界面全部由设计师主导，这是因为所有的东西都可以转换为描述性的结构，因此我们对后者更为适合的定义是：特性。

# 使用特性验证属性合法性
&emsp;&emsp;好了，在了解了什么是特性、什么是属性以及二者的差异后，我们就可以切入今天正式的话题了。首先思考一件事情：我们为什么需要数据验证?我认为这是考虑到一个最基本的问题，即人这种高等灵长类动物是会犯错的，所以我们从Win32时期的全局变量检验机制到现代编程语言提供的异常处理机制，从本质上来讲都是为了防止人类出错，而我们程序员、培养防御式编程习惯、追求的程序鲁棒性和健壮性，同样是为了防止愚蠢的人类作死。当你打开上帝视角来看待这个问题的时候，你会觉得编程这件事情是个非常幸苦、非常酷的事情，所以在编程的时候你应该像上帝一样为愚蠢的人类指定规则，而非被愚蠢的人类提出的离奇需求钉死在十字架上，所以当需求不合理的时候，就应该用上帝一般的睿智，来告诉用户其逻辑的错误性。如果一味地迁就用户，最终导致的结果必然是，优雅的设计向肮脏的实现妥协，而这是恰恰是耶稣悲剧的开始。

## 设计目标
&emsp;&emsp;我们的设计目标是希望实现这样的效果，例如我们定义了一个类SomeClass，然后我们在这个类中定义了各种属性，我们希望通过添加Attribute来明确每个属性的验证要求，这样可以避免我们在具体业务中编写各种if-else，我的同事需要做各种界面数据的输入验证，而这些验证条件组合起来会导致不同的结果，我曾帮助他处理一个环节的验证逻辑，因为验证逻辑的复杂性让他编写的代码漏洞百出，所以这让我决心设计一种数据验证机制，而.NET平台下的Attribute完全能够满足我的要求，所以就有了今天这篇文章中的实践过程，具体来讲，是实现类似下面这样的效果：
```
public class SomeClass
{
    //日期验证
    [ValidateAttribute(ValidateType.IsDate)]
    public string SomeProperty1 { get; set; }

    //非空验证
    [ValidateAttribute(ValidateType.IsEmpty)]
    public string SomeProperty2 { get; set; }

    //最大长度验证
    [ValidateAttribute(ValidateType.MaxLength)]
    public string SomeProperty3 { get; set; }
          
    //More and more
}
```
在这里我们可以看到，我们通过使用一种类似标记的机制来配置每个属性的验证要求，这是一种灵活的实现方式，如果你曾经接触过ORM相关的内容，你一定会知道我们使用类似地方式来处理数据库字段和实体属性间的映射问题，在Java中这种类似的技术称为注解，而一切问题的根源在于数据库是关系型的，而编程是面向对象的，这两者间需要一种转换来实现同步，可我觉得最好的方式是面向对象的数据库，虽然目前技术尚不成熟，可是我们还是很高兴地看到各种NoSQL数据库开始流行，我就是不喜欢SQL语言，我觉得这种方式非常蛋疼，其实无论是.NET里的EF框架还是Java的SSH框架，它们重合的功能点无非是ORM、持久化和IoC(依赖注入)，虽然我没有做过Web项目更不喜欢微软的ASP.NET(因为我喜欢一个叫做Lucy的轻量级框架)，可我觉得在这里我们浪费了大量的时间。好了，现在我们来一步步的实现这个设计目标。

## 实现过程
&emsp;&emsp;首先，需要说明的是我们这里采用的这套机制称为自定义特性，自定义特性可以通过反射，因此我们实现验证的原理实际上依然是通过反射，简而言之，我们定义了一种标记规则，然后由程序通过反射获取标记信息，最终实现的目标是数据和逻辑分离。我们先来定义基本的数据结构：
```
public class Validation
{
   public static ValidationResult Validate<T>(T entity)
   {

   }
}
```
可以非常明显的看到，这是我们最终需要去实现和调用的一个静态方法，我们可以将任何使用了自定义特性的类的实例传入这个方法中，而它将返回一个ValidationResult类型的结果，从字面含义我们可以非常容易的理解，它表示的是我们对entity这个泛型类型实例的验证结果，那么具体它是如何定义的，我们一起来看：
```
/// <summary>
/// 验证结果定义
/// </summary>
class ValidationResult
{
    /// <summary>
    /// 是否通过验证 
    /// </summary>
    public bool Success { get; set; }

    /// <summary>
    /// 验证消息
    /// </summary>
    public string Message { get; set; }
}
```
为什么我们需要验证消息呢？难道返回一个布尔型的结果簿更直接吗？我的理解是，当通过对数据的验证时，我们是否返回验证信息是无关紧要的；而当数据的验证不通过时，我们有必要明确告诉调用者相关错误信息，就像底层程序抛出一个异常信息，并不是因为编写底层应用程序的人懒惰，而是在实际项目中上层调用者需要处理异常，同样地，如果底层程序抛出了异常而上层调用者不去处理异常，我想说这样的异常处理是完全没有意义的。好了，现在我们完成了数据结构的定义，我们最终会实现Validate这个方法。

&emsp;&emsp;OK，接下来我们简单定义下验证类型，它是一个枚举类型，即我们在SomeClass中看到的ValidateType，它提供了各种验证类型并且这些验证类型可以进行自由组合，我们这里仅仅提供常见的验证类型，更多的东西需要大家自己去发现，因为我发现博主写的非常清楚的话，除了让更多的伸手党变得懒惰和傲慢以外，对这个世界不会有任何良好的影响，所以我希望大家不是因为,这里为你给出了答案而想要读这篇文章，而是这篇文章能够带给你思考，这是我一直追求的写作目标，面向新手的小白教程会让别人觉得我非常肤浅.

&emsp;&emsp;我不是一个非常牛逼的开发者，因为很多原因我现在不再做Unity相关的开发了，所以你希望我在做过很多事情的基础上能够给你一个确定的答案，抱歉我做不到，原因是我最近因此被人谩骂和攻击，理由是我没有读懂对方问题的意图，而且我确实没有相关的经验。既然这个世界需要的是，在对方表达不清楚的时候就能快速理解其意图，并且还必须要为对方的无知而背锅的人，抱歉我宁愿选择沉默。好了，一个简单的枚举类型在我吐槽的期间已经写好了：

```
[Flags]
enum ValidateType
{
    //是否为空
    IsEmpty,
    //是否为邮件地址
    IsEmail,
    //最大字符长度
    MaxLength,
    //最小字符长度
    MinLength,
    //是否为数字
    IsNumber,
    //是否为时间
    IsTime,
    //是否为日期
    IsDate
}
```
注意到在枚举声明头部我们加入了Flags标记，该标记是为了确保我们能够在自定义的Attribute中使用这些枚举类型，为什么会提到自定义的Attribute呢？实际上.NET中所有的这种"标记"机制都是通过Attribute实现的，比如我们熟悉的Serializable关键字是表示一个类可以被序列化，所以我们要实现一组自定义的标记，就要继承自Attribute类，我们这里定义为ValidateAttribute类，为什么是ValidateAttribute类呢？这个类的名称能不能是是其它的名称呢？答案是不可以的，因为在我们写下SomeClass的时候，其实就已经确定了验证类和它的构造函数，我们一起来看具体代码上是如何实现的：
```
/// <summary>
/// 表明我们这里是对属性应用Attribute
/// </summary>
[AttributeUsage(AttributeTargets.Property)]
class ValidationAttribute : Attribute
{
	/// <summary>
	/// 当前验证类型
	/// </summary>
	public ValidationType ValidateType { get; private set; }

	/// <summary>
	/// 字符串最大长度
	/// </summary>
	public int MaxLength { get; set; }

	/// <summary>
	/// 字符串最小长度
	/// </summary>
	public int MinLength { get; set; }

	/// <summary>
	/// 构造函数
	/// </summary>
	/// <example>[Validate(ValidateType.IsDate)]</example>
	/// <param name="type">验证类型</param>
	public ValidationAttribute(ValidationType type)
	{
		this.ValidateType = type;
	}
}
```
在这里有三个地方需要注意，第一，自定义特性类全部继承自Attribute;第二，自定义特性类的构造函数和实体类中的“标记”一致;第三，使用AttributeUsage来限定特性的使用范围。这里想说明的是第二点，这种说法严格来讲是不严格的，因为对MaxLength这种类型的验证，除了传入验证类型以外，我们还可以设置它的MaxLength属性：
```
[ValidationAttribute(ValidationType.MaxLength,MaxLength = 8)]
public string Property2 { get; set; }
```
&emsp;&emsp;现在我们终于可以开始着手具体验证逻辑的编写啦，在这种情况下，我们的验证逻辑仅需要编写一次，而且和具体的数据类型无关。具体怎么做呢？直接看代码：
```
public static ValidationResult Validate<T>(T entity)
        {
            if (entity == null)
                throw new ArgumentNullException("请确认实体类型实例是否为空!");

            ValidationResult result = new ValidationResult() { Success = true, Message = "验证通过" };

            Type type = entity.GetType();
            PropertyInfo[] properties = type.GetProperties();
            foreach (PropertyInfo property in properties)
            {
                //获取每个属性对应的自定义特性
                object[] validations = property.GetCustomAttributes(typeof(ValidationAttribute),true);
                if (validations != null)
                {
                    object value = property.GetValue(entity, null);

                    //遍历全部自定义特性
                    foreach (ValidationAttribute validate in validations)
                    {
                        List<ValidationModel> models = new List<ValidationModel>();
                        switch (validate.ValidateType)
                        {
                            case ValidationType.IsTime:
                                models.Add(new ValidationModel()
                                {
                                    Type = ValidationType.IsTime,
                                    Function = () => { return true;},
                                    Message = string.Format("当前属性值{0}:{1}必须为时间格式",property.Name,value)
                                });
                                break;
                            case ValidationType.IsEmail:
                                models.Add(new ValidationModel()
                                {
                                    Type = ValidationType.IsTime,
                                    Function = () => { return true; },
                                    Message = string.Format("当前属性值{0}:{1}必须为Email格式", property.Name, value)
                                });
                                break;
                            case ValidationType.IsEmpty:
                                models.Add(new ValidationModel()
                                {
                                    Type = ValidationType.IsEmpty,
                                    Function = () => { return !string.IsNullOrEmpty(value.ToString()); },
                                    Message = string.Format("当前属性值{0}:{1}不能为空", property.Name, value)
                                });
                                break;
                            case ValidationType.IsNumber:
                                models.Add(new ValidationModel()
                                {
                                    Type = ValidationType.IsNumber,
                                    Function = () => { return true; },
                                    Message = string.Format("当前属性值{0}:{1}必须为数字", property.Name, value)
                                });
                                break;
                            case ValidationType.IsDate:
                                models.Add(new ValidationModel()
                                {
                                    Type = ValidationType.IsDate,
                                    Function = () => { return string.IsNullOrEmpty(value.ToString()); },
                                    Message = string.Format("当前属性值{0}:{1}必须为日期格式", property.Name, value)
                                });
                                break;
                            case ValidationType.MaxLength:
                                models.Add(new ValidationModel()
                                {
                                    Type = ValidationType.MaxLength,
                                    Function = () => { return value.ToString().Length<=validate.MaxLength; },
                                    Message = string.Format("当前属性值{0}:{1}其长度不得超过{2}", property.Name, value,validate.MaxLength)
                                });
                                break;
                            case ValidationType.MinLength:
                                models.Add(new ValidationModel()
                                {
                                    Type = ValidationType.MinLength,
                                    Function = () => { return value.ToString().Length >= validate.MinLength; },
                                    Message = string.Format("当前属性值{0}:{1}其长度不得超过{2}", property.Name, value, validate.MinLength)
                                });
                                break;
                        }

                        //处理全部的model
                        foreach (ValidationModel model in models)
                        {
                            result = Validate(model);
                        }
                    }
                }
            }

            return result;
        }
```

## 使用示例

# 本文小结

