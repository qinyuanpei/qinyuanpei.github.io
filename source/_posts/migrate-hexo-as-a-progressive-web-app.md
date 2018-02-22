---
title: 迁移Hexo博客到Google渐进式Web应用(PWA)
categories:
  - 独立博客
tags:
  - Hexo
  - PWA
  - Web
abbrlink: 450254281
date: 2017-10-24 23:13:41
---
&emsp;&emsp;如果说通过TravisCI实现博客的自动化部署，是持续集成这个概念在工作以外的一种延伸，那么今天这篇文章想要和大家分享的，则是我自身寻求技术转型和突破的一种挣扎。前段时间Paul同我聊到Web技术的发展趋势，Paul认为Web应用会逐渐取代原生应用成为主流，我对此不置可否。真正让我陷入思考的是，在这个充满变化的时代，知识的更新速度远远超过你我的学习速度，我们应该如何去追随这个时代的步伐。如同那些淹没在时间河流里的技术名词，当青春不再的时候，我们喜欢把这个过程称之为成长，当发现距离第一次使用FontPage制作网站已过去十年，当发现曾经的网页三剑客在岁月蹉跎里频频改换姓名，当发现那些淹没在历史里的技术来不及学习就成为过往......或许，这个世界真正迷人的地方，就在于它每天都在不断变化。

# 新一代Web应用——PWA
&emsp;&emsp;接着Paul关于Web技术的这个话题，我认为Web技术在短期内会成为原生应用的一种补充。事实上，原生应用和Web应用哪一个会是未来，这个问题的争论由来已久，在业界我们可以看到HTML5、PhoneGap、React/React Native、Electron/NW.js、小程序等方案百家争鸣，每一种方案都可以让我们去Web技术去打破平台间的差异。与此同时，我们注意到移动开发领域对原生技术的需求在缩减，虽然马克·扎克伯格曾表示，“选择HTML5是Facebook最大的错误“，可我们注意到，越来越多的Web技术被运用在原生应用中，Web技术被认为是最佳的打造跨平台应用的技术，可以通过一套代码实现不同平台间体验的一致性。我们注意到知乎和天猫的客户端中都混合使用了一定的Web技术，因为纯粹使用原生技术去开发一个移动应用，其最大的弊端就在于我们要为Android和iOS维护两套不同的代码，从国内曾经疯狂火热的iOS培训就可以看出，单独使用原生技术去开发客户端，其成本实际上是一直居高不下的。

&emsp;&emsp;虽然我们有Xamarin这样的跨平台技术，试图用一种编程语言和代码共享的方式，去开发两种不同平台的应用程序，可是我们注意到，平台间的差异和抗阻是天然存在的，就像SQL和面向对象这样我们再熟悉不过的例子。同样的，Facebook的React Native项目，试图用Web技术去弱化平台间的差异，React Native存在的主要问题是，它依然依赖原生组件暴露出来的组件和方法，所以像DatePickerIOS、TabBarIOS等控件是iOS Only的，这意味着在开发过程中开发者还是要考虑平台间的差异性，其次React本身的JSX(对应HTML)、CSS Layout(对应CSS)本身是具有一定的学习曲线的，虽然底层因为没有使用WebView的原因提高了部分性能，然而整体上是牺牲了扩展性的。总而言之，这是一个介于Web技术和原生技术之间的中间技术，在我看来地位着实蛮尴尬的，因为无论在Web层还是Native层都选择了部分妥协，完美实现跨平台真心不容易啊。

&emsp;&emsp;要掌握一门新技术，最好的方法就是去应用它。我的博客使用的是Indigo主题，这是一个典型的Material Design风格的主题，所以我一直想尝试将其改造成原生应用，我曾经接触过移动端应用开发，如果通过WebView内嵌网页的方式来实现，我需要处理离线状态下页面的显示问题，以及所有混合应用开发都会遇到的一个问题，即原生应用层需要和Web应用层进行通信的问题。而如果采用Hybrid App的思路去开发一个混合应用，意味着我需要去学习Cordova这样的Hybrid开发框架，去了解JavaScript和Native交互的细节。那么有没有一种学习成本相对较低，同时可以提供原生应用体验的思路呢？答案是确定的，这就是我们下面要说的渐进式应用(PWA)。

