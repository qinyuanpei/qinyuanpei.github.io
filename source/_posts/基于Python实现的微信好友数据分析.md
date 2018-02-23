---
title: 基于Python实现的微信好友数据分析
categories:
  - 数据分析
tags:
  - Python
  - Wechat
  - matplotlib
abbrlink: 2805694118
date: 2018-02-23 12:50:52
---
&emsp;&emsp;最近微信迎来了一次重要的更新，允许用户对"发现"页面进行定制。不知道从什么时候开始，微信朋友圈变得越来越复杂，当越来越多的人选择"仅展示最近三天的朋友圈"，大概连微信官方都是一脸的无可奈何。逐步泛化的好友关系，让微信从熟人社交逐渐过渡到陌生人社交，而朋友圈里亦真亦幻的状态更新，仿佛在努力证明每一个个体的"有趣"。有人选择在朋友圈里记录生活的点滴，有人选择在朋友圈里展示观点的异同，可归根到底，人们无时无刻不在窥探着别人的生活，唯独怕别人过多地了解自己的生活。人性中交织着的光明与黑暗，像一只浑身长满刺的刺猬，离得太远会感觉到寒冷，而靠得太近则害怕被刺扎到。朋友圈就像过年走亲戚，即便你心中有一万个不痛快，总是不愿意撕破脸，或屏蔽对方，或不给对方看，或仅展示最后三天，于是通讯录里的联系人越来越多，朋友圈越来越大，可再不会有能真正触动你内心的"小红点"出现，人类让一个产品变得越来越复杂，然后说它无法满足人类的需求，这大概是一开始就始料不及的吧！

# 引言

&emsp;&emsp;有人说，人性远比计算机编程更复杂，因为即使是人类迄今为止最伟大的发明——计算机，在面对人类的自然语言时同样会张惶失措 。人类有多少语言存在着模棱两可的含义，我认为语言是人类最大的误解，人类时常喜欢揣测语言背后隐藏的含义，好像在沟通时表达清晰的含义会让人类没有面子，更不用说网络上流行的猜测女朋友真实意图的案例。金庸先生的武侠小说《射雕英雄传》里，在信息闭塞的南宋时期，江湖上裘千丈的一句鬼话，就搅得整个武林天翻地覆。其实，一两句话说清楚不好吗？黄药师、全真七子、江南六怪间的种种纠葛，哪一场不是误会？一众儿武功震古烁今的武林高手，怎么没有丝毫的去伪存真的能力，语言造成了多少误会。

&emsp;&emsp;可即便人类的语言复杂得像一本无字天书，可人类还是从这些语言中寻觅到蛛丝马迹。古人有文王"拘而演周易"、东方朔测字卜卦，这种带有"迷信"色彩的原始崇拜，就如同今天人们迷信星座运势一般，都是人类在上千年的演变中不断对经验进行总结和训练的结果。如此说起来，我们的人工智能未尝不是一种更加科学化的"迷信"，因为数据和算法让我们在不断地相信，这一切都是真实地。生活在数字时代的我们，无疑是悲哀的，一面努力地在别人面前隐藏真实地自己，一面不无遗憾地感慨自己无处遁逃，每一根数字神经都紧紧地联系着你和我，你不能渴望任何一部数字设备具备真正的智能，可你生命里的每个瞬间，都在悄然间被数据地折射出来。

