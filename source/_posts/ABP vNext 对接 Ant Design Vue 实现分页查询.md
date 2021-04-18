---
toc: true
title: ABP vNext 对接 Ant Design Vue 实现分页查询
categories:
  - 编程语言
tags:
  - ABP
  - Vue
  - 分页
  - 前端
copyright: true
abbrlink: 3670340170
date: 2021-04-07 21:07:47
---
在 [上一篇](https://blog.yuanpei.me/posts/2151871792/) 博客中，博主和大家分享了如何在 [EF Core](https://docs.microsoft.com/zh-cn/ef/core/get-started/overview/first-app?tabs=netcore-cli) 中实现多租户架构。在这一过程中，博主主要参考了 [ABP vNext](https://github.com/abpframework/abp) 这个框架。从上个月开始，我个人发起了一个项目，基于 [ABP vNext](https://github.com/abpframework/abp) 和 [Ant Design Vue](https://www.antdv.com/docs/vue/introduce-cn/) 来实现一个通用的后台管理系统，希望以此来推进 [DDD](https://www.jdon.com/ddd.html) 和 [Vue](https://cn.vuejs.org/) 的学习，努力打通前端与后端的“**任督二脉**”。因此，接下来的这段时间内，我写作的主题将会围绕 ABP vNext 和 Ant Design Vue。而在今天的这篇博客中，我们来说说 ABP vNext 对接 Ant Design Vue 实现分页查询的问题，希望能让大家在面对类似问题时有所帮助。我不打算写一个系列教程，更多的是从我个人的关注点出发，如果大家有更多想要交流的话题，欢迎大家通过评论或者邮件来留言，谢谢大家！

# ABP vNext中的分页查询

OK，当大家接触过 ABP vNext 以后，就会了解到这样一件事情，即，ABP vNext 中默认提供的分页查询接口，在大多数情况下，通常都会是下面这样的风格。这里以角色查询的接口为例，它对应的请求地址是：`/api/identity/roles?SkipCount=0&MaxResultCount=10`。此时，我们可以注意到，返回的数据结构中含有`totalCount`和`items`两个属性。其中，`totalCount`表示记录的总数目，`items`表示当前页对应的记录。

```json
{
  "totalCount": 2,
  "items": [
    {
      "name": "Admin",
      "isDefault": false,
      "isStatic": true,
      "isPublic": true,
      "concurrencyStamp": "cb53f2d7-159e-452d-9d9c-021629b500e0",
      "id": "39fb19e8-fb34-dfbd-3c70-181f604fd5ff",
      "extraProperties": {}
    },
    {
      "name": "Manager",
      "isDefault": false,
      "isStatic": false,
      "isPublic": false,
      "concurrencyStamp": "145ec550-7fe7-4c80-85e3-f317a168e6b6",
      "id": "39fb6216-2803-20c6-7211-76f8fe38b90e",
      "extraProperties": {}
    }
  ]
}
```

事实上，ABP vNext 中自带的分页查询，主要是通过`SkipCount`和`MaxResultCount`两个参数来实现。假设`MaxResultCount`，即分页大小为`m`，则第`n`页对应的`SkipCount`应该为`(n-1) * m`。如果大家对于`LINQ`非常熟悉的话，应该可以自然而然地联想到`Skip()`和`Take()`两个方法，这是一个非常自然的联想，因为 ABP vNext 就是这样实现分页查询的。这里以博主的“**数据字典**”分页查询接口为例：

```csharp
public async Task<PagedResultDto<DataDictionaryQueryDto>> GetCategories(
    GetDataDictionaryRequestInput input
)
{
  var totalCount = (await _dataDictRepository.GetQueryableAsync())
    .WhereIf(!string.IsNullOrEmpty(input.Name), x => x.Name.Contains(input.Name) || x.Name == input.Name)
    .WhereIf(!string.IsNullOrEmpty(input.Description), x => x.Description.Contains(input.Description) || x.Description == input.Description)
    .Count();

  var items = (await _dataDictRepository.GetQueryableAsync())
    .WhereIf(!string.IsNullOrEmpty(input.Name), x => x.Name.Contains(input.Name) || x.Name == input.Name)
    .WhereIf(!string.IsNullOrEmpty(input.Description), x => x.Description.Contains(input.Description) || x.Description == input.Description)
    .Skip(input.SkipCount)
    .Take(input.MaxResultCount)
    .ToList();

    return new PagedResultDto<DataDictionaryQueryDto>()
    {
      TotalCount = totalCount,
      Items = ObjectMapper.Map<List<DataDictionary>, List<DataDictionaryQueryDto>>(items)
    };
}
```

可以注意到，在 ABP vNext 中我们只需要构造好`TotalCount`和`Items`这两个属性即可。
 
# STable组件中的分页查询

接下来，在 Ant Design Vue 的 Pro 版本中，我们使用`STable`组件来展示列表类的数据，关于这个组件的使用方法，大家可以参考 [官方文档](https://github.com/vueComponent/ant-design-vue-pro/blob/master/src/components/Table/README.md)。按照最小化可行产品(**MVP**)的理念，一个最简单的`STable`组件的使用，如下面所示：

```html
<template>
  <s-table
    ref="table"
    size="default"
    :rowKey="(record) => record.data.id"
    :columns="columns"
    :data="loadData"
    :rowSelection="{ selectedRowKeys: selectedRowKeys, onChange: onSelectChange }"
  >
  </s-table>
</template>
```

对于这个组件而言，其中最重要的地方当属`data`属性，它接受一个函数，该函数的返回值为`Promise`对象，并且有一个参数：

```javascript
<script>
  import STable from '@/components'

  export default {
    components: {
      STable
    },
    data() {
      return {
        // 表格列名
        columns: [],
        // 查询条件
        queryParam: { },
        // 加载数据方法，必须为 Promise 对象
        loadData: parameter => {
          return getRoles(Object.assign({}, this.queryParam, parameter))
            .then(res => {
              return res.result
            })
        },
        // ...
        selectedRowKeys: [],
        selectedRows: []
      }
    }
  }
</script>
```

也许，你会好奇这个`parameter`到底是个什么东西？可如果我们将其打印出来，就会发现它其实是分页查询相关的参数：`Object { pageNo: 1, pageSize: 10 }`，而更进一步，如果深入到这个组件的源代码中，我们会注意到组件内部有一个`loadData()`方法：

```javascript
loadData (pagination, filters, sorter) {
  this.localLoading = true
  const parameter = Object.assign({
    pageNo: (pagination && pagination.current) ||
      this.showPagination && this.localPagination.current || this.pageNum,
    pageSize: (pagination && pagination.pageSize) ||
      this.showPagination && this.localPagination.pageSize || this.pageSize
    },
    (sorter && sorter.field && {
      sortField: sorter.field
    }) || {},
    (sorter && sorter.order && {
      sortOrder: sorter.order
    }) || {}, {
    ...filters
    }
  )
  const result = this.data(parameter)
  // 对接自己的通用数据接口需要修改下方代码中的 r.pageNo, r.totalCount, r.data
```

可以注意到，在`STable`组件内部，它会将分页、排序和过滤三种不同类型的参数，通过`Object.assign()`方法聚合到一个对象上，这个对象实际上就是我们刚刚打印出来的`parameter`。为什么这样说呢？因为它接下来就要调用`data`属性指向的方法啦！还记得这个`data`是什么吗？不错，它是一个函数，既然是一个函数，当然可以直接调用。到这里，我们可以获得第一个信息，即，**ABP vNext 中的表格组件STable，本身封装了分页查询相关的参数，只要将这些参数传递给后端就可以实现分页查询**。

# 实现参数转换层

既然，这个参数和 ABP vNext 需要的参数不同，为了不修改已有的接口，我们考虑在这中间加一层转换。为此，我们定义下面的函数：

```javascript
// 默认列表查询条件
const baseListQuery = {
  page: 1,
  limit: 20
}

// 查询条件转化
export function transformAbpListQuery (query) {
  query.filter = query.filter === '' ? undefined : query.filter

  if (window.isNaN(query.pageSize)) {
    query.pageSize = baseListQuery.limit
  }
  if (window.isNaN(query.pageNo)) {
    query.pageNo = baseListQuery.page
  }

  const abpListQuery = {
    maxResultCount: query.pageSize,
    skipCount: (query.pageNo - 1) * query.pageSize,
    sorting: '',
    filter: '',
    ...query
  }

  if (typeof (query.sortField) !== 'undefined' && query.sortField !== null) {
    abpListQuery.sorting = query.sortOrder === 'ascend'
      ? query.sortField
      : `${query.sortField} Desc`
  }

  return abpListQuery
}
```

代码非常简单，通过`transformAbpListQuery`函数，我们就实现了从`STable`到`ABP vNext`的参数转换。需要说明的是，这里的排序使用到了 [System.Linq.Dynamic.Core](https://github.com/zzzprojects/System.Linq.Dynamic.Core) 这个库，它可以实现`IQueryable`级别的、基于字符串的动态表达式构建功能，使用方法如下：

```csharp
var resultSingle = queryable.OrderBy<User>("NumberProperty");
var resultSingleDescending = queryable.OrderBy<User>("NumberProperty DESC");
var resultMultiple = queryable.OrderBy<User>("NumberProperty, StringProperty");
```

所以，当它为降序排序时，我们在排序字段的后面添加`DESC`即可。关于`filter`参数，我准备做一套通用性更强的方案，所以，这里就暂时留空啦！接下来，如果大家足够细心的话，会发现`STable`组件对返回值同样有一定的要求，它要求返回值中至少含有`pageNo`、`totalCount`, `data`三个属性，而这，是我们获得的第二个信息：

```javascript
// 对接自己的通用数据接口需要修改下方代码中的 r.pageNo, r.totalCount, r.data
// eslint-disable-next-line
if ((typeof result === 'object' || typeof result === 'function') 
  && typeof result.then === 'function') {
  result.then(r => {
    this.localPagination = this.showPagination 
    && Object.assign({}, this.localPagination, {
      current: r.pageNo, // 返回结果中的当前分页数
      total: r.totalCount, // 返回结果中的总记录数
      showSizeChanger: this.showSizeChanger,
      pageSize: (pagination && pagination.pageSize) ||
      this.localPagination.pageSize
    }) || false

    this.localDataSource = r.data // 返回结果中的数组数据
    this.localLoading = false
  })
}
```

依样画葫芦，我们继续编写转换层的代码，返回值格式参考了 Ant Design Vue 中Mock接口的返回值格式：

```javascript
// 查询结果转化
export function transformAbpQueryResult (data, message, code = 0, headers = {}) {
  const responseBody = { }
  responseBody.result = data
  if (message !== undefined && message !== null) {
    responseBody.message = message
  }
  if (code !== undefined && code !== 0) {
    responseBody.code = code
    responseBody._status = code
  }
  if (headers !== null && typeof headers === 'object' 
    && Object.keys(headers).length > 0) {
    responseBody._headers = headers
  }
  responseBody.timestamp = new Date().getTime()
  return responseBody
}

// 分页查询结果转化
export function buildPagingQueryResult (queryParam, data) {
  for (const item of data.items) {
    // Ant Design Vue 中要求每行数据中必须存在字段：key
    item.key = item.id
  }
  const pagedResult = {
    pageSize: queryParam.pageSize,
    pageNo: queryParam.pageNo,
    totalCount: data.totalCount,
    totalPage: data.totalCount / queryParam.pageSize,
    data: data.items
  }
  return transformAbpQueryResult(pagedResult)
}
```

对于分页结果而言，我们会将分页大小、当前页数、总页数、总记录数及其对应的数据，统一封装到一个对象中，然后再将其传递给返回值中的`result`属性。

# 最终对接效果

好了，写了这么多，我们到底实现了一个什么效果呢？对于一开始的角色查询接口，我们可以这样封装到前端的服务层：

```javascript
export function getRoles (query) {
    const queryParam = transformAbpListQuery(query)
    return axios({
      url: AppConsts.resourceService.baseUrl + '/api/identity/roles',
      method: 'get',
      params: queryParam
    }).then(data => {
        return buildPagingQueryResult(queryParam, data)
    })
}
```

接下来，我们只需要实现`loadData()`方法即可：

```javascript
import { getRoles, updateRole, createRole, deleteRole } from '@/api/recipe/abp.role'

loadData: parameter => {
  return getRoles(Object.assign({}, parameter, this.queryParam))
    .then(res => {
      return res.result
    })
  },
```

此时，我们可以注意到，ABP vNext 与 Ant Design Vue 完美地集成在一起，并且参数的转换完全符合我们的预期。这样做的好处显而易见，我们只需要遵循 ABP vNext 的规范进行开发即可，考虑到 ABP vNext 可以直接将`ApplicationService`暴露为 API 接口，这意味着我们写完了接口，就可以立即开始前后端的联调工作，这无疑可以加快我们的研发效率！

![ABP vNext 与 Ant Design Vue 完成整合](https://i.loli.net/2021/04/09/Uq1M4ZEOJ5VhTdl.png)

好了，以上就是这篇博客的全部内容啦！这篇博客要实现的功能其实并不复杂，唯一的难点是，需要在前端和后端两个技术栈上频繁地切换上下文，这可能就是全栈开发者面临的最大挑战，因为技术世界浩如烟海，而一个人的精力终究有限，古人云：**朝闻道，夕死可矣**，人生百年，吾道不孤，还是请你继续努力哦！
