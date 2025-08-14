import logging
import re
from urllib.parse import urljoin
import datetime

import lxml.sax
from lxml import etree
import requests




def convert_time_format(before_time_style, before_convert_time, convert_style):
    middle_time = datetime.datetime.strptime(before_convert_time, before_time_style)
    return middle_time.strftime(convert_style)


def generate_words_rex(p):
    key_words = []
    with open(p) as f:
        for key_word in f.xreadlines():
            key_words.append(key_word)
    return ".*?(%s).*" % "|".join(key_words)


def words_in(string, rex):
    match = re.compile(rex)
    res = match.match(string)
    if res and res.group(1):
        return True
    return False


def join_url(origin_url, data):
    try:

        data = urljoin(origin_url, data)
    except Exception as error:
        logging.error(error)
    finally:
        return data





class TextElementTreeContentHandler(lxml.sax.ElementTreeContentHandler, object):
    BLOCK_LABEL = ('p', 'div', 'br', 'hr', 'h1', 'h2', 'form', 'table', 'ul',
                   'address', 'blockquote', 'dd', 'dl', 'fieldset', 'noscript',
                   'hr', 'h3', 'h4', 'h5', 'h6', 'ol', 'pre', 'tfoot')

    PASS_LABEL = ('script', 'style',"time")



    def __init__(self, origin_url, remove_img={}, proxy=None):
        super(TextElementTreeContentHandler, self).__init__()
        self.origin_url = origin_url
        self.text = ''
        self.pass_flag = False

        self.images = []

        self.img_num = 0
        self.remove_img = remove_img

        self.proxy = proxy



    def check_img(self,resource_url, proxy=None):
        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'cache-control': 'no-cache',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
            'Referer': self.origin_url
        }
        if proxy:
            proxies = {
                "http": proxy,
                "https": proxy,
            }
        else:
            proxies = None

        with requests.get(resource_url, stream=True, allow_redirects=True, timeout=5, headers=headers,
                          proxies=proxies) as response:
            response.raise_for_status()
            content_length = response.headers.get('Content-Length')
            if content_length:
                file_size = int(content_length)
                min_attachments_size = 20 * 1024  # 20KB
                if file_size < min_attachments_size:
                    logging.info(f"附件大小: {file_size} 可能不是附件: {resource_url}")
                    return False
                return True


    def startElementNS(self, ns_name, qname, attributes=None):
        super(TextElementTreeContentHandler, self).startElementNS(ns_name, qname, attributes=None)
        if qname in TextElementTreeContentHandler.BLOCK_LABEL and self.text and not self.text.endswith('\n'):
            self.text += '\n'
        if qname in TextElementTreeContentHandler.PASS_LABEL:
            self.pass_flag = True
        if qname == 'img' and attributes:
            try:
                iters = attributes.iteritems()
            except:
                iters = attributes.items()
            for key, value in iters:

                print("value" + value)


                if key[1].lower() == 'src':
                    if self.text and not self.text.endswith('\n'):
                        self.text += '\n'
                    img_url = join_url(self.origin_url, value)

                    print("img_url", img_url)


                    if not self.check_img(img_url, proxy=self.proxy):
                        print(f"该图片不符合大小：{img_url}")
                        continue

                    #self.text += '<img src="%s"/>\n' % img_url
                    placeholder = f"[img:{self.img_num}]"
                    self.img_num += 1





                    if placeholder in self.remove_img:
                        continue

                    self.text += f"{placeholder}\n"

                    img_dict =  {
                                "placeholder": placeholder,
                                "resource_link": img_url,
                                "resource_minio_path": "",
                                "status": 0
                                }

                    self.images.append(img_dict)
                    break

    def endElementNS(self, ns_name, qname):
        if qname in TextElementTreeContentHandler.BLOCK_LABEL and not self.text.endswith('\n'):
            self.text += '\n'
        if qname in TextElementTreeContentHandler.PASS_LABEL:
            self.pass_flag = False

    def characters(self, data):
        if data.strip() and not self.pass_flag:
            self.text += data


def extract(xpath,raw_html, url_rex="", remove_img={}, proxy=None):
    html_node = etree.HTML(raw_html)
    res = []
    nodes = html_node.xpath(xpath)

    img = []

    for node in nodes:
        # 用 HTMLParser 解析文本
        handler = TextElementTreeContentHandler(url_rex, remove_img,proxy)
        lxml.sax.saxify(node, handler)
        res.append(handler.text)
        img.extend(handler.images)

    return {
        "content": "".join(res),
        "img": img
    }


def extract_node(nodes, url_rex="", remove_img={}, proxy=None):
    res = []
    img = []

    handler = TextElementTreeContentHandler(url_rex, remove_img,proxy)
    lxml.sax.saxify(nodes, handler)
    res.append(handler.text)
    img.extend(handler.images)

    return {
        "content": "".join(res),
        "img": img
    }





if __name__ == '__main__':
    with open('../1111.html', 'r', encoding="utf-8") as f:
        html = f.read()


        xpath = '''//article'''
        print(extract(xpath,html,remove_img={}))



