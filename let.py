
from    debug       import *
from    common      import *

import  copy

import  refnames
from    node        import Node


# Constants

# Types of Expressions (the order is used in Expression.repr())
VAR     = 0    # Variable
APPL    = 1    # Application
ABS     = 2    # Abstraction
LET     = 3    # Let


# Types of Reduction
BETA    = 1
DEREF   = 2
LIFT    = 3     # Arrange:
ASSOC   = 4
NOREF   = 5     # Garbage Collection:
XINX    = 6
XISY    = 7
ONEREF  = 8



class Red:
    "Class of result of Reduction"

    def __init__( self, result, data= None ):
        self.result = result
        self.data   = data
        
    def __repr__( self ):
        str = { BETA:  'Beta',  \
                DEREF: 'Deref',  \
                LIFT:  'Lift',  \
                ASSOC: 'Assoc',  \
                NOREF: 'Garbage: no ref',  \
                XINX:  'Garbage: x=E in x',  \
                XISY:  'Garbage: x=y in E',  \
                ONEREF:'Garbage: 1 ref' }[ self.result ]
        if self.data:
            str += ' ' + repr(self.data)
        return str

    def __eq__( self, other ):  # ?? what for (compare 'data' ?)
        return other == self.result




class Mode:
    "Mode of Reduction"
    def __init__( self, applicative= False, lazy= True, redex= False, find= False ):
        self.applicative = applicative  # Reduction strategy: Normal or Applicative
        self.lazy        = lazy         # Pure Lambda-calculus or Lazy Let-calculus
        self.redex       = redex        # Redex for Reduction specified directly
        self.find        = find         # Only find Redex or Deref, do not reduce (Graphical Mode)



#-------------------------------------------------------------


class Expression( Node ):

    reducible = ()

    type      = None


    # Representation

    def __repr__( self ):
        "Sets Representation to Brackets according the Type"
        return 'root of ' + repr(self.expr)

    def repr( self, level=0 ):
        "Sets Representation to Brackets according the Type"
        return ( level < self.type and '(%s)' or '%s' ) % repr(self)

    def name( self ):
        #return hex( id(self) )
        return refnames.repr( self )


    # References

    def replace( self, vars ):
        for c in self.childs.values():
            c.replace( vars )

    def unref( self ):
        for c in self.childs.values():
            c.unref()

    def copy( self, vars= None ):
        vars = vars or ({},{})
        expr = self.expr.copy( vars )
        return  Expression( expr= expr )



    def pure( self ):
        """
        Skips let-expressions and let-bound variables.
        Returns pair (pure Expression, skipped Variables)
        Pure expression: Lambda-bound Variable, Abstraction or Application
        """
        vars = []
        
        while True:
            if VAR == self.type:
                if self.letbound():
                    vars.append( self )
                    self = self.ref.be
                else:
                    break                    
            elif LET == self.type:
                self = self.expr
            else:
                break
            
        return self, tuple(vars)
    

    # Reduce

    def arrange( self, *args ):
        "Arranges all childs-Expressions: Assoc, Lift, Garbages"
        for child in self.reducible:    # ?? maybe arrange all childs, not only reducible (it's about Let.be)
            for r in self.childs[ child ].arrange( *args ):
                yield r

    def deref( self, *args ):
        "Derefs all Let-bound Variables in childs-Expressions"
        for child in self.reducible:
            for r in self.childs[ child ].deref( *args ):
                yield r


    def reduce( self, *args ):
        "Tries to reduce one of Sub-Expression"
        for child in self.reducible:
            r = self.childs[ child ].reduce( *args )
            if r:
                return r
        return False



    def postReduce( root, mode ):
        """
        Deref all in case of Pure Lambda-calculus.
        and Arrange (Assoc, Lift, Garbage) all.
        """

        # Deref All Let-expressions
        # in case of Pure Lambda-calculus
        if not mode.lazy:
            print('not lazy')
            for r in root.expr.deref():   # Deref all
                yield r

        # Arrange + Garbage
        while 1:
            rs = False
            for r in root.expr.arrange( True ):
                yield r
                rs = True

            if not rs:
                break


    def reduceStep( root, mode= None ):
        "Reduction Step and Garbage collection after"

        mode = mode or Mode()

        r = root.expr.reduce( mode )
        if r:
            debug( 'red', r )
            debug( 'red', root.expr )

            rs = False
            for q in root.postReduce( mode ):
                debug( 'red', q )
                rs = True
            if rs:
                debug( 'red', root.expr )


        return r    # return main result of Reduction



    def withRoot( self ):
        "Add Root to Expression"
        root = Expression( expr= self )
        #root.reducible = 'expr',
        return root




