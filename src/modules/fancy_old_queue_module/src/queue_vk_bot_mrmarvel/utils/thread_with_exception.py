import ctypes
import threading
from typing import Callable, Any


class ThreadWithException(threading.Thread):
    def __init__(self, target, args, daemon):
        threading.Thread.__init__(self, target=target, args=args, daemon=daemon)

    def get_id(self):

        # returns id of the respective thread
        if hasattr(self, '_thread_id'):
            return self._thread_id
        for id, thread in threading._active.items():
            if thread is self:
                return id

    def raise_exception(self):
        thread_id = self.get_id()
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id,
                                                         ctypes.py_object(SystemExit))
        if res > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)
            print('Exception raise failure')


class ThreadWithEvent(threading.Thread):
    def __init__(self, target: Callable[[threading.Event, Any], Any], args: tuple, daemon: bool = True):
        self._stop_state = threading.Event()
        threading.Thread.__init__(self, target=target, args=(self._stop_state,) + args, daemon=daemon)

    def stop(self):
        self._stop_state.set()
