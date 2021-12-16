---
toc: true
title: gRPC 借助 Any 类型实现接口的泛化调用
categories:
  - 编程语言
tags:
  - gRPC
  - Protobuf
  - Any
copyright: true
abbrlink: 2617947988
date: 2021-12-10 11:53:29
---
我发现，人们非常喜欢在一件事情上反复横跳。譬如，以编程语言为例，人们喜欢静态的、强类型语言的严谨和安全，可难免会羡慕动态的、弱类型语言的自由和灵活。于是，在过去的这些年里，我们注意到，`.NET` 的世界里出现了 `dynamic` 类型，`JavaScript` 的世界里出现了 `TypeScript`，甚至连 `Python` 都开始支持类型标注。这种动与静、强与弱的角逐，隐隐然有种太极圆转、轮回不绝的感觉。果然，“城外的人想冲进去，城里的人想逃出来”，钱钟书先生说的固然是婚姻，可世上的事情，也许都差不多罢！人们反复横跳的样子，像极了「九品芝麻官」里的方唐镜。曾经有段时间，好多人吹捧 [Vue3](https://v3.cn.vuejs.org/) + [TypeScript](https://www.tslang.cn/) 的技术栈，有位前辈一针见血地戳破了这种叶公好龙式的喜欢，“你那么喜欢 TypeScript，不还是关掉了 ESLint 的规则，项目里全部都用 Any”。对于这个吐槽，我表示非常真实，因为我们对于动与静、强与弱的心理变化是非常微妙的。常言道，“动态类型一时爽，代码重构火葬场”，你是如何看待编程语言里的动与静静、强与弱的呢？在 gRPC 中我们通过 Protobuf 来描述接口的参数和返回值，由此对服务提供/消费方进行约束。此时，参数和返回值都是静态的、强类型的。如果我们希望提供某种“泛型”的接口，又该如何去做呢？所以，这篇文章我们来聊聊 gPRC 里的 Any 类型。

# Protobuf 里的 Any 类型

在讲 Any 类型前，我想，我们应该想明白，为什么需要这样一个类型？现在，假设我们有下面的 `Protobuf` 定义：

```protobuf
// Vehicle
message Vehicle {
  int32 VehicleId = 1;
  string FleetNo = 2;
}

// Officer
message Officer {
  int32 OfficerId = 1;
  string Department = 2;
} 
```
此时，按照`Protobuf`的规范，我们必须像下面这样定义对应的集合：

```protobuf
// VehicleList
message VehicleList {
  repeated Vehicle List = 1;
}

// OfficerList
message OfficerList {
  repeated Officer List = 1;
} 
```
考虑到，在`C#` 中我们只需要使用 `List<Vehicle>` 和 `List<Officer>` 即可，这样难免就会形成一种割裂感，因为你几乎要为每一种类型建立对应的表示集合的类型，从语义化的角度考虑，我们更希望使用下面的 `Protobuf` 定义：

```protobuf
message Collection {
  repeated Any List = 1;
}
```
此时，`VehicleList` 和 `OfficerList` 就可以统一到 `Collection` 这个类型中，这样，不但减少了花在类型定义的时间，更能帮助我们打开一点思路。在过去，我们编写 API 的时候，通常会定义下面的类来返回结果：

```csharp
public class ApiResult<TData> {
  public int Code { get; set; }
  public string Msg { get; set; }
  public TData Data { get; set; }
}
```

类似地，当我们用 gPRC 来做微服务的时候，我们希望在 `Protobuf` 中沿用这个设计： 

```protobuf
message ApiResult {
  int32 Code = 1;
  string Msg = 2;
  Any Data = 3;
}
```
至此，它可以和我们在 `C#` 中的认知联系起来，不会让你有太多心智上的负担。基于上述两种诉求，我们发现， `Protobuf` 中存在着需要泛化的场景，你可以理解为，我们需要用 `Protobuf` 来表示泛型或者模板类这样的东西。幸运的是，Google 为我们定义了 `Any` 类型，它到底是何方神圣呢？我们一起来看看：

```protobuf
message Any {
  string type_url = 1;
  bytes value = 2;
}
```

没错，它就是这样的朴实无华，甚至比古天乐还要平平无奇，简单来说，`type_url`字段告诉你这是一个什么类型，`value`字段里则存放对应的二进制数据，而这就是 `Any` 类型的全部秘密！

# 在 .NET 中使用 Any 类型

好了，下面我们来演示，如何在 .NET 中使用 `Any` 类型。通过前面我们已经知道， `Any` 类型和我们自定义的消息没有区别，所以，它同样实现了 `IMessage` 和 `IMessage<Any>`两个接口，唯一不同的地方在于，它拥有`Pack()`、`Unpack<T>()`、`TryUnpack<T>()`这样几个静态方法，这是实现任意 `IMessage` 到 `Any` 相互转换的关键。现在，假设我们现在有如下的 `Protobuf` 定义：

```protobuf
message AnyRequest {
  google.protobuf.Any Data = 1; 
}

message AnyResponse {
  google.protobuf.Any Data = 1;
}

message Foo {
  string Name = 1;
}

message Bar {
  string Name = 1;
}
```

此时，如果我们希望在 `AnyRequest` 或者 `AnyResponse` 里传递 `Any` 类型，我们可以这样做：

```csharp
var anyRequest = new AnyRequest()

// Foo -> Any，默认类型地址前缀
var foo = new Foo();
foo.Name = "Foo";
anyRequest.Data = Any.Pack(foo);

// Bar -> Any, 自定义类型地址前缀
var bar = new Bar();
bar.Name = "Bar";
anyRequest.Data = Any.Pack(bar, "type.company.com/bar");
```

反过来，我们可以从 `Any` 中解析出 `IMessage` ：

```csharp
if (request.Data.Is(Foo.Descriptor))
{
  // Any -> Foo
  var foo = request.Data.Unapck<Foo>();
} 
else if (request.Data.Is(Bar.Descriptor))
{
  // Any -> Bar
  var bar = request.Data.Unapck<Bar>();
}
```

默认的 `Any` 类型，只能对 `Protobuf` 生成的类型(即实现了 IMessage 接口)进行 `Pack` ，如果我们想做得更绝一点(最好还是不要)，那么，可以使用自定义的 `MyAny` 类型：

```protobuf
message MyAny {
  string TypeUrl = 1;
  bytes Value = 2;
}
```
相应地，我们为 `MyAny` 类型编写一点扩展方法：

```csharp
public static class MyAnyExtension
{
    public static MyAny Pack(this object obj, string typeUrlPrefix = "")
    {
        var any = new MyAny();
        any.TypeUrl = $"{typeUrlPrefix}/{obj.GetType().FullName}";
        var bytes = Encoding.UTF8.GetBytes(JsonConvert.SerializeObject(obj));
        any.Value = Google.Protobuf.ByteString.CopyFrom(bytes);
        return any;
    }

    public static T Unpack<T>(this MyAny any, string typeUrlPrefix = "")
    {
        var typeUrl = $"{typeUrlPrefix}/{typeof(T).FullName}";
        if (typeUrl == any.TypeUrl)
        {
            var json = Encoding.UTF8.GetString(any.Value.ToByteArray());
            return JsonConvert.DeserializeObject<T>(json);
        }

        return default(T);
    }

    public static bool Is<T>(this MyAny any, string typeUrlPrefix = "")
    {
        var typeUrl = $"{typeUrlPrefix}/{typeof(T).FullName}";
        return typeUrl == any.TypeUrl;
    }
}
```

接下来，我们就可以对任意类型进行处理，虽然，此时此刻，从严格意义上来讲，它已不再属于 `Protobuf` 的范畴，因为序列化/反序列化都交给了 JSON ：

```csharp
var client = serviceProvider.GetService<ProtobufAny.Greeter.GreeterClient>();
client.Ping(new Foo() { Name = "Foo" }.Pack());
client.Ping(new Bar() { Name = "Foo" }.Pack());
client.Ping(new { X = 0, Y = 1, Z = 0 }.Pack());
```

这样看起来是不是非常酷？我始终认为，这件事情是有意义的，一个系统中最多的接口显然是查询接口，此时，我们可以构建一个通用的 [查询](https://github.com/qinyuanpei/DynamicSearch) 来处理，使用者只需要传递一个实体、一个Proto，一组过滤条件，它就可以返回对应的数据，这样是不是比写一个又一个差不多的接口要好一点呢？过去我们开发 API，主张用数据传输对象(DTO)来隔离持久化层和业务层，从这个角度来看，Protobuf 本身就是 一种 DTO ，对于大多数相似的、模板化的、套路化的接口，我们完全可以考虑用这种方案来实现，只要双方约定好类型即可。


# 本文小结
对于编程语言中的动与静、强与弱，我个人觉得还是要看场景，只要双方定义好契约，我相信，它都可以运作起来，当然，更多的时候，我们是在灵活与严谨间反复横跳。作为一门 DSL，Protobuf 虽然可以对服务提供/消费方产生一定约束，可当我们面对需要泛型或者模板类的场景的时候，这种做法就变成了一种负担，更不必说它缺乏对继承的支持。想象一下，你要写二十多个大同小异的接口，譬如为每一张数据表写一个 `GetXXXById()` 的接口。此时，我们可以借助 `Any` 类型来实现类似泛型、模板类的东西，它本质上还是 ` IMessage` 接口的实现类，唯一的不同是增加了 Pack/Unpack 这组静态方法，可以帮助我们实现 `Any` 和 `IMessage` 的相互转换，关于本文中使用的的实例，可以参考：[]()，好了，以上就是这篇博客的全部内容，如果有朋友对文章中的内容和观点存在疑问，欢迎在评论区积极留言，谢谢大家！