class Variable( Expression ):

    type = VAR

    def __init__( self, ref= 0 ):
        Expression.__init__( self )

        self.ref = ref      # Reference to Abstraction or Let Expression
                            # 0    - Free Variable
                            # None - Constant



    def __setattr__( self, name, value ):

        if 'ref' == name:
            try:
                self.ref.refs -= 1      # Decrease previous
            except:                     # (no .ref or None==.ref)
                pass

            if value:
                value.refs += 1


        self.__dict__[ name ] = value



    def __repr__( self ):
        return  self.ref and self.ref.name()  or 'O'

    # References

    def letbound( self ):
        return  self.ref and LET == self.ref.type
    

    def unref( self ):
        "Call it before deleting Variable"
        if self.ref:
            self.ref.refs -= 1

    def replace( self, vars ):
        """Tries to replace Variables with new ones.
        vars is dict {old variable: new variable} """
        if self.ref in vars:
            self.ref = vars[ self.ref ]

    def copy( self, vars ):
        ref = self.ref
        if ref:
            l = int( LET == ref.type )
            if ref in vars[l]:          # Not Free Variable
                ref = vars[l][ ref ]
        return Variable( ref )


    # Reduce

    def reduce( self, mode ):
        debug( 4, 'come to var', self )
        if self.letbound():
            return self.ref.be.reduce( mode )   # Try to reduce inside Let-expression
        
        #return first( self.deref() )    # Try to Deref Variable
        # !! Deref only from Application in case of redex


    def deref( self ):
        "Generator. Deref-reduction in case of Let-bound Variable"
        if self.letbound():
            debug( 4, 'deref needed. let', self.ref )
            expr = self.ref.derefBe()   # Deref Be-part of linked Let-expression
            debug( 4, 'derefed', expr )
            self.subst( expr )
            yield Red( DEREF, expr )
        
        # Else: Variable is not linked to Let-expression
        # (Free Variable (or Constant) or Bound to Abstraction)


    def arrange( self, garbage ):    
        if garbage:            
            if self.letbound() and 1 == self.ref.refs:  # Garbage ONEREF                
                first( self.deref() )           # Deref Variable (And Remove this Let Expression)
                yield Red( ONEREF )


    def getClosed( var ):
        """
        Returns pair ( fvs, closed )
        where  fvs    - set of free variables
               closed - list of closed expressions (as lists of abs)
                        closed[0] is closed if not fvs
        """

        if None == var.ref:   # Constant
            return set(), [[]]

        elif 0 == var.ref:    # Free Variable
            return set(), [[]]
            #return set([var.ref]), [[]]

        else:
            if ABS == var.ref.type:
                return set([var.ref]), [[]]

            else:   # LET
                return var.ref.be.getClosed()







class Let( Expression ):

    type = LET

    reducible = 'expr',     # 'be' is not reducible!


    def __init__( self, **childs ):
        Expression.__init__( self, **childs )
        self.refs = 0       # Reference counter


    def __repr__( self ):
        if debugTag('refs'):
            return '[%d]let %s = %s in %s' % ( self.refs, self.name(), repr(self.be), repr(self.expr))
        else:
            return 'let %s = %s in %s' % ( self.name(), repr(self.be), repr(self.expr))


    def derefBe( self ):
        "Returns Copy of Be-Expression"
        self.refs -= 1
        if 0 == self.refs:              # Do not copy for single reference
            # self.be.unref() -- do not unref, because self.be leaves instead of variable
            self.subst( self.expr )     # Garbage 'no ref' here too
            return self.be
        else:
            return self.be.copy( ({},{}) )


    def copy( self, vars ):
        be = self.be.copy( vars )
        let = Let( be= be, expr= None )
        vars[1][ self ] = let   # Add bound Variable to dict of Let-vars {old variable: new variable}
        let.expr = self.expr.copy( vars )
        return let



    def arrange( self, garbage ):
        "garbage is True if garbage collection needed too"

        while LET == self.be.type:      # ASSOC
            let  = self.be
            expr = let.expr

            self.subst( let )
            let.expr = self
            self.be  = expr

            self = let
            yield Red( ASSOC )


        if garbage:

            if not self.refs:               # Garbage NOREF
                self.be.unref()             # Remove this Let Expression
                self.subst( self.expr )
                yield Red( NOREF )
                for r in self.expr.arrange( garbage ):
                    yield r     # We will restart arrange() because now may appear new NOREF case
                return


            if VAR == self.expr.type and self == self.expr.ref:
                self.subst( self.be )       # Remove this Let Expression
                yield Red( XINX )           # Garbage: let x=E in x
                for r in self.be.arrange( garbage ):
                    yield r
                return


            if VAR == self.be.type:
                self.expr.replace( {self: self.be.ref} )
                self.be.unref()             # Remove this Let Expression
                self.subst( self.expr )
                yield Red( XISY, self )     # Garbage: let x=y in E
                for r in self.expr.arrange( garbage ):
                    yield r
                return


        for r in self.expr.arrange( garbage ):
            yield r




    def getClosed( let ):
        return let.expr.getClosed()









