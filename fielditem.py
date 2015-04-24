
from    debug       import  *

from    vector      import  *
from    matrix      import  TransformMatrix



class FieldItem:
    
    def __init__( self ):

        # Position of Element on Field
        self.position  = TransformMatrix()
        self.position.setTranspose( 0,0, 1 )    # Default Position

        self.transform = None

    def refreshTransform( self ):
        pass


class TextItem( FieldItem ):
    
    def __init__( self, text ):
        
        FieldItem.__init__( self )        
        self.refreshTransform()
        
        self.text = text
        
        self.fontsize = 14
        
    def copy( self ):
        copy = TextItem( self.text )

        copy.position = self.position.copy()
        copy.refreshTransform()

        return copy


    def refreshTransform( self ):
        self.transform = self.position


    def pick( self, font, matrix, pos ):
        
        vector = matrix * Vector((0,0,1,1))
        x,y,s,_ = vector
        
        sx,sy = font.size( self.text )
        
        return x < pos.x < x+sx and  \
               y < pos.y < y+sy
            
        
        
        
        
        