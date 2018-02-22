---
title: 编写脚本为博客配图批量添加水印
categories:
  - 独立博客
tags:
  - 版权
  - 知识共享
  - 脚本
abbrlink: 676734393
date: 2016-04-03 18:46:52
---

&emsp;&emsp;各位朋友，大家好，我是秦元培，欢迎大家关注我的博客，我的博客地址是[http://qinyuanpei.com](http://qinyuanpei.com)。今天想和大家分享下通过编写脚本来为博客配图批量添加水印，这个需求主要来自两个方面，其一是个人兴趣使然，其二是保护文章版权。我个人是非常不喜欢在图片上添加水印的，因为这样会破坏图片的美感。这样造成的后果就是，我的文章被某些网站非法转载以后赫然便添加上了这些网站的水印，对一个原创博客作者来说，这种行为就是赤裸裸的盗窃，除了伤害博客作者继续原创的积极性以外，我看不到任何的优点，我们常常吐槽在百度上检索不到优秀的中文内容，可实际上是因为复制和抄袭让真正优秀的内容无法进入公众视野。独立博客无论从流量还是名气上都无法和知名网站相提并论，因此在这种情况下如果知名网站无法在版权保护上做出表率，对博客作者来说没有比博客网页权重被降低更为气愤的事情了。

<!--more-->

&emsp;&emsp;国内对知识版权的无视让人常常无法适从，“可怜年年压金线，为他人做嫁衣裳”，如果转载的网站有着良好的阅读体验和稳定的阅读受众，我可以牺牲署名权和原始链接来让你继续侵权，可现实常常是各种靠网络爬虫来积累内容的站点，全然无视知识共享协议，在未经博客作者允许的情况下直接通过爬虫来抓取博客内容，因为通过爬虫抓取的内容无法保证良好的可读性，所以这类站点在降低博客阅读体验的同时，通过SEO让优质内容的关键字永远无法排在搜索结果前面，对这种行为我表示严厉谴责，再次声明，我的博客采用知识共享协议方式共享转载请注明文章作者、原始链接，为了表示对作者的尊重，请不要使用百度文库等公开性质的站点收集博客内容，建议使用笔记类产品进行收集，谢谢！那么，接下来我们说说给博客配图添加水印这件事情，这里我们尝试使用.NET中的GDI+来为图片添加水印。

<!--more-->


&emsp;&emsp;.NET中的GDI+可以轻松地绘制图形和文字，因此我们可以选择这种方式将文字水印绘制在输入的图片上然后输出。因为这个非常简单，所以这里直接给出代码：
```
 /// <summary>
 /// 向指定图片添加文字水印并保存到指定位置
 /// </summary>
 /// <param name="source">需要添加水印的图片</param>
 /// <param name="output">最终输出图片位置</param>
 /// <param name="text">文字水印内容</param>
 /// <param name="position">水印位置默认在右下角</param>
 private void AddWaterMark(string source, string output, string text, WaterMaterPosition position = WaterMaterPosition.RightBottom)
{
    //加载原始图片
    Image image = Image.FromFile(source);

    //构建GDI+位图
    Bitmap bitmap = new Bitmap(image.Width, image.Height);

    //取得绘图画面
    Graphics grap = Graphics.FromImage(bitmap);

    //绘制原始图片
    grap.Clear(Color.White);
    grap.DrawImage(image, new Rectangle(0, 0, image.Width, image.Height));

    //加载字体
    Font font = new Font("arial", 18);
    SizeF textSize= grap.MeasureString(text, font);

    //根据水印位置计算坐标
    float x = 0.0f;
    float y = 0.0f;
    switch (position)
    {
        case WaterMaterPosition.LeftTop:
            x = 0;
            y = 0;
            break;
        case WaterMaterPosition.LeftBottom:
            x = 0;
            y = image.Height - textSize.Height;
            break;
        case WaterMaterPosition.RightTop:
            x = image.Width - textSize.Width;
            y = 0;
            break;
        case WaterMaterPosition.RightBottom:
            x = image.Width - textSize.Width;
            y = image.Height - textSize.Height;
            break;
        case WaterMaterPosition.TopCenter:
            x = image.Width/2 - textSize.Width/2;
            y = 0;
            break;
        case WaterMaterPosition.BottomCenter:
            x = image.Width / 2 - textSize.Width/2;
            y = image.Height - textSize.Height;
            break;
        case WaterMaterPosition.Center:
            x = image.Width / 2 - textSize.Width/2;
            y = image.Height / 2 - textSize.Height/2;
            break;
    }

    //绘制文字
    SolidBrush brush = new SolidBrush(Color.FromArgb(125, 255,255,255));
    StringFormat format = new StringFormat { Alignment = StringAlignment.Near, FormatFlags = StringFormatFlags.NoWrap };
    grap.DrawString(text, font, brush, new RectangleF(x, y, textSize.Width, textSize.Height));

    //输出图片
    bitmap.Save(output, ImageFormat.Jpeg);
}
```
现在给图片添加水印只需要：
```
AddWaterMark("source.jpg", "output.jpg", "http://qinyuanpei.com");
```
添加完水印以后可以看看效果：

![未添加水印的原始图片]()

![添加水印后的输出图片]()

