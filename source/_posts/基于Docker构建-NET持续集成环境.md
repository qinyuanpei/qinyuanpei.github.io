---
abbrlink: 3995512051
categories:
- 开发工具
date: 2018-06-12 17:53:59
description: RUN sudo mono ./sonar-scanner/SonarQube.Scanner.MSBuild.exe begin /k:"Sonar-HttpServer"
  /d:sonar.organization="qinyuanpei-github" /d:sonar.host.url="https://sonarcloud.io"
  /d:sonar.login="db795a28468dc7c12805b330afed53d362fdd2d9";对于单元测试，微软提供的MSTest功能相对薄弱，关键是严重依赖Visual
  Studio，一旦我们想要移植到Linux平台下，就会发现阻力重重，所以在平时开发中，我更建议大家去使用NUnit或者XUnit，它们比MSTest功能强大，可以直接通过Nuget安装，同时自带TestRunner，这是一个控制台程序，我们直接通过Mono调用它，并把单元测试项目生成的动态链接库作为参数传递给它即可;RUN
  sudo mono ./sonar-scanner/SonarQube.Scanner.MSBuild.exe end /d:sonar.login="db795a28468dc7c12805b330afed53d362fdd2d9"
tags:
- .NET
- Docker
- MSBuild
title: 基于Docker构建.NET持续集成环境
---

&emsp;&emsp;最近在考虑将整个项目组的产品，努力向着持续集成(CI)/持续部署(CD)的方向靠拢，因为目前我们仅仅实现了基于 Docker 的自动化部署，而部署包的构建依然依赖于人工打包，而每个版本的测试和部署，基本上都要给所有相关人员发一遍邮件，而写邮件无非是填写版本号和变更历史。身处在这样一个社会化分工逐渐加剧的『摩登时代』，我们唯一的希望就追求技能的多元化，你越是担心有一天会被AI所替代，就越是应该去追求灵动与美。这个世界何尝不是一个运行中的大型机器，可恰恰就是这种掺杂了情感的冰冷法则，让我们意识到需要更多的理解和宽容。管理者常常迷信敏捷开发的人月神话，希望人可以像零件一样按部就班，在这场噩梦到来以前，为何不去做一点更有用的事情，让云计算帮我们解放双手。

# 背景说明
&emsp;&emsp;我们的产品，从结构上来讲，分为后端、前端和客户端三个部分，其中，后端提供了从认证到上传、查询和下载等主要的AP接口；前端提供了基于后端API接口的页面，主要功能是监控和管理；客户端承担了主要的业务交互能力，主要功能是整合常用的硬件资源。从技术上来讲，后端是基于 Spring Cloud 的微服务架构，前端是基于node.js的典型前端工具链，而客户端是基于 .NET / Win32 的技术体系。所以，即使我们的客户端是运行在 Window 平台上，我们依然有大量的服务是运行在 Linux 环境下。负责部署的同事不愿意单独再构建一套持续集成(CI)环境，所以我们决定借助 Docker 完成整个持续集成(CI)环境的构建。

# 构建过程
&emsp;&emsp;完成整个项目的构建，需要覆盖到代码编译、单元测试、静态检查、版本发布这四个基本环节，我们整体上使用 Jenkins 作为内部持续集成的平台，这意味着我们只需要在提交代码或者合并代码的时候，触发一个构建指令即可。这里我们考虑通过 Docker 来完成这些工作，一个整体上的设计思路如下图所示：
![构建思路](http://7wy477.com1.z0.glb.clouddn.com/Docker%20Flow.png)

## MSBuild 
&emsp;&emsp;首先是 MSBuild，它是我们整个构建流程中最重要的环节，我们平时通过 Visual. Studio 编译一个项目，背后其实就是由 MSBuild 这个构建工具来驱动，而通过 MSBuild 我们定义更多的构建流程，例如执行单元测试、实现Zip打包等等的流程。在 Window 平台下我们安装 Visual Studio 后就可以使用 MSBuild ，那么在 Linux 平台下呢？目前， MSBuild 已经被微软开源并托管在 Github 上，大家可以通过这个地址：[https://github.com/Microsoft/msbuild](https://github.com/Microsoft/msbuild)来访问。通过阅读 MSBuild的文档，我们了解到，目前 MSBuild 实际上有三个流向，分别是目前官方主推的 [.Net Core](https://github.com/Microsoft/msbuild/wiki/Building-Testing-and-Debugging-on-.Net-Core-MSBuild) 、传统的 [.Net Framework](https://github.com/Microsoft/msbuild/wiki/Building-Testing-and-Debugging-on-Full-Framework-MSBuild)以及由 [Mono](https://github.com/Microsoft/msbuild/wiki/Building-Testing-and-Debugging-on-Mono-MSBuild) 托管的部分。

&emsp;&emsp;.Net Core中MSBuild实际上被集成在 [.Net CLI](https://docs.microsoft.com/zh-cn/dotnet/core/tools/?tabs=netcore2x) 中，熟悉 .NET Core 的朋友一定都知道， .NET Core 类型的项目，是可以直接通过 dotnet 命令来创建项目、还原 Nuget 包、运行项目、构建项目和发布项目的，可以想象的到这些功能是依赖 MSBuild 和 Nuget 的，可惜这种目前对我们来说不太适合。接下来，我们有两个选择，一个是 Full Framework，一个是 Mono，因为我们的服务器是一台 Linux 服务器，所以 Full Framework 对我们来说不适合，我们在无奈的情况下选择了 Mono，按照官方文档，从源代码安装过程如下：
```Shell
git clone -b xplat-master https://github.com/mono/msbuild/
cd msbuild
make
```
&emsp;&emsp;果不其然，这个无论是在 Linux 主机还是D ocker 中都失败了，官方的源代码我们编译不过去，那就只能考虑非源代码安装啦！按照官方的说法，我们需要Mono，所以兴奋地跑到 Mono 官方去安装，根据以前使用 Mono的 经验，飞快地在终端里输入下面两行代码：
```Shell
sudo apt-get install mono-runtime
sudo apt-get install mono-xbuild
```
&emsp;&emsp;装完以后，发现可以使用 Mono 和 XBuild，可无奈是 XBuild 版本实在太低，换句话说我们从 Ubuntu 官方源里安装完的 Mono 相当于 .NET Framework 2.0 的版本，这怎么可以呢？果断从 Mono 官方下载最新版本的 Mono，这是一个经过反复试验的安装方法：
```Shell
sudo apt-get update
sudo apt-get upgrade -y
sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 3FA7E0328081BFF6A14DA29AA6A19B38D3D831EF
sudo apt install apt-transport-https -y
sudo apt-get install wget -y
echo "deb https://download.mono-project.com/repo/ubuntu stable-trusty main" | sudo tee /etc/apt/sources.list.d/mono-official-stable.list
sudo apt-get update
sudo apt-get install aptitude -y
sudo apt-get install -f
sudo apt-get install -y git
sudo aptitude install -y mono-complete
```
&emsp;&emsp;这里顺带安装了 git 和 wget，因为下面我们会用到这两个软件。 aptitude 实在是修复 Linux 依赖问题的神器，我准备找时间用它修复下我的 Linux 环境。 apt-transport-https 这个是为了支持 https 协议，这个不用说太多，我们选择了最全的一个 Mono 版本 mono-complete，它包含了我们在 Linux 下可以使用的所有程序集，换句话说，这些程序集以外的程序集，或者是和 Windows 联系紧密的 COM 组件、 OCX 等等，想都不要想啦，只有一件事情是对的，对平台的依赖越少，跨平台的可能性越高。

## Nuget 
&emsp;&emsp;[Nuget](https://www.nuget.org/)是 .NET 下使用最多的包管理器，虽然目前 .NET Core 里的依赖管理越来越像Maven，可我觉得作为整个构建工具里的一环，还是应该考虑进来，虽然我们的项目中的第三方库基本都靠拷。Nuget 只有单独的命令行版本和 Visual Studo 扩展两个版本，这里我们使用 wget 下载命令行版本，然后再通过 Mono 来调用 nuget.exe :
```
sudo wget https://dist.nuget.org/win-x86-commandline/v4.6.2/nuget.exe /usr/local/bin/nuget.exe
alias nuget="mono /usr/local/bin/nuget.exe"
```
## Sonar 
&emsp;&emsp;对于 Sonar 的话，这里我推荐用 SonarCloud，因为我们只需要通过 wget 下载 SonarScanner，然后通过 Mono 调用并提供 SonarCloud 提供的 token 即可。曾经博主写过一篇关于使用 SonarCloud为.NET/.NET Core项目提供静态检查的文章，在这篇文章中我们提到，SonarCloud 支持 .NET Framework 4.6+ 以上的版本以及 .NET Core 版本，所以，这里我们沿用当时的脚本即可，想了解 SonarCloud 的朋友，可以找到这篇文章进行深入了解。下面给出脚本：
```Shell 
sudo wget https://github.com/SonarSource/sonar-scanner-msbuild/releases/download/4.3.0.1333/sonar-scanner-msbuild-4.3.0.1333-net46.zip sonar-scanner.zip
sudo unzip sonar-scanner.zip
sudo alias sonar-scanner="mono ./sonar-scanner/SonarQube.Scanner.MSBuild.exe"
sonar-scanner begin /k:"Sonar-HttpServer" /d:sonar.organization=<Your-Org> /d:sonar.host.url="https://sonarcloud.io" /d:sonar.login=<Your-Token>
msbuild /t:Rebuild
sonar-scanner end /d:sonar.login=<Your-Token>
```

## NUnit 
&emsp;&emsp;既然我们有了 Nuget，那么自然要用 Nuget 来做点事情。对于单元测试，微软提供的 MSTest 功能相对薄弱，关键是严重依赖 Visual Studio，一旦我们想要移植到 Linux 平台下，就会发现阻力重重，所以在平时开发中，我更建议大家去使用 NUnit 或者 XUnit，它们比 MSTest 功能强大，可以直接通过 Nuget 安装，同时自带 TestRunner，这是一个控制台程序，我们直接通过 Mono 调用它，并把单元测试项目生成的动态链接库作为参数传递给它即可。
下面给出基本的脚本：
```Shell 
nuget install NUnit.Runners -Version 3.8.0 -OutputDirectory ./TestRunner
alias nunit="mono ./TestRunner/NUnit.ConsoleRunner.3.8.0/tools/nunit3-console.exe"
nunit <Your-UnitTest-Project>
```
# 牛刀小试
&emsp;&emsp;下面我们来试试在 Docker 里完成镜像的构建，其实这里更推荐在Linux下安装 Docker，博主在 Window 平台下安装了 Docker for Windows，需要系统支持虚拟化技术。因为博主在构建镜像的时候，一直提示磁盘空间不足，所以，这里我们把 Dockerfile 放到 DaoCloud 上去跑，关于 Docker 的安装以后有机会在同大家分享。这里， DaoCloud 你可以理解为一个帮我们装好了 Docker 的云主机，事实上用 DaoCloud 以后，感觉测试 Dockerfile 可以更省时间啦，效率上相差十倍啊！ Dockerfile 其实就是本文中这些脚本的集合，这里我们给出完整的 Dockerfile，这个文件可以从[这里](https://github.com/qinyuanpei/HttpServer/blob/master/Dockerfile)获取：
```Shell 
FROM ubuntu:14.04
LABEL vendor="qinyuanpei@163.com"

# Install Mono && XBuild
RUN sudo apt-get update
RUN sudo apt-get upgrade -y
RUN sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 3FA7E0328081BFF6A14DA29AA6A19B38D3D831EF
RUN sudo apt install apt-transport-https -y
RUN sudo apt-get install wget -y
RUN echo "deb https://download.mono-project.com/repo/ubuntu stable-trusty main" | sudo tee /etc/apt/sources.list.d/mono-official-stable.list
RUN sudo apt-get update
RUN sudo apt-get install aptitude -y
RUN sudo apt-get install -f
RUN sudo apt-get install -y git
RUN sudo apt-get install -y zip
RUN sudo apt-get install -y unzip
RUN sudo aptitude install -y mono-complete

# Intall Nuget
RUN sudo wget -O nuget.exe https://dist.nuget.org/win-x86-commandline/v4.6.2/nuget.exe 
#RUN alias nuget="mono nuget.exe"

# Install Sonar-Scanner
RUN sudo wget -O sonar-scanner.zip https://github.com/SonarSource/sonar-scanner-msbuild/releases/download/4.3.0.1333/sonar-scanner-msbuild-4.3.0.1333-net46.zip
RUN sudo unzip sonar-scanner.zip -d ./sonar-scanner
#RUN alias sonar-scanner="mono .SonarQube.Scanner.MSBuild.exe"

# Install NUnit
RUN mono nuget.exe install NUnit.Runners -Version 3.8.0 -OutputDirectory ./TestRunner
#RUN alias nunit="mono ./TestRunner/NUnit.ConsoleRunner.3.8.0/tools/nunit3-console.exe"

# Build Project && Sonar Analyse && UnitTest
RUN git clone https://github.com/qinyuanpei/HttpServer.git
RUN sudo mono ./sonar-scanner/SonarQube.Scanner.MSBuild.exe begin /k:"Sonar-HttpServer" /d:sonar.organization="qinyuanpei-github" /d:sonar.host.url="https://sonarcloud.io" /d:sonar.login="db795a28468dc7c12805b330afed53d362fdd2d9"
RUN msbuild /p:Configuration=Release ./HttpServer/HTTPServer/HTTPServer.sln
RUN sudo mono ./sonar-scanner/SonarQube.Scanner.MSBuild.exe end /d:sonar.login="db795a28468dc7c12805b330afed53d362fdd2d9"
# RUN mono ./TestRunner/NUnit.ConsoleRunner.3.8.0/tools/nunit3-console.exe ./HttpServer/HTTPServer/HTTPServerLib.UnitTest/bin/Release/HttpServerLib.UnitTest.dll
EXPOSE 2048
 
```
好了，下面我们通过 Dockerfile 来构建镜像，这里不需要考虑部署，我们就是在 Docker 这个环境里跑跑结果(PS：不知道为什么alias在 Docker 里不起作用)：
```Shell 
docker build -t httpserver:v1 . 
```
可以看到，我们整个过程除了单元测试没有通过以外，其它的环节都非常顺利，这其中一个重要的原因是，博主这个项目对 Window 依赖较少，它是一个 C# 开发的简易 Web 服务器，主要是类库和控制台程序，可以完美地运行在 Linux 平台下，所以，跨平台最终考验的还是开发人员。
![Docker中构建的结果](https://ww1.sinaimg.cn/large/4c36074fly1fz0200fqctj212i0op77q.jpg)

# One More Thing 
&emsp;&emsp;这里我们主要针对的是 .NET Framework，那么针对传统的 ASP.NET 以及最新的 .NET Core 又该如何做持续集成呢？这里简单说一下思路，具体的 Dockerfile 大家可以去 DockerHub 去找(抄)，这里我就不帮大家写了。对于传统的 ASP.NET，在本文的基础上增加 Jexus 就可以做 Linux 下的部署，当然，前提是要避免和 Window 太过紧密的耦合，否则即便是大罗神仙亲临，这持续集成永远都是个梦。对于 .NET Core ，只要安装了它的SDK，编译、依赖管理、发布、部署都不再是问题，只要完善下单元测试和静态检查就可以，因为它是可以自部署的，并且天生就是为了跨平台而生，如果有可能，还是考虑用 .NET Core 吧，Windows 最适合的还是吃鸡打游戏(逃……

# 本文小结
&emsp;&emsp;读过我之前[博客](ttps://blog.yuanpei.me/posts/4891372/)的朋友，一定会发现，我今天这篇博客里所做的事情，同我曾经在 .NET 项目上使用 TravisCI 是完全一样的，所不同的是， TravisCI 里的构建环境是别人提供好的，而这里的构建环境是我们自己搭建的。这并不是在做无用功，如果你需要搭建私有的 Linux 下的构建环境，我相信这篇文章会带给你一点启示。项目组最后还是放弃了这个方案，因为产品里集成了太多和 Window 关联的东西。而负责部署的同事最终如释重托，因为他们不必去踩这些无聊的坑，可对我来说，这像一道屈辱的烙印刻在我的心上，我甚至试过在 Docker 环境里搭建 Window 的环境，哪怕最终我发现我不能把 Docker 当一个虚拟机来用，我越来越害怕自己对那些变化一无所知，还庆幸自己可以在时光的影子里偷懒。

&emsp;&emsp;有时候，人们假装配合持续集成的流程，因为它听上去非常美好，可对环境的依赖不愿意削弱，对单元测试不是那么重视，对代码质量不是那么在意，这一切又永远都只是听上去美好而已。我听到有面试官在面试的时候，批评面试者所做的运维工作不是那么的高大上，毕竟我们只是写了点脚本而已，离面试官心中的 DevOps 相去甚远。可 MSBuild是 XML 写成的脚本， make 不过是个纯文本的脚本，到底哪一种更高大上？我在这篇文章里使用了 Docker，能否让我的工作显得高大上？我们的工作到底有多少能适应 DevOps？我觉得想清楚这个再谈高大上，不是不可以啊？对吧？好了，这就是这篇文章的全部内容啦，谢谢大家！