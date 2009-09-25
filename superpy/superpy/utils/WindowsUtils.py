"""Module containing useful utitlies for windows machines.
"""

import logging

try:
    import win32api, win32con, win32process
except Exception, e:
    logging.error('''
    Could not import win32api, win32con, win32process due to exception:
    %s
    Have you installed python win32 tools?
    ''' % str(e))


def SetPriority(priority, pid=None):
    """Set priority for current windows process.

    INPUTS:

    -- priority:       String in [IDLE_PRIORITY_CLASS,
                       BELOW_NORMAL_PRIORITY_CLASS, NORMAL_PRIORITY_CLASS,
                       ABOVE_NORMAL_PRIORITY_CLASS, HIGH_PRIORITY_CLASS,
                       REALTIME_PRIORITY_CLASS] indicating priority.


    -- pid=None:       Optional process id. None indicates current process. 

    -------------------------------------------------------

    PURPOSE:    Set priority for windows process.

    """

    logging.debug('Setting priority to %s' % str(priority))


    if (pid is None):
        pid = win32api.GetCurrentProcessId()

    handle = win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS, True, pid)
    if (isinstance(priority, (str,unicode))):
        priority = getattr(win32process, priority)
    win32process.SetPriorityClass(handle, priority)

