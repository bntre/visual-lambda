

import sys, os
import configparser

#-----------------------------------------------
# Platform

IS_WEB_PLATFORM = sys.platform == 'emscripten'
#IS_WEB_PLATFORM = True  # to test web mode

ALLOW_SYSTEM_CONSOLE = not IS_WEB_PLATFORM


#-----------------------------------------------
# Config file

cfgFileName = 'config.cfg'

# Configuration dict
cfg = None


def readCfg():

    global cfg

    scriptpath = sys.argv[0]

    # Get full path of Read config.cfg
    path = os.path.join( os.path.dirname( scriptpath ), cfgFileName )
    
    parser = configparser.ConfigParser()
    try:
        f = open( path )
    except IOError:
        cfg = {}

    else:
        # Read config.cfg
        parser.readfp( f )

        # Get Configuration dict
        cfg = dict( parser.items('Visual Lambda') )

        f.close()


def get( key, default= None ):
    
    if cfg is None:     # Read config.cfg once
        readCfg()
    
    return cfg.get(key, default)
