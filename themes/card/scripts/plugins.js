//const { version, name } = require('../package.json');
var fs = require('fs');
var version = 'master'
fs.readFile('./BUILD_NUMBER.txt', function (error, data) {
    if (error) {
      console.log('load BUILD_NUMBER.txt fails, ' + error)
    } else {
        //version = data.toString().trim();
        console.log(`load version ${version} from BUILD_NUMBER.txt...`);
    }
});

hexo.extend.helper.register('theme_version', () => version)

const source = (path, cache, ext) => {
    if (cache) {
        const minFile = `${path}${ext === '.js' ? '.min' : ''}${ext}`;
        const jsdelivrCDN = hexo.config.jsdelivr;
        return jsdelivrCDN.enable ? `//${jsdelivrCDN.baseUrl}/gh/${jsdelivrCDN.gh_user}/${jsdelivrCDN.gh_repo}@${version}/${minFile}` : `${minFile}?v=${version}`
    } else {
        return path + ext
    }
}
hexo.extend.helper.register('theme_js', (path, cache) => source(path, cache, '.js'))
hexo.extend.helper.register('theme_css', (path, cache) => source(path, cache, '.css'))

function renderImage(src, alt = '', title = '') {
    return `<figure class="image-bubble">
                <div class="img-lightbox">
                    <div class="overlay"></div>
                    <img src="${src}" alt="${alt}" title="${title}" referrerpolicy="no-referrer">
                </div>
                <div class="image-caption">${title || alt}</div>
            </figure>`
}

hexo.extend.tag.register('image', ([src, alt = '', title = '']) => {
    return hexo.theme.config.lightbox ? renderImage(src, alt, title) : `<img src="${src}" alt="${alt}" title="${title}">`
})

hexo.extend.filter.register('before_post_render', data => {
    if (hexo.theme.config.lightbox) {
        // 包含图片的代码块 <escape>[\s\S]*\!\[(.*)\]\((.+)\)[\s\S]*<\/escape>
        // 行内图片 [^`]\s*\!\[(.*)\]\((.+)\)([^`]|$)
        data.content = data.content.replace(/<escape>.*\!\[(.*)\]\((.+)\).*<\/escape>|([^`]\s*|^)\!\[(.*)\]\((.+)\)([^`]|$)/gm, match => {

            // 忽略代码块中的图片
            if (/<escape>[\s\S]*<\/escape>|.?\s{3,}/.test(match)) {
                return match
            }

            return match.replace(/\!\[(.*)\]\((.+)\)/, (img, alt, src) => {
                const attrs = src.split(' ')
                const title = (attrs[1] && attrs[1].replace(/\"|\'/g, '')) || ''
                return `{% image ${attrs[0]} '${alt}' '${title}' %}`
            })
        })
    }
    return data
})
