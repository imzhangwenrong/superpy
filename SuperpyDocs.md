

# Introduction #

This document outlines how to use superpy.

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

You can use [easy\_install](http://peak.telecommunity.com/DevCenter/EasyInstall) to try superpy via "easy\_install superpy" or download a python egg from [downloads](http://code.google.com/p/superpy/downloads).

# Quick Start and Example Usage #

You can find a simple example of how to use superpy in the main docstring for superpy. For example, doing
```
>>> import superpy
>>> print superpy.__doc__
```
should show you the following example usage:
```
The superpy module provides super-computing for python.

The superpy package allows you to distribute python programs across a
cluster of machines or across multiple processers on a single
machine. This is a coarse-grained form of parallelism in the sense
that remote tasks generally run in separate processes and do not share
memory with the caller.

What makes superpy different than the many other excellent parallel
processing packages already available for python? The superpy package
is designed to allow sending jobs across a large number of machines
(both Windows and LINUX). This requires the ability to monitor, debug,
and otherwise get information about the status of jobs. Such job
control features (and Windows support) was not widely available in
other packages at the time superpy was created.

Some key features of superpy include:

 * Send tasks to remote servers or to same machine via XML RPC call
 * GUI to launch, monitor, and kill remote tasks
   * GUI can automatically launch tasks every day, hour, etc.
 * Works on the Microsoft Windows operating system
   * Can run as a windows service
   * Jobs submitted to windows can run as submitting user or as service
 * Inputs/outputs are python objects via python pickle
 * Pure python implementation
 * Supports simple load-balancing to send tasks to best servers 

The following provides a simple example to show how superpy can be
used in practice.

   First you would generally use the Spawn script on various machines to
   spawn superpy servers. Better yet would be to setup a windows
   service or similar script to make superpy spawn servers
   automatically. To illustrate this in a doctest, we import the
   Spawn script and call the SpawnServer function directly to setup
   a few servers. (Note that usually you would only do this once or
   not even have to do it at all if your servers start automatically
   as services).
   

>>> from superpy.scripts import Spawn
>>> print '1:'; server1 = Spawn.SpawnServer(0, daemon=True) #doctest: +ELLIPSIS
1:
Entering service loop forever or until killed...
>>> print '2:'; server2 = Spawn.SpawnServer(0, daemon=True) #doctest: +ELLIPSIS
2:
Entering service loop forever or until killed...
    
    Next we instantiate an instance of the scheduler class and tell it
    about the servers we have instantiated:

>>> from superpy.core import Servers
>>> myServers = [
... (server1._host,server1._port),(server2._host,server2._port)]
>>> s = Servers.Scheduler(myServers)

    Now we can submit tasks to the servers. The tasks can represent
    pretty much anything you want to do in python. The only real
    constraint is that since we use pickle, the tasks must be
    unpickleable on the remote machine. This basically means that
    tasks must be objects in modules the remote machine can see. For
    this example, we use the example in Process._ExampleForTest, but
    you can easily create your own tasks by simply providing an object
    with a run method.

>>> import os
>>> from superpy.core import Tasks, Process
>>> target = Process._ExampleForTest(  # create an example task with delay
... func=sum,args=[[1,2,3],5],delay=10)# of 10 to illustate timeout
>>> task = Tasks.ImpersonatingTask(
... name='example',targetTask=target,workingDir=os.getcwd())
>>> handle = s.SubmitTaskToBestServer(task)
>>> handle = handle.UpdatedHandle(timeout=3) # Try to quickly get update.
>>> # The above should get a handle showing tasks status as not finished.
>>> print handle # doctest: +ELLIPSIS
TaskHandle(
    name='example',
    started=True,
    finished=False,
    alive=True,
    host='...',
    port=...,
    result=None,
    starttime=datetime.datetime(...),
    endtime=None,
    user='...',
    taskRepr="ImpersonatingTask(...)",
    pids=[...])
<BLANKLINE>
>>> handle = handle.WaitForUpdatedHandle(60) # wait for task to finish
>>> print handle.result # show result
11
>>> handle.Cleanup() # cleans task out of server queue
```

# Superpy as a windows service #

An important feature of superpy is that it can run as a windows service. This means that superpy will always run in the background, get restarted when the machine reboots, and generally be available all the time to process requests. To install superpy as a service, start a command window (i.e., a DOS prompt), enter the Scripts directory of your python install (this is in c:/Python25/Scripts for me but may be different on your machine) and do the following:
```
C:\Python25\Scripts> SpawnAsService --start auto install
C:\Python25\Scripts> SpawnAsService restart
```

If desired, you can type `SpawnAsService.py --help` or use the Windows GUI to go to `Start-->Settings-->Control Panel-->Administrative Tools-->Services` and click on the superpy service to change the service parameters.

Once you have superpy running as a service on a given machine, you can just send tasks to it without having to worry about spawning the server.

Note: you will need the python windows extensions installed to use superpy on windows. See [the install faq](http://code.google.com/p/superpy/wiki/InstallFAQ#Do_I_need_to_do_anything_special_on_windows?) for details.

# Make Sure Privileges Assigned Properly (On XP) #

On certain versions of windows, superpy's ability to run a process as the submitting user requires you to assign certain rights to the user running superpy. If you get errors about required privileges for running `CreateProcessAsUser` (e.g., "A required privilege is not held by the client") then you need to do the following. To assign user rights to an account on the local computer do:

  1. From the Start Menu click on Settings-->Control Panel, select Administrative Tools, and then click Local Security Policy.
  1. In the Local Security Settings dialog box, double-click Local Policies, and then double-click User Rights Assignment.
  1. In the details pane, double-click Adjust memory quotas for a process. This is the SE\_INCREASE\_QUOTA\_NAME user right.
  1. Click Add User or Group, and, in the Enter the object names to select box, type the user or group name to which you want to assign the user right, and then click OK. Generally, you should add the user that will be running superpy as a service.
  1. Click OK again, and then, in the details pane, double-click Replace a process level token. This is the SE\_ASSIGNPRIMARYTOKEN\_NAME user right.
  1. Click Add User or Group, and, in the Enter the object names to select box, type the user or group name to which you want to assign the user right, and then click OK. Generally, you should add the user that will be running superpy as a service.
# Make Sure Privileges Assigned Properly (On Windows 7) #
  1. If run in Windows 7, the names in local security policy for which you need to assign privilege should be 'Adjust memory quotas for a process' and 'Replace a process level token'
  1. You need to set Control Panel\System and Security\Action Center\User Account Control Setting to 'Never notify'. Otherwise you may still get the same error.



# Detailed Documentation #

Coming soon.