---
abbrlink: 118272597
categories:
- 编程语言
copyright: true
date: 2020-05-08 12:27:11
description: var propertyParam = Expression.Property (parameter, condition.Field);searchParameters.Query.Add(new
  Condition() { Field = "StringValue", Op = Operation.Contains, Value = "山", OrGroup
  = "StringValue" });searchParameters.Query.Add(new Condition<Foo>() { Field = x =>
  x.StringValue, Op = Operation.Contains, Value = "有朋", OrGroup = "StringValue" })
tags:
- Linq
- Lambda
- 表达式树
title: 使用 Dynamic Linq 构建动态 Lambda 表达式
toc: true
---

相信大家都有这样一种感觉，`Linq`和`Lambda`是.NET 中一以贯之的存在，从最早的 Linq to Object 到 Linq to SQL，再到 EF/EF Core 甚至如今的.NET Core，我们可以看到`Lambda`表达式的身影出现地越来越频繁。虽然 Linq to Object 和 Linq to SQL，分别是以`IEnumerable<T>`和`IQueryable <T>`为基础来实现的。我个人以为，`Lambda`呢，其实就是匿名委托的“变种”，而`Linq`则是对`Lambda`的进一步封装。在`System.Linq.Expressions`命名空间下，提供大量关于表达式树的 API，而我们都知道，这些表达式树最终都会被编译为委托。所以，动态创建 Lambda 表达式，实际上就是指从一个字符串生成对应委托的过程，而一旦这个委托被生成，可以直接传递给 Where()方法作为参数，显然，它可以对源数据进行过滤，这正是我们想要的结果。

# 事出有因
在今天这篇博客中，我们主要介绍`System.Linq.Dynamic.Core`这个库，即我所说的 Dynamic Linq。本着“艺术源于生活的态度”，在介绍它的用法之前，不妨随博主一起看看，一个“简单“的查询是如何随着业务演进而变得越来越复杂。从某种意义上来说，正是它让博主想起了 Dynamic Linq。我们为客户编写了一个生成订单的接口，它从一张数据表中“消费”订单数据。最开始，它只需要过滤状态为“未处理”的记录，对应的 CRUD 可以表示为这样：
```CSharp
var orderInfos = repository.GetByQuery<tt_wg_order>(x => x.STATUS == 10);
```
后来，因为业务方存在重复/错误下单的情况，业务数据有了“软删除”的状态，相应地查询条件再次发生变化，这看起来还行对吧：
```CSharp
var orderInfos = repository.GetByQuery<tt_wg_order>(x => x.STATUS == 10 && x.Isdelete == 0);
```
再后来，因为接口处理速度不理想，无法满足客户的使用场景，公司大佬们建议“加机器”，而为了让每台服务器上消费的订单数据不同(据说是为了避免发生并发)，大佬们要求博主开放所有字段作为查询条件，这样，每台服务器上可以配置不同查询条件。自此，又双叒叕改：
```CSharp
var repository = container.Resolve<CrudRepositoryBase>();
var searchParameters = new SearchParameters() { PageInfo = new PageInfo() { PageSize = parameters.PAGE_SIZE.Value }};
searchParameters.QueryModel.Items.Add(new ConditionItem { Field = "STATUS", Method = QueryMethod.Equal, Value = 10 });
searchParameters.QueryModel.Items.Add(new ConditionItem { Field = "Isdelete", Method = QueryMethod.Equal, Value = 0 });
//此处省略更多的查询条件:)
var orderInfos = repository.GetByPage<tt_wg_order>(searchParameters);
```
可以想象得出，终极终终极的查询会变成下面这张图。这种方式看起来很美好对不对？可谁能想到，就在五一放假前的某一天里，博主还在替某个“刁钻”客户排查一组同样“刁钻”的过滤条件为什么没有生效。显然，我需要有一种更友好的方式，它可以从一个字符串变成一个委托，就像 JavaScript 里"邪恶"的 Eval()函数一样，说它邪恶，是因为它的输入是不可控的，"机智"的人类习惯把事件万物都当成 SQL 语句，其实，RESTful 接口里传 SQL、调存储过程难道不可以吗？同样，是因为这种做法太"邪恶"。

