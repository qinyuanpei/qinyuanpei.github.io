---
title: MySQL/Oracle/SQLServer三个版本的Split函数
categories:
  - 数据存储
tags:
  - 数据库
  - SQL
  - 函数
date: 2019-03-26 18:58:40
abbrlink:
---
最近工作中用到了SQL中的Split函数，在这里简单记录下这段脚本，我不得不吐槽SQL的表达能力。
```SQL
DELIMITER $$  
DROP FUNCTION IF EXISTS `SPLIT_STR`$$ 
CREATE FUNCTION SPLIT_STR(
  x VARCHAR(255),
  delim VARCHAR(12),
  pos INT
)
RETURNS VARCHAR(255)
BEGIN
RETURN REPLACE(SUBSTRING(SUBSTRING_INDEX(x, delim, pos),
       LENGTH(SUBSTRING_INDEX(x, delim, pos -1)) + 1),
       delim, '');
End $$
DELIMITER ; 
```

