
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
        
        x,y,_,_ = matrix * Vector((0,0,1,1))
        
        sx,sy = font.size( self.text )
        
        return x < pos.x < x+sx and  \
               y < pos.y < y+sy




class RectItem( FieldItem ):

    def __init__( self, size, color ):
        
        FieldItem.__init__( self )
        self.refreshTransform()

        self.size = size  # tuple
        self.color: str = color

    def copy( self ):
        copy = RectItem( self.size, self.color )

        copy.position = self.position.copy()
        copy.refreshTransform()

        return copy

    def refreshTransform( self ):
        self.transform = self.position

    def pick( self, matrix, pos ):
        
        x,y,s,_ = matrix * Vector((0,0,1,1))
        
        sx,sy = self.size
        
        return x < pos.x < x+sx*s and  \
               y < pos.y < y+sy*s