![过滤条件在风中凌乱]](https://i.loli.net/2020/05/11/QEDHwA9bZUTInJY.png)

# ParseLambda
首先，通过`nuget`安装：`System.Linq.Dynamic.Core`。这里主要介绍的是介绍的是其中的 ParseLambda()方法，顾名思义，它可以把一个字符串转换为指定类型的委托，一起来看下面的例子。首先，我们定义一个通用方法 BuildLambda<T>：
```CSharp
Func<T, bool> BuildLambda<T>(string exps)
{
  var sourceType = typeof(T);
  var sourceParameter = Expression.Parameter(sourceType);
  var lambdaExps = DynamicExpressionParser.ParseLambda(
    new[] { sourceParameter }, 
    typeof(bool), 
    exps
  );
  return lambdaExps.Compile() as Func<T, bool>;
}

var students = new List<Student>()
{
  new Student() { 
    Name = "长安书小妆", Age = 25, Address = "洛阳市洛龙区", 
    Teacher = new Teacher() { Name = "孔子" } },
  new Student() { 
    Name = "飞鸿踏雪", Age = 28, Address = "宁夏中卫市", 
    Teacher = new Teacher() { Name = "孔子" } },
};

var exps = "Age<=25 && Address.Contains(\"洛阳市\") && Teacher.Name=\"孟子\"";
var lambda = BuildLambda<Student>(exps);
var results = students.Where(lambda);
```
注意到，核心的代码其实只有`DynamicExpressionParser.ParseLambda()`这一句，这充分暴露了博主“调包侠”的本质。按照示例代码中的过滤条件，我们知道给定数据中是没有符合条件的数据的。假如你真的运行了这段代码，你就会得到真正的结果：我说的是对的(逃

# One More Thing
其实，我们今天所说这一切，从本质上来讲，还是属于表达式树的范畴，因为上面的例子，我们同样可以使用表达式树来编写，无非是这个第三方库帮我们隐藏了这部分细节。对于上面这个例子，如果用表达式树来写，会是什么样子的呢？相信熟悉表达式树的朋友，可以非常容易地写出下面的代码：
```CSharp
//x
var parameter = Expression.Parameter(typeof(tt_wg_order), "x");
//x.STATUS == 10
var condStatus = Expression.Equal(Expression.Property(parameter, "STATUS"), Expression.Constant(10));
//x.Isdelete == 0
var condIsDelete = Expression.Equal(Expression.Property(parameter, "Isdelete"), Expression.Constant(0));
//x.STATUS == 10 && x.Isdelete == 0
var condAndAlso = Expression.AndAlso(condStatus, condIsDelete);
//x => x.STATUS == 10 && x.Isdelete == 0
var lambda = Expression.Lambda<Func<tt_wg_order,bool>>(condAndAlso, parameter);
```
我们可以注意到，一个Lmabda表达式，可以抽象为:参数(`Parameter`)和函数体(`Body`)两部分，而`Body`实际上是由一个`操作符`和一个`值`组成。譬如这里的第一个条件：`x.STATUS == 10`。在这里基础上，我们可以定义一个类型：SearchParameters，它将每个条件抽象为字段(Field)、查询方法(QueryMethod)、值(Value)和或分组(OrGroup)。所以，它的处理逻辑就是，将相同 OrGroup 的条件放在一起用 Or 连接，然后再和其它条件放在一起用 And 连接。故而，它可以通过表达式构造出一个 Predict<T>类型的委托，而我们的数据持久层是使用 EF 来实现的，所以，它可以顺利成章地和 IQueryable<T>搭配使用，这就是我们这个 SearchParameters 的实现原理，它唯一让我觉得不好的地方是，字段(Field)不能通过一个 Lambda 表达式去构造，而必须传入一个字符串，这给了使用者写错字段名称的机会(逃：
```CSharp
 public static class LambdaExpressionBuilder 
 {
     private static Expression GetExpression (ParameterExpression parameter, Condition condition) 
     {
         var propertyParam = Expression.Property (parameter, condition.Field);
         var propertyInfo = propertyParam.Member as PropertyInfo;
         if (propertyInfo == null) throw new ArgumentException ($"Invalid field \"{condition.Field}\"");
         var realPropertyType = Nullable.GetUnderlyingType (propertyInfo.PropertyType) ?? propertyInfo.PropertyType;
         if (condition.Op != Operation.StdIn && condition.Op != Operation.StdNotIn)
             condition.Value = Convert.ChangeType (condition.Value, realPropertyType);
         var constantParam = Expression.Constant (condition.Value);
         switch (condition.Op) {
             case Operation.Equals:
                 return Expression.Equal (propertyParam, constantParam);
             case Operation.NotEquals:
                 return Expression.NotEqual (propertyParam, constantParam);
             case Operation.Contains:
                 return Expression.Call (propertyParam, "Contains", null, constantParam);;
             case Operation.NotContains:
                 return Expression.Not (Expression.Call (propertyParam, "Contains", null, constantParam));
             case Operation.StartsWith:
                 return Expression.Call (propertyParam, "StartsWith", null, constantParam);
             case Operation.EndsWith:
                 return Expression.Call (propertyParam, "EndsWith", null, constantParam);
             case Operation.GreaterThen:
                 return Expression.GreaterThan (propertyParam, constantParam);
             case Operation.GreaterThenOrEquals:
                 return Expression.GreaterThanOrEqual (propertyParam, constantParam);
             case Operation.LessThan:
                 return Expression.LessThan (propertyParam, constantParam);
             case Operation.LessThanOrEquals:
                 return Expression.LessThanOrEqual (propertyParam, constantParam);
             case Operation.StdIn:
                 return Expression.Call (typeof (Enumerable), "Contains", new Type[] { realPropertyType }, new Expression[] { constantParam, propertyParam });
             case Operation.StdNotIn:
                 return Expression.Not (Expression.Call (typeof (Enumerable), "Contains", new Type[] { realPropertyType }, new Expression[] { constantParam, propertyParam }));
         }

         return null;
     }

     private static Expression GetGroupExpression (ParameterExpression parameter, List<Condition> orConditions) 
     {
         if (orConditions.Count == 0)
             return null;

         var exps = orConditions.Select (c => GetExpression (parameter, c)).ToList ();
         return exps.Aggregate<Expression, Expression> (null, (left, right) => {
             if (left == null)
                 return right;
             return Expression.OrElse (left, right);
         });
     }

     public static Expression<Func<T, bool>> BuildLambda<T> (IEnumerable<Condition> conditions) 
     {
         if (conditions == null || !conditions.Any ()) return x => true;
         var parameter = Expression.Parameter (typeof (T), "x");

         //简单条件
         var simpleExps = conditions.ToList ().FindAll (c => string.IsNullOrEmpty (c.OrGroup))
             .Select (c => GetExpression (parameter, c))
             .ToList ();

         //复杂条件
         var complexExps = conditions.ToList ().FindAll (c => !string.IsNullOrEmpty (c.OrGroup))
             .GroupBy (x => x.OrGroup)
             .Select (g => GetGroupExpression (parameter, g.ToList ()))
             .ToList ();

         var exp = simpleExps.Concat (complexExps).Aggregate<Expression, Expression> (null, (left, right) => {
                 if (left == null)
                     return right;
                 return Expression.AndAlso (left, right);
             });;
         return Expression.Lambda<Func<T, bool>> (exp, parameter);
     }
 }

```
接下来，我们就可以以一种优雅的方式来对编写查询条件：
```CSharp
var searchParameters = new SearchParameters();
searchParameters.Query = new QueryModel();
searchParameters.Query.Add(new Condition() { Field = "IntValue", Op = Operation.LessThan, Value = 30 });
searchParameters.Query.Add(new Condition() { Field = "StringValue", Op = Operation.Contains, Value = "山", OrGroup = "StringValue" });
searchParameters.Query.Add(new Condition<Foo>() { Field = x => x.StringValue, Op = Operation.Contains, Value = "有朋", OrGroup = "StringValue" });
var lambda = LambdaExpressionBuilder.BuildLambda<Foo>(searchParameters.Query);
var where = lambda.Compile();
var result = list.Where(where);
```
这种实现可以说相当巧妙啦，因为通过有限的条件，我们就可以覆盖到大部分查询的场景，而如果直接去解析一个 Lambda 表达式，难度显然会增加不少。这里是以一个普通的泛型列表作为示例的，而在实际使用中，常常是结合 EntityFramework 这类 ORM 来使用的。相应地，我们只需要为 IQueryable 接口扩展出支持 SearchParameter 作为参数进行查询地扩展方法即可，这分别对应了我们在文章一开头所提到的`IEnumerable<T>`和`IQueryable <T>`。

可如果遇上 Dapper 这样的轻量级 ORM，我们要考虑的问题就变成了怎么通过 Lambda 表达式生成 SQL 语句，所以，通过 Dapper 来扩展功能的时候，最困难的地方，往往在于没法儿像 EF/EF Core 一样去随心所欲地 Where()，像 Dapper.Contrib 则只能先查询出所有结果再去做进一步的过滤，这种在数据量特别大的时候就会出问题。通过 Lambda 生成 SQL，最难的地方是，你压根不知道，人家会写一个什么样的表达式，而这个表达式，又怎么通过 SQL 去表达。那么，退而求其次，我们继续用 SearchParameters 来实现，因为它里面的 QueryMethod 是有限的，下面给出一个简单的实现：
```CSharp
public static class SearchParametersExtension 
{
    public static (string, Dictionary<string, object>) BuildSqlWhere (this SearchParameters searchParameters) 
    {
        var conditions = searchParameters.Query;
        if (conditions == null || !conditions.Any ())
            return (string.Empty, null);

        var sqlExps = new List<string> ();
        var sqlParam = new Dictionary<string, object> ();

        //构建简单条件
        var simpleConditions = conditions.FindAll (x => string.IsNullOrEmpty (x.OrGroup));
        sqlExps.Add (simpleConditions.BuildSqlWhere (ref sqlParam));

        //构建复杂条件
        var complexConditions = conditions.FindAll (x => !string.IsNullOrEmpty (x.OrGroup));
        sqlExps.AddRange (complexConditions.GroupBy (x => x.OrGroup).ToList ().Select (x => "( " + x.BuildSqlWhere (ref sqlParam, " OR ") + " )"));

        var sqlWhwere = sqlExps.Count > 1 ? string.Join (" AND ", sqlExps) : sqlExps[0];
        return ($" WHERE {sqlWhwere} ", sqlParam);
    }

    public static string BuildSqlWhere (this IEnumerable<Condition> conditions, ref Dictionary<string, object> sqlParams, string keywords = " AND ") 
    {
        if (conditions == null || !conditions.Any ())
            return string.Empty;

        var sqlParamIndex = 1;
        var sqlExps = new List<string> ();
        foreach (var condition in conditions) {
            var index = sqlParams.Count + sqlParamIndex;
            switch (condition.Op) {
                case Operation.Equals:
                    sqlExps.Add ($"{condition.Field} = @Param{index}");
                    sqlParams[$"Param{index}"] = condition.Value;
                    break;
                case Operation.NotEquals:
                    sqlExps.Add ($"{condition.Field} <> @Param{index}");
                    sqlParams[$"Param{index}"] = condition.Value;
                    break;
                case Operation.Contains:
                    sqlExps.Add ($"{condition.Field} LIKE @Param{index}");
                    sqlParams[$"Param{index}"] = $"%{condition.Value}%";
                    break;
                case Operation.NotContains:
                    sqlExps.Add ($"{condition.Field} NOT LIKE @Param{index}");
                    sqlParams[$"Param{index}"] = $"%{condition.Value}%";
                    break;
                case Operation.StartsWith:
                    sqlExps.Add ($"{condition.Field} LIKE @Param{index}");
                    sqlParams[$"Param{index}"] = $"%{condition.Value}";
                    break;
                case Operation.EndsWith:
                    sqlExps.Add ($"{condition.Field} LIKE @Param{index}");
                    sqlParams[$"Param{index}"] = $"{condition.Value}%";
                    break;
                case Operation.GreaterThen:
                    sqlExps.Add ($"{condition.Field} > @Param{index}");
                    sqlParams[$"Param{index}"] = $"{condition.Value}";
                    break;
                case Operation.GreaterThenOrEquals:
                    sqlExps.Add ($"{condition.Field} >= @Param{index}");
                    sqlParams[$"Param{index}"] = $"{condition.Value}";
                    break;
                case Operation.LessThan:
                    sqlExps.Add ($"{condition.Field} < @Param{index}");
                    sqlParams[$"Param{index}"] = $"{condition.Value}";
                    break;
                case Operation.LessThanOrEquals:
                    sqlExps.Add ($"{condition.Field} <= @Param{index}");
                    sqlParams[$"Param{index}"] = $"{condition.Value}";
                    break;
                case Operation.StdIn:
                    sqlExps.Add ($"{condition.Field} IN @Param{index}");
                    sqlParams[$"Param{index}"] = $"{condition.Value}";
                    break;
                case Operation.StdNotIn:
                    sqlExps.Add ($"{condition.Field} NOT IN @Param{index}");
                    sqlParams[$"Param{index}"] = $"{condition.Value}";
                    break;
            }

            sqlParamIndex += 1;
        }

        return sqlExps.Count > 1 ? string.Join (keywords, sqlExps) : sqlExps[0];
    }
}
```
现在，我们可以换一种方式来查Dapper，果然是因为手写SQL没有安全感的缘故啊！
```CSharp
var searchParameters = new SearchParameters();
searchParameters.Page = new PageModel() { PageSize = 10, CurrentPage = 1 };
searchParameters.Query = new QueryModel();
searchParameters.Query.Add(new Condition() { Field = "OrgCode", Op = Operation.Contains, Value = "飞天御剑流", OrGroup = "OrgCode" });
searchParameters.Query.Add(new Condition() { Field = "OrgCode", Op = Operation.Equals, Value = "新选组", OrGroup = "OrgCode" });
searchParameters.Query.Add(new Condition() { Field = "CreatedAt", Op = Operation.GreaterThenOrEquals, Value = new DateTime(2020, 1, 1)});
_repository.GetByQuery<BusinessUnit>(searchParameters);
```
对于定义`Condition`时，`Field`属性安全感缺失的问题，我们可以这样来解决：
```CSharp
public class Condition<T> : Condition

  public new Expression<Func<T, dynamic>> Field { get; set; }
  public Operation Op { get; set; }
  public object Value { get; set; }
  public string OrGroup { get; set; }
}

public class QueryModel : List<Condition>
{
  public void Add<T>(Condition<T> condition) where T : class
  {
    var filedName = string.Empty;
    var memberExp = condition.Field.Body as MemberExpression;
    if (memberExp == null)
    {
      var ubody = (UnaryExpression)condition.Field.Body;
      memberExp = ubody.Operand as MemberExpression;
    }
    filedName = memberExp.Member.Name;
    Add(new Condition() { Field = filedName, Op = condition.Op, Value = condition.Value, OrGroup = condition.OrGroup });
    }
  }
```
其实，这还是表达式树的内容，在上面的代码片段中，早已出现过它的身影，回想起多年前用这个东西改造 INotifyPropertyChanged 的时候，总觉得一切似曾相识：
```CSharp
searchParameters.Query.Add(new Condition<Foo>() { Field = x => x.StringValue, Op = Operation.Contains, Value = "有朋", OrGroup = "StringValue" });
```
# 本文小结
和博主的大多数博客一样，这篇博客是一个“醉翁之意不在酒”的博客。听起来在说如何动态创建 Lambda 表达式，实际上讲的还是表达式树，至于原因，则还是博客开篇所提到的“一以贯之”。博主想写这篇博客，是源于实际工作中遇到的“查询”问题，而最后解决的还真就是查询的问题。不管是 Dynamic Linq 中的 ParseLambda()还是表达式树中的 LambdaExpression，本质上都是同一个东西，最终的命运都是 Predict<T>这个委托。SearchParameters 则是对前者的一种简化，通过控制 Lambda 表达式的复杂度来简化问题，相比起直接传一个字符串过来，这种在风险的控制上要更高一点，之所以要传字符串，则是又一个非关技术的无聊的问题了，用 Jira 里的概念说应该叫做设计如此(By Design)。好了，以上就是这篇博客的内容啦，谢谢大家！