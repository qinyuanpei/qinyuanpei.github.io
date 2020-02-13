---
abbrlink: 70687890
categories:
- 游戏开发
date: 2015-03-31 00:53:22
description: 开发Unity3D编辑器扩展程序的命名空间主要是UnityEditor，在该命名空间下常用的类有EditorGUI、EditorGUILayout、EditorWindow(可能还有其它的类，不过到目前为止博主就用过这些，如果有其它的类，欢迎大家来补充啊)
tags:
- Unity3D
- 编辑器
- 扩展
title: Unity3D游戏开发之编辑器扩展程序开发实例
---

&emsp;&emsp;各位朋友大家好，欢迎关注我的博客，我的博客地址是[http://www.qinyuanpei.com](http://www.qinyuanpei.com)。今天我们来说说如何在Unity3D中为编辑器开发扩展程序。提到扩展程序，相信大家都不会陌生了。不管是Google的Chrome浏览器还是经典的FireFox，这些浏览器最为人所称道的就是它支持各种各样的扩展。扩展程序是一种插件，它遵循插件式设计的原则，可以随时在宿主程序中安装、卸载而不会影响宿主程序的正常运行。我们知道在Unity3D中有各种各样的插件，如NGUI、2DToolKit、EasyTouch等等都是一种扩展程序。扩展程序在丰富宿主程序功能的基础上，可以帮助宿主程序完成大量额外的工作。可以说正是因为Unity3D拥有大量的插件和资源支持，Unity3D才能够受到大家如此的追捧。可是作为一个有节操的程序员，如果仅仅会使用工具，那么我们和普通用户有什么区别啊，所以在今天的文章中博主将通过三个具体的实例来教大家如何为Unity3D的编辑器开发扩展程序，希望对大家学习Unity3D技术有所帮助！

<!--more-->

# 常用的命名空间和类
&emsp;&emsp;开发Unity3D编辑器扩展程序的命名空间主要是UnityEditor，在该命名空间下常用的类有EditorGUI、EditorGUILayout、EditorWindow(可能还有其它的类，不过到目前为止博主就用过这些，如果有其它的类，欢迎大家来补充啊)。为Unity3D编辑器开发的扩展程序同样是一种脚本，通常需要将脚本文件放在项目资源文夹下的Editor文件夹中，即Assets/Editor。不过该脚本不再继承自MonoBehaviour，具体的内容我们会放到后面的实例中来讲Unity3D编辑器扩展程序的形式通常有两种，一种是没有界面的(如案例1)、一种是有界面的(如案例2、案例3)。对于没有界面的这种扩展程序，我们只需要定义一个类(无需继承任何父类)然后再这个类中定义一个静态的方法就可以了;而对于有界面的这种扩展程序，我们需要让定义的这个类继承EditorWindow并实现OnGUI()方法,因为在OnGUI()方法中我们将会对扩展程序的界面进行绘制，不过无需担心啦，因此扩展程序的界面绘制和Unity3D脚本中的OnGUI()方法是相似的，我们要做的就是要熟悉常见的控件。好了，下面进入今天的实战环节，大家准备好了吗？
# Unity3D编辑器扩展程序开发实例
## 案例1 快速修改贴图类型
&emsp;&emsp;Unity3D4.6版本的一个重要更新就是UGUI和Unity2D的支持，因为有了对Unity2D的支持，所以Unity3D的贴图类型就增加了一个Sprite的类型。如果导入到Unity3D中的贴图是那种打好的小图的图集，那么Unity3D能够自动识别为Sprite类型。可是对于那种单张的贴图，Unity3D默认还是按照默认的设置来处理，因此如果每次需要用到这些图片，就必须手动地将其TextureType设为sprite，如果贴图数量比较少，那么手动修改也没有什么了。可是如果项目中的贴图数量较多的话，这样一张一张地去调整TextureType可能会浪费大量的时间啊！怎么办呢？简单！写代码！
```C#
using UnityEngine;
using UnityEditor;
using System.Collections;

public class ImportSprite
{
    /// <summary>
    /// 批量将贴图格式转换为Sprite
    /// </summary>
    [MenuItem("Tools/ConvertToSprite")]
    static void ConvertToSprite()
    {
        //获取所有被选中的物体
        Object[] selection=(Object[])Selection.objects;
        //合法性处理
        if(selection.Length==0) return;
        //批量导入贴图
        foreach(Object obj in selection)
        {
            //取得每一张贴图
            Texture texture=(Texture)obj;
            //获得贴图路径
            string localpath=AssetDatabase.GetAssetPath(texture);
            //贴图导入
            TextureImporter importer=(TextureImporter)AssetImporter.GetAtPath(localpath);
            //设置贴图类型
            importer.textureType=TextureImporterType.Sprite;
            //导入项目资源
            AssetDatabase.ImportAsset(localpath);
        }
        //刷新项目资源
        AssetDatabase.Refresh();
    }
}
```
&emsp;&emsp;我们将这个脚本放到Editor文件夹中，如果不出现什么意外的话，Unity3D的菜单栏中会增加一个Tools的菜单项，该菜单项目前只有一个子菜单项ConvertToSprite。好了，现在我们要做的事情就是在项目资源文件夹中选中要转换成sprite类型的贴图，然后单击Tools->ConvertToSprite。很快(具体有多快可以自己在编辑器窗口中去尝试，总之就是很快就对了，哈哈)所有的贴图的都如我们所愿地被转换成了sprite类型，此时此刻你有没有懊悔当年手动创建的92个空物体，反正博主是后悔当初做塔防游戏的时候手动创建了92个空物体，如果那个时候我知道Unity3D可以做这些事情，我打死都不会手动去创建92个空物体的，现在想想都佩服当时自己的勇气啊。好了，作为第一个编辑器扩展程序，我们稍微总结下主要的内容：
* 在Unity3D中我们可以通过TextureImporter、ModelImporter、AudioImporter、MovieImporter等来分别向Unity3D中导入贴图、模型、音频、视频等等，经过设置后最终通过AssetDatabase.ImportAsset()来将其添加到项目中热完全，最后需要使用AssetDatabase.Refresh()方法来刷新本地资源，使导入的资源生效。
* Selection.objects取得的物体无法区分是从场景中选取的还是从项目资源文件夹中选取的，如果需要从场景中来选取，建议使用Selection.transforms来代替。
## 案例2 动态生成Prefab
&emsp;&emsp;首先让我们来回顾一下大家平时制作Prefab的流程：
* 在项目资源文件夹中选取素材拖放到场景中
* 在场景中调整名称、位置、缩放、组件等等
* 将物体拖放到Prefabs文件夹下生成Prefab
尽管这是Unity3D官方推荐的一种做法，可是如果我们现在有大量的Prefab要制作怎么办呢？一个最直观的例子就是游戏里的敌人。在一个中等规模的游戏中，敌人的种类通常很多，而且每一个敌人的行为可能都不相同。然后从宏观的角度来看，敌人的大部分特征都是相同的，因此我们这里考虑使用程序动态生成Prefab，这里假定Prefab不需要附加脚本，因为如何给Prefab附加脚本博主还没有研究出来。好了，下面我们来看代码：
```C#
using UnityEngine;
using UnityEditor;
using System.Collections;

public class PrefabWrap : EditorWindow {

    //预设物体名称
    private string prefabName;
    //预设物体tag
    private static string prefabTag;
    //预设物体Layer
    private static int  prefabLayer;
    //当前插件窗口实例
    private static PrefabWrap instance;
    
    /// <summary>
    /// 显示插件窗口
    /// </summary>
    [MenuItem("Tools/PrefabWrapTool")]
    static void PrefabWrapTool()
    {
        //获取当前窗口实例
        instance=EditorWindow.GetWindow<PrefabWrap>();
        //显示窗口
        instance.Show();
    }

    /// <summary>
    /// 在OnGUI方法中实现界面定制
    /// </summary>
    private void OnGUI()
    {
        //绘制一个文本框
        prefabName=EditorGUILayout.TextField("预设物体名称:",prefabName);
        //绘制预设物体标签选择框
        prefabTag=EditorGUILayout.TagField("预设物体tag:",prefabTag);
        //绘制预设物体层级选择框
        prefabLayer=EditorGUILayout.LayerField("预设物体Layer:",prefabLayer);
        //绘制一个按钮
        if(GUILayout.Button("生成预设物体",GUILayout.Height(20)))
        {
            if(prefabName!=string.Empty)
            {
                CreatePrefab(prefabName);
            }
        }
    }

    /// <summary>
    /// 批量创建Prefab
    /// </summary>
    static void CreatePrefab(string name)
    {
        //获取所有被选中的物体
        Object[] selection=(Object[])Selection.objects;
        //合法性处理
        if(selection.Length==0) return;
        //批量处理
        foreach(Object obj in selection)
        {
            //生成预设
            GameObject prefab=(GameObject)PrefabUtility.CreatePrefab("Assets/Prefabs/"+name+".prefab",(GameObject)obj);
            //设置tag和Layer
            prefab.tag=prefabTag;
            prefab.layer=prefabLayer;
            //导入项目
            AssetDatabase.ImportAsset(AssetDatabase.GetAssetPath(prefab));
        }
        //刷新本地资源
        AssetDatabase.Refresh();
    }

    //当界面发生变化时重绘
    void OnInspectorUpdate() 
    {
        Repaint();
    }
}
```
&emsp;&emsp;首先我们让这个脚本继承自EditorWindow，这样它将在Unity3D中显示一个窗口。在OnGUI()方法中我们定义了窗口需要绘制的内容为一个文本框、两个选择框和一个按钮，当单击按钮后会执行CreatePrefab()方法。当界面发生变化的时候，需要对窗口进行重绘。最终的程序演示效果如下：

![动态生成Prefab效果演示](https://ww1.sinaimg.cn/large/4c36074fly1fyzcvrvdgej20kx0ejaak.jpg)

&emsp;&emsp;当我们在场景中选择好物体后，只要填好预设物体的名称、tag、Layer就可以直接生成Prefab了，不过这里有个问题，因为生成Prefab必须要传入一个GameObject，因此如果直接选择项目资源文件夹里的内容可能会报错，因为你选择的不是一个GameObject。博主做这样一个功能的初衷原本是想直接为每一个精灵图片生成预设文件，现在看来需要寻找其它的方法了，不过基本思路是创建一个空物体，然后向这个空物体中增加子物体，如果大家对此有兴趣的话，可以结合本文的方法自行去尝试。
## 案例3 快速为Sprite设置图集tag
&emsp;&emsp;接下来这个案例呢，同样是和贴图有关的内容。我们知道在没有UGUI以前，我们使用NGUI的时候要做的第一件事情就是把要用到的贴图打成图集，现在在Unity3D里面我们可以通过贴图的Packing Tag来实现图集打包，就是说具有相同Packing Tag的物体会被打到一张大图上，这样做的好处是节省资源。如果大家对这部分内容不太熟悉，可以了解下我的这篇文章[]()。既然明白了原理，那么我们为什么不来尝试着通过程序将这件事情一次完成呢？好了，直接给出代码：
```C#
using UnityEngine;
using UnityEditor;
using System.Collections;

public class PackageTools : EditorWindow 
{
    /// <summary>
    /// 图集标签    
    /// </summary>
    private string tagName;
    /// <summary>
    /// 当前实例
    /// </summary>
    private static PackageTools instance;

    /// <summary>
    /// 在OnGUI方法中实现界面定制
    /// </summary>
    private void OnGUI()
    {
        //绘制一个文本框
        tagName=EditorGUILayout.TextField("PackageTagName:",tagName);
        //绘制一个按钮
        if(GUILayout.Button("Package",GUILayout.Height(20)))
        {
            if(tagName!=string.Empty)
            {
                PackgeTextureWidthTag(tagName);
            }
        }
    }

    /// <summary>
    /// 显示插件窗口
    /// </summary>
    [MenuItem("Tools/ShowPackageTools")]
    static void ShowPackageTools()
    {
        //获取当前窗口实例
        instance=EditorWindow.GetWindow<PackageTools>();
        //显示窗口
        instance.Show();
    }

    /// <summary>
    /// 快速为图片生成图集
    /// </summary>
    static void PackgeTextureWidthTag(string tagName)
    {
        //获取所有被选中的物体
        Object[] selection=(Object[])Selection.objects;
        //合法性处理
        if(selection.Length==0) return;
        //批量处理贴图
        foreach(Object obj in selection)
        {
            //取得每一张贴图
            Texture texture=(Texture)obj;
            //获得贴图路径
            string localpath=AssetDatabase.GetAssetPath(texture);
            //贴图导入
            TextureImporter importer=(TextureImporter)AssetImporter.GetAtPath(localpath);
            //判断贴图类型,只有贴图类型为Sprite且精灵类型为SpriteMode
            if(importer.textureType==TextureImporterType.Sprite)
            {
                importer.spritePackingTag=tagName;
                //导入项目资源
                AssetDatabase.ImportAsset(localpath);
            }
        }
        //刷新本地资源
        AssetDatabase.Refresh();
    }

    //当界面发生变化时重绘
    void OnInspectorUpdate() 
    {
        Repaint();
    }

}
```
&emsp;&emsp;因为打包图集只需要一个参数，因此这个打包工具只需要一个文本框和一个按钮，整个过程和案例2是一样的，这里就不做分析了。这个扩展程序的演示效果如下：

![图集打包效果演示](https://ww1.sinaimg.cn/large/4c36074fly1fyzcue77dpj20ky0e5weu.jpg)

&emsp;&emsp;好了，这就是今天的内容了，今天的内容基本上涵盖了为Unity3D开发扩展程序的基本内容，我们接下来要做的就是积极地在平时生活、工作和学习中寻找问题和解决问题，"授人以鱼不如授人以渔"，向他人传授知识和技能，这件事情本身对博主而言就是是快乐的，博主希望今天的内容大家能够喜欢。好了，谢谢大家！