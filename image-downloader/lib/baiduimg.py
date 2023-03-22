import json
import math

import requests

from lib.base import ImageClient, PageResult, ImageInfo, DataResult
from lib.common import md5_hex


HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
}


def is_valid_item(item: dict) -> bool:
    return 'thumbURL' in item and 'objURL' in item


def conv_image_info(item: dict) -> ImageInfo:
    img_url = item['objURL']
    img_id = md5_hex(img_url)
    return ImageInfo(
        id=img_id,
        original_url=img_url,
        thumb_url=item.get('thumbURL'),
        medium_url=item.get('middleURL'),
        source_url=item.get('fromURL'),
        source_host=item.get('fromURLHost'),
        source_title=item.get('fromPageTitle'),
        width=item.get('width'),
        height=item.get('height'),
    )


class BaiduImageClient(ImageClient):

    def __init__(self):
        self._session = self._init_session()

    def _init_session(self):
        headers = HEADERS.copy()
        headers.update({
            'Referer': 'https://image.baidu.com/',
        })
        session = requests.session()
        session.headers = headers
        return session

    def search(self, keyword: str, page: int = 1, page_size: int = 20) -> PageResult:
        offset = page_size * (page - 1)
        params = {
            'tn': 'baiduimage',
            'ie': 'utf-8',
            'word': keyword,
            'pn': offset
        }
        url = f'https://image.baidu.com/search/flip'
        resp = self._session.get(url=url, params=params, timeout=(3, 5))
        resp.raise_for_status()
        html = str(resp.text)

        result = PageResult(keyword=keyword, page=page, page_size=page_size, images=[])

        if '找到相关图片0张</div>' in html:
            return result

        prefix = "flip.setData('imgData', "
        suffix = "flip.setData('fcadData'"
        i_start = html.index(prefix)
        i_end = html.index(suffix)
        if i_start < 1 or i_end < 1:
            return result

        content = html[i_start + len(prefix):i_end].strip()
        content = content[:-2]
        content = content.replace("\\'", "'")
        data = json.loads(content, strict=False)

        total = int(data['displayNum'])
        page_count = math.ceil(float(total) / float(page_size))

        result.total = total
        result.page_count = page_count
        result.images = [conv_image_info(x) for x in data['data'] if is_valid_item(x)]
        return result

    def get_data(self, url: str) -> DataResult:
        resp = self._session.get(url, headers=HEADERS, timeout=(3, 5))
        resp.raise_for_status()
        hdr = resp.headers
        mime_type = hdr.get('Content-Type')
        etag = hdr.get('ETag')
        return DataResult(url=url, data=resp.content, mime_type=mime_type, etag=etag)
