---
abbrlink: 1960676615
categories:
- 编程语言
date: 2019-10-11 08:56:27
description: 考虑到 Python 是一门解释型的语言，我们在编写插件的时候，更希望做到“热插拔”，比如修改了某个插件后，希望它可以立刻生效，这个时候我们就需要重新加载模块，此时 importlib 的 reload 就能满足我们的要求，这正是博主一开始就要使用 importlib，而不是 import 语法对应内建方法__import__()的原因;好了，现在我们就完成了这次“插件化”的迭代，截止到目前为止，博主共完成了
  [Unsplash](.) 、 [Bing 壁纸](.) 、 [WallHaven](.) 和 [国家地理](.) 四个“源”的接入，这些插件在实现上基本大同小异，本质上来讲它们是一个又一个的爬虫，只要实现了 getImage()这个方法都可以接入进来，这就是我们通常说的“约定大于配置”，关于更多的代码细节，大家可以通过[Github]((https://github.com/qinyuanpei/WallPaper))来了解;mkt=zh-CN)
  和 [WallHaven](https://wallhaven.cc) 两个壁纸来源，考虑到大多数的壁纸抓取流程是一样的，博主决定以“插件”的方式完成这次迭代，换句话说，主程序不需要再做任何调整，当我们希望增加新的数据源的时候，只需要写一个.py 脚本即可，这就是今天这篇文章的写作缘由
tags:
- Python
- 插件化
- 壁纸
title: 使用 Python 开发插件化应用程序
---

插件化应用是个老话题啦，在我们的日常生活中更是屡见不鲜。无论是多年来臃肿不堪的 Eclipse，亦或者是扩展丰富著称的 Chrome，乃至近年来最优秀的编辑器 VSCode，插件都是这其中重要的组成部分。插件的意义在于扩展应用程序的功能，这其实有点像 iPhone 手机和 AppStore 的关系，没有应用程序的手机无非就是一部手机，而拥有了应用程序的手机则可以是 Everything。显然，安装或卸载应用程序并不会影响手机的基本功能，而应用程序离开了手机同样无法单独运行。所以，所谓“插件”，实际上是**一种按照一定规范开发的应用程序，它只能运行在特定的软件平台/应用程序且无法运行**。这里，最重要的一点是应用程序可以不依赖插件单独运行，这是这类“插件式”应用的基本要求。

好了，在了解了插件的概念以后，我们来切入今天的正文。博主曾经在[《基于 Python 实现 Windows 下壁纸切换功能》](https://blog.yuanpei.me/posts/2822230423/)这篇文章中编写了一个小程序，它可以配合 Windows 注册表实现从 [Unsplash](https://unsplash.com/) 上抓取壁纸的功能。最近，博主想为这个小程序增加 [必应壁纸](https://cn.bing.com/?mkt=zh-CN) 和 [WallHaven](https://wallhaven.cc) 两个壁纸来源，考虑到大多数的壁纸抓取流程是一样的，博主决定以“插件”的方式完成这次迭代，换句话说，主程序不需要再做任何调整，当我们希望增加新的数据源的时候，只需要写一个.py 脚本即可，这就是今天这篇文章的写作缘由。同样的功能，如果使用 Java/C#这类编译型语言来做，我们可能会想到为插件定义一个 IPlugin 接口，这样每一个插件实际上都是 IPlugin 接口的实现类，自然而然地，我们会想到通过反射来调用接口里的方法，这是编译型语言的做法。而面对 Python 这样的解释型语言，我们同样有解释型语言的做法。

首先，我们从一个最简单的例子入手。我们知道，Python 中的 import 语法可以用来引入一个模块，这个模块可以是 Python 标准库、第三方库和自定义模块。现在，假设我们有两个模块：`foo.py` 和 `bar.py`。

```Python
#foo.py
import sys

class Chat:

    def send(self,uid,msg):
        print('给{uid}发送消息：{msg}'.format(uid=uid,msg=msg))

    def sendAll(self,msg):
        print('群发消息：{msg}'.format(msg=msg))
```

---

```Python
#bar.py
import sys

class Echo:

    def say(self):
        print("人生苦短，我用Python")

def cry():
    print("男人哭吧哭吧不是罪")
```


通常, 为了在当前模块(main.py)中使用这两个模块，我们可以使用以下语句：

```Python
import foo
from bar import *
```

这是一种简单粗暴的做法，因为它会导入模块中的全部内容。一种更好的做法是按需加载，例如下面的语句：

```Python
from foo import Chat
```

到这里，我们先来思考第一个问题，Python 是怎么样去查找一个模块的呢？这和 Python 中的导入路径有关，通过`sys.path`我们可以非常容易地找到这些路径，常见的导入路径有`当前目录`、`site-package目录`和`PYTHONPATH`。熟悉 Python 的朋友应该都知道，`site-package`和`PYTHONPATH`各自的含义，前者是通过 pip 安装的模块的导入目录，后者是 Python 标准库的导入目录。当前目录这个从何说起呢？事实上，从我们写下`from…import…`语句的时候，这个机制就已经在工作了，否则 Python 应该是找不到 foo 和 bar 这两个模块的了。这里还有相对导入和绝对导入的问题，一个点(`.`)和两个点(`..`)的问题，这些我们在这里暂且按下不表，因为我们会直接修改`sys.path`(逃

在 Python 中有一种动态导入模块的方式，我们只需要告诉它模块名称、导入路径就可以了，这就是下面要说的`importlib`标准库。继续用 foo 和 bar 这两个神奇的单词来举例，假设我们现在不想通过 import 这种偏“静态”的方式导入一个模块，我们应该怎么做呢？一起来看下面代码：

```Python
import foo
from foo import Chat
from bar import *
import importlib

#调用foo模块Chat类方法
foo.Chat().send('Dear','I Miss You')
moduleFoo = importlib.import_module('.','foo')
classChat = getattr(moduleFoo,'Chat')
classChat().send('Dear','I Miss You')

#调用bar模块Echo类方法
Echo().say()
moduleBar = importlib.import_module('.','bar')
classEcho = getattr(moduleBar,'Echo')
classEcho().say()

#调用bar模块中的cry()方法
cry()
methodCry = getattr(moduleBar,'cry')
methodCry()
```

可以注意到，动态导入可以让我们在运行时期间引入一个模块(.py)，这恰恰是我们需要的功能。为了让大家对比这两种方式上的差异，我给出了静态引入和动态引入的等价代码。其中，`getattr()`其实可以理解为 Python 中的反射，我们总是可以按照`模块`->`类`->`方法`的顺序来逐层查找,即：通过 dir()方法，然后该怎么调用就怎么调用。所以，到这里整个“插件化”的思路就非常清晰了，即：首先，通过配置来为 Python 增加一个导入路径，这个导入路径本质上就是插件目录。其次，插件目录内的每一个脚本文件(.py)就是一个模块，每个模块都有一个相同的方法签名。最终，通过配置来决定要导入哪一个模块，然后调用模块中类的实例方法即可。顺着这个思路，博主为 [WallPaper](https://github.com/qinyuanpei/WallPaper) 项目引入了插件机制，核心代码如下：

```Python
if(pluginFile == '' or pluginName == ''):
        spider = UnsplashSpider()
        imageFile = spider.getImage(downloadFolder)
        setWallPaper(imageFile)
    else:
        if(not check(pluginFile,addonPath)):
            print('插件%s不存在或配置不正确' % pluginName)
            return
        module = importlib.import_module('.',pluginFile.replace('.py',''))
        instance = getattr(module,pluginName)
        imageFile = instance().getImage(downloadFolder)
        setWallPaper(imageFile)
```
接下来，我们可以很容易地扩展出 [必应壁纸](https://cn.bing.com/?mkt=zh-CN) 和 [WallHaven](https://wallhaven.cc) 两个“插件”。按照约定，这两个插件都必须实现 getImage()方法，它接受一个下载目录作为参数，所以，显而易见，我们在这个插件里实现壁纸的下载，然后返回壁纸的路径即可，因为主程序会完成剩余设置壁纸的功能。

```Python
# 必应每日壁纸插件
class BingSpider:

    def getImage(self, downloadFolder):
        searchURL = 'https://cn.bing.com/HPImageArchive.aspx?format=js&idx=0&n=1&mkt=zh-CN'
        response = requests.get(searchURL)
        data = json.loads(response.text)

        resultId = data['images'][0]['hsh']
        resultURL = 'https://cn.bing.com' + data['images'][0]['url']
        print(u'正在为您下载图片:%s...' % resultId)
        if(not path.exists(downloadFolder)):
            os.makedirs(downloadFolder)
        
        jpgFile = resultId + '.jpg'
        jpgFile = os.path.join(downloadFolder, jpgFile)
        response = requests.get(resultURL)
        with open(jpgFile,'wb') as file:
            file.write(response.content)
        return jpgFile      
```

---

```Python
# WallHaven壁纸插件
class WallHavenSpider:

    def getImage(self,downloadFolder): 
        url = 'https://alpha.wallhaven.cc/wallpaper/' 
        response = requests.get(url) 
        print(response.text)
        soup = BeautifulSoup(response.text,'html.parser')
        imgs = soup.find_all('img')
        length = len(imgs)
        if length > 0:
            match = random.choice(imgs)
            rawUrl = match.get('src')
            rawId = rawUrl.split('/')[-1]
            rawUrl = 'https://w.wallhaven.cc/full/' + rawId[0:2] + '/wallhaven-' + rawId
            raw = requests.get(rawUrl) 
            imgFile = os.path.join(downloadFolder, rawId)
            with open(imgFile,'wb') as f:
                f.write(raw.content)
        return imgFile  
```

好了，现在功能是实现了，我们来继续深入“插件化”这个话题。考虑到 Python 是一门解释型的语言，我们在编写插件的时候，更希望做到“热插拔”，比如修改了某个插件后，希望它可以立刻生效，这个时候我们就需要重新加载模块，此时 importlib 的 reload 就能满足我们的要求，这正是博主一开始就要使用 importlib，而不是 import 语法对应内建方法__import__()的原因。以 C#的开发经历而言，虽然可以直接更换 DLL 实现更新，可更新的过程中 IIS 会被停掉，所以，这种并不能被称之为“热更新”。基于以上两点考虑，博主最终决定使用 watchdog 配合 importlib 来实现“热插拔”，下面是关键代码：
```Python
class LoggingEventHandler(FileSystemEventHandler):

    # 当配置文件修改时重新加载模块
    # 为节省篇幅已对代码进行精简
    def on_modified(self, event):
        super(LoggingEventHandler, self).on_modified(event)
        what = 'directory' if event.is_directory else 'file'
        confPath = os.path.join(sys.path[0],'config.ini')
        if(what =='file' and event.src_path == confPath):
            importlib.reload(module)
        logging.info("Modified %s: %s", what, event.src_path)
```
好了，现在我们就完成了这次“插件化”的迭代，截止到目前为止，博主共完成了 [Unsplash](.) 、 [Bing 壁纸](.) 、 [WallHaven](.) 和 [国家地理](.) 四个“源”的接入，这些插件在实现上基本大同小异，本质上来讲它们是一个又一个的爬虫，只要实现了 getImage()这个方法都可以接入进来，这就是我们通常说的“约定大于配置”，关于更多的代码细节，大家可以通过[Github]((https://github.com/qinyuanpei/WallPaper))来了解。

简单回顾下这篇博客，核心其实是 importlib 模块的使用，它可以让我们在运行时期间动态导入一个模块，这是实现插件化的重要前提。以此为基础，我们设计了基于 Python 脚本的单文件插件，即从指定的目录加载脚本文件，每个脚本就是一个插件。而作为插件化的一个延伸，我们介绍了 watchdog 模块的简单应用，配合 importlib 模块的 reload()方法，就可以实现所谓的“热更新”。好了，以上就是这篇博客的所有内容了，我们下一篇见！