
import  copy

from    debug       import  *
from    common      import  *

from    let         import  *

import  figure

        
        
def addkey( var, key ):
	return (var,) + key

def getkey( key ):
	return key[0], key[1:]



    
class Noke:

    
    def __init__( self, node, key=() ):
        self.node = node
        self.key  = key

    def __repr__( self ):
        return 'Noke( %s, %s )' % ( self.node, self.key )

    def __eq__( self, other ):
        return self.node == other.node and  \
               self.key  == other.key

    def __call__( self ):
        return self.get()

    def __getitem__( self, attr ):
        "Same as self.down( attr )"
        return self.down( attr )



    def set( self, bubble ):
        self.node.fission[ self.key ] = bubble

    def get( self ):
        try:
            return self.node.fission[ self.key ]
        except KeyError: 
            return None

    def remove( self ):
        try:
            del self.node.fission[ self.key ]
        except KeyError: 
            pass


    # Arhive
    
    def archiveKey( self ):
        return addkey( None, self.key )    # Modified key
    
    def save( self ):
        "Saves Bubble to Archive of Noke"
        self.node.fission[ self.archiveKey() ] = self().lightCopy()

    def load( self ):
        "Loads Bubble from Archive of Noke"
        try:
            return self.node.fission[ self.archiveKey() ]
        except KeyError: 
            return None

    def clean( self ):
        "Cleans Archive of Noke"
        try:
            del self.node.fission[ self.archiveKey() ]
        except KeyError: 
            pass




    def down( self, attr ):
        """
        Moves Noke pointer down through Tree.
        For jumping to 'ref' use Noke.ref()
        """
        try:
            node = getattr( self.node, attr )
        except AttributeError:
            raise KeyError()
            
        if VAR == self.node.type and LET == node.type:      # Gone from VAR to LET
            key = addkey( self.node, self.key )
        else:
            key = self.key
            
        return Noke( node,key )     # Create new Noke
        
    
    def ref( self ):
        "Jump up to '.ref' (referenced Let or Abs)"
        target = self.node.ref

        if not target:  # target is 0 or None: Free Variable or Constant
            return Noke( target )

        #print('jump to ref', self, target)
        while target != self.node:
            self = self.stepUp()
            #print('jump', self)
        return self


    def through( self ):
        "Skips Let-Expressions and Let-bound Variables"

        node = self.node
        key  = self.key
        
        while True:     # Skip Let-Expressions
            if LET == node.type:
                node = node.expr
            
            elif VAR == node.type and node.letbound():
                key = addkey( node, key )
                node = node.ref.be

            else:
                return Noke( node,key )     # Create new Noke



    def stepUp( self ):
        "Moves Noke pointer up through Tree. Does not skip Let-s"
        
        key  = self.key
        prev = self.node
        
        node = prev.parent
        if LET == node.type and node.be == prev:    # Gone to LET from 'be'
            _,key = getkey( key )                   # Decrease Key

        return Noke( node,key )                 # Create new Noke



    def up( self ):   # Rename to throughUp() ??
        "Moves Noke pointer up through Tree. Skips Let-Expressions"
        
        key  = self.key
        prev = self.node
        node = prev.parent
        
        while True:
            if LET == node.type:
                if node.be == prev:             # Gone to LET from 'be'
                    prev = node
                    node,key = getkey( key )    # Go to VAR                    
                else:                           # Gone to LET from 'expr'
                    prev = node
                    node = prev.parent
            else:
                break

        return Noke( node,key )                 # Create new Noke



    def skipLambdas( noke ):
        
        while ABS == noke.node.type:
            noke = noke['expr'].through()
        
        return noke
        

    def withAppls( noke ):
        
        yield noke
        
        parent = noke.up()
        if APPL == parent.node.type and noke == parent['func']:
            for n in parent.withAppls():
                yield n
            
        
        
    def isRedex( self ):
        if ABS == self.node.type:
            up = self.up()
            if APPL == up.node.type and self == up['func']:
                return True
        return False


    def isRedexAppl( self ):
        return APPL == self.node.type and ABS == self['func'].through().node.type

    
    def derefable( self ):
        return VAR == self.up().node.type
       

    #----------------------------------------------------------
    # Figure


    def bubbles( noke ):
        # ?? ?? it not work like Group.bubbles() !!
        "Iterates all Bubble-Nokes down this Noke"
    
        noke = noke.through()
        
        if APPL == noke.node.type:
            args = noke['arg'].bubblesDraw()
            yield first( args )     # Yield distant arg first (as base, rootnoke)
            
            for b in noke['func'].bubblesDraw():
                yield b
                    
            for b in args:
                yield b
                    
        else:   # ABS or Abs-VAR
            yield noke



    def bubblesDraw( noke ):
        """
        Iterates all Bubble-Nokes in Group, starting from noke
        in order to draw
        """
    
        noke = noke.through()
        
        if APPL == noke.node.type:
            for n in noke['arg'], noke['func']:
                for b in n.bubblesDraw():
                    yield b
                    
        else:   # ABS or Abs-VAR
            yield noke



    def group( noke ):
        "Get Group object by APPL-Noke"
        
        noke = noke.through()
        
        if APPL == noke.node.type:
            return noke['func'].group()
        else:
            bubble = noke()
            return bubble.group
        

    
    def bubbleNokes( noke ):
        """
        Iterates all Bubble-Nokes in Figure
        in order to draw
        """
        noke = noke.through()
        
        type = noke.node.type

        if VAR == type:
            yield noke
            return
        
        elif ABS == type:
            yield noke
            nokes = noke['expr'],
        
        elif APPL == type:
            nokes = noke['arg'], noke['func']

        
        for noke in nokes:
            for n in noke.bubbleNokes():
                yield n
        
                
        
        
        


    def copyBubble( self, noke ):
        "Copy Bubble from one Noke to another"
        
        if self.node != noke.node:
            raise Exception("can't copy Bubble")
        
        bubble = noke()
        if bubble:
            self.set( bubble.lightCopy() )
                
        
