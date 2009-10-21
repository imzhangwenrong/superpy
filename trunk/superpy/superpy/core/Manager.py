"""Module providing a client manager to help distribute tasks over superpy.
"""

import datetime, socket, logging
import TaskInfo, Process

def ProcessElements(elements, dispatchElement, handleResult, maxTime=0):
    unfinishedHandles = []
    numElements = len(elements)
    elementNum = 0
    while (elementNum < numElements):
        element = elements[elementNum]
        handle = dispatchElement(element)
        unfinishedHandles.append((handle, element))
        elementNum += 1
        finishedHandles, unfinishedHandles = WaitForTasks(
            unfinishedHandles, untilFinished=1, maxTime=maxTime)
        CleanupFinishedHandles(finishedHandles, handleResult)
    finishedHandles, unfinishedHandles = WaitForTasks(
        unfinishedHandles, untilFinished=None)
    CleanupFinishedHandles(finishedHandles, handleResult)



def WaitForTasks(handles, untilFinished=None, maxTime=0, handleException=None):
    """Wait for tasks to finish.

    INPUTS:

    -- handles:        List of pairs of the form (handle, element) where
                       handle is a handle to a task that is not finished
                       yet and element is the underlying task element.

    -- untilFinished=None:        Either None or an integer indicating
                                  how man tasks must finish before we
                                  stop waiting.

    -- maxTime=0:   Max time to allow for a test (0 means infinite).

    -- handleException=None:    Optional callable object that can be called as
                                handleException(handle, element, exception).
                                This will be called whenever we get an
                                exception waiting for a task.

    -------------------------------------------------------

    RETURNS:        The pair of lists (finishedHandles, unfinishedHandles)
                    representing tasks that finished or may not yet be
                    finished. Each is a list of pairs of the form
                    (handle, element) like the input.

    -------------------------------------------------------

    PURPOSE:        Takes a list of taskHandles, periodically checking if
                    some or all are finished. When all tasks are
                    done, return a list of handles to the finished
                    tasks. 
    """
    if (handleException is None):
        handleException = lambda _h, _el, exc: logging.debug(
            'Ignoring exception %s' % str(exc))
        
    threshold = datetime.datetime.now() + datetime.timedelta(maxTime)
    finishedHandles, tempHandles = [], []
    while(len(handles) > 0 and
          (untilFinished is None or
           len(finishedHandles) < untilFinished)):
        tempHandles = []
        for (handle, element) in handles:
            newHandle = None
            try:
                oldInfo = handle.StatusInfo()                
                newHandle = handle.UpdatedHandle(timeout = 3)
                info = newHandle.StatusInfo()
                if (info['mode'] == 'finished'):
                    finishedHandles.append((newHandle, element))
                elif (maxTime and newHandle.started and
                      info['starttime'] > threshold):
                    logging.warning('Timeout exceeded; killing task %s'
                                    % str(newHandle))
                    newHandle.Kill()
                    # put back in tempHandles so we clean it up later
                    tempHandles.append((newHandle, element))
                else:
                    tempHandles.append((newHandle, element))
            except socket.error, e:
                logging.warning("""
                Got exception: %s while waiting for task:\n%s
                Will assume task has same status as before and
                continue.""" % (str(e), str(handle)))
                tempHandles.append((handle, element))
            except Exception, e:
                handleInfo = 'unknown'
                try:
                    handleInfo = str(handle)
                except Exception, eAgain:
                    logging.error(
                        'Could not show handle info due to exception:%s'
                        % str(eAgain))
                logging.error("Got exception: %s while waiting for task:\n%s"
                              % (str(e), str(handleInfo)))
                handleException(handle, element, e)
                oldInfo['result'] = 'Got Exception in WaitForTasks: %s'%str(e)
                handle = TaskInfo.InvalidHandle(element.Name(), oldInfo)
                finishedHandles.append((handle, element))

        handles = tempHandles
        
    return finishedHandles, tempHandles

def CleanupFinishedHandles(finishedHandles, handleResult):
    """Cleanup handles that have finished running.

    INPUTS:

    -- finishedHandles:        List of pairs for the form (handle, element)
                               representing handles for finished tasks
                               and the corresponding test plan elements.

    -- handleResult:           Function which takes an element and the
                               corresponding result obtained by running the
                               task and processes that in an appropriate
                               manner.

    -------------------------------------------------------

    PURPOSE:        Remove finished tasks from queue of servers.

    """
    for (h, element) in finishedHandles:
        info = h.StatusInfo()
        theResult = info['result']
        if (isinstance(theResult, Process.PickleHolder)):
            theResult = theResult.Extract()

        handleResult(element, theResult)
        try:
            h.Cleanup()
        except Exception, e:
            logging.warning('Unable to clean handle %s because %s' % (
                str(h), str(e)))
