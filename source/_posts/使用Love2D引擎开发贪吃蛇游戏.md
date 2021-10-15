---
abbrlink: 426338252
categories:
- 游戏开发
date: 2015-03-10 10:51:19
description: local dir=1;这里定义了 getNextPoint()的方法，目的是计算在蛇头位置添加的下一个元素，这里我们注意到根据蛇的移动方向(dir)的不同，其中 0 表示上、1 表示下、2 表示左、3 表示右，计算出下一个元素的位置，因为在这个游戏中网格大小是 20，所以这里可以直接根据坐标来计算一个元素的位置;local
  gameState=1
tags:
- Love2D
- 游戏开发
- 贪吃蛇
title: 使用 Love2D 引擎开发贪吃蛇游戏
---

&emsp;&emsp;今天来介绍博主最近捣腾的一个小游戏“贪吃蛇”。“贪吃蛇”这个游戏相信大家都不会感到陌生吧。今天博主将通过[Love2D](http://love2d.org/)这款游戏引擎来为大家实现一个简单的贪吃蛇游戏,在本篇文章当中我们将会涉及到“贪吃蛇”的基本算法、Lua 语言编程等基本的内容，希望能够对大家开发类似的游戏提供借鉴和思考，文章中如有不足之处，还希望大家能够谅解，因为博主的游戏开发基本就是这样慢慢摸索着学习，所以难免会有不足的地方。

<!--more-->

## 游戏算法
&emsp;&emsp;我们首先来看看贪吃蛇是怎么移动的？
![贪吃蛇游戏算法演示1](https://ww1.sinaimg.cn/large/4c36074fly1fz05nhb62pj205m05lq33.jpg)
![贪吃蛇游戏算法演示2](https://ww1.sinaimg.cn/large/4c36074fly1fz05k1yzipj205m05lq33.jpg)
![贪吃蛇游戏算法演示3](https://ww1.sinaimg.cn/large/4c36074fly1fz05dugbchj205m05lq33.jpg)
![贪吃蛇游戏算法演示4](https://ww1.sinaimg.cn/large/4c36074fly1fz01zh5qn2j205m05lq33.jpg)
&emsp;&emsp;通过这四张图的演示，我们可以发现这样一个规律：
>蛇的移动其实是将蛇身体的最后一个元素移动到第一个元素的位置

&emsp;&emsp;那么完成这样一个工作需要两个步骤：
> 1、将在蛇头位置插入一个新的元素
> 2、移除蛇尾位置的最后一个元素

&emsp;&emsp;好了，了解了蛇的移动后我们再来考虑一个问题，怎样判断蛇吃到了食物？思路和蛇的移动类似，主要考虑在蛇头插入的这个元素和食物的关系，如果这个元素的坐标和食物的坐标是相同的，那么就可以认为蛇吃到了食物，此时蛇的身体应该是变长的，所以只要在蛇头位置插入一个元素就可以了。反之，如果蛇没有吃到食物，那么蛇应该是移动的，所以就可以按照移动的方法来处理了。那么在蛇头位置插入的这个元素该如何确定呢？我们来看下面这段程序：
```Lua
--计算下一个目标点
function getNextPoint()
  --计算下一个目标点
  snake={}
  if(dir==0) then
    snake.x=snakes[1].x
    snake.y=snakes[1].y-20
  end
  if(dir==1) then
    snake.x=snakes[1].x
    snake.y=snakes[1].y+20
  end
  if(dir==2) then
    snake.x=snakes[1].x-20
    snake.y=snakes[1].y
  end
  if(dir==3) then
    snake.x=snakes[1].x+20
    snake.y=snakes[1].y
  end

  return snake
end
```
&emsp;&emsp;这里定义了 getNextPoint()的方法，目的是计算在蛇头位置添加的下一个元素，这里我们注意到根据蛇的移动方向(dir)的不同，其中 0 表示上、1 表示下、2 表示左、3 表示右，计算出下一个元素的位置，因为在这个游戏中网格大小是 20，所以这里可以直接根据坐标来计算一个元素的位置。snakes 是一个 table，保存的是当前的蛇的全部元素的坐标。通过维护这个 table，我们就可以利用绘图的函数绘制出蛇的身体，这样蛇就可以移动起来了。我们来看看蛇是怎样移动的：
```Lua
--核心算法——蛇的移动
function SnakeUpdate()
  --获取元素个数
  local n=table.maxn(snakes)
  if(table.maxn(snakes)>0) then
    if(getNextPoint().x==foodX and getNextPoint().y==foodY) then
      --将下一个目标点的位置插入表中
      table.insert(snakes, 1, getNextPoint())
      --将食物状态设置为BeEated
      foodState="BeEated"
    else
      --将下一个目标点的位置插入表中
      table.insert(snakes, 1, getNextPoint())
      --移除最后一个元素
      table.remove(snakes,n+1)
    end 
  end
end
```
&emsp;&emsp;在这里我们定义了一个 foodState 变量以保存食物的状态，当食物的状态为 BeEated 的时候表示食物被蛇吃掉了，此时应该重新生成一个食物的坐标，此时事物的状态将变成 WaitToEat。食物的坐标保存在 foodX 和 foodY 这两个变量中，大家可以到完整的代码中去查看。
## 游戏状态
我们知道蛇碰到四周墙壁的时候就会死亡，此时游戏结束。这个比较简单，只要判断蛇头的坐标和屏幕的关系就可以了。因为在这个游戏中屏幕的尺寸为 640X640，所以判断游戏是否结束的代码可以这样写：
```Lua
--判断游戏状态
  if(snakes[1].x<=0 or snakes[1].x>=640 or snakes[1].y<=0 or snakes[1].y>=640) then
    gameState=0
  else
    gameState=1
  end
```
&emsp;&emsp;这里 gameState 为 0 表示游戏结束，gameState 为 1 表示游戏正常进行。
## 完整代码
&emsp;&emsp;在完成了这些核心的算法以后，剩下的事情就交给 Love2D 引擎来绘制吧，最后给出完整的程序代码：
```Lua
--定义窗口宽度和高度
local w=640
local h=640
--定义网格单元大小
local unitSize=20;

--方块的初始位置
local initX=320
local initY=320

--移动方向
local dir=1

--贪吃蛇集合
local snakes={}

--食物状态
--WaitToEat：绘制食物
--BeEated：随机生成食物
local foodState="WaitToEat"

--游戏状态
--0：游戏结束
--1：游戏正常
local gameState=1

--食物的位置
local foodX=0
local foodY=0

--Love2D加载事件
function love.load()
  --设置窗口标题
  love.window.setTitle("Love2D-贪吃蛇游戏")
  --设置窗口大小
  love.window.setMode(w,h)
  --定义字体
  myFont=love.graphics.newFont(30)
  --设置字体
  love.graphics.setFont(myFont)
  --设置背景色
  love.graphics.setBackgroundColor(255,255,255,255)
  --设置线条类型为平滑
  love.graphics.setLineStyle("smooth")
  --设置线宽
  love.graphics.setLineWidth(0.1)

  --蛇的初始化(蛇的长度为5)
  for i=1,5 do
    snake={}
    snake.x=initX +(i-1) * 20
    snake.y=initY
    snakes[i]=snake
  end

  --食物初始化
  foodX=love.math.random(32-1)*20
  foodY=love.math.random(32-1)*20
end


--Love2D绘制事件
function love.draw()
  --绘制竖线
  love.graphics.setColor(0,0,0,255)
  for i=0,w,unitSize do
    love.graphics.line(0,i,h,i)
  end
  --绘制横线
  for j=0,h,unitSize do
    love.graphics.line(j,0,j,w)
  end

  --绘制蛇
  for i=1,table.maxn(snakes) do
    love.graphics.setColor(0,0,255,255)
    love.graphics.rectangle("fill",snakes[i].x,snakes[i].y,20,20)
  end

  --绘制食物
  if(foodState=="WaitToEat") then
    love.graphics.setColor(255,0,0,255)
    love.graphics.rectangle("fill",foodX,foodY,20,20)
  end

  --如果游戏结束则显示GameOver
  if(gameState==0) then
    love.graphics.setColor(255,0,0,255)
    love.graphics.print("Game Over",250,300)
  end
end 

--
function love.update(dt)
  --判断游戏状态
  if(snakes[1].x<=0 or snakes[1].x>=640 or snakes[1].y<=0 or snakes[1].y>=640) then
    gameState=0
  else
    gameState=1
  end

  --如果游戏状态为正常
  if(gameState==1) then
    SnakeUpdate()
    FoodUpdate()
  end
end

--核心算法——蛇的移动
function SnakeUpdate()
  --获取元素个数
  local n=table.maxn(snakes)
  if(table.maxn(snakes)>0) then
    if(getNextPoint().x==foodX and getNextPoint().y==foodY) then
      --将下一个目标点的位置插入表中
      table.insert(snakes, 1, getNextPoint())
      --将食物状态设置为BeEated
      foodState="BeEated"
    else
      --将下一个目标点的位置插入表中
      table.insert(snakes, 1, getNextPoint())
      --移除最后一个元素
      table.remove(snakes,n+1)
    end 
  end
end

--随机生成食物
function FoodUpdate()
  --如果食物被蛇吃掉则重新生成食物
  if(foodState=="BeEated") then
    foodX=love.math.random(32-1)*20
    foodY=love.math.random(32-1)*20
    foodState="WaitToEat"
   end
end

--根据玩家按下的键位定义不同的方向
function love.keypressed(key)
  if(key=="a") then 
    dir=2
  end
  if(key=="d") then 
    dir=3
  end
  if(key=="w") then 
    dir=0
  end
  if(key=="s") then 
    dir=1
  end
end

--计算下一个目标点
function getNextPoint()
  --计算下一个目标点
  snake={}
  if(dir==0) then
    snake.x=snakes[1].x
    snake.y=snakes[1].y-20
  end
  if(dir==1) then
    snake.x=snakes[1].x
    snake.y=snakes[1].y+20
  end
  if(dir==2) then
    snake.x=snakes[1].x-20
    snake.y=snakes[1].y
  end
  if(dir==3) then
    snake.x=snakes[1].x+20
    snake.y=snakes[1].y
  end

  return snake
end
```
&emsp;&emsp;将代码压缩成.love 文件后就可以运行了，我们来看看最终的效果：

![Demo1](https://camo.githubusercontent.com/c67d24e7970bb47f8c6ed45bd520ab09dfb4c917/687474703a2f2f7069632e636f6e6e2e63632f62732e706e67)
![Demo2](https://camo.githubusercontent.com/479dd593c4a4f722e07ed4ccc5ddd574fe5dbd10/687474703a2f2f7069632e636f6e6e2e63632f5a722e706e67)

&emsp;&emsp;本文的项目作为开源项目托管在 Github 上，可以通过[Github](https://github.com/qinyuanpei/Love2D_Snake)来获取项目源代码。谢谢大家，今天的内容就是这样了。