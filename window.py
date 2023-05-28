
import  pygame

from    debug       import  *
import  events
import  config

if config.ALLOW_SYSTEM_CONSOLE:
  import  console


class Window:
    
    def __init__( self, caption, size ):

        pygame.init()
        self.size = size     # tuple, size of window in pixels
        pygame.display.set_mode( self.size, pygame.RESIZABLE )  
        self.window = pygame.display.get_surface()  # main surface
        
        self.caption = caption
        pygame.display.set_caption( caption )
        
        fontsize = int( config.get( 'fontsize' ) )  or  11
        if config.IS_WEB_PLATFORM: 
            fontsize = fontsize * 2  #!!! fixing pygbag
        self.font = pygame.font.SysFont( 'lucidaconsole', fontsize )
        self.fontAntialias = config.IS_WEB_PLATFORM  #!!! fixing pygbag

        self.surface = None     # Draw to other Surface, not self.window
        
        # Invalidation
        self.paintEvent = pygame.event.Event( events.ONPAINTEVENT )
        self.paintEventSent = False
        
        
    def __del__( self ):
        #print("quit", self)
        pygame.quit()



    def getSurface( self ):
        return  self.surface or self.window


    def invalidate( self ):
        "Set Event to redraw window"
        if not self.paintEventSent:
            self.postEvent( self.paintEvent )
            self.paintEventSent = True


    def erase( self, color=(0xFF,0xFF,0xFF), rect=None ):
        rect = rect or pygame.Rect( (0,0), self.size )
        self.getSurface().fill( color, rect )

    def flip( self ):
        pygame.display.flip()

    def getColor( self, col=None ):
        if type( col ) is tuple:
            return col
        if None == col:
            return (0,0,0)
        return [ (255,0,0), (0,0,255), (0,255,0), (200,200,200), (100,100,100), (179,213,200) ][ col ]

    def circle( self, pos, r, col=None, width=1 ):
        if r < 1:
            print("Error: circle radius < 1")
            return            
        col = self.getColor( col )
        pygame.draw.circle( self.getSurface(), col, pos, r, width )

    def line( self, p0,p1, col=None ):
        col = self.getColor( col )
        pygame.draw.line( self.getSurface(), col, p0,p1 )

    def polygon( self, ps, col=None ):
        if len(ps) < 2:
            print("Error: polygon points < 2")
            return
        col = self.getColor( col )
        pygame.draw.polygon( self.getSurface(), col, ps )

    def mark( self, pos ):
        col = (0,127,0)
        x,y = pos
        r = 1
        self.getSurface().fill( col, pygame.Rect(x-r,y-r,r*2,r*2) )

    def text( self, str, pos, col=None ):
        col = self.getColor( col )
        text = self.font.render( str, self.fontAntialias, col )
        self.getSurface().blit( text, pos )

    
    def paint( self ):
        "Override and use invalidate() to initiate it"
        pass


    def setCursor( self, cursor= None ):
        cursor = cursor or pygame.cursors.arrow
        pygame.mouse.set_cursor( *cursor )


    def handleEvent( self, event ):
        "Process standart events"
        if pygame.VIDEORESIZE == event.type:
            if self.size != event.size:
                self.size = event.size
                self.window = pygame.display.set_mode( self.size, pygame.RESIZABLE )
                self.invalidate()

        elif events.ONPAINTEVENT == event.type:
            self.paint()
            self.paintEventSent = False
        

    def postEvent( self, event ):
        pygame.event.post( event )
        debug( 'event', 'event added', event )
    
    
    # Console wrapper
    if config.ALLOW_SYSTEM_CONSOLE:
    
        blockedEvents = (  # Events blocked on console input
            pygame.KEYDOWN, pygame.KEYUP, 
            pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION
        )

        def consoleInput( self, prompt, callback ):
            
            pygame.display.set_caption( 'Console input mode' )
            pygame.event.set_blocked(Window.blockedEvents)
            self.invalidate()
            
            def c( result ):
                pygame.display.set_caption( self.caption )  # Restore default caption
                pygame.event.set_allowed(None)              # Allowing all
                self.invalidate()
                
                callback( result )
            
            console.requestInput( prompt, c )
                
        def consoleCheck( self ):
            console.checkInputs()
    
    def isFrozen( self ):
        return config.ALLOW_SYSTEM_CONSOLE and console.isWaiting()
    
    
