---
abbrlink: 3019914405
categories:
- 游戏开发
date: 2015-10-13 12:59:01
description: 注意到DrawRotate()方法与DrawPositin()及DrawScale()方法在实现方式上略有不同，这是因为Transform组件的Rotation属性是一个Quaternion即四元数的结构，四元数是利用x、y、z、w四个数值来表示物体的三维旋转，这不仅和我们平时习惯的欧拉角相违背而且更为关键的是貌似目前我还没有发现可以直接绘制四元数的API接口，如果有的话希望大家可以告诉我，所以这里我们用了变通的一种方法，即通过Transform的eulerAngles来实现，但是这种方式绘制的属性框大小和EditorGUILayout.PropertyField()方法绘制的属性框大小并不一致，同时我们需要自己去完成属性值的更新;此时如果我们给场景中的某个物体附加上该脚本，则我们在Inspector窗口可以看到Example类的实例Example将被序列化到编辑器面板中，同时我们可以注意到私有的editable字段并没有被序列化出来，这是因为**在Unity3D中，公有的字段默认支持序列化，私有的字段除非显式的增加[SerializeField]标记，否则都不会被序列化**，这一点希望大家注意;在第一个示例中，可以注意到我们使用了FindProperty()方法来获取一个可序列化物体的属性(字段)，然后我们在EditorGUILayout.PropertyField()方法来绘制了各种属性框，这种方式可以实现属性的自动更新
tags:
- 编辑器
- 扩展
- Unity3D
title: Unity3D游戏开发之Unity3D场景编辑器扩展开发
---

