---
abbrlink: 1940333895
categories:
- 读书笔记
date: 2015-02-03 16:06:31
description: '*  数据类型：在Lua中支持6种数据类型，即数字(number)、字符串(string)、函数(function)、表(table)、用户数据(userdata)、空值(nil);#include
  "lua.h";print("This is a function declared in Lua")'
tags:
- Lua
- 脚本语言
- 语法
- 游戏
title: 脚本语言编程：Lua脚本编程入门
---

Lua是一门简单而强大的语言，其本身强大的扩展性使得这门语言在游戏设计等领域发挥着重要的作用。博主曾在Unity3D中使用过这门语言，并且针对Lua和Unity、C++等方面的内容进行了学习和讨论。最近因为在【游戏脚本高级编程】这本书中详细介绍了Lua脚本的相关内容，因此在这里记录下博主的读书心得，方便以后在需要的时候查阅。
<!--more-->
###Lua系统构成
Lua系统由Lua链接库、Luac编译器、Lua解释器三部分构成。
*  Lua链接库主要由lua.lib和lua.h这两个文件组成。Lua链接库主要负责对自身进行初始化及关闭操作、装载脚本与执行脚本、提
供可调用交互接口。
*  Luac编译器是一个由命令行驱动的编译器，其名称为Luac。当我们需要使用Luac编译器来编译一个脚本时，只需输入
```
>luac <FileName>    //FileName为脚本名称
```
   我们可以直接通过Lua链接库来装载脚本并在装载的过程中实现动态编译，可是这样会造成两个问题，即无法在动态编译过程中获取错误信息和动态编译使脚本加载速度变慢，在使用的时候应该注意到这个问题。
*  Lua解释器是一个由命令行驱动的代码运行环境，我们可以直接在这个环境中运行和测试脚本代码。

###Lua脚本语法
*  注释：Lua脚本的注释以--开始，如
```
> --这是一句注释
```
   当我们需要对多行脚本进行注释的时候，可以采取手动换行的方式进行多个单行的注释。
*  变量：Lua脚本中的变量是无类型的、隐式声明、首个字符必须是非数字字符、对大小写敏感。Lua脚本中变量的一个重要特性生支持多重赋值，即允许在赋值运算符的左边同时写下多个变量。如
```
-- 变量个数等于数值个数
x,y,z=1,2,3
-- 变量个数大于数值个数,z的值为nil
x,y,z=1,2
-- 变量个数小于数值个数,3这个数值将被忽略
x,y=1,2,3
```

*  数据类型：在Lua中支持6种数据类型，即数字(number)、字符串(string)、函数(function)、表(table)、用户数据(userdata)、空值(nil)。
```
数字(number)指整型和浮点型的数据。
字符串(string)指字符串类型的数据。
函数(function)指一个正式声明的函数的引用。如：
function fib(n)
  if(n<2) then 
  	return n
  else
    return fib(n-1)+fib(n-2)
  end
end
-- 在Lua中函数可以赋值给变量
fib2=fib
-- 调用fib函数
print(fib2(5))
表(table)是Lua语言中最简单同时是最复杂的数据结构：简单如普通数组，复杂如链表、字典、类等。
-- 我们在构造一个数据集合时，不需要指定数据类型和数据大小
-- 完成初始化后的数据集合默认索引从1开始，除非显示地声明索引0处的数值
-- 构造一个数字类型的数组
IntArray={1,2,3,4,5}
-- 构造一个字符串类型的数组
StringArray={"A","B","C","D"}
-- 打印IntArray的第一个元素,输出为1
print(IntArray[1])
-- 显示声明StringArray索引0处的数值
StringArray[0]="E"
-- 打印StringArray的第一个元素和第二个元素，输出为E,A
print(StringArray[0],StringArray[1])
-- 打印一个越界的数组值，输出为nil
print(IntArray[10])
-- 在Lua中表的数据类型可以是不同的
table[0]="table"
table[1]=1
-- 在Lua中表的索引可以是任意类型,因为表是基于键-值原理来工作的
Enemy={}
Enemy["Name"]="Enemy"
Enemy["HP"]=100
Enemy["Speed"]=30
-- 特别地，如果Key是一个合法的字符串类型，那么Table[Key]与Table.Key是等价的。
Enemy={}
Enemy.Name="Enemy"
Enemy.HP=100
Enemy.Speed=30
用户数据(userdata)是Lua语言中一个特殊的数据类型，它允许在Lua脚本的变量中存放C语言中的指针。
空值(nil)是各种语言中通用的一种数据类型，在此不再赘述。
在Lua脚本中我们可以使用type()函数来获取任意数据的类型
```

