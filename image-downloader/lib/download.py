import logging
import os

from requests import HTTPError

from lib.base import ImageClient, PageResult, DataResult
from lib.common import DuplicateDetector


class ImageDownloader:

    def __init__(self, client: ImageClient, logger: logging.Logger = None):
        self.client = client
        self.logger = logger or logging.getLogger(self.__class__.__name__)
        self.search_attempts = 10
        self.download_attempts = 10

    def _search(self, keyword: str, page: int = 1) -> PageResult | None:
        for i in range(self.search_attempts):
            try:
                return self.client.search(keyword, page)
            except HTTPError as e:
                self.logger.error(e, exc_info=True)
                code = e.response.status_code
                if code == 404:
                    return None
            except Exception as e:
                self.logger.error(e, exc_info=True)
        return None

    def _get_data(self, url: str) -> DataResult | None:
        for i in range(self.download_attempts):
            try:
                return self.client.get_data(url)
            except HTTPError as e:
                self.logger.error(e, exc_info=True)
                code = e.response.status_code
                if code == 404:
                    return None
            except Exception as e:
                self.logger.error(e, exc_info=True)
        return None

    def run(self, keyword: str, output_dir: str, name_prefix: str = '', limit: int = 1000):
        os.makedirs(output_dir, exist_ok=True)
        dl_count = 0
        page = 0
        det = DuplicateDetector()

        while dl_count < limit:
            page += 1
            resp = self._search(keyword, page)
            if not resp:
                continue
            items = resp.images
            if not items:
                break
            if det.detect(resp.dict()['images']):
                self.logger.error('duplicate detected, break loop')
                break

            for item in items:
                if dl_count >= limit:
                    break
                name = name_prefix + item.id
                filename = os.path.join(output_dir, name + '.jpg')
                if os.path.exists(filename):
                    self.logger.info('[page:%d] file exists, skip: %s', page, filename)
                    continue
                data = self._get_data(item.thumb_url)
                if not data:
                    continue
                self.logger.info('[page:%d] save file: %s', page, filename)
                with open(filename, 'wb+') as fp:
                    fp.write(data.data)
                dl_count += 1
