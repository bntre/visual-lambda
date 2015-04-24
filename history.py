

from    debug       import  *


class History:
    """
    History of Figure Expressions.
    Saves and restores Expression steps.
    """
    
    def __init__( self ):
        
        self.before  = []
        self.after   = []   # ?? needed?
        
        
    def step( self, obj ):
        
        self.before.append( obj )
        
 
    def undo( self ):
        
        if 1 < len( self.before ):
            self.after.append( self.before.pop() )
            return self.before[-1]
        

    def redo( self ):

        if self.after:
            self.before.append( self.after.pop() )
            return self.before[-1]



