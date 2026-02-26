

from    debug       import  *

from    figure      import  *

#from    matrix      import  *
import  let



def hasParent( node: Node ):
    p = node.parent
    return p and p.type is not None  # skip fake parent (see made in withRoot)


def applicate( dropped, node ):
    debug('con','dropped',dropped,'-->',node)

    #appl = let.Application( func= func, arg= node )
    #node.subst( appl )

    #!!! Doubtful UX: if it's free variable (but not a single one) - replace it with dropped node
    if VAR == node.type and 0 == node.ref and hasParent( node ):   # Replace Free Variable to Dropped Expression
        node.subst( dropped )
    
    else:
        appl = let.Application( func= None, arg= None )
        node.subst( appl )
        appl.func = dropped
        appl.arg  = node



def applicationBefore( node ):
    debug('con','add application before',node)

    var = let.Variable()
    var.ref = 0     # Free Variable 
    
    appl = let.Application( func= var, arg= None )
    
    node.subst( appl )
    appl.arg = node
    

def applicationAfter( node ):
    debug('con','add application after',node)

    var = let.Variable()
    var.ref = 0     # Free Variable 
    
    appl = let.Application( func= None, arg= var )
    
    node.subst( appl )
    appl.func = node
   
   
   
def addLambda( node ):
    debug('con','add Lambda after',node)

    abs = let.Abstraction( expr= None )
    
    node.subst( abs )
    abs.expr = node
    
    return abs


def reref( var, abs ):
    debug('con','reref',var,abs)
    
    # Check Abstraction above (above only!) the Variable
    found = var
    while found and abs != found:
        found = found.parent
        debug('con','reref checking',found)
    if not found:
        return False
    
    # Reref
    var.ref = abs
    return True



def delete( node ):
    
    if let.ABS == node.type:
        # Reref Abs-Vars to 0
        node.replace( {node:0} )
        # Remove from Tree
        node.subst( node.expr )

    elif let.LET == node.type:
        pass    # ?? Can't delete

    else:   # APPL or VAR
        parent = node.parent
        if let.ABS == parent.type:
            if let.VAR == node.type:  # VAR - Can't delete
                node.ref = 0
            else:                     # APPL - Replace to VAR
                var = let.Variable()
                var.ref = 0
                node.subst( var )
        
        elif let.APPL == parent.type:
            if node == parent.func:
                parent.subst( parent.arg )
            elif node == parent.arg:
                parent.subst( parent.func )


