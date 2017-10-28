title: .NET平台下Xml读写方式归纳与总结
date: 2016-07-15 15:04:45
categories: [编程语言]
tags: [Xml,.NET,C#]
---
&emsp;&emsp;最近因为项目上的原因，接触到了大量的Xml读写的工作。虽然在平时的工作学习中，或多或少地对Xml有过接触和了解，可是在这次工作中暴露出的种种问题，开始让我反思自己在学习上的不足。或许有时候我们觉得编程应该是一件充满创作力的工作，可是事实上你很快就会意识到解决问题比项目架构更为紧急迫切。我从来没有想要试图告诉大家，项目架构在实际工作中并不重要，仅仅是因为和我的Team Leader一起调试我的程序时，我第一次感觉到一种无力感和迷茫感，我们带着项目架构的思想来开发项目，可你却在不知不觉中身陷重围，或许最简单的就是最有效的解决方案吧，在今天这篇文章里，我想和大家说说.NET平台下常见的Xml读写方式及其各自的优劣。

<!--more-->

# .NET平台下Xml相关的技术
&emsp;&emsp;.NET平台下与Xml相关的类有哪些呢？我们通常比较熟悉的是为System.Xml命名空间下的XmlDocument，以及为Linq量身打造的位于Sytem.Xml.Linq命名空间下的XDocument，而从我个人的角度来讲，我更喜欢XDocument，因为它可以和我非常喜欢的Linq一起使用。而从客观上来讲，XmlDocument和XDocument都可以处理Xml的读写，并且它们会将所有的Xml节点加载到内存中，所以当Xml文件体积较小或者处理相对复杂的时候，这两者都是相对不错的选择，它们唯一的区别可能是在.NET版本和兼容性上，XmlDocument使用传统的DOM对Xml进行解析处理，而XDocument使用全新的Linq来对Xml进行解析处理。事实上目前使用XmlDocument的开发者通常都是为了照顾低版本.NET的用户，如果你从现在开始了解这些内容，我建议你直接使用XDocument，因为Linq可以让程序员做些他们真正喜欢的东西。为了让大家了解这两者的不同，我们这里准备了下面这张表：

|                 | XmlDcoument               | XDcoument                 |
|:--------------  |:-------------------------:|:-------------------------:|
| 核心技术        | DOM                       | Linq                      | 
| 命名空间        | System.Xml                | System.Xml.Linq           |
| Linq to Xml     | 不支持                    | 支持Linq扩展语法          |
| 流、文件、字符串| 支持                      | 支持                      |
| NameSpace       | 支持写入                  | 支持元素级写入            |
| XPath           | 支持                      | 支持(System.Xml.XPath)    |
| 注释            | 支持                      | 支持可扩展的批注集合      |


&emsp;&emsp;从这张表可以看出，XmlDocument和XDocument在处理Xml的能力上对比明显，显然XDocument能够帮助我们完成更多的工作，这是为什么我向大家推荐XDocument的原因，我个人更喜欢XDocument中通过XElement来组织Xml节点的这种设计，这种设计能让我们在筛选Xml节点的时候借助Linq快速地完成工作。我最近工作中遇到解析上万行的Xml文档，而在这份文档中大部分信息对人类来讲都是没有意义的，所以在接到这个任务以后我没有像同事建议的那样去遍历，为什么呢？因为我觉地这样很傻呀，当用户向开发者提出不合理或者是“弱智”的需求的时候，我认为开发者绝对不能选择忍气吞声，虽然开发者以实现需求和解决问题为荣，可这并不代表开发者有责任帮助用户来完成本该由用户来完成的工作，在这个项目中我采用了一种标记文档的思路，这样就为Xml文档中的部分节点创建了索引，因为我仅仅需要更新这部分节点的内容，我很庆幸我在这里使用了Linq，作为程序员我想说在我使用Linq以后我就不再想要使用SQL了。


&emsp;&emsp;好了，具体到.NET中Xml相关技术，我这里想说是XmlDocument、XDocument、XElement以及XmlReader和XmlWriter，关于Xml中序列化和反序列化的相关内容，我们不打算在这里展开论述。在日常开发中，当我们熟悉XmlDocument、XDocument、XElement以后，理论上我们可以完成大部分Xml相关的开发任务了。可是最近的项目中存在的问题，让我意识到XmlReader和XmlWriter在某些应用场景下占有一席之地，所以在这里我想将其和XmlDocument、XDocument、XElement放到一起来讲解，希望对大家了解.NET平台下Xml能够有所帮助。为了统一整篇文章中代码实例，我们这里统一采用下面的Xml文档来演示不同的API之间如何进行读写：

```
<?xml version="1.0" encoding="utf-8"?>
<Root>
 <Child1 Name="Child1">
   <ChildNode1 Name="ChildNode1">Node1</ChildNode1>
 </Child1>
 <Child2 Name="Child2">2</Child2>
 <Child3 Name="Child3">3</Child3>
</Root>
```

## XmlDocument
&emsp;&emsp;XmlDocument是我们在.NET中接触到的最早的处理Xml的一个类，这个类曾经因为在Unity3D中执行效率的原因，而被官方推荐使用一个社区维护的Xml处理库来代替。熟悉Xml解析的朋友应该知道XmlDocument是采用DOM来解析整个文档的，所以在处理执行效率上XmlDocument是无法和全新的XDocument相提并论的，这同样是我向大家推荐使用后者的原因之一。好了，技术上细节我们直接通过代码来体现吧，所以一起来看下面的代码：

###加载Xml文档
&emsp;&emsp;使用XmlDocument加载一个Xml文档，主要通过XmlDocument类的Load方法和LoadXml这两个方法来实现，前者可以从文件路径、IO流加载，而后者则可以通过XML文本加载，需要注意的是，在使用XmlDocument的时候需要首先实例化，在这一点上XDocument和XElement则提供了静态方法，在讲解到相应部分的时候我们会提到这个问题。因此，在假定我们将示例中的Xml文档存储到应用程序根目录下(我们这里将其命名为childs.xml)，此时代码可以这样编写：

```
//示例化XmlDocument
XmlDocument document = new XmlDocument();
//通过路径加载
document.Load("childs.xml");
//通过Stream加载
using(FileStream stream = new FileStream("childs.xml", FileMode.Open)) { document.Load(stream);}
//通过XmlReader加载
using(XmlReader reader = XmlReader.Create("childs.xml")){ document.Load(reader);}        
```

###读写Xml文档
&emsp;&emsp;在加载完Xml文档后，我们现在就可以开始着手进行Xml文档读写的相关工作了。需要说明的是，在Xml文档中有且只有一个根节点，我们对文档的读写都要从根节点开始。你可以将Xml文档想象为一棵树，这样文档中的每个节点元素就是这棵树上的分支树叉，所以从根节点开始查找整棵树上的元素，这是显而易见而且顺理成章的。我们在学习算法的时候，常常对二叉树这种抽象的东西敬之畏之，因为我们都觉得在平时工作中用不到这些东西，可是万万没想到的是我们在这里遇到了这种相近的“概念”，这其实就是文档对象模型(Document Object Model，简称[DOM]())啦，简单来说在XML文档中所有的数据都可以以元素(Element)和属性(Attribute)两种形式存储在一个树形结构中，我们一起来看如何读取Xml文档：

```
//获取根节点
XmlElement root = document.DocumentElement;
//获取Child1节点
XmlNode child1 = root.SelectSingleNode("Child1");
//获取Child1节点的Name属性
XmlAttribute name1 = child1.Attributes["Name"];
//获取根节点下所有子节点
XmlNodeList nodes = root.ChildNodes;
//设置Child1节点数值
child1.InnerText = "XmlDocument";
//获取Child1节点的Name属性
name1.InnerText = "XDocument";
```
###创建Xml文档
&emsp;&emsp;通过修改Xml文档，我们能够达到保存信息的目的。通常来讲，我们使用XmlDocument类的Save方法就可以了，可是有时候我们不得不从头开始创建一个Xml文件，微软从Office2007以后使用的.docx、.xlsx和.pptx其实都是由各种Xml文件组成的一种开放格式，官方提供了OpneXML SDK来帮助我们创建Word、Excel和PPT文档，可是即使在这种情况下，通过代码来创建Office文档依然是件繁琐而枯燥的，因为人们将80%的精力都浪费在文档样式上面，所以从我个人角度来讲，我更喜欢Markdown，它在简化文档结构的同时，提供了一种和样式无关的内容格式，所以如果主流办公软件考虑支持对Markdown的支持，我相信喜欢Markdown的人将会和同事们更好的协作。在这里创建一个Xml文档是相对容易的：

```
//创建Xml文档
XmlDocument document = new XmlDocument();
//创建根节点
XmlElement root = document.CreateElement("Root");
//创建ChildNode1节点
XmlElement childNode1 = document.CreateElement("ChildNode1");
childNode1.SetAttribute("Name", "ChildNode1");
childNode1.InnerText = "Node1";
//创建Child1节点
XmlElement child1 = document.CreateElement("Child1");
child1.SetAttribute("Name", "Child1");
child1.AppendChild(childNode1);
//创建Child2节点
XmlElement child2 = document.CreateElement("Child2");
child2.SetAttribute("Name", "Child2");
child2.InnerText = "2";
//创建Child3节点
XmlElement child3 = document.CreateElement("Child3");
child3.SetAttribute("Name", "Child3");
child3.InnerText = "3";
//添加节点到根节点中
root.AppendChild(child1);
root.AppendChild(child2);
root.AppendChild(child3);
//添加根节点到文档中
document.AppendChild(root);
//保存文档
document.Save("output.xml");
```
&emsp;&emsp;我可以说，通过这样的方式来创建Xml文档非常难受吗？因为我们可以注意到，在这个过程中，节点的层级关系完全由开发者来维护，所以这中方式无论是对写代码的人还是读代码的人来讲都是一种灾难，所幸的是我们有XDocument，这是一种清晰、优雅的文档描述方法，而且自带Linq特性加持，所以我相信你一定会爱上它的，下面我们就来一起看看XDocument在使用上和XmlDcocument有什么不同吧！

## XDocument
&emsp;&emsp;XDocument和XmlDocument都可以处理Xml文档，所不同的是XDocument是.NET3.5版本以后为Linq to Xml提供的轻量级Document对象，因此Linq可以说是XDocument与生俱来的一种良好特性，Linq让我们从繁重的if-else语句中解放出来，Linq让数据库和对象集合都可以使用莱姆达表达式进行查询，所以Linq在处理Xml文档的时候会感觉更加得心应手，对我个人而言，我更喜欢Linq提供的各种扩展方法，因为它是完全面向对象的一种设计，而类似SQL的Linq用法因为我不喜欢SQL的缘故所以比较抵制，总体来讲，XDocument更加轻量、更加适合查询。

###加载Xml文档
&emsp;&emsp;加载Xml文档对XDocument对象来说是非常友好的，因为它提供了相对简洁的静态方法入口，而在API设计上遵循某种一致性，例如XmlDocument对应XDocument、XmlElement对应XElement等等，因此从XmlDocument更换到XDocument是非常容易适应和迁移的，如果你想从XmlDocument迁移到XDocument，本文将是一个非常不错的参考，我们一起来看下面的示例：

```
//从文件路径加载
XDocument document = XDocument.Load("childs.xml");
//从Stream加载
using(FileStream stream = new FileStream("childs.xml",FileMode.Open))
{ 
  document = XDocument.Load(stream);
}
//从XmlReader加载
using(XmlReader reader = XmlReader.Create("childs.xml"))
{ 
  document = XDocument.Load(reader); 
}
//从Xml文本加载
using(StreamReader reader = new StreamReader("childs.xml")) 
{ 
  document = XDocument.Parse(reader.ReadToEnd());
}
```
###读取Xml文档
&emsp;&emsp;我们可以注意到在加载Xml文档的时候，XDocument和XmlDocument是非常相近的，所以希望了解XDocument的朋友完全可以无视学习新知识的成本，这个世界上每天都会有新的知识产生，我们可以以没有时间为理由拒绝学习，我们同样可以像五柳先生一样“不求甚解”，就像WPF这类在国内相对冷僻的技术，你可以选择性的了解而不是以此来作为学习的目标，你了解什么呢？我的答案是了解它的MVVM设计、声明式编程和过程式编程的区别以及命令与委托的内在联系等等，因为这些东西都是针对特有的技术，当你了解到这些你就不会为Angular这类前端而纠结，因为这些无非是将一种思想引入到前端开发中，这符合我一贯的学习风格，即学习架构而非学习框架。同样的，读取Xml在这里是非常友好的：

```
//获取根节点
XElement root = document.Root;
//查询child1节点
XElement child1 = root.Element("Child1");
//查询Child1节点下的ChildNode1节点
XElement childNode1 = child1.Element("ChildNode1");
//获取ChildNode1节点的值
string childNode1Value = childNode1.Value;
//查询Child2节点
XElement child2 = root.Element("Child2");
//获取Child2节点的Name属性
XAttribute child2Name = child2.Attribute("Name");
//获取全部的Child1节点,一级查询
IEnumerable<XElement> childs = root.Elements("Child1");
//获取全部的Child2节点,多级查询
IEnumerable<XElement> nodes = root.Descendants("Child2");
//筛选出nodes中Name属性为Child2的第一个节点
XElement first = nodes.Where
	(node => node.Attribute("Name").Value == "Child2").FirstOrDefault();
```
&emsp;&emsp;在这里查询节点我们通常有两种方式，一种是Element/Elements，一种是Descendants，这两种方式的区别在什么地方呢？Element/Elements是返回当前节点下的指定名称的一级节点的第一个或者全部，这是一种逐级查找的方式。在最近的一个项目中，我们就是采用这种方式来对元素进行定位的，因为我们无法通过正常的方式定位元素，这从侧面说明用户傻到天真，遍历配置if-else这种事事情我是不会去做的，因为我觉这样在迫使我写难以维护的代码，当你用心思考你的设计并提供完善的工作流的时候，你的同事依然将认识停留在当前这个问题而不是一类问题的解决上，我想说这是一种整体理解上的偏差。为了向大家说明使用XDocument创建一个Xml是多么的优雅，我们一起来看如何使用XDocument来创建一个Xml文档。

###创建Xml文档
&emsp;&emsp;我更喜欢将下面这种方式称为声明式的编程，就像我们常常提到函数式编程，那么什么是函数式编程呢？我的理解是，函数式编程是一种编程范式，它的基本思想是将运算过程简化为嵌套的函数调用，就像我们熟悉的Linq一样，Linq从形式上简化了开发者编写的代码，它让大量的筛选、排序、分组这样的频繁性的操作都简化为一行莱姆达表达式，而这恰恰符合函数式编程的特点，即尽可能地使用表达式而非语句、以更接近自然语言的形式组织语言。

```
//构建Xml文档
XDocument document = new XDocument(
  new XDeclaration("1.0", "utf-8", "yes"),
  new XElement("Root",
    new XElement("Child1", new XAttribute("Name", "Child1"),
      new XElement("ChildNode1", "Node1", new XAttribute("Name", "ChildNode1"))),
    new XElement("Child2", 2),
    new XElement("Child3", 3)));

//保存文档
document.Save("output.xml");
```
&emsp;&emsp;我们可以注意到，在这里我们可以非常容易的根据缩进来编写和理解整个Xml文档的层次，虽然Python使用缩进的来代替“{}”的做法颇为人所诟，可是事实上造成这个问题的原因不在语言本身而是在人身上，因为使用缩进来代替“{}”的做法是没有问题的，只要严格遵守这个规则，Python解释器都能够正确解释一段Python代码，可是人是一种奇怪的动物，在使用Tab缩进还是空格缩进、大括号换行还是不换行、使用动态语言还是静态语言这类问题上一直争论不休，所以我认为这个世界上大部分问题，都是人类希望以一己之力打破自然规则造成的，人类永远不会成为自然的主宰，所以按照自然本来的规则去做事情难道不好吗？所有的工作流、框架和工具，从本质上来讲都是因为作者喜欢这样，可这并不代表这一切就应该是这样的，一件事物的流行不一定能够证明这个事物一定优秀，事实上影响它的因素非常多。

## XElement
&emsp;&emsp;看到这里你可能会好奇，XElement难道不是应该是XDocument的一个组成部分吗？为什么这里要单独拿出来讲，这是因为在某些特定场景下，XElement可以作为一个轻量级的Xml解析器来使用，简单来讲，XElement.Load()这种方式通常不会加载根节点，而XDocument.Load()这种方式通常会加载整个文档及其根节点，前者返回的是XElement，后者返回的是XDocument，除了这里不同以外，两者在使用上基本是一致的，当Xml文档结构相对简单所以对XElement我们这里不再展开详细说明啦。

## XmlReader
&emsp;&emsp;XmlReader这个类，我不知道大家是不是和我一样陌生，因为在我的印象中这个类我是从来没有使用过的，如果不是因为最近项目上的原因，我可能永远都不会接触到XmlReader和XmlWriter这两个类，在我看来，这两个类都是辅助类，大家应该注意到在XmlDocument和XDocument中关于加载Xml文档的部分都有涉及，在某些时候，当我们无法直接通过路径操作Xml文档的时候，XmlReader将派上用场，例如最近的项目中涉及到从压缩包中读取Xml，这个时候Xml文件是在内存里的，所以普通的从过路径加载这种方式完全就无用武之地，而同样的，当你修改完Xml文档以后需要保存的时候你需要XmlWriter，这大概就是这两个类的应用场景啦！所以综合这些观点，我的理解是，当你需要按需读取Xml文档的时候，XmlReader能够提供一种消耗资源最少的方式来读取文档，因为我们知道无论是XmlDocument还是XDocument，它们都需要将整个文档读入内存，而XmlReader则不需要因为它是基于数据流的、只读的一种读取方式。我们通过下面的代码来认识它：

```
using(XmlReader reader = XmlReader.Create("childs.xml"))
{
  while(reader.Read())
  {
	if(reader.NodeType == XmlNodeType.Element){
	  if(reader.Name == "Child1"){
	    Console.WriteLine(reader.ReadElementContentAsString());
	  }else if(reader.Name == "Child2"){
	    Console.WriteLine(reader.ReadElementContentAsString());
	  }else if(reader.Name == "Child3"){
        Console.WriteLine(reader.ReadElementContentAsString());
      }
    }
  }
}
```
&emsp;&emsp;看起来这是一种相当原始的处理方式，可我觉得这个对我们理解一个Xml解析器是由帮助的，如果你仔细看这个类的文档，你会发现它支持CDATA、Comment等这种“黑科技”级别的元素的读取，可能是我工作中接触这些东西比较少，有时候在Xml文档中引入CDATA、DTD和注释这类特殊元素的时候，处理方式和普通文档是有所不同的，而XmlReader更为神奇的地方在于它在构造函数中提供了XmlReaderSettings这个参数，该参数支持对是否忽略注释、是否忽略空格以及DTD、Schemas等，从你看到我给出的代码就应该认识到我对这个类不是特别熟悉，所以对这中读取方式我就在这里提一下，让我日后读起这篇文章的时候知道它曾经存在过，如果你对这部分内容比较感兴趣，可以自己花时间去阅读相关内容。

## XmlWriter
&emsp;&emsp;XmlWriter之于XmlReader，就像StreamWriter之于StreamReader一样，这种通过命名就能完全理解一个类的用途的设计完全都不需要注释，可是遗憾的是人们总认为自己的代码比别人写得好，所以从来都不愿意写注释，可是实际上当你无法达到代码自注释这种水平的时候，我的建议是多写注释少写代码，前者是为了让你的代码具有可读性，而后者是为了让你的代码具有可维护性，做到这两点很难，尤其是软件开发这项工作都是有开发周期的，这就造成了我们为了赶交付日期而不重视代码质量的状况发生。好了，闲话少叙，我们来说说XmlWriter。

```
using(FileStream stream = new FileStream("output.xml", FileMode.Create, FileAccess.Write))
{
  using(XmlWriter writer = XmlWriter.Create(stream))
  {
    //Xml头部声明
    writer.WriteStartDocument(true);
    writer.WriteStartElement("Root");
    writer.WriteStartElement("Child1");
    writer.WriteAttributeString("Name", "Child1");
    writer.WriteStartElement("ChildNode1");
    writer.WriteAttributeString("Name", "ChildNode1");
    writer.WriteString("ChildNode1");
    writer.WriteEndElement();
    writer.WriteEndElement();
    writer.WriteEndElement();
  }
}
```
&emsp;&emsp;这的确是相当原始的方法，甚至你都可以自己通过StreamWriter类来实现一个自己的XmlWriter，因为我曾经就用StreamWriter输出过简单的Xml文档，这种方法的原始性体现在哪里呢？我们仅仅输出了一个含有一个子节点及属性的Xml文档而已，可是这个代码已经非常复杂了，因此对一个喜欢简洁优雅的人来说，这种原始的方式是无法满足我的使用欲望的，而它的优点在哪里呢？和XmlReader类似，它支持CDATA、Comment等这种“黑科技”级别的元素的写入，当你发现加载Xml文档的时候可以传入XmlReader，同样的，在保存Xml文档的时候可以传入XmlWriter，就是因为这点简单地好奇心，让我从上周拖到这周想要写这样一篇博客，表示心好累啊，周末白天喜欢睡觉，这样到了晚上可以由充足的精力来写博客，事实证明，我对这两个类就是单纯地好奇而已，可能我了解了以后连使用它都不想吧！


# 工作中Xml读写相关的问题
&emsp;&emsp;现在快1点啦，写完这部分就要睡觉啦。嗯，最后来说说工作中Xml读写相关的问题，实际问题通常会有很多，我这里选择两个我最近遇到的问题来说说它们该如何解决，这两个问题是什么呢？相信大家都看到了这篇文章的目录，即Xml中非法字符和名称空间的处理。这两个问题都有比较完善的解决方案，我仅仅是因为遇到了这两个问题，并且想要将其记录下来而已，所以如果你对这部分内容不感兴趣的话，你可以选择直接忽略它，这里就简单地描述下啦。

## 非法字符
&emsp;&emsp;Xml中的非法字符是指在处理Xml文档时会引发异常的字符内容，而通常来讲，它们主要分为两类，第一类是指在XML规范中规定不允许出现在文档内容中的，例如Xml允许的字符范围是#x9、#xA、#xD、[#x20-#xD7FF]、[#xE000-#xFFFD]、[#x10000-#x10FFFF]，因此在这个范围以外的字符都需要被过滤掉，而需要过滤的字符范围是[0x00-0x08]、[0x0b-0x0c]、[0x0e-0x1f]，第一类字符是绝对要过滤的。第二类是指Xml文档中自身已经在使用的字符，例如&、‘、“、>、<这5个字符都是需要做转义处理的，这种类型我们可以通过Replace方法进行替换，具体转义字符我们可以通过下面这张表格来了解：

| 字符            | HTML转义                  | 字符编码                  |
|:--------------  |:-------------------------:|:-------------------------:|
| &               | &amp;(此处被转义无法显示) | &#38;(此处被转义无法显示) | 
| ’               | &apos;(此处被转义无法显示)| &#39;(此处被转义无法显示) |
| "               | &quot;(此处被转义无法显示)| &#34;(此处被转义无法显示) |
| >               | &gt;(此处被转义无法显示)  | &#62;(此处被转义无法显示) |
| <               | &lt;(此处被转义无法显示)  | &#60;(此处被转义无法显示) |

&emsp;&emsp;对第一类字符，看到这种奇怪的字符我表示是奔溃的，所以如果你熟悉各种字符编码、熟悉正则表达式的编写，我相信你会觉得这里非常有意思，对我而言知道第二种情况怎么处理就好了，这里不知道为什么在Markdown中输入的HTML转义和字符编码都被强制转义，所以大家在这里是没有办法看到正常内容的，希望有知道的朋友可以告诉我如何解决这个问题。

##名称空间
&emsp;&emsp;名称空间这个问题，在普通的Xml文档中通常不会遇到，可是当Xml文档变得非常复杂的时候，Xml就会遇到和编程语言的一样的问题，即如何区分不同的模块文件。在Xml文件中，名称空间可以将不同的元素进行划分，所以在遇到有名称空间的节点的时候，我们都需要指定名称空间。名称空间通常采用简写 + ":" + 元素名称的形式(如w:t这样的节点)，而节点中的简写(如w)通常都可以在Xml文档头部的xmlns中找到定义，如果你接触过WPF中XAML就知道在WPF中编写声明式的代码非常依赖名称空间，这是因为XAML是XML的一个子集，所以XML中的特性就被XAML所继承了，有时候在WPF里发现前端界面无法通过编译通常都是因为XML文档中的名称空间缺失或者是节点标签没有闭合。我想说的是，虽然声明式的界面对设计师友好，可是对程序而言它是一种性能上的灾难，完全的MVVM或者是禁止编写Code-Behind代码在我看来都是一种极端，WPF为人所垢的一个重要因素就是因为反射，而我们都知道这种声明式的界面其实是大量使用了反射技术的。

&emsp;&emsp;虽然名称空间在形式上是w:t这种形式，可是这真的不代表它的节点名称是w:t，而事实上这样的节点名称在Xml是不被允许的，因为":"这个符号是非法的。那么该怎么读取含有名称空间的节点呢？在Linq to Xml(即XDocument)中我们可以使用XNameSpace，在XmlDocument中我们可以使用XmlNamespaceManager，我在这里仅仅给出基本的示例代码，相关内容大家可以自己找时间去了解，因为这个的确是我以前一直忽视的一个知识点吧！

XDocument下的命名空间支持：
```
//假设在xmlns定义中r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
//则xmlNS可以代表r这个名称空间，当查询含有r这个名称空间的节点时在节点名称中添加xmlNS即可
XNamespace xmlNS = @"http://schemas.openxmlformats.org/officeDocument/2006/relationships";
//查询<r:Name></r:Name>节点
XElement element = root.Element(xmlNS + "Name");
```

XmlDocument下的命名空间支持：
```
XmlNamespaceManager xmlNS = new XmlNamespaceManager();
xmlNS.AddNamespace("r", "http://schemas.openxmlformats.org/officeDocument/2006/relationships");
XmlNode  node = root.SelectNodes("//Name", xmlNS);
```

# 本文小结
&emsp;&emsp;本文对.NET平台下Xml读写的常见方式进行了归纳与总结，主要的关注点在XmlDocument和XDocument，XmlReader和XmlWriter作为辅助内容提供补充.XML是一种跨平台、跨语言的文档结构，虽然现在更流行使用JSON，可当我发现原来XML中海油如此多的特性不为我所知或者是等待我去挖掘，我还是决定花费大量的时间、查阅大量资料来写这篇文章。行文至此，虽然我们花费了大量的篇幅来了解Xml，可是实际上我们所认识的这些仅仅是Xml中的冰山一角，关于CDATA、DTD和注释以及XPath、序列化/反序列这些内容，等使用到的时候在做研究吧，我想说我们应该保持这样一种谦逊的态度来生活和学习，当你发现你所不知道的越来越多的时候，最好的方式就是让自己慢下来安心地学习，在学校里我们都是学生，可是出了校门以后，在生活面前我们永远都是学生啊。好了，今天这篇文章就写到这里吧，将近15000多字，博主表示再不想写这么大篇幅的博客啦！