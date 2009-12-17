# vim: set encoding=utf-8 et sw=4 sts=4 :
from error import Error
import logging 
log = logging.getLogger('threader')

class Threader(object):
    """Thread handling class.
    """
    threads = []
    last_id = 0
    processors = {}

    def register_processor(self, processor, class_):
        if processor in self.processors:
            raise AlreadyRegisteredProcessorError(processor)
        log.debug(u'register_processor(): %s' % (processor,))
        self.processors[processor] = class_

    def close(self):
        """Closes all threads.
        """
        log.debug(u'close(): Stopping threads.')
        for thread in self.threads:
            self.stop_thread(thread)
        log.debug(u'close(): Joining threads.')
        for thread in self.threads:
            self.join_thread(thread)
        log.debug(u'We have a Threader going down. Bye Bye!')

    def start_thread(self, processor=None, qty=1, *args, **kwargs):
        """Starts a number of threads (defined by qty parametr), and sends all
           named args to the thread constructor.
        """
        if processor not in self.processors or processor is None:
            raise InvalidProcessorError(processor)

        i = 0
        while i < qty:
            name   = '%s_%03d' % (processor, self.last_id + i,)
            thread = self.processors[processor](name=name, **kwargs)
            self.threads.append(thread)
            log.debug(u'start_thread(): %s' % (name))
            thread.start()
            i+=1
        self.last_id+= i
        return i

    def stop_thread(self, thread):
        """Tries to stop a thread. Only live threads are stopped.
        """
        if thread.isAlive():
            log.debug(u'stop_thread(): %s ' % (thread.getName()))
            thread.stop()

    def join_thread(self, thread):
        """Tries to join a thread. Only live threads are joined.
        """
        if thread.isAlive():
            log.debug(u'join_thread(): %s ' % (thread.getName()))
            thread.join()

    def flush(self, **kwargs): 
        """Removes all dead threads from thread list.
        """
        log.debug(u'flush()')
        for thread in self.threads[:]:
            if not thread.isAlive():
                self.threads.remove(thread)

class AlreadyRegisteredProcessorError(Error):
    """Raised when a processor is already registered.
    """
    pass

class InvalidProcessorError(Error):
    """Raised when a processor is already registered.
    """
    pass
