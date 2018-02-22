---
title: Unity3D塔防游戏开发项目讲解(下)
categories:
  - 游戏开发
tags:
  - 游戏开发
  - Unity3D
  - 塔防
abbrlink: 1176959868
date: 2015-01-21 13:50:48
---
各位朋友，大家好，我是秦元培，欢迎大家关注我的博客，我的博客地址是[http://blog.csdn.net/qinyuanpei](http://blog.csdn.net/qinyuanpei)。我们知道一个完整的塔防游戏由地图、敌人、防守单位三个部分组成，在上一篇文章中我们已经对地图这块儿进行了全面的讲解，今天我们来说说敌人和防守单位。

<!--more-->

# 敌人篇
## 敌人自动寻路的实现
敌人在游戏中有一个基本的行为，即沿着寻路路径向我方阵地移动并发起攻击。在地图篇中，我们详细地介绍了敌人寻路路径的生成原理。既然有了敌人寻路的路线，那么怎么让敌人沿着路线移动呢？其实只要指定敌人寻路的起点就可以了，因为在寻路路径的设计中，我们使用的是一个类似于链表的结构，这样我们就能根据每个结点获取它的目标结点，从而实现敌人沿着寻路路径移动的效果了。因为敌人寻路的路线是定义在PathNode类中的，因此我们可以写出下面这样的代码：
```C#
void Move()
{
	Vector3 mPos1=this.transform.position;
	Vector3 mPos2=this.StartNode.transform.position;
	//计算敌人与路径节点间的距离
	float mDis=Vector2.Distance(new Vector2(mPos1.x,mPos1.y),new Vector2(mPos2.x,mPos2.y));
	if(mDis<0.1F){
		if(StartNode.ThatNode==null){
			//对防守阵地进行摧毁
			GameManager.Instance.PlayerHP-=20;
			//从敌人列表中移除自身
			GameManager.Instance.Enemys.Remove(this);
			//销毁自身
			Destroy(this.gameObject);
			//销毁血条
			Destroy(mHPBar.gameObject);
			}else{
			StartNode=StartNode.ThatNode;
		}
	}
	//计算敌人的移动方向
	Vector3 mDir=new Vector3(mPos2.x-mPos1.x,mPos2.y-mPos1.y,0).normalized;
	transform.Translate(mDir * MoveSpeed * Time.deltaTime);
} 
```
好了，现在我们来一起分析这段代码。首先，我们计算了敌人与路径结点间的距离，这里我们用0.1来近似地表示敌人已经到了路径结点上，此时如果该结点的目标结点为null则表示此时敌人已经到了最后一个结点处，所以敌人会对我方的阵地造成20点的伤害并销毁敌人。在GameManager我们使用了一个列表来管理和维护当前场景中的所有敌人，因此当当前敌人销毁时需要从列表中移除，GameManager类是一个静态类，负责对游戏的全局维护，这个类我们放到稍后来讲啊。那么如果敌人没有走到最后一个结点怎么办呢？我们只需要将StartNode指向StartNode的目标节点，这样我们就可以对整个路径结点实现遍历。这里是不是有种数据结构的感觉呢？哈哈，数据结构和算法是编程中最基础、最重要的内容，这些内容到了游戏开发领域同样是适用的。那么，好了，既然知道敌人是怎么移动的，现在我们就来对敌人进行移动吧，这里是采用计算移动方向的方式来实现，这个很简单啦。

好了，现在我们来说说敌人的血条吧，我们知道当怪物沿着寻路路径向我方阵地发起攻击的时候，我方防守单位会自动地对敌人进行防御性攻击，那么此时血条就可以显示敌人的实时血量，从而方便玩家根据战场的情况来调整兵力部署情况。我们知道从Unity4.6以后Unity开始使用全新的GUI系统UGUI，因为博主在之前的项目中一直使用NGUI，加上博主不是很喜欢做UI，所以每次用NGUI的时候整个人的心情都是不好的，有段时间被NGUI虐得体无完肤，感觉整个人都不好了。好了，既然现在我们有了新的选择UGUI，那么就让我们先睹为快吧！如图，全新的NGUI位于GameObect->UI菜单下，基本覆盖了常用的如Button、Image、Slider、ScrollBar等控件，因为UGUI刚推出不久，所以博主希望大家还是能客观、公正的对待UGUI和NGUI，博主认为在短期内这两个GUI系统将处于共存的状态，不存在相互替代的可能性。
<img src="http://img.blog.csdn.net/20150301184316413" alt="UGUI"/>
 好了，UGUI所有的控件都是放到一个叫做Canvas的父控件下的，这一点和NGUI的UIRoot有些类似吧！Canvas提供了三种模式的UI系统，即Screen Space-Overlay、Screen Space-Camera、World Space。第一种Screen Space-Overlay它是完全以当前屏幕的像素大小创建的一个矩形范围，即控件是以屏幕坐标来绘制的；第二种Screen Space-Camera它是根据相机的视线范围来确定的一个矩形范围，其控件是根据Camera的ViewPortPoint坐标来绘制的;第三种从名称我们就可以知道，它是完全3D化的UI,使用的是常用的世界坐标。博主是刚开始研究UGUI,如果有不对的地方还希望大家能够原谅啊。好了，下面我们正式来做血条吧，在这里我们使用的是默认的Slider控件，用Slider控件来制作血条需要将Slider控件自带的滑块删除，然后我们通过改变value就可以实现一个简单的血条了。在UGUI中所有的图片素材都是以Sprite的形式来出现的，所以UGUI可以自己生成图集，不需要像NGUI在做UI前首先要生成图集。这是博主做的一个简单的血条。现在血条做好了，可是问题来了：这UGUI的所有控件都必须要放到Canvas下面啊，所以我们没法像NGUI一样直接把做好的血条放到怪物下面。怎么办呢？既然不能放到怪物下面，那我们就放到Canvas下面吧，不过我们需要自己计算血条的位置。好了，下面来看代码：
```C#
public class Enemy : MonoBehaviour 
{

	//敌人的生命值
	public float MaxHP;
	public float HP;

	//敌人的初始路径节点
	public PathNode StartNode;
	//敌人的移动速度
	public float MoveSpeed=0.15F;
	//敌人的旋转速度
	public float RotateSpeed=0.3F;

	//敌人血条预制件
	public GameObject HPBar;
	//敌人血条组件
	private Slider mHPBar;

	//public EnemySpawn mSpawn;

	void Awake()
	{
		//在敌人列表中增加一个敌人
		GameManager.Instance.Enemys.Add(this.GetComponent<Enemy>());
		//查找UI
		Transform mUiRoot=GameObject.Find("UIManager").transform;
		//计算血条位置
		Vector3 mPos=this.transform.FindChild("EnemyHP").transform.position;
		//mPos=Camera.main.WorldToViewportPoint(mPos);
		mPos.z=-5;
		//生成血条
		GameObject go=(GameObject)Instantiate(HPBar,mPos,Quaternion.identity);
		//使血条成为Canvas的子物体
		go.transform.parent=mUiRoot;
		//对血条进行放缩
		go.GetComponent<RectTransform>().localScale=new Vector3(0.5F,0.30F,1);
		//获取Slider
		mHPBar=go.transform.GetComponent<Slider>();
	}

	void Move()
	{
		Vector3 mPos1=this.transform.position;
		Vector3 mPos2=this.StartNode.transform.position;
		//计算敌人与路径节点间的距离
		float mDis=Vector2.Distance(new Vector2(mPos1.x,mPos1.y),new Vector2(mPos2.x,mPos2.y));
		if(mDis<0.1F){
			if(StartNode.ThatNode==null){
				//对防守阵地进行摧毁
				GameManager.Instance.PlayerHP-=20;
				//从敌人列表中移除自身
				GameManager.Instance.Enemys.Remove(this);
				//销毁自身
				Destroy(this.gameObject);
				//销毁血条
				Destroy(mHPBar.gameObject);
			}else{
				StartNode=StartNode.ThatNode;
			}
		}
		//计算敌人的移动方向
		Vector3 mDir=new Vector3(mPos2.x-mPos1.x,mPos2.y-mPos1.y,0).normalized;
		transform.Translate(mDir * MoveSpeed * Time.deltaTime);
	} 

	void Rotate()
	{
		//初始角度
		float mStartAngle=this.transform.eulerAngles.z;
		transform.LookAt(StartNode.transform);
		//目标角度
		float mTargetAngle=this.transform.eulerAngles.z;
		//计算旋转量
		float mAngle=Mathf.MoveTowardsAngle(mStartAngle,mTargetAngle,RotateSpeed *Time.deltaTime);
		this.transform.eulerAngles = new Vector3(0,0,mAngle);
	}

	void Update () 
	{
		Move();
		UpdateHPBar();
	}

	private void UpdateHPBar()
	{
		//更新血条位置
		Vector3 mPos=this.transform.FindChild("EnemyHP").transform.position;
		//使血条位于顶层
		mPos.z=-5;
		mHPBar.transform.position=mPos;
		//更新血量
		mHPBar.value=(float)HP/MaxHP;
	}

	public void SetDamage(int mValue)
	{
		HP-=mValue;
		if(HP<=0){
		  Destroy(this.gameObject);
		  Destroy(mHPBar.gameObject);
		  GameManager.Instance.Enemys.Remove(this.GetCopmonent<Enemy>());
		}
	}
}
```
在这里我们做了三件事情：
*   第一，在Awake方法中我们首先计算出血条的位置然后在这个位置生成血条，并取得相关的变量备用。
*   第二，在Update方法中增加一个UpdateHPBar方法以实现对血条血量的更新。
*   第三，增加了一个SetDamage方法，当敌人血量为0时销毁自身、销毁血条、从敌人列表中移除敌人

## 敌人按波次进攻的实现
好了，到现在为止，对于敌人的逻辑我们就全部实现了。可是我们知道在塔防游戏中敌人通常是一波一波出现的，所以我们需要一个敌人生成器EnemySpawn。那么，怎么来生成敌人呢，这里我们使用Xml文件来配置要生成的敌人列表，首先我们来构建一个Xml文件：
```
<?xml version="1.0" encoding="utf-8" standalone="yes"?>
<Enemies>
	<Enemy Wave="1" EnemyName="Enemy" Level="1" Wait="0.5"/>
	<Enemy Wave="2" EnemyName="Enemy" Level="2" Wait="0.45"/>
	<Enemy Wave="2" EnemyName="Enemy" Level="2" Wait="0.45"/>
	<Enemy Wave="3" EnemyName="Enemy" Level="3" Wait="0.4"/>
	<Enemy Wave="3" EnemyName="Enemy" Level="3" Wait="0.4"/>
	<Enemy Wave="3" EnemyName="Enemy" Level="3" Wait="0.4"/>
	<Enemy Wave="4" EnemyName="Enemy" Level="4" Wait="0.35"/>
	<Enemy Wave="4" EnemyName="Enemy" Level="4" Wait="0.35"/>
	<Enemy Wave="4" EnemyName="Enemy" Level="4" Wait="0.35"/>
	<Enemy Wave="4" EnemyName="Enemy" Level="4" Wait="0.35"/>
	<Enemy Wave="5" EnemyName="Enemy" Level="5" Wait="0.3"/>
	<Enemy Wave="5" EnemyName="Enemy" Level="5" Wait="0.3"/>
	<Enemy Wave="5" EnemyName="Enemy" Level="5" Wait="0.3"/>
	<Enemy Wave="5" EnemyName="Enemy" Level="5" Wait="0.3"/>
	<Enemy Wave="5" EnemyName="Enemy" Level="5" Wait="0.3"/>
	<Enemy Wave="6" EnemyName="Enemy" Level="99" Wait="0.15"/>
</Enemies>
```
从这个Xml文件中我们可以看到这样一个结构：
```C#
using UnityEngine;
using System.Collections;
using System.Collections.Generic;
using System.Xml;


public class SpawnData 
{
	//敌人进攻波数
	public int Wave;
	///敌人名称，我们将根据这个名称来生成不同的敌人
	public string EnemyName;
	//敌人等级，我们将根据这个值来调整敌人的生命值和移动速度
	public int Level;

	public float Wait;
}
```
在SpawnData这个结构中，我们可以得到敌人攻击的波数、敌人的名称、敌人等级、敌人生成需要等待的时间，因为博主在游戏中只有一种敌人，所以敌人的名称都是一样的。好了，现在我们可以开始解析Xml了：
```C#
//解析Xml文件
void ReadXml()
{
	//创建一个字典以存储敌人列表
	mEnemyDatas=new List<SpawnData>();
	//加载Xml文档
	XmlDocument mDocument=new XmlDocument();
	mDocument.LoadXml(ConfigFile.text);
	XmlElement mRoot=mDocument.DocumentElement;
	//解析Xml文档
	XmlNodeList mNodes=mRoot.SelectNodes("/Enemies/Enemy");
	foreach(XmlNode mNode in mNodes)
	{
		//为每一个SpawnData赋值
		SpawnData mData=new SpawnData();
		mData.Wave=int.Parse(mNode.Attributes[0].Value);
		mData.EnemyName=mNode.Attributes[1].Value;
		mData.Level=int.Parse(mNode.Attributes[2].Value);
		mData.Wait=float.Parse(mNode.Attributes[3].Value);

		mEnemyDatas.Add(mData);
	}
}
```
那么好了，在解析完Xml后我们得到了所有的敌人数据，接下来我们只需要按照顺序生成敌人就可以了。具体怎么做呢，我们知道在塔防游戏中生成敌人有两种情况：
*   一个是要生成的敌人和当前敌人是同一波的，这种情况只要继续生成就好了。
*   一个是要生成的敌人的波数大于当前波数，这种情况需要等待这一波敌人被消灭完。

好了，现在来写代码：
```C#
using UnityEngine;
using System.Collections;
using System.Collections.Generic;
using System.Xml;

public class EnemySpawn : MonoBehaviour {

	//敌人寻路起点
	public PathNode SpawnPath;
	//敌人预制件
	public GameObject Enemy;
	//Xml文件
	public TextAsset ConfigFile;

	//存放敌人的数组
	private List<SpawnData> mEnemyDatas;

	//当前敌人进攻波数
	private int mWave=0;
	//当前敌人索引
	private int mIndex=0;
	//当前等待的时间
	private float mWait;

	void Start()
	{
		//读取Xml数据
		ReadXml();
		Debug.Log(mEnemyDatas.Count);
		//初始化攻击波数
		SpawnData mData=mEnemyDatas[mIndex];
		//设置攻击波数和等待时间
		mWave=mData.Wave;
		mWait=mData.Wait;
		GameManager.Instance.AttackWave=mWave;
		//生成第一个敌人
		CreateEnemy(mData);
		mIndex+=1;
	}

	void CreateEnemy(SpawnData mData)
	{
		GameObject go=(GameObject)Instantiate(Enemy,SpawnPath.transform.position,Quaternion.identity);
		Enemy _Enemy=go.GetComponent<Enemy>();
		//根据Level计算敌人的生命值和移动速度
		_Enemy.MaxHP= (float)mData.Level*0.25F * 100;
		_Enemy.HP= (float)mData.Level*0.25F * 100;
		go.GetComponent<Enemy>().MoveSpeed=(float)mData.Level * 0.15F;
		go.GetComponent<Enemy>().StartNode=SpawnPath;
	}

	void Update () 
	{
	   if(mIndex<=mEnemyDatas.Count-1){
	     SpawnEnemy();
	   }else
		{
			//当索引数目大于敌人列表中的数目时，表示所有敌人以及生成完毕，此时
			//如果所有的敌人都被消灭，则表示玩家获胜。
			if(GameManager.Instance.Enemys.Count==0){
				GameManager.Instance.IsWin=true;
				Debug.Log("玩家胜");
			}
		}
	}

	private void SpawnEnemy()
	{
		//取得下一个生成的敌人的数据
		SpawnData mData=mEnemyDatas[mIndex];

		//开始计时
		mWait-=Time.deltaTime;
		if(mWait<=0 ){
			//如果当前是同一波敌人，则继续生成敌人
		    if(mWave==mData.Wave){
			   //设置等待时间
			   mWait=mEnemyDatas[mIndex].Wait;
			   //设置进攻波数
			   mWave=mEnemyDatas[mIndex].Wave;
			   GameManager.Instance.AttackWave=mWave;
			   //生成一个敌人
			   if(mData!=null){
			   CreateEnemy(mData);
			   }
			   mIndex+=1;
			}//如果是下一波敌人，则需要等待这一波敌人全部死亡后再生成
			else if(mWave<mData.Wave && GameManager.Instance.Enemys.Count==0){
				//设置等待时间
				mWait=mData.Wait;
				//设置进攻波数
				mWave=mData.Wave;
				GameManager.Instance.AttackWave=mWave;
				//生成一个敌人
				CreateEnemy(mData);
				mIndex+=1;
			}
		}
	}

	//解析Xml文件
	void ReadXml()
	{
		//创建一个字典以存储敌人列表
		mEnemyDatas=new List<SpawnData>();
		//加载Xml文档
		XmlDocument mDocument=new XmlDocument();
		mDocument.LoadXml(ConfigFile.text);
		XmlElement mRoot=mDocument.DocumentElement;
		//解析Xml文档
		XmlNodeList mNodes=mRoot.SelectNodes("/Enemies/Enemy");
		foreach(XmlNode mNode in mNodes)
		{
			//为每一个SpawnData赋值
			SpawnData mData=new SpawnData();
			mData.Wave=int.Parse(mNode.Attributes[0].Value);
			mData.EnemyName=mNode.Attributes[1].Value;
			mData.Level=int.Parse(mNode.Attributes[2].Value);
			mData.Wait=float.Parse(mNode.Attributes[3].Value);

			mEnemyDatas.Add(mData);
		}
	}
}
```
我们可以注意到，到现在为止敌人相关的内容博主都已经为大家讲解完了，这里博主和大家开了一个小玩笑，不知道大家有没有发现，在敌人的Xml配置文件中博主最后设计了一个等级为99级的敌人，哈哈，这个敌人在游戏中的特点大家要自己从代码中来探索了，大家可以按照博主的思路做出这个塔防游戏然后自己去试试看，相信大家会更加深刻地理解数值平衡的重要性吧！

# 防守单位篇
防守单位是塔防游戏中玩家可以支配和控制的一种资源，玩家通过合理地分布防守单位的位置来对玩家的防守阵地进行防御，当玩家的防守阵地被摧毁时玩家将无法继续部署防守单位。这就是防守单位在游戏中的主要作用。通常为了增加游戏的可玩性，游戏设计者往往会设计多种防守单位，在博主的这个小游戏中，我们只设计了一种防守单位，更多的防守单位的设计大家可以参考《保卫萝卜》和《植物大战僵尸》这两个游戏。好了，说了这么多，那么防守单位在整个塔防游戏中主要的作用是什么呢？答案就是防守，哈哈，这是一句不折不扣的废话。可是就是这样一句废话，却足以让我们知道防守单位需要对敌人进行自动攻击，这就要涉及到简单的AI算法了。好了，我们来看下面的脚本：
```C#
using UnityEngine;
using System.Collections;

public class Defender : MonoBehaviour {

	//目标敌人
	private Enemy mTarget;
	//攻击半径
	public float AttackArea=2.5F;
	//与敌人的距离
	private float mDistance=0;
	//防守单位的旋转速度
	public float RotateSpeed=1.5F;
	//防守单位攻击间隔
	public float AttakTime=2.5F;
	//防守单位攻击间隔
	private float mTime=0.0F;

	//炮弹预设
	public GameObject BulletObject;

	void Start () 
	{
		//初始化防守单位攻击间隔
		mTime=AttakTime;
	}

	//查找攻击范围内的敌人
	void FindEnemy()
	{
		//初始化目标敌人
		mTarget=null;
		//获取敌人列表
		ArrayList mEnemys=GameManager.Instance.Enemys;
		//遍历每个敌人
		foreach(Enemy _enemy in mEnemys)
		{
			//忽略生命值为0的敌人
			if(_enemy.HP==0) continue;
			//计算防守单位与敌人间的距离
			Vector3 mPos1=transform.position;
			Vector3 mPos2=_enemy.transform.position;
			float mDis=Vector2.Distance(new Vector2(mPos1.x,mPos1.y),new Vector2(mPos2.x,mPos2.y));
			if(mDis>AttackArea){
				//Debug.Log("敌人" + _enemy.transform.name + "未进入攻击范围,距离为:" + mDis);
				//return;
			}else{
				//Debug.Log("敌人" + _enemy.transform.name + "已进入攻击范围,距离为:" + mDis);
				//选择最近的敌人
				if(mDistance==0 || mDistance > mDis){
					mTarget=_enemy;
					mDistance=mDis;
				}

				/*//选择生命值最低的敌人
				if(mLife==0 || mLife > _enemy.HP){
					mTarget=_enemy;
					mLife=_enemy.HP;
				}
				*/
			}
		}
		mDistance=0;
	}

	void RotateTo()
	{
		//判断目标敌人是否为空
		if(mTarget==null) return;
		//计算要旋转到敌人方向的角度
		Vector3 mPos1=this.transform.position;
		Vector3 mPos2=mTarget.transform.position;
		Vector3 mDir=(mPos2-mPos1).normalized;
		//使得两向量共面
		mDir.z=0;
		//计算两向量角度
		float mAngle=getAngle(Vector3.up,mDir);
		this.transform.eulerAngles=new Vector3(0,0,mAngle) * RotateSpeed;

	}

	//根据向量数学计算角度
	private float getAngle(Vector3 v1,Vector3 v2)
	{
		float mDot=Vector3.Dot(v1,v2);
		float mv1=Mathf.Sqrt(v1.x*v1.x+v1.y*v1.y+v1.z*v1.z);
		float mv2=Mathf.Sqrt(v2.x*v2.x+v2.y*v2.y+v2.z*v2.z);
		if(v2.x>v1.x){
			return -Mathf.Acos(mDot/(mv1*mv2))* Mathf.Rad2Deg ;
		}else{
			return Mathf.Acos(mDot/(mv1*mv2))* Mathf.Rad2Deg ;
		}
	}

	void Attack()
	{
		RotateTo();
		if(mTarget==null) return;
		//以下添加攻击逻辑
		mTime-=Time.deltaTime;
		if(mTime<0){
			Vector3 _angle=transform.Find("Bullet").eulerAngles;
			Vector3 _pos=new Vector3(this.transform.position.x,this.transform.position.y,-2);
			Instantiate(BulletObject,_pos,Quaternion.Euler(_angle));
			mTime=AttakTime;
		}
	}

	void Update () 
	{
		FindEnemy();
		Attack();
	}


}

```
防守单位的脚本定义在Defender这个类中，主要的行为有两个，即发现敌人后转向敌人、向敌人发射炮弹，这块的代码较为简单，大家自己去领会就好啦。我们知道在塔防游戏中玩家可以通过点击屏幕来自由地增加或移动防守单位，这部分的内容主要是和GUI相关的，因为目前博主对UGUI掌握地还不是很熟，所以就等以后博主有时间了再来补充吧！好了，这个塔防游戏的讲解教程就是这样了，希望大家能够喜欢，我知道大家等这篇下篇已经好久了，哈哈！
<img src="http://img.blog.csdn.net/20150301190040972" alt="效果演示"/>
最后想说的是，博主的独立博客[http://qinyuanpei.github.io](http://qinyuanpei.github.io)正式开始使用了，以后发表的文章会在独立博客和CSDN同时更新，希望大家能继续关注博主的博客！谢谢大家