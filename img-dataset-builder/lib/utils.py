import functools
import logging
import time
from typing import List
from urllib.parse import urlparse

from requests import HTTPError


def read_lines(file: str, delimiter: str = '\n') -> List[str]:
    with open(file, 'rb') as fp:
        lines = fp.read().decode('utf-8').strip().split(delimiter)
    return lines


def write_lines(file: str, lines: List[str], delimiter: str = '\n'):
    data = delimiter.join(lines).encode('utf-8')
    with open(file, 'wb+') as fp:
        fp.write(data)


def extract_hostname(url: str) -> str:
    return urlparse(url).hostname


def http_retry(count: int = 99999):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for n in range(count):
                try:
                    return func(*args, **kwargs)
                except HTTPError as e:
                    code = e.response.status_code
                    logging.error('Response: %d, %s', code, str(e))
                    if code in [401, 403, 404]:
                        return None
                    if code in [429, 514]:
                        time.sleep(1)
                except Exception as e:
                    logging.error(e, exc_info=True)

        return wrapper

    return decorator
