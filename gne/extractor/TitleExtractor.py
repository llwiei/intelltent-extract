import re
from gne.utils import config, get_longest_common_sub_string
from lxml.html import HtmlElement
from gne.defaults import TITLE_HTAG_XPATH, TITLE_SPLIT_CHAR_PATTERN
import numpy as np


class TitleExtractor:
    def extract_by_xpath(self, element, title_xpath):
        if title_xpath:
            title_list = element.xpath(title_xpath)
            if title_list:
                return title_list[0]
            else:
                return ''
        return ''

    def extract_by_title(self, element):
        title_list = element.xpath('//title/text()')
        if not title_list:
            return ''
        title = re.split(TITLE_SPLIT_CHAR_PATTERN, title_list[0])
        if title:
            if len(title[0]) >= 4:
                return title[0]
            return title_list[0]
        else:
            return ''

    def extract_by_htag(self, element):
        title_list = element.xpath(TITLE_HTAG_XPATH)
        if not title_list:
            return ''
        return title_list[0]

    def levenshtein_distance(self, str1, str2):
        m, n = len(str1), len(str2)
        dp = np.zeros((m + 1, n + 1))

        for i in range(m + 1):
            for j in range(n + 1):
                if i == 0:
                    dp[i][j] = j
                elif j == 0:
                    dp[i][j] = i
                elif str1[i - 1] == str2[j - 1]:
                    dp[i][j] = dp[i - 1][j - 1]
                else:
                    dp[i][j] = 1 + min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1])

        return dp[m][n]

    def strip_x(self, raw, texts):

        x = ""
        for text in texts:
            x = raw.replace(text, "")

        return x

    def extract_by_htag_and_title(self, content, element: HtmlElement) -> str:


        titlexpaths = ["//h1//text()", "//h2//text()", "//h3//text()", "//h4//text()", "//h5//text()"]
        calc_title = ""
        distance = 100000000
        for xpath_item in titlexpaths:
            title = element.xpath(xpath_item)

            if title:
                title.append(title[0])
                print(title[0])
                the_distance = self.levenshtein_distance(self.strip_x(title[0], ["\n", "\t"]), content[0][1]['text'][:500])
                print(the_distance)
                if the_distance < distance:
                    distance = the_distance
                    calc_title = title[0]

        return calc_title



    def extract(self, element: HtmlElement, content: [], title_xpath: str = '') -> str:
        title_xpath = title_xpath or config.get('title', {}).get('xpath')
        title = (self.extract_by_xpath(element, title_xpath)
                 or self.extract_by_htag_and_title(content, element)
                 or self.extract_by_title(element)
                 or self.extract_by_htag(element)
                 )
        return title.strip()
