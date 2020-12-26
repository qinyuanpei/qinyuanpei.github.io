---
toc: true
title: 视频是不能P的系列：OpenCV人脸检测
categories:
  - 编程语言
tags:
  - OpenCV
  - Python
  - 图像处理
  - 人脸检测
copyright: true
abbrlink: 2997581895
date: 2020-12-25 22:49:47
---
恍惚间，2020年已接近尾声，回首过去这一年，无论是疫情、失业还是“996”，均以某种特殊的方式铭刻着这一年的记忆。也许，是这个冬天的西安雾霾更少一点。所以，有时透过中午的一抹冬阳，居然意外地觉得春天的脚步渐渐近了，甚至连圣诞节这种“洋节日”都感到亲切而且期待，我想，这大概是我丧了一段时间的缘故吧！可不管怎样，人们对未来的生活时常有一种“迷之自信”，果然生还还是要继续下去的呀！趁着最近的时间比较充裕，我决定开启一个信息的系列：视频是不能P的。这是互联网上流传的一个老梗了，正所谓“视频是不能P的，所以是真的”。其实，在如今这个亦真亦假的世界里，哪里还有什么东西是不能PS的呢？借助人工智能“改头换面”越来越轻而易举，而这背后关于隐私和伦理的一连串问题随之而来，你越来越难以确认屏幕对面的那个是不是真实的人类。所以，这个系列会以OpenCV作为起点，去探索那些好玩、有趣的视频/图像处理思路，通过技术来证明视频是可以被PS的。而作为这个系列的第一篇，我们将从一个最简单的地方开始，它就是人脸检测。

# 第一个入门示例

