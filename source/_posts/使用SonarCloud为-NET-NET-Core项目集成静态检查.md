---
abbrlink: 4891372
categories:
- 开发工具
date: 2018-05-12 01:16:52
description: 经过反复尝试，最终我们实现了：**在 TravisCI 下使用 MSBuild 构建项目**、**使用 Nuget 在线安装 NUnit 并运行单元测试**、**使用 SonarCloud 对代码进行静态检查**;通常使用 Sonar 来构建静态检查工具时，需要我们在本地搭建一套运行环境，而 SonarCloud 是针对 Sonar 推出的一个“云”版本;在编写 TravisCI 脚本的过程中，我们一同验证了 MSBuild、Nuget、NUnit 等.NET 常规工具或者类库在 Linux 平台下使用的可能性，最终在 TravisCI 的帮助下完成了从项目构建、单元测试再到代码的分析的整个流程
tags:
- Mono
- Sonar
- Travis
title: 使用 SonarCloud 为.NET/.NET Core 项目集成静态检查
---

&emsp;&emsp;Hi，朋友们，大家好，欢迎大家关注我的博客，我是 Payne，我的博客地址是[http://qinyuanpei.github.io](http://qinyuanpei.github.io)。在不知不觉间，5 月份已然度过大半，最近无论是读书还是写作均停滞不前，被拖延症支配的我深感有虚度时光之嫌。今天这篇文章，我将为大家介绍如何使用[SonarCloud](https://about.sonarcloud.io/)，来为.NET/.NET Core 项目集成静态检查。如果大家使用过[SonarCube](https://www.sonarqube.org/)的话，对接下来我要讲的内容一定不会感到陌生，因为[SonarCloud](https://about.sonarcloud.io/)实际上就是[SonarCube](https://www.sonarqube.org/)的“云”版本。在云计算概念深入人心的今天，我们可以通过互联网来访问各种各样的服务。譬如，我曾经为大家介绍过的 TravisCI 就是一个在线的持续集成(CI)服务。这些云服务可以让我们不再关心基础设施如何去搭建，进而集中精力去解决最核心、最关键的问题。和持续集成关注“持续”不同，静态检查关注的是代码质量。目前，SonarCloud 支持**.NET Framework 4.6**以上及**.NET Core**版本。通过这篇文章，你将了解到**SonarCloud 的基本使用**、**SonarCloud 与 TravisCI 的服务集成**这两方面的内容。

# SonarCloud
&emsp;&emsp;静态检查，顾名思义就是通过扫描源代码来发现代码中隐藏的缺陷，譬如潜在的 Bug、重复/复杂的代码等等，这些通常被称为代码中的“坏味道”，静态检查就是通过工具去扫描这些“坏味道”。Sonar 是一个基于 Java 的代码质量管理工具，由 Sonar 和 SonarScanner 两个主要部分组成，前者是一个 Web 系统用以展示代码扫描结果，而后者是真正用以扫描代码的工具。Sonar 具备良好的扩展性，众多的插件使得它可以和 Jenkins 等集成工具结合使用，同时可支持不同语言项目的扫描分析。在.NET 中我们可以使用[Stylecop](https://github.com/StyleCop)来进行静态检查，无独有偶，[ReShaper](http://www.jetbrains.com/resharper/)中同样提供了静态检查的特性。在这篇文章中我们主要使用 Sonar 来作为.NET 项目的静态检查工具。

&emsp;&emsp;通常使用 Sonar 来构建静态检查工具时，需要我们在本地搭建一套运行环境，而 SonarCloud 是针对 Sonar 推出的一个“云”版本。我们只需要执行脚本就可以完成代码分析，而分析的结果则可以直接在 SonarCloud 网站中看到。这就是“云计算”的魅力所在，我们无需关心 Sonar 是如何安装以及配置的，当我们需要使用这种服务的时候直接使用就好了。目前，SonarCloud 对开源项目是免费提供的。因此，如果你不想亲自去搭建一个静态分析的环境，那么你可以选择使用 SonarCloud 来对代码进行静态分析。SonarCloud 支持 17 种语言的扫描分析，支持和 Travis、VSTS、AppVeyor 等 CI 工具集成，甚至你可以在 SonarCloud 上找到大量实际的项目。

&emsp;&emsp;我对 SonarCloud 感兴趣的一个重要原因是，它可以和 TravisCI 完美地集成在一起，而且在此之前，我曾经使用过一段时间的 Sonar。在使用 SonarCloud 前，我们需要注册一个账号，这里建议使用 Github 账号授权登录，因为我们需要授权给 SonarCloud 来拉取代码，尤其当你使用 TravisCI 来集成 SonarCloud 的时候。除此之外，我们需要准备好以下工具：
* [JDK](http://www.oracle.com/technetwork/java/javase/downloads/index.html)，即 Java SE Development Kit，运行 SonarScanner 时依赖 Java 环境。
* [Git](https://git-scm.com/)，版本控制工具，如果身为一名程序员而没有安装 Git，请面壁思过并自我检讨。
* [MSBuild](https://msdn.microsoft.com/en-us/library/dd393574.aspx)，.NET 平台项目构建工具，推荐一个无脑安装的方法，安装全宇宙无敌的 IDE：Visual Studio。
* [SonarScanner](https://docs.sonarqube.org/display/SCAN/Analyzing+with+SonarQube+Scanner+for+MSBuild)，即 Sonar 的代码扫描器，注意这里有两个版本：[.NET Framework 4.6 +](https://github.com/SonarSource/sonar-scanner-msbuild/releases/download/4.2.0.1214/sonar-scanner-msbuild-4.2.0.1214-net46.zip) 和 [.NET Core](https://github.com/SonarSource/sonar-scanner-msbuild/releases/download/4.2.0.1214/sonar-scanner-msbuild-4.2.0.1214-netcoreapp2.0.zip)，本文以.NET Framework 4.6 +为例。

# 第一个.NET 项目
&emsp;&emsp;好了，下面我们来使用 SonarCloud 对博主的一个项目[HttpServer](https://github.com/qinyuanpei/HttpServer)进行分析。首先，我们需要在 SonarCloud 中创建一个项目。如下图所示，我们首先选择 Organization，默认情况下，通过 Github 授权登录以后，会生成一个格式为：${UserName}-github 的组织名称，例如我这里是：qinyuanpei-github。这里我们选择默认组织，然后点击：Continue。
![设置组织名称](https://ww1.sinaimg.cn/large/4c36074fly1fziy4wzsedj21h40jcjsm.jpg)
&emsp;&emsp;接下来，我们需要设置一个 Token，其目的是通过这个 Token 登录 SonarCloud，然后把 SonarScanner 在本地扫描的结果发送到 SonarCloud。这里我们可以选择生成一个新的 Token 或者是使用一个已经存在的 Token。建议使用一个 Token 来管理所有的项目，因为这个 Token 显示一次后就不再显示，同时维护多个 Token 实在是太痛苦啦，当然，如果你能管理好所有 Token 的 Key 的话。设置完 Token 点击下一步：
![设置Token](https://ww1.sinaimg.cn/large/4c36074fly1fzixye65qqj21gn0j7dh1.jpg)
&emsp;&emsp;设置完 Token 以后需要选择项目类型以及设置项目名称，在这个例子中，博主的项目名称是 HttpServer，建议使用 Sonar-${Project Name}的形式来为项目命名，而项目类型显然应该选择“C# or VB.NET”。
![设置项目名称](https://ww1.sinaimg.cn/large/4c36074fly1fz05nliq9vj21ef0bhaaj.jpg)
&emsp;&emsp;接下来我们就得到最关键的信息，如图所示，这里有三条命令，我们将其复制下来，然后将其写到批处理(.bat)或者 PowerShll 脚本里。以后运行这三条命令，就可以对当前项目进行静态检查，是不是很简单啊？简单分析下，这三条命令，第一条命令根据我们设置的 Token、项目名称、组织等信息“开始”对项目进行分析，注意到这里有一个“begin”；第二条命令是一个 MSBuild 命令，其目的是对整个项目重新构建；第三条命令是将静态分析的提交到 SonarCloud，注意到这里有一个“end”。具体文档可以参考 [这里](https://docs.sonarqube.org/display/SCAN/Analyzing+with+SonarQube+Scanner+for+MSBuild)  哦！
![复制3条命令](https://ww1.sinaimg.cn/large/4c36074fly1fz05k8xmafj20r60h1t9n.jpg)
&emsp;&emsp;好了，现在我们在 SonarCloud 中就可以看到扫描结果啦，开心！如果执行命令出现问题，请确保正确安装了相关工具，并检查这些工具是否被添加到系统变量中，特别是 Java 需要设置 JAVA_HOME。
![扫描结果](https://ww1.sinaimg.cn/large/4c36074fly1fz05e26i0aj21h40pmdj2.jpg)
# TravisCI 与 SonarCloud 的集成
&emsp;&emsp;现在我们来回顾下整个过程，我们需要在本地安装 SonarScanner，这是一个 Java 编写的应用程序，因此我们需要一个 Java 运行环境。每次都需要通过 SonarCloud 来创建项目，获得项目相关的信息以后，在命令中携带这些参数并执行命令，就可以在 SonarCloud 中获得本地的扫描结果。在整个过程中，我们依然需要一个本地的环境，这一点都不灵活。现实世界的复杂性，就在于我们无法为还原出完全一致的处境。
&emsp;&emsp;所以，托尔斯泰开宗明义地说道：“幸福的家庭都是相似的，不幸的家庭各有各的不幸”，况且作为一个执着于让重复的事情自动化的人，如果让我做这件事情，我保证第一次会意外地觉得好奇，而等到第二次、第三次的时候我就会感到厌烦，这就是人们所说的三分钟热度。诚然，我的确是一个花心的双子座。我们提到，SonarCloud 支持 TravisCI，所以，接下来我们来考虑如何让 TravisCI 帮助我们运行 Sonar。
&emsp;&emsp;常规的思路是，下载 SonarScanner 并执行脚本。这种思路的问题在于 TravisCI 运行在 Linux 下，我们确定 SonnarScanner 是否可以支持 Linux 平台，尽管 SonarScanner 使用 Java 开发。通过阅读 TravisCI 的[文档](https://docs.travis-ci.com/user/sonarcloud/)，我们发现 TravisCI 本身是支持 SonarCloud 的插件的，由此我们就可以着手将这一切交给 TravisCI 来做啦！
&emsp;&emsp;关于如何使用 TravisCI，这里不再赘述啦！大家可以参考我的这两篇博客，这两篇博客分别是：[持续集成在 Hexo 自动化部署上的实践](https://qinyuanpei.github.io/posts/3521618732/)、[基于 Travis CI 实现 Hexo 在 Github 和 Coding 的同步部署](https://qinyuanpei.github.io/posts/1113828794/)。当然第一手的资料必然是官方文档，我是不好意思随便对别人说 RTFM 的。按照文档说明，我们首先需要一个名为 sonar-project.properties 的配置文件，在该配置文件中配置了诸如项目名称、组织名称等关键信息，Sonar 会自动读取这个配置文件里的信息并携带到命令中去，这个配置文件是在是太熟悉啦，假如你认真地读了这篇文章，并注意到了 SonarCloud 生成的三条命令。这个配置文件内容如下：
```plain
# must be unique in a given SonarQube instance
sonar.projectKey=Sonar-HttpServer
# this is the name and version displayed in the SonarQube UI. Was mandatory prior to SonarQube 6.1.
sonar.projectName=HttpServer
sonar.projectVersion=1.0
# Path is relative to the sonar-project.properties file. Replace "\" by "/" on Windows.
# This property is optional if sonar.modules is set.
sonar.sources=.
# Encoding of the source code. Default is default system encoding
#sonar.sourceEncoding=UTF-8
```
&emsp;&emsp;配置文件中有来自官方的注释，我就不再狗尾续貂的去做相应的解释了。我们发现，这个里面是没有 token 的，按照官方[文档](https://docs.travis-ci.com/user/sonarcloud/)中的说明，token 应该配置在.travis.yml 这个文件中，熟悉 TravisCI 的朋友就会知道，这个文件通常用来配置持续集成的流程。按照约定，SonarCloud 属于 TravisCI 的一个插件，应该配置在 addons 节点下，我们注意到，在这里可以配置组织名称和 token 两个节点的信息。组织信息这个简单，直接按照前面的流程填写即可，需要注意的是这里的 token。
&emsp;&emsp;因为 token 采用明文配置的话，难免会存在安全风险，所以官方的建议是：使用 TravisCI 的终端工具进行加密。这是一个基于 Ruby 的命令行工具，直接在命令行中对 token 进行加密即可。不过想起很多年前，第一次接触 Jekyll 时被 Ruby 支配的恐惧感，我决定寻找新的出路。官方文档说可以在 TravisCI 中配置[全局变量](https://docs.travis-ci.com/user/environment-variables/#Defining-Variables-in-Repository-Settings)，这种方式我们接入 Coding Page 时曾使用过，不过经过博主尝试，这种方式一直无法获得权限，所以，我不得不在配置文件中写明文，大家不要学我啊：
```plain
addons:
  sonarcloud:
    organization: "在这里输入你的组织名称" 
    token: "在这里输入你的token"
```
&emsp;&emsp;原本走到这一步时，我就该和大家对本文进行小结啦！可偏偏我注意到了 SonarCloud 生成命令中有 MSBuild 的身影，于是我开始尝试在 TravisCI 脚本中编写.NET 相关的命令，因为我从未在 TravisCI 中对.NET 项目进行持续集成，所以我很好奇它如果跑起来会是什么样子的。同样参照官方[文档](https://docs.travis-ci.com/user/languages/csharp/)，发现目前 TravisCI 支持 Mono 和.NET Core 的两个版本的构建工具，Mono 我可以理解，因为 TravisCI 运行在 Linux 环境下，这和我们以前运行在 Windows 环境下是不一样的。而.NET Core 原本就支持跨平台，目前官方释放出了 2.0 预览版，同时 3.0 的计划开始提上日程。无论或早或晚，我们面对的都将是一个多平台化的未来，永远不要固执地封闭在一个生态系统里，技术是如此，人生何尝不是如此呢？
&emsp;&emsp;好啦，言归正传，了解到这种可能性以后，我开始尝试编写 TravisCI 脚本，官方默认的构建系统是 XBuild，实际使用中遇到些问题，开始考虑能不能替换成 MSBuild，事实上 MSBuild 目前已经是跨平台的，Nuget 同样跨平台。微软收购 Mono 以后，Visual Studio 基本上算是跨平台了，况且我们还有一个编辑器中的黑马 Visual Studio Code。IIS 目前可以考虑用 Jexus 替换，而有了 OWIN 这个服务器接口以后，我们有更多的 Host 可以去选择，现在剩下的只有 SQL Server 啦，可想而知，除了 WinForm/WPF/COM 等这种系统依赖性强的东西，大多数的服务其实都可以跑在 Linux 上。经过反复尝试，最终我们实现了：**在 TravisCI 下使用 MSBuild 构建项目**、**使用 Nuget 在线安装 NUnit 并运行单元测试**、**使用 SonarCloud 对代码进行静态检查**。一起来看脚本怎么写：
```plain
jdk:
  - oraclejdk8
mono: 
  - latest

language: csharp
solution: ./HTTPServer/HTTPServer.sln

notifications:
  email:
    recipients:
      - 875974254@qq.com #请替换成你的邮箱，谢谢
      - qinyuanpei@163.com #请替换成你的邮箱，谢谢
    on_success: change # default: change
    on_failure: always # default: always

install:
  - cd ./HTTPServer
  - nuget restore ./HTTPServer.sln # restore nuget
  - nuget install NUnit.Runners -Version 3.8.0 -OutputDirectory ./TestRunner # install nunit

script:
  - msbuild /p:Configuration=Release HTTPServer.sln
  - mono ./TestRunner/NUnit.ConsoleRunner.3.8.0/tools/nunit3-console.exe ./HTTPServerLib.UnitTest/bin/Release/HttpServerLib.UnitTest.dll
  - sonar-scanner -Dsonar.verbose=true -X

branches:
  only:
    - master

addons:
  sonarcloud:
    organization: "在这里输入你的组织名称" 
    token: "在这里输入你的token"

    
cache:
  directories:
    - '$HOME/.sonar/cache'
```
&emsp;&emsp;好啦，感受技术的魅力吧！可以注意到，我这里有 4 个单元测试，其中 2 个通过、2 个失败。虽然单元测试没有通过，可我代码没有 Bug 呀！
![NUnit运行结果](https://ww1.sinaimg.cn/large/4c36074fly1fz01zprsfuj20jr0a73z5.jpg)

# 本文小结
&emsp;&emsp;本文介绍了一个“云”服务：SonarCloud。SonarCloud 是一个基于 SonarCube 的静态分析工具，通过 SonarCloud 我们无需搭建 Sonar 环境就可以对项目进行静态分析。为了验证和实现这个诉求，我们首先提供了通过 SonarScanner 来扫描代码的示例，其原理是在命令行参数中携带相关信息，通过 token 来验证和登录 SonarCloud，在完成对代码的扫描以后，就可以在 SonarCloud 中查看整个项目的分析结果。
&emsp;&emsp;接下来，为了验证 SonarCloud 和 TravisCI 进行集成的可行性，我们尝试通过 travisCI 脚本的方式来调用 SonarCloud，其原理是通过配置文件获得相关信息由 TravisCI 完成所有的分析工作，这里需要注意的是要对 token 进行加密。在编写 TravisCI 脚本的过程中，我们一同验证了 MSBuild、Nuget、NUnit 等.NET 常规工具或者类库在 Linux 平台下使用的可能性，最终在 TravisCI 的帮助下完成了从项目构建、单元测试再到代码的分析的整个流程。
&emsp;&emsp;虽然静态分析并不能完全保证代码没有问题，可人类总是不情愿承认自己仅仅是一种高等动物而已，这个世界上有好多东西人们不一定会喜欢，因为它们要么是正确的要么是有益的。本文这个方案需要把代码暴露在 Github，对于一般的服务集成，我们更推荐 Jenkins + Sonar 这样的组合，前者可以替换 TravisCI 提供持续集成服务，同 Github、Gitlib 等代码托管服务进行集成、同 Stylecop、Sonar 等静态检查工具进行集成，这方面的资料非常丰富，我们这里就不再多说啦，总而言之，让一切更好就是我们的目的，晚安！