---
abbrlink: 1124152964
categories:
- 游戏开发
date: 2015-11-15 13:07:57
description: 最后，全部的三角面会被读取到faceVertexNormalUV列表中，它表示的是每个三角面的顶点、法线和UV的索引向量，是一个List<Vector3>类型的变量
tags:
- OBJ
- Unity3D
- 格式
title: 解析OBJ模型并将其加载到Unity3D场景中
---

&emsp;&emsp;各位朋友，大家好，欢迎大家关注我的博客，我是**秦元培**，我的博客地址是[http://qinyuanpei.com](http://qinyuanpei.com)。今天想和大家交流的是解析obj模型并将其加载到Unity3D场景中，虽然我们知道Unity3D是可以直接导入OBJ模型的，可是有时候我们并不能保证我们目标客户知道如何使用Unity3D的这套制作流程，可能对方最终提供给我们的就是一个模型文件而已，所以这个在这里做这个尝试想想还是蛮有趣的呢，既然如此，我们就选择在所有3D模型格式中最为简单的OBJ模型来一起探讨这个问题吧！<!--more-->

#关于OBJ模型
&emsp;&emsp;OBJ格式是一种3D模型文件格式，是由Alias|Wavefront公司为3D建模和动画软件 “Advanced Visualizer”开发的一种标准，适合用于3D软件模型之间的互相转换。和FBX、Max这种内部私有格式不同，OBJ模型文件是一种文本文件，我们可以直接使用记事本等软件打开进行编辑和查看，因此我们这里选择OBJ模型主要是基于它开放和标准这两个特点。需要说明的是，OBJ文件是一种3D模型文件，它主要支持多边形模型（三个点以上的面）。OBJ模型支持法线和贴图坐标，可是因为它本身并不记录动画、材质特性、贴图路径、动力学及粒子等信息，所以我们在游戏开发中基本看不到这种模型格式的，所以我们这里做下简单研究就好。
#OBJ模型解读
&emsp;&emsp;因为OBJ模型文件是一个文本文件，所以我们可以使用记事本等软件打开它来对它的文件结构进行下了解。首先OBJ文件没有头文件，如果你曾经尝试解析过mp3文件的ID3v1/ID3v2标签就应该知道它是根据mp3文件的开头或者末尾的若干字节来判断这些标签信息的，而在OBJ文件中是没有类似这样的头文件的。OBJ文件是由一行行由关键字、空格和文本字符组成的文本文件，通过关键字我们就可以知道这一行的文本表示的是什么数据。例如：
```
# Blender v2.76 (sub 0) OBJ File: ''
```
**#**关键字表示一个注释行，通过这个注释信息我们可以知道这个OBJ模型是由Blender2.76版本导出的。再比如：
```
mtllib liumengli.mtl
```
**mtllib**关键字则表示当前模型对应的材质库(.mtl)文件名称，每个OBJ模型文件都会有这样一个对应和它同名的.mtl文件，在这个文件中记录了材质相关的信息，稍后我们说到材质的时候会详细说说这个文件的格式，因为它和OBJ文件一样是一个文件文件。再比如：
```
usemtl Material__33
```
**usemtl**关键字则表示从当前行到下一个usemtl关键字所在行间的全部网格结构都使用其对应的材质，通过这个材质名称我们可以在.obj文件对应的.mtl文件中找到它的材质定义，这个我们在讲到材质部分的时候会详细说。

&emsp;&emsp;好了，目前我们要做的工作室解析.obj文件然后创建网格进而可以使其显示在Unity3D场景中，在这里我们要重点关注的关键字有：
* v即Vertex，表示一个顶点的局部坐标系中的坐标，通常有三个分量，因为这里讨论的是三角面。例如：

```
v  1.5202 14.9252 -1.1004
```

* vn即Vertex Normal，表示法线，注意到这些向量都是单位向量，所以我们可以认为三维软件在导出模型的时候已经做好了相关的标准化工作。

```
vn 0.8361 -0.0976 0.5399
```

* vt即Vertex Texture，表示纹理坐标，就是我们熟悉的UV坐标啦，显然UV是个2D坐标，有两个分量。

```
vt -0.5623 0.4822 1.0000
```

* f即face，这是一个真正描述面的关键字，通常它后面有三个索引结构，每个索引结构由顶点索引、法线索引和纹理坐标索引三部分构成。例如：

```
f 256/303/637 257/304/638 258/305/639 
```
以上这些关键字对我们解析.obj文件来说已经完全足够了，如果大家想对这些细节有更为深入的了解，可以参考这里[这里](http://baike.baidu.com/link?url=Wwxg_S2gk5mksyNLzLPC0W5Iqb8SHyZuH19lpkFEAvd3ZYheo9ZReW3s59Vp75T8vYFBzaRL7__dmJlhCbR0tyBsZqKJY7JC0ixrXER2X4m)。

#OBJ模型的读取
&emsp;&emsp;OBJ模型的读取涉及到网格部分的读取和材质部分的读取两个部分，其中网格部分的读取难点在于当模型存在多个材质的时候，需要将模型分为若干个子物体，然后分别为这些子物体添加材质。可是不幸的是到目前为止，博主并没有找到一种行之有效的方法来对这些网格进行分类，所以这里我们假定模型是一个整体且共享同一种材质和一张贴图。如果大家找到了更好的解决方案，请记得告诉我，再次谢谢大家！

##网格部分
&emsp;&emsp;在网格读取这部分，因为我们已经假设所有的面构成一个物体，因此我们可以先将OBJ文件内的文本按照换行符来进行分割，然后再按照关键字去判断每一行的数据类型并进行相应的处理就可以了。读取OBJ模型的基本流程是：
* 读取顶点、法线、UV以及三角面
* 将三角面合并为四边面
* 根据索引重新计算顶点、法线、UV数组

###读取顶点、法线、UV以及三角面
&emsp;&emsp;首先我们来看第一步的代码实现：
```
/// <summary>
/// 从一个文本化后的.obj文件中加载模型
/// </summary>
public ObjMesh LoadFromObj(string objText)
{
    if(objText.Length <= 0) 
        return null;
	//v这一行前面是两个空格后面是一个空格
	objText=objText.Replace("  ", " ");

    //将文本化后的obj文件内容按行分割
    string[] allLines = objText.Split('\n');
    foreach(string line in allLines)
    {
        //将每一行按空格分割
	    string[] chars = line.Split(' ');
        //根据第一个字符来判断数据的类型
        switch(chars[0])
        {
             case "v":
             //处理顶点
             this.vertexArrayList.Add(new Vector3(
			 	ConvertToFloat(chars[1]), 
			 	ConvertToFloat(chars[2]),
			 	ConvertToFloat(chars[3]))
			 	);
                break;
             case "vn":
             //处理法线
             this.normalArrayList.Add(new Vector3(
				ConvertToFloat(chars[1]), 
				ConvertToFloat(chars[2]), 
				ConvertToFloat(chars[3]))
				);
              break;
              case "vt":
              //处理UV
              this.uvArrayList.Add(new Vector3(
				ConvertToFloat(chars[1]),
				ConvertToFloat(chars[2]))
				);
                break;
              case "f":
              //处理面
              GetTriangleList(chars);
              	break;
       }
 }
```
在这段代码中，我们首先将文本化的.obj文件按照换行符分割成字符串数组allLines，然后再对每一行按照空格分隔成字符串数组chars，这样我们就可以通过该数组的第一个元素chars[0]来判断当前行中的数据类型。这样我们将每一行的文本读取完后，所有的数据都被存储到了其相对应的列表中。其中，vertexArrayList存储顶点信息、normalArrayList存储法线信息、uvArrayList存储UV坐标。至此，我们完成第一部分中的顶点、法线和UV的读取。

&emsp;&emsp;这里可以注意到我们在开始对文本化的.obj文件的内容有1次替换操作，这是因为在3dsMax中导出的.obj文件关键字**v**这一行中v后面的第一处空格位置是有2个空格，而我们在处理的时候是按照空格来分割每一行的内容的，这样chars[1]就会变成一个空字符串，显然这不符合我们的初衷，所以这里就需要对字符串进行这样一个操作，希望大家在解析的过程中注意，好吧，我承认我想吐槽3dsMax了，我不明白同一家公司的3dsMax和Maya为什么不能互相转换，我不明白3dsMax导出.obj文件的时候要做这样奇葩的设定，我更不明白为什么有开源、免费、轻巧的Blender都不去用非要每次都去安装容量动辄上G的盗版软件和不知道会不会变成下一个GhostXXXX的注册机，我更加不能容忍的是封闭的FBX格式和用起来就如同自虐的FBX SDK。

&emsp;&emsp;好了，吐槽结束，我们接下来来看看三角面是如何读取的。三角面的读取定义在GetTriangleList()方法中，因此三角面的读取实际上首先需要将每一行文本按照空格进行分割，然后再将每一个元素按照/分割，这样就可以依次得到顶点索引、法线索引和UV索引。在某些情况下法线索引可能不存在，所以在处理的过程中需要对其进行处理。

```
/// <summary>
/// 获取面列表.
/// </summary>
/// <param name="chars">Chars.</param>
private void GetTriangleList(string[] chars)
{
   List<Vector3> indexVectorList = new List<Vector3>();
   List<Vector3> triangleList = new List<Vector3>();

   for(int i = 1; i < chars.Length;++i )
   {
       //将每一行按照空格分割后从第一个元素开始
       //按照/继续分割可依次获得顶点索引、法线索引和UV索引
       string[] indexs = chars[i].Split('/');
       Vector3 indexVector = new Vector3(0, 0);
       //顶点索引
       indexVector.x = ConvertToInt(indexs[0]);
       //法线索引
       if(indexs.Length > 1){
          if(indexs[1] != "")
             indexVector.y = ConvertToInt(indexs[1]);
       }
       //UV索引
       if(indexs.Length > 2){
          if(indexs[2] != "")
              indexVector.z = ConvertToInt(indexs[2]);
       }

	   //将索引向量加入列表中
       indexVectorList.Add(indexVector);
   }

   //这里需要研究研究
   for(int j = 1; j < indexVectorList.Count - 1; ++j)
   {
	   //按照0,1,2这样的方式来组成面
	   triangleList.Add(indexVectorList[0]);
	   triangleList.Add(indexVectorList[j]);
	   triangleList.Add(indexVectorList[j + 1]);
   }

   //添加到索引列表
   foreach(Vector3 item in triangleList)
   {
      faceVertexNormalUV.Add(item);
   }
}
```
在这里，我们首先使用一个索引向量列表indexVectorList存储每一行的索引向量。这里的索引向量是指由顶点索引、法线索引和UV索引分别构成Vector3的三个分量，这样做的好处是我们可以节省重新去定义数据机构的时间。好了，我们把所有的索引向量读取完后，按照0、1、2这样的方式组成三角面，这里可能是.obj文件本身定义的一种方式，我们暂且按照这样的方式来处理。最后，全部的三角面会被读取到faceVertexNormalUV列表中，它表示的是每个三角面的顶点、法线和UV的索引向量，是一个List<Vector3>类型的变量。

###将三角面合并为四边面
&emsp;&emsp;现在我们读取到的是三角面，接下来我们需要将它们合并成四边面，合并的原理是判断它们是否在同一个面上。如果两个点的顶点索引相同则表明它们是同一个点，如果两个点的法线索引相同则表明它们在同一个面上。好了，我们来看定义的一个方法Combine():
```
/// <summary>
/// 合并三角面
/// </summary>
private void Combine()
{
   //使用一个字典来存储要合并的索引信息
   Dictionary<int, ArrayList> toCambineList = new Dictionary<int,ArrayList>();
   for(int i = 0; i < faceVertexNormalUV.Count; i++)
   {
       if(faceVertexNormalUV[i] != Vector3.zero)
       {
           //相同索引的列表
           ArrayList SameIndexList = new ArrayList();
           SameIndexList.Add(i);
           for(int j = 0; j < faceVertexNormalUV.Count; j++)
           {
               if(faceVertexNormalUV[j]!=Vector3.zero)
               {
                  if(i != j)
                  {
					 //如果顶点索引和法线索引相同，说明它们在一个面上
                     Vector3 iTemp = (Vector3)faceVertexNormalUV[i];
				     Vector3 jTemp = (Vector3)faceVertexNormalUV[j];
                     if(iTemp.x == jTemp.x && iTemp.y == jTemp.y)
                     {
						//将索引相同索引列表然后将其重置为零向量
					    //PS:这是个危险的地方，如果某个索引信息为Vector3.Zero
						//就会被忽略过去，可是貌似到目前为止没有发现为Vector3.Zero的情况
                        SameIndexList.Add(j);
						faceVertexNormalUV[j]=Vector3.zero;
                     }
                   }
               }
           }
		   //用一个索引来作为字典的键名，这样它可以代替对应列表内所有索引
           toCambineList.Add(i, SameIndexList);
       }
    }
 }
```
在这里我们使用了一个字典来存储合并后的四边面，这个字典的键名为这一组三角面共同的索引，因为大家都是用同一个索引，因此它可以代替那些被合并的三角面的索引，这样合并以后的四边面列表中元素的个数就是实际的网格中的面数个数，因为如果采用三角面的话，这个面数会比现在的面数还要多，这意味着这样会带来更多的性能上的消耗。这里可能不大好理解，大家可以将博主这里的表达方式换成自己能够理解的方式。佛曰不可说，遇到这种博主自己都说不明白的地方，博主就只能请大家多多担待了。好了，接下来要做的是重新计算顶点、法线和UV数组。可能大家会比较疑惑，这部分内容我们在第一步不是就已经读取出来了嘛，怎么这里又要重新计算了呢？哈哈，且听我慢慢道来！

###根据索引重新计算顶点、法线、UV数组
&emsp;&emsp;虽然我们在第一步就读取到了这些坐标数据，可是当我们合并三角面以后，就会出现大量的无用的点，为什么无用呢，因为它被合并到四边面里了，这样我们原来读取的这些坐标数据就变得不适用了。那怎么办呢？在第三步中我们合并四边面的时候已经用一个字典保存了合并后的索引信息，这就相当于我们已经知道哪些是合并前的索引，哪些是合并后的索引，这个时候我们只要根据索引重新为数组赋值即可：
```
//初始化各个数组
this.VertexArray = new Vector3[toCambineList.Count];
this.UVArray = new Vector2[toCambineList.Count];
this.NormalArray = new Vector3[toCambineList.Count];
this.TriangleArray = new int[faceVertexNormalUV.Count];

//定义遍历字典的计数器
int count = 0;

//遍历词典
foreach(KeyValuePair<int,ArrayList> IndexTtem in toCambineList)
{
	//根据索引给面数组赋值
	foreach(int item in IndexTtem.Value)
	{
    	TriangleArray[item] = count;
	}

    //当前的顶点、UV、法线索引信息
    Vector3 VectorTemp = (Vector3)faceVertexNormalUV[IndexTtem.Key];

    //给顶点数组赋值
    VertexArray[count] = (Vector3)vertexArrayList[(int)VectorTemp.x - 1];

	//给UV数组赋值
    if(uvArrayList.Count > 0)
    {
       Vector3 tVec =(Vector3)uvArrayList[(int)VectorTemp.y - 1];
       UVArray[count] = new Vector2(tVec.x, tVec.y);
    }

			//给法线数组赋值
            if(normalArrayList.Count > 0)
            {
                NormalArray[count] = (Vector3)normalArrayList[(int)VectorTemp.z - 1];
            }

            count++;
        }
```
这样我们就读取到了合并后的坐标信息，通过顶点、法线、UV、面等信息我们现在就可以生成网格了。这部分我们暂且不着急，因为这基本上属于最后整合到Unity3D中步骤了。好了，为了方便大家理解，我已经完整的项目上传到Github，大家可以通过[这里](https://github.com/qinyuanpei/Unity-Obj-Loader)了解完整的项目。

##材质部分
&emsp;&emsp;材质这块儿的解析主要集中在.mtl文件中，和.obj文件类似，它同样是一个文本文件、同样采用关键字、空格、文本字符这样的结构来表示数据，因此我们可以借鉴.obj文件的读取。例如：
```
newmtl Material
```
**newmtl**关键字表示从当前行到下一个newmtl关键字所在行间都表示该关键字所对应的材质，这里的Material即表示材质的名称，它和.obj文件中的**usemtl**关键字相对应，因此我们给模型添加材质的过程本质上是从.obj文件中读取网格，然后找到其对应的材质名称，然后在.mtl文件中找到对应的材质定义，并根据定义来生成材质。目前已知的关键字有：
```
Ka 0.5880 0.5880 0.5880
```
**Ka**关键字表示环境反射的RGB数值。

```
Kd 0.640000 0.640000 0.640000
```
**Kd**关键字表示漫反射的RGB数值。

```
Ks 0.500000 0.500000 0.500000
```
**Ks**关键字表示镜面反射的RGB数值。

```
map_Ka E:\学习资料\Unity3D技术\Unity3D素材\柳梦璃\Texture\1df2eaa0.dds
```
**map_Ka**关键字表示环境反射的纹理贴图，注意到这里使用的是绝对路径，显然我们在读取模型的时候不会将贴图放在这样一个固定的路径，因此我们这里初步的想法读取贴图的文件名而非贴图的完整路径，考虑到我们在Unity3D中一般使用PNG格式的贴图，因此这里需要对路径进行处理。

```
map_Kd E:\学习资料\Unity3D技术\Unity3D素材\柳梦璃\Texture\1df2eaa0.dds
```
**map_Kd**关键字表示漫反射的纹理贴图，和环境反射的纹理贴图是类似地，这里就不再说了。此外还有其它的关键字，初步可以推断出的结论是它和3dsMax中材质编辑器里的定义特别地相似，感兴趣的朋友可以进一步去研究。可是现在就有一个新的问题了，怎样将这些参数和Unity3D里的材质关联起来呢？我们知道Unity3D里的材质是是由着色器和贴图两部分组成的，博主对Shader并不是很熟悉，因此这里确实有些说不清楚了。博主感觉对OBJ文件来说，其实使用Diffuse就完全足够了，所以这里对材质部分的研究我们点到为止，不打算做代码上的实现。如果不考虑这些参数的话，我们要做的就是通过WWW或者Resource将贴图加载进来，然后赋值给我们通过代码创建的Shader即可。而对于.obj文件来说，无论是通过Resource、WWW或者是IO流，只要我们拿到了这个文件中的内容就可以使用本文中的方式加载进来，因为我们假定的是读取只有一种材质的模型。有朋友可能要问，那如果有多种材质怎么办呢？答案是在.mtl问价中获取到所有贴图的名称，然后再到程序指定的路径去读取贴图，分别为其创建不同的材质，可是这些材质要怎么附加到它对应的物体上呢？这个目前博主没有找到解决的方法，所以此事暂且作罢吧！


#在Unity3D中加载obj模型
&emsp;&emsp;下面我们以一个简单的例子来展示今天研究的成果，我们将从.obj文件中读取出一个简单的模型并将其加载到场景中。好了，我们一起来看代码：
```
if(!File.Exists("D:\\cube.obj"))
	Debug.Log("请确认obj模型文件是否存在!");

StreamReader reader = new StreamReader("D:\\cube.obj",Encoding.Default);
string content = reader.ReadToEnd();
reader.Close();

ObjMesh objInstace = new ObjMesh();
objInstace = objInstace.LoadFromObj(content);
		
Mesh mesh = new Mesh();
mesh.vertices = objInstace.VertexArray;
mesh.triangles = objInstace.TriangleArray;
if(objInstace.UVArray.Length > 0)
	mesh.uv = objInstace.UVArray;
if(objInstace.NormalArray.Length>0)
	mesh.normals = objInstace.NormalArray;
mesh.RecalculateBounds();
		
GameObject go = new GameObject();
MeshFilter meshFilter = go.AddComponent<MeshFilter>();
meshFilter.mesh = mesh;
		
MeshRenderer meshRenderer = go.AddComponent<MeshRenderer>();
```
这里没有处理材质，所以读取出来就是这个样子的，哈哈！

![最终效果，这是一个悲伤的故事](https://ww1.sinaimg.cn/large/4c36074fly1fzix9cbxdaj20kt0h6t8j.jpg)

材质大家可以尝试用代码去创建一个材质，然后在给一张贴图，这个玩玩就好，哈哈！好了，今天的内容就是这样子了，希望大家喜欢，为了写这篇文章我都怀疑我是不是有拖延症啊！