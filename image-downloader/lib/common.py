import hashlib
import json
import logging
import sys


def md5_hex(val: any) -> str:
    if not isinstance(val, bytes):
        if not isinstance(val, str):
            val = str(val)
        val = val.encode('utf-8')
    h = hashlib.md5()
    h.update(val)
    return h.hexdigest().lower()


def config_logging():
    logging.basicConfig(level=logging.INFO,
                        encoding='utf-8',
                        stream=sys.stdout,
                        format='%(message)s')


class DuplicateDetector:

    def __init__(self, limit: int = 3):
        self._limit = limit
        self._saved = None
        self._count = 0

    def detect(self, data: any) -> bool:
        data = json.dumps(data)
        if data == self._saved:
            self._count += 1
            if self._count >= self._limit:
                return True
        else:
            self._saved = data
            self._count = 0
        return False
