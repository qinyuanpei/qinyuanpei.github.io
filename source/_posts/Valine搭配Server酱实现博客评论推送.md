---
abbrlink: 369095810
categories:
- 独立博客
date: 2019-11-06 18:15:14
description: 所以，说白了我们就是想利用它这个“云引擎”来调用 Server 酱的接口，幸运的是，LeanCloud 提供的 Hooks 目前是支持 Nodejs 的，所以，到这里思路就非常清晰了，我们给`Comment`这张表加一个`AfterSave`类型的 Hooks，在保存完以后调用 Server 酱接口推送评论信息即可;[Valine](https://valine.js.org/)是一个基于[LeanCloud](https://leancloud.cn)的评论系统，在很长的一段时间里，一直作为多说、[Gitalk](https://gitalk.github.io/)、[Gitment](https://github.com/imsun/gitment)等等的一个替代品，博主所使用的评论系统实际上就是 Valine，虽然独立博客的整体活跃度无法媲美专业博客，可还是想在这纷扰的世界里有自己的一方天地啊;Valine 本身是利用 LeanCloud 的数据存储 SDK 来实现评论的读写的，所以，它相对于“多说”这种第三方的服务，在数据安全性上更有保障一点，虽然“多说”在关闭评论服务以前，提供了导出 JSON 格式评论信息的功能
tags:
- Valine
- Server 酱
- 评论
title: Valine 搭配 Server 酱实现博客评论推送
---

[Valine](https://valine.js.org/)是一个基于[LeanCloud](https://leancloud.cn)的评论系统，在很长的一段时间里，一直作为多说、[Gitalk](https://gitalk.github.io/)、[Gitment](https://github.com/imsun/gitment)等等的一个替代品，博主所使用的评论系统实际上就是 Valine，虽然独立博客的整体活跃度无法媲美专业博客，可还是想在这纷扰的世界里有自己的一方天地啊。多说评论的关闭，某种意义上来说，是很多 90 后站长们关于互联网的集体记忆，因为从博主搭建第一个 WordPress 博客的时候，多说就一直作为首选的评论系统而存在。那个时候通过多说就能接入主流的社交媒体，对于一个还不大会编写 Web 应用的博主来说，此刻想来实在是有种时过境迁的感觉。所以，Valine 作为一个相当优秀的评论系统，凭借着简洁大方的界面和开箱即用的优势，在这个时间点进入人们的视野，我们就不难理解，为什么它会成为博客作者们的“新宠”。

Valine 本身是利用 LeanCloud 的数据存储 SDK 来实现评论的读写的，所以，它相对于“多说”这种第三方的服务，在数据安全性上更有保障一点，虽然“多说”在关闭评论服务以前，提供了导出 JSON 格式评论信息的功能。可话说回来，以国内这种“敏感”的网络环境，其实没有一家云服务提供商敢打这样的包票，像阿里云、LeanCloud、七牛云存储这些服务，都曾经出现过宕机或者封杀域名的事情，所以，趁着数据还在自己手上，尽可能地做好备份工作吧！Valine 本身并没有提供评论推送的功能，我还是挺怀念过去“多说”推送评论到邮箱的功能。虽然[Valine-Admin](https://github.com/DesertsP/Valine-Admin)这个项目提供了类似的功能，但我感觉使用起来并不顺手，尤其是配置邮箱的时候，国内像 QQ、163 这些都非常麻烦，遇到一两个废弃的手机号，你就会发现短信验证码，是件多么尴尬而繁琐的事情，如同扫码使用的共享电话一般魔幻。

为了解决这个问题，我想到了 Valine 搭配 Server 酱实现评论推送的方案。首先，Valine 是基于 LeanCloud 而开发的，用户发表评论实际上就是向`Comment`表插入记录。因此，我们可以利用 LeanCloud 提供的[Hooks](https://leancloud.cn/docs/leanengine_cloudfunction_guide-node.html#hash1095356413)来捕获写入评论的事件。所谓“Hooks”呢，通俗地说就是数据库里触发器的概念，我们可以在数据写入前后做点“小动作”。而[Server 酱](http://sc.ftqq.com/)则是一个消息推送服务，它提供了一个基于 HTTP 的请求接口，通过这个接口，我们就能实现向微信推送消息，前提是关注“方糖”公众号。关于 Server 酱的原理大家可以进一步去看它的[文档](http://sc.ftqq.com/?c=code)，我们这里只需要考虑怎么样把它们结合起来，这就是工程师和科学家的区别所在[doge]。

![运行在Valine云引擎中代码](https://i.loli.net/2019/11/07/DlxWPgGNoKMVeOw.png)

LeanCloud 提供了一个称作“云引擎”的环境，它可以提供运行比如 Nodejs、Python 等等的环境，实际上，[Valine-Admin](https://github.com/DesertsP/Valine-Admin)这个项目就是用 Nodejs 编写的，你可以理解为，只要你的应用符合它的规范，就能在它的环境里运行，这就是所谓的“FAAS”(函数即软件)和“BAAS”(后端即软件)。所以，说白了我们就是想利用它这个“云引擎”来调用 Server 酱的接口，幸运的是，LeanCloud 提供的 Hooks 目前是支持 Nodejs 的，所以，到这里思路就非常清晰了，我们给`Comment`这张表加一个`AfterSave`类型的 Hooks，在保存完以后调用 Server 酱接口推送评论信息即可。创建 Hooks 是在部署->云引擎选项下，我们来看下面的代码：
```JavaScript
AV.Cloud.afterSave('Comment', async function(request) {
  var http = require("request");

  var obj = request.object;
  console.log('收到一条新的评论：' + JSON.stringify(obj));

  var title = "收到一条新的评论";
  var url = request.object.get('url');
  var nick = obj.get('nick');
  if (nick == 'Anonymous'){
      nick = '陌生人';
  }
  var comment = obj.get('comment');

  var content = nick + "给你留言：\n\n" + comment + "\n\n详情请访问：\n\n" + url;
  var options = { method: 'GET',
    url: 'https://sc.ftqq.com/<在这里输入你的token>.send',
    qs: { 
        text: title,
        desp: content
    },
    headers: { } 
  };

  http(options, function (error, response, body) {
    if (error) throw new Error(error);
    console.log(body);
  });
});
```

这里主要利用了 Nodejs 中的`requests`模块来发送 HTTP 请求，其中 token 是 Server 酱经过 Github 授权以后获得的，具体可以参考 Server 酱的[文档](http://sc.ftqq.com/?c=code)。这里有一点要注意，Comment 表里的记录是无法区分发出人的，因为有时候我们可能忘记填写邮箱或者昵称，所以，目前只要写入记录都会发送消息到手机。这个消息模板是 Server 酱作者提供的，我们无法对它的样式进行自定义，收到消息以后需要点击查看详情。不过，我认为这个方案可以满足我的日常使用，因为博客的评论数量并不多，而 Servet 酱的接口调用次数完全足够。免费的 LeanCloud 实例虽然会强制休眠，只要大部分时间能覆盖到就可以啦，谁让这些东西都是免费的呢，博主表示已经相当知足啦，哈哈！好了，看看消息推送到手机的效果吧！

![博客评论推送到手机上的展示效果](https://i.loli.net/2019/11/07/BSsu4cPFe1ZvhGN.png)

如果大家想调整消息的格式，参考文章中给出的代码即可，每次调整完可以直接部署到线上，这是我在这个过程中体验到的 Serverless 的魅力，相比我们中华田园式的 996 敏捷开发，这种方式真的能缩短部署的周期。我还是那句话，敏捷开发是大家一起敏捷，不是只有开发苦哈哈地加班加点干活，快速交付的前提是基础设施完善，具备自动化测试、自动化部署的能力，让开发安心地写代码比什么都重要，就像 LeanCloud 里提供的云函数和 Hooks，开发写完代码就能自动部署，这是真正的敏捷、真正的灵活。好了，这篇博客就先写到这里。想试试博主能不能第一时间收到你们的留言？欢迎在博客评论区留下你的足迹，谢谢大家！