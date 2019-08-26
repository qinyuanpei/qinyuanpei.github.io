---
abbrlink: 3449402269
categories:
- 游戏开发
date: 2015-03-12 19:13:38
description: 首先这种转盘游戏概率设计的前提是转盘固定不动，转盘指针绕中心位置旋转，与这篇文章中的恰好相反
tags:
- 转盘
- 游戏
- 概率
title: 使用Unity3D创建一个幸运转盘
---

&emsp;&emsp;今天我们来做点和游戏无关的事情吧！博主最近情绪一直比较低落，因为在找工作的过程中遇到了些挫折。当一个人内心缺乏斗志的时候，通常会难以静下心来认真地做事情，所以这段时间博主并不打算再去为大家分享新的游戏案例，希望大家能够谅解啊。

<!--more-->

&emsp;&emsp;好了，博主今天想和大家分享的是一个叫做幸运转盘的案例。我们知道平时在节假日商场为了促销商品，通常都会推出诸如转盘抽奖这样的游戏。在学了概率以后，虽然我们都知道中奖是一个小概率事件，可是人们对买彩票中奖这样的事情仍然乐此不疲。就像腾讯通过今年的春晚成功地为微信支付培养了大量忠实用户一样，虽然大家抢红包抢到的钱都不算多，可是大家都还是愿意去抢红包啊。为什么呢？呵呵，不就图一乐嘛。好了，那么下面我们一起乐一乐吧，因为激动人心的抽奖环节就要开始了！

&emsp;&emsp;首先我们来看看在Unity3D中如何实现转盘抽奖：

