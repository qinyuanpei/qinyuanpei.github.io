var firstpages = document.getElementsByClassName("hexo-douban-firstpage");
var previouspages = document.getElementsByClassName("hexo-douban-previouspage");
var nextpages = document.getElementsByClassName("hexo-douban-nextpage");
var lastpages = document.getElementsByClassName("hexo-douban-lastpage");
var pagenums = document.getElementsByClassName("hexo-douban-pagenum");

function makePageNum(num, arr) {
    return (num + 1) + ' / ' + (Math.ceil(arr.length / 10 === 0 ? 1 : Math.ceil(arr.length / 10)));
}

function firstBtn() {
    var sibs = this.parentNode.siblings();
    displayPage(sibs, 0);
    this.parentNode.getElementsByClassName('hexo-douban-pagenum')[0].innerText = makePageNum(0, sibs);
}

function previousBtn() {
    var sibs = this.parentNode.siblings();
    var currNum = this.parentNode.getElementsByClassName('hexo-douban-pagenum')[0].innerText;
    currNum = currNum.substr(0, currNum.indexOf('/') - 1);
    currNum = parseInt(currNum, 10) - 1;
    if (currNum > 0) {
        currNum--;
    }
    displayPage(sibs, currNum);
    this.parentNode.getElementsByClassName('hexo-douban-pagenum')[0].innerText = makePageNum(currNum, sibs);
}

function nextBtn() {
    var sibs = this.parentNode.siblings();
    var currNum = this.parentNode.getElementsByClassName('hexo-douban-pagenum')[0].innerText;
    currNum = currNum.substr(0, currNum.indexOf('/') - 1);
    currNum = parseInt(currNum, 10) - 1;
    if (currNum < Math.ceil(sibs.length / 10) - 1) {
        currNum++;
    }
    displayPage(sibs, currNum);
    this.parentNode.getElementsByClassName('hexo-douban-pagenum')[0].innerText = makePageNum(currNum, sibs);
}

function lastBtn() {
    var sibs = this.parentNode.siblings();
    displayPage(sibs, Math.ceil(sibs.length / 10) - 1);
    this.parentNode.getElementsByClassName('hexo-douban-pagenum')[0].innerText = makePageNum(Math.ceil(sibs.length / 10) - 1 === -1 ? 0 : Math.ceil(sibs.length / 10) - 1, sibs);
}

function displayPage(arr, num) {
    for (var i = 0; i < arr.length; i++) {
        if (Math.floor(i / 10) === num) {
            arr[i].classList.remove('hexo-douban-hide');
            if (arr[i].getElementsByTagName('img').length > 0) {
                var img = arr[i].getElementsByTagName('img')[0];
                img.src = img.getAttribute('data-src');
            }
        } else {
            arr[i].classList.add('hexo-douban-hide');
        }
    }
}

for (var i = 0; i < firstpages.length; i++) {

    //add listener
    firstpages[i].onclick = firstBtn;
    previouspages[i].onclick = previousBtn;
    nextpages[i].onclick = nextBtn;
    lastpages[i].onclick = lastBtn;

    //set page num
    var size = pagenums[i].parentNode.siblings().length;
    pagenums[i].innerText = '1 / ' + (Math.ceil(size / 10) === 0 ? 1 : Math.ceil(size / 10));
    firstpages[i].click();
}
