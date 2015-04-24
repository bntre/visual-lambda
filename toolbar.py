

import  pygame

from    common      import  *



# Toolbar Align
LEFT    = 0
RIGHT   = 1
TOP     = 2
BOTTOM  = 3



class ImageSet:
    
    def __init__( self, filename= None, size= (32,32) ):
        
        self.image = None
        self.size  = size

        if filename:
            self.loadImage( filename )

        
    def loadImage( self, filename ):
        self.image = pygame.image.load( filename )
        self.image.set_colorkey( self.image.get_at((0,0)) )
    
    
    def blit( self, surface, dest, key ):
        """
        key - (Int,Int) - key of icon on image
        """
        if self.image:
            i,j   = key
            dx,dy = self.size
            area = pygame.Rect( j*dx, i*dy, dx, dy )
            surface.blit( self.image, dest, area )
    
    



class ToolbarItem:

    
    highlighted = None      # single highlighted ToolbarItem
    
    font        = None
    fontsize    = 0
    
    
    def __init__( self, callback, tip, *args ):

        self.callback = callback
        self.size     = 16,16
        
        self.tip      = tip
        
        self.toggle   = 3==len( args ) and args[2]      # Function of getting toggled value

        # Det States of Item
        # Each Argument is tuple String   or  tuple (ImageSet,i,j)
        # Each State    is       Surface  or  tuple (ImageSet,key)

        self.states   = []

        for arg in args[: self.toggle and 2 or 1 ]:
            
            if type( arg ) is tuple:       # (ImageSet,i,j)
                ims,i,j = arg
                self.size = maxsize( self.size, ims.size )
                self.states.append( (ims,(i,j)) )
                
            else:                       # String
                text = ToolbarItem.font.render( arg, False, (0,0,0) )
                #self.size = text.get_size()
                self.size = maxsize( self.size, ( text.get_size()[0], ToolbarItem.fontsize * 7//5 ) )
                self.states.append( text )



    def draw( self, surface, pos ):
        
        if ToolbarItem.highlighted == self:
            pos = pos[0]-1, pos[1]-1
        
        state = self.states[ self.toggle and bool( self.toggle() ) ]
        
        if type( state ) is tuple:  # (ImageSet,key)
            ims, key = state
            ims.blit( surface, pos, key )
            
        else:                       # Surface
            surface.blit( state, pos )
        


class Toolbar:
    

    dir = { LEFT:1, RIGHT:1, TOP:0, BOTTOM:0 }   # Down,Down,Right,Right

    topmargin  = 30
    sidemargin = 8

    
    def __init__( self, align ):
        self.align  = align
        self.items  = []
        self.length = 0
        self.width  = 0
        

    def add( self, *args ):
        
        item = ToolbarItem( *args )
        self.items.append( item )
        
        dir = Toolbar.dir[ self.align ]
        self.length += item.size[ dir ]
        
        self.width = max( self.width, item.size[ dir^1 ] )



    def getRect( self, size ):
        
        if LEFT == self.align:
            top  = Toolbar.topmargin
            side = Toolbar.sidemargin
            return pygame.Rect( side, top, self.width, self.length )
        
        elif RIGHT == self.align:
            top  = Toolbar.topmargin
            side = size[0] - Toolbar.sidemargin
            return pygame.Rect( side - self.width, top, self.width, self.length )

        elif BOTTOM == self.align:
            side = size[1] - Toolbar.sidemargin
            left = ( size[0] - self.length ) / 2
            return pygame.Rect( left, side - self.width, self.length, self.width )


    def iterItemPoses( self, size ):
        
        if LEFT == self.align:
            top  = Toolbar.topmargin
            side = Toolbar.sidemargin
            for i in self.items:
                yield i, ( side, top )
                top += i.size[1]
        
        elif RIGHT == self.align:
            top  = Toolbar.topmargin
            side = size[0] - Toolbar.sidemargin
            for i in self.items:
                yield i, ( side - i.size[0], top )
                top += i.size[1]

        elif BOTTOM == self.align:
            side = size[1] - Toolbar.sidemargin
            left = ( size[0] - self.length ) / 2
            for i in self.items:
                yield i, ( left, side - i.size[1] )
                left += i.size[0]


        
        
    
    def draw( self, surface, size ):
        
        for item,pos in self.iterItemPoses( size ):
            item.draw( surface, pos )


    def pick( self, cur, size ):

        if self.getRect( size ).collidepoint( cur ):
            for item,pos in self.iterItemPoses( size ):
                if item.callback and  \
                   pos[0] < cur[0] < pos[0] + item.size[0] and  \
                   pos[1] < cur[1] < pos[1] + item.size[1]:
                    return item


