// 一言 API
async function getHitokoto() {
    try {
        const response = await fetch('https://v1.hitokoto.cn');
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('一言获取失败：', error);
        return null;
    }
}

// 更新一言内容
async function updateHitokoto() {
    const textElement = document.querySelector('#main-banner .subtitle .text');
    if (!textElement) return;

    const defaultText = textElement.textContent.trim();
    const result = await getHitokoto();
    
    if (result && result.hitokoto) {
        // 添加淡出效果
        textElement.style.opacity = '0';
        
        setTimeout(() => {
            textElement.textContent = result.hitokoto;
            // 添加淡入效果
            textElement.style.opacity = '0.8';
        }, 300);
    }
}

// 滚动到内容区域
function scrollToContent() {
    const banner = document.getElementById('main-banner');
    if (!banner) return;
    
    window.scrollTo({
        top: banner.offsetHeight,
        behavior: 'smooth'
    });
}

// 初始化
document.addEventListener('DOMContentLoaded', function() {
    // 延迟加载一言
    setTimeout(updateHitokoto, 2000);

    // 绑定向上箭头点击事件
    const upIcon = document.querySelector('#main-banner .icon-up');
    if (upIcon) {
        upIcon.addEventListener('click', scrollToContent);
    }
}); 