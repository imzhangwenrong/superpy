"""
Module containing code to represent a Scheduler class which is
used to submit tasks to the best server in a group.
"""
import os, socket, logging, time, pickle
import PicklingXMLRPC
from Servers import BasicRPCServer

class Scheduler:
    """
    Class representing a scheduler to balance tasks among multiple servers.
    """

    def __init__(self,hostList):
        self.hosts = {} # this should only include remote servers
        for i in range(len(hostList)):
            entry = hostList[i]
            if (isinstance(entry,(str,unicode))): entry = [entry]
            if (len(entry) == 1): host,port=entry[0],BasicRPCServer.defaultPort
            elif (len(entry) == 2): host,port = entry
            else:
                raise Exception("Entry %i=%s is not a valid host,port pair." % (
                    i,entry))
            if ((host,port) in self.hosts):
                raise Exception("Pair %s:%s was specified more than once." % (
                    host, port))
            else:
                logging.debug('Making connection to %s' % ([host,port]))
                self.hosts[(host,port)] = self.Connection(host, port)

    def __del__(self):
        """
        Shutdown the local server is it's up.
        Usually called automatically by python.
        """
        logging.info('destroying scheduler')
        localServer = self.Connection()
        if self.IsServerUp(localServer):
            logging.info(
                'Shutting down the local server at localhost:defaultPort')
            localServer.Terminate()
            time.sleep(3)
            logging.info('Local server shutdown')

    def Connection(
        self, host = 'localhost', port = BasicRPCServer.defaultPort):
        """
        return a connection to a server, as an instance of ServerProxy.
        No guarantee the server is up or the connection is usable.
        """
        if host == 'localhost':
            host = os.getenv('computername')
        return self.hosts.get(
            (host, port),
            PicklingXMLRPC.PicklingServerProxy('http://%s:%i'%(host, port)))
    
    @staticmethod
    def IsServerUp(connection):
        """
        ping and see if the server is up.
        connection is an instance of ServerProxy
        """
        try:
            connection.system.listMethods()
        except socket.error:
            return False
        return True
            
    def ConnectToLocalServer(self):
        """
        return a connection to local server, if the server is not up, start it.
        """
        connection = self.Connection()
        if not self.IsServerUp(connection):
            BasicRPCServer().serve_forever_as_thread()
            logging.info('started the server at local host:defaultport')
            time.sleep(3)
        if self.IsServerUp(connection):
            return connection
        raise Exception('could not connect to the local server')
    
    def AllHosts(self):
        """
        return a sorted list of tuple (host, port) including all servers
        """
        hosts = self.hosts.keys()
        # add local server if it's up
        if self.IsServerUp(self.Connection()):
            hosts.append(
                (os.getenv('computername'), BasicRPCServer.defaultPort))
        return sorted(list(set(hosts)))

    def SubmitTaskToBestServer(self,task,*args,**kw):
        """Submit a task to the best available server.
        
        INPUTS:
        
        -- task:        Subclass of Tasks.BasicTask to submit.
        
        -- *args, **kw: Passed to Submit method of best server.
        
        -------------------------------------------------------
        
        RETURNS:        Handle for newly submitted task.
        
        -------------------------------------------------------
        
        PURPOSE:        Submit a task to the best available server.
        
        """
        assert None != task.Name(), 'Task must have a name!'
        logging.debug('Requesting estWaitTimes from known servers.')
        newtimeout = 30
        estWaitTimes = []
        for (k,v) in self.hosts.iteritems():
            try:
                oldtimeout = socket.getdefaulttimeout()
                socket.setdefaulttimeout(
                    newtimeout) # set timeout in case server dead
                logging.debug('Contacting %s:%s...' % (str(k), str(v)))
                
                # maintain backward compatibility,
                # old servers have CPULoad instead of EstWaitTime
                methods = set(pickle.loads(v.system.listMethods()))
                estWaitTime = None
                if 'EstWaitTime' in methods:
                    estWaitTime = v.EstWaitTime(task.priority)
                elif 'CPULoad' in methods:
                    estWaitTime = v.CPULoad()

                if estWaitTime is None:
                    raise Exception(
                        'tried EstWaitTime and CPULoad with no useful result')
                estWaitTimes.append((k, v, estWaitTime))
                logging.debug(
                    'Got estWaitTime of %s from %s:%s'%(estWaitTimes[-1],k,v))
            except socket.error, e:
                logging.warning('Unable to contact %s:%s because %s;skipping'% (
                    str(k),str(v),str(e)))
            except Exception, e:
                logging.warning('Unable to contact %s:%s because %s;skipping'% (
                    str(k),str(v),str(e)))
            finally:
                socket.setdefaulttimeout(oldtimeout)
                
        if len(estWaitTimes) < 1:
            raise Exception(
                'No server can be reached in %s seconds, re-try later'
                %newtimeout)
        estWaitTimes.sort(key=lambda entry: entry[2])
        logging.debug('Loads are %s' % str(estWaitTimes))
        handle = estWaitTimes[0][1].Submit(task,*args,**kw)
        return handle

    def ShowQueue(self, host, port, timeout=3):
        """Show queue for server at given host, port.
        """
        try:
            oldtimeout = socket.getdefaulttimeout()
            socket.setdefaulttimeout(timeout) # set timeout in case server dead
            logging.debug('Contacting %s:%s...' % (host, port))
            return self.Connection(host, port).ShowQueue()
        except Exception, e:
            logging.info('Timeout: Unable to contact %s:%s because %s' % (
                str(host),str(port),str(e)))
        finally:
            socket.setdefaulttimeout(oldtimeout)

    def CleanOldTasks(self, host, port):
        """Call CleanOldTasks for server at given host, port.
        """
        return self.Connection(host, port).CleanOldTasks()
