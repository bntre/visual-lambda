
import  copy

from    vector  import  *


class Matrix:
    
    def __init__( self, rows, cols, matrix=None ):
        self.rows = rows
        self.cols = cols
        self.matrix = matrix  or  [ [0] * cols  for _ in range(rows) ]

    def copy( self ):
        return copy.deepcopy( self )

    def unit( self ):
        for r in range( self.rows ):
         for c in range( self.cols ):
            self.matrix[r][c] = int( r == c )

    def __repr__( self ):
        return `self.matrix`

    def __getitem__( self, index ):
        return self.matrix[ index ]

    def __setitem__( self, index, value ):
        self.matrix[ index ] = value


    def __mul__( a, b ):
    
        if isinstance( b, Vector ):
            assert a.cols == len(b)
            mult = Vector( a.rows )
            for r in range( a.rows ):
               m = 0
               for i in range( a.cols ):
                   m += a[r][i] * b[i]
               mult[r] = m
            return mult

        elif isinstance( b, Matrix ):
            assert a.cols == b.rows
            mult = Matrix( a.rows, b.cols )
            for r in range( a.rows ):
             for c in range( b.cols ):
                m = 0
                for i in range( a.cols ):
                    m += a[r][i] * b[i][c]
                mult[r][c] = m
            return mult
            
        else:
            for r in range( a.rows ):
             for c in range( a.cols ):
                a[r][c] *= b
            




class InversibleMatrix( Matrix ):

    def __init__( self, rows, matrix=None, inversion=None ):
        Matrix.__init__( self, rows, rows, matrix )
        self.inversion = inversion or Matrix( rows, rows )    # Save Inversion Matrix
    

    def inverse( self ):
        return InversibleMatrix( self.rows, self.inversion, self )


    def __mul__( a, b ):
        
        res = Matrix.__mul__( a, b )
        
        if isinstance( b, Vector ):
            return res
            
        elif isinstance( b, InversibleMatrix ):
            inversion = Matrix.__mul__( b.inversion, a.inversion )
            return InversibleMatrix( res.rows, res.matrix, inversion )

        elif isinstance( b, Matrix ):
            return res
        
        else:
            raise "Not implemented"


    


class TransformMatrix( InversibleMatrix ):
    "Especially for Ring as Vector"
    
    def __init__( self, **dict ):
    
        InversibleMatrix.__init__( self, 4 )
        
        if 'ring' in dict:
            ring = dict['ring']
            self.setTranspose( ring.pos.x, ring.pos.y, ring.r )


    def setTranspose( self, cx, cy, k ):
        
        def set( m ):
            m.unit()
            m[0][3] = cx
            m[1][3] = cy
            m[0][0] = k
            m[1][1] = k
            m[2][2] = k

        set( self )

        k **= -1
        cx *= -k
        cy *= -k
        set( self.inversion )
        


    def setReflection( self ):
        
        def set( m ):
            m.unit()
            m[1][1] = -1

        set( self )
        set( self.inversion )



    def setRotate( self, dir ):
        
        if not isinstance( dir, Vector2 ):
            dir = Vector2( angle= dir )
        
        def set( m ):
            m.unit()
            m[0][0] =  dir.x
            m[0][1] = -dir.y
            m[1][0] =  dir.y
            m[1][1] =  dir.x

        set( self )

        dir = dir.conjugate()
        set( self.inversion )


    def setExpand( self, k ):
        
        def set( m ):
            m.unit()
            m[2][2] = k

        set( self )

        k **= -1
        set( self.inversion )
