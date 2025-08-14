from .exceptions import NoContentException
from .utils import pre_parse, remove_noise_node, config, html2element, normalize_text, fix_html
from gne.extractor import ContentExtractor, TitleExtractor, TimeExtractor, AuthorExtractor, ListExtractor, MetaExtractor
import re
__version__ = "0.3.1"
__author__ = "liwei"

from .common_utils import extract, extract_node

class GeneralNewsExtractor:
    def extract(self,
                html,
                title_xpath='',
                author_xpath='',
                publish_time_xpath='',
                host='',
                body_xpath='',
                normalize=False,
                noise_node_list=None,
                with_body_html=False,
                use_visiable_info=False):

        # 对 HTML 进行预处理可能会破坏 HTML 原有的结构，导致根据原始 HTML 编写的 XPath 不可用
        # 因此，如果指定了 title_xpath/author_xpath/publish_time_xpath，那么需要先提取再进行
        # 预处理
        html = fix_html(html)
        if normalize:
            normal_html = normalize_text(html)
        else:
            normal_html = html
        element = html2element(normal_html)
        meta_content = MetaExtractor().extract(element)
        publish_time = meta_content.get("article:published_time", TimeExtractor().extractor(element, publish_time_xpath=publish_time_xpath))
        author = meta_content.get("article:author",AuthorExtractor().extractor(element, author_xpath=author_xpath))
        element = pre_parse(element)
        remove_noise_node(element, noise_node_list)
        content = ContentExtractor().extract(element,
                                             host=host,
                                             with_body_html=with_body_html,
                                             body_xpath=body_xpath,
                                             use_visiable_info=use_visiable_info)


        title = meta_content.get("og:title", TitleExtractor().extract(element, content,title_xpath=title_xpath)).split("-")[0]

        site_name = meta_content.get("og:site_name", "")

        if not content:
            raise NoContentException('无法提取正文！')

        resp = extract_node(nodes=content[0][1]['node'],url_rex=host)



        # ccc = content[0][1]['node'].xpath("string(.)").strip()
        #
        # clea_text = re.sub(' +', ' ', ccc, flags=re.S)
        # cla_text = re.sub('\n\s+|\s+\n+|\n{2,}|\s{2,}', '\n', clea_text, flags=re.S)

        cla_text = resp["content"]

        print(cla_text)


        if meta_content.get("og:image", None):

            content[0][1]['images'].append(meta_content.get("og:image"))

        result = {'title': title,
                  'author': author,
                  'publish_time': publish_time,
                  #'content': content[0][1]['text'],
                  'content': cla_text,
                  #'images': content[0][1]['images'],
                  "images": resp["img"],

                  'meta': meta_content,
                  "site_name": site_name
                  }
        print(result)
        if with_body_html or config.get('with_body_html', False):
            result['body_html'] = content[0][1]['body_html']
        return result


class ListPageExtractor:
    def extract(self, html, feature):
        normalize_html = normalize_text(html)
        element = html2element(normalize_html)
        extractor = ListExtractor()
        return extractor.extract(element, feature)

