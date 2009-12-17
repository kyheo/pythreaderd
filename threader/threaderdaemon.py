# vim: set encoding=utf-8 et sw=4 sts=4 :

import sys
import signal
import socket

import eventloop
import threader
import dispatcher
import tprocessor

from dispatcher import AlreadyRegisteredActionError, InvalidActionError

import logging 
log = logging.getLogger('threaderdaemon')

class ThreaderDaemon(eventloop.EventLoop, threader.Threader):
    """Example class wich extends both EventLoop and Threader.
    """

    dispatcher = None

    def __init__(self, port=9000):
        """Set up the file handler and register all actions to handle messages
           with the dispatcher.
        """
        log.debug('ThreaderDaemon()')
        
        # "File" creation
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('', port))

        signals = {signal.SIGINT : self._action_close, \
                   signal.SIGTERM: self._action_close}
        eventloop.EventLoop.__init__(self, sock, signals=signals)

        log.debug(u'ThreaderDaemon(): register processors')
        self.register_processor('processor', tprocessor.Processor)
        self.register_processor('processor2', tprocessor.Processor2)

        self.dispatcher = dispatcher.Dispatcher()
        log.debug(u'ThreaderDaemon(): register actions')
        self.dispatcher.register_action('close' , self._action_close)
        self.dispatcher.register_action('count' , self._action_count)
        self.dispatcher.register_action('start' , self._action_start)
        self.dispatcher.register_action('istop' , self._action_istop)
        self.dispatcher.register_action('mstop' , self._action_mstop)
        self.dispatcher.register_action('flush' , self._action_flush)
        self.dispatcher.register_action('list'  , self._action_list )

    def run(self, processor, qty):
        """Runs the main process. 
           Qty parameter is used to start the number of threads defined.
        """
        log.debug(u'run(): %s - %d' % (processor, qty))
        self.start_thread(processor=processor, qty=qty)
        return self.loop()

    def handle(self):
        """EventLoop.handle redefinition. Send incomming messages to the
           dispatcher and the response to the sender.
        """
        (msg, addr) = self.file.recvfrom(65535)
        response = u' -- nok -- \n'
        try:
            response = self.dispatcher.dispatch(unicode(msg, 'utf-8'))
        except InvalidActionError, e:
            response = u"""Invalid action: %s. Call help to get the full list of available actions.\n""" % (str(e),)
        except Exception, e:  
            response = u'Error: %s\n' % (str(e),)
        self.file.sendto(response.encode('utf-8'), addr)            

    def _action_count(self, params):
        """Numerical stats about threads.
        """
        running  = True
        stopped  = True
        response = ""
        if params is not None:
            if params[0] == 'on':
                stopped = False
            elif params[0] == 'off':
                running = False

        if running and stopped:
            response+= u"Total threads: %d\n" % (len(self.threads),)
        
        dead  = 0
        alive = 0
        for thread in self.threads:
            if thread.isAlive():
                alive+= 1
            else:
                dead+= 1
        
        response+= u" - Alive: %d\n" % (alive,)
        response+= u" - Dead : %d\n" % (dead,)
        return response

    def _action_start(self, params):
        """Start X threads, being X the first (and only) parameter sent.
           Example: start <type> 3 # Will start 3 new threads of type <type>.
        """
        tot = self.start_thread(processor=params[0], qty=int(params[1]))
        return u"%d threads started.\n" % (tot,)

    def _action_istop(self, params):
        """Stop X thread, being X the position in the thread list.
          Multiple positions can be sent using , as separator
           Example: istop 1       # Will stop thred in position 1 (not 0).
                    istop 2,3,4,5 # Will stop all those threads.
        """
        response = ""
        for tid in params:
            if self.threads[int(tid)] is not None:
                thread = self.threads[int(tid)]
                self.stop_thread(thread)
                response+= u"%s stopped.\n" % (thread.getName(),)
        for tid in params:
            if self.threads[int(tid)] is not None:
                thread = self.threads[int(tid)]
                self.join_thread(thread)
                response+= u"%s joined.\n" % (thread.getName(),)
        return response
    
    def _action_mstop(self, params):
        """Multiple Stop X threads, being X the number of threads that will be stopped.
           Example: mstop 13 # Will stop the first 13 threads that are running.
        """
        total   = int(params[0])
        stopped = 0
        joined  = 0 
        i       = 0
        threads = []
        while stopped < total and i < len(self.threads):
            thread = self.threads[i]
            if thread.isAlive():
                self.stop_thread(thread)
                threads.append(thread)
                stopped+= 1
            i+= 1
        for thread in threads:
            if thread.isAlive():
                joined+= 1
                thread.join()

        return u"%d threads stopped. %d threads joined.\n" % (stopped, joined)
    
    def _action_close(self, *args, **kwargs):
        """Shutdown the application,
           Example: close
        """
        self.stop()
        threader.Threader.close(self)
        return u'close()\n'
    
    def _action_flush(self, **kwargs):
        """Removes from the thread list all the dead ones.
           Example: flush
        """
        self.flush()
        return u"flushed.\n"

    def _action_list(self, params=None):
        """Display statistics. nil, on and off are the accepted parameters
           Example: list     # Will list all threads
                    list on  # Will list all alive threads
                    list off # will list only dead threads
        """
        running = True
        stopped = True
        if params is not None:
            if params[0] == 'on':
                stopped = False
            elif params[0] == 'off':
                running = False
            
        response = "ID - NAME - ALIVE - LOOPS\n"
        response+= "-------------------------\n"
        for thread in self.threads:
            if (thread.isAlive() and running) or (not thread.isAlive() and stopped):
                response+= u"%d - %s - %s - %d - %.2f\n" % \
                    ( \
                        self.threads.index(thread), \
                        thread.getName(), \
                        str(thread.isAlive()), \
                        thread.loops, \
                        thread.run_time \
                    )

        return response
