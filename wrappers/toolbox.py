import time
from threading import Timer

'''
    This is the generic function module.
    All generic functions should be placed here.
'''

# Returns current time in second from epoch UTC
current_utc_time = lambda: int(round(time.time()))

# Runs a task at a specified interval.
#     delay = time in seconds between runs
#     action = function name to be repeated
#     actionargs = args to be passed to action function
def repeat_task(delay, action, actionargs=()):
    Timer(delay, repeat_task, (delay, action, actionargs)).start()
    action(*actionargs)