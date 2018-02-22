---
title: 使用Mecanim动画系统来控制2D动画
categories:
  - 游戏开发
tags:
  - Mecanim
  - 动画
  - Unity3D
abbrlink: 2583252123
date: 2015-02-11 13:35:58
---
各位朋友，大家好，我是秦元培，欢迎大家关注我的博客，我的博客地址是[http://blog.csdn.net/qinyuanpei](http://blog.csdn.net/qinyuanpei)。今天我想和大家分享的话题是在Unity3D中使用Mecanim动画系统来控制2D动画。

<!--more-->

相信在大家的印象中，Mecanim动画系统主要运用在3D动画中，因为Mecanim动画系统提供了像动画重定向、人体骨骼动画等3D动画的特性，那么Unity3D的Mecanim动画系统能不能用来控制2D动画呢？如果在以前，博主和大家的理解是一样的，认为Mecanim只能运用到3D动画中，对于2D动画只能使用传统的逐帧动画和骨骼动画。可是前不久有位朋友问我，为什么不使用动画组件来控制2D动画呢？博主心想啊，这Mecanim动画系统真的能控制2D动画吗？经过博主查找大量资料和亲身实践，发现Mecanim是可以用来控制2D动画的，而且由于状态机的引入，我们对动画状态的控制会变得更为简单，从写代码的角度来看，这样可以减少我们的代码量便于维护。那么好了，今天我们就来一起学习下如何使用Mecanim动画系统来控制2D动画吧！

#传统2D动画的实现方式
在Unity3D中传统2D动画的实现方式是基于逐帧动画的原理实现的，这种实现方式在Unity3D没有推出Unity2D前甚至在Unity2D推出后相当长的一段时间内，基本上我们最为常用的实现方式，博主在刚开始学习Unity3D的时候通常是以2D形式来展开的，因为博主认为2D和3D在原理上基本是相通的，如果我们掌握了2D游戏的基本原理，那么在实现3D游戏的时候就会相对容易些。我们来看看一个最简单的2D动画的脚本实现：
```C#
//精灵渲染器
private SpriteRenderer mRenderer;
//精灵集合
public Sprite[] Sprites;
//FPS,即每秒钟的画面帧数
public float FPS = 24;
//精灵索引
private int index = 0;
//当前时间
private float currentTime = 0;

void Start () 
{
    mRenderer = GetComponent<SpriteRenderer>();
}
	
void Update () 
{
    //获取当前时间
    currentTime += Time.deltaTime;
    //如果达到了更新画面的时间
    if(currentTime >= 1 / FPS)
    {
        //使索引增加
        index += 1;
        //清除时间记录
        currentTime = 0;
        //当索引更新到最后一帧时,索引重置
        if(index >= Sprites.Length)
        {
            index = 0;
        }
    }

    //更新画面
    mRenderer.sprite = Sprites[index];
}

```
通过分析，我们可以发现这段脚本存在以下问题：
*  动画维护困难：每增加一个动画就需要添加一个数组，不仅增加了动画的维护难度，同时降低了脚本的效率。
*  状态维护困难：因为在Update方法里实现的是一个动画，因此当我们需要在各个动画状态间进行切换的时候，我们需要使用更多的代码来维护相关逻辑。

#使用Mecanim动画系统的实现方式
为了解决传统的2D动画实现方式中存在的动画维护困难、状态维护困难这两个问题，我们需要一种更好的方案来实现2D动画的控制，这种方案需要提供较为方便的动画维护功能，即各个动画是独立的，当改变了某一个动画时，其余的动画不会发生改变。其次，这种方案需要提供较为方便的状态维护功能，即各个动画状态切换是方便的，我们可以更好地从这一种状态切换到另一种状态。关于动画状态切换，大家可以去了解下有限状态机(FSM)的概念，这里我们不做深入的探究，这里我们选择Unity3D的Mecanim动画系统，因为Mecanim动画系统正好解决了这两个问题。好了，下面我们来一起学习一个2D动画的实例：
首先我们在场景中创建一个名为PlayerController的空物体，然后在该物体的下面增加一个精灵组件(Sprite),并将其命名为PlayerSprite，这样做的好处是Unity3D将为我们自动创建较为规范的命名。好了，现在我们选择PlayerController这个物体，然后通过Window->Animation菜单打开Animation窗口：

<img src="http://img.blog.csdn.net/20150301180418811" alt="创建第一个动画" />

首先我们点击AddCurve按钮，此时将弹出一个对话框让我们保存动画文件，这里我们存储为Player@Idle.anim,并将其保存在项目目录下的Animations\Player目录下，这样可以方便我们维护和查找特定的动画文件。在保存完动画文件后，此时会弹出如下的界面，我们选择PlayerSprite节点下的SpriteRenderer，然后选择Sprite，因为这里我们的2D动画主要是通过改变SpriteRenderer的Sprite属性来实现的，最后我们点击Sprite节点后面的加号来完成对象的选取。此时会在动画窗口中显示时间轴和刻度线，我们将在这里完成动画的编辑。大家可以注意到默认情况下，动画面板添加了两帧，即第1帧和最后一帧，其总时间是1秒，同时我们注意到这里有一个采样率(Sample),其实这就是当前动画的FPS了。好了，现在我们开始制作第一个动画：

<img src="http://img.blog.csdn.net/20150301180502756" alt="动画序列" />

在资源文件夹中，我们可以找到当前动画的图片素材，注意到这个图片中总共有12帧画面，因此我们可以按照0.05s的间隔来分配整个时间轴，所以我们可以这样添加帧：

<img src="http://img.blog.csdn.net/20150301180533660" alt="为Idle动画添加帧" />

好了，现在我们就完成了一个Idle动画的制作，现在打开角色的动画控制器PlayerController，这是Unity3D为我们自动创建的一个动画控制器，因为我们现在只有一个Idle动画，所以在Animaotr窗口中我们可以看到只有一个Idle状态，现在我们将这个状态设为默认状态。好了，现在我们可以直接运行游戏，发现在场景中角色开始循环播放Idle动画了。好了，现在让我们重复刚才的步骤，来完成角色的其余动画。

<img src="http://img.blog.csdn.net/20150301180634110" alt="Idle动画效果演示" />

经过一番努力，我们现在已经完成了角色所有动画的制作，现在我们来设计角色的动画状态机：

<img src="http://img.blog.csdn.net/20150301180705294" alt="玩家角色控制器设计" />

设计好角色的动画状态机后我们开始来编写脚本，以实现角色动画的控制：

```C#
using UnityEngine;
using System.Collections;

public class PlayerController : MonoBehaviour {

    public enum PlayerState
    {
        Idle,
        Move,
        LightAttack,
        WeightAttack
    }

    public PlayerState State=PlayerState.Idle;
    //玩家移动速度
    public float WalkSpeed = 0.75f;
    public float RunSpeed = 1.5f;
    //玩家跳跃力的强度
    public float JumpForce = 200f;

    //位置限制
    public float MinX = -5.80f;
    public float MaxX =  5.80f;
    public float MinY = -1.80f;
    public float MaxY =  0.35f;

    //玩家朝向，默认朝右
    public bool isFaceRight = true;

    //动画组件
    private Animator mAnim;
    //2D刚体
    private Rigidbody2D mRig2D;


    void Start () 
    {
        mAnim=GetComponent<Animator>();
        mRig2D=GetComponent<Rigidbody2D>();
    }

    void Update()
    {
        SpriteMove();
        SpriteAttack();
        SpriteJump();
        SpriteIdle();
    }

    /// <summary>
    /// 精灵Idle
    /// </summary>
    private void SpriteIdle()
    {
        //当玩家无任何操作时恢复到Idle状态
        if (!Input.anyKey)
        {
            mAnim.SetBool("Jump", false);
            mAnim.SetBool("Attack", false);
            mAnim.SetBool("BigAttack", false);
            mAnim.SetBool("Skill", false);
            mAnim.SetBool("BigSkill", false);
            State=PlayerState.Idle;
        }
    }

    /// <summary>
    /// 精灵攻击
    /// </summary>
    private void SpriteAttack()
    {
        //轻击，键位J
        if(Input.GetKey(KeyCode.J))
        {
            mAnim.SetBool("Attack", true);
            State=PlayerState.LightAttack;
        }

        //重击，键位K
        if(Input.GetKey(KeyCode.K))
        {
            mAnim.SetBool("BigAttack", true);
            State=PlayerState.WeightAttack;
        }

    }

    /// <summary>
    /// 精灵跳跃
    /// </summary>
    private void SpriteJump()
    {
        if (Input.GetKey(KeyCode.I))
        {
            mAnim.SetBool("Jump", true);
            mRig2D.AddForce(new Vector2(0, Time.deltaTime * JumpForce), ForceMode2D.Impulse);
        }
    }

    private void SpriteMove()
    {
        float h = Input.GetAxis("Horizontal");
        float v = Input.GetAxis("Vertical");

        Vector2 mPos = mRig2D.position;

        mAnim.SetFloat("Speed", Mathf.Sqrt(h * h + v * v));

        float mPosX, mPosY;

        if (Mathf.Sqrt(h * h + v * v) > 0.5f){
            mPosX = mPos.x + h * Time.deltaTime * RunSpeed;
            mPosY = mPos.y + v * Time.deltaTime * RunSpeed;
        }else{
            mPosX = mPos.x + h * Time.deltaTime * WalkSpeed;
            mPosY = mPos.y + v * Time.deltaTime * WalkSpeed;
        }


        mRig2D.MovePosition(new Vector2(mPosX, mPosY));

        if (h > 0 && !isFaceRight)
        {
            FlipSrite();
        }
        else if (h < 0 && isFaceRight)
        {
            FlipSrite();
        }
    }


    void FlipSrite()
    {
        if(isFaceRight){
            transform.rotation=Quaternion.Euler(0,180,0);
            isFaceRight=false;
        }else{
            transform.rotation=Quaternion.Euler(0,0,0);
            isFaceRight=true;
        }
    }
}

```

好了，现在我们可以来看看最终的效果，博主这里是想利用这些素材来制作一个横板过关的游戏，可是因为文章篇幅有限，所以这部分内容只能留到以后再和大家分享了。

<img src="http://img.blog.csdn.net/20150301180829879" alt="最终效果演示"/>

#Mecanim动画系统应用扩展
好了，到现在为止，基于Mecanim动画系统的2D动画控制基本上讲解完了。下面我们说说Mecaanim动画系统应用扩展。通过前面的学习，我们知道Unity2D使用的Mecanim动画系统主要是通过改变游戏体的属性来实现某种特定的动画效果的，例如我们这里的动画是通过改变角色精灵附加的SpriteRenderer组件的Sprite属性来实现的，因此从本质上来说Unity2D的动画控制器是一种属性动画。总体来说，Unity2D可以实现以下类型的动画：
*  位移动画：通过Transform组件的Position属性实现
*  旋转动画：通过Transform组件的Rotation属性实现
*  伸缩动画：通过Transform组件的Scale属性实现
*  渐变动画：通过更改指定组件的颜色或材质实现
*  脚本动画：通过更改指定脚本的变量或字段实现


好了，这就是今天这篇文章的全部内容了，希望大家喜欢！



