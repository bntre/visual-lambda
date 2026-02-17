

import  pygame
import  time


#TIMEREVENT      = pygame.USEREVENT + 0
#DELAY = 60


#EATINGEVENT     = pygame.USEREVENT + 1


#COLOREVENT      = pygame.USEREVENT + 2


ENDURINGEVENT   = pygame.USEREVENT + 3


ONPAINTEVENT    = pygame.USEREVENT + 4


SYSTEMCONSOLE_TIMEREVENT = pygame.USEREVENT + 5


class Enduring:      # ?? move class to another module
    """
    Enduring Event.
    Traces the relative changing of values from 0.0 to 1.0
    according to functions 'funcs'
    in time 'sec' of enduring event
    """

    # Exporting bitmap frames for Animation
    exportMode      = False
    exportModeStep  = 0.1
    exportModeFrame = 0
    

    @staticmethod
    def I( x ):     # simpliest, here must be curves too
        return x
    
    
    def __init__( self, sec, funcs ):
        self.sec   = sec
        self.begin = None   # Begin time
        self.cur   = 0.0    # 0..1  Position of process
        self.end   = False
        self.funcs = [  { 'name':name, \
                          'func':func, \
                          'prevval':func(0) }  \
                              for name,func in funcs.items()  ]
        
        # Create pygame event   
        self.event = pygame.event.Event( ENDURINGEVENT, {'data':self} )


    def start( self ):
        self.begin = time.time()
        return self.event
        

    def timefuncs( self ):

        if Enduring.exportMode:
            self.cur += Enduring.exportModeStep
        else:
            self.cur = ( time.time() - self.begin ) / self.sec


        if self.cur >= 1.0:
            self.cur = 1
            self.end = True                 # End of changing of values

        def getK( func ):
            curval  = func['func']( self.cur )
            prevval = func['prevval']
            func['prevval'] = curval        # Change prevval to current
            
            # Return pair ( current value, part of remained way for step )
            return  func['name'],  ( curval,  (curval - prevval) / (1.0 - prevval) )

        return dict( map( getK, self.funcs ) )

    
    
        