*  逻辑与表达式：Lua和大部分的编程类似支持加减乘除等运算，不同的是在Lua中使用~=来表示不等关系。
Lua支持的条件逻辑主要有if-then-else以及嵌套的if-then-else，Lua不支持switch结构。Lua支持的循环结构主要有while、for、repea三种结构，如：
```
-- 这是一个while循环
i=0
while(i<10) do
  i++
  print(i)
end

-- 这是一个for循环
for i=0,10 do
  print(i)
end 

-- 这是一个repeat循环
repeat 
  print(i)
  i++
until(i>10)

-- 这是一个扩展的for循环，类似于Foreach结构,主要用来遍历表(table)
for key,value in tables do
  print(k,value)
end
```
  
###Lua与C/C++交互
Lua与C/C++交互主要通过Lua 提供的C API来完成，其核心是Lua堆栈，一个简单的C++代码调用Lua脚本的示例代码如下：
```
#include <iostream>

using namespace std;

#include <iostream>

extern "C" {
#include "lua.h"
#include "lualib.h"
#include "lauxlib.h"
}

using namespace std;

int main()
{
    //创建Lua环境
    lua_State* L=luaL_newstate();
    //打开Lua标准库,常用的标准库有luaopen_base、luaopen_package、luaopen_table、luaopen_io、
    //luaopen_os、luaopen_string、luaopen_math、luaopen_debug
    luaL_openlibs(L);

    //下面的代码可以用luaL_dofile()来代替
    //加载Lua脚本
    luaL_loadfile(L,"script.lua");
    //运行Lua脚本
    lua_pcall(L,0,0,0);

    //将变量arg1压入栈顶
    lua_getglobal(L,"arg1");
    //将变量arg2压入栈顶
    lua_getglobal(L,"arg2");

    //读取arg1、arg2的值
    int arg1=lua_tonumber(L,-1);
    int arg2=lua_tonumber(L,-2);

    //输出Lua脚本中的两个变量
    cout <<"arg1="<<arg1<<endl;
    cout <<"arg2="<<arg2<<endl;

    //将函数printf压入栈顶
    lua_getglobal(L,"printf");
    //调用printf()方法
    lua_pcall(L,0,0,0);

    //将函数sum压入栈顶
    lua_getglobal(L,"sum");
    //传入参数
    lua_pushinteger(L,15);
    lua_pushinteger(L,25);
    //调用printf()方法
    lua_pcall(L,2,1,0);//这里有2个参数、1个返回值
    //输出求和结果
    cout <<"sum="<<lua_tonumber(L,-1)<<endl;

    //将表table压入栈顶
    lua_getglobal(L,"table");
    //获取表
    lua_gettable(L,-1);
    //输出表中第一个元素
    cout <<"table.a="<<lua_tonumber(L,-2)<<endl;

    //调用C++方法首先需要注册该方法
    lua_register(L, "AverageAndSum", AverageAndSum);
}

static int AverageAndSum(lua_State *L)
{
  //返回栈中元素的个数
  int n = lua_gettop(L);
  //存储各元素之和
  double sum = 0;
  for (int i = 1; i <= n; i++)
  {
      //参数类型处理
    if (!lua_isnumber(L, i))
    {
        //传入错误信息
      lua_pushstring(L, "Incorrect argument to 'average'");
      lua_error(L);
    }
    sum += lua_tonumber(L, i);
  }
  //传入平均值
  lua_pushnumber(L, sum / n);
  //传入和
  lua_pushnumber(L, sum);

  //返回值的个数，这里为2
  return 2;
}
```
请确保在计算机中安装了Lua环境，并在VC++目录中添加相关的头文件引用和库文件引用。相应的Lua脚本代码定义如下：
```
--在Lua中定义两个变量
arg1=15
arg2=20

--在Lua中定义一个表
table=
{
  a=25,
    b=30
}

--在Lua中定义一个求和的方法
function sum(a,b)
  return a+b
end

--在Lua中定义一个输出的方法
function printf()
  print("This is a function declared in Lua")
end

--在Lua中调用C++中定义并且注册的方法
average,sum=AverageAndSum(20,52,75,14)
print("Average=".average)
print("Sum=".sum)

```