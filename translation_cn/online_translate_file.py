'''
首先从亚马逊上，购买需要翻译的电子书，然后用 PC 版 Kindle app[5] 打开并下载，在转化为 epub[6] 格式的电子书。
再用 Calibre[7] 电子书转化工具，将 epub 格式的电子书转化为 html 格式。
处理完原始资料，利用 Python 的 open 方法，打开 html格式的原始文件，简单处理格式后，逐行使用 requests 发送到 Deep L[8] 进行翻译。
将翻译结果收集起来，和原始内容相间排放，最后保存成 html 文件，用 VS code[9] 编辑器，进行编排和校对。

[1] 工具源码: https://github.com/xiaolai/apple-computer-literacy/tree/main/deepl-aided-semi-automatic-book-translatiion
[2] 翻译工具源码: https://github.com/xiaolai/apple-computer-literacy/blob/main/deepl-aided-semi-automatic-book-translatiion/deepl-automatic-html-translation.ipynb
[3] requests: https://docs.python-requests.org/en/latest/
[4] 正则表达式: https://www.runoob.com/python/python-reg-expressions.html
[5] Kindle app: https://www.amazon.cn/gp/browse.html%3Fnode=2331640071&ref=kcp_fd_hz
[6] epub: https://zh.wikipedia.org/wiki/EPUB
[7] Calibre: https://calibre-ebook.com/
[8] Deep L: https://www.deepl.com/zh/translator
[9] VS code: https://code.visualstudio.com/
[10] 黑客与画家: https://book.douban.com/subject/6021440/
[11] 保罗·格雷厄姆 (Paul Graham): https://zh.wikipedia.org/wiki/%E4%BF%9D%E7%BD%97%C2%B7%E6%A0%BC%E9%9B%B7%E5%8E%84%E5%A7%86
[12] Paul-Graham 文集: https://github.com/evmn/Paul-Graham
[13] 电子书源码: https://github.com/evmn/Paul-Graham/blob/master/calibre.recipe
'''
