!function(l,r){function o(){}function c(t){var e,i=t.offsetLeft,n=t.offsetTop;return t.offsetParent&&(i+=(e=arguments.callee(t.offsetParent)).x,n+=e.y),{x:i,y:n}}function n(){return r.documentElement.scrollTop||r.body.scrollTop}var t,d=r.body,h=r.querySelector.bind(r),s=r.querySelectorAll.bind(r),a=h("html"),e=h("#gotop"),u=h("#menu"),f=h("#header"),m=h("#mask"),g=h("#menu-toggle"),v=h("#menu-off"),L=h("#loading"),p=l.requestAnimationFrame,w=Array.prototype.forEach,y="ontouchstart"in l&&/Mobile|Android|iOS|iPhone|iPad|iPod|Windows Phone|KFAPWI/i.test(navigator.userAgent)?"touchstart":"click",$=/micromessenger/i.test(navigator.userAgent),x={goTop:function(t){var e=n(),i=2<arguments.length?arguments[1]:Math.abs(e-t)/12;e&&t<e?(l.scrollTo(0,Math.max(e-i,0)),p(arguments.callee.bind(this,t,i))):t&&e<t?(l.scrollTo(0,Math.min(e+i,t)),p(arguments.callee.bind(this,t,i))):this.toc.actived(t)},toggleGotop:function(t){t>l.innerHeight/2?e.classList.add("in"):e.classList.remove("in")},toggleMenu:function(t){var e,i=h("#main");t?(u.classList.remove("hide"),l.innerWidth<1241&&(m.classList.add("in"),u.classList.add("show"),$?(e=n(),i.classList.add("lock"),i.scrollTop=e):a.classList.add("lock"))):(u.classList.remove("show"),m.classList.remove("in"),$?(e=i.scrollTop,i.classList.remove("lock"),l.scrollTo(0,e)):a.classList.remove("lock"))},fixedHeader:function(t){t>f.clientHeight?f.classList.add("fixed"):f.classList.remove("fixed")},toc:function(){var e=h("#post-toc");if(!e||!e.children.length)return{fixed:o,actived:o};var n=h(".post-header").clientHeight,s=f.clientHeight,a=h("#post-content").querySelectorAll("h1, h2, h3, h4, h5, h6");return e.querySelector('a[href="#'+a[0].id+'"]').parentNode.classList.add("active"),{fixed:function(t){n-s<=t?e.classList.add("fixed"):e.classList.remove("fixed")},actived:function(t){for(i=0,len=a.length;i<len;i++)t>c(a[i]).y-s-5&&(e.querySelector("li.active").classList.remove("active"),e.querySelector('a[href="#'+a[i].id+'"]').parentNode.classList.add("active"));t<c(a[0]).y&&(e.querySelector("li.active").classList.remove("active"),e.querySelector('a[href="#'+a[0].id+'"]').parentNode.classList.add("active"))}}}(),hideOnMask:[],modal:function(t){this.$modal=h(t),this.$off=this.$modal.querySelector(".close");var e=this;this.show=function(){m.classList.add("in"),e.$modal.classList.add("ready"),setTimeout(function(){e.$modal.classList.add("in")},0)},this.onHide=o,this.hide=function(){e.onHide(),m.classList.remove("in"),e.$modal.classList.remove("in"),setTimeout(function(){e.$modal.classList.remove("ready")},300)},this.toggle=function(){return e.$modal.classList.contains("in")?e.hide():e.show()},x.hideOnMask.push(this.hide),this.$off&&this.$off.addEventListener(y,this.hide)},share:function(){var e=h("#pageShare"),i=h("#shareFab"),t=new this.modal("#globalShare"),n=(h("#menuShare").addEventListener(y,t.toggle),i&&(i.addEventListener(y,function(){e.classList.toggle("in")},!1),r.addEventListener(y,function(t){i.contains(t.target)||e.classList.remove("in")},!1)),new this.modal("#wxShare"));n.onHide=t.hide,w.call(s(".wxFab"),function(t){t.addEventListener(y,n.toggle)})},search:function(){var t=h("#search-wrap");h("#search").addEventListener(y,function(){t.classList.toggle("in")})},reward:function(){var t=new this.modal("#reward"),t=(h("#rewardBtn").addEventListener(y,t.toggle),h("#rewardToggle")),e=h("#rewardCode");t&&t.addEventListener("change",function(){e.src=this.checked?this.dataset.alipay:this.dataset.wechat})},waterfall:function(){l.innerWidth<760||w.call(s(".waterfall"),function(t){var e=t.querySelectorAll(".waterfall-item"),i=[0,0];w.call(e,function(t){var e=i[0]<=i[1]?0:1;t.style.cssText="top:"+i[e]+"px;left:"+(0<e?"50%":0),i[e]+=t.offsetHeight}),t.style.height=Math.max(i[0],i[1])+"px",t.classList.add("in")})},tabBar:function(t){t.parentNode.parentNode.classList.toggle("expand")},page:(t=s(".fade, .fade-scale"),{loaded:function(){w.call(t,function(t){t.classList.add("in")}),0},unload:function(){w.call(t,function(t){t.classList.remove("in")}),0},visible:!1}),lightbox:void w.call(s(".img-lightbox"),function(t){new E(t)}),loadScript:function(t){t.forEach(function(t){var e=r.createElement("script");e.src=t,e.async=!0,d.appendChild(e)})},dialog:function(t,e,i,n){var s=new this.modal("#dialog");h(".mdui-dialog-title").innerText=t,h(".mdui-dialog-content").innerText=e,i&&h("#btnOK").addEventListener("click",i),n&&h("#btnCancel").addEventListener("click",function(){n(),s.hide()})}};function E(t){this.$img=t.querySelector("img"),this.$overlay=t.querySelector("overlay"),this.margin=40,this.title=this.$img.title||this.$img.alt||"",this.isZoom=!1,this.calcRect=function(){o=d.clientWidth;var t=(c=d.clientHeight)-2*this.margin,e=n,i=s,t=(this.margin,Math.min(o<e?o/e:1,t<i?t/i:1));return{w:e*=t,h:i*=t,t:(c-i)/2-a.top,l:(o-e)/2-a.left+this.$img.offsetLeft}},this.setImgRect=function(t){this.$img.style.cssText="width: "+t.w+"px; max-width: "+t.w+"px; height:"+t.h+"px; top: "+t.t+"px; left: "+t.l+"px"},this.setFrom=function(){this.setImgRect({w:a.width,h:a.height,t:0,l:(t.offsetWidth-a.width)/2})},this.setTo=function(){this.setImgRect(this.calcRect())},this.addTitle=function(){this.title&&(this.$caption=r.createElement("div"),this.$caption.innerHTML=this.title,this.$caption.className="overlay-title",t.appendChild(this.$caption))},this.removeTitle=function(){this.$caption&&t.removeChild(this.$caption)};var n,s,a,o,c,e=this;this.zoomIn=function(){n=this.$img.naturalWidth||this.$img.width,s=this.$img.naturalHeight||this.$img.height,a=this.$img.getBoundingClientRect(),t.style.height=a.height+"px",t.classList.add("ready"),this.setFrom(),this.addTitle(),this.$img.classList.add("zoom-in"),setTimeout(function(){t.classList.add("active"),e.setTo(),e.isZoom=!0},0)},this.zoomOut=function(){this.isZoom=!1,t.classList.remove("active"),this.$img.classList.add("zoom-in"),this.setFrom(),setTimeout(function(){e.$img.classList.remove("zoom-in"),e.$img.style.cssText="",e.removeTitle(),t.classList.remove("ready"),t.removeAttribute("style")},300)},t.addEventListener("click",function(t){e.isZoom?e.zoomOut():"IMG"===t.target.tagName&&e.zoomIn()}),r.addEventListener("scroll",function(){e.isZoom&&e.zoomOut()}),l.addEventListener("resize",function(){e.isZoom&&e.zoomOut()})}l.addEventListener("load",function(){L.classList.remove("active"),x.page.loaded(),l.lazyScripts&&l.lazyScripts.length&&x.loadScript(l.lazyScripts)}),l.addEventListener("DOMContentLoaded",function(){x.waterfall();var t=n();x.toc.fixed(t),x.toc.actived(t),x.page.loaded()});var T=!1,b=h('a[href^="mailto"]');b&&b.addEventListener(y,function(){T=!0}),l.addEventListener("beforeunload",function(t){T?T=!1:x.page.unload()}),l.addEventListener("pageshow",function(){x.page.visible||x.page.loaded()}),l.addEventListener("resize",function(){l.BLOG.even=y="ontouchstart"in l?"touchstart":"click",x.toggleMenu(),x.waterfall()}),e.addEventListener(y,function(){p(x.goTop.bind(x,0))},!1),g.addEventListener(y,function(t){x.toggleMenu(!0),t.preventDefault()},!1),v.addEventListener(y,function(){u.classList.add("hide")},!1),m.addEventListener(y,function(t){x.toggleMenu(),x.hideOnMask.forEach(function(t){t()}),t.preventDefault()},!1),r.addEventListener("scroll",function(){var t=n();x.toggleGotop(t),x.fixedHeader(t),x.toc.fixed(t),x.toc.actived(t)},!1),l.BLOG.SHARE&&x.share(),l.BLOG.REWARD&&x.reward(),x.noop=o,x.even=y,x.$=h,x.$$=s,Object.keys(x).reduce(function(t,e){return t[e]=x[e],t},l.BLOG),l.Waves?(Waves.init(),Waves.attach(".global-share li",["waves-block"]),Waves.attach(".article-tag-list-link, #page-nav a, #page-nav span",["waves-button"])):console.error("Waves loading failed.")}(window,document);