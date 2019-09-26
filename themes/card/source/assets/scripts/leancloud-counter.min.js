function VisitorCounter(appId, appKey, region, className) {
    this.appId = appId;
    this.appKey = appKey;
    this.baseUrl = 'https://' + this.appId.substring(0, 8) + '.api.lncld.net';
    this.ipServUrl = 'https://api.ip.sb/jsonip';
    this.className = 'VisitorCounter'
    this.headers = {
        'X-LC-Id': this.appId,
        'X-LC-Key': this.appKey,
        'Content-Type': 'application/json'
    }

    /* 初始化UV/PV */
    this.init = function (opts) {
        var site_uv = opts.site_uv || 0;
        var site_pv = opts.site_pv || 0;
        var page_url = location.href;
        var site_url = page_url.split('//')[1];
        site_url = site_url.substring(0, site_url.indexOf('/'));
        var site_title = document.title;
        var where = { page_url: site_url };
        var self = this;
        this.queryClass('VisitorCounter', where).then(function (data) {
            if (data.results.length == 0) {
                var newCounter = {};
                newCounter.page_pv = site_pv;
                newCounter.page_uv = site_uv;
                newCounter.page_url = site_url;
                newCounter.page_title = site_title
                self.createClass('VisitorCounter', newCounter).then(function (data) {
                    console.log('init PV/UV of ' + site_url + 'success');
                });
            }
        });

        //填充DOM
        this.pagePV();
        this.pageUV();
        this.sitePV();
        this.pageUV();
    }

    /* 返回站点PV */
    this.sitePV = function () {
        var url = location.href;
        if(url.indexOf('//')!=-1){
            url = url.split('//')[1];
            url = url.substring(0,url.indexOf('/'));
        }
        var where = { page_url: url };
        this.queryClass('VisitorCounter', where).then(function (data) {
            if (data.results.length > 0) {
                var counter = data.results[0];
                var ele = document.getElementById('lc_counter_value_site_pv')
                ele.innerText = counter.page_pv;
            }
        });
    };

    /* 返回站点UV */
    this.siteUV = function () {
        var url = location.href;
        if(url.indexOf('//')!=-1){
            url = url.split('//')[1];
            url = url.substring(0,url.indexOf('/'));
        }
        var where = { page_url: url };
        this.queryClass('VisitorCounter', where).then(function (data) {
            if (data.results.length > 0) {
                var counter = data.results[0];
                var ele = document.getElementById('lc_counter_value_site_pv')
                ele.innerText = counter.page_uv;
            }
        });
    };

    /* 返回页面PV */
    this.pagePV = function () {
        var url = location.href;
        var title = document.title;
        var where = { page_url: url };
        var self = this;
        this.queryClass('VisitorCounter', where).then(function (data) {
            if (data.results.length > 0) {
                var counter = data.results[0];
                var newCounter = {};
                newCounter.objectId = counter.objectId;
                newCounter.page_pv = counter.page_pv;
                newCounter.page_pv += 1;
                self.updateClass('VisitorCounter', newCounter).then(function (data) { console.log(data); });
                var ele = document.getElementById('lc_counter_value_page_pv')
                ele.innerText = newCounter.page_pv;
            } else {
                var newCounter = {};
                newCounter.page_title = title;;
                newCounter.page_url = url;
                newCounter.page_pv = 1;
                newCounter.page_uv = 1;
                self.createClass('VisitorCounter', newCounter);
                var ele = document.getElementById('lc_counter_value_page_pv')
                ele.innerText = newCounter.page_pv;
            }
        });
    };

    /* 返回页面UV */
    this.pageUV = function () {
        var url = location.href;
        var title = document.title;
        var self = this;
        this.getIp().then(function(res)
        {
            console.log(res);
            var where = { page_url: url, visitor_ip: res.ip };
            self.queryClass('VisitorRecord', where).then(function (data) {
                if (data.results.length == 0) {
                    newRecord = {};
                    newRecord.page_url = url;
                    newRecord.visitor_ip = ip;
                    self.createClass('VisitorRecord', newRecord);
                }
            });
        });
        

        where = { page_url: url };
        self.queryClass('VisitorCounter', where).then(function (data) {
            if (data.results.length > 0) {
                var counter = data.results[0];
                var ele = document.getElementById('lc_counter_value_page_pv')
                ele.innerText = counter.page_uv;
            }
        });
    };

    /* 查询访客记录 */
    this.queryClass = function (className, where) {
        var url = this.baseUrl + '/1.1/classes/' + className + '?where=' + JSON.stringify(where);
        return fetch(url, {
            mode: 'cors',
            method: 'GET',
            headers: this.headers,
        }).then(function (response) {
            return response.json();
        });
    };

    /* 新建访客记录 */
    this.createClass = function (className, obj) {
        var url = this.baseUrl + '/1.1/classes/' + className;
        return fetch(url, {
            mode: 'cors',
            method: 'POST',
            headers: this.headers,
            body: JSON.stringify(obj)
        }).then(function (response) {
            return response.json();
        });
    };

    /* 更新访客记录 */
    this.updateClass = function (className, obj) {
        var url = this.baseUrl + '/1.1/classes/' + className + '/' + obj.objectId;
        return fetch(url, {
            mode: 'cors',
            method: 'PUT',
            headers: this.headers,
            body: JSON.stringify(obj)
        }).then(function (response) {
            return response.json();
        });
    };

    /* 返回IP */
    this.getIp = function () {
        var url = 'http://ip-api.com/json/?lang=zh-CN';
        return fetch(url, {
            mode: 'cors',
            method: 'GET',
            headers: {
                'Access-Control-Allow-Origin': '*',
            }
        }).then(function (response) {
            return response.json();
        });
    }
};
