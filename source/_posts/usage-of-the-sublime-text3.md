title: 在Sublime Text3下安装Package Control
toc: true
comment: true
date: 2015-04-17 12:54:41
categories: [开发工具]
tags: [Sublime,编辑器,IDE]
---
&emsp;&emsp;Sublime Text,是这个地球上最好的代码编辑器，没有之一。因为在过去的一段时间里，我使用的版本是SublimeText2，所以听说Sublime Text3版本稳定后，决定开始尝鲜。哈哈，我就是这么一个"喜新厌旧"的人！Sublime的强大不仅仅在它优雅的外表，更为重要的是她无可匹敌的扩展性，就是说我们可以通过插件来扩展它的功能，这对于一个喜欢DIY的人来说简直是无法抗拒的诱惑。不过在接收这些诱惑前，我们需要一个工具Package Control，它是Sublime里最为基础、最为重要的插件，好了，现在问题来了，Sublime怎么安装Package Control！

<!--more-->

&emsp;&emsp;在Sublime Text2下我们可以通过CTRL+~打开控制台，然后输入代码：
```Python
import urllib2,os; 
pf='Package Control.sublime-package'; 
ipp = sublime.installed_packages_path(); 
os.makedirs( ipp ) 
if not os.path.exists(ipp) 
   else None; 
urllib2.install_opener( urllib2.build_opener( urllib2.ProxyHandler( ))); 
open( os.path.join( ipp, pf), 'wb' ).write( urllib2.urlopen( 'http://sublime.wbond.net/' 
+pf.replace( ' ','%20' )).read()); 
print( 'Please restart Sublime Text to finish installation')
```
&emsp;&emsp;可是到了Sublime Text3下，因为版本不同的关系，内部API发生变化，因此需要使用新的代码：
```Python
import urllib.request,os; 
pf = 'Package Control.sublime-package'; 
ipp = sublime.installed_packages_path(); 
urllib.request.install_opener( urllib.request.build_opener( urllib.request.ProxyHandler()) ); 
open(os.path.join(ipp, pf), 'wb').write(urllib.request.urlopen( 'http://sublime.wbond.net/' 
+ pf.replace(' ','%20')).read())
```
&emsp;&emsp;当代码因为某些原因无法正常工作的时候，我们可以手动安装Package Control：
* 下载[PackageControl](https://sublime.wbond.net/Package%20Control.sublime-package)或者通过Github获取
```Shell
git clone git@github.com:wbond/package_control.git
```
* 通过Preferences->Browser Packages进入Installed Packages目录
* 重新启动Sublime，然后Enjoy it！