&emsp;&emsp;今天博主想和大家分享的是Unity3D场景编辑器的扩展开发，相关的话题我们在[Unity3D游戏开发之编辑器扩展程序开发实例](http://localhost:4000/2015/03/31/unity3d-plugins-development-application-case/)这篇文章中我们已经有所涉及，今天博主想特别针对场景编辑器的扩展开发来进行下深入研究。对于一个场景编辑器来说，它主要的作用是3D场景视图中实时显示、输入反馈和相关信息的更新。在Unity3D中提供了Editor、EditorWindow、GUILayout、EditorGUILayout、GUIUtility、EditorGUIUtility、Handles、Event等来完成这些工作。其中基于EditorWindow的这种扩展方式我们已经研究过了，这种扩展方式拥有自己的独立窗口使用OnGUI方法进行界面的绘制。<!--more-->今天我们想说的是基于Editor的这种扩展方式，这种扩展方式只能针对脚本，从脚本内容在Inspector里的显示布局到变量在Scene视图的可视化编辑，它都可以完全胜任。这里特别想说的是Handles和Event这两个类，这两个类分别提供了3D显示和输入反馈的功能，我们下面就来学习如何使用这些类来扩展Unity3D的场景编辑器。

# 创建一个扩展的Transform组件
&emsp;&emsp;Transform是Unity3D中一个基本的组件，下面我们来创建一个扩展的Transform组件，该组件可以对游戏体的坐标、旋转、缩放进行重置。首先，我们创建一个ExtendTransform的类，该类继承自Editor类：
```
using UnityEngine;
using System.Collections;
using UnityEditor;

[CustomEditor(typeof(Transform),true)]
public class ExtendTransform : Editor 
{
    /// <summary>
    /// Position属性
    /// </summary>
    private SerializedProperty mPos;

    /// <summary>
    /// Scale属性
    /// </summary>
    private SerializedProperty mScale;

    void OnEnable()
    {
        mPos = serializedObject.FindProperty("m_LocalPosition");
        mScale = serializedObject.FindProperty("m_LocalScale") ;
    }

    /// <summary>
    /// Inspector相关GUI函数
    /// </summary>
    public override void OnInspectorGUI()
    {
        EditorGUIUtility.labelWidth = 15;
        //获取最新的可序列化对象
        serializedObject.Update();
        //绘制物体的坐标、旋转和缩放
        DrawPosition();
        DrawRotate();
        DrawScale();
        //更新可序列化对象的属性
        serializedObject.ApplyModifiedProperties();
    }

    /// <summary>
    /// 绘制位置
    /// </summary>
    private void DrawPosition()
    {
        GUILayout.BeginHorizontal();
        {
            bool Reset = GUILayout.Button("P", GUILayout.Width(20f));
            EditorGUILayout.LabelField("Position");
            EditorGUILayout.PropertyField(mPos.FindPropertyRelative("x"));
            EditorGUILayout.PropertyField(mPos.FindPropertyRelative("y"));
            EditorGUILayout.PropertyField(mPos.FindPropertyRelative("z"));
            if(Reset) mPos.vector3Value = Vector3.zero;
        }
        GUILayout.EndHorizontal();
    }

    /// <summary>
    /// 绘制旋转
    /// </summary>
    private void DrawRotate()
    {
        Vector3 eulerAngles = ((Transform)target).eulerAngles;
        GUILayout.BeginHorizontal();
        {
            bool Reset = GUILayout.Button("R", GUILayout.Width(20f));
            EditorGUILayout.LabelField("Rotation", GUILayout.Width(70f));
            EditorGUILayout.LabelField("X", GUILayout.Width(13f));
            float angleX=EditorGUILayout.FloatField(eulerAngles.x, GUILayout.Width(56f));
            EditorGUILayout.LabelField("Y", GUILayout.Width(13f));
            float angleY = EditorGUILayout.FloatField(eulerAngles.y, GUILayout.Width(56f));
            EditorGUILayout.LabelField("Z", GUILayout.Width(13f));
            float angleZ = EditorGUILayout.FloatField(eulerAngles.z, GUILayout.Width(56f));
            ((Transform)target).eulerAngles = new Vector3(angleX, angleY, angleZ);
            if(Reset)
            {
                eulerAngles = Vector3.zero;
                ((Transform)target).eulerAngles = Vector3.zero;
            }
        }
        GUILayout.EndHorizontal();
    }

    /// <summary>
    /// 绘制缩放
    /// </summary>
    private void DrawScale()
    {
        GUILayout.BeginHorizontal();
        {
            bool Reset = GUILayout.Button("S", GUILayout.Width(20f));
            EditorGUILayout.LabelField("Scale");
            EditorGUILayout.PropertyField(mScale.FindPropertyRelative("x"));
            EditorGUILayout.PropertyField(mScale.FindPropertyRelative("y"));
            EditorGUILayout.PropertyField(mScale.FindPropertyRelative("z"));
            if (Reset) mScale.vector3Value = Vector3.one;
        }
        GUILayout.EndHorizontal();
    }
}
```
&emsp;&emsp;首先我们注意到ExtendTransform继承自Editor，这是我们开发这类编辑器扩展的第一个前提。其次我们注意到在该类的声明位置有这样一个标记:
```
[CustomEditor(typeof(Transform),true)]
```
该标记表明我们这个编辑器扩展是针对Transform组件进行扩展的，即当物体存在Tranform组件时会在编辑器中响应这个编辑器扩展程序。我们在这个编辑器扩展程序中都做了哪些事情呢？第一，我们实现了OnEnable()方法，该方法相当于一个初始化的方法；第二，我们重写了OnOnInspectorGUI()方法，该方法将覆盖默认的Inspector窗口外观。

![扩展后的Transform](https://ww1.sinaimg.cn/large/None.jpg)

好了，现在我们点击场景中默认的相机MainCamera可以发现默认的Transform会变成具有重置功能的扩展型Transform。下面我们来介绍这段程序中较为重要的核心内容：
## Unity3D中的可序列化对象
&emsp;&emsp;通常我们所说的序列化是指将一个对象的实例转化为字符串的过程，而在Unity3D中可序列化对象更像是一种智能对象，它可以将脚本中的属性显示在Inspector窗口中，当场景发生变化时这些属性值将自动被更新。例如我们可以定义这样一个简单的脚本：
```
/// <summary>
/// 定义一个可序列化类
/// </summary>
[System.Serializable]
public class ExampleClass 
{
    [SerializeField]
    public int ID;
    [SerializeField]
    public string Name;
    [SerializeField]
    public Vector3[] Points;

    private bool editable = false;
}

/// <summary>
/// 定义一个简单的脚本
/// </summary>
public class ExampleScript : MonoBehaviour 
{
    public ExampleClass Example;
}
```
此时如果我们给场景中的某个物体附加上该脚本，则我们在Inspector窗口可以看到Example类的实例Example将被序列化到编辑器面板中，同时我们可以注意到私有的editable字段并没有被序列化出来，这是因为**在Unity3D中，公有的字段默认支持序列化，私有的字段除非显式的增加[SerializeField]标记，否则都不会被序列化**，这一点希望大家注意。好了，那么我们为什么要讲这部分内容呢，这是因为它和我们下面要讲的**Editor基类中的属性和方法**有着十分密切的关联。

![Unity3D中的可序列化对象](https://ww1.sinaimg.cn/large/None.jpg)

## Editor基类中的属性和方法
&emsp;&emsp;Editor基类中有两个重要的属性，即target和serializedObject。target表示当前受检查的物体我们可以通过它获得当前物体；而serializedObject表示当前物体的全部可序列化信息，我们可以通过它获得指定的序列化字段及其数值。Editor基类中重要的方法有：
* OnInspectorGUI():该方法可对Inspector窗口面板进行扩展或者重写，比如我们可以通过DrawDefaultInspector()方法来绘制默认Inspector窗口面板然后在此基础上使用GUILayout或者EditorGUILayout等辅助类进行自定义的绘制。在这个示例中我们对整个面板进行了重写，值得注意的是为了让Inspector窗口面板正常工作，如果要重绘该窗口请确保对该方法进行覆盖。
* OnSceneGUI():该方法可对场景视图进行绘制，在实际的使用中可以配合Handles类和Event类来进行网格编辑、地形绘制或高级Gizmos等方面的工作。在本文的第二个示例中，我们将利用这一特性来编写一个用于NPC寻路的路径节点编辑工具。

##对第一个示例的总结
&emsp;&emsp;在第一个示例中，可以注意到我们使用了FindProperty()方法来获取一个可序列化物体的属性(字段)，然后我们在EditorGUILayout.PropertyField()方法来绘制了各种属性框，这种方式可以实现属性的自动更新。注意到DrawRotate()方法与DrawPositin()及DrawScale()方法在实现方式上略有不同，这是因为Transform组件的Rotation属性是一个Quaternion即四元数的结构，四元数是利用x、y、z、w四个数值来表示物体的三维旋转，这不仅和我们平时习惯的欧拉角相违背而且更为关键的是貌似目前我还没有发现可以直接绘制四元数的API接口，如果有的话希望大家可以告诉我，所以这里我们用了变通的一种方法，即通过Transform的eulerAngles来实现，但是这种方式绘制的属性框大小和EditorGUILayout.PropertyField()方法绘制的属性框大小并不一致，同时我们需要自己去完成属性值的更新。好了，暂时先总结到这里更多的细节大家可以通过代码来了解。

#创建一个NPC寻路节点编辑工具
&emsp;&emsp;创建这样一个工具的想法来自我实际的工作体验，当我Unity3D中使用的Tween动画库从iTween变成Dotween后，我在使用Dotween的过程中一直没有找到类似于iTweenPath的路径节点编辑工具。作为一个有节操的程序员，去寻找破解版的Dotween Pro这样的事情我是能不干就不干啦，因为我觉得自己有能力做这样一个类似的小工具，所以在一边准备这篇文章的时候，一边开始设计这样一个路径节点编辑工具。相信经过第一个示例的铺垫和相关知识的储备，大家都了解了这些内容，所以这里直接给出代码啦，因为实在是没有多少内容，嘿嘿：
```
using UnityEngine;
using System.Collections;
using UnityEditor;

[CustomEditor(typeof(PatrolNPC))]
public class PatrolPathEditor : Editor 
{
    /// <summary>
    /// 寻路节点
    /// </summary>
    private Vector3[] paths;

    /// <summary>
    /// 显示寻路信息的GUI
    /// </summary>
    private GUIStyle style=new GUIStyle();

    /// <summary>
    /// 初始化
    /// </summary>
    void OnEnable()
    {
        //获取当前NPC的寻路路径
        paths = ((PatrolNPC)target).Paths;
        //初始化GUIStyle
        style.fontStyle = FontStyle.Normal;
        style.fontSize = 15;
    }


    void OnSceneGUI()
    {
        //获取当前NPC的寻路路径
        paths = ((PatrolNPC)serializedObject.targetObject).Paths;
        //设置节点的颜色为红色
        Handles.color = Color.red;
        if(paths.Length <= 0 || paths.Length<2) return;
        //在场景中绘制每一个寻路节点
        //可以在场景中编辑节点并将更新至对应的NPC
        for (int i = 0; i < paths.Length; i++)
        {
            paths[i] = Handles.PositionHandle(paths[i], Quaternion.identity);
            Handles.SphereCap(i, paths[i], Quaternion.identity, 0.25f);
            Handles.Label(paths[i], "PathPoint" + i, style);
            if (i < paths.Length && i + 1 < paths.Length)
            {
                Handles.DrawLine(paths[i], paths[i + 1]);
            }
        }
    }
    
}
```
&emsp;&emsp;这里的PatrolNPC是一个可寻路NPC类，基本和这篇文章的内容无关，大家只要知道那个Paths字段是一个Vector3[]就好啦，这样当我们在场景中编辑这些路径节点的时候，对应NPC的路径节点信息就会同步发生更新，这样我们就可以随心所欲地规划NPC的移动路径啦，哈哈。好了，今天的内容就是这样啦，写完熬到这个点真心不容易啊，大家晚安，这是这个小工具在场景编辑器中的效果，嘻嘻，感觉还是蛮不错的吧，反正我是很喜欢就对啦！

![路径节点编辑工具演示](https://ww1.sinaimg.cn/large/4c36074fly1fz68jsnh8kj20nn0hrnnk.jpg)