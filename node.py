

from    debug       import  *



class Node:
    """
    Class of Node of Tree (for Tree of Lambda-Expression in let.py)
    Each Node has dict of Childs:   self.childs
    Each Node may be substituted with some other Node.
    """
    
    def __init__( self, **childs ):

        self.__dict__['childs'] = childs    # dict of Childs {name:Node}
                                            # Do not call __setattr__ here
        self.parent = None
        
        for c in childs.values():
            if c:
                c.parent = self             # Backlink from linked Child too

        # For Noke class
        self.fission = {}                   # Dict {key: Bubble} where key is (var,var,..)
                
        

    def __setattr__( self, name, value ):

        if name in self.childs:
            self.childs[ name ] = value
            if value:
                value.parent = self         # Backlink from linked Child too
        
        else:
            self.__dict__[ name ] = value



    def __getattr__( self, name ):

        if name in self.childs:
            return self.childs[ name ]

        else:
            raise AttributeError(name)



    def subst( self, node ):
        "Substitute for self: Link Parent to-and-from new Node."
        
        debug( 4, 'subst: %s -to- %s' % (self, node) )
        debug( 4, 'parent.childs: %s' % self.parent.childs )
        
        for k,child in self.parent.childs.items():
            if self == child:                   # Find Link to this Node
                self.parent.childs[ k ] = node
                node.parent = self.parent       # Backlink from linked Child too
                self.parent = None              # Mark as deleted!
                return

        debug( 4, 'no child %s; only %s' % (self, self.parent.childs) )
        raise KeyError()


    def allNodes( self ):
        "Iterates all Nodes of Branch"
        yield self
        for child in self.childs.values():
            for node in child.allNodes():
                yield node


