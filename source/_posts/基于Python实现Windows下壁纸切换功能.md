---
abbrlink: 2822230423
categories:
- 编程语言
date: 2018-02-05 16:48:39
description: 本文使用Python实现了Windows下切换壁纸的功能，通过requests模块从网络上抓取图片，通过PIL模块实现JPEG格式到BMP格式的转换，通过win32api和win32gui模块实现壁纸设置，并通过修改注册表的方式，将这一功能整合到系统菜单中，可以非常便捷地更换桌面壁纸
tags:
- Python
- 脚本
- Windows
title: 基于Python实现Windows下壁纸切换功能
---

&emsp;&emsp;在过去一年多的时间里，我尝试改变博客的写作风格，努力让自己不再写教程类文章，即使在这个过程中，不断地面临着写作内容枯竭的痛苦。因为我渐渐地意识到，告诉别人如何去做一件事情，始终停留在"术"的层面，而比这个更为重要的是，告诉别人为什么要这样做，这样就可以过渡到"道"的层面。古人云：形而上者谓之道，形而下者谓之器。我们常常希望通过量变来产生质变，可是如果在这个过程中不能及时反思和总结，我们认为的努力或许仅仅是重复的劳作而已。如你所见，在这篇文章里，我们将通过Python和Windows注册表实现壁纸切换功能，主要涉及到的Python中的requests、pyinstaller这两个模块的使用，希望大家喜欢。

