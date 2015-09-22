# Introduction #

PyFog is a simple superpy application to create a cloud (or in this case a fog) of words based on some set of input documents. You can provide lists of web pages, files, or RSS feeds and PyFog will crawl them in parallel, count how often each word or group of words occurs, and display statistics on the most common words.

To use Pyfog, you can just launch the fogGUI.py script from the command line or double click on it. On LINUX, this script should be located in your path (on my system it ends up in /usr/bin/fogGUI.py after you install superpy). On Windows, this usually goes in your scripts directory (e.g., in C:\Python25\Scripts\fogGUI.py). Once you start the fogGUI.py script, you should see a window showing the PyFog parameters:

![http://superpy.googlecode.com/svn/wiki/PyFog.wiki.attach/pyfog.jpg](http://superpy.googlecode.com/svn/wiki/PyFog.wiki.attach/pyfog.jpg)

If you quick on a question mark next to one of the parameters, a window will appear with information about that parameter. Once you have filled in the parameters as you like (or you can just leave the defaults), click OK to run PyFog. If you have started some superpy servers on your local machine and specified these in the serverList, PyFog will then send jobs to the remote machines. Otherwise, it will start a number of local servers to take advantage of the multiple processors on your machine. In any case, it will analyze the given sources and then show the frequency with which they occur as shown below.

![http://superpy.googlecode.com/svn/wiki/PyFog.wiki.attach/pyfog_results.jpg](http://superpy.googlecode.com/svn/wiki/PyFog.wiki.attach/pyfog_results.jpg)

The default RSS example file provided simply scans RSS feeds for various news sources. This gives an interesting snapshot of what the key words for today's news are. Of course, you can provide whatever inputs you like. You could try to give a list of your 100 favorite books (or maybe the current top 100 books on Amazon) and see what are the key words that show up there.

By providing a large number of sources and experimenting with how long PyFog takes with different settings for the `localServers` parameter, you can get a sense of how well superpy exploits multiple processors on your machine. By spawning superpy processes on remote machines (using the Spawn.py or SpawnAsService.py scripts provided with superpy), you can see how much more quickly a cluster of machines can do at analyze word counts. For a task like that you may want to analyze larger sources such as books from Project Gutenberg.