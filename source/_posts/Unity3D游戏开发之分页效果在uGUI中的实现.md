---
title: Unity3D游戏开发之分页效果在uGUI中的实现
categories:
  - Unity3D
tags:
  - 游戏开发
  - uGUI
  - Unity3D
toc: false
abbrlink: 166983157
date: 2015-11-10 20:46:35
---
&emsp;&emsp;各位朋友大家好，我是**秦元培**，欢迎大家关注我的博客，我的博客地址是[http://qinyuanpei.com](http://qinyuanpei.com)。今天想和大家分享的是uGUI中分页效果的实现，我们知道相对NGUI来说uGUI在功能覆盖上来讲，它并没有像NGUI那样提供较为丰富和炫酷的组件，可是因为uGUI有着较好的扩展性，因此我们可以通过编写脚本来扩展它的功能。虽然在移动开发时代以开发速度论成败，可是这并不是我们“不求甚解”的正当理由。每次看到NGUI各种"丰富"的组件在脑海中打转的时候，每次看到编译项目时弹出各种Warming的时候，我内心是如此地期望有这样一个简单高效的UI系统啊，直到有一天我遇上了uGUI。

<!--more-->

&emsp;&emsp;好了，博主这里并没有想要表达厚此薄彼的观点啦，博主真正想要表达的是我们在开发中应该摒弃“唯语言论”、“唯平台论”的狭隘观点，努力去掌握和语言无关、平台无关的“通用型技能”。这样，当我们面对全新的任务的时候我们可以更快地适应新的环境。言归正传，我们这里来接着说uGUI中的分页，分页通常是指将内容分散到不同的页面上来显示的一种手段，这种手段我们在传统的Web开发中可以经常看到。到了移动互联网以后分页被我们更为熟知的“下拉更新”所替代，这种方式我们就更为熟悉啦。好了，我们回到分页，为什么要要分页呢？这里有两个关键点：**第一，内容在一页内无法展示完全；第二，对内容的数量无法进行估计。**

&emsp;&emsp;例如，我们在uGUI中可以使用ScrollRect组件 + GridLayout组件 + Mask组件实现一个滚动列表，具体的案例可以参考[这里](http://www.cnblogs.com/zhaoqingqing/p/3973167.html)。这里我们可以注意到一件事情就是这个滚动列表，它可以滚动的范围是由Mask组件来决定的，因此这个滚动列表是无法无限滚动的，虽然我们知道在游戏设计中不会出现这种无限滚动的列表，可是我们这里是为了探讨这个问题，所以我们假设这个情况是允许发生的。那么面对这个问题，我们有什么好的解决方案呢？博主尝试过一种思路，即借鉴Android中的ListView控件，这个控件的特点是可以对列表中的项目进行回收。相信说到这里，大家都明白我想做什么了吧，大概的思路就是制作一个高度大于屏幕高度的列表，然后让所有的列表项在这个列表中循环显示。可是新的问题就来了，**第一，频繁地生成和销毁物体是Unity3D大忌**。虽然我们可以缓存池来解决这个问题，可是因为博主并没有具体这样实践过，所以这里目前是存疑的。**第二，GridLayout这个组件内的元素排序是根据子元素添加的顺序来决定的，因此每次列表更新以后都需要将所有的子元素更新一遍。**曾经因为这样需求和策划发生过争执，最终妥协的一个结果就是采用分页来解决这个问题。分页首先解决了无限滚动的需求，因为它是一种“以不变应万变”的策略，不论列表内元素有多少它都可以显示出来。其次，在分页的过程是将数据模板化的过程，它改变是界面的外观和行为，UI结构是相对稳定的，这样可以避免频繁地生成和销毁物体。

&emsp;&emsp;下面我们以一个简单的案例来探讨分页效果在uGUI中的实现，首先我们使用GridLayoutGroup来制作一个简单的网格布局，请用心感受下图中萌萌哒十二生肖：

![请不要伤害一个程序员的艺术细胞，虽然我知道它比较难看](http://img.blog.csdn.net/20151111131947806)

这里我们不再对这个布局的制作方法进行详细的说明，因为我们今天的重点不在这里。我们注意到这里有12个元素，当我们每次对页面进行切换的时候，实际上这12个元素是基本不会发生变化的，真正变化的是这些元素的外观（如这里的精灵图片和名称）以及其对应的UI事件，在这个案例中我们利用匿名函数实现了一个简单的Click事件的监听。好了，前面我们说到分页的一个目的是可以解决列表内元素数目不确定的问题，因此我们这里利用一个12生肖的数组来随机生成元素数目不同的列表，代码实现如下：
```
	/// <summary>
    /// 初始化元素
    /// </summary>
    private void InitItems()
    {
        //准备一个存储着12生肖信息的数组
        GridItem[] items = new GridItem[]
        {
            new GridItem("鼠","Mouse"),
            new GridItem("牛","Ox"),
            new GridItem("虎","Tiger"),
            new GridItem("兔","Rabbit"),
            new GridItem("龙","Dragon"),
            new GridItem("蛇","Snake"),
            new GridItem("马","Horse"),
            new GridItem("羊","Goat"),
            new GridItem("猴","Monkey"),
            new GridItem("鸡","Rooster"),
            new GridItem("狗","Dog"),
            new GridItem("猪","Pig")
        };

        //利用12生肖数组来随机生成列表
        m_ItemsList = new List<GridItem>();
        for(int i = 0; i < Random.Range(1,1000); i++)
        {
            m_ItemsList.Add(items[Random.Range(0,items.Length)]);
        }

        //计算元素总个数
        m_ItemsCount = m_ItemsList.Count;
        //计算总页数
        m_PageCount = (m_ItemsCount % 12) == 0 ? m_ItemsCount / 12 : (m_ItemsCount / 12) + 1;

        BindPage(m_PageIndex);
        //更新界面页数
        m_PanelText.text = string.Format("{0}/{1}",
         m_PageIndex.ToString(),
         m_PageCount.ToString());
    }
```
在这段代码中，m_ItemList表示我们要展示的元素列表，m_ItemsCount表示元素列表中元素的个数，m_PageCount表示这些元素可以分成的总页数，m_PageIndex表示页数的索引**默认从1开始**。其中GridItem是一个简单的类，它有ItemName和ItemSprite两个属性，这里不再具体说明了。好了，现在我们来思考如何将这些元素和UI对应起来，因为列表中元素的数目不确定，因此我们可以分成两种情况来讨论：

* 页面总数为1，即m_PageCount=1，此时列表内的元素个数的范围是1~12，因此我们可以利用循环判断哪些元素是要展示的？哪些元素是不需要的？因为如果此时列表内的元素为10，则意味着前面10个元素是要展示给用户，而剩下的2个元素是不需要的。在这里我们简单地使用SetActive来让这些元素隐藏起来。

* 页面总数大于1，即m_PageCount>1，此时前面的m_PageCount-1个页面都是显示完全的，它相当于元素总个数中被12整除的部分。而第m_PageCount个页面此时的情况和页数总数为1的情况类似，我们可以采取和页面总数为1类似的方法来处理。

&emsp;&emsp;好了，下面我们来看这部分代码的具体实现：
```
    /// <summary>
    /// 绑定指定索引处的页面元素
    /// </summary>
    /// <param name="index">页面索引</param>
    private void BindPage(int index)
    {
        //列表处理
        if(m_ItemsList == null || m_ItemsCount <= 0)
            return;

        //索引处理
        if(index < 0 || index > m_ItemsCount)
            return;

        //按照元素个数可以分为1页和1页以上两种情况
        if(m_PageCount == 1)
        {
            int canDisplay = 0;
            for(int i = 12; i > 0; i--)
            {
                if(canDisplay < 12){
                    BindGridItem(transform.GetChild(canDisplay), m_ItemsList[12 - i]);
                    transform.GetChild(canDisplay).gameObject.SetActive(true);
                }else{
                    //对超过canDispaly的物体实施隐藏
                    transform.GetChild(canDisplay).gameObject.SetActive(false);
                }
                canDisplay += 1;
            }
        }else if(m_PageCount > 1){
            //1页以上需要特别处理的是最后1页
            //和1页时的情况类似判断最后一页剩下的元素数目
            //第1页时显然剩下的为12所以不用处理
            if(index == m_PageCount){
                int canDisplay = 0;
                for(int i = 12; i > 0; i--)
                {
                    //最后一页剩下的元素数目为 m_ItemsCount - 12 * (index-1)
                    if(canDisplay < m_ItemsCount - 12 * (index-1)){
                        BindGridItem(transform.GetChild(canDisplay), m_ItemsList[12 * index-i]);
                        transform.GetChild(canDisplay).gameObject.SetActive(true);
                    }else{
                        //对超过canDispaly的物体实施隐藏
                        transform.GetChild(canDisplay).gameObject.SetActive(false);
                    }
                    canDisplay += 1;
                }
            }
            else{
                for(int i = 12; i > 0; i--)
                {
                    BindGridItem(transform.GetChild(12 - i), m_ItemsList[12 * index - i]);
                    transform.GetChild(12 - i).gameObject.SetActive(true);
                }
            }
        }
    }
```
好了，在这里完成BindPage方法的定义以后，我们就可以指定程序显示对应页面的元素，此时上一页和下一页的工作基本上就是改变索引的一个过程了。这部分我们不再说了，大家可以去看最终给出的完整代码，我们这里来看看实际的效果吧！

![简单的分页效果展示](https://ws1.sinaimg.cn/large/4c36074fly1fz68jx43btg20kp0gqne1.jpg)

其实这里核心的内容是分页的处理，在处理里只有1页时的元素个数和超过1页的最后1页时我们可以采取两个循环处理的方法，即先从0循环到m_ItemsCount - 12 * (index-1))设置要显示的元素，然后再从m_ItemsCount - 12 * (index-1))循环到12设置要隐藏的元素，可是这样的方式我不太喜欢，所以在文章中就没有采取这样的方式。这篇文章是根据一个项目当时的经历写的，因为时间过得比较久，所以如果文章中不当之处希望大家指出并批评。现在这个方案感觉还可以在特效上进行改进，因为现在感觉切换的时候画面比较突兀，这一点请大家注意。好了，下面给出完整的代码和场景布局截图。再次强调：**请在看懂文章的基础上“抄”代码**，每次看到别人问我把XXX脚本挂到场景中不起作用这类的问题，我就觉得整个世界充满了深深地罪恶感。别人愿意分享技术文章，更多的是希望可以和别人交流学习相互促进，如果你只是希望拿到一个随便抄来就能用地代码，抱歉！这违背了我的初衷所以我很难做到！
```
/*
 * 一个基于uGUI的分页功能的实现
 * 作者：秦元培
 * 时间：2015年11月11日
 * 博客：http://qinyuanpei.com
 */

using UnityEngine;
using System.Collections;
using System.Collections.Generic;
using UnityEngine.UI;

public class PaginationPanel : MonoBehaviour
{
    /// <summary>
    /// 当前页面索引
    /// </summary>
    private int m_PageIndex = 1;

    /// <summary>
    /// 总页数
    /// </summary>
    private int m_PageCount = 0;

    /// <summary>
    /// 元素总个数
    /// </summary>
    private int m_ItemsCount = 0;

    /// <summary>
    /// 元素列表
    /// </summary>
    private List<GridItem> m_ItemsList;

    /// <summary>
    /// 上一页
    /// </summary>
    private Button m_BtnPrevious;

    /// <summary>
    /// 下一页
    /// </summary>
    private Button m_BtnNext;

    /// <summary>
    /// 显示当前页数的标签
    /// </summary>
    private Text m_PanelText;

   

	void Start() 
    {
        InitGUI();
        InitItems();
	}

    /// <summary>
    /// 初始化GUI
    /// </summary>
    private void InitGUI()
    {
        m_BtnNext = GameObject.Find("Canvas/Panel/BtnNext").GetComponent<Button>();
        m_BtnPrevious = GameObject.Find("Canvas/Panel/BtnPrevious").GetComponent<Button>();
        m_PanelText = GameObject.Find("Canvas/Panel/Text").GetComponent<Text>();

        //为上一页和下一页添加事件
        m_BtnNext.onClick.AddListener(() => { Next(); });
        m_BtnPrevious.onClick.AddListener(() => { Previous(); });
    }

    /// <summary>
    /// 初始化元素
    /// </summary>
    private void InitItems()
    {
        //准备一个存储着12生肖信息的数组
        GridItem[] items = new GridItem[]
        {
            new GridItem("鼠","Mouse"),
            new GridItem("牛","Ox"),
            new GridItem("虎","Tiger"),
            new GridItem("兔","Rabbit"),
            new GridItem("龙","Dragon"),
            new GridItem("蛇","Snake"),
            new GridItem("马","Horse"),
            new GridItem("羊","Goat"),
            new GridItem("猴","Monkey"),
            new GridItem("鸡","Rooster"),
            new GridItem("狗","Dog"),
            new GridItem("猪","Pig")
        };

        //利用12生肖数组来随机生成列表
        m_ItemsList = new List<GridItem>();
        for(int i = 0; i < Random.Range(1,1000); i++)
        {
            m_ItemsList.Add(items[Random.Range(0,items.Length)]);
        }

        //计算元素总个数
        m_ItemsCount = m_ItemsList.Count;
        //计算总页数
        m_PageCount = (m_ItemsCount % 12) == 0 ? 
        m_ItemsCount / 12 : (m_ItemsCount / 12) + 1;

        BindPage(m_PageIndex);
        //更新界面页数
        m_PanelText.text = string.Format("{0}/{1}",
         m_PageIndex.ToString(),
          m_PageCount.ToString());
    }

    /// <summary>
    /// 下一页
    /// </summary>
    public void Next()
    {
        if(m_PageCount <= 0)
            return;
        //最后一页禁止向后翻页
        if(m_PageIndex >= m_PageCount)
            return;

        m_PageIndex += 1;
        if (m_PageIndex >= m_PageCount)
            m_PageIndex = m_PageCount;

        BindPage(m_PageIndex);

        //更新界面页数
        m_PanelText.text = string.Format("{0}/{1}",
         m_PageIndex.ToString(), 
         m_PageCount.ToString());
    }

    /// <summary>
    /// 上一页
    /// </summary>
    public void Previous()
    {
        if(m_PageCount <= 0)
            return;
        //第一页时禁止向前翻页
        if(m_PageIndex <= 1)
            return;
        m_PageIndex -= 1;
        if(m_PageIndex < 1)
            m_PageIndex = 1;

        BindPage(m_PageIndex);

        //更新界面页数
        m_PanelText.text = string.Format("{0}/{1}",
         m_PageIndex.ToString(), 
         m_PageCount.ToString());
    }

    /// <summary>
    /// 绑定指定索引处的页面元素
    /// </summary>
    /// <param name="index">页面索引</param>
    private void BindPage(int index)
    {
        //列表处理
        if(m_ItemsList == null || m_ItemsCount <= 0)
            return;

        //索引处理
        if(index < 0 || index > m_ItemsCount)
            return;

        //按照元素个数可以分为1页和1页以上两种情况
        if(m_PageCount == 1)
        {
            int canDisplay = 0;
            for(int i = 12; i > 0; i--)
            {
                if(canDisplay < 12){
                    BindGridItem(transform.GetChild(canDisplay), m_ItemsList[12 - i]);
                    transform.GetChild(canDisplay).gameObject.SetActive(true);
                }else{
                    //对超过canDispaly的物体实施隐藏
                    transform.GetChild(canDisplay).gameObject.SetActive(false);
                }
                canDisplay += 1;
            }
        }else if(m_PageCount > 1){
            //1页以上需要特别处理的是最后1页
            //和1页时的情况类似判断最后一页剩下的元素数目
            //第1页时显然剩下的为12所以不用处理
            if(index == m_PageCount){
                int canDisplay = 0;
                for(int i = 12; i > 0; i--)
                {
                    //最后一页剩下的元素数目为 m_ItemsCount - 12 * (index-1)
                    if(canDisplay < m_ItemsCount - 12 * (index-1)){
                        BindGridItem(transform.GetChild(canDisplay),
                        m_ItemsList[12 * index-i]);
                        transform.GetChild(canDisplay).
                        gameObject.SetActive(true);
                    }else{
                        //对超过canDispaly的物体实施隐藏
                        transform.GetChild(canDisplay).
                        gameObject.SetActive(false);
                    }
                    canDisplay += 1;
                }
            }
            else{
                for(int i = 12; i > 0; i--)
                {
                    BindGridItem(transform.GetChild(12 - i), m_ItemsList[12 * index - i]);
                    transform.GetChild(12 - i).gameObject.SetActive(true);
                }
            }
        }
    }


    /// <summary>
    /// 加载一个Sprite
    /// </summary>
    /// <param name="assetName">资源名称</param>
    private Sprite LoadSprite(string assetName)
    {
        Texture texture = (Texture)Resources.Load(assetName);

        Sprite sprite = Sprite.Create((Texture2D)texture, 
        new Rect(0, 0, texture.width, texture.height), 
        new Vector2(0.5f, 0.5f));
        return sprite;
    }

    /// <summary>
    /// 将一个GridItem实例绑定到指定的Transform上
    /// </summary>
    /// <param name="trans"></param>
    /// <param name="gridItem"></param>
    private void BindGridItem(Transform trans,GridItem gridItem)
    {
        trans.GetComponent<Image>().sprite = LoadSprite(gridItem.ItemSprite);
        trans.Find("Item/Name").GetComponent<Text>().text = gridItem.ItemName;
        trans.GetComponent<Button>().onClick.AddListener(()=>
        {
            Debug.Log("当前点击的元素名称为:" + gridItem.ItemName);
        });
    }
}
```
好了，今天的内容就是这样啦，欢迎大家继续关注我的博客，谢谢大家！

**2016年1月10日更新**：
&emsp;&emsp;经过博客中一位朋友指出，这篇文章中实现BindPage这个方法时可以在代码上再精简些，主要是考虑这个代码中有部分功能是重合的，因此这里对这个方法进行重写，分页从本质上来讲是编写这样一个函数：输入数据集合data、每页显示的元素个数pageSize以及当前页数page，然后返回一个新的数据集合。为了考虑扩展性我们这里编写一个分页的泛型方法，代码实现如下：
```
List<T> Pagination(List<T> data,int size,int page)
{
    //要返回的结果
    List<T> output = new List<T>();

    //计算最大页数
    int PageCount = (data.Count % size) == 0 ?
    (data.Count / size) : (data.Count / size) + 1;

    //判断输入页数的合法性
    if(page < 1 || page > PageCount)
        return null;

    //计算第page页第一个元素的索引
    int startIndex = (page - 1) * size;

    //除了尾页所有的页面中元素个数都是size个
    if(page < PageCount)
    {
        for (int i = 0; i < size; i++)
        {
            output.Add(data[startIndex + i]);
        }
    }
    else
    {
        for (int i = startIndex; i < data.Count; i++)
        {
            output.Add(data[i]);
        }
    }

    return output;
}
```
这里我们只需要考虑传入的页数是不是尾页即可，因为在所有的页面中除了尾页以外都有size个元素，所以我们只需要计算出第page页的第一个元素的索引，然后以此递增即可，而尾页显然是从startIndex到data.Count-1个。现在回过头来看，写个分页函数确实是简单至极，这篇博客显然是小题大做了。
