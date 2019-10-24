function VisitorCounter(appId, appKey, region, className) {
    this.appId = appId;
    this.appKey = appKey;
    this.baseUrl = 'https://' + this.appId.substring(0, 8) + '.api.lncld.net';
    this.ipServUrl = 'https://api.ip.sb/jsonip';
    this.className = 'VisitorCounter'
    this.ipInfo = {};
    this.headers = {
        'X-LC-Id': this.appId,
        'X-LC-Key': this.appKey,
        'Content-Type': 'application/json'
    }


    /* 初始化UV/PV */
    this.init = function (opts) {
        var self = this;
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

        //注入脚本
        this.injectScript();

        //填充DOM
        this.pagePV();
        this.pageUV();
        this.sitePV();
        this.siteUV();
    }

    /* 返回站点PV */
    this.sitePV = function () {
        var url = location.href;
        if (url.indexOf('//') != -1) {
            url = url.split('//')[1];
            url = url.substring(0, url.indexOf('/'));
        }
        var where = { page_url: url };
        this.queryClass('VisitorCounter', where).then(function (data) {
            if (data.results.length > 0) {
                var counter = data.results[0];
                var ele = document.getElementById('lc_counter_value_site_pv');
                if (ele != null) {
                    ele.innerText = counter.page_pv;
                }
            }
        });
    };

    /* 返回站点UV */
    this.siteUV = function () {
        var url = location.href;
        if (url.indexOf('//') != -1) {
            url = url.split('//')[1];
            url = url.substring(0, url.indexOf('/'));
        }
        var where = { page_url: url };
        this.queryClass('VisitorCounter', where).then(function (data) {
            if (data.results.length > 0) {
                var counter = data.results[0];
                console.log(counter);
                var ele = document.getElementById('lc_counter_value_site_uv');
                if (ele != null) {
                    ele.innerText = counter.page_uv;
                }
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
                var ele = document.getElementById('lc_counter_value_page_pv');
                if (ele != null) {
                    ele.innerText = newCounter.page_pv;
                }
            } else {
                var newCounter = {};
                newCounter.page_title = title;;
                newCounter.page_url = url;
                newCounter.page_pv = 1;
                newCounter.page_uv = 1;
                self.createClass('VisitorCounter', newCounter);
                var ele = document.getElementById('lc_counter_value_page_pv');
                if (ele != null) {
                    ele.innerText = newCounter.page_pv;
                }
            }
        });
    };

    /* 返回页面UV */
    this.pageUV = function () {
        var url = location.href;
        var title = document.title;
        var ipInfo = JSON.parse(localStorage.getItem('ipInfo'));
        var where = { page_url: url, visitor_ip: ipInfo.ip };
        var self = this;
        self.queryClass('VisitorRecord', where).then(function (data) {
            if (data.results.length == 0) {
                newRecord = {};
                newRecord.page_url = url;
                newRecord.page_title = title;
                var ipInfo = JSON.parse(localStorage.getItem('ipInfo'));
                newRecord.visitor_ip = ipInfo.ip;
                newRecord.visitor_geo = ipInfo;
                var parser = new UAParser();
                newRecord.visitor_ua = parser.getResult();
                console.log(newRecord.visitor_ua);
                self.createClass('VisitorRecord', newRecord);
            }
        })
        .then(function(error){
            console.log(error);
        });

        where = { page_url: url };
        self.queryClass('VisitorCounter', where).then(function (data) {
            if (data.results.length > 0) {
                var counter = data.results[0];
                console.log(counter);
                var ele = document.getElementById('lc_counter_value_page_uv');
                if (ele != null) {
                    ele.innerText = counter.page_uv;
                }
            }
        });
    };

    /* 查询Class */
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

    /* 新建Class */
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

    /* 更新Class */
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

    /* 脚本注册 */
    this.injectScript = function () {
        var ipScript = document.createElement('script');
        ipScript.type = 'text/javascript';
        ipScript.src = 'https://api.ip.sb/geoip?callback=handleIP';
        var head = document.getElementsByTagName('head')[0]
        head.appendChild(ipScript);
        window.handleIP = function (data) {
            this.localStorage.clear();
            this.localStorage.setItem('ipInfo',this.JSON.stringify(data));
        };

        var uaScript = document.createElement('script');
        uaScript.type = 'text/javascript';
        uaScript.src = 'http://faisalman.github.io/ua-parser-js/src/ua-parser.js'
        head.appendChild(uaScript);
    }

    
};