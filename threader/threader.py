# vim: set encoding=utf-8 et sw=4 sts=4 :

import tprocessor

import logging 
log = logging.getLogger('threader')

class Threader(object):
    threads    = []
    last_id    = 0

    def close(self):
        """Closes all threads and then the main process.
        """
        log.debug(u'close(): Stopping threads.')
        for thread in self.threads:
            self.stop_thread(thread)
        log.debug(u'close(): Joining threads.')
        for thread in self.threads:
            self.join_thread(thread)
        log.debug(u'We have a Threader going down. Bye Bye!')

    def start_thread(self, qty=1):
        i = 0
        while i < qty:
            name   = 'TProcessor_%03d' % (self.last_id + i,)
            thread = tprocessor.Processor(name=name)
            self.threads.append(thread)
            log.debug(u'start_thread(): %s' % (name))
            thread.start()
            i+=1
        self.last_id+= i
        return i

    def stop_thread(self, thread):
        if thread.isAlive():
            log.debug(u'stop_thread(): %s ' % (thread.getName()))
            thread.stop()

    def join_thread(self, thread):
        if thread.isAlive():
            log.debug(u'join_thread(): %s ' % (thread.getName()))
            thread.join()

    def flush(self, **kwargs): 
        log.debug(u'flush()')
        for thread in self.threads[:]:
            if not thread.isAlive():
                self.threads.remove(thread)
