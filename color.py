
import  colorsys
import  math
import  pygame

from    debug       import  *

from    events      import  *




# Normalization method, so the colors are in the range [0,1]
def normalize( color ):
    return color[0] / 255.0,  \
           color[1] / 255.0,  \
           color[2] / 255.0


# Reformats a color tuple, that uses the range [0,1] to a 0xFF
# representation.
def reformat( color ):
    return int( round( color[0] * 255 ) ),  \
           int( round( color[1] * 255 ) ),  \
           int( round( color[2] * 255 ) )



def logSequence( n ):
    """
    Returns values in range 0..1.
    Distances between values are maximal.
    """
    return math.log( 2*n+1, 2 )  %  1


class ColorValue:
    
    def __init__( self, group ):
        self.group = group
        self.value = group.next()       # Value of Color: 0..1
        
        self.rgb = ()                   # Calculated RGB color

        
    def color( self ):
        "Return color"
        if not self.rgb:
            saturation = 0.6                # Saturation is constant
            self.rgb = reformat( colorsys.hsv_to_rgb( self.group.hue, saturation, self.value ) )
        return self.rgb



class ColorGroup:

    
    def __init__( self ):

        self.hue   = 0      # Hue of Color: 0..1

        self.count = 0      # Counter of Variables
            

    
    def next( self ):
        "Get next color value for ColorValue object"
        #step = ( 5 ** .5 - 1 ) * .5        # Step of values
        min  = 0.5                         # Minimal value

        #val = ( self.count * step  %  1 )  *(1-min)+min
        val = logSequence( self.count )  *(1-min)+min

        self.count += 1
        
        return val
        

class ColorSpace:
    
    def __init__( self, expression= None ):
        
        self.vars   = {}    # Dict {var:ColorValue}
        self.groups = []    # Color Groups

        if expression:  
            self.add( expression )
            


    def add( self, expression, groups= None ):
        "Add Variables of Expression to Space"

        if not groups:
            # Get groups of Variables by Expression
            vars, groups = expression.getClosed()
            if vars:
                groups[0] += list( vars )       # Add Free vars to last Group
            
        debug('color','init color groups:',groups)

        # Create groups and vars collections
        map( self.addGroup, groups )
        


    def addGroup( self, vars ):
        "Adds Group into Color Space"
        
        group = None
        
        for var in vars:
            if var not in self.vars:                    # Var may be already in Space (at Deref)
                
                if not group:                           # Create Group once if needed
                    n = len( self.groups )
                    group = ColorGroup()
                    group.hue = logSequence( n )        # Det Hue of Group
                    self.groups.append( group )
                    
                self.vars[ var ] = ColorValue( group )  # Fill dict {var:ColorValue}



    def color( self, var ):

        if 0 == var:                # Free Variable
            return 0xFF,0xFF,0xFF

        elif None == var:             # Constant
            return 0xFF,0xFF,0x7F

        elif var in self.vars:
            return self.vars[ var ].color()

        else:
            debug( 1, 'Error. Color of Unknow Variable' )
            return 0xFF,0x00,0x00
        
        
        

class ColorChange:
    "It may be used for smooth changing of colors at figure rebuilding.."
    # Not implemented

    def __init__( self ):
        #self.event  = pygame.event.Event( COLOREVENT, handler= self.handler,  \
        #                                              timefunc= None,  \
        #                                              cur_hsv= None )
        pass

        
    def handler( self, event ):
        
        if event != self.event:
            debug( 'event', 'Error? ColorValue wrong event.' )
            return
        
        return
        yield self.event
        
        