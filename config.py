

import sys, os
import configparser

#-----------------------------------------------
# Platform

#!!! Testing web mode locally
#   Use http://127.0.0.1:8000/
#   To debug: uncomment debug_hidden = false in *html.tmpl

FORCE_WEB_PLATFORM = 0

IS_WEB_PLATFORM = FORCE_WEB_PLATFORM or sys.platform == 'emscripten'

ALLOW_SYSTEM_CONSOLE = not IS_WEB_PLATFORM

ALLOW_FILE_WRITING = not IS_WEB_PLATFORM


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
        parser.read_file( f )

        # Get Configuration dict
        cfg = dict( parser.items('Visual Lambda') )

        f.close()


def get( key, default= None ):
    
    if cfg is None:     # Read config.cfg once
        readCfg()
    
    return cfg.get(key, default)
