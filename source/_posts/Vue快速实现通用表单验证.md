---
abbrlink: 169430744
categories:
- 编程语言
date: 2019-09-06 14:53:46
description: 通过Vue文档中关于[数据校验](<https://cn.vuejs.org/v2/cookbook/form-validation.html>)这一节的内容，我们了解到官方推荐的两个表单验证插件是[vuelidate](https://github.com/monterail/vuelidate)和[VeeValidate](http://vee-validate.logaretm.com/)，而实际上这篇博客中的第一个例子，就是由文档中的例子演化而来;<div
  class="form-group" name="password" rules="required">;-- script of LoginForm -->
tags:
- Vue
- 表单
- 验证
title: Vue快速实现通用表单验证
---

本文开篇第一句话，想引用鲁迅先生《祝福》里的一句话，那便是：**“我真傻，真的，我单单知道后端整天都是CRUD，我没想到前端整天都是Form表单”**。这句话要从哪里说起呢？大概要从最近半个月的“全栈工程师”说起。项目上需要做一个城市配载的功能，顾名思义，就是通过框选和拖拽的方式在地图上完成配载。博主选择了前后端分离的方式，在这个过程中发现：**首先，只要有依赖jQuery的组件，譬如Kendoui，即使使用了Vue，依然需要通过jQuery去操作DOM。其次，只有有通过Rozar生成的DOM，譬如HtmlHelper，Vue的双向绑定就突然变得尴尬起来，更不用说，Rozar中的@语法和Vue中的@指令相互冲突的问题，原本可以直接用v-for生成列表，因为使用了HtmlHelper，突然一下子变得厌恶起来，虽然Rozar语法非常强大，可我依然没有在JavaScript里写C#的热情，因为实在太痛苦啦Orz……**

所以，想做好前后端分离，首先需要分离出一套前端组件库，做不到这一点，前后端分离就无从谈起，就像我们公司的项目，即使框架切换到.NET Core，可是在很长的一段时间里，我们其实还是再写MVC，因为所有的组件都是后端提供的HtmlHelper/TagHelper这种形式。我这次做项目的过程中，其实是通过jQuery实现了一部分组件，正因为如此，一个在前后端不分离时非常容易实现的功能，在前后端分离以后发现缺好多东西，就比如最简单的表单验证功能，即便你是在做一个新项目，为了保证产品在外观上的一致性，你还是得依赖老项目的东西，所以，这篇博客主要想说说前后端分离以后，Vue的时代怎么去做表单的验证。因为我不想测试同事再给我提Bug，问我为什么只有来自后端接口的验证，而没有来自前端页面的验证。我希望，在写下这篇博客之前，我可以实现和老项目一模一样的表单验证。如同CRUD之于后端，80%的前端都是在写Form表单，所以，这个事情还是挺有意思的。

# 最简单的表单验证

OK，作为国内最接“地气”的前端框架，Vue的文档可以说是相当地“亲民”啦！为什么这样说呢，因为其实在[官方文档](<https://cn.vuejs.org/v2/cookbook/form-validation.html>)中，尤大已经提供了一个表单验证的示例，这个示例让我想起给某银行做自动化工具时的情景，因为这两者都是采用MVVM的思想，所以，理解起来是非常容易的，即：通过一个列表来存储错误信息，而这个错误信息会绑定到视图层，所以，验证的过程其实就是向这个列表里添加错误信息的过程。我们一起来看这个例子：

```HTML
<div>
    <h2>你好，请登录</h2>
    <div>
        <form id="loginFrom">
            <div>
                <label>邮箱</label>
                <input type="text" class="form-control" id="inputEmail3" placeholder="Email" v-model="email">
                </div>
            </div>
            <div>
                <label>密码</label>
                <input type="password" class="form-control" id="inputPassword3" placeholder="Password" v-model="password">
            </div>
            <div>
               <button type="button" class="btn btn-default login" v-on:click="login()">登录</button>
            </div>
            <div v-if="errorList.length > 0">
                <div class="alert alert-danger" role="alert">{{errorList.join(';')}}</div>
            </div>
        </form>
    </div>
</div>
<script>
var vm = new Vue({
    el: '#loginFrom',
    data: {
        email: "",
        password: "",
        errorList: []
    },
    methods: {
        validate: function () {
            this.errorList = []
            if (this.email == '') {
                this.errorList.push('请输入邮箱');
            } else {
                var reg = /^([a-zA-Z]|[0-9])(\w|\-)+@[a-zA-Z0-9]+\.([a-zA-Z]{2,4})$/;
                if (!reg.test(this.email)) {
                    this.errorList.push('请输入有效的邮箱');
                }
            }
            if (this.password == '') {
                this.errorList.push('请输入密码');
            } else {
                if (this.password.length < 6) {
                    this.errorList.push('密码长度不得少于6位');
                }
            }

            return this.errorList.length <= 0;
        },
        login: function () {
            if (this.validate()) {
                alert('登录成功');
            }
        }
    }
});
</script>
```

为了排除无关内容对大家的影响，写这个例子的时候，博主排除了一切复杂的HTML结构和CSS样式，经过简单润色以后，这个例子的效果展示如下，果然GUI满足了人们颜控的一面，可让这个世界高速运行的是CLI，Bootstrap是博主这种“全栈工程师”的最爱之一。这种验证方式简直是人类本能的反应，可这恰好是最糟糕的一个例子，因为这个代码完全没法复用，可以想象得到，如果再继续增加针对密码强度，譬如大小写、数字等等的验证，这个代码会混乱成什么样子，所以，这是最简单的表单验证，同样是最糟糕的表单验证。

![第一个表单验证的例子](https://ww1.sinaimg.cn/large/4c36074fly1g6q1v1x70cj20n50aa3yq.jpg)


# 基于jQuery的表单验证

其实，如果不是因为老项目依赖jQuery，而新项目在某些地方又需要和老项目保持一致，有谁会喜欢在Vue的世界里使用jQuery呢？因为数据驱动和事件驱动，真的是两种不同的思想，我就见过因为监听不到某个事件而花费一整天时间的人……所以，这里使用jQuery的表单验证插件[jQuery Validation](https://jqueryvalidation.org/documentation/)，目的只有一个，即实现博主对自己的承诺，做一个和老项目一模一样的表单验证。官方这个示例最大的问题是，它的检验逻辑扩展性比较差，后端同学对这个应该有所体会啦，譬如实际业务中常常有邮箱、手机号、非空、数字、正则等等的验证规则，而后端常常采用基于Attribute的验证或者是FluentValidation这样的库，所以，核心问题是，能不能定义相应的验证规则。接下来，我们通过jQuery的表单验证插件来实现验证。

通常情况下，jQuery Validation支持面向控件和面向代码两种验证方式。所谓面向控件，就是指在控件里添加类似`required`、`email`、`range`等等的扩展属性，jQuery Validation内置了十余种标准的验证规则，基本可以满足我们的日常使用。而面向代码，就是通过JavaScript来定义验证规则，这就非常符合Vue数据驱动的风格了，因为在JavaScript里一切皆是对象，而这些对象可以作为Vue中的数据来使用。自然而然地，在第一个示例的基础上，我们可以非常容易地扩展出基于jQuery的表单验证：

```HTML
var vm = new Vue({
    el:'#loginFrom',
    data:{
        email:"",
        password:"",
        validators:{
            rules: {
                email: {
                    required: true,
                    email: true
                },
                password: {
                    required: true,
                    minlength: 6,
                }
            },
            messages:{
                email:{
                    required:"请输入邮箱",
                    email:"请输入有效的邮箱"
                },
                password:{
                    required:"请输入密码",
                    minlength:"密码长度不得少于6位"
                }
            }
        }
    },
    mounted:function(){
        $('#loginFrom').validate(this.validators);
    }
});
```

对于当前表单loginFrom，其验证规则为validators，它完全参照`jQuery Validation`的API文档而来，具体大家可以从`jQuery Validation`的文档来做进一步了解。这里唯一看起来不爽的就是`#loginFrom`，因为它和整个Vue看起来格格不入。不过，像博主目前项目的处境，如果老项目里使用`jQuery`来对表单进行验证，而使用Vue开发的新项目要兼容老项目的设计风格，使用jQuery有什么不可以呢？不得不说，Vue作为一个渐进式的开发框架，真正照顾了各个"年龄"段的前端工程师。使用`jQuery Validation`以后的表单验证效果如下：

![基于jQuery的表单验证](https://ww1.sinaimg.cn/large/4c36074fly1g6q3nex2jhj20nk0anq36.jpg)

通过`jQuery Validation`，我们或许能感觉到一点不一样的地方，那就是表单验证其实还是蛮有意思的哈。也许是因为我原本是一个无聊的人，所以看到一点新的东西就觉得有趣。就像我虽然在提交数据时在后端做了校验，可牺牲的其实是整个前端的使用体验。而如果在前端对数据进行校验，是在输入过程中校验还是在输入完成校验，是通过表单自带的提交功能还是自己发起一个AJAX请求，这里面的确是有非常多的细节支撑的。第一种方案不支持远程校验，这更加能说明校验本身要考虑的不单单只有前端了，同理，有了前端的校验，不代表后端可以不做校验。前端时间有人在知乎上提问，大意是说前端该不该完全信任后端返回的数据，严格来说，我们不应该信任任何人提供的数据，而这就是校验这件事情本身的意义。

# 基于Vue的表单验证

OK，如果说前面的两种校验是因为我们有一点历史包袱，那么，接下来，我们将尝试采用更“现代化”的表单验证方式。通过Vue文档中关于[数据校验](<https://cn.vuejs.org/v2/cookbook/form-validation.html>)这一节的内容，我们了解到官方推荐的两个表单验证插件是[vuelidate](https://github.com/monterail/vuelidate)和[VeeValidate](http://vee-validate.logaretm.com/)，而实际上这篇博客中的第一个例子，就是由文档中的例子演化而来。我个人比较喜欢后者，所以，下面我们将使用这个插件来完成第三个例子。首先 ，我们通过`Vue-Cli`创建一个Vue项目，然后安装下面`vee-validate`和`vue-i18n`两个插件：

```Shell
npm install vee-validate@2.0.0 --save
npm install vue-i18n
```
注意到这里指定了版本号，这是因为最新的3.x超出了我这个新人的接受范围，一句话，太难了！接下来，我们在入口文件`main.js`中添加下面的代码，目的是启用这两个插件：

```JavaScript
import VueI18n from 'vue-i18n';
import VeeValidate from 'vee-validate';
import zh_CN from 'vee-validate/dist/locale/zh_CN'

//启用Vue国际化插件
Vue.use(VueI18n)

//配置VeeValidate
const i18n = new VueI18n({
    locale: 'zh_CN',
})

Vue.use(VeeValidate, {
    i18n,
    i18nRootKey: 'validation',
    dictionary: {
        zh_CN
    }
});
```
接下来，编写一个单文件组件`LoginForm.vue`:

```HTML
<!-- template of LoginForm -->
<template>
  <div class="container">
    <h2 class="text-center">你好，请登录</h2>
    <div class="row">
      <form class="form-horizontal col-md-offset-4 col-md-4" id="loginFrom">
        <div class="form-group">
          <label for="inputEmail3" class="col-sm-2 control-label">邮箱</label>
          <div class="col-sm-10">
            <input type="text" class="form-control" id="email" name="email" placeholder="Email" v-model="email" v-validate="'required|email'" data-vv-as="邮箱"/>
            <p class="alert alert-danger" role="alert" v-show="errors.has('email')">{{ errors.first('email') }}</p>
          </div>
        </div>
        <div class="form-group" name="password" rules="required">
          <label for="inputPassword3" class="col-sm-2 control-label">密码</label>
          <div class="col-sm-10">
            <input type="password" class="form-control" id="password" name="password" placeholder="Password" v-model="password" v-validate="'required|min:6'" data-vv-as="密码"/>
            <p class="alert alert-danger" role="alert" v-show="errors.has('password')">{{ errors.first('password') }}</p>
          </div>
        </div>
        <div class="form-group">
          <div class="col-sm-offset-2 col-sm-10">
            <div class="checkbox">
              <label>
                <input type="checkbox" />记住密码
              </label>
            </div>
          </div>
        </div>
        <div class="form-group">
          <div class="col-sm-offset-2 col-sm-10">
            <button type="button" class="btn btn-default login" v-on:click="login()">登录</button>
          </div>
        </div>
      </form>
    </div>
  </div>
</template>
<!-- script of LoginForm -->
<script>
export default {
  name: "LoginForm",
  components: {},
  data: () => ({
    email: "",
    password: ""
  }),
  methods: {
    login: function() {

    }
  }
};
</script>
<!-- style of LoginForm -->
<style scoped>
.login {
  color: white;
  height: 38px;
  width: 300px;
  background-color: #2b669a;
}
</style>

```

可以看到，我们在关键的两个input控件上添加了`v-validate`和`data-vv-as`这两个属性。比如我们这里需要验证用户输入的邮箱是否合法、邮箱是否为空，那么我们就可以使用下面的语法：

```HTML
<input type="text" class="form-control" id="email" name="email" placeholder="Email" v-model="email" v-validate="'required|email'" data-vv-as="邮箱"/>
<p class="alert alert-danger" role="alert" v-show="errors.has('email')">{{ errors.first('email') }}</p>
```

这些语法在Vue中被称为指令，而`data-vv-as`则是HTML5中的一个特性，用来给提示信息中的字段起一个别名。实际上，这个插件里同样内置了一批常见的校验规则。当控件中的值不满足校验条件时，就会在`errors`中产生错误信息，所以，我们根据错误信息中是否包含指定字段来决定要不要展示错误信息，这就是这个插件的作用。运行这个例子，我们会得到下面的结果。

![基于Vue的表单校验](https://ww1.sinaimg.cn/large/4c36074fly1g6rebtg81jj20n70hj74u.jpg)

既然提到这类表单验证最难的地方在于扩展性，那么下面我们再来看看如何扩展一个新的校验规则，这里以最常见的手机号校验为例,  个人以为这是这个插件最为强大的地方：

```JavaScript
Validator.extend('isMobile', {
  messages: {
    zh_CN: field => field + '必须是11位手机号码'
  },
  validate: value => {
    return value.length === 11 && /^((13|14|15|17|18)[0-9]{1}\d{8})$/.test(value)
  }
})
```
相信通过今天这篇博客，大家应该对Vue里的表单验证有一点心得了。这类验证的库或者框架其实非常多，整合到Vue中要做的工作无外乎写一个插件，在控件触发相关事件或者表单提交的时候进行验证。作为一个Vue的新人，这个过程可谓是路漫漫其修远。你大概想不到，我是在凌晨加班加到凌晨两点半的情况下做完这几个示例的，最近这两三个月里加的班比我过去三年都多，这到底是好事还是坏事呢？有时候不知道自己还能不能坚持下去，往事已矣，人难免会感到迷茫的吧！

# 本文小结

这篇博客主要通过三个示例分享了Vue下表单校验的实现，而促使博主对这一切进行研究的原始动力，则是源于一个实际工作中通过Vue开发的新项目。前后端要不要分离、项目里要不要继续使用jQuery、该不该频繁地操作DOM，这其实是毫无关联地三件事情，而这种事情90%的人是完全不关心的，就像有一种看起来相当“成年人”的做法，出了事情第一时间不是去纠结谁的过错，而是问能不能马上解决以及解决问题需要多长时间。这看起来好像一点问题都没有，可不去在意事件本身对错的人，是因为这些问题不需要他去处理，利益相关和责任相关是完全不一样的，因为你不能一出问题全部都找到程序员这里，这项目又不是程序员一个人的。我关心这些无关紧要的问题，纯粹是因为我对自己做的东西有一种感情，我想做好它而已，我希望自己是个纯粹的人，而且可以一直纯粹下去，晚安！