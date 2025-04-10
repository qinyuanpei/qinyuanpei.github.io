(()=>{function p(s,r){var a=document.getElementById(s),r=JSON.parse(a.getAttribute("data-chart")),n=echarts.init(a,c()),i={title:{text:"\u6587\u7AE0\u7EDF\u8BA1",x:"center"},tooltip:{trigger:"axis",formatter(e){var o=e[0].name+"\u5E74";let l=`<span style="display:inline-block;margin-right:5px;border-radius:10px;width:10px;height:10px;background-color:${e[0].color};"></span>`;return o+=`<br/>${l} ${e[0].seriesName}: ${e[0].value}\u7BC7`,o}},xAxis:{data:Object.keys(r)},yAxis:{type:"value",name:"\u6570\u91CF",min:0,max:55,interval:10},series:[{name:"\u6570\u91CF",type:"bar",data:Object.values(r)},{name:"\u6570\u91CF",type:"line",smooth:!0,data:Object.values(r)}]};n.setOption(i),window.addEventListener("resize",()=>{n.resize()})}function g(s,r){var a=document.getElementById(s),r=JSON.parse(a.getAttribute("data-chart")),n=echarts.init(a,c());n.on("click",function(t){typeof t.seriesIndex>"u"||t.type=="click"&&(location.href="/categories/"+encodeURI(t.data.name))});var i=[];for(var e in r)i.push({name:e,value:r[e]});var o={title:{text:"\u5206\u7C7B\u7EDF\u8BA1",x:"center"},tooltip:{trigger:"item",formatter:"{a} <br/>{b} : {c} \u7BC7({d}%)"},series:[{name:"\u5206\u7C7B",type:"pie",radius:"50%",center:["50%","50%"],data:i,roseType:"area",itemStyle:{emphasis:{shadowBlur:10,shadowOffsetX:0,shadowColor:"rgba(0, 0, 0, 0.5)"}}}]};n.setOption(o),window.addEventListener("resize",()=>{n.resize()})}function v(s){var d=document.getElementById(s),a=JSON.parse(d.getAttribute("data-chart")),r=echarts.init(d,c());r.on("click",function(o){typeof o.seriesIndex>"u"||o.type=="click"&&(location.href="/tags/"+encodeURI(o.data.name.toLowerCase()))});var n=[];for(var i in a)n.push({name:i,value:a[i]});var e={title:{text:"\u6807\u7B7E\u7EDF\u8BA1",x:"center"},series:[{type:"wordCloud",sizeRange:[10,100],rotationRange:[-90,90],rotationStep:45,gridSize:2,shape:"circle",image:"data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAABAklEQVQ4T63TLyyFURjH8c8trs0UicDMNFMIBF3RkJhNoOmKzSapJgkKzZ8k0BWBQjQbAkUym5vYs513e++7l3fX9dvOTjjP893v+XNq2lStzXxFQC82MIOBAvwJZ9jCa/aWB/TjCn0Vrl4wgeeIywMOsIgLzOO9AOrGEaYRsUsZ4BydmEQHBhF2yxRlPeIzuW2Egx3MJetv2K0oYQ09iFKOAzCCa9RbnEgD4wFYT2cZC5itAJ3iEPvYDsBmShpNTb3H0A+QBwzjC7c4CcAK9nCDD0wVppNnReIlujCG1QBE56Oev6ie7UGQy5arDNoUmwHu0jTijl78pqbYf/9MLffhG9gELuqHjsg6AAAAAElFTkSuQmCC",drawOutOfBound:!1,textStyle:{color:function(){return"rgb("+[Math.round(Math.random()*160),Math.round(Math.random()*160),Math.round(Math.random()*160)].join(",")+")"}},emphasis:{textStyle:{shadowBlur:10,shadowColor:"#333",color:"#409EFF"}},data:n.sort(function(o,t){return t.value-o.value})}]};r.setOption(e),window.addEventListener("resize",()=>{r.resize()})}function y(s){var d=document.getElementById(s),a=JSON.parse(d.getAttribute("data-chart")),r=echarts.init(d,c()),n=Object.keys(a).map(function(t){return a[t]}).reduce(function(t,l,u,m){return t+l}),i=[],e=[];for(let t of Object.keys(a)){e.push({text:t,max:100});var o=Math.round((a[t]/n+.32).toFixed(2)*100);i.push(o)}option={title:{text:"\u8BED\u8A00\u7EDF\u8BA1",x:"center"},tooltip:{trigger:"axis"},radar:[{indicator:e,radius:80,center:["50%","60%"]}],series:[{type:"radar",tooltip:{trigger:"item"},areaStyle:{},data:[{value:i,name:"\u8BED\u8A00\u4F7F\u7528(%)"}]}]},r.setOption(option),window.addEventListener("resize",()=>{r.resize()})}function f(s){var d=document.getElementById(s),a=JSON.parse(d.getAttribute("data-chart")),r=echarts.init(d,c()),n=[];n.push({name:"\u5B66\u4E60\u65F6\u957F",type:"line",smooth:!0,data:a.map(i=>i.words.used_time+i.listen.used_time+i.speak.used_time+i.read.used_time)}),option={title:{text:"\u6247\u8D1D\u6253\u5361",x:"center"},tooltip:{trigger:"axis"},xAxis:{type:"category",boundaryGap:!1,data:a.map(i=>{let e=new Date(i.checkin_date),o=e.getMonth()+1,t=o<10?`0${o}`:o.toString(),l=e.getDate(),u=l<10?`0${l}`:l.toString();return`${t}-${u}`})},yAxis:[{type:"value",name:"\u65F6\u95F4",min:0,max:25,interval:5}],series:n},r.setOption(option),window.addEventListener("resize",()=>{r.resize()})}function x(s){var d=document.getElementById(s),a=JSON.parse(d.getAttribute("data-chart")),r=echarts.init(d,c()),n=[];for(let e=0;e<a.books.length;e++)n.push(Number(a.books[e])+Number(a.movies[e]));var i={title:{text:"\u4E66\u5F71\u97F3\u7EDF\u8BA1",x:"center"},tooltip:{trigger:"axis",axisPointer:{type:"cross",crossStyle:{color:"#999"}},formatter(e){for(var o=e[0].name+"\u6708",t=0,l=e.length;t<l;t++){let m=`<span style="display:inline-block;margin-right:5px;border-radius:10px;width:10px;height:10px;background-color:${e[t].color};"></span>`,h="\u4E2A";e[t].seriesName=="\u8BFB\u4E66"?h="\u672C":e[t].seriesName=="\u89C2\u5F71"&&(h="\u90E8"),o+=`<br/>${m} ${e[t].seriesName}: ${e[t].value}${h}`}return o}},xAxis:[{type:"category",data:["1","2","3","4","5","6","7","8","9","10","11","12"],axisLabel:{formatter:"{value}\u6708"},axisPointer:{type:"shadow"}}],yAxis:[{type:"value",name:"\u6570\u91CF",min:0,max:20,interval:5,axisLabel:{formatter:"{value}"}}],series:[{name:"\u8BFB\u4E66",type:"bar",tooltip:{valueFormatter:function(e){return e+" \u672C"}},data:a.books},{name:"\u89C2\u5F71",type:"bar",tooltip:{valueFormatter:function(e){return e+" \u90E8"}},data:a.movies},{name:"\u5408\u8BA1",type:"line",smooth:!0,tooltip:{valueFormatter:function(e){return e+" \u4E2A"}},data:n}]};r.setOption(i),window.addEventListener("resize",()=>{r.resize()})}function c(){return localStorage.getItem("theme")||"light"}window.$Statics={handleYearlyChart:p,handleCategoryChart:g,handleTagsChart:v,handleLanguagesChart:y,handleDoubanChart:x,handleShanbayChart:f};window.addEventListener("storage",function(s){s.key==="theme"&&console.log("myKey value changed to:",s.newValue)});})();
