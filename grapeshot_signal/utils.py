from functools import wraps
import time
import threading

# based on https://gist.github.com/gregburek/1441055
def rate_limited(max_per_second):

    min_interval = 1.0 / max_per_second
    last_time_called = (0.0,)
    lock = threading.Lock()

    def decorate(func):
        last_time_called = time.perf_counter()

        @wraps(func)
        def rate_limited_function(*args, **kwargs):
            lock.acquire()
            elapsed = time.perf_counter() - last_time_called
            left_to_wait = min_interval - elapsed

            if left_to_wait > 0:
                time.sleep(left_to_wait)

            ret = func(*args, **kwargs)
            last_time_called = time.perf_counter()
            lock.release()
            return ret

        return rate_limited_function

    return decorate
