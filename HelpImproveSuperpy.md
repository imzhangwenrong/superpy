# Introduction #

While superpy is currently being used in production, there are still many ways to improve it. This page discusses areas where help is needed.

# Security #

Superpy currently has a small level of security suitable for in house use behind a firewall. It could benefit a lot from improving the security to be more robust. Since superpy is written in python, the main issues are not necessarily buffer overflows but designing a better security model for client/server operation.

# LINUX/Windows Integration #

Superpy currently works on both windows and LINUX, but the security model is somewhat different. On Windows, superpy supports spawning a job on a remote machine and having the remote job change user to the desired user. This is not yet supported on LINUX. It would be great to be able to change the remote user on LINUX.

# Python API for Supercomputing #

One of the original motivations of superpy was to have a relatively lightweight python API to allow super-computing or cloud computing. While we think superpy has a good API, it could certainly be better. The ideal would be to have a clear, simple API similar to python's DB-API for databases. Such an API would allow different modules to implement super-computing, cloud-computing, etc. in different ways but still allow users to program to a single API.

# More Demos #

Superpy currently has a few demos as discussed at http://code.google.com/p/superpy/wiki/Demos, but we could always user more.