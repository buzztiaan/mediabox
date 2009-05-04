"""
Module for working with threads in PyGTK.

Threading with PyGTK is a sad thing.
If you don't call gtk.threads_init(), your threads will only run while the
GTK event queue is filled.
If you call gtk.threads_init(), you'll sacrifice battery on mobile devices
and risk all sorts of deadlocks when working with callbacks in GTK.

This module is a workaround for this situation and keeps threads running
by keeping the GTK event queue filled with a simple idle callback.
In order to save battery, this idle callback shuts down automatically if
not in use.

Threads must invoke keep_alive() regularly.

B{Anyway, better avoid threads at all costs unless there's a really compelling
reason for using threads.}

@since: 0.96
"""

import logging
import threading
import gobject


_timer = None
_counter = 0
_waiting_lock = threading.Lock()


def _keep_alive():
    global _counter, _timer
    
    _counter += 1
    if (_counter > 100):
        #print "keep alive stopped"
        _timer = None
        return False
    else:
        return True


def run_threaded(f, *args):

    t = threading.Thread(target = f, args = args)
    t.start()
    keep_alive()
    
    
def run_unthreaded(f, *args):

    gobject.timeout_add(0, f, *args)


def keep_alive():
    global _timer, _counter
    
    _counter = 0
    if (not _timer):
        _timer = gobject.idle_add(_keep_alive)



def wait_for(tester, why = None):
    """
    Waits until the given tester returns True.
    @since: 0.96
    
    @param tester: boolean function
    """

    #if (not why): raise IOError
    if (why): print "BEGIN", why
    import gtk
    cnt = 0
    while (not tester()):
        #if (not _waiting_lock.locked()):
        #    _waiting_lock.acquire()
        #print "TICK"
        #print "DEPTH", gobject.main_depth()
        gtk.main_iteration(False)
        #_waiting_lock.release()
        cnt += 1
        #end if
    #end while
    if (why): print "END", why

