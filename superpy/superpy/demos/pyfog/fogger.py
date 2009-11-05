"""Module to run fog maker.
"""

import os, logging
from superpy.demos.pyfog import fogConfig, fogMaker

def Run(args=None):
    """Run main fog maker.
    
    INPUTS:
    
    -- args=None:        List of options to pass to automatic option parser.
                         If this is None, sys.argv will be used.
    
    -------------------------------------------------------
    
    PURPOSE:    Runs main fog maker.
    
    """
    conf = fogConfig.FoggerConfig(args)
    conf.Validate()
    logging.getLogger('').setLevel(getattr(logging,conf.session.logLevel))
    logging.info('Starting fogger.\n\tworking dir = %s\n' % os.getcwd())
    maker = fogMaker.FogMachine(conf)
    maker.MakeFog()
    
if __name__ == '__main__':
    Run()