![转盘游戏示意图](https://ws1.sinaimg.cn/large/4c36074fly1fz05nmzwwtj20nb0h9q7h.jpg)

&emsp;&emsp;从这张图片我们可以看出，转盘抽奖有两部分组成：转盘是可以旋转的、转盘指针是固定不动的。那么，好了，抽奖无非就是让转盘转起来然后再停下来嘛，直接给出代码：
```C#
using UnityEngine;
using System.Collections;

public class LuckyRoll : MonoBehaviour {

    //幸运转盘
    private Transform mRoolPanel;

    //初始旋转速度
    private float mInitSpeed;
    //速度变化值
    private float mDelta=0.5f;

    //转盘是否暂停
    private bool isPause=true;

    void Start () 
    {
        //获取转盘
        mRoolPanel=this.transform.FindChild("Background");
    }

    //开始抽奖
    public void OnClick()
    {
        if(isPause)
        {
            //随机生成一个初始速度
            mInitSpeed=Random.Range(100,500);
            //开始旋转
            isPause=false;
        }
    }

    void Update()
    {
        if(!isPause)
        {

            //转动转盘(-1为顺时针,1为逆时针)
            mRoolPanel.Rotate(new Vector3(0,0,-1) * mInitSpeed * Time.deltaTime);
            //让转动的速度缓缓降低
            mInitSpeed-=mDelta;
            //当转动的速度为0时转盘停止转动
            if(mInitSpeed<=0)
            {
                //转动停止
                isPause=true;
            }
        }
    }
}
```
&emsp;&emsp;这里我们随机给出一个速度mInitSpeed，然后让它按照mDelta的速率缓慢的减少，当mInitSpeed的数值为0时表示转盘停止转动。好了，我们来看看最后的效果：

![转盘游戏演示](https://ws1.sinaimg.cn/large/4c36074fly1fz05knyqung20ln0e67wk.gif)

&emsp;&emsp;从现在的效果来看，这个案例基本上成功了，所以以后如果碰到需要这种抽奖活动的场合，大家就可以跟美术协调好，快速地制作出这样一个幸运转盘来向身边的人们炫耀了。不过这个案例同样存在问题：
*  基于随机数的转盘转动不受玩家控制，玩家无法参与到互动当中，可以考虑触摸操作，这样可以根据玩家的操作来模拟转动，提高游戏的真实性和可玩性。
*  因为抽奖的结果是由美术设计在转盘上的，所以程序无法根据转盘停止后指针的位置直接判断出玩家抽奖的结果以及本次抽奖是否为有效的抽奖(指针恰好停留在两个扇形区域的分界线上)。
*  因为这里转盘的旋转并没有严格地按照实际情况下转盘的受力情况来设计，因此可以说这个游戏中的概率分布可能不是均匀的，因此计算机里使用的随机数是伪随机数。

&emsp;&emsp;好了，暂时就发现这些问题，如果有朋友知道如何模拟触屏操作和阻尼运动，可以在这篇文章后面给我留言，今天的内容就是这样了，希望大家会喜欢！


#### 2015年3月31日更新：
&emsp;&emsp;今天找到了关于转盘游戏概率设计的相关内容，所以经过整理后补充在这里：
首先这种转盘游戏概率设计的前提是转盘固定不动，转盘指针绕中心位置旋转，与这篇文章中的恰好相反。如下图所示，在这个转盘游戏的设计中主要遵循基本的三角函数,这里以指针默认位置朝上来讲解该原理。如果指针的默认位置在其它位置上的，可以此类推。

![转盘游戏示意图](https://ws1.sinaimg.cn/large/4c36074fly1fz05e8swoxj20f20c2t99.jpg)

>x+=x*cosᶱ
>y+=y*cosᶱ

&emsp;&emsp;好了，现在我们就可以通过调整指针的角度来实现抽奖游戏了。比如我们将转盘平均分成8份，指针角度为0表示奖品A,指针角度为45度表示奖品B等等，以此类推。这样的话，我们只要调整指针的角度就可以控制抽奖的结果。可是在实际生活中，指针不可能一次就指到对应的奖品上去，通常会在旋转若干圈后慢慢地停下来。因此我们可以使用下列公式：

>指针角度=360*圈数+(目标角度与初始角度的差值)

&emsp;&emsp;这里的圈数可以通过随机数来生成，这样可以让每次抽奖更加随机些，当然为了增加抽奖的真实感，我们可以采用这篇文章中提到的减速的方法来实现一个缓停的效果。那么问题来了，如果转盘上的奖项不是均匀分布的怎么呢？这种情况可以根据转盘上圆心角的大小为每一个奖项设定一个范围，然后在这个范围内随机生成一个角度来计算指针的角度，好了，下面给出代码实现：
```C#
using UnityEngine;
using System.Collections;
using System.Collections.Generic;

public class LuckyRoll2 : MonoBehaviour {

    //对奖项进行封装
    private class WrapItem
    {
        public WrapItem(string name,float rank,float ang1,float ang2)
        {
            this.ItemName=name;
            this.ItemRank=rank;
            this.MinAngle=ang1;
            this.MaxAngle=ang2;
        }

        //奖项名称
        public string ItemName{get;set;}
        //奖项概率
        public float ItemRank{get;set;}
        //最大角度
        public float MaxAngle{get;set;}
        //最小角度
        public float MinAngle{get;set;}
    }

    
    //全部的奖项
    private List<WrapItem> allItems;
    void Start () 
    {
        //初始化奖品
        allItems=new List<WrapItem>()
        {
           //圆心角为5°，概率为10%，以此类推
            new WrapItem("奖品1",10,0,30),
            new WrapItem("奖品2",15,30,90),
            new WrapItem("奖品3",20,90,165),
            new WrapItem("奖品4",25,165,255),
            new WrapItem("奖品5",30,255,360),
        };

        //模拟抽奖10次
        for(int i=0;i<10;i++)
        {
            Debug.Log(Roll());
        }
    }
    
    /// <summary>
    /// 抽奖方法
    /// </summary>
    private string Roll()
    {
        //抽奖结果
        string result="";
        //概率总精度为100
        float totalRank=100;
       foreach(WrapItem item in allItems)
       {
          //产生一个0到100之间的随机数
          float random =Random.Range(0,totalRank);
          //将该随机数和奖品的概率比较
          if(random<=item.ItemRank)
          {
             //抽奖结果
             result=item.ItemName;
             //为转盘指针随机生成旋转角度
             float angle=Random.Range(item.MinAngle,item.MaxAngle);
             //旋转转盘指针,此处略
             break;
          }else
          {
             totalRank-=item.ItemRank;
          }
       }
       return "抽奖结果为:"+result;
    }
}
```
&emsp;&emsp;好了，这里我们没有写转盘旋转的功能，这部分内容大家自己去实现好了，因为在Unity3D里面实现这样一个功能实在是太简单了。今天我们主要关注的内容是概率，所以我们重点对概率做了些研究，这里我们来讨论下算法中的概率计算问题，首先奖品1、奖品2、奖品2、奖品4、奖品5的概率分别为10%、15%、20%、25%、30%，其概率之和为100。因此
>奖品1：从0~100中随机抽取一个数，这个数值小于10的概率显然是10%，这是第一轮数组遍历。

>奖品2：在第一轮数组遍历没有返回的情况下，进入第二轮遍历，此时从0~90中随机抽取一个数，其概率为(1-(10/100)*(15/(100-10))=15%。同样的，抽到奖品3的概率为(1-(25/100))*(20/(100-25))=20%，以此类推。

好了，这部分内容终于补充到这篇文章里了，对于这个问题的研究基本上可以告一段落，不得不说概率对于游戏开发来说还是蛮重要的啊，有时间学习下数学吧，反正咱底子不弱啊，哈哈。

&emsp;&emsp;下面给出程序演示效果：

![转盘游戏概率设计效果演示](https://ws1.sinaimg.cn/large/4c36074fly1fz01zwac2hj20e407gq32.jpg)

## 参考资料
[大家快来玩转盘抽奖游戏(走在网页游戏开发的路上)(七)](http://www.cnblogs.com/skynet/archive/2011/06/15/2081106.html)
[php+jquery实现转盘抽奖概率可任意调整](http://www.xiaomlove.com/phpjquery%E5%AE%9E%E7%8E%B0%E8%BD%AC%E7%9B%98%E6%8A%BD%E5%A5%96-%E6%A6%82%E7%8E%87%E5%8F%AF%E4%BB%BB%E6%84%8F%E8%B0%83/)