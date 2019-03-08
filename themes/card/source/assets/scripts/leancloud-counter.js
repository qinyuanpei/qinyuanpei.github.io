"use strict";
exports.__esModule = true;
var AV = require("leancloud-storage");
var AVCounter = /** @class */ (function () {

    function AVCounter(appId, appKey) {
        AV.init({ appId: appId, appKey: appKey });
    }

    //保存页面UV
    AVCounter.prototype.addPageUV = function () {
        return 0;
    };

    //保存页面PV
    AVCounter.prototype.addPagePV = function () {
        var ele = document.querySelector('#leancloud-counter-page-pv');
        var post_id = ele.attributes['data-post-id'];
        var post_url = ele.attributes['data-post-url'];
        var post_title = ele.attributes['data-post-title'];

        //优先使用post_id查询，否则使用post_url查询
        var query = new AV.Query('Counter');
        if (post_id != '') {
            query.equalTo('post_id', post_id);
        }
        else {
            query.equalTo("post_url", post_url);
        }

        query.find({
            success: function (results) {
                if (results.length > 0) {
                    var counter = results[0];
                    counter.fetchWhenSave(true);
                    counter.increment("page_pv");
                    counter.save(null, {
                        success: function (counter) {
                            var slot = document.querySelector('#leancloud-counter-value-page-pv');
                            var page_pv = counter.get('page_pv');
                            slot.text = page_pv;
                        },
                        error: function (counter, error) {
                            console.log('Failed to save page_pv with error message: ' + error.message);
                        }
                    });
                } else {
                    var newcounter = new Counter();
                    var acl = new AV.ACL();
                    acl.setPublicReadAccess(true);
                    acl.setPublicWriteAccess(true);
                    newcounter.setACL(acl);
                    newcounter.set("post_id", podt_id);
                    newcounter.set("post_url", post_url);
                    newcounter.set("post_title", post_title);
                    newcounter.set("page_pv", 1);
                    newcounter.save(null, { // 上传到LeanCloud服务器中
                        success: function (newcounter) {
                            var slot = document.querySelector('#leancloud-counter-value-page-pv');
                            var page_pv = counter.get('page_pv');
                            slot.text = page_pv;
                        },
                        error: function (newcounter, error) {
                            console.log('Failed to save page_pv with error message: ' + error.message);
                        }
                    });
                }
            },
            error: function (error) {
                console.log('Error:' + error.code + " " + error.message);
            }
        });
    };
    return AVCounter;
}());
