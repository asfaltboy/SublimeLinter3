from . import persist

import time
import threading


# Map from view_id to threading.Timer objects
timers = {}


# For compatibility this is a class with unchanged API from SL3.
class Daemon:
    def start(self, callback):
        self._callback = callback

    def hit(self, view):
        assert self._callback, "Queue: Can't hit before start."

        vid = view.id()
        delay = get_delay()  # [seconds]
        return queue_lint(vid, delay, self._callback)


def queue_lint(vid, delay, callback):
    hit_time = time.monotonic()

    def worker():
        callback(vid, hit_time)

    try:
        timers[vid].cancel()
    except KeyError:
        pass

    timers[vid] = timer = threading.Timer(delay, worker)
    timer.start()

    return hit_time


def get_delay():
    """Return the delay between a lint request and when it will be processed.

    If the lint mode is not background, there is no delay. Otherwise, if
    a "delay" setting is not available in any of the settings, MIN_DELAY is used.
    """
    if persist.settings.get('lint_mode') != 'background':
        return 0

    return persist.settings.get('delay')


queue = Daemon()
