import logging
import queue
import threading
from abc import ABCMeta, abstractmethod
from typing import Callable


class Item:

    def __init__(self, name: str, content: any):
        self.name = name
        self.content = content
        self.output = None


class Scanner(metaclass=ABCMeta):

    @abstractmethod
    def scan(self) -> list[str]:
        pass


class Loader(metaclass=ABCMeta):

    @abstractmethod
    def load(self, name: str) -> any:
        pass


class Saver(metaclass=ABCMeta):

    @abstractmethod
    def save(self, item: Item):
        pass


class MultiThreadProcessor:

    def __init__(self,
                 scanner: Scanner, loader: Loader,
                 processor: Callable, saver: Saver,
                 num_workers: int = 1, queue_size: int = 10):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.scanner = scanner
        self.loader = loader
        self.saver = saver
        self.processor = processor
        self.num_workers = num_workers
        self.queue_loaded = queue.Queue(maxsize=queue_size)
        self.queue_processed = queue.Queue(maxsize=queue_size)
        self.worker_threads = None
        self.saver_thread = None
        self.item_names = None

    def run(self):
        self._scan_items()
        self._start_worker_threads()
        self._start_saver_thread()
        self._load_items()
        self._wait_worker_threads()
        self._wait_saver_thread()

    def _scan_items(self):
        self.logger.info('scanning items', )
        item_names = self.scanner.scan()
        total = len(item_names)
        self.logger.info('items found: %d', total)
        self.item_names = item_names

    def _load_items(self):
        for name in self.item_names:
            try:
                data = self.loader.load(name)
                item = Item(name, data)
                self.queue_loaded.put(item)
            except Exception as e:
                self.logger.error(e, exc_info=True)

    def _start_worker_threads(self):
        threads = []
        for n in range(1, self.num_workers + 1):
            th = threading.Thread(target=self._run_worker_process, name=f'worker-{n}', daemon=True)
            th.start()
            threads.append(th)
        self.worker_threads = threads

    def _wait_worker_threads(self):
        for _ in range(self.num_workers):
            self.queue_loaded.put(None)
        for th in self.worker_threads:
            if th.is_alive():
                th.join()

    def _start_saver_thread(self):
        th = threading.Thread(target=self._run_saver_process, name='saver', daemon=True)
        th.start()
        self.saver_thread = th

    def _wait_saver_thread(self):
        self.queue_processed.put(None)
        self.saver_thread.join()

    def _run_worker_process(self):
        while True:
            item = self.queue_loaded.get()
            if item is None:
                self.logger.debug('got none, break')
                break
            try:
                item.output = self.processor(item.content)
                self.queue_processed.put(item)
            except Exception as e:
                self.logger.error(e, exc_info=True)
            self.queue_loaded.task_done()

    def _run_saver_process(self):
        while True:
            item = self.queue_processed.get()
            if item is None:
                self.logger.debug('got none, break')
                break
            try:
                self.saver.save(item)
            except Exception as e:
                self.logger.error(e, exc_info=True)
            self.queue_processed.task_done()
