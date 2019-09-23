function VisitorCounter(appId, appKey, region, className) {
    this.appId = appId;
    this.appKey = appKey;
    this.baseUrl = 'https://' + this.appId.substring(0,8) + '.api.lncld.net';
    this.ipServUrl = 'https://api.ip.sb/jsonip';
    this.className = 'VisitorCounter'
    this.headers = {
        'X-LC-Id': this.appId,
        'X-LC-Key': this.appKey,
        'Content-Type': 'application/json'
    }

    /* 返回站点PV */
    this.sitePV = function () {
        return 0;
    };

    /* 返回站点UV */
    this.siteUV = function () {
        return 0;
    };

    /* 返回页面PV */
    this.pagePV = function () {
        var ele = document.getElementById('lc_counter_container_page_pv');
        var url = location.href;
        var title = ele.getAttribute('data-page-title').trim();
        var where = { page_url: url };
        var self = this;
        this.queryCounter('VisitorCounter', where).then(function (data) {
            if (data.results.length > 0) {
                var counter = data.results[0];
                var newCounter = {};
                newCounter.objectId = counter.objectId;
                newCounter.page_pv = counter.page_pv;
                newCounter.page_pv += 1;
                self.updateCounter('VisitorCounter', newCounter).then(function (data) { console.log(data); });
                ele.style.display = 'inline';
                ele = document.getElementById('lc_counter_value_page_pv')
                ele.innerText = newCounter.page_pv;
            } else {
                var newCounter = {};
                newCounter.page_title = title;;
                newCounter.page_url = url;
                newCounter.page_pv = 1;
                newCounter.page_uv = 1;
                self.createCounter('VisitorCounter', newCounter);
                ele.style.display = 'inline';
                ele = document.getElementById('lc_counter_value_page_pv')
                ele.innerText = newCounter.page_pv;
            }
        });
    };

    /* 返回页面UV */
    this.pageUV = function () {
        return 0;
    };

    /* 查询访客记录 */
    this.queryCounter = function (className, where) {
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
    this.createCounter = function (className, obj) {
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
    this.updateCounter = function (className, obj) {
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
    this.getIp = function(){
        var url = 'https://api.ip.sb/jsonip';
        return fetch(url, {
            mode: 'no-cors',
            method: 'POST',
        }).then(function (response) {
            console.log(response);
            return response.json();
        });
    }
};
