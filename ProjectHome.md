Superpy distributes python programs across a cluster of machines or across multiple processors on a single machine. This is a coarse-grained form of parallelism in the sense that remote tasks generally run in separate processes and do not share memory with the caller.

Key features of superpy include:

  * Send tasks to remote servers or to same machine via XML RPC call
  * GUI to launch, monitor, and kill remote tasks
  * GUI can automatically launch tasks every day, hour, etc.
  * Works on the Microsoft Windows operating system
    * Can run as a windows service
    * Jobs submitted to windows can run as submitting user or as service user
  * Inputs/outputs are python objects via python pickle
  * Pure python implementation
  * Supports simple load-balancing to send tasks to best servers

The ultimate vision for superpy is that you:
  1. Install it as an always on service on a cloud of machines
  1. Use the superpy scheduler to easily send python jobs into the cloud as needed
  1. Use the `SuperWatch` GUI to track progress, kill tasks, etc.

For smaller deployments, you can use superpy to take advantage of multiple processors on a single machine or multiple machines to maximize computing power.

What makes superpy different than the many other excellent parallel
processing packages already available for python? The superpy package
is designed to allow sending jobs across a large number of machines
(both Windows and LINUX). This requires the ability to monitor, debug,
and otherwise get information about the status of jobs.

While superpy is currently used in production for a number of different purposes, there are still many features we want to add. For a list of future plans and opportunities to help out or add to the discussion, please visit http://code.google.com/p/superpy/wiki/HelpImproveSuperpy.

For a quick example of some of the the things superpy can do, check out http://code.google.com/p/superpy/wiki/Demos or in particular the demo application PyFog at http://code.google.com/p/superpy/wiki/PyFog.

To install, you can use [easy\_install](http://peak.telecommunity.com/DevCenter/EasyInstall) to try superpy via "easy\_install superpy" or download a python egg from [downloads](http://code.google.com/p/superpy/downloads). Of course, you will need python installed and if you are using windows, you should also install the python windows tools from http://sourceforge.net/projects/pywin32/files. See http://code.google.com/p/superpy/wiki/InstallFAQ if you have more questions about installation.