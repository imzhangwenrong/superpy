"""Module containing configuration information for superpy.

This module should define the following configuration variables:

  smtpServer:      String name of smtp server to use when sending mail.
  serviceLogFile:  String path to location for superpy server log file.
  defaultLogLevel: Log level to use when starting server.
  
"""

import logging

smtpServer = 'FIXME'

# Location that superpy service will use for its logging
serviceLogFile = 'c:/temp/superpy_log.txt'

# Default log level
defaultLogLevel = logging.DEBUG 
