

from    debug       import  *

import  copy

import  let

import  config



class Library:

    def __init__( self ):
        
        self.dict = {}
        
        self.numbers = True     # Simulate numbers in library
        
        
    
    def __setitem__( self, key, value ):
        self.dict[ key ] = isinstance( value, let.Expression )  \
                               and value  \
                               or  self.parser.parse( value )

    def __getitem__( self, key ):

        if key in self.dict:
            #return copy.deepcopy( self.dict[ key ] )
            debug( 4, 'library. asked', key, self.dict[ key ] )
            return self.dict[ key ].copy( ({},{}) )

        elif self.numbers and key.isdigit():
            return self.number( int( key ) )

        else:
            raise KeyError(key)

        
    def __iter__( self ):
        return self.dict.__iter__()


    
    def init( self, parser ):
    
        self.parser = parser
        
        def getDefs( lines, spaces ):

            def strip( s ):
                return s.strip( spaces )
            
            while lines:
                line = strip( lines.pop(0) )
                
                while  lines  and  lines[0]  and  lines[0][0] in spaces:
                    next = strip( lines.pop(0) )
                    if next: line += ' ' + next
                
                if line and not '#'==line[0]:
                    yield list(map( strip, line.split('=',1) ))
            
        

        # Read library from txt
        txt = config.get( 'library', 'library.txt' )
        try:
            f = open( txt )
        except IOError:
            print("Warning: no library found", txt)
        else:
            lines = f.readlines()
            f.close()
        
            for d in getDefs( lines, ' \t\n\r' ):
                self[ d[0] ] = d[1]       # Add synonym to Library
        
            

    def number( self, n ):
        "Generates Number Expression"
        
        lf = let.Abstraction( expr= None )
        lx = let.Abstraction( expr= None )
        
        x = let.Variable( lx )

        for _ in range( n ):            
            f = let.Variable( lf )
            x = let.Application( func= f, arg= x )

        lx.expr = x
        lf.expr = lx

        return lf
        