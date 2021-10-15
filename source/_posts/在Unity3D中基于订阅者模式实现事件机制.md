---
abbrlink: 632291273
categories:
- Unity3D
date: 2016-01-15 12:30:41
description: 注意到在这个“通知中心”中，我们首先实现了单例模式，这样我们可以通过Get方法来获取该“通知中心”的唯一实例，其次这里利用一个字典来存储对所有事件的引用，这样保证外部可以通过AddEventListener和RemoveEventListener这两个方法来进行事件的添加和移除，对于添加的事件引用我们可以通过DispatchEvent方法来分发一个事件，事件的回调函数采用委托来实现，注意到这个委托需要一个Notification类型，对该类型简单定义如下：;public
  void DispatchEvent(string eventKey, GameObject sender, object param);public void
  DispatchEvent(string eventKey,object param)
tags:
- 设计模式
- 消息
- 事件
title: 在Unity3D中基于订阅者模式实现事件机制
---

&emsp;&emsp;各位朋友，大家好，欢迎大家关注我的博客，我是秦元培，我的博客地址是[http://qinyuanpei.com](http://qinyuanpei.com)。今天博主想和大家分享的是在Unity3D中基于订阅者模式实现消息传递机制，我们知道Unity3D中默认提供了一种消息传递机制SendMessage，虽然SendMessage使用起来的确非常简单，可是它的这种简单是建立在付出一定的代价的基础上的。经常有朋友提及不同的模块间如何进行通信的问题，可能答案最终会落到**单例模式**、**委托**和**事件机制**这些关键词上，在这种情况下本文所探讨的内容可能会帮助你找到最终的答案。

<!--more-->
# 从生活中得到的启示
&emsp;&emsp;我们知道通过在Unity3D中通过GetComponent就可以获得某个模块的实例，进而引用这个实例完成相关任务的调用。可是显然这种方法，就像我们随身带着现金去和不同的人进行交易，每次交易的时候都需要我们考虑现金的支入和支出问题，从安全性和耦合度两个方面进行考虑，这种方法在面对复杂的系统设计的时候，非常容易造成模块间的相互依赖，即会增加不同模块间的耦合度。为了解决这个问题，大家开始考虑单例模式，因为单例模式能够保证在全局内有一个唯一的实例，所以这种方式可以有效地降低模块间的直接引用。单例模式就像是我们在银行内办理了一个唯一的账户，这样我们在交易的时候只需要通过这个账户来进行控制资金的流向就可以了。单例模式确保了各个模块间的独立性，可是单例模式更多的是一种主动行为，即我们在需要的时候主动去调用这个模块，单例模式存在的问题是无法解决被调用方的反馈问题，除非被调用方主动地去调用调用方的模块实例。说到这里我们好像看到了一种新的模式，这就是我们下面要提到的事件机制。

# 订阅者模式和事件机制
&emsp;&emsp;首先这里要提到一种称为“订阅者模式”的设计模式，这种设计模式在《大话设计模式》这本书中称为“观察者模式”或者“发布-订阅（Publish/Subscribe）模式”，我们这里暂且叫做“订阅者模式”吧！该模式定义了一种一对多的依赖关系，让多个观察者对象同时监听某一个主题对象。这个对象在状态发生变化时会通知所有观察者对象，使它们能够自动更新自己。针对这个模式，我们可以考虑事件机制的实现，事件机制可以理解为在一个事件中心（Subject）保存有对所有事件（Observer）的引用，事件中心负责对这些事件进行分发，这样每个事件就可以通过回调函数的方式进行更新，这样就实现了一个事件机制。下面给出基本的代码实现：
```csharp
using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;

namespace UniEventDispatcher
{
    /// <summary>
    /// 定义事件分发委托
    /// </summary>
    public delegate void OnNotification(Notification notific);

    /// <summary>
    ///通知中心 
    /// </summary>
    public class NotificationCenter
    {

        /// <summary>
        /// 通知中心单例
        /// </summary>
        private static NotificationCenter instance=null;
        public static NotificationCenter Get()
        {
            if(instance == null){
                instance = new NotificationCenter();
                return instance;
            }
            return instance;
        }


        /// <summary>
        /// 存储事件的字典
        /// </summary>
        private Dictionary<string,OnNotification> eventListeners 
            = new Dictionary<string, OnNotification>();

        /// <summary>
        /// 注册事件
        /// </summary>
        /// <param name="eventKey">事件Key</param>
        /// <param name="eventListener">事件监听器</param>
        public void AddEventListener(string eventKey,OnNotification eventListener)
        {
            if(!eventListeners.ContainsKey(eventKey)){
                eventListeners.Add(eventKey,eventListener);
            }
        }

        /// <summary>
        /// 移除事件
        /// </summary>
        /// <param name="eventKey">事件Key</param>
        public void RemoveEventListener(string eventKey)
        {
            if(!eventListeners.ContainsKey(eventKey))
                return;

            eventListeners[eventKey] =null;
            eventListeners.Remove(eventKey);
        }

        /// <summary>
        /// 分发事件
        /// </summary>
        /// <param name="eventKey">事件Key</param>
        /// <param name="notific">通知</param>
        public void DispatchEvent(string eventKey,Notification notific)
        {
            if (!eventListeners.ContainsKey(eventKey))
                return;
            eventListeners[eventKey](notific);
        }

        /// <summary>
        /// 分发事件
        /// </summary>
        /// <param name="eventKey">事件Key</param>
        /// <param name="sender">发送者</param>
        /// <param name="param">通知内容</param>
        public void DispatchEvent(string eventKey, GameObject sender, object param)
        {
            if(!eventListeners.ContainsKey(eventKey))
                return;
            eventListeners[eventKey](new Notification(sender,param));
        }

        /// <summary>
        /// 分发事件
        /// </summary>
        /// <param name="eventKey">事件Key</param>
        /// <param name="param">通知内容</param>
        public void DispatchEvent(string eventKey,object param)
        {
            if(!eventListeners.ContainsKey(eventKey))
                return;
            eventListeners[eventKey](new Notification(param));
        }

        /// <summary>
        /// 是否存在指定事件的监听器
        /// </summary>
        public Boolean HasEventListener(string eventKey)
        {
            return eventListeners.ContainsKey(eventKey);
        }
    }
}
```
&emsp;&emsp;注意到在这个“通知中心”中，我们首先实现了单例模式，这样我们可以通过Get方法来获取该“通知中心”的唯一实例，其次这里利用一个字典来存储对所有事件的引用，这样保证外部可以通过AddEventListener和RemoveEventListener这两个方法来进行事件的添加和移除，对于添加的事件引用我们可以通过DispatchEvent方法来分发一个事件，事件的回调函数采用委托来实现，注意到这个委托需要一个Notification类型，对该类型简单定义如下：
```csharp
using System;
using UnityEngine;

namespace UniEventDispatcher
{
    public class Notification
    {
        /// <summary>
        /// 通知发送者
        /// </summary>
        public GameObject sender;

        /// <summary>
        /// 通知内容
        /// 备注：在发送消息时需要装箱、解析消息时需要拆箱
        /// 所以这是一个糟糕的设计，需要注意。
        /// </summary>
        public object param;

        /// <summary>
        /// 构造函数
        /// </summary>
        /// <param name="sender">通知发送者</param>
        /// <param name="param">通知内容</param>
        public Notification(GameObject sender, object param)
        {
            this.sender = sender;
            this.param = param;
        }

        /// <summary>
        /// 构造函数
        /// </summary>
        /// <param name="param"></param>
        public Notification(object param)
        {
            this.sender = null;
            this.param = param;
        }

        /// <summary>
        /// 实现ToString方法
        /// </summary>
        /// <returns></returns>
        public override string ToString()
        {
            return string.Format("sender={0},param={1}", this.sender, this.param);
        }
    }
}
```
&emsp;&emsp;对Notification的定义需要提供发送者和发送内容，这样可以保证所有的通知都按照这样的格式进行定义，如果有Socket开发经验的朋友可能会联想到通讯协议的定义，这里是比较相似啦，哈哈！

# 使用事件机制的一个示例
&emsp;&emsp;这里以一个简单的示例来验证事件机制的可行性，我们在场景中有一个球体，默认这个球体的颜色为白色，通过调整界面中的RGB数值，可以改变球体的颜色，在这个示例中UI是事件发送者，负责UI中Slider控件的数值发生变化时向球体发送消息，传递的数据类型是Color类型；球体为事件接收者，负责注册事件及接收到消息后的处理。因为代码较为简单，所以这里写在一个脚本中：
```csharp
using UnityEngine;
using UnityEngine.UI;
using System.Collections;
using UniEventDispatcher;

public class Example : MonoBehaviour 
{
    /// <summary>
    /// R数值的Slider
    /// </summary>
    private Slider sliderR;

    /// <summary>
    /// G数值的Slider
    /// </summary>
    private Slider sliderG;

    /// <summary>
    /// B数值的Slider
    /// </summary>
    private Slider sliderB;

    void Start () 
    {
        //在接收者中注册事件及其回调方法
        NotificationCenter.Get().AddEventListener("ChangeColor", ChangeColor);

        //在发送者中分发事件，这里以UI逻辑为例
        sliderR = GameObject.Find("Canvas/SliderR").GetComponent<Slider>();
        sliderG = GameObject.Find("Canvas/SliderG").GetComponent<Slider>();
        sliderB = GameObject.Find("Canvas/SliderB").GetComponent<Slider>();
        //注册UI事件
        sliderR.onValueChanged.AddListener(OnValueChanged);
        sliderG.onValueChanged.AddListener(OnValueChanged);
        sliderB.onValueChanged.AddListener(OnValueChanged);
    }

    public void OnValueChanged(float value)
    {
        //获得RGB数值
        float r = sliderR.value;
        float g = sliderG.value;
        float b = sliderB.value;
        //分发事件,注意和接收者协议一致
        NotificationCenter.Get().DispatchEvent("ChangeColor", new Color(r, g, b));
    }

    /// <summary>
    /// 改变物体材质颜色
    /// </summary>
    /// <param name="notific"></param>
    public void ChangeColor(Notification notific)
    {
        Debug.Log(notific.ToString());
        //设置颜色
        renderer.material.color = (Color)notific.param;
    }
}
```
该示例运行效果如下：

![事件机制的简单示例](https://ww1.sinaimg.cn/large/4c36074fly1fzix8enrpvg20d108n0xz.jpg)

# 小结
&emsp;&emsp;虽然目前这个事件机制在实现和使用上没有什么问题，可是从扩展性和可优化性上来考虑，这个设计目前存在以下问题：
* 字符型的键名使用起来方便，可是对通知者和接收者由1个以上的人力来维护的时候双方需要通过沟通来确定键名，可以考虑使用GameObject或者Transform来替代现在的键名设计，可是这种设计带来的新问题是会增加不同模块间的GameObject或者Transform的相互引用。
* 通知者和接收者在传递参数和接受参数的时候需要分别进行装箱和拆箱，所以这并非一个优秀的设计，同时需要双方保证传递的参数类型一致。解决方法是针对不同的类型对通知中心进行派生或者考虑对通知中心提供泛型约束，这样做的目的是使Notification中的通知内容变成具体的类型，这样就可以解决目前需要进行装箱和拆箱而带来的性能问题。