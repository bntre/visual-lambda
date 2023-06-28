
import  copy

from    debug       import  *

from    library     import  Library
from    let         import  *



# Consts
LAMBDA  = 1
BODY    = 2
LET     = 3
BE      = 4
IN      = 5
BRACKET = 6



class Parser:
    
    # Chars for multi-char Tokens
    chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_'"

    # Delimiters (single-char Tokens)
    dels  = "\\/.():,+*="
    

    def __init__( self ):
        
        self.lib = Library( self )  # Create Library
        self.lib.init()             # parser.lib reference must exist before initialization of Library

    
    def parse( self, str ):

        #print(list( self.tokenize( str ) ))
        tokens = self.tokenize( str )
        struct = self.getStruct( tokens )
        #print(struct)

        return self.getExpression( struct, {} )

   
    def getExpression( self, struct, vars, func=None ):
        
        if not struct:
            print("Error: Empty Expression: ()")
            return Variable()
        
        head, tail = struct[0], struct[1:]
        
        if type( head ) is not tuple:       # head is list
            expr = self.getExpression( head, vars )

        else:
            varname,vartype = head
            
            if LAMBDA == vartype:           # Lambda
                
                abs = Abstraction( expr= None )
                
                vars1 = copy.copy( vars )   # Create copy of bound Variables
                vars1[ varname ] = abs      # And Append/Replace the varname
    
                if not tail:
                    print("Error: Lambda %s without Expression" % varname)
                    return Variable()
    
                abs.expr = self.getExpression( tail, vars1 )
                
                if func:
                    return Application( func= func, arg= abs )
                
                return abs

            elif BODY == vartype:           # Variable (Free or Bound)

                if varname in vars:                         # Try to search in Bound variables
                    expr = Variable( vars[ varname ] )
                
                else:
                    expr = self.lib.find_item( varname )
                    if not expr:
                        expr = Variable()
                        print("Warning: Free Variable '%s'" % varname)

            
            elif LET == vartype:            # Variable of Let-Expression
                
                let = Let( be= None, expr= None )

                if not tail or len( tail ) < 2:
                    print("Error: Let %s without Expression" % varname)
                    return Variable()
                    
                vars1 = copy.copy( vars )   # Create copy of bound Variables
                let.be = self.getExpression( tail[0], vars1 )
                
                vars1 = copy.copy( vars )   # Create copy of bound Variables
                vars1[ varname ] = let      # And Append/Replace the varname                
                let.expr = self.getExpression( tail[1:], vars1 )

                if func:
                    return Application( func= func, arg= let )
                
                return let
                
            else:
                raise Exception("Parser Error: Unknow var %s::%d" % (varname,vartype))
                

        if func:
            expr = Application( func= func, arg= expr )

        if tail:
            expr = self.getExpression( tail, vars, expr )

        return expr
            

    
    def getStruct( self, tokens ):
        "Creates Tree of lists [(token,type)]"
    
        tree  = []
        level = tree    # list of current level: [ ( varname, vartype ) | next level ]
        stack = []      # stack of levels: [ ( type of current level, prev level ) ]

        
        def addlevel( type, level ):
            stack.append( ( type, level ) )
            new = []
            level.append( new )
            return new

        def poplevel( type ):
            while stack:
                t,prev = stack.pop()
                if type == t:             # Exit from level of type
                    break
            return prev
            
        
        type = BODY     # vartype: LAMBDA or BODY

        for t in tokens:
        
            if '/' == t or '\\' == t:               # Lambda of Abstraction
                type = LAMBDA

            elif '.' == t:                          # Body of Abstraction
                type = BODY


            elif '(' == t:
                level = addlevel( BRACKET, level )  # Enter to BRACKET level

            elif ')' == t:
                level = poplevel( BRACKET )         # Exit from BRACKET level
                type = BODY

                
            elif 'let' == t:
                level = addlevel( LET, level )

                var = next(tokens)
                level.append( ( var, LET ) )
                
                be = next(tokens)
                if not( '=' == be or 'be' == be ):
                    debug('parse', "Error: 'let %s' without '=' (got %s)" % (var, be) )

                level = addlevel( BE, level )       # Enter to BE level
            
            elif 'in' == t:
                level = poplevel( BE )              # Exit from BE level
                type = BODY
            
            else:
                level.append( ( t, type ) )         # Variable

        return tree
        


    def tokenize( self, str ):
        "Break str to Tokens"
        i = 0
        n = len( str )
        while i<n:
            if str[i] in Parser.chars:
                j = i+1
                while j<n and str[j] in Parser.chars:
                    j += 1
                yield str[i:j]
                if not j<n:
                    break
                i = j
            if str[i] in Parser.dels:
                yield str[i]
            i += 1
            



parser = Parser()

def parse( str ):
    return parser.parse( str )
    