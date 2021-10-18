---
abbrlink: 3653662258
categories:
- Unity3D
date: 2016-01-08 13:58:44
description: 现在解决了创建资源的问题，我们接下来只要调用 ProjectWindowUtil 的 StartNameEditingIfProjectWindowExists 方法即可，该方法需要传入一个继承自 EndNameEditAction 的类的实例、目标文件路径和模板文件的路径;好了，第二个参数作为一个验证的标志，如果该标志为 true，意味着我们定义的静态方法是一个验证方法在执行静态方法前会首先对方法进行验证，这个我们暂且不管，因为今天我们这个来自星星的黑科技主要和第三个参数有关，第三个参数表示一个优先级，它表示菜单项在菜单栏中的展示顺序，优先级大的菜单项会展示在优先级小的菜单项下面，由此我们就明白了了模板文件名中的类似 81、83 这样的数字的真实含义，注意到模板文件的排列顺序和编辑器中的菜单项顺序是一样的，我们做一个尝试，编写下面的代码：;Unity3D 默认的脚本模版位于/Editor/Data/Resources/ScriptTemplates/目录下，注意该目录相对 Unity3D 的安装目录而言，在这个目录中我们可以找到 Unity3D 中脚本模板的某些蛛丝马迹，首先，脚本模板是一个简单的文本文件，这个文本文件中预先填充了内容，我们在编辑器中创建模脚本或者 Shader 的时候实际上是读取这些文件然后在写入项目中的指定路径的
tags:
- Unity3D
- 编辑器
- 模板
title: 扩展 Unity3D 编辑器的脚本模板
---

最近在学习 Shader 时感觉 Shader 语言参数众多、语法诡异，如果每次都从头开始写 Shader 一定是一件痛苦的事情。如果可以在本地定义好一组标准的 Shader 模板，这样当我们需要实现某些效果类似的 Shader 时，就可以在这个 Shader 模板的基础上进行修改。因为 Shader 文件是一个文本文件，所以我们可以非常容易地创建这样一个模板，在这个模板中我们可以进一步完善相关的参数注释，这样就不用每次写 Shader 的时候都需要查文档了，从这个角度出发，就进入了这篇文章的正题：扩展 Unity3D 编辑器的脚本模板。
<!--more-->

# 按图索骥，模板在哪里
Unity3D 默认的脚本模版位于/Editor/Data/Resources/ScriptTemplates/目录下，注意该目录相对 Unity3D 的安装目录而言，在这个目录中我们可以找到 Unity3D 中脚本模板的某些蛛丝马迹，首先，脚本模板是一个简单的文本文件，这个文本文件中预先填充了内容，我们在编辑器中创建模脚本或者 Shader 的时候实际上是读取这些文件然后在写入项目中的指定路径的。其次，这些模板文件中#SCRIPTNAME#或者#NAME#这样的标记，当我们在编辑器中创建文件的时候，这个标记会被替换成指定的文件名。比如 Unity3D 中继承自 MonoBehaviour 的脚本，有一个非常重要的特性是文件名必须和类名保持一致，这固然是 Unity3D 引擎的一个设定，可是在这里亦可以找到一个可以称得上理由的理由。我们注意到这些模板的文件名中都有一个独一无二的数字，比如 C#脚本的模板中的数字是 81、Shader 模板中的数字是 83，这些数字是什么呢，博主这里将其称为来自星星的黑科技。

# 来自星星的黑科技
作为一个经常捣鼓 Unity3D 编辑器的人，如果说你不知道 MenuItem、EditorWindow、ScriptableWizard 这些黑科技，那么说明你不是一个喜欢折腾和探索的人。从 Unity3D 的 API 文档中，我们知道 MenuItem 的原型为：
```csharp
MenuItem(string itemName,bool isValidateFunction,int priority) 
```
我知道我们通常使用 MenuItem 常常使用的是它的第一个参数，即定义一个菜单项的名称，我们可以使用"/"这样的分隔符来表示菜单的层级，MenuItem 需要配合一个静态方法来使用，可以理解为当我们点击当前定义的菜单后就会去执行静态方法中的代码，因此 MenuItem 常常可以帮助我们做些编辑器扩展开发的工作。好了，第二个参数作为一个验证的标志，如果该标志为 true，意味着我们定义的静态方法是一个验证方法在执行静态方法前会首先对方法进行验证，这个我们暂且不管，因为今天我们这个来自星星的黑科技主要和第三个参数有关，第三个参数表示一个优先级，它表示菜单项在菜单栏中的展示顺序，优先级大的菜单项会展示在优先级小的菜单项下面，由此我们就明白了了模板文件名中的类似 81、83 这样的数字的真实含义，注意到模板文件的排列顺序和编辑器中的菜单项顺序是一样的，我们做一个尝试，编写下面的代码：
```csharp
[MenuItem("Assets/Create/Lua Scripts", false, 85)]
static void CreateLuaScripts()
{
        
}

[MenuItem("Assets/Create/固定功能着色器", false, 86)]
static void CreateFixedFunctionShader()
{
        
}

[MenuItem("Assets/Create/表面着色器", false, 87)]
static void CreateSurfaceShader()
{
       
}

[MenuItem("Assets/Create/可编程着色器", false, 88)]
static void CreateVertexAndFragmentShader()
{
        
}
```
注意到我们按照已知的优先级继续写了四个方法，现在我们在编辑器中可以发现默认的菜单栏发生了变化：

![黑科技让菜单栏发生了变化](https://i.loli.net/2021/10/18/ZeBFMRDiGk24fSz.png)

我们可以看到我们编写的这四个菜单都生效了，虽然它们暂时什么都做不了，但顺着这个方向去探索，我们是可以实现最初的梦想的。现在我们来思考如何根据模板来创建文件，这个对我们来说简直太简单了，通过 StreamReader 来读取模板，然后再用 StreamWriter 来生成文件就可以了。可是这样创建的文件的文件名是固定的，在创建文件的时候我们没法修改，而且即使修改了文件内定义的名字并不会改变啊。所以我们需要一个更好的解决方案。Unity3D 提供了一个 UnityEditor.ProjectWindowCallback 的命名空间，在这个空间中提供了一个称为 EndNameEditAction 的类，我们只需要继承这个类就可以完成这个任务。这个类需要重写 Action 的方法，我们知道创建一个文件的完整步骤是创建文件然后使其高亮显示，因此这部分代码实现如下：
```csharp
/// <summary>
/// 定义一个创建资源的Action类并实现其Action方法
/// </summary>
class CreateAssetAction : EndNameEditAction
{

    public override void Action(int instanceId, string pathName, string resourceFile)
    {
        //创建资源
        Object obj = CreateAssetFormTemplate(pathName, resourceFile);
        //高亮显示该资源
        ProjectWindowUtil.ShowCreatedAsset(obj);
    }

    internal static Object CreateAssetFormTemplate(string pathName, string resourceFile)
    {

        //获取要创建资源的绝对路径
        string fullName = Path.GetFullPath(pathName);
        //读取本地模版文件
        StreamReader reader = new StreamReader(resourceFile);
        string content = reader.ReadToEnd();
        reader.Close();

        //获取资源的文件名
        string fileName = Path.GetFileNameWithoutExtension(pathName);
        //替换默认的文件名
        content = content.Replace("#NAME", fileName);

        //写入新文件
        StreamWriter writer = new StreamWriter(fullName, false, System.Text.Encoding.UTF8);
        writer.Write(content);
        writer.Close();

        //刷新本地资源
        AssetDatabase.ImportAsset(pathName);
        AssetDatabase.Refresh();

        return AssetDatabase.LoadAssetAtPath(pathName, typeof(Object));
    }
}
```
这部分代码相对来说比较简单，就是读取本地模板文件然后生成新文件，在生成新文件的时候会将#NAME 替换成实际的文件名，这样我们就完成了文件资源的创建。现在的问题是如何在创建文件的时候获取实际的路径，这部分代码实现如下：
```csharp
private static string GetSelectedPath()
{
    //默认路径为Assets
    string selectedPath = "Assets";

    //获取选中的资源
    Object[] selection = Selection.GetFiltered(typeof(Object), SelectionMode.Assets);

    //遍历选中的资源以返回路径
    foreach (Object obj in selection)
    {
        selectedPath = AssetDatabase.GetAssetPath(obj);
        if (!string.IsNullOrEmpty(selectedPath) && File.Exists(selectedPath))
        {
            selectedPath = Path.GetDirectoryName(selectedPath);
            break;
        }
    }

    return selectedPath;
}
```
现在解决了创建资源的问题，我们接下来只要调用 ProjectWindowUtil 的 StartNameEditingIfProjectWindowExists 方法即可，该方法需要传入一个继承自 EndNameEditAction 的类的实例、目标文件路径和模板文件的路径。例如要创建一个 Lua 脚本可以这样实现：
```csharp
[MenuItem("Assets/Create/Lua Scripts", false, 85)]
static void CreateLuaScripts()
{
    ProjectWindowUtil.StartNameEditingIfProjectWindowExists(0,
        ScriptableObject.CreateInstance<CreateAssetAction>(),
        GetSelectedPath() + "/NewLuaScript.lua", null,
        "Assets/Editor/Template/85-Lua-NewLuaScript.lua.txt");
}
```

![通过编辑器扩展实现 Shader 文件的创建](https://i.loli.net/2021/10/18/y3p5Gf81XLaKkle.gif)


# 小结
现在有了这个黑科技以后，我们可以创建更多的模板来扩展编辑器的功能，比如对 Shader 而言，我们可以创建些基础性的 Shader 模板，然后每次需要写 Shader 的时候直接从模板库中选择一个功能类似的 Shader 然后在此基础上进行修改，这样比从头开始写一个新的 Shader 应该会轻松不少，这段时间学习 Shader，感觉进程缓慢离图形学高手遥遥无期，行了，这篇博客就是这样了。

