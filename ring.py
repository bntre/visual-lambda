
import  copy

from    debug       import  *
from    common      import  *


from    vector      import  *






class Ring:

    unit = None     # Unit-Ring as constant

    def __init__( self, pos, r ):
        "Create Ring from Positiion and Radius  or  from 4-Vector"
        self.pos = pos and Vector2( pos )
        self.r   = r
        
    def __repr__( self ):
        return 'Ring(%s, %s)' % (repr(self.pos), repr(self.r))
    
    
    def copy( self ):
        return copy.deepcopy( self )
        
        
    def pick( self, pos ):
        "Is Point pos inside Ring?"
        p = Vector2( self.pos, pos )
        d2 = p.dot( p )
        return  d2 < self.r**2


    def mix( self, kpos, kr, a, b ):
        self.pos = mix( kpos, a.pos, b.pos )
        self.r   = mix( kr,   a.r,   b.r )
            

    def vector( self ):
        "Converts Ring Data to 4-Vector for Matrix Transformations"
        return Vector( (self.pos.x, self.pos.y, self.r, 1) )

    def transform( self, matrix ):
        "Transforms Ring by Matrix"
        vec = matrix * self.vector()
        return Ring( (vec[0],vec[1]), vec[2] )






Ring.unit = Ring( (0,0),1 )

