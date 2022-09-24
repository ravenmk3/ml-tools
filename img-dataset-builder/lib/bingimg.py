import json
from typing import Optional, Tuple
from urllib.parse import urlparse

import bs4
import requests

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
}


class BingImageClient:

    def __init__(self):
        self._session = self._init_session()

    def _init_session(self):
        headers = HEADERS.copy()
        headers.update({
            'Referer': 'https://cn.bing.com/images/trending',
        })
        session = requests.session()
        session.headers = headers
        return session

    def search(self, keyword: str, page: int = 1, size: int = 35) -> dict:
        offset = (page - 1) * size
        params = {
            'q': keyword,
            'first': offset,
            'count': size,
            'cw': 1920,
            'ch': 1080,
            'mmasync': 1,
        }
        url = 'https://cn.bing.com/images/async'
        resp = self._session.get(url, params=params, timeout=(1, 3))
        resp.raise_for_status()

        doc = bs4.BeautifulSoup(resp.text, 'lxml')
        li_elms = doc.select('ul.dgControl_list > li')
        items = []
        for elm in li_elms:
            item = self._parse_li(elm)
            items.append(item)

        return {
            'keyword': keyword,
            'page': page,
            'size': size,
            'items': items
        }

    def _parse_li(self, elm: bs4.element.Tag) -> dict:
        a_elm = elm.select_one('a.iusc')
        data = json.loads(a_elm.attrs['m'])
        info_lnk = elm.select_one('a.inflnk')
        title = info_lnk.attrs['aria-label']
        return {
            'thumb_url': data['turl'],
            'image_url': data['murl'],
            'page_url': data['purl'],
            'md5': data['md5'],
            'title': title,
        }

    def get_data(self, url: str) -> bytes:
        p_url = urlparse(url)
        referer = f'{p_url.scheme}://{p_url.hostname}/'
        headers = HEADERS.copy()
        headers.update({
            'Referer': referer
        })
        resp = self._session.get(url, headers=headers, timeout=(3, 9))
        resp.raise_for_status()
        return resp.content
