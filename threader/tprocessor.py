import threading
import time

import logging 
log = logging.getLogger('tprocessor')

class TProcessor(threading.Thread):
    _stop = False
    _time_started = 0
    _time_stopped = 0

    def __init__(self, **kwargs):
        threading.Thread.__init__(self, **kwargs)

    def stop(self):
        self._stop = True
    
    def run(self):
        self._time_started = time.time()
        self._run()
        self._time_stopped = time.time()

    def get_run_time(self):
        run_time = 0
        if self._time_started > 0 and self._time_stopped > 0:
            run_time = self._time_stopped - self._time_started
        elif self._time_started > 0 and self._time_stopped == 0:
            run_time = time.time() - self._time_started
        return run_time

    run_time = property(get_run_time, doc='Thread running time.')


class Processor(TProcessor):
    loops = 0

    def _run(self):
        log.debug(u'Starting %s' % (self.getName()))
        while not self._stop:
            self.loops+=1
            time.sleep(2)
        log.debug(u'Stopping %s' % (self.getName()))
