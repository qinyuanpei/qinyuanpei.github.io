---
title: 使用Jexus实现ASP.NET在Linux平台下的部署
categories:
  - 开发工具
tags:
  - Jexus
  - Docker
  - Linux
date: 2018-05-20 14:00:03
abbrlink:
---
&emsp;&emsp;Hello，大家好，我是Payne，欢迎大家关注我的博客，我的博客地址是[https://qinyuanpei.github.io](https://qinyuanpei.github.io)。今天想写一点关于Linux部署ASP.NET相关的话题，为什么突然想写这个话题呢？因为就在几天前，我被我所认识的一位前辈深深地鄙视了一番，原因是我依然在使用一个落后的IoC框架——Unity。在如今已然是公元2018年的今天，我突然想到，距离.NET Core 2.0发布已经有一段时间，而.NET Core 3.0的roadmap已经开始提上日程，可我好像还没来得及认真地去对待这个现状。我一直在关注跨平台和跨语言的技术，就像我在大学里的时候就开始接触Linux一样，未来我们要面对的是种类繁多的终端平台，从PC时代到移动互联网，再到VR、AR、IoT和AI，有太多太多的事情在悄然发生着变化。偶尔我的内心会泛起焦虑和迷茫，可在时光蹉跎直至褪色以前，我或许只是变回了曾经的自己。既然要如同涅槃一般重新开始，为什么不首先重新拾起曾经关注的领域呢？所以，在这今天这篇文章里，你将看到：**如何使用Jexus实现ASP.NET在Linux平台下的部署**。

# 故事背景
&emsp;&emsp;我们项目组在开发这样一种服务，它可以通过收集招聘网站的简历来提取相关信息，而这些信息将作为训练集供AI算法使用。考虑到Python在AI领域的优势，我们决定采用Python来开发自然语言处理相关的业务，而简历的收集则是通过.NET中的Web Service暴露给前端。整个开发相对顺利，可是在部署环节出现了问题。因为项目组以往的的项目都是部署在Linux Server上，所以在部署Web Service的问题上产生了分歧，负责运维的同事不愿意为这一个项目而单独配置一台Windows Server。这里需要说明的是，采用.NET来开发Web Service的一个重要原因是，这些简历中存在大量Word文档(.doc/.docx)，因此不得不采用Office提供的COM组件来支持文档的解析，虽然后来证明的确是这些COM组件拖了跨平台的后腿。所以，在这个时候，我们面临着两种选择，第一种方案是采用Windows Server来部署，我们的运维同事表示不开心；第二种方案是采用Linux Server来部署。我们知道.NET跨平台的一个关键技术是Mono，可Mono的问题是它的基础类库不大健全，相信微软收购Mono以后这个问题能够得到解决。目前官方主推的跨平台技术是.NET Core，考虑到迁移到.NET Core版本的成本，我们最终没有选择这个方案。事实上，即使采用.NET Core进行开发，最终我们的部署依然需要依赖[Jexus](https://www.jexus.org/)。综合考虑这些因素，我们决定采用[Jexus](https://www.jexus.org/)来将ASP.NET项目部署到Linux平台。

# 关于Jexus
&emsp;&emsp;Jexus是由[宇内流云](http://www.cnblogs.com/yunei)开发的一款Linux平台上的高性能Web服务器，它是一个可以免费使用、不开源的项目，最大的特色是可以支持ASP.NET、ASP.NET Core、PHP。通俗地来讲，我们可以认为它是Linux平台上的IIS，这并不为过，因为你可以注意到[Jexus Manager](https://www.jexusmanager.com/en/latest/)这个项目，它可以同时支持Jexus，IIS 和 IIS Express三种服务器的管理，并提供了各个平台下一致的使用体验，而Linux平台则主要是针对Jexus。Jexus提供了不亚于商用服务器的众多特性，比如多站点支持、使用应用程序池来调度管理工作进程、具有良好的稳定性和容错能力、支持 HTTPS 和 WebSockets、支持 FastCGI 协议和 OWIN 标准。除此以外，它同时支持 URL 重写、反向代理、压缩传输、入侵检测等重要功能。Jexus底层采用Linux中的epoll机制来处理网站请求，所以会比通常使用libuv实现的技术拥有更高的性能。作为一款跨平台软件，Jexus支持主流的Linux发行版本。目前，国内外已经有大量的网站采用Jexus作为它的服务器，我们可以在Jexus的官网上找到这些[案例](https://www.jexus.org/Examples.htm)。虽然微软官方正在全力推广.NET Core，但对于那些需要维护的旧项目而言，迁移到全新的.NET Core平台着实是个不小的挑战，而且目前支持.NET Core版本的类库并不丰富，虽然最终的趋势一定是.NET Core替代Mono，但对于Mono而言，在.NET宣布开源以后，从.NET Framework中吸收的基础类库，极大的改善了Mono基础类库不完善的状况，而Mono针对CLR的实现、C#编译器的实现、AOT环境等等特性，或许可以为.NET跨平台提供借鉴，这是一个相互促进的过程。在新时代到来以前，我们暂时需要使用Jexus来过渡。

# Hello Linux
&emsp;&emsp;OK，下面我们来体验一下Jexus在Linux平台上的效果，这里我们以ASP.NET MVC4为例，我们直接通过Visual Studio创建一个项目即可，这里我们需要的是这个项目发布以后的所有文件。总之，这些文件需要通过某种方式放到Linux平台上，大家自己去想办法就好啦，这个不再说多余的话。

## 安装Jexus
&emsp;&emsp;Jexus安装起来是非常简单的，这里博主使用的是Elementary OS，基于Ubuntu14.0的衍生版本。在终端下执行如下命令：
```
curl https://jexus.org/release/x64/install.sh|sudo sh
```
你没有看错，真的只需要一行命令。事实上，Jexus分为两个版本，即通用版和独立版。其差别是通用版不含Mono运行时，独立版含有Mono运行时。官方建议使用独立版，如果有朋友想尝试安装通用版，请在终端下执行如下命令：
```
curl https://jexus.org/release/install|sudo sh
```
无论采用哪一种方式安装，当你看到终端中显示：Jexus已经被成功安装到系统，就表示Jexus安装成功了。

## 配置Jexus
&emsp;&emsp;Jexus部署到网站，需要两个东西，一个是网站内容(废话)，一个是网站配置。假定我们这里将这两个东西打包在一起，压缩包的名字为app.tar。为什么这里选择了.tar格式的压缩文件呢？因为在Linux平台下这个格式更好用些，我们熟悉的.zip格式，可能会需要我们安装相应的扩展。此时，我们可以使用如下脚本来部署网站：
```
tar -xf website.tar
sudo mv  -f .aspnetconf usr/jexus/siteconf/aspnetconf
sudo mv ./aspnet /var/www
```
OK，现在来解释下这个脚本，这里我们需要部署一个名为“aspnet”的网站，所以，网站的内容被放置在“aspnet”这个目录里。该网站对应一个作用于Jexus的配置文件，配置文件的名字为aspnetconf。首先，我们将“aspnetconf”这个配置文件移动到了“usr/jexus/siteconf/”目录下，这是Jexus指定的配置路径，即**每一个站点都有一个配置文件，且该配置文件被放置在“usr/jexus/siteconf/”目录下**。然后，我们将“aspnet”这个文件夹移动到了“/var/www”目录下，这是Jexus指定的网站目录，即**每一个站点都有一个文件夹，文件夹的名字可以理解为网站的名字**。默认情况下，Jexus会在www目录里创建一个名为default的文件夹，即默认有一个名为default的站点，不过经过博主核实，最新版(v5.8.3)中是没有default站点。同理，Jexus会siteconf目录里创建一个名为default的配置文件。我们通常以这个配置文件为参照来编写我们自己的配置文件，例如下面是aspnetconf中的内容：
```
port=4000                  
root=/ /var/www/aspnet          
hosts=  
indexs= 
aspnet_exts=
```
其中，
* port表示Jexus Web服务器监听的端口(必填）
* root表示网站虚拟目录与其对应的物理目录，中间使用空格分开(必填）
* hosts表示网站域名(建议填写)，可以使用泛域名如*.yourdomain.com或者填写*表示默认网站，一个端口有且只有一个默认网站，选填
* indexs表示网站首页文件名，如index.html、index.aspx等，多个文件名使用英文逗号分开，选填
* aspnet_exts表示ASP.NET扩展名，不建议填写。如要填写，多个扩展名(不含.)使用英文都好分开。

最简单的配置只需要port和root即可，更多的配置项可以参考官方文档。

## 基本使用
&emsp;&emsp;Jexus的常用命令简单到只有3个，start、restart、stop。命令的基本格式为：
```
sudo /usr/jexus/jws start [站点名(可选，不指定时表示所有)]
sudo /usr/jexus/jws restart [站点名(可选，不指定时表示所有)]
sudo /usr/jexus/jws stop [站点名(可选，不指定时表示所有)]
```
在这个例子里，我们执行如下命令来启动aspnet这个站点：
```
sudo /usr/jexus/jws start aspnet
```
当终端中返回OK时，就表示启动成功啦，此时，我们打开浏览器，输入“http://localhost:4000”就可以看到如下画面(这里的端口号为4000)：
![运行在Linux上的ASP.NET](http://7wy477.com1.z0.glb.clouddn.com/Blog_Jexus_01.jpg)
你就说，这算不算惊喜。我们还可以输入“http://localhost:4000/info”来验证Jexus是否配置正确，当Jexus被正确配置以后，你就会看到一个显示着“Welcome to Jexus”的页面。嗯嗯，好像是和Nginx挺像的哈！

# Docker+
&emsp;&emsp;接下来，让我们考虑将这些Linux上的工作转移到Docker中来做，因为借助Docker的容器技术，它可以为我们提供一个足以自给自足的环境。通过这个环境编译测试通过的镜像可以批量地部署到生产环境中。如果你不想在每一台Linux Server上都覆盖本文的流程，那么Docker将是提高你部署效率的不二选择，而且从认知完整性的角度来看待Docker，你就会发现它和Jekins、TravisCI、VSTS工具一样，都可以非常完美地被接入到持续集成(CI)的流程里去，譬如我们项目组采用的是Jekins + Gitlib + Docker的方案，所以，如果你想要选择一个最适合你的持续集成(CI)方案，无论如何，Docker都是需要去了解的一个知识。关于Docker的背景知识大家可以自己去了解，这里我们通过编写Dockerfile来完成网站镜像的构建：
```
FROM ubuntu:14.04
LABEL vendor="qinyuanpei@163.com"

# Prepare Environment
RUN sudo apt-get update 
RUN sudo apt-get install -y
RUN sudo apt-get install -y curl
RUN sudo apt-get install -y wget
RUN sudo curl -sSL https://jexus.org/release/x64/install.sh|sudo sh

# Deploy Website
ADD dest/ /
RUN sudo mv -f aspnetconf /usr/jexus/siteconf/aspnetconf
RUN sudo mkdir -p /var/www
RUN sudo mv ./aspnet /var/www

# Start Jexus
EXPOSE 4000
WORKDIR /usr/jexus
CMD sudo ./jws start aspnet
```
如果你熟悉Linux下的命令的话，你就会知道apt-get、curl、wget这些命令的含义，真正需要的解释的是ADD，它表示的是，将Dockerfile同级目录下的dest目录添加到Docker环境中，接下来的命令我们同样非常熟悉，因为这和Linux下操作是完全一样的。不过，这里的确有些坑需要踩，在博主构建镜像的过程中，发现容器环境和虚拟机环境还是有本质不同的，这里的mv命令在Docker下有时候会引发“hard link”的问题，从Stackoverflow上好像并没有找到太有价值的答案，总之，这个问题非常的玄学。接下来，我们会将Docker容器的4000端口暴露出来，为什么是4000端口呢？因为这个网站的配置中指向了4000端口，这一点在上文中我们已经提及。而入口处的命令，显然是启动Jexus服务，这个不再解释。

这里，我们通过如下命令来构建一个镜像版本：
```
docker build -t jexus-aspnet:v1.0 .
```
假如这个镜像被成功构建出来，我们就可以使用这个镜像来启动网站啦。如下图所示：
![使用Docker创建网站镜像](http://7wy477.com1.z0.glb.clouddn.com/Blog_Jexus_02.jpg)
具体地，我们可以使用docke image命令来管理所有的docker镜像。这里我们启动网站：
```
docker run -p 4050:4000 -t jexus-aspnet:v1.0
```
这里，我们将Docker容器的4000端口映射到主机的4050端口，当我们在浏览器中输入“http://localhost:4050”，就可以得到和Linux下一样的结果。不过，在写作这篇博客时，博主使用的是Windows下的Docker，如果大家遇到相关问题，欢迎在博客评论区留言。

# 本文小结
&emsp;&emsp;本文从一个实际工作的场景切入，分析和阐述了如何使用Jexus实现ASP.NET项目在Linux下的部署。为了简化这篇文章的写作，我们使用了一个ASP.NET MVC4的示例项目，真实的项目通常会有数据库，所以情况会比本文所介绍的流程更为复杂，可这让我们看到了一种可能性不是吗？通过查阅相关资料，博主发现ASP.NET Core的部署不需要Jexus，它只需要一个dotnet run命令即可。然后，作为一次体验Docker的过程，我们通过编写Dockerfile的方式让Jexus和Docker发生了某种奇妙的关联。作为本文的一个延伸，我们需要考虑网站服务停止后可以自动重启，这就是所谓的守护进程机制啦，感兴趣的朋友可以继续深入研究，Jexus提供了大量的优秀特性，这篇文章中所看到的不过是冰山一角。最终，我们的项目还是没有使用Jexus，这其中有对Jexus性能的不信任，有因为COM组件而做出的妥协，有对Mono非官方方案的鄙夷......可以说，技术选型是一个受到多种因素制约的问题，谁拥有了话语权，就可以左右技术选型的走向，这是否又印证了，人类并非如自己所标榜的那般理性和正义？好了，以上就是这篇文章的全部内容啦，今天是5月20日，如果没有人对你说“我爱你”，请记得对自己说“我爱你”，谢谢大家！
