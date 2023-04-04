from threading import Lock


class AtomicCounter:

    def __init__(self, init_value: int = 0):
        self.value = init_value
        self.lock = Lock()

    def increase(self, val: int) -> int:
        self.lock.acquire()
        new_val = self.value + val
        self.value = new_val
        self.lock.release()
        return new_val

    def is_less_then(self, val: int) -> bool:
        self.lock.acquire()
        result = self.value < val
        self.lock.release()
        return result

    def is_more_then(self, val: int) -> bool:
        self.lock.acquire()
        result = self.value > val
        self.lock.release()
        return result