# 故事缘由
&emsp;&emsp;人们常常相信事出有因，可这世界上有些事情，哪里会有什么原因啊，比如喜欢与不喜欢。做这样一个小功能的初衷，起源于我对桌面壁纸的挑剔。作为一个不完全的强迫症患者，我需要花费大量时间去挑选一张壁纸，丝毫不亚于在网上挑选一件喜欢的商品。我注意到知乎上有这样的话题：[有哪些无版权图片网站值得推荐？](https://www.zhihu.com/question/22857942)，因此对于桌面壁纸的筛选，我渐渐地开始摆脱对搜索引擎的依赖，我个人比较喜欢[Pexels](https://www.pexels.com)和[Unsplash](https://unsplash.com/)这两个网站，所以我想到了从这两个网站抓取图片来设置Windows壁纸的方案。市面上类似的商业软件有[百度壁纸](http://bizhi.baidu.com/)、[搜狗壁纸](http://bizhi.sogou.com/index.html)等，可这些软件都不纯粹，或多或少地掺杂了额外功能，个中缘由想来大家都是知道的。联想到微信最新版本的更新，"发现"页面支持所有项目的隐藏，甚至是盟友京东的电商入口和腾讯最赚钱的游戏入口，这让我开始正视腾讯这家公司，我收回曾经因为抄袭对腾讯产生的不满，腾讯是一家值得尊重的互联网公司。做一个纯粹的应用程序，这就是我的初心。

# 设计实现
&emsp;&emsp;好了，现在我们考虑如何来实现这个功能，我们的思路是从[Unsplash](https://unsplash.com/)这个网站抓取图片，并将其存储在指定路径，然后通过Windows API完成壁纸的设置。Python脚本会通过pyinstaller模块打包成可执行文件，我们通过修改注册表的方式，在右键菜单内加入切换壁纸的选项，这样我们可以直接通过右键菜单实现壁纸切换功能。在编写脚本的时候，起初想到的是抓包这样的常规思路，因为请求过程相对复杂而失败，后来意外地发现官方提供了API接口。事实上[Pexels](https://www.pexels.com)和[Unsplash](https://unsplash.com/)都提供了API接口，通过调用这些API接口，我们的探索进行得非常顺利，下面是具体脚本实现：
```Python
# Query Images
searchURL = 'https://unsplash.com/napi/search?client_id=%s&query=%s&page=1'
client_id = 'fa60305aa82e74134cabc7093ef54c8e2c370c47e73152f72371c828daedfcd7'
categories = ['nature','flowers','wallpaper','landscape','sky']
searchURL = searchURL % (client_id,random.choice(categories))
response = requests.get(searchURL)
print(u'正在从Unsplash上搜索图片...')

# Parse Images
data = json.loads(response.text)
results = data['photos']['results']
print(u'已为您检索到图片共%s张' % str(len(results)))
results = list(filter(lambda x:float(x['width'])/x['height'] >=1.33,results))
result = random.choice(results)
resultId = str(result['id'])
resultURL = result['urls']['regular']

# Download Images
print(u'正在为您下载图片:%s...' % resultId)
basePath = sys.path[0]
if(os.path.isfile(basePath)):
    basePath = os.path.dirname(basePath)
baseFolder = basePath + '\\Download\\'
if(not path.exists(baseFolder)):
    os.makedirs(baseFolder)
jpgFile = baseFolder + resultId + '.jpg'
bmpFile = baseFolder + resultId + '.bmp'
response = requests.get(resultURL)
with open(jpgFile,'wb') as file:
    file.write(response.content)
img = Image.open(jpgFile)
img.save(bmpFile,'BMP')
os.remove(jpgFile)
```
&emsp;&emsp;这部分代码非常简单，需要关注的地方有：第一，这个API对应的密钥是公共的，即所有人都可以使用，这里随机从指定的分类中去搜索图片。第二，这里使用filter()函数过滤出宽高比超过1.33的图片，即分辨率为1366 * 768的图片。这里需要注意的是，在Python3.X下filter需要转化为list，否则会引发一个异常。第三，下载的图片默认为JPEG格式，而Windows下设置壁纸使用的是位图格式，即BMP格式，所以在这里我们使用PIL模块来完成格式转换。这里需要注意的是，PIL模块目前不支持Python3.X以后的版本，我们这里使用的是Pillow模块，该模块可以通过pip直接完成安装。

&emsp;&emsp;现在，我们将壁纸下载到本地以后，就可以着手设置壁纸相关的工作。这些工作主要借助为win32api和win32gui这两个内置模块，我们一起来看具体代码：
```Python
print(u'正在设置图片:%s为桌面壁纸...' % resultId)
key = win32api.RegOpenKeyEx(win32con.HKEY_CURRENT_USER,
    "Control Panel\\Desktop",0,win32con.KEY_SET_VALUE)
win32api.RegSetValueEx(key, "WallpaperStyle", 0, win32con.REG_SZ, "2") 
#2拉伸适应桌面,0桌面居中
win32api.RegSetValueEx(key, "TileWallpaper", 0, win32con.REG_SZ, "0")
win32gui.SystemParametersInfo(win32con.SPI_SETDESKWALLPAPER, bmpFile, 1+2)
print(u'成功应用图片:%s为桌面壁纸'  % resultId)
```
&emsp;&emsp;这部分内容非常简单，基本没有复杂的东西在里面。接下来我们需要通过pyinstaller模块将脚本打包成可执行文件，实际上这个步骤完全可以省略，因为现在我们通过命令行就可以实现壁纸切换，为什么要做这样额外的工作呢？考虑到Windows下GUI更为便捷一点，所以我们打包成可执行文件，主要是为了给右键菜单添加功能，我们最终点击想要实现的功能是，点击右键菜单就可以完成壁纸的切换。首先通过pip安装pyinstaller模块，在终端下执行命令：
```Shell
python -m pip install pyinstaller
```
安装完成后按照[官方](http://www.pyinstaller.org/)文档即可在./dist/目录中找到生成的可执行文件，如果打包出错可以修改Python根目录下的./Scripts/pyinstaller-script.py文件，修改第一行Python.exe的路径，删除两端的引号即可，如下图所示。关于pyinstaller模块打包时的详细参数设定，请自行查阅官方文档。

![pyinstaller-script.py文件](https://ww1.sinaimg.cn/large/4c36074fly1fzixyh5f8bj20wl0aj3za.jpg)

&emsp;&emsp;现在，在生成可执行文件以后，我们打开注册表，定位到以下节点：
**计算机\HKEY_CLASSES_ROOT\Directory\Background\shell**，然后创建一级子节点WallPaper，其默认值填写"更换壁纸"，接下来创建二级子节点command，注意这个名称不能修改，其默认值填写可执行文件路径，本例中为：E:\Software\WallPaper\main.exe，如下图所示：

![为右键菜单增加更换壁纸选项](https://ww1.sinaimg.cn/large/4c36074fly1fzixbecv5vj20vp0g3myc.jpg)

&emsp;&emsp;好了，现在我们可以看看在右键菜单中增加"更换壁纸"选项以后的效果：
![最终效果](https://ww1.sinaimg.cn/large/4c36074fly1fzix8icn54g20xi0ize81.jpg)

# 文本小结
&emsp;&emsp;本文使用Python实现了Windows下切换壁纸的功能，通过requests模块从网络上抓取图片，通过PIL模块实现JPEG格式到BMP格式的转换，通过win32api和win32gui模块实现壁纸设置，并通过修改注册表的方式，将这一功能整合到系统菜单中，可以非常便捷地更换桌面壁纸。作为一个设计上的扩展，我们需要考虑更多的问题，比如当网络断开的时候如何避免异常，如何接入更多的在线图库API，如何支持可配置的图片分类信息以及如何将修改注册表的过程自动化等等，这些问题博主会利用空闲时间去解决，今天这篇文章就是这样啦，本文源代码可以通过[这里](https://github.com/qinyuanpei/WallPaper)获取，谢谢大家！