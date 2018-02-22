---
title: 在Socket通信中使用Protobuf来进行消息的序列化
categories:
  - 编程语言
tags:
  - Socket
  - 通信
  - Protobuf
abbrlink: 2141352005
date: 2016-01-28 11:48:58
---
&emsp;&emsp;最近一直在研究Socket通信，在实现了简单的字符串型消息发送和接收以后，博主开始尝试探索更多的内容。比如目前服务器端在接受到客户端消息后默认采取的处理方式是对消息进行群发，当我们尝试让客户端给指定客户端发送消息的时候，我们发现现有的消息模式可能无法更好的支持这一个想法，博主的思路是定义这样一种结构，这个结构由发送者、接收者和消息三部分组成，如果接收者为空则对消息进行群发否则对指定接收者发送消息，这样就面临一个问题：如何让Socket通信支持更多的类型。

<!--more-->

#Socket通信中的类型问题
&emsp;&emsp;通常为了解决这个问题，我们可以从类型转换或者说序列化/反序列化的角度来考虑，由此我们有下面三种思路：
* Socket通信中核心是一个byte数组，因此可以尝试将各种类型转化为byte数组。例如一个int类型占4个字节，因此可以考虑使用System.BitConverter.GetBytes()方法将一个整型变量转化为byte数组，相应地在解析数据的时候可以使用System.BitConverter.ToInt32()方法转化为整型数值。这种方式需要定义一个结构，该结构由消息头和消息体组成，消息头表示消息类型，消息体表示具体的消息，其缺点是在收发数据的时候需要保持高度一致。

* 考虑到目前实现了字符串类型的发送和接收，因此可以尝试将各种类型转化为字符串类型，这个就是我们较为的序列化和反序列化了，我们可以选择的数据形式有XML和JSON两种形式，考虑到JSON的数据冗余度较低，因此选择使用JSON来作为消息传递的数据形式从效率上来说更为高效。这种方式的缺点是客户端和服务器需要约定好数据类型，例如在我们开始提到的问题中，我们可以使用这样的结构来描述：
```
{sender:"消息发送者",reciver"消息接收者",message:"消息体"}
```
* 基于byte数组或者基于字符串都可以解决Socket通信中的消息类型问题，可是它需要我们提前设计好数组后者字符串的长度。为此我们需要一个更好的解决方案，这个解决方案就是来自Google的开源项目Protobuf，其特点是可以按照定义好的协议内容将数据直接序列化为byte数组，这样可以保证在数组长度上得到优化。Protobuf最大的问题时需要在服务器和客户端中使用相同的协议，因为协议到实体结构的转化依赖自工具ProtoGen，当客户端使用一种新的协议的时候，服务器需要有同样的协议来处理。

#Protobuf的简单使用及其示例
##Protobuf的下载和安装
&emsp;&emsp;Protobuf在使用的时候相对简单，首先我们需要到[http://code.google.com/p/protobuf-net/](http://code.google.com/p/protobuf-net/)下载Protobuf的.NET版本，该项目提供了各种.NET框架下的插件版本，因为我们这里是在Unity3D中使用该插件，所以我们需要的是Full目录下的Unity版本，将其复制到Unity3D项目中就可以使用了，这里建议放在Plugins目录内。

##Protobuf协议的定义
&emsp;&emsp;接下来，我们定义一个简单的协议文件，该文件是一个纯文本文件，其扩展名为.proto。我们继续沿用文章开始提到的那个消息结构：
```
package ChatMessage; //package可以看作命名空间

    message Message //message可以看作类或者是结构
    {
        required string sender = 1;//required表示该成员为必选选项
        optional string reciver = 2;  //optional表示该成员为可选选项
        required string message = 3;//数字表示该成员字段的序号
    }
```
关于Protobuf协议定义的更多细节，大家可以在ProtoGen目录下的descriptor.proto文件中进行查看，这里仅仅作为一个简单的协议定义呈现出来。

##使用ProtoGen生成实体类
&emsp;&emsp;C#是一门面向对象的语言，因此在C#中使用Protobuf必须要有与协议对应的实体类，ProtoGen能够帮助我们完成这个工作，它是一个命令行工具，在该目录下使用命令行输入，注意这里假定协议文件在该目录下：
```
protogen -i:chatmessage.proto -o:ChatMessage.cs
```
执行该命令后即可生成对应的ChatMessage.cs文件，我们需要将这个文件分别放置在服务器和客户端项目中备用。

##序列化和反序列化
```
ChatMessage.Message message = new ChatMessage.Message();
message.sender = "路人甲";
message.reciver = "路人乙";
message.message="这些年你过得好吗?";

//序列化
System.IO.MemoryStream stream = new System.IO.MemoryStream();
ProtoBuf.Serializer.Serialize<ChatMessage.Message>(stream, message);
byte[] bytes = stream.ToArray();

//反序列化
System.IO.MemoryStream stream = new System.IO.MemoryStream(bytes);
ChatMessage.Message message = ProtoBuf.Serializer.Deserialize<ChatMessage.Message>(stream);
```

可以注意到Protobuf的序列化和反序列化主要针对byte数组，这是非常适合Socket通讯的我们只需要在客户端发送byte数组然后再客户端解析byte数组就可以了，从整体上来看Protobuf的使用是比较简洁的，当然Protobuf的用途不仅仅局限在Soket通讯中，有序列化和反序列化处皆可考虑使用Protobuf。讲到这里，Protobuf和Socket相关的部分我们不再尝试了，因为实在没有什么可说的了，有兴趣的朋友可以尝试以JSON作为数据传输模型的研究，好了，今天的内容就是这样啦。