学习OpenCV最好的方式，就是从官方的示例开始，我个人非常推荐的两个教程是 [OpenCV: Cascade Classifier](https://docs.opencv.org/3.4/db/d28/tutorial_cascade_classifier.html) 和 [Python OpenCV Tutorial](https://pythonexamples.org/python-opencv/)，其次是 [浅墨大神](https://blog.csdn.net/poem_qianmo) 的[【OpenCV】入门教程](https://blog.csdn.net/poem_qianmo/category_9262318.html)，不同的是， [浅墨大神](https://blog.csdn.net/poem_qianmo) 的教程主要是使用C++，对于像博主这样的“不学无术”的人，这简直无异于从入门到放弃，所以，建议大家结合自己的实际情况，选择适合自己的“难度”。好了，思绪拉回我们这里，在OpenCV中实现人脸检测，主要分为以下三个步骤，即，首先，定义联级分类器**CascadeClassifier**并载入指定的模型文件；其次，对待检测目标进行灰度化和直方图均衡化处理；最后，对灰度图调用`detectMultiScale()`方法进行检测。下面是一个简化过的入门示例，使用世界上最省心的Python语言进行编写：

```Python
import cv2

# 步骤1: 定义联级分类器CascadeClassifier并载入指定的模型文件
faceCascade = cv2.CascadeClassifier('./haarcascades/haarcascade_frontalface_alt2.xml')

# 步骤2: 对待检测目标进行灰度化和直方图均衡化处理
target = cv2.imread('target.jpg')
target_gray = cv2.cvtColor(target, cv2.COLOR_BGR2GRAY)
target_gray = cv2.equalizeHist(target_gray)

# 步骤3: 人脸检测
faces = faceCascade.detectMultiScale(target_gray)
for (x,y,w,h) in faces:
    cv2.rectangle(target, (x, y), (x + w, y + h), (0, 255, 0), 2)

# 步骤4: 展示结果
cv2.imshow('Face Detection', target)
cv2.waitKey(0)
cv2.destroyAllWindows() 
```
正常情况下，你会得到下面的结果，这里选取的素材是经典日剧《半泽直树》：

![OpenCV人脸检测效果展示](https://i.loli.net/2020/12/25/DcQRW32aUTBx5lY.png)

怎么样？是不是被OpenCV的强大给震惊到了？下面我们针对每个步骤做更详细的说明：
* 第1行引入OpenCV，需要我们安装OpenCV的[Python版本](https://pypi.org/project/opencv-python/)。
* 第4行实例化级联分类器CascadeClassifier，关于这个级联分类器，它是OpenCV下做目标检测的模块，内置**Haar**、**HOG**和**LBP**三类特性算法，而所谓“级联”，则是指它通过多个强分类器串联实现最终分类的思路。在初始化级联分类器的时候，需要载入指定的模型文件，这些模型文件是官方提前训练好的，可以从[Github](https://github.com/opencv/opencv/tree/master/data/haarcascades)上进行下载，不同的模型文件对应不同的功能，这里使用的`haarcascade_frontalface_alt2.xml`主要针对面部检测，而像`haarcascade_eye_tree_eyeglasses.xml`则可以对眼睛进行检测。除此之外，我们还通过训练获得自己的模型文件，当然，这一切都是后话啦！
* 第7~9行，我们载入了一张图片素材，并对其进行了灰度化和直方图均衡化处理。这里需要关注的三个函数是：[imread]()、[cvtColor](https://docs.opencv.org/3.4/d8/d01/group__imgproc__color__conversions.html#ga397ae87e1288a81d2363b61574eb8cab) 和 [equalizeHist](https://docs.opencv.org/3.4/d6/dc7/group__imgproc__hist.html#ga7e54091f0c937d49bf84152a16f76d6e)，它们的作用分别是读取图片、转换颜色和直方图均衡化处理。其中，对人脸检测而言，灰度图是必要的条件，而直方图均衡化则是可选的一个过程。
* 第12~14行，通过 [detectMultiScale](https://docs.opencv.org/3.4/d1/de5/classcv_1_1CascadeClassifier.html#aaf8181cb63968136476ec4204ffca498) 方法我们就可以对待检测目标进行检测，关于它的参数，常用的有scaleFactor、minNeighbors、minSize、maxSize，它可以对人脸检测做进一步的细节上控制，对于我们而言，我们更关心检测的结果，这里我们将检测到的人脸区域以矩形的方式绘制出来。
* 第17~19行，主要是为了方面大家观察结果，实际使用中可能会输出为文件或者实时渲染，这里需要关注的重点函数是：[imshow](https://docs.opencv.org/3.4/df/d24/group__highgui__opengl.html#gaae7e90aa3415c68dba22a5ff2cefc25d)，顾名思义，它可以让图片展示在窗口中，类似我们这个示例中的效果。

# 柴犬界的“网红”

曾经，有“好事者”分析过微信和QQ的年度表情，表情包文化流行的背后，实际上表达方式多样化的一种体现，例如：“笑哭”这一符号，固然有哭笑不得的含义在里面，可又何尝不是**二十多岁人生总是边哭边笑的真实写照**呢？而“捂脸”这一符号在我看来更多的是一种无可奈何，甚至有一种自我嘲讽的意味在里面。至于“呲牙”，**朴实无华的微笑背后，大抵是看惯了庭前花开花落，可以“不以物喜，不以己悲”地笑对人生吧**！其实，在这许许多多地表情里，我最喜欢的是微博里的“Doge”，这个眉清目秀的“狗头”能表达出各种丰富的含义，相比之下，微信里的“Doge”就有一点拙劣的模仿的意味了，俗话说**“狗头保命”**，在一个互联网信仰缺失的时代，用这样一种表情作为人类的保护色，又是不是一种反讽呢？而大家都知道，这个“Doge”表情，实际上是源于一个叫做[Homestar Runner](https://baike.baidu.com/item/Homestar%20Runner)的网上动画系列，其原型则来源于一只名为[Kabosu](https://baijiahao.baidu.com/s?id=1567521374438179&wfr=spider&for=pc)的柴犬，由于它融合了萌宠和故意搞笑两大特点，因此在网络上迅速走红，并由此衍生出一系列二次创作。

![微信年度表情](https://i.loli.net/2020/12/26/i3OZfYwHvugT6JU.png)

![QQ年度表情](https://i.loli.net/2020/12/26/lN9ZgjuXxfs54cF.jpg)

现在，让我们唤醒身体里的中二灵魂，通过OpenCV让这个柴犬界的网红出现在我们面前。这里的思路是，在检测到人脸后，在人脸区域绘制一个“狗头”表情，为此，我们需要定义一个`copyTo()`函数，它可以将一张小图(MaskImage)绘制到大图(SrcImage)的指定位置，我们一起来看它的具体实现：

```Python
def copyTo(srcImage, maskImage, x, y, w, h):
    # 按照区域大小对maskImage进行缩放
    img_h, img_w, _ = maskImage.shape
    img_scale = h / img_h
    new_w = int(img_w * img_scale)
    new_h = int(img_h * img_scale)
    img_resize = cv2.resize(maskImage ,(new_w ,new_h))

    # “粘贴”小图到大图的指定位置
    if (srcImage.shape[2] != maskImage.shape[2]):
        y1, y2 = y, y + img_resize.shape[0]
        x1, x2 = x, x + img_resize.shape[1]
        alpha_s = img_resize[:, :, 3] / 255.0
        alpha_l = 1.0 - alpha_s
        for c in range(0, 3):
            srcImage[y1:y2, x1:x2, c] = (
                alpha_s * img_resize[:, :, c] + alpha_l * srcImage[y1:y2, x1:x2, c]
            )
    else:
        srcImage[y:y + img_resize.shape[0], x:x + img_resize.shape[1]] = img_resize

    return srcImage
```
在这里，我们首先要关注这样一件事情，即OpenCV默认使用的是由R、G、B组成的三通道，可对于像PNG这种格式的图片，它会含有一个Alpha通道。这样，当我们尝试把一张含Alpha通道的小图，“粘贴”到只有R、G、B三个通道的大图上时，就会出现通道数对不上的问题，所以，这个函数实际上对这种情况做了特殊处理。其次，每一个OpenCV中的图片，即Mat，其shape属性是一个由三个元素组成的元组，依次为图片高度、图片宽度和图片通道数。“黏贴”的过程实际上是修改对应位置处的像素信息。好了，现在，我们来修改一下第一版的代码：

```Python
# 步骤1: 定义联级分类器CascadeClassifier并载入指定的模型文件
faceCascade = cv2.CascadeClassifier('./haarcascades/haarcascade_frontalface_alt2.xml')
# cv2.IMREAD_UNCHANGED表示保留Alpha通道信息
doge = cv2.imread('doge-4.png', cv2.IMREAD_UNCHANGED) 

# 步骤2: 对待检测目标进行灰度化和直方图均衡化处理
target = cv2.imread('target.jpg')
target_gray = cv2.cvtColor(target, cv2.COLOR_BGR2GRAY)
target_gray = cv2.equalizeHist(target_gray)

# 步骤3: 人脸检测
faces = faceCascade.detectMultiScale(target_gray)
for (x,y,w,h) in faces:
    target = copyTo(target, doge, x, y, w, h) # 粘贴“狗头”表情至每一个面部区域

# 步骤4: 展示结果
cv2.imshow('Face Detection', target)
cv2.waitKey(0)
cv2.destroyAllWindows() 
```

此时，我们就可以得到下面的结果：

![全员Doge!](https://i.loli.net/2020/12/26/Y9Al67cnvtgWmBz.png)

其实，我本人更喜欢这张，一张充满精神污染意味的图片：

![来自神烦狗的精神污染](https://i.loli.net/2020/12/26/8QaJlR5XIxLftCo.png)

# 视频级PS入门
OK，相信到这里为止，各位读者朋友，都已经顺着博主的思路实现了图片级别的“PS”，既然我们这个系列叫**做视频是不能P的**，那么大家要问了，视频到底能不能P呢？答案显然是可以，不然博主写这个系列就不是“人脸检测”而是“人肉打脸”啦！下面，我们来继续对今天的这个例子做一点升级。考虑在OpenCV中，**VideoCapture**可以通过摄像头捕捉视频画面，所以，我们只需要把这个“狗头”绘制到每一帧画面上，就可以实现视频级别的PS啦！

```Python
# 步骤1: 定义联级分类器CascadeClassifier并载入指定的模型文件
faceCascade = cv2.CascadeClassifier('./haarcascades/haarcascade_frontalface_alt2.xml')
doge = cv2.imread('doge-4.png', cv2.IMREAD_UNCHANGED)
cap = cv2.VideoCapture(0) #笔记本自带摄像头

while (True):
    ret, frame = cap.read() 
    if (ret == False):
        break

    # 步骤2: 对待检测目标进行灰度化和直方图均衡化处理
    # 读取视频中每一帧
    target = frame
    target_gray = cv2.cvtColor(target, cv2.COLOR_BGR2GRAY)
    target_gray = cv2.equalizeHist(target_gray)

    # 步骤3: 人脸检测
    faces = faceCascade.detectMultiScale(target_gray)
    for (x,y,w,h) in faces:
        target = copyTo(target, doge, x, y, w, h)

    # 步骤4: 展示结果
    cv2.imshow('Face Detection', target)
    # 按Q退出
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release() 
cv2.destroyAllWindows() 
```

一起来看看实现的效果吧！可能当你看完这篇博客的时候，你会觉得我写这玩意儿到底有什么用？不好意思，这玩意儿还真有用！它解决了像博主这样腼腆、不敢在公开场合抛头露面的人的困惑。暴走大事件里“王尼玛”一直戴着头罩，所以，很多人都好奇他本人到底长什么样子，如果当时能考虑这个思路的话，是不是可以不用一直戴着头罩。同样地，还有在浪客剑心真人版里饰演志志雄真实的藤原龙也，全身上下缠满绷带的造型其实对演员来说是非常不友好的，如果当时能考虑这个思路的话，是不是演员可以不用受那么大的罪。如果说这些都有些遥远的话，那么，至少在采访后期希望保护受访者隐私的场景下，这个思路是完全可行的，就像大家看到的它可以完全的遮挡住我的脸，而类似的打马赛克等等技术，本质上还是对图像进行处理，甚至美颜相机里的各种特效，底层都离不开OpenCV里的这些算法。怎么样？现在有没有觉得博主其实是一个非常有趣的人，哈哈!

![视频级别的“PS”](https://i.loli.net/2020/12/26/CZi4SYOgzsoy8Qk.gif)

# 本文小结

这篇博客主要分享了OpenCV在人脸检测方面的简单应用，OpenCV中的CascadeClassifier整合**Haar**、**HOG**和**LBP**三类特性算法，通过预置的模型文件可以实现不同程度的目标检测功能，而在人脸检测的基础上，我们可以通过训练来实现简单的人脸识别，正如今年爆发的新冠疫情让人脸识别出现新的挑战一样，虽然人脸识别的场景正在变得越来越复杂，可作为一个世界上最流行的计算机视觉库，OpenCV中的各种模块、算法还是一如既往的经典。结合imread()、resize()、cvtColor()等等的方法，我们可以将“狗头”表情贴到图片或者视频中的人脸区域，而这个思路可以为人脸遮挡相关的场景做一点探索。

在一个流行美颜的时代，人们对于别人甚至自己的期望在无限拔高，像博主本人一直不怎么喜欢拍照，有时候我们埋怨别人没有把我们拍得好看一点，可那究竟是你眼中的自己还是别人眼中的自己呢？正如相亲的时候，人们总喜欢把最好的、美化过的一面展示给别人，因为只有这样才能让别人对你产生兴趣，可往往现实的落差会让这种来得快的兴趣消失得更快。所以，我想说，虽然在技术面前万物似乎皆可“PS”，可对于我们自己而言，你是否了解真正的自己呢？关于我博客的写作风格，我一直不确定是要用偏严谨还是偏活泼的方式来表达，因为眼看着被后浪们一点点超越，这实在是种难以言说的感觉，欢迎大家在评论区留下你对博客内容或者观点的想法，祝大家周末愉快，一个人一样要活得浪漫！