---
abbrlink: 4159187524
categories:
- 编程语言
date: 2019-04-22 22:13:36
description: 好了，以上就是在使用WSL中的Docker搭建ELK全家桶过程中遇到的问题的梳理，从体验上来讲，我个人会把Linux平台相关的工作渐渐转移到WSL上，因为安装双系统总会分散你的精力去处理维护相关的事情，虽然装系统对程序员来说都不算是个事儿，可我内心依旧排斥自己被贴上“修电脑”的标签
tags:
- WSL
- Docker
- Linux
title: WSL下Docker使用踩坑小记
---

众所周知，Win10中开始提供Linux子系统，即Windows Subsystem for Linux，简称WSL，它可以让我们在Windows系统使用Linux系统，自从有了这个新功能以后，博主果断地放弃双系统的方案，因为折腾起来实在花费时间。关于如何使用WSL，网上有非常多的文章可以参考，这里不再赘述。今天想说的是，WSL下使用Docker遇到的各种坑。

装完WSL以后，对各种编译环境的使用相当满意，最近在研究日志可视化平台ELK，其中需要使用Docker来搭建环境，一顿sudo操作猛如虎，快速安装完Docker环境，结果发现熟悉的命令行居然无法正常工作，是可忍孰不可忍。
```Shell
sudo apt-get update
sudo apt-get install \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg-agent \
    software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo apt-key fingerprint 0EBFCD88
sudo add-apt-repository \
   "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
   $(lsb_release -cs) \
   stable"
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io
```
第一个错误是，你按照官方文档安装完Docker，输入docker -v，一切显示正常的时候，此时，如果会执行docker run hello-world命令，会出现以下错误：
```Shell
$ docker run hello-world docker: Cannot connect to the Docker daemon at unix:///var/run/docker.sock. Is the docker daemon running?. See 'docker run --help'.
```
此时，你可能会尝试通过执行systemctl start docker命令来启动Docker服务，因为错误信息告诉我们，Docker的守护进程没有启动，可你会发现这样依然报错。可是为什么呢？明明Docker都在WSL里安装成功了啊，事实上除了docker -v不需要依赖守护进程，其余的命令都需要依赖守护进程，而WSL恰恰是不支持docker-engine的，所以，一种曲线救国的思路就是，让WSL去连接宿主机上的docker engine。果然，还是要安装Docker for Windows啊！那么，剩下的事情变得就非常简单啦，确保系统开启Hyper-V，然后安装Docker for Windows，并打开对宿主机Docker的监听，这些相信玩过Docker的人都会啦！

![暴露宿主机器Docker端口](https://ws1.sinaimg.cn/large/4c36074fly1g2oho3u2jcj20m80f8757.jpg)

接下来，我们给WSL中的Docker设置宿主机的地址，在终端中输入下列命令即可：
```Shell
export DOCKER_HOST=tcp://localhost:2375
```
此时，我们执行docker run hello-world命令，如果不出意外的话，我们会看到下面的画面，这说明我们的Docker环境已经正常工作啦：

![WSL中完美运行的Docker](https://ws1.sinaimg.cn/large/4c36074fly1g2ohrctulqj20m80bomy1.jpg)

博主按捺不住内心的激动，果断安装ELK全家桶，体验了下Kibana的可视化界面，开始思考：如何把存储在Mongodb中的日志数据放到ElasticSearch中。当然，这都是后话啦，因为博主马上发现了WSL中Docker的第二个坑，那就是终端关闭以后，针对宿主机的Docker连接就结束了。

![ELK全家桶](https://ws1.sinaimg.cn/large/4c36074fly1g2oht8m7jnj20m80badgj.jpg)

OK，为了解决这个问题，我们继续在终端中输入以下命令：
```Shell
echo "export DOCKER_HOST=tcp://localhost:2375" >> ~/.bashrc && source ~/.bashrc
```
在使用Docker的过程中，最令人困惑的部分当属分区的挂载，因为你时刻要搞清楚，它到底表示的是容器内部的分区，还是宿主机上的分区。对于运行在WSL中的Docker而言，它会采用类似/mnt/c/Users/Payne/<Your-App>这样的更符合Linux习惯的路径，而Docker for Windows则会使用类似/c/Users/Payne/<Your-App>这样更符合Windows习惯的路径。因此，如果你在使用Docker的过程中，需要处理分区挂载相关的东西，一个比较好的建议是修改WSL的配置文件(如果不存在需要自行创建)：
```Shell
sudo nano /etc/wsl.conf
[automount]
root = /
options = "metadata"
```
好了，以上就是在使用WSL中的Docker搭建ELK全家桶过程中遇到的问题的梳理，从体验上来讲，我个人会把Linux平台相关的工作渐渐转移到WSL上，因为安装双系统总会分散你的精力去处理维护相关的事情，虽然装系统对程序员来说都不算是个事儿，可我内心依旧排斥自己被贴上“修电脑”的标签。我会在后续的博客中分享.NET Core下日志分析平台构建相关内容，希望大家可以继续关注我的博客，这篇文章到此结束，谢谢大家！