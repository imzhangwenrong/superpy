"""Module providing main fog computing tools.
"""

import re, urllib

class FogSource:
    """Abstract class representing input source for FogMachine.

    Subclasses should override GetWords as described in the docstring
    for GetWords to return a word frequency dictionary.
    """

    def __init__(self):
        pass

    def GetWords(self):
        """Return a dictionary representing word frequency from this source.

        This method shall return a dictionary with string keys representing
        words or phrases and values of integers representing number of
        occurences in the given source.
        """
        
        raise NotImplementedError

    @staticmethod
    def _GetWordsFromFD(config, fd):
        result = {}
        data = fd.read()
        data = re.sub(config.session.killRegexp,'',data)
        for word in data.split():
            if (word == ''):
                pass
            elif (word in result):
                result[word] += 1
            else:
                result[word] = 1
        return result
    

class WebSource(FogSource):

    def __init__(self, url):
        FogSource.__init__(self)
        self.url = url

    def GetWords(self, config):
        opener = urllib.FancyURLopener({})
        fd = opener.open(self.url)
        return self._GetWordsFromFD(config, fd)

class FileSource(FogSource):
    """FogSource taking input from an existing file.
    """

    def __init__(self, fileName):
        FogSource.__init__(self)
        self.fileName = fileName

    def GetWords(self, config):
        """Override as required by FogSource.
        """
        fd = open(self.fileName,'r')
        return self._GetWordsFromFD(config, fd)

class FogMachine:
    """Class to create a word fog from many input sources.
    """

    def __init__(self, config, sources=(),):
        self.sources = list(sources)
        self.config = config
        self.wordCount = {}

    def Reset(self):
        """Reset state of FogMachine so you can run it again.
        """
        self.wordCount = {}

    def AddSource(self, source):
        """Add a new source to pull data from.
        
        INPUTS:
        
        -- source:        Instance of FogSource.
        
        -------------------------------------------------------
        
        PURPOSE:        Tells FogMachine to add given source to list of sources
                        to analyze.
        
        """
        if (not isinstance(source, FogSource)):
            raise TypeError('FogMachine.AddSource excepts a FogSource; got %s'
                            % str(source))
        self.sources.append(source)

    def CountWords(self):
        """Count words in all sources.
        
        -------------------------------------------------------
        
        RETURNS:      Dictionary of word frequencies extracted from all
                      sources.
        
        -------------------------------------------------------
        
        PURPOSE:      Count the words in all sources.
        
        """
        wordCount = {}
        for source in self.sources:
            sourceData = self.ProcessSource(source)
            for (k, v) in sourceData.items():
                if (k not in wordCount):
                    wordCount[k] = 0
                wordCount[k] += v
        return wordCount

    def ProcessSource(self, source):
        return source.GetWords(self.config)
    
    def MakeRankedResultList(self, numWords):
        if (not len(self.wordCount)):
            self.wordCount = self.CountWords()

        total = float(sum(self.wordCount.values()))
        sortedCounts = list(reversed(sorted(
            self.wordCount.items(), key=lambda pair:pair[1])))

        result = ['Word'.ljust(33) + 'hits'.ljust(13) + '%'.ljust(10)]
        result.extend(
            [word.ljust(33) + ('%i'%count).ljust(13) +
             ('%.5f%%'%(count/total*100.0))
             for (word, count) in sortedCounts[0:numWords]])
        
        return '\n'.join(result)

    def MakeFog(self):
        outputFile = self.config.session.outputFile
        result = self.MakeRankedResultList(self.config.session.maxWords)
        if (outputFile in ['', 'None', None]):
            print result
        else:
            open(outputFile,'w').write(result)
        
        
    @staticmethod
    def _regr_test_simple():
        """Simple regression test for FogMachine.

>>> import os, shutil, tempfile, inspect
>>> import fogMaker, fogConfig
>>> import logging; logging.getLogger('').setLevel(logging.DEBUG)
>>> myDir = tempfile.mkdtemp(suffix='_fogTest')
>>> fd, outFile = tempfile.mkstemp(dir=myDir,suffix='_output.txt')
>>> os.close(fd)
>>> fd, confFile = tempfile.mkstemp(dir=myDir,suffix='_fogConf.txt')
>>> _ignore = os.write(fd, '''
... logLevel=DEBUG
... maxWords=3
... ''')
>>> os.close(fd)
>>> fd, sourceFile = tempfile.mkstemp(dir=myDir,suffix='_sourceData.txt')
>>> _ignore = os.write(fd, inspect.getsource(fogConfig))
>>> os.close(fd)
>>> myConf = fogConfig.FoggerConfig(configFile=confFile)
>>> myConf.Validate()
>>> maker = fogMaker.FogMachine(myConf)
>>> maker.AddSource(fogMaker.FileSource(sourceFile))
>>> maker.AddSource(fogMaker.WebSource(
... 'http://code.google.com/p/superpy/people/list'))
>>> maker.MakeFog()
Word                             hits         %         
to                               35           2.60417%
for                              29           2.15774%
in                               26           1.93452%
>>> logging.warning('FIXME: need to make special web page for above test')
>>> shutil.rmtree(myDir)
>>> os.path.exists(myDir)
False
        """


def _test():
    "Test docstrings"
    import doctest
    doctest.testmod()

if __name__ == "__main__":    
    _test()
    print 'Test finished.'
            