&emsp;&emsp;今天这篇文章会基于 Python 对微信好友进行数据分析，这里选择的维度主要有：性别、头像、签名、位置，主要采用图表和词云两种形式来呈现结果，其中，对文本类信息会采用词频分析和情感分析两种方法。常言道：工欲善其事，必先利其器也。在正式开始这篇文章前，简单介绍下本文中使用到的第三方模块：
* [itchat](https://github.com/littlecodersh/itchat)：微信网页版接口封装Python版本，在本文中用以获取微信好友信息。
* [jieba](https://github.com/fxsjy/jieba)：结巴分词的 Python 版本，在本文中用以对文本信息进行分词处理。
* [matplotlib](https://matplotlib.org/)： Python 中图表绘制模块，在本文中用以绘制柱形图和饼图
* [snownlp](https://github.com/isnowfy/snownlp)：一个 Python 中的中文分词模块，在本文中用以对文本信息进行情感判断。
* [PIL](http://www.pythonware.com/products/pil/)： Python 中的图像处理模块，在本文中用以对图片进行处理。
* [numpy](http://www.numpy.org/)： Python中 的数值计算模块，在本文中配合 [wordcloud](https://amueller.github.io/word_cloud/) 模块使用。
* [wordcloud](https://amueller.github.io/word_cloud/)： Python 中的词云模块，在本文中用以绘制词云图片。
* [TencentYoutuyun](https://github.com/Tencent-YouTu/Python_sdk)：腾讯优图提供的 Python 版本 SDK ，在本文中用以识别人脸及提取图片标签信息。
  &emsp;&emsp;以上模块均可通过 pip 安装，关于各个模块使用的详细说明，请自行查阅各自文档。
# 数据分析
&emsp;&emsp;分析微信好友数据的前提是获得好友信息，通过使用 itchat 这个模块，这一切会变得非常简单，我们通过下面两行代码就可以实现：
```Python
itchat.auto_login(hotReload = True)
friends = itchat.get_friends(update = True)
```
&emsp;&emsp;同平时登录网页版微信一样，我们使用手机扫描二维码就可以登录，这里返回的friends对象是一个集合，第一个元素是当前用户。所以，在下面的数据分析流程中，我们始终取friends[1:]作为原始输入数据，集合中的每一个元素都是一个字典结构，以我本人为例，可以注意到这里有Sex、City、Province、HeadImgUrl、Signature这四个字段，我们下面的分析就从这四个字段入手：

![好友信息结构展示](http://img.blog.csdn.net/20180223205004843)

## 好友性别

&emsp;&emsp;分析好友性别，我们首先要获得所有好友的性别信息，这里我们将每一个好友信息的Sex字段提取出来，然后分别统计出Male、Female和Unkonw的数目，我们将这三个数值组装到一个列表中，即可使用matplotlib模块绘制出饼图来，其代码实现如下：
```Python
def analyseSex(firends):
    sexs = list(map(lambda x:x['Sex'],friends[1:]))
    counts = list(map(lambda x:x[1],Counter(sexs).items()))
    labels = ['Unknow','Male','Female']
    colors = ['red','yellowgreen','lightskyblue']
    plt.figure(figsize=(8,5), dpi=80)
    plt.axes(aspect=1) 
    plt.pie(counts, #性别统计结果
            labels=labels, #性别展示标签
            colors=colors, #饼图区域配色
            labeldistance = 1.1, #标签距离圆点距离
            autopct = '%3.1f%%', #饼图区域文本格式
            shadow = False, #饼图是否显示阴影
            startangle = 90, #饼图起始角度
            pctdistance = 0.6 #饼图区域文本距离圆点距离
    )
    plt.legend(loc='upper right',)
    plt.title(u'%s的微信好友性别组成' % friends[0]['NickName'])
    plt.show()
```
&emsp;&emsp;这里简单解释下这段代码，微信中性别字段的取值有Unkonw、Male和Female三种，其对应的数值分别为0、1、2。通过Collection模块中的Counter()对这三种不同的取值进行统计，其items()方法返回的是一个元组的集合，该元组的第一维元素表示键，即0、1、2，该元组的第二维元素表示数目，且该元组的集合是排序过的，即其键按照0、1、2 的顺序排列，所以通过map()方法就可以得到这三种不同取值的数目，我们将其传递给matplotlib绘制即可，这三种不同取值各自所占的百分比由matplotlib计算得出。下图是matplotlib绘制的好友性别分布图：
![微信好友性别分析](http://img.blog.csdn.net/20180223205838851)
&emsp;&emsp;看到这个结果，我一点都不觉得意外，男女比例严重失衡，这虽然可以解释我单身的原因，可我不觉得通过调整男女比例就能解决问题，好多人认为自己单身是因为社交圈子狭小，那么是不是扩展了社交圈子就能摆脱单身呢？我觉得或许这样会增加脱单的概率，可幸运之神应该不会眷顾我，因为我的好运气早在我24岁以前就消耗完啦。在知乎上有一个热门的话题：[现在的男性是否普遍不再对女性展开追求了？](https://www.zhihu.com/question/55744630)，其实哪里会有人喜欢孤独呢？无非是怕一次又一次的失望罢了。有的人并不是我的花儿，我只是恰好途径了她的绽放。曾经有人说我是一个多情的人，可她永远不会知道，我做出的每一个决定都炽热而悲壮。所谓"慧极必伤，情深不寿；谦谦君子，温润如玉"，世人苦五毒者大抵如此。

## 好友头像

&emsp;&emsp;分析好友头像，从两个方面来分析，第一，在这些好友头像中，使用人脸头像的好友比重有多大；第二，从这些好友头像中，可以提取出哪些有价值的关键字。这里需要根据HeadImgUrl字段下载头像到本地，然后通过[腾讯优图](http://youtu.qq.com/#/home)提供的人脸识别相关的API接口，检测头像图片中是否存在人脸以及提取图片中的标签。其中，前者是分类汇总，我们使用饼图来呈现结果；后者是对文本进行分析，我们使用词云来呈现结果。关键代码如下 所示：
```Python
def analyseHeadImage(frineds):
    # Init Path
    basePath = os.path.abspath('.')
    baseFolder = basePath + '\\HeadImages\\'
    if(os.path.exists(baseFolder) == False):
        os.makedirs(baseFolder)

    # Analyse Images
    faceApi = FaceAPI()
    use_face = 0
    not_use_face = 0
    image_tags = ''
    for index in range(1,len(friends)):
        friend = friends[index]
        # Save HeadImages
        imgFile = baseFolder + '\\Image%s.jpg' % str(index)
        imgData = itchat.get_head_img(userName = friend['UserName'])
        if(os.path.exists(imgFile) == False):
            with open(imgFile,'wb') as file:
                file.write(imgData)

        # Detect Faces
        time.sleep(1)
        result = faceApi.detectFace(imgFile)
        if result == True:
            use_face += 1
        else:
            not_use_face += 1 

        # Extract Tags
        result = faceApi.extractTags(imgFile)
        image_tags += ','.join(list(map(lambda x:x['tag_name'],result)))
    
    labels = [u'使用人脸头像',u'不使用人脸头像']
    counts = [use_face,not_use_face]
    colors = ['red','yellowgreen','lightskyblue']
    plt.figure(figsize=(8,5), dpi=80)
    plt.axes(aspect=1) 
    plt.pie(counts, #性别统计结果
            labels=labels, #性别展示标签
            colors=colors, #饼图区域配色
            labeldistance = 1.1, #标签距离圆点距离
            autopct = '%3.1f%%', #饼图区域文本格式
            shadow = False, #饼图是否显示阴影
            startangle = 90, #饼图起始角度
            pctdistance = 0.6 #饼图区域文本距离圆点距离
    )
    plt.legend(loc='upper right',)
    plt.title(u'%s的微信好友使用人脸头像情况' % friends[0]['NickName'])
    plt.show() 

    image_tags = image_tags.encode('iso8859-1').decode('utf-8')
    back_coloring = np.array(Image.open('face.jpg'))
    wordcloud = WordCloud(
        font_path='simfang.ttf',
        background_color="white",
        max_words=1200,
        mask=back_coloring, 
        max_font_size=75,
        random_state=45,
        width=800, 
        height=480, 
        margin=15
    )

    wordcloud.generate(image_tags)
    plt.imshow(wordcloud)
    plt.axis("off")
    plt.show()
```
&emsp;&emsp;这里我们会在当前目录新建一个HeadImages目录，用以存储所有好友的头像，然后我们这里会用到一个名为FaceApi类，这个类由腾讯优图的SDK封装而来，这里分别调用了[人脸检测](http://youtu.qq.com/#/develop/api-face-analysis-detect)和[图像标签识别](http://youtu.qq.com/#/develop/api-image-tag)两个API接口，前者会统计"使用人脸头像"和"不使用人脸头像"的好友各自的数目，后者会累加每个头像中提取出来的标签。其分析结果如下图所示：
![](http://img.blog.csdn.net/20180223224120825)
&emsp;&emsp;可以注意到在所有微信好友中，约有接近1/4的微信好友使用了人脸头像， 而有接近3/4的微信好友没有人脸头像，这说明在所有微信好友中对"颜值 "有自信的人，仅仅占到好友总数的25%，或者说75%的微信好友行事风格偏低调为主，不喜欢用人脸头像做微信头像。这是否说明"好看的皮囊"并非是千篇一律，长得好看的人实在是少数中的少数。所以，当女生的妆容越来越向着"韩式半永久粗平眉"、"瓜子脸"和"大红唇"靠拢的时候，当男生的服饰越来越向着"大背头"、"高领毛衣"和"长款大衣"靠拢的时候，我们能不能真正得个性一次。生命中有太多被世俗绑架着的事情，既要和别人不一样 ，同时还要和大多数人一样，这是人生在世的无可奈何。考虑到腾讯优图并不能真正得识别"人脸"，我们这里对好友头像中的标签再次进行提取，来帮助我们了解微信好友的头像中有哪些 关键词，其分析结果如图所示：
![微信好友头像标签词云展示]()
&emsp;&emsp;通过词云，我们可以发现：在微信好友中

## 好友签名

&emsp;&emsp;分析好友签名，签名是好友信息中最为丰富的文本信息，按照人类惯用的"贴标签"的方法论，签名可以分析出某一个人在某一段时间里状态，就像人开心了会笑、哀伤了会哭，哭和笑两种标签，分别表明了人开心和哀伤的状态。这里我们对签名做两种处理，第一种是使用用结巴分词进行分词后生成词云，目的是了解好友签名中的关键字有哪些，哪一个关键字出现的频率相对较高；第二种是使用SnowNLP分析好友签名中的感情倾向，即好友签名整体上是表现为正面的、负面的还是中立的，各自的比重是多少。这里提取Signature字段即可，其核心代码如下：
```Python

```
&emsp;&emsp;通过词云，我们可以发现：在微信好友中

&emsp;&emsp;通过柱状图，我们可以发现：在微信好友中

## 好友位置

&emsp;&emsp;分析好友位置，主要通过提取Province和City这两个字段。Python中的地图可视化主要通过Basemap模块，这个模块需要从国外网站下载地图信息，使用起来非常的不便。百度的[ECharts](http://echarts.baidu.com/)在前端使用的比较多，虽然社区里提供了[pyecharts](http://pyecharts.org/)项目，可我注意到因为政策的改变，目前Echarts不再支持导出地图的功能，所以地图的定制方面目前依然是一个问题，主流的技术方案是配置全国各省市的JSON数据，这里博主使用的是[BDP个人版](https://me.bdp.cn/home.html)，这是一个零编程的方案，我们通过Python导出一个CSV文件，然后将其上传到BDP中，通过简单拖拽就可以制作可视化地图，简直不能再简单，这里我们仅仅展示生成CSV部分的代码：
```Python
def analyseLocation(friends):
    headers = ['NickName','Province','City']
    with open('location.csv','w',encoding='utf-8',newline='',) as csvFile:
        writer = csv.DictWriter(csvFile, headers)
        writer.writeheader()
        for friend in friends[1:]:
           row = {}
           row['NickName'] = friend['NickName']
           row['Province'] = friend['Province']
           row['City'] = friend['City']
           writer.writerow(row)
```
&emsp;&emsp;下图是BDP中生成的微信好友地理分布图，可以发现：我的微信好友主要集中在宁夏和陕西两个省份。数字时代的神经牵动着每一个社交关系链的人，我们想要竭力去保护的那点隐私，在这些数据中一点点地折射出来。人类或许可以不断地伪装自己，可这些从数据背后抽离出来的规律和联系不会欺骗人类。数学曾经被人称为最没有用的学科，因为生活中并不需要神圣而纯粹的计算，在不同的学科知识里，经验公式永远比理论公式更为常用。可是此时此刻，你看，这世界就像一只滴滴答答转动着的时钟，每一分每一秒都是严丝合缝的。
![微信好友地理分布图](http://img.blog.csdn.net/20180223234011645)

# 本文小结
&emsp;&emsp;写这篇文章的时候，我一直不知道该如何下笔，因为微信是一个神奇的存在，它是一个国民级别的全民APP，所以，微信的产品设计一直都是一个有趣的现象，从最初底部Tab的数目、每个Tab的名称、"发现"页面的定制、小程序入口、朋友圈入口到朋友圈评论等等一系列的设计细节，都是值得我们透过人性和心理去研究的。即使是被人们封神的"张小龙"，在面对结构最为复杂的中国用户群体的时候，他的潇洒中依旧不免充满无奈，从对朋友圈的置之不理就可以看出，这是一个怎么做都不会让人满意的功能，任何一个生态在面对巨大的用户群体的时候，功能的增减就会变成一个难题，所谓"林子大了什么鸟都有"，知乎面对的是同样的问题，营销类公众号在不断消费社会话题的同时，引导着一批又一批粉丝的价值取向，人类总渴望着别人了解自己，可人类真的了解自己吗？这篇博客是我对数据分析的又一次尝试，主要从性别、头像、签名、位置四个维度，对微信好友进行了一次简单的数据分析，主要采用图表和词云两种形式来呈现结果。总而言之一句话，"数据可视化是手段而并非目的"，重要的不是我们在这里做了这些图出来，而是从这些图里反映出来的现象，我们能够得到什么本质上的启示，我一位朋友问我怎么什么都想抓取，为什么啊，因为我不懂人类啊！
