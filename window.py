

from    debug       import  *

import  pygame

import  events

import  random



class Window:
    
    def __init__( self, caption ):

        pygame.init()
        self.size = 600,450     # Size of window for Y-coordinate reorientation
        self.window = pygame.display.set_mode( self.size, pygame.RESIZABLE )
        
        self.caption = caption
        pygame.display.set_caption( caption )
        
        #self.font = pygame.font.SysFont( pygame.font.get_default_font(), 16 )
        #self.font = pygame.font.SysFont( 'system', 20 )   
        self.font = pygame.font.SysFont( 'lucidaconsole', 11 )
        #self.font = pygame.font.SysFont( 'couriernew', 14 )

        self.surface = None     # Draw to other Surface, not self.window
        
       
        # Invalidation
        self.onpaint = {}
        self.onpaint['event'] = pygame.event.Event( events.ONPAINTEVENT )
        self.onpaint['sent']  = False
        #self.onpaint = {'event':pygame.event.Event( events.ONPAINTEVENT ), 'sent':False}
        
        
        
        
    def __del__( self ):
        #print "quit", self
        pygame.quit()




    def run( self ):
        while True:
            for event in pygame.event.get():
                self.input( event )
                if pygame.QUIT == event.type:
                    return


    def getSurface( self ):
        return  self.surface or self.window


    def invalidate( self ):
        "Set Event to redraw window"
        if not self.onpaint['sent']:
            self.addEvent( self.onpaint['event'] )
            self.onpaint['sent'] = True


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
            print "Error: circle radius < 1"
            return            
        col = self.getColor( col )
        pygame.draw.circle( self.getSurface(), col, pos, r, width )

    def line( self, p0,p1, col=None ):
        col = self.getColor( col )
        pygame.draw.line( self.getSurface(), col, p0,p1 )

    def polygon( self, ps, col=None ):
        if len(ps) < 2:
            print "Error: polygon points < 2"
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
        text = self.font.render( str, False, col )      # "pygame.error: Text has zero width"
        self.getSurface().blit( text, pos )

    
    def paint( self ):
        "Use invalidate() for call this event"
        pass


    def setCursor( self, cursor= None ):
        cursor = cursor or pygame.cursors.arrow
        pygame.mouse.set_cursor( *cursor )


    def input( self, event ):
        "Process standart events"
        if pygame.VIDEORESIZE == event.type:
            self.size = event.size
            self.window = pygame.display.set_mode( self.size, pygame.RESIZABLE )
            self.paint()

        elif events.ONPAINTEVENT == event.type:
            self.paint()
            self.onpaint['sent'] = False

    
    def consoleInput( self, text ):
        
        block = pygame.KEYDOWN, pygame.KEYUP

        pygame.event.set_blocked( block )
        pygame.display.set_caption( 'Console Mode' )

        input = raw_input( text )

        pygame.display.set_caption( self.caption )
        pygame.event.set_allowed( block )
        
        return input

        

    def addEvent( self, event ):
        pygame.event.post( event )
        debug( 'event', 'event added', event )

    def addUserEvent( self, type, **dict ):
        event = pygame.event.Event( type, **dict )
        pygame.event.post( event )
        debug( 'event', 'userevent added', event )



    #def block( self, block ):
    #    pygame.event.set_blocked( block )
        