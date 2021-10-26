---
abbrlink: 815861661
categories:
- 开发工具
date: 2018-05-20 14:00:03
description: 所以，在这今天这篇文章里，你将看到：**如何使用 Jexus 实现 ASP.NET 在 Linux 平台下的部署**;综合考虑这些因素，我们决定采用[Jexus](https://www.jexus.org/)来将 ASP.NET 项目部署到 Linux 平台;Jexus 是由[宇内流云](http://www.cnblogs.com/yunei)开发的一款 Linux 平台上的高性能 Web 服务器，它是一个可以免费使用、不开源的项目，最大的特色是可以支持 ASP.NET、ASP.NET
  Core、PHP
tags:
- Jexus
- Docker
- Linux
title: 使用 Jexus 实现 ASP.NET 在 Linux 平台下的部署
---

Hello，大家好，我是 Payne，欢迎大家关注我的博客，我的博客地址是：[https://qinyuanpei.github.io](https://qinyuanpei.github.io)。今天想写一点关于 Linux 部署 ASP.NET 相关的话题，为什么突然想写这个话题呢？因为就在几天前，我被我所认识的一位前辈深深地鄙视了一番，原因是我依然在使用一个落后的 IoC 框架——Unity，在如今已然是公元 2018 年的今天。我突然想到，距离.NET Core 2.0 发布已经有一段时间，而.NET Core 3.0 的 roadmap 已经开始提上日程，可我好像还没来得及认真地去对待这个现状。我一直在关注跨平台和跨语言的技术，就像我在大学里的时候就开始接触 Linux 一样，未来我们要面对的是种类繁多的终端平台，从 PC 时代到移动互联网，再到 VR、AR、IoT 和 AI，有太多太多的事情在悄然发生着变化。偶尔我的内心会泛起焦虑和迷茫，可在时光蹉跎直至褪色以前，我或许只是变回了曾经的自己。既然要如同涅槃一般重新开始，为什么不首先重新拾起曾经关注的领域呢？所以，在这今天这篇文章里，你将看到：**如何使用 Jexus 实现 ASP.NET 在 Linux 平台下的部署**。

# 故事背景
我们项目组在开发这样一种服务，它可以通过收集招聘网站的简历来提取相关信息，而这些信息将作为训练集供 AI 算法使用。考虑到 Python 在 AI 领域的优势，我们决定采用 Python 来开发自然语言处理相关的业务，而简历的收集则是通过.NET 中的 Web Service 暴露给前端。整个开发相对顺利，可是在部署环节出现了问题。因为项目组以往的的项目都是部署在 Linux Server 上，所以在部署 Web Service 的问题上产生了分歧，负责运维的同事不愿意为这一个项目而单独配置一台 Windows Server。这里需要说明的是，采用.NET 来开发 Web Service 的一个重要原因是，这些简历中存在大量 Word 文档(.doc/.docx)，因此不得不采用 Office 提供的 COM 组件来支持文档的解析，虽然后来证明的确是这些 COM 组件拖了跨平台的后腿。所以，在这个时候，我们面临着两种选择，第一种方案是采用 Windows Server 来部署，我们的运维同事表示不开心；第二种方案是采用 Linux Server 来部署。我们知道.NET 跨平台的一个关键技术是 Mono，可 Mono 的问题是它的基础类库不大健全，相信微软收购 Mono 以后这个问题能够得到解决。目前官方主推的跨平台技术是.NET Core，考虑到迁移到.NET Core 版本的成本，我们最终没有选择这个方案。事实上，即使采用.NET Core 进行开发，最终我们的部署依然需要依赖[Jexus](https://www.jexus.org/)。综合考虑这些因素，我们决定采用[Jexus](https://www.jexus.org/)来将 ASP.NET 项目部署到 Linux 平台。

# 关于 Jexus
Jexus 是由[宇内流云](http://www.cnblogs.com/yunei)开发的一款 Linux 平台上的高性能 Web 服务器，它是一个可以免费使用、不开源的项目，最大的特色是可以支持 ASP.NET、ASP.NET Core、PHP。通俗地来讲，我们可以认为它是 Linux 平台上的 IIS，这并不为过，因为你可以注意到[Jexus Manager](https://www.jexusmanager.com/en/latest/)这个项目，它可以同时支持 Jexus，IIS 和 IIS Express 三种服务器的管理，并提供了各个平台下一致的使用体验，而 Linux 平台则主要是针对 Jexus。Jexus 提供了不亚于商用服务器的众多特性，比如多站点支持、使用应用程序池来调度管理工作进程、具有良好的稳定性和容错能力、支持 HTTPS 和 WebSockets、支持 FastCGI 协议和 OWIN 标准。除此以外，它同时支持 URL 重写、反向代理、压缩传输、入侵检测等重要功能。Jexus 底层采用 Linux 中的 epoll 机制来处理网站请求，所以会比通常使用 libuv 实现的技术拥有更高的性能。作为一款跨平台软件，Jexus 支持主流的 Linux 发行版本。目前，国内外已经有大量的网站采用 Jexus 作为它的服务器，我们可以在 Jexus 的官网上找到这些[案例](https://www.jexus.org/Examples.htm)。虽然微软官方正在全力推广.NET Core，但对于那些需要维护的旧项目而言，迁移到全新的.NET Core 平台着实是个不小的挑战，而且目前支持.NET Core 版本的类库并不丰富，虽然最终的趋势一定是.NET Core 替代 Mono，但对于 Mono 而言，在.NET 宣布开源以后，从.NET Framework 中吸收的基础类库，极大的改善了 Mono 基础类库不完善的状况，而 Mono 针对 CLR 的实现、C#编译器的实现、AOT 环境等等特性，或许可以为.NET 跨平台提供借鉴，这是一个相互促进的过程。在新时代到来以前，我们暂时需要使用 Jexus 来过渡。

# Hello Linux
OK，下面我们来体验一下 Jexus 在 Linux 平台上的效果，这里我们以 ASP.NET MVC4 为例，我们直接通过 Visual Studio 创建一个项目即可，这里我们需要的是这个项目发布以后的所有文件。总之，这些文件需要通过某种方式放到 Linux 平台上，大家自己去想办法就好啦，这个不再说多余的话。

## 安装 Jexus
Jexus 安装起来是非常简单的，这里博主使用的是 Elementary OS，基于 Ubuntu14.0 的衍生版本。在终端下执行如下命令：
```bash
curl https://jexus.org/release/x64/install.sh|sudo sh
```
你没有看错，真的只需要一行命令。事实上，Jexus 分为两个版本，即通用版和独立版。其差别是通用版不含 Mono 运行时，独立版含有 Mono 运行时。官方建议使用独立版，如果有朋友想尝试安装通用版，请在终端下执行如下命令：
```bash
curl https://jexus.org/release/install|sudo sh
```
无论采用哪一种方式安装，当你看到终端中显示：Jexus 已经被成功安装到系统，就表示 Jexus 安装成功了。

## 配置 Jexus
Jexus 部署到网站，需要两个东西，一个是网站内容(废话)，一个是网站配置。假定我们这里将这两个东西打包在一起，压缩包的名字为 app.tar。为什么这里选择了.tar 格式的压缩文件呢？因为在 Linux 平台下这个格式更好用些，我们熟悉的.zip 格式，可能会需要我们安装相应的扩展。此时，我们可以使用如下脚本来部署网站：
```bash
tar -xf app.tar
sudo mv  -f .aspnetconf usr/jexus/siteconf/aspnetconf
sudo mv ./aspnet /var/www
```
OK，现在来解释下这个脚本，这里我们需要部署一个名为“aspnet”的网站，所以，网站的内容被放置在“aspnet”这个目录里。该网站对应一个作用于 Jexus 的配置文件，配置文件的名字为 aspnetconf。首先，我们将“aspnetconf”这个配置文件移动到了“usr/jexus/siteconf/”目录下，这是 Jexus 指定的配置路径，即**每一个站点都有一个配置文件，且该配置文件被放置在“usr/jexus/siteconf/”目录下**。然后，我们将“aspnet”这个文件夹移动到了“/var/www”目录下，这是 Jexus 指定的网站目录，即**每一个站点都有一个文件夹，文件夹的名字可以理解为网站的名字**。默认情况下，Jexus 会在 www 目录里创建一个名为 default 的文件夹，即默认有一个名为 default 的站点，不过经过博主核实，最新版(v5.8.3)中是没有 default 站点。同理，Jexus 会 siteconf 目录里创建一个名为 default 的配置文件。我们通常以这个配置文件为参照来编写我们自己的配置文件，例如下面是 aspnetconf 中的内容：
```conf
port=4000                  
root=/ /var/www/aspnet          
hosts=  
indexs= 
aspnet_exts=
```
其中，
* port 表示 Jexus Web 服务器监听的端口(必填）
* root 表示网站虚拟目录与其对应的物理目录，中间使用空格分开(必填）
* hosts 表示网站域名(建议填写)，可以使用泛域名如*.yourdomain.com 或者填写*表示默认网站，一个端口有且只有一个默认网站，选填
* indexs 表示网站首页文件名，如 index.html、index.aspx 等，多个文件名使用英文逗号分开，选填
* aspnet_exts 表示 ASP.NET 扩展名，不建议填写。如要填写，多个扩展名(不含.)使用英文逗号分开。

最简单的配置只需要 port 和 root 即可，更多的配置项可以参考官方文档。

## 基本使用
Jexus 的常用命令简单到只有 3 个，start、restart、stop。命令的基本格式为：
```bash
sudo /usr/jexus/jws start [站点名(可选，不指定时表示所有)]
sudo /usr/jexus/jws restart [站点名(可选，不指定时表示所有)]
sudo /usr/jexus/jws stop [站点名(可选，不指定时表示所有)]
```
在这个例子里，我们执行如下命令来启动 aspnet 这个站点：
```bash
sudo /usr/jexus/jws start aspnet
```
当终端中返回 OK 时，就表示启动成功啦，此时，我们打开浏览器，输入`http://localhost:4000` 就可以看到如下画面(这里的端口号为 4000)：
![运行在Linux上的ASP.NET](https://ww1.sinaimg.cn/large/4c36074fly1fz05dq1tcmj20m80aqjsf.jpg)
你就说，这算不算惊喜。我们还可以输入`http://localhost:4000/info`来验证 Jexus 是否配置正确，当 Jexus 被正确配置以后，你就会看到一个显示着“Welcome to Jexus”的页面。嗯嗯，好像是和 Nginx 挺像的哈！

# Docker+
接下来，让我们考虑将这些 Linux 上的工作转移到 Docker 中来做，因为借助 Docker 的容器技术，它可以为我们提供一个足以自给自足的环境。通过这个环境编译测试通过的镜像可以批量地部署到生产环境中。如果你不想在每一台 Linux Server 上都覆盖本文的流程，那么 Docker 将是提高你部署效率的不二选择，而且从认知完整性的角度来看待 Docker，你就会发现它和 Jekins、TravisCI、VSTS 工具一样，都可以非常完美地被接入到持续集成(CI)的流程里去，譬如我们项目组采用的是 Jekins + Gitlib + Docker 的方案，所以，如果你想要选择一个最适合你的持续集成(CI)方案，无论如何，Docker 都是需要去了解的一个知识。关于 Docker 的背景知识大家可以自己去了解，这里我们通过编写 Dockerfile 来完成网站镜像的构建：
```dockerfile
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
如果你熟悉 Linux 下的命令的话，你就会知道 apt-get、curl、wget 这些命令的含义，真正需要的解释的是 ADD，它表示的是，将 Dockerfile 同级目录下的 dest 目录添加到 Docker 环境中，接下来的命令我们同样非常熟悉，因为这和 Linux 下操作是完全一样的。不过，这里的确有些坑需要踩，在博主构建镜像的过程中，发现容器环境和虚拟机环境还是有本质不同的，这里的 mv 命令在 Docker 下有时候会引发“hard link”的问题，从 Stackoverflow 上好像并没有找到太有价值的答案，总之，这个问题非常的玄学。接下来，我们会将 Docker 容器的 4000 端口暴露出来，为什么是 4000 端口呢？因为这个网站的配置中指向了 4000 端口，这一点在上文中我们已经提及。而入口处的命令，显然是启动 Jexus 服务，这个不再解释。

这里，我们通过如下命令来构建一个镜像版本：
```bash
docker build -t jexus-aspnet:v1.0 .
```
假如这个镜像被成功构建出来，我们就可以使用这个镜像来启动网站啦。如下图所示：
![使用Docker创建网站镜像](https://ww1.sinaimg.cn/large/4c36074fly1fz01zbucjvj20m80d5jsm.jpg)
具体地，我们可以使用 docke image 命令来管理所有的 docker 镜像。这里我们启动网站：
```bash
docker run -p 4050:4000 -t jexus-aspnet:v1.0
```
这里，我们将 Docker 容器的 4000 端口映射到主机的 4050 端口，当我们在浏览器中输入：`http://localhost:4050`，就可以得到和 Linux 下一样的结果。不过，在写作这篇博客时，博主使用的是 Windows 下的 Docker，如果大家遇到相关问题，欢迎在博客评论区留言。

# 本文小结
本文从一个实际工作的场景切入，分析和阐述了如何使用 Jexus 实现 ASP.NET 项目在 Linux 下的部署。为了简化这篇文章的写作，我们使用了一个 ASP.NET MVC4 的示例项目，真实的项目通常会有数据库，所以情况会比本文所介绍的流程更为复杂，可这让我们看到了一种可能性不是吗？通过查阅相关资料，博主发现 ASP.NET Core 的部署不需要 Jexus，它只需要一个 dotnet run 命令即可。然后，作为一次体验 Docker 的过程，我们通过编写 Dockerfile 的方式让 Jexus 和 Docker 发生了某种奇妙的关联。作为本文的一个延伸，我们需要考虑网站服务停止后可以自动重启，这就是所谓的守护进程机制啦，感兴趣的朋友可以继续深入研究，Jexus 提供了大量的优秀特性，这篇文章中所看到的不过是冰山一角。最终，我们的项目还是没有使用 Jexus，这其中有对 Jexus 性能的不信任，有因为 COM 组件而做出的妥协，有对 Mono 非官方方案的鄙夷……可以说，技术选型是一个受到多种因素制约的问题，谁拥有了话语权，就可以左右技术选型的走向，这是否又印证了，人类并非如自己所标榜的那般理性和正义？好了，以上就是这篇文章的全部内容啦，今天是 5 月 20 日，如果没有人对你说“我爱你”，请记得对自己说“我爱你”，谢谢大家！