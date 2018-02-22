---
title: 标准化数据库查询语言SQL知识点归纳
categories:
  - 编程语言
tags:
  - 数据库
  - SQL
  - SQLite
abbrlink: 2607734262
date: 2016-04-01 20:21:07
---
&emsp;&emsp;最近打算补补数据库这个短板，因为接触到“大数据”和“高并发”这类应用场景非常稀少，而且因为我自身对数据库存在抵触心理，认为数据库无非就是增删改写(CUID,即Create、Update、Insert、Delete)这些操作，所以平时我宁可用配置文件、SQLite这种轻量级的存储方案，每次安装Visual Studio看到各种和SQLServer相关的文件，我内心就充满了深深的厌恶感，所以像Orcale和SQLServer这种“存在感”非常强的数据库，我从来都是敬而远之。因为我就想使用一个简单的数据库，你为什么要给我这样复杂的东西？LAMP阵营里的MySQL和这两者相比会稍微好点，因为我可以通过Apache搭建的服务器来访问数据库而无需在设备上安装任何软件，可是对我来说MySQL的页面还是显得复杂了，因为我每次都需要为了了解如何去使用这些功能而花费时间。从程序员天性中的单纯来考虑这个世界，我们希望看到和使用的是一个简单的东西，这意味着我们将不再花费时间去了解如何使用它，就像你在微信中按下话筒按钮然后说话，当你松开手的时候语音消息自动发出一样。

<!--more-->

#什么是SQL？
&emsp;&emsp;好了，吐槽归吐槽，虽然我非常讨厌这些东西，可是我尊重这些东西被创造出来以至存在的意义。所以，我们首先来说说什么是SQL。SQL，即结构化查询语言(Structured Query Language)的简称，SQL是一种数据库查询和程序设计语言，可以实现对数据库数据的存储、查询、更新和管理功能。SQL是高级的非过程化编程语言，允许用户在高层数据结构上工作，用户无需了解数据的存储方式，所以SQL是一种和具体数据库无关的语言，结构化查询语句可以嵌套，因此它具有高度灵活性和强大的功能。事实上，从1986年10月美国国家标准协会对SQL进行规范后，SQL就作为关系型数据库管理系统的标准语言存在，1987年后在国际标准组织的支持下成为国际标准，而不同的数据库管理系统在实践过程中都对SQL进行了扩充，因此实际上不同的数据库系统上使用的SQL是无法相互通用的。
#SQL基本语法
##数据定义
###定义基本表
```
 CREATE TABLE<表名>(
 <字段名><数据类型><约束条件>,
 <字段名><数据类型><约束条件>,
);
```
例如，建立一个Student表，它由学号ID、姓名Name、性别Sex、年龄Age共4个属性组成。其中学号不能为空，其取值唯一，姓名取值唯一，则对应的SQL语句为：
```
CREATE TABLE Student(
ID CHAR(5) NOT NULL UNIQUE,
Name CHAR(20) UNIQUE,
Sex CHAR(2),
Age INT,
);
```
###修改基本表
```
ALTER TABLE<表名>
[ADD<新列名><数据类型>[约束条件]]
[DROP<约束条件>]
[MODIFY<列名><数据类型>]
```
例如，向Student表增加入学时间属性，其类型为日期型，则SQL命令为：
```
ALTER TABLE Student ADD EnterTime Date;
```
###删除基本表
```
DROP TABLE<表名>
```
例如，删除Student表的SQL命令为：
```
DROP TABLE Student；
```
###建立索引
```
CREATE [Unique] [Cluster] INDEX <索引名>
      ON <表名>（<列名>[次序],<列名>[次序]…）;
```
其中，[次序]可以为ASC(升序)、DESC(降序)，默认为升序。
```
Unique：每一个索引值对应唯一的数据记录
Cluster：聚簇索引，即索引项的顺序与表中记录的物理顺序保持一致。
```
例如，在Student表的Name列上建立一个聚簇索引并按照降序排列的SQL命令为：
```
CREATE Cluster INDEX StuName ON Student(Name DESC)
```
###删除索引
```
DROP INDEX <索引名>
```
例如，删除Student表的索引StuName的命令为：
```
DROP INDEX StuName;
```
##数据查询
```
SELECT[All|Distinct]<目标表达式> FROM <表名或视图名> WHERE<条件表达式> GROUP BY <列名>[HAVING<条件表达式>] ORDER BY <列名>[ASC|DESC];
```
###单表查询
1、查询全体学生的学号和姓名
```
SELECT ID Name FROM Student;
```
2、查询全体学生记录
```
SELECT * FROM Student;
```
3、查询年龄>21岁的学生记录
```
SELECT * FROM Student WHERE Age>21;
```
4、查询名字中第二个字为“阳”的学生记录
```
SELECT * FROM Student WHERE Name LIKE '__阳';
```
5、查询所有学生记录并按照成绩降序排列
```
SELECT * FROM Student ORDER BY Grade DESC;
```
6、求各个课程号及其相应的选课人数
```
SELECT CID,Count(SID) FROM SC GROUP BY CID；
```
在SQL语言中，可以使用下列集函数：
Count(*)：统计元祖个数
Count(<列名>)：统计指定列中元素个数
Sum(<列名>)：计算指定列中元素之和
Avg(<列名>)：计算指定列中元素平均数
Min和Max分别来计算指定列中的最小值和最大值

###连接查询

###嵌套查询

##数据更新
###插入数据
```
INSERT INTO <表名> [<属性列>,<属性列>…] VALUES [<属性值>,<属性值>…]
```
例如，在Student表中插入新记录(95020,'陈冬','男',18)的SQL命令为：
```
INSERT INTO Student (ID,Name,Sex,Age) VALUES (95020,'陈冬','男',18)
```
###修改数据
```
UPDATE <表名> SET [<列名>=<表达式>,<列名>=<表达式>…] WHERE <条件>
```
例如，将学号为95001的学生的年龄改为22岁
```
UPDATE Student SET Age=22 WHERE ID='95001';
```
###删除数据
```
DELETE FROM <表名> WHERE <条件>
```
例如，删除学号为95019的学生记录：
```
DELETE FROM Student WHERE ID='95019';
```
#SQLite案例
&emsp;&emsp;下面我们以SQLite这个数据库为例，来将SQL语言从理论的层面上提高到应用的层面上来。为什么选择SQLite呢？因为它轻量仅仅需要一个动态链接库就足矣！为什么选择Python来讲解这个案例呢？因为Python标准库中集成了SQLite！没错，我依然如此执著地选择自己喜欢的数据库，因为我喜欢！



#总结