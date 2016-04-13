import time
from threading import Timer

'''
    This is the generic function module.
    All generic functions should be placed here.
'''

# Returns current time in seconds from epoch UTC
current_utc_time = lambda: int(round(time.time()))

# Returns current time in millis from epoch UTC
current_utc_time_millis = lambda: int(round(time.time()) * 1000)

# Runs a task at a specified interval.
#     delay = time in seconds between runs
#     action = function name to be repeated
#     *args, **kwargs = arguments and keyword arguments to be passed to the function
#     this is an overloaded function and can take an infinite number of arguments
#     syntax = repeat_task(5, myFunc, 3, 4, myKwarg1=True, myKwarg2=10)
def repeat_task(delay, action, *args, **kwargs):
    Timer(delay, repeat_task, [delay, action] + list(args), kwargs).start()
    action(*args, **kwargs)