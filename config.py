

import sys, os
import ConfigParser


cfgFileName = 'config.cfg'

# Configuration dict
cfg = None


def readCfg():

    global cfg, cfgName

    scriptpath = sys.argv[0]

    # Get full path of Read config.cfg
    path = os.path.join( os.path.dirname( scriptpath ), cfgFileName )
    
    parser = ConfigParser.ConfigParser()
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
    
    global cfg
    
    if cfg is None:     # Read config.cfg once
        readCfg()
    
    return  key in cfg  and  cfg[ key ]  or  default

