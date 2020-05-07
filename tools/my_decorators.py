import functools
import time


def run_time(func):
    """Print the runtime of the decorated function
    Return the runtime as the timed attribute of the function"""
    @functools.wraps(func)
    def wrapper_timer(*args, **kwargs):
        start_time = time.perf_counter()  # 1
        value = func(*args, **kwargs)
        end_time = time.perf_counter()  # 2
        run_time = end_time - start_time  # 3
        wrapper_timer.timed = run_time
        print(f"Finished {func.__name__!r} in {run_time:.4f} secs")
        return value

    wrapper_timer.timed = 0.0
    return wrapper_timer
