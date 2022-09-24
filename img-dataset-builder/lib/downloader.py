import logging
import os
from typing import List, Optional
from urllib.parse import urlparse

from requests import ConnectTimeout

from lib import LIB_PATH, utils
from lib.bingimg import BingImageClient
from lib.utils import http_retry, read_lines


class BadHostManager:

    def __init__(self, data_dir: str = '.data'):
        self._data_dir = data_dir
        self._bad_hosts = self._load_data()
        self._white_list = ['cn.bing.com', 'bing.com']

    def _load_data(self) -> set:
        file_path = os.path.join(LIB_PATH, 'bad_hosts.txt')
        lines = read_lines(file_path)
        hosts = set(lines)
        file_path = os.path.join(self._data_dir, 'bad_hosts.txt')
        if os.path.isfile(file_path):
            lines = read_lines(file_path)
            hosts.update(lines)
        return hosts

    def contains(self, host: str) -> bool:
        if host in self._white_list:
            return False
        return host in self._bad_hosts

    def add(self, host: str):
        if host in self._white_list:
            return
        self._bad_hosts.add(host)

    def save(self):
        file_path = os.path.join(self._data_dir, 'bad_hosts.txt')
        utils.write_lines(file_path, list(self._bad_hosts))


class ImageDownloader:

    def __init__(self, data_dir: str = '.data', keywords: List[str] = None, num_per_kw: int = 100):
        self.client = BingImageClient()
        self.data_dir = data_dir
        self.keywords = keywords or []
        self.num_per_kw = num_per_kw
        self.bad_hosts = BadHostManager(data_dir=data_dir)
        self.downloaded_md5 = set()

    @http_retry()
    def fetch_list(self, keyword: str, page: int) -> dict:
        return self.client.search(keyword, page)

    @http_retry(5)
    def get_file_data(self, url: str) -> Optional[bytes]:
        try:
            return self.client.get_data(url)
        except ConnectTimeout as e:
            host = urlparse(url).hostname
            self.bad_hosts.add(host)
            self.bad_hosts.save()
            logging.info('add bad host: %s', host)
            logging.error(e, exc_info=True)
            return None

    def download_file(self, url: str, file_path: str) -> bool:
        if os.path.isfile(file_path):
            return True
        host = urlparse(url).hostname
        if self.bad_hosts.contains(host):
            logging.info('skip bad host: %s', url)
            return False
        data = self.get_file_data(url)
        if data is None:
            return False
        with open(file_path, 'wb+') as file:
            file.write(data)
        return True

    def download(self, keyword: str):
        kw_dir = os.path.join(self.data_dir, 'images', keyword)
        os.makedirs(kw_dir, exist_ok=True)
        page_num = 1
        count = 0

        while page_num < 100 and count < self.num_per_kw:
            resp = self.fetch_list(keyword, page_num)
            if resp is None:
                break

            page_num += 1
            items = resp['items']

            for item in items:
                md5 = item['md5']
                if md5 in self.downloaded_md5:
                    logging.info('skip md5: %s', md5)
                    continue

                img_url = item['image_url']
                thumb_url = item['thumb_url']
                file_name = f'{md5}.jpg'
                file_path = os.path.join(kw_dir, file_name)
                if self.download_file(img_url, file_path) or self.download_file(thumb_url, file_path):
                    self.downloaded_md5.add(md5)
                    count += 1
                    logging.info('downloaded: %s (%d/%d)', keyword, count, self.num_per_kw)
                if count >= self.num_per_kw:
                    break

    def run(self):
        for keyword in self.keywords:
            self.download(keyword)