class Abstraction( Expression ):

    type = ABS

    reducible = 'expr',


    def __init__( self, **childs ):
        Expression.__init__( self, **childs )

        self.refs = 0


    def __repr__( abs ):
        vars = []
        while abs and ABS == abs.type:       # Represent sequence of Abstractions at once
            if debugTag('refs'):
                vars.append( ('[%d]' % abs.refs) + self.name() )
            else:
                vars.append( abs.name() )
            abs = abs.expr
        return '\\%s. %s' % (' '.join( vars ), repr(abs))



    def copy( self, vars ):
        abs = Abstraction( expr= None )
        vars[0][ self ] = abs       # Append dict of Abs-vars
        abs.expr = self.expr.copy( vars )
        return abs



    def getClosed( abs ):

        fvs, closed = abs.expr.getClosed()

        if fvs:
            if abs in fvs:
                fvs.remove( abs )
            closed[0].insert( 0, abs )
        else:
            closed.insert( 0, [abs] )

        return fvs, closed










class Application( Expression ):

    type = APPL

    reducible = 'func','arg'


    def __repr__( appl ):
        return '%s %s' % ( appl.func and appl.func.repr(1) or '?',
                           appl.arg  and appl.arg.repr() or '?' )   # func Expression - without brackets
            


    def copy( appl, vars ):
        #func = appl.func.copy( copy.copy( vars ) )
        func = appl.func.copy( vars )
        arg  = appl.arg .copy( vars )
        return Application( func= func, arg= arg )




    def reduce( appl, mode ):

        funcPure,skipped = appl.func.pure()

        if ABS == funcPure.type:
            
            if skipped:                     # Dereference skipped Variable
                return first( skipped[0].deref() )
                
            else:
                if mode.applicative:        # Applicative Strategy => Try to reduce Childs
                    r = Expression.reduce( appl, mode )   # Find Redex among the Childs
                    if r:
                        return r
    
                if mode.find:               # Graphical mode - find only - do not reduce
                    return Red( BETA, funcPure )
    
                else:
                    # ?? Here is error: 
                    # between funcPure and appl may be
                    # let-bound variables and let-expressions
                    let = Let( be= appl.arg, expr= funcPure.expr )
                    let.expr.replace( {appl.func: let} )
                    appl.subst( let )
                    return Red( BETA )

        return Expression.reduce( appl, mode )



    def arrange( self, garbage ):

        if LET == self.func.type:    # Lift
            let  = self.func
            expr = let.expr

            self.subst( let )
            let.expr  = self
            self.func = expr

            yield Red( LIFT )
            for r in let.arrange( garbage ):
                yield r
            return


        for r in Expression.arrange( self, garbage ):
            yield r



    def getClosed( appl ):

        fvs0, closed0 = appl.func.getClosed()
        fvs1, closed1 = appl.arg .getClosed()

        if fvs0 and not fvs1:               # One of child Expressions is not free
            return fvs0, closed0+closed1    # Incomplete Group - first

        elif fvs1 and not fvs0:
            return fvs1, closed1+closed0

        if not fvs0 and not fvs1:           # Both of child Expressions are free
            return fvs0, closed0+closed1    # fvs0 is empty set

        else:                               # Both of child Expressions are not free
                                            # Join their unfound vars and incomplete groups
            return fvs0|fvs1, [closed0[0]+closed1[0]] + closed0[1:] + closed1[1:]












def reduce( expr, mode=None ):

    mode = mode or Mode()
    print("mode:", mode.__dict__)

    r = 'Reduce:'
    print(r)
    print(expr)

    root = expr.withRoot()
    while r:
        r = root.reduceStep( mode )

    print('-------')
    return root.expr



def printClosed( expr ):
    "For test: print closed Sub-expressions"
    vars, gs = expr.getClosed()
    print(expr)
    print('free:', vars)
    print('groups:')
    for g in gs:
        print(' '.join(abs.name() for abs in g))



