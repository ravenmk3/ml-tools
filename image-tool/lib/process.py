import logging
import os
import queue
import threading
from typing import Callable


class WorkItem:

    def __init__(self, filepath: str, content: any):
        self.filepath = filepath
        self.content = content
        self.output = None


class MultiThreadFileProcessor:

    def __init__(self, src_dir: str,
                 scanner: Callable, loader: Callable,
                 processor: Callable, saver: Callable,
                 num_workers: int = 1, queue_size: int = 10):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.src_dir = src_dir
        self.scanner = scanner
        self.loader = loader
        self.saver = saver
        self.processor = processor
        self.num_workers = num_workers
        self.queue_loaded = queue.Queue(maxsize=queue_size)
        self.queue_processed = queue.Queue(maxsize=queue_size)
        self.worker_threads = None
        self.saver_thread = None
        self.files = None

    def run(self):
        self._scan_files()
        self._start_worker_threads()
        self._start_saver_thread()
        self._load_files()
        self._wait_worker_threads()
        self._wait_saver_thread()

    def _scan_files(self):
        self.logger.info('scanning files in %s', self.src_dir)
        files = self.scanner(self.src_dir)
        total = len(files)
        self.logger.info('files found: %d', total)
        self.files = files

    def _load_files(self):
        for file in self.files:
            rel_path = os.path.relpath(file, self.src_dir)
            try:
                data = self.loader(file)
                item = WorkItem(rel_path, data)
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
                self.logger.debug('get none item, break')
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
                self.logger.debug('get none item, break')
                break
            try:
                self.saver(item)
            except Exception as e:
                self.logger.error(e, exc_info=True)
            self.queue_processed.task_done()
