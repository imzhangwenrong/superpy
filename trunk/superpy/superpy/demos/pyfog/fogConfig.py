"""Module representing configuration parameters.
"""

import re, logging, os, optparse

def ConfProp(func):
    """Decorator to make a config item property.
    
    INPUTS:
    
    -- func:    Function containing name and docstring for property.
    
    -------------------------------------------------------
    
    RETURNS:    Function representing config property.
    
    -------------------------------------------------------
    
    PURPOSE:    Provide a simple way to make config item properties.

    Example usage is illustrated below:

>>> from config import ConfProp
>>> class foo(object):
...     def __init__(self):
...             self._bar = None     # actual property will refer to this
...     @ConfProp
...     def bar(self):
...             'The bar property is an example property.'
... 
>>> f = foo()
>>> f.bar = 5
>>> f.bar
5
    """

    privateName = '_' + func.__name__
    doc = func.__doc__
    def GenericGet(instance):
        "Return value."
        return getattr(instance, privateName)
    def GenericSet(instance, value):
        "Set value."
        setattr(instance, privateName, value)
    result = property(GenericGet, GenericSet, None, doc)
    return result

class GenericConfig(object):
    """Base class for generic configuration sections.
    """

    # Dictionary of string keys of configuration objects in self
    # and their default values.
    # Sub-classes should override with their own defaults.
    _defaults = {}

    # Dictionary of string keys of configuration objects in self
    # and the action to use for each. The default action 'store'
    # will be provided. Override only if you want special actions
    # (e.g., 'append') used for some items.
    _actions = {}
    
    @classmethod
    def UpdateParser(cls, parser, withDefaults):
        """Update OptionParser to parse args expected by this class.
        
        INPUTS:
        
        -- cls:        Class (usually supplied by python interpreter).
        
        -- parser:     Instance of optparse.OptionParser class.
        
        -- withDefaults:        Whether to include defaults in parser.
        
        -------------------------------------------------------
        
        PURPOSE:        Go through all configuration properties in cls,
                        and add entries for them to parser. If withDefaults,
                        is true, then default values are added to the parser.
        
        """
        for (name, item, default) in cls.GetProperties():
            if (not withDefaults): default = None
            parser.add_option(
                '--%s'%name, dest=name, help=item.__doc__,
                default = default, action=cls._actions.get(name, 'store'))

    @classmethod
    def GetProperties(cls):
        """Return list of configuration properties.
        
        -------------------------------------------------------
        
        RETURNS:        List of tuples of the form (name, item, default)
                        representing the name, property object and default
                        value for all configuration properties in the class.
        
        -------------------------------------------------------
        
        PURPOSE:        Provide a simple way to get config properties.
        
        """

        defaults = cls._defaults
        result = []
        for name in dir(cls):
            item = getattr(cls, name, None)
            if (isinstance(item, property)):
                result.append((name, item, defaults.get(name, None)))
        return result

    def SetFromOptions(self, options):
        """Set configuration properties in self from options.
        
        INPUTS:
        
        -- options:        Options parsed by optparse.OptionParser class.
        
        -------------------------------------------------------
        
        PURPOSE:        Sets the values of all configuration properties in
                        self from the values in options. Any values of None
                        are ignored and the old values are kept.
        
        """
        for (name, _ignore, _junk) in self.GetProperties():
            value = getattr(options, name, None)
            if (value is not None): setattr(self, name, value)

    def Validate(self):
        "Validate args in self; sub-classes should override"
        
        _ignore = self

    

class CountingSessionConfig(GenericConfig):
    """Configuration for test session.
    """

    _defaults = {
        'logLevel' : 'INFO',
        'outputFile' : '',
        'maxWords' : 30,
        'serverList' : 'None',        
        'domain' : '', 
        'password' : '',
        'killRegexp' : '''(<[^<>]+>)|([=.><,;:"'!?\[\]{}\\\\])|'''
        }


    @ConfProp
    def logLevel(self):
        """String log-level (one of DEBUG, INFO, WARNING, CRITICAL, ERROR).
        """

    @ConfProp
    def killRegexp(self):
        """Regular expression for characters to kill/erase before counting.
        """

    @ConfProp
    def maxWords(self):
        """Maximum number of words to show results for.
        """

    @ConfProp
    def serverList(self):
        """Either 'None' or comma separated list of host:port:re triples.

        If present, this represents a list of superpy servers to parallelize
        tests to. For example, if you provide

          'USBODV30:9287,USBODV31:9287'

        then the servers USBODV30 and USBODV31 would be used each with
        port number 9287. Of course, you must make sure a superpy server
        is listening at the appropriate place.

        You can also provide regular expressions to force things matching
        those regular expressions to be sent to specific servers. For example,

          'USBODV30:9287:foobar,USBODV31:9287:barbaz,USBODV32:9287'

        would send things matching foobar to USBODV30, things matching
        barbaz to USBODV31 and send anything else to the next available
        server. This feature is particularly useful if you want to force
        a set of tests to run in order on a specific server.
        """

    @ConfProp
    def domain(self):
        """Network domain to use for remote tasks.

        This is used as the network domain when superpy is used to
        spawn tests remotely.
        """

    @ConfProp
    def password(self):
        """Password used to spawn remote tasks.
        """

    @ConfProp
    def outputFile(self):
        """File to write output to. If not given, output is sent to stdout.
        """


    def __init__(self, *args, **kw):
        self._logLevel = None
        self._serverList = None
        self._outputFile = None
        self._maxWords = None

        GenericConfig.__init__(self, *args, **kw)
        
    def Validate(self):
        """Validate arguments and raise exceptions if something is wrong.
        """
        self._maxWords = int(self._maxWords)
        if (self._serverList is None or self._serverList == 'None' or
            self._serverList == ''):
            self._serverList = None
        elif (isinstance(self._serverList,(str,unicode))): # split into lists
            myList = str(self._serverList)
            self._serverList = []
            for origItem in myList.split(','):
                item = origItem.split(':')
                if (len(item) == 2):
                    self._serverList.append((item[0], int(item[1]), None))
                elif (len(item) == 3):
                    self._serverList.append((item[0], int(item[1]),
                                             re.compile(item[2])))
                else:
                    raise Exception('Could not parse serverList element %s.'
                                    % str(origItem))

def GetHome():
    """Determine and return home directory for user.
    """
    env = os.environ
    result = env.get('HOME',env.get('HOMEDRIVE',None))
    if (result is None):
        logging.warning('Could not determine home drive. Using c:/HOME')
        result = 'c:/HOME'
        if (not os.path.exists(result)): os.mkdir(result)
    if (not os.path.exists(result)):
        raise Exception('Home drive %s does not exists' % result)
    return result

        
class MetaConfig(GenericConfig):
    """Meta-configuration item that holds other config items.

    Sub-classes must define the following class variables:
    
        _subconfigs_:   List of pairs of the form (name, kls) where name is
                        the string name of a GenericConfig instance in self
                        and kls is the corresponding class for that item.
                        For example, if self.files contains a FileConfig
                        instance, subconfigs would be ['files', FileConfig].

        _conf_name_:    String used to determine configuration file name.
    """

    _subconfigs_ = None
    _conf_name_ = None

    def __init__(self, optionArgs=None, configFile = None):
        GenericConfig.__init__(self)

        # First create parser to read config file
        if (configFile is None):
            if (self._conf_name_ is None):
                raise Exception('Could not determine config file name.')
            else:
                configFile = os.path.join(GetHome(),'.pyfog_%s_rc'
                                          % self._conf_name_)

        if (not os.path.exists(configFile)):
            logging.warning('Config file %s does not exist; creating.'
                            % configFile)
            self.CreateDefaultConfigFile(configFile)

        self.SetFromConfigFile(configFile)

        # Next create parser to read the given options
        parser = optparse.OptionParser()
        self.UpdateParser(parser, withDefaults = False)        
        if (optionArgs is None): options, args = parser.parse_args()
        else: options, args = parser.parse_args(args = optionArgs)
        if (args): raise Exception('Invalid positional args: %s.' % str(args))
        self.SetFromOptions(options)

    def Validate(self):
        "Call validate on all children if possible."
        for (name, _kls) in self._subconfigs_:
            subConf = getattr(self, name)
            subConf.Validate()

    def CreateDefaultConfigFile(self, configFile):
        """Create default config file.
        
        INPUTS:
        
        -- configFile:        String name of where config file should go.
        
        -------------------------------------------------------
        
        PURPOSE:        Write out default config file based on default params.
        
        """
        fd = open(configFile, 'w')
        fd.write('# Configuration file for Fogger %s\n\n' % self._conf_name_)
        for (name, kls) in self._subconfigs_:
            fd.write('# Section for %s\n\n' % name)
            fd.write('# ' + '\n# '.join(kls.__doc__.split('\n')) + '\n\n')
            for (name, item, default) in kls.GetProperties():
                fd.write('\n')
                fd.write('# ' + '\n# '.join(item.__doc__.split('\n')) + '\n')
                if (default is None): fd.write('#%s=<value>\n' % name)
                else: fd.write('%s=%s\n' % (name, str(default)))
        fd.close()
        
    def SetFromConfigFile(self, configFile):
        """Set self based on values in given configFile.
        
        INPUTS:
        
        -- configFile:        String path to existing config file.
        
        -------------------------------------------------------
        
        PURPOSE:        Set values in self and child config objects based
                        on values in given config file.
        
        """
        parser = optparse.OptionParser()
        self.UpdateParser(parser, withDefaults = True)        
        fd = open(configFile, 'r')
        data = fd.read().split('\n')
        args = []
        for line in data:
            line = line.strip()
            if (not len(line)): pass
            elif (line[0] == '#'): pass
            else:
                args.append('--'+line)
        options, otherArgs = parser.parse_args(args = args)
        if (otherArgs):
            raise Exception('Invalid positional args: %s.' % str(otherArgs))
        self.SetFromOptions(options)
    
    @classmethod
    def UpdateParser(cls, parser, withDefaults):
        """Override UpdateParser to call UpdateParser for subconfigs.
        """
        for (_name, kls) in cls._subconfigs_:
            kls.UpdateParser(parser, withDefaults)

    def SetFromOptions(self, options):
        """Override SetFromOptions to call SetFromOptions for subconfigs.
        """        
        for (name, _kls) in self._subconfigs_:
            getattr(self, name).SetFromOptions(options)

class FoggerConfig(MetaConfig):
    """MetaConfig object containing configuration for tester.
    """

    _subconfigs_ = [('session', CountingSessionConfig)]
    _conf_name_ = 'counter'

    def __init__(self, *args, **kw):
        self.session = CountingSessionConfig()
        MetaConfig.__init__(self, *args, **kw)

