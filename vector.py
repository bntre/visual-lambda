
# http://gflanagan.net/site/python/sci/2dvector.html

import copy
import math
import operator as op


def is_numeric( obj ):
    return isinstance( obj, (int, float) )



class Vector( object ):
    
    def __init__( self, arg ):
        if is_numeric( arg ):
            self.vector = [ 0 ] * arg
        else:
            self.vector = list( arg )


    def __repr__( self ):
        return 'Vector([%s])' % ','.join( map( repr, self ) )


    def __setitem__( self, index, value ):
        self.vector[ index ] = value

    def __getitem__( self, index ):
        return self.vector[ index ]

    def __iter__( self ):
        return self.vector.__iter__()
    
    def __len__( self ):
        return self.vector.__len__()


    def __add__( a, b ):
        return a.__class__( map( op.add, a, b ) )

    def __sub__( a, b ):
        return a.__class__( map( op.sub, a, b ) )

    def __neg__( a ):
        return a.__class__( map( op.neg, a ) )

    def __mul__( a, b ):
        if is_numeric( b ):
            b = [b] * len(a)
        return a.__class__(  map( op.mul, a, b ) )


    #def __rmul__( a, k ):
    #    return a.__mul__( k )

    def __truediv__( a, k ):
        return a.__mul__( 1.0/k )

    def __abs__( a ):
        return a.length()
    

    def dot( a, b ):
        return sum( a.__mul__(b) )

    def length( a ):
        return math.sqrt( a.dot(a) )

    def unit( a, length=None ):
        if None == length:
            length = a.length()
        if length:
            return a / length
        else:
            v = a.__class__( len(a) )
            v[0] = 1.0
            return v

    def dist( a, b ):   # bntr
        return ( b - a ).length()




class Vector2( Vector ):

    def __init__( self, *args, **dict ):
        
        self.vector = [0,0]
        
        if 'cos' in dict:
            # Create Unit-vector by x coordinate
            cos = dict['cos']
            if 1 < abs( cos ):
                Vector.__init__( self, 2 )
            else:
                Vector.__init__( self, ( cos, math.sqrt( 1.0 - cos*cos ) ) )
        
        elif 'angle' in dict:
            # Create Unit-vector of angle
            angle = dict['angle']
            Vector.__init__( self, ( math.cos(angle), math.sin(angle) ) )

        
        elif args:
            
            if type( args[0] ) is complex:
                Vector.__init__( self, ( args[0].real, args[0].imag ) )
            
            elif args[1:]:      # ??
                a,b = args
                Vector.__init__( self, ( b[0]-a[0], b[1]-a[1] ) )
                            
            else:
                Vector.__init__( self, *args )
       
        else:
            print(args, dict)
            raise Exception("wrong constructor")


    def __repr__( self ):
        return 'Vector2((%s,%s))' % tuple( self )


    def __getattr__( self, name ):
        alias = { 'x':0, 'y':1 }
        if name in alias:
            return self.vector[ alias[ name ] ]
        else:
            raise AttributeError(name)

    def __setattr__( self, name, value ):
        alias = { 'x':0, 'y':1 }
        if name in alias:
            self.vector[ alias[ name ] ] = value
        else:
            self.__dict__[ name ] = value
 

    def cross( a, b ):
        return a.x * b.y - a.y * b.x

    def conjugate( a ):
        return Vector2(( a.x, -a.y ))
                                        #        ^ result
    def perpendicular( a ):             # self   | 
        return Vector2(( -a.y, a.x ))   #   ---->|

    def rotate( a, b ):
        return Vector2(( a.x * b.x - a.y * b.y,  \
                         a.x * b.y + a.y * b.x ))
    
    #def projection( self, vector ):
    #    k = (self.dot(vector)) / vector.length()
    #    return k * vector.unit()


    def atan2( a ):
        return math.atan2( a.y, a.x )

    def degrees( a ):
        return a.atan2() * 180 / math.pi
        
    def between( c, a, b ):
        """Detect if self is between a and b anticlockwise.
        self, a, b must be unit-vectors"""
        # Return riple product of a, self, b  with 1 as z-coordinates
        return 0 < a.x * c.y - a.x * b.y +  \
                   b.x * a.y - c.x * a.y +  \
                   c.x * b.y - b.x * c.y

    def angle( self, origin=None, positive=False ):
        "Returns 0..2pi - angle of vector v0  or between vectors v1 and v0"
        if origin:
            self = self.rotate( origin.conjugate() )
        a = self.atan2()
        if positive and a < 0:
            a += 2 * math.pi
        return a

    def complex( self ):
        #print("complex", self)
        return complex( *self.vector )
        
        