(()=>{var a=class{ele;subjectId;requestUrl;requestType;localData;constructor(e,t,s,r,n){if(this.ele=e,this.subjectId=t,this.requestUrl=s,this.requestType=r,this.localData=n?JSON.parse(n):null,this.localData){let i=this.convert(this.localData,this.requestType);this.requestType=="movie"?this.renderMovie(i):this.renderBook(i)}else{let i=this.fetchData();this.requestType=="movie"?this.renderMovie(i):this.renderBook(i)}}fetchData(){var e=localStorage.getItem(this.subjectId);if(e==null||typeof e>"u")fetch(this.requestUrl).then(t=>t.json()).then(t=>{let s={};if(this.requestType=="movie")s={title:t.data[0].name,link:"https://movie.douban.com/subject/"+t.doubanId,cover:t.data[0].poster,desc:t.data[0].description,star:Math.floor(parseFloat(t.doubanRating||0)),vote:t.doubanRating||0,genre:t.data[0].genre,date:t.dateReleased,director:t.director[0].data[0].name};else{let r=t.summary;r=r.replaceAll("<p>",""),r=r.replaceAll("</p>",""),s={title:t.title,link:"https://book.douban.com/subject/"+this.subjectId,cover:t.images.medium,desc:r,star:Math.floor(parseFloat(t.rating.average||0)),vote:t.rating.average||0,date:t.pubdate,author:t.author.join(",")}}return localStorage.setItem(this.subjectId,JSON.stringify(s)),s});else return JSON.parse(e)}renderMovie(e){let t=e.genres.map(r=>`<span class="card-tag">${r}</span>`).join(""),s=`
        <div class="douban-card" id="douban-card">
            <div class="card-content">
                <div class="card-title">${e.title}</div>
                <div class="card-meta">
                    <span class="card-rating">${e.vote}</span>
                    <div class="card-stars">
                        <span class="card-stars-dark">
                            <span class="card-stars-light" style="width: ${e.vote*10}%;"></span>
                        </span>
                    </div>
                    <span>${e.date}</span>
                </div>
                <div class="card-description">${e.comment}</div>
                <div class="card-info">${e.desc}</div>
                <div class="card-tags">${t}</div>
                
            </div>
            <div class="card-cover">
                <img src="${e.cover}" alt="${e.title}">
            </div>
            <a href="${e.link}" class="link-overlay" id="douban-link" target="_blank"></a>
        </div>`;this.ele.insertAdjacentHTML("afterend",s)}renderBook(e){let t=e.tags.map(r=>`<span class="card-tag">${r}</span>`).join(""),s=`
        <div class="douban-card" id="douban-card">
            <div class="card-content">
                <div class="card-title">${e.title}</div>
                <div class="card-meta">
                    <span class="card-rating">${e.vote}</span>
                    <div class="card-stars">
                        <span class="card-stars-dark">
                            <span class="card-stars-light" style="width: ${e.vote*10}%;"></span>
                        </span>
                    </div>
                    <span>${e.date}</span>
                </div>
                <div class="card-description">${e.comment}</div>
                <div class="card-info">${e.desc}</div>
                <div class="card-tags">${t}</div>
            </div>
            <div class="card-cover">
                <img src="${e.cover}" alt="${e.title}">
            </div>
            <a href="${e.link}" class="link-overlay" id="douban-link" target="_blank"></a>
        </div>
        `;this.ele.insertAdjacentHTML("afterend",s)}convert(e,t){return t=="movie"?{title:e.subject.title,link:e.subject.url,cover:e.subject.pic.normal,desc:e.subject.card_subtitle.split("/").map(s=>s.trim()).join("/"),star:e.subject.rating.star_count,vote:e.subject.rating.value,genres:e.subject.genres,date:e.subject.pubdate[0],director:e.subject.directors[0].name,comment:e.comment??""}:{title:e.subject.title,link:e.subject.url,cover:e.subject.pic.normal,desc:e.subject.card_subtitle.split("/").map(s=>s.trim()).join("/"),intro:e.subject.intro,star:e.subject.rating.star_count,vote:e.subject.rating.value,date:e.subject.pubdate[0],author:e.subject.author[0],comment:e.comment??"",tags:e.tags}}};window.$DoubanCard=function(c,e,t,s,r){return new a(c,e,t,s,r)};})();
