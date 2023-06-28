r"""
The Parser owns (and initializes) the Library object.
"""

from    debug       import  *

import  copy

import  let

import  config


def strip( expr ):
    return expr.strip(' \t\n\r')


class Library:

    def __init__( self, parser ):
        self.parser = parser

        self.globalItems = {}  # loaded from (e.g.) "library.txt" always available
        self.localItems  = {}  # loaded from workspace; reset on workspace reload

        self.generateNumbers = True     # Generate numbers by demand
    
    
    def add_item( self, key, value, isGlobal = True ):
        if not isinstance( value, let.Expression ):
            value = self.parser.parse( value )
        if isGlobal:
            self.globalItems[ key ] = value
        else:
            self.localItems[ key ] = value


    def reset_local_items( self ):
        self.localItems  = {}


    def add_line( self, line, isGlobal = True ):
        line = strip(line)
        if not line or line[0] == '#': return False
        if '=' not in line: return False
        key, value = tuple(map( strip, line.split('=', 1) ))
        self.add_item( key, value, isGlobal )
    
        
    def init( self ):
        # Read library from txt
        libraryFile = config.get( 'library', 'library.txt' )
        try:
            f = open( libraryFile, 'r' )
        except IOError:
            print("Warning: can't open library file", libraryFile)
            return
        else:
            lines = f.readlines()
            f.close()
        
            for line in lines:
                self.add_line( line, isGlobal = True )
        

    def find_item( self, key ):
        value = self.localItems.get( key ) or  \
                self.globalItems.get( key )
        if value:
            debug( 4, 'library. asked', key, value )
            return value.copy( ({},{}) )

        elif self.generateNumbers and key.isdigit():
            return self.generate_number( int( key ) )

        else:
            return None
    
    
    def generate_number( self, n ):
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
        