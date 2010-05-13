"""Script to spawn server on current machine as a windows service.

To install, start, stop, debug, or perform other tasks with the service,
run this module from the command line. If you run it without any arguments,
a help message will be printed describing how to run it.

Generally, the things you want to do are

SpawnAsService.py --startup auto install
SpawnAsService.py start
SpawnAsService.py stop
SpawnAsService.py debug
"""
# do not import logging or logging.handler just yet
import sys
import win32serviceutil, win32service, win32event

from superpy.scripts import Spawn
from superpy.utils import WindowsUtils
from superpy.core import config

class RotatedFile:
    """
    A file based stream implementation.
    
    It opens a file in mode 'a+' and never close or redirect to other files,
    so that its  reference can be kept as stdout and stderr.
    
    When the file gets full, it truncate the beginning of the file and save
    the last part (the tail) to make more space.
    
    The beginning of the file will be lost but it's the tail that is more
    relavant and kept.
    """
    def __init__(self, fName, size = 20000000, tail = None):
        """
        fName is the full path-and-name of the file
        size is the max bytes allowed for this file
        tail specifies how many bytes at the end of the file should be kept
        when rotating. if tail is None or larger than size, half of the size
        will be kept.
        """
        self._file = file(fName, 'a+')
        self._size = size
        self._tail = tail
        if self._tail is None or self._tail >= self._size:
            self._tail = self._size / 2
        
    def _File(self):
        """
        truncate and keep the tail
        """
        self._file.seek(0, 2)
        size = self._file.tell()
        if size > self._size:
            self._file.seek(-self._tail, 2)
            tail = self._file.read()
            self._file.truncate(0)
            self._file.write(tail)
            self._file.flush()
        return self._file
        
    def __getattr__(self, name):
        if name in ['__init__', '_File', '__getattr__', '__getattribute__']:
            return getattr(self, name)
        return getattr(self._File(), name)        

    def __getattribute__(self, name):
        return self.__getattr__(name)

class SuperpyService(win32serviceutil.ServiceFramework):
    """Class to act as superpy service.
    """
    _svc_name_ = 'SuperpyService'
    _svc_display_name_ = 'Superpy parallel processing server'

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        # Create an event which we will use to wait on.
        # The "service stop" requrest will set this event.
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)

    def SvcStop(self):
        "Stop the service."
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        "Start the service."

        self.SetupLogging()

        WindowsUtils.SetPriority('REALTIME_PRIORITY_CLASS')
        _server = Spawn.SpawnServer(daemon=True)

        import logging
        logging.info('Running until we see service stop event')
        # Now just wait for a stop request
        win32event.WaitForSingleObject(self.hWaitStop, win32event.INFINITE)

        # Time to shutdown.
        # Since we started server as daemon, just exit program by returning.
        return None


    @staticmethod
    def SetupLogging():
        "Arrange output to go to log file."
        logFile = config.serviceLogFile
        logFile = RotatedFile(logFile)
        sys.stdout = logFile
        sys.stderr = logFile
        import logging, logging.handlers
        handler = logging.StreamHandler(logFile)
        logging.getLogger('').addHandler(handler)

        logging.getLogger('').setLevel(config.defaultLogLevel)
        logging.info('Set log level to %s from config.'%config.defaultLogLevel)

        logging.info('Redirected stdout and stderr to %s'%logFile.name)

if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(SuperpyService)