&emsp;&emsp;渐进式应用(Progressive Web Apps，PWA)是Google提出的新一代Web应用概念，其目的是提供可靠、快速、接近Native应用的服务方案。我们知道传统Web应用有两个关键问题无法解决，即**需要从网络实时加载内容而带来的网络延迟**和**依赖浏览器入口而带来的用户体验**，从某种意义上而言，渐进式应用的出现有望让这些问题得到解决，首先，渐进式应用可以显著加快应用加载速度，其提供的离线缓存机制可以让应用在离线环境下继续使用，关键技术为Service Worker和Cache Storage；其次，渐进式应用可以被添加到主屏，有独立的图标、启动页、全屏支持，整体上更像Native App，关键技术为Web.App Manifest；最后，渐进式应用同操作系统集成能力得到提高，具备在不唤醒状态下推送消息的能力，关键技术为Push API和Notification API。

# PWA中关键技术解析
&emsp;&emsp;Google对外提出PWA这个概念其实是在今天的二月份左右，所以现在我写这篇文章实际上是在赶一趟末班车。我最近比较喜欢的一个男演员张鲁一，在接受媒体采访时媒体称他是一个大器晚成的人，他的确让我找到了理想中成熟男人的一个标准，如果你要问我这个标准是什么，我推荐你去看他主演的电视剧《红色》。那么，好了，为了让大家了解渐进式Web应用(**PWA**)，相比其它跨平台方案有何优缺点，我们这里来简单讨论下PWA中的关键技术。

## ServiceWorker
&emsp;&emsp;我们知道，传统的Web应用需要在网络环境下使用，当处在离线环境下时，因为HTTP请求无法被发送到服务器上，所以浏览器通常会显示一个空白页，并告知用户页面无法加载，因此会影响用户在离线环境下的使用体验，与此同时，因为Web页面在打开的过程中需要加载大量资源，因此在页面刚刚打开的一段时间内，用户看到的页面通常都是一个空白页面，考虑到缓存或者是预加载的Web应用，通常都会以预设资源作为占位符来填充页面，因此带来访问者的印象往往会更好。那么渐进式Web应用带给我们最大的惊喜，就是它可以在离线环境下使用，其核心技术就是ServiceWorker，我们来一起看看如何使用SeviceWorker：
```
if (navigator.serviceWorker) {
  navigator.serviceWorker.register('service-worker.js')
  .then(function(registration) {
    console.log('service worker 注册成功');
  }).catch(function (err) {
    console.log('servcie worker 注册失败');
  });
}
```
&emsp;&emsp;我们这里看到一个基本的注册ServiceWorker的代码片段，并且它采用了业界流行的Promise的写法。那么首先第一个问题，ServiceWorker到底是什么？ServiceWorker本质上是一个Web应用程序和浏览器间的代理服务器，它可以在离线环境下拦截网络请求，并基于网络是否可用以及资源是否可用，来采取相对应的处理动作，所以ServiceWorker最基本用法是作为离线缓存来使用，而高阶用法则是消息推送和后台同步。通常来讲，ServiceWorker会经历如下的生命周期：

