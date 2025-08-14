from gne import GeneralNewsExtractor

extractor = GeneralNewsExtractor()
import json
with open('news.txt.html', 'r', encoding='utf-8') as f:

    result = extractor.extract(f.read(),normalize=False, host="https://k.sina.com.cn/article_7732457677_1cce3f0cd01901f90i.html?from=news&subch=onews")
    print(json.dumps(result, ensure_ascii=False))
