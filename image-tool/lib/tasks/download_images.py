import logging
import os
from urllib.parse import urlparse

import requests

from lib.process.core import Saver, WorkItem, InputObject, MultiThreadProcessor, Loader
from lib.process.scanner import UrlListFileScanner


HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
}


class Downloader():

    def __init__(self, max_attempts: int = 10):
        self.max_attempts = max_attempts
        self.session = self.init_session()

    def init_session(self):
        session = requests.session()
        session.headers = HEADERS.copy()
        return session

    def try_download_data(self, url: str) -> bytes | None:
        for i in range(self.max_attempts):
            resp = self.session.get(url, timeout=(5, 10))
            if resp.ok:
                return resp.content
            code = resp.status_code
            if code >= 400 and code < 500:
                return None
        return None


def url_to_filename(url: str) -> str:
    u = urlparse(url)
    host = u.netloc.replace(':', '_')
    path = u.path.replace('/', '_')
    return f'{host}_{path}'


class TaskLoader(Loader):

    def __init__(self, save_dir: str):
        self.save_dir = save_dir

    def load(self, url: str) -> tuple[bool, str]:
        basename = url_to_filename(url)
        fullpath = os.path.join(self.save_dir, basename)
        exists = os.path.exists(fullpath)
        if exists:
            size = os.path.getsize(fullpath)
            exists = exists and size > 0
        return exists, url


class DownloadProcessor():

    def __init__(self):
        self.downloader = Downloader()

    def __call__(self, input: InputObject):
        exists, url = input.content
        if exists:
            return None
        return self.downloader.try_download_data(url)


class TargetSaver(Saver):

    def __init__(self, save_dir: str):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.save_dir = save_dir
        self.num_failed = 0
        os.makedirs(save_dir, exist_ok=True)

    def save(self, item: WorkItem):
        exists, url = item.input.content
        if exists:
            return
        data = item.output
        if data is None or len(data) < 1:
            self.num_failed += 1
            return

        basename = url_to_filename(url)
        dst_path = os.path.join(self.save_dir, basename)
        with open(dst_path, 'wb+') as fp:
            fp.write(data)


def run_download_images(url_file: str, save_dir: str, shuffle: bool = False, num_workers: int = 10):
    scanner = UrlListFileScanner(url_file, shuffle)
    loader = TaskLoader(save_dir)
    saver = TargetSaver(save_dir)
    processor = DownloadProcessor()
    runner = MultiThreadProcessor(scanner, loader, processor, saver, num_workers)
    runner.run()