![ServiceWorker生命周期](http://jbcdn2.b0.upaiyun.com/2016/01/55b0169cdfe92b08203757ebc4e5ece2.png)
注：**配图来自  [http://web.jobbole.com/84792/](http://web.jobbole.com/84792/)**

&emsp;&emsp;按照[官方文档](https://developer.mozilla.org/zh-CN/docs/Web/API/Service_Worker_API)中的定义，ServiceWorker同WebWorker一样，是一段JavaScript脚本，作为一个后台独立线程运行，其运行环境与普通的JavaScript不同，因此不直接参与Web交互行为，从某种意义上来说，ServiceWorker的出现，正是为了弥补Web应用天生所不具备的离线使用、消息推送、后台自动更新等特性，我们这里来看一个使用ServiceWorker缓存文件已达到离线使用的目的的例子：
```
var cacheStorageKey = 'minimal-pwa-1'
var cacheList = [
  '/',
  "index.html",
  "main.css",
  "e.png"
]
self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(cacheStorageKey)
    .then(cache => cache.addAll(cacheList))
    .then(() => self.skipWaiting())
  )
})
```

&emsp;&emsp;在这里例子中，我们在ServiceWorker的install事件中添加了待缓存文件列表，这将意味着这些静态资源，会在网页中的ServiceWorker被install的时候添加到缓存中，我们在某个合适的时机到来时就可以再次使用这些缓存资源。事实上考虑到安全性的问题，ServiceWorker在设计时被约束为按照路径给予最高权限，即ServiceWorker在指定路径下是有效的。这里简单提下ServiceWorker的缓存策略，因为这个问题在我看来蛮复杂的，例如官方出品的[sw-tool](https://github.com/GoogleChromeLabs/sw-toolbox)中定义的缓存策略就有如下五种：
* 网络优先:：从网络获取, 失败或者超时再尝试从缓存读取
* 缓存优先:：从缓存获取, 缓存插叙不到再尝试从网络抓取
* 最快：同时查询缓存和网络, 返回最先拿到的
* 仅限网络：仅从网络获取
* 仅限缓存：仅从缓存获取

&emsp;&emsp;我们刚刚提到被缓存的静态资源会在合适的时机被再次使用，那么什么时候可以称之未合适的时机呢？在这个问题中，我们是指fetch事件，事实上通过拦截fetch事件，我们就可以拦截即将被发送到服务器端的HTTP请求，ServiceWorker首先会检查缓存中是否存在待请求资源，如果存在，就直接使用这个资源并返回HTTP响应，否则就发起HTTP请求到服务器端，此时ServiceWorker担任的是一个代理服务器的角色。至此，我们就会明白，ServiceWorker的作用其实就是在离线条件下利用缓存伪造HTTP响应返回，这样我们就达到了离线使用的目的，传统的Web应用在离线环境无法使用，根本原因是没有这样一个Mock的Server去伪造HTTP响应并返回，因为HTTP请求此时根本就无法发送到服务端。为了让ServiceWorker全面接管HTTP请求以便利用请求，我们这里的实现方式如下：
```
self.addEventListener('fetch', function(event) {
  event.respondWith(
    caches.match(event.request)
      .then(function(response) {
        // Cache hit - return response
        if (response) {
          return response;
        }
        return fetch(event.request);
      }
    )
  );
});
```

&emsp;&emsp;好了，以上就是ServiceWorker在离线缓存方面的基本用法，希望进行深入了解的朋友，可以参考文末链接做进一步研究。

## Web App Manifest
&emsp;&emsp;接下来介绍Web App Manifest，它其实是Web开发领域的一个"叛徒"，因为它所做的事情为大家所不齿，基本可以概括为，怎么样假装自己是一个Native App，我们直接看它的定义：
```
{
  "name": "Minimal app to try PWA",
  "short_name": "Minimal PWA",
  "display": "standalone",
  "start_url": "/",
  "theme_color": "#8888ff",
  "background_color": "#aaaaff",
  "icons": [
    {
      "src": "e.png",
      "sizes": "256x256",
      "type": "image/png"
    }
  ]
}
```

&emsp;&emsp;这个我确认没有什么好说的，详细的参数可以参考[这里](http://link.zhihu.com/?target=https%3A//developer.mozilla.org/en-US/docs/Web/Manifest)，通常我们需要将以上文件命名为manifest.json，并通过以下方式引入到HTML结构中，通常是添加在<head>标签下，我们所期望的图标、启动页、主题色等Native App的特性都是在这里定义的，这里想吐槽的是，随着越来越多的平台开始向<head>标签中注入"新血液"，譬如<meta>标签和<link>标签：现在HTML结构变得越来越复杂，更不要说主流的AngularJS和Vue这类MVVM框架，基本上都是通过扩展HTML属性来完成数据绑定的。对PWA应用来讲，我们只需要在<head>标签下引入以下内容：
```
<link rel="manifest" href="manifest.json" />
```
这里简单介绍下Web App Manifest中常见的参数含义及其作用：
* name/short_name：表示应用被添加到屏幕上以后显示的名称，当屏幕空间不足以显示完整的name时，将显示short_name。
* start_url：表示用户从屏幕启动应用时所加载网页的URL，通常我们将其指向网站的首页。
* theme_color：表示应用程序的主题颜色，PWA事实上是建议使用Material Design设计风格的，因此该属性可以控制应用的主题颜色，并在页面加载完成前展示一个过渡动画。
* scope：表示PWA应用的作用域，即哪些页面可以以PWA应用的形式呈现。
* display：表示PWA应用呈现的方式，可以是fullscreen、standalone、minimal-ui和browser中的任意取值。
* orientation：表示PWA应用的屏幕方向，如果你有移动开发的经验，对此应该不会感到陌生。
* icons：表示PWA应用在屏幕上的图标，为了适配不同尺寸的屏幕，这里可以设置不同尺寸下的图标。同样地，如果你有移动开发的经验，对此应该不会感到陌生。


## Push/Notification API
&emsp;&emsp;关于这两个东西，我们简单说一下啊，PWA中的Push机制主要有[Notification](https://www.w3.org/TR/notifications/)和[Push API](https://www.w3.org/TR/push-api/)两部分组成，前者用于向用户展示通知，而后者用于订阅推送消息。网络上对这块介绍的并不多，关于推送这个问题，一直是国内Android用户和开发者的一块心病，因为Google的推送服务在国内水土不服，因此国内厂商或者是SDK提供商基本上都有自己的一套方案，这就导致在用户的设备上同时开启着若干个消息推送服务，用户手机里的电就是这样一点点被耗尽的，所以这个问题大家看看就好。在PWA中，我们可以通过ServiceWorker 的后台计算能力结合 Push API 对推送事件进行响应，并通过 Notification API 实现通知的发出与处理：
```
// sw.js
self.addEventListener('push', event => {
  event.waitUntil(
    // Process the event and display a notification.
    self.registration.showNotification("Hey!")
  );
});

self.addEventListener('notificationclick', event => {  
  // Do something with the event  
  event.notification.close();  
});

self.addEventListener('notificationclose', event => {  
  // Do something with the event  
});
```


# 移植Hexo博客到PWA应用
&emsp;&emsp;现在，我们基本了解了PWA的概念以及实现PWA的关键技术，我们现在考虑将Hexo博客改造成一个PWA应用，我们这里不打算考虑消息推送的相关问题，所以对Hexo这样一个静态博客生成器而言，我们可以做的实际上只有两件事情，即通过Web App Manifest让它更像一个Native应用，通过ServiceWorker为它提供离线缓存的特性。我们从最简单的开始，我们需要在Hexo的根目录中增加一个manifest.json文件，该文件我们可以通过这个网站 [manifoldjs.com](http://www.manifoldjs.com/generator) 来生成。下面给出博主博客中使用的配置：
```
{
  "name":"飞鸿踏雪的部落格",
  "short_name":"Payne's Blog",
  "description":"人生到处知何似，应似飞鸿踏雪泥",
  "icons":[
  {
    "src":"assets/images/icons/bird36.png",
    "sizes":"36x36",
    "type":"image/png"
  },
  {
    "src":"assets/images/icons/bird48.png",
    "sizes":"48x48",
    "type":"image/png"
  },
  {
    "src":"assets/images/icons/bird72.png",
    "sizes":"72x72",
    "type":"image/png"
  },
  {
    "src":"assets/images/icons/bird96.png",
    "sizes":"96x96",
    "type":"image/png"
  },
  {
    "src":"assets/images/icons/bird144.png",
    "sizes":"144x144",
    "type":"image/png"
  },
  {
    "src":"assets/images/icons/bird192.png",
    "sizes":"192x192",
    "type":"image/png"
  }],
  "background_color":"#fff",
  "theme_color":"#000",
  "start_url":"/",
  "display":"standalone",
  "orientation":"portrait"
}
```
&emsp;&emsp;好了，现在我们来考虑如何去实现一个ServiceWorker，Google官方提供了一个ServiceWorker的[示例项目](https://github.com/GoogleChrome/samples/tree/gh-pages/service-worker/basic)，以及网友提供的[Minimal-PWA](https://github.com/minimal-xyz/minimal-pwa)，这两个项目都可以帮助我们去了解，如何去实现一个ServiceWorker，甚至于我们有[sw-toolbox](http://link.zhihu.com/?target=https%3A//github.com/GoogleChrome/sw-precache)和[sw-precache](http://link.zhihu.com/?target=https%3A//github.com/GoogleChrome/sw-precache)这样的工具，配合gulp和webpack我们定制缓存策略并生成ServiceWorker。可是你要知道，懒惰对程序员而言是一种美德，在这里我选择了Hexo的插件[hexo-offline](https://github.com/JLHwung/hexo-offline)，该插件可以帮助我们生成ServiceWoker，关于它的使用及配置，大家可以自行去了解，我重点想说说支持ServiceWorker以后，我的博客所呈现出来的变化以及PWA实际运行的效果。

![ServiceWorker和Cache Storage](http://img.blog.csdn.net/20171119125504778)

&emsp;&emsp;通过这张图，我们可以清楚地看到，ServiceWorker确实在后台工作着，而Cache Storage确实对博客内的静态资源做了缓存处理。事实上对Hexo这样的静态博客而言，整个博客都是静态资源，所以在实际运行中它会对所有内容进行缓存，我们可以在终端中验证这个想法：

![在Hexo中监听到的缓存请求](http://img.blog.csdn.net/20171119130811446)

&emsp;&emsp;可我想说这一切并没有什么用，因为我并不能如愿地在离线状态下访问我的博客，甚至因为有了缓存机制，当我在撰写这篇博客时，虽然我改变了markdown文档的内容，但当我刷新博客的时候，因为缓存机制的存在，我不能像从前那样直接看到博客的变化，更重要的一点是，整个缓存大概有8M左右的体积，因此每次请求页面时，我能够明显地感觉到页面加载的延迟，看起来我们费了大量周折最终却一无所获，这听起来实在是讽刺不是吗？

&emsp;&emsp;说完了ServiceWorker，我们再来说说Web App Manifest，我尝试从豌豆荚下载了移动版Chrome，可我自始至终无法将应用添加到主屏幕，貌似这需要Android系统底层的支持，我测试了两部手机，一部OPPO手机和一部小米手机，发现都没有明显的PWA支持，当我访问页面的时候，浏览器更加不会主动提示我"将应用添加到主屏"，像UC浏览器是将网站以应用的形式添加到浏览器首页，这的确没有什么值得令人惊喜的地方，因为在PC端的时候，我们就可以做到类似地实现，这篇文章耗费时间蛮长的啦，大概是因为我不知道，该如何描述这个失败的尝试。最近接触到一位前辈的项目，这是一个需要跨PC端和移动端的项目。目前面临的一个挑战就是，移动端有太多依赖原生接口的功能设计，所以一套代码在全平台适配，真的仅仅是一个美好的理想，离实现永远有一段不可逾越的距离。


# 本文小结
&emsp;&emsp;本文主要以Google提出的渐进式Web应用(Progressive Web Apps)为主线，简单探讨了Google的渐进式Web应用及其关键技术。渐进式Web应用试图解决传统Web应用的两个关键问题，即**需要从网络实时加载内容而带来的网络延迟**和**依赖浏览器入口而带来的用户体验**。首先，渐进式应用可以显著加快应用加载速度，其提供的离线缓存机制可以让应用在离线环境下继续使用，关键技术为Service Worker和Cache Storage；其次，渐进式应用可以被添加到主屏，有独立的图标、启动页、全屏支持，整体上更像Native App，关键技术为Web.App Manifest；最后，渐进式应用同操作系统集成能力得到提高，具备在不唤醒状态下推送消息的能力，关键技术为Push API和Notification API。在此背景下，我们对静态博客Hexo进行了改造，尝试将其迁移到一个PWA应用上，虽然最终以失败告终，可是在整个过程中我们依然有所收获，我觉得一件事情能让我们有所思考或者有所感悟的话，这就已然是一种幸运、一种成功啦。

&emsp;&emsp;其实Web应用与原生应用并非彼此水火不容，除了纯粹的Web技术和Native技术以外，在这两者之间我们看到的更多是混合技术的应用，所以我认为开发人员在未来一定要具备两种能力，即跨语言和跨平台开发的能力。比如小程序是在微信原生生态下建立的定制化Web应用，它有着类似HTML/CSS/JavaScript的技术方案，同时提供了统一的应用程序外观和使用体验；而跨平台游戏引擎cocos2d-x，通过JavaScript Bridge等类似技术，则可以实现将Web技术转化为Native技术.....总而言之，在技术选型这个问题上，我们可以选择的方案越来越多，如何让想法可以伴随技术产生优秀的产品，这是我们在这个时代真正该去思考的问题。目前来讲，国内普遍重视iOS，可惜遗憾的是iOS不支持PWA；国内的Android系统经过阉割以后，国内用户无法使用Chrome，以及各个厂商定制的浏览器存在兼容性问题；国内因为政策及现实原因，第三方推送相对GCM推送要活跃很多，厂商并不会太关注对PWA应用推送的支持。虽然现实如此，可Web技术发展到今天为止，我们能做的就是希望它越来越好，在此引用[黄玄](https://huangxuan.me)的一句话：

>我们信仰 Web，不仅仅在于软件、软件平台与单纯的技术，还在于『任何人，在任何时间任何地点，都可以在万维网上发布任何信息，并被世界上的任何一个人所访问到。』而这才是 web 的最为革命之处，堪称我们人类，作为一个物种的一次进化。」

---
* [PWA 初探：基本特性与标准现状](http://harttle.com/2017/01/28/pwa-explore.html)
* [Service Worker API](https://developer.mozilla.org/zh-CN/docs/Web/API/Service_Worker_API)
* [Using the Push API](https://developer.mozilla.org/zh-CN/docs/Web/API/Push_API/Using_the_Push_API)
* [Service Worker初体验](http://web.jobbole.com/84792/)
* [PWA 入门: 理解和创建 Service Worker 脚本](https://zhuanlan.zhihu.com/p/25524382)
* [PWA 入门: 写个非常简单的 PWA 页面](https://zhuanlan.zhihu.com/p/25459319)
* [下一代 Web 应用模型 —— Progressive Web App](http://huangxuan.me/2017/02/09/nextgen-web-pwa/)











