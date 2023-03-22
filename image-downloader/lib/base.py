from abc import ABCMeta, abstractmethod

from pydantic import BaseModel


class ImageInfo(BaseModel):
    id: str
    thumb_url: str
    medium_url: str | None
    raw_url: str
    source_url: str | None
    source_host: str | None
    width: int | None
    height: int | None
    etag: str | None
    md5: str | None


class PageResult(BaseModel):
    keyword: str
    total: int | None
    page: int
    page_size: int
    page_count: int | None
    images: list[ImageInfo]


class DataResult(BaseModel):
    url: str
    data: bytes
    headers: dict


class ImageClient(metaclass=ABCMeta):

    @abstractmethod
    def search(self, keyword: str, page: int = 1) -> PageResult:
        pass

    @abstractmethod
    def get_data(self, url: str) -> DataResult:
        pass
