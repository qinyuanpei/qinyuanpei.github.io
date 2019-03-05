var CloudCounter

<script>AV.initialize("{{site.leancloud.app_id}}", "{{site.leancloud.app_key}}");</script>
  <script>
    //新增访问次数
    function addCount(Counter) {
      // 页面（博客文章）中的信息：leancloud_visitors
      // id为page.url， data-flag-title为page.title
      var $visitors = $(".leancloud_visitors");
      var url = $visitors.attr('id').trim();
      var title = $visitors.attr('data-flag-title').trim();
      var query = new AV.Query(Counter);

      // 只根据文章的url查询LeanCloud服务器中的数据
      query.equalTo("post_url", url);
      query.find({
        success: function(results) {
          if (results.length > 0) {//说明LeanCloud中已经记录了这篇文章
            var counter = results[0];
            counter.fetchWhenSave(true);
            counter.increment("visited_times");// 将点击次数加1
            counter.save(null, {
              success: function(counter) {
                var $element = $(document.getElementById(url));
                var newTimes = counter.get('visited_times');
                $element.find('.leancloud-visitors-count').text(newTimes);
              },
              error: function(counter, error) {
                console.log('Failed to save Visitor num, with error message: ' + error.message);
              }
            });
          } else {
            // 执行这里，说明LeanCloud中还没有记录此文章
            var newcounter = new Counter();
            /* Set ACL */
            var acl = new AV.ACL();
            acl.setPublicReadAccess(true);
            acl.setPublicWriteAccess(true);
            newcounter.setACL(acl);
            /* End Set ACL */
            newcounter.set("post_title", title);// 把文章标题
            newcounter.set("post_url", url); // 文章url
            newcounter.set("visited_times", 1); // 初始点击次数：1次
            newcounter.save(null, { // 上传到LeanCloud服务器中
              success: function(newcounter) {
                var $element = $(document.getElementById(url));
                var newTimes = newcounter.get('visited_times');
                $element.find('.leancloud-visitors-count').text(newTimes);
              },
              error: function(newcounter, error) {
                console.log('Failed to create');
              }
            });
          }
        },
        error: function(error) {
          console.log('Error:' + error.code + " " + error.message);
        }
      });
    }

    //仅根据url和title查出当前访问次数，不做+1操作
    function showCount(Counter) {
      var $visitors = $(".leancloud_visitors");
      var url = $visitors.attr('id').trim();
      var title = $visitors.attr('data-flag-title').trim();
      var query = new AV.Query(Counter);

      // 只根据文章的url查询LeanCloud服务器中的数据
      query.equalTo("post_url", url);
      query.find({
        success: function(results) {
          if (results.length > 0) {//说明LeanCloud中已经记录了这篇文章
            var counter = results[0];
            var $element = $(document.getElementById(url));
            var newTimes = counter.get('visited_times');
            $element.find('.leancloud-visitors-count').text(newTimes);
          } else {
            //如果表里没查到记录，那就是异常情况了
            console.log('异常情况，不应该没记录的');
          }
        },
        error: function(error) {
          console.log('Error:' + error.code + " " + error.message);
        }
      });
    }

    //调用API获取IP
    function getVisitorIpAndJudge() {
      var ip;
      var options = {
        type: 'POST',
        dataType: "json",
        //async: false, //jquery3中可以直接使用回调函数，不用再指定async
        url: "https://freegeoip.net/json/?callback=?"
      };
      $.ajax(options)
      .done(function(data, textStatus, jqXHR) {
        if(textStatus == "success") {
          ip = data.ip;
        }
        judgeVisitor(ip)
      });
    }

    //判断访客是否已访问过该文章，及访问时间，符合条件则增加一次访问次数
    function judgeVisitor(ip) {
      var Counter = AV.Object.extend("visited_times");
      var Visitor = AV.Object.extend("visitors_record");

      var $postInfo = $(".leancloud_visitors");
      var post_url = $postInfo.attr('id').trim();

      var query = new AV.Query(Visitor);

      query.equalTo("visitor_ip", ip);
      query.equalTo("post_url", post_url);
      query.find({
        success: function(results) {
          if (results.length > 0) {
            console.log('该IP已访问过该文章');

            var oldVisitor = results[0];

            var lastTime = oldVisitor.updatedAt;
            var curTime = new Date();

            var timePassed = curTime.getTime() - lastTime.getTime();

            if(timePassed > 1 * 60 * 1000) {
              console.log('距离该IP上一次访问该文章已超过了1分钟，更新访问记录，并增加访问次数');

              addCount(Counter);

              oldVisitor.fetchWhenSave(true);
              oldVisitor.save(null, {
                success: function(oldVisitor) { },
                error: function(oldVisitor, error) {
                  console.log('Failed to save visitor record, with error message: ' + error.message);
                }
              });
            } else {
              console.log('这是该IP 1分钟内重复访问该文章，不更新访问记录，不增加访问次数');
              showCount(Counter);
            }
          } else {
            console.log('该IP第一次访问该文章，保存新的访问记录，并增加访问次数');

            addCount(Counter);

            var newVisitor = new Visitor();
            /* Set ACL */
            var acl = new AV.ACL();
            acl.setPublicReadAccess(true);
            acl.setPublicWriteAccess(true);
            newVisitor.setACL(acl);
            newVisitor.set("visitor_ip", ip);
            newVisitor.set("post_url", post_url);
            newVisitor.save(null, { // 上传到LeanCloud服务器中
              success: function(newVisitor) { },
              error: function(newVisitor, error) {
                console.log('Failed to create visitor record, with error message: ' + error.message);
              }
            });
          }
        },
        error: function(error) {
          console.log('Error:' + error.code + " " + error.message);
          addCount(Counter);
        }
      });
    }

    $(function() {
      if ($('.leancloud_visitors').length == 1) {
        // 文章页面，调用判断方法，对符合条件的访问增加访问次数
        getVisitorIpAndJudge();
      } else if ($('.post-link').length > 1){
        // 首页 暂未使用
        // showHitCount(Counter);
      }
    });
  </script>