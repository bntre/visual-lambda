
import  math


from    debug       import  *

from    vector      import  *
from    matrix      import  *
from    ring        import  Ring

from    let         import  *
from    noke        import  *
from    cache       import  Cache

from    lambdaparser import parse

from    fielditem   import FieldItem

import  color
import  history






class Drawn:
    "Class of Drawn Ring. Output of Bubble.ringsToDraw()"
    
    def __init__( self, noke, ring, fade= None ):
        self.noke = noke
        self.ring = ring
        self.fade = fade




class Bubble:


    @staticmethod
    def getDir( key ):      # key is pair of Bubbles
        return Vector2( key[0].ring.pos, key[1].ring.pos ).unit()
    
    @staticmethod
    def getArc( key ):      # key is pair of Bubbles
        a,b = key[0].ring, key[1].ring
        return math.asin( 1.0 * b.r / (a.r + b.r) )



    dirs = None     # Cache
    arcs = None

    

    def __init__( self ):

        # Group Topology
        self.parent = None     # Noke  # not Bubble: for Group.buildGeometry()
        self.childs = []       # Nokes
        self.upper  = False    # Upper level - first child

        self.group  = None     # Parent Group of Bubble

        # Geometry and Correction
        self.ring   = Ring((0,0),1)
        
        # For building Geometry
        self.tight  = 0         # Left (Parents) and right (Childs) Tights
        self.corr   = 0         # Correction of Radius
        self.angles = {}        # dict {Bubble:angle}

        
        # Eating
        self.fading = None      # Fading object


    def __repr__( self ):
        return 'Bubble: %s' % self.ring


    def neighbor( self, n ):
        "Returns previous or next neighbor (or parent if not); n = -1 or 1"
        if self.parent:
            nokes = self.parent().childs + [self.parent]
            bubbles = list(map( Noke.get, nokes ))
            return nokes[ bubbles.index( self ) + n ]

    def neighbors( self ):
        "Iterates all neighbor Nokes"
        if self.childs:
            for n in self.childs:
                yield n
        
        if self.parent:
            yield self.parent
            for n in (-1,1):
                neighbor = self.neighbor( n )
                if neighbor != self.parent:
                    yield neighbor


    #def strongParents( self ):
    #    "Skips first Parent if Bubble is not on upper level"
    #    return  self.parents[ self.upper^1 :]


    def lightCopy( self ):
        "Copies main attributes of Bubble"
        bubble = Bubble()
        bubble.group  = self.group
        bubble.ring   = self.ring.copy()
        bubble.fading = self.fading
        return bubble
        
    def markUpperChilds( self, mark ):
        
        self.upper = mark
        
        if self.childs:
            upper = self.childs[0]
            for c in self.childs:
                c().markUpperChilds( c == upper )
            

            

    def detTights( self ):
        
        def arc( noke ):
            return Bubble.arcs[ ( self,noke() ) ]

            
        if self.parent:
            self.tight += arc( self.neighbor(-1) )
            self.tight += arc( self.neighbor( 1) )
        if self.childs:
            self.tight += arc( self.childs[ 0] )
            self.tight += arc( self.childs[-1] )
        
        
        if not self.upper:

            a = self.parent()                   # Bubbles: Parent
            c = self.neighbor(-1)()             #          Prev Neighbor

            ra = c.ring.r + self.ring.r         # Radiuses
            rb = a.ring.r + c.ring.r
            rc = a.ring.r + self.ring.r
                                                # Cosines
            ca = 1.0 * ( rb**2 + rc**2 - ra**2 ) / ( 2 * rb * rc )
            cc = 1.0 * ( ra**2 + rb**2 - rc**2 ) / ( 2 * ra * rb )
            
            aa = math.acos( ca )                # Angles
            ac = math.acos( cc )
            ab = math.pi - (aa + ac)
            
            a   .tight += aa                    # Increase Tights
            c   .tight += ac
            self.tight += ab
        
            # Save angle aa for detPosition()
            a.angles[ self ] = aa
            

            
    def detCorrections( self ):
        "Dets Correction values. Returns False if Correction is not needed."

        if not ( self.parent or self.childs ):  # Skip single Bubbles
            return False


        minChink = math.pi * 0.2        # ?? maybe to Constants
        
        # Set tight as chink
        self.tight = math.pi*2 - self.tight
        self.tight /= 2
            

            
        if self.tight < minChink:       # Correction needed
        
            self.corr += 2
            for n in self.neighbors():
                n().corr -= 0.2         # ?? Here may be wrong values, and some Figures may be unbuildable
            
            return True
        
        return False                    # Correction is not needed
            
            
    def correct( self ):
        "Corrects Radius of Ring."
        if self.corr:
            self.ring.r *= math.exp( self.corr * 0.06 )

            
    def detPosition( self ):
        "Dets Position of Bubble. Calculates initial values of Chinks."
        
        if self.upper:
            
            if not self.parent:             # Root of Group
                self.ring.pos = Vector2((0,0))
                return
            
            else:
                parent = self.parent()      # Parent Bubble
                
                if not parent.parent:
                    dir = Vector2((1,0))    # Default direction
                
                else:
                    parent1 = parent.neighbor( -1 )()
                    a = parent.tight + Bubble.arcs[(parent,self)] + Bubble.arcs[(parent,parent1)] - math.pi
                    dir = Bubble.dirs[(parent1,parent)]
                    dir = dir.rotate( Vector2( angle= -a ) )     # Det direction

        else:
            parent = self.parent()
            prev   = self.neighbor(-1)()
            a = parent.angles[ self ]
            dir = Bubble.dirs[(parent,prev)]
            dir = dir.rotate( Vector2( angle= -a ) )             # Det direction

            
        Bubble.dirs[(parent,self)] = dir
        
        self.ring.pos = parent.ring.pos + dir * (parent.ring.r + self.ring.r)
          


    def transform( self ):
        """
        Returns transformation Matrix of Bubble,
        includes transformation Matrix of Group if is.
        """
        
        # Default transformation is Unit 
        # (Variable or Lambda inside another Lambda)
        matrix = TransformMatrix()
        matrix.unit()
        
        # Group reference may not exist 
        # (Variable or Lambda inside fading Let-Bound Variable ??)
        if self.group:
            matrix *= self.group.transformMatrix

        if self.ring:
            matrix *= TransformMatrix( ring= self.ring )

        return  matrix




Bubble.dirs = Cache( Bubble.getDir )
Bubble.arcs = Cache( Bubble.getArc )



class Group:

    def __init__( self ):
        
        self.rootnoke = None
        
        # Bounding Ring
        self.boundingRing      = None
        self.boundingMatrix    = None     # Unit-Ring -> Bounding Ring
        self.transformMatrix   = None     # Unit-Ring <- Bounding Ring

    
    
    def bubbles( self, noke= None ):    # ?? move to Bubble
        """
        Iterates Nokes of Bubbles of Group 
        from root (reverse of order to draw)
        #in strange Order (deeply, elder Parents before)
        """
        
        noke = noke or self.rootnoke
        
        yield noke
        for p in noke().childs:
            for n in self.bubbles( p ):
                yield n
        
        #yield noke
        #for p in noke().strongParents():
        #    for n in self.bubbles( p ):
        #        yield n
    

    #def bubblesDraw( self, bubble= None ):
    #    "Iterates Bubbles of Group in order of drawing"
    #    bubble = bubble or self.root
        
    #    yield bubble
    #    parents = bubble.strongParents()
    #    for p in parents[::-1]:
    #        for b in self.bubblesDraw( p ):
    #            yield b



    @staticmethod
    def getBounding( bubbles ):
        "Returns Bounding Ring of Bubbles in Group"
        
        center = Vector2((0,0))
        ws     = 0
        for b in bubbles:
            weight = b.ring.r ** 2
            center += b.ring.pos * weight
            ws     += 1.0 * weight
        center /= ws

        radius = max([ Vector2( center, b.ring.pos ).length() + b.ring.r  \
                        for b in bubbles ])
        
        return Ring( center, radius )


    def resetBoundingRing( self ):
        "Resets Bounding Ring of Bubbles in Group"
        bubbles = tuple( map( Noke.get, self.bubbles() ) )
        self.boundingRing = Group.getBounding( bubbles )


    def resetBoundingMatrix( self ):
        "Resets Bounding Matrix of Bubbles in Group"
        self.boundingMatrix  = TransformMatrix( ring=self.boundingRing )    # Unit -> Bounding Ring
        self.transformMatrix = self.boundingMatrix.inverse()


    def balanceGroup( self ):

        sum = Vector2((0,0))
        for b in self.bubbles():
            bubble = b()
            for c in bubble.childs:
                child = c()
                sum += Bubble.dirs[ (bubble,child) ] * child.ring.r    # Let it depend on radius of child

        balance = sum.unit().conjugate()
        
        for b in self.bubbles():
            bubble = b()
            bubble.ring.pos = bubble.ring.pos.rotate( balance )
    
        Bubble.dirs.reset()     # Reset Dirs Cache
        




class Figure( FieldItem ):


    drawing = {}        # Feedback from Manipulator at drawing


    # Geometry Constants
    lambdaCoef = 1.22   # Constriction of Bubble by Abstraction
    expandCoef = 1.07   # Expand all Rings for intersection of Bubbles (?? maybe move to Manipulator)
    holeLens   = 1.0
    groupCoef  = 0.8    # 0..1  Expand Bubble according Group inside
    
    lambdaMatrix = TransformMatrix()
    lambdaMatrix.setTranspose( 0,0, lambdaCoef )
    
    
    isFigure   = True
    
    
    def __init__( self, expression ):

        FieldItem.__init__( self )

        # Parse Expression if needed
        if type( expression ) is str:
            expression = parse( expression )
            debug( 2, 'init Figure', expression )

        self.expression = expression.withRoot()

        # History of Expression
        self.history = history.History()

        # Colorspace
        self.detColorSpace()


        # Size of Figure
        self.sizeRing  = Ring((0,0),1.0)        # Ring for setting size of Figure (used in morphing)
        self.refreshTransform()

        
        self.groups = []
        self.buildGroups()
        self.buildGeometry()
        
        self.history.step( self.expression.copy() )

        # Eating Act
        self.eating = None


    
    def copy( self ):
        copy = Figure( self.expression.copy().expr )

        copy.position = self.position.copy()
        copy.refreshTransform()

        return copy
    
    
    def detColorSpace( self ):
        self.colorspace = color.ColorSpace( self.expression.expr )
        

    def refreshTransform( self ):
        self.transform = self.position * TransformMatrix( ring= self.sizeRing )
        
            
    def root( self ):
        "Root Noke of Figure"
        return Noke( self.expression )['expr']
        


    def detGroups( self, noke, childs, group= None ):
        "Returns rootnoke of Group"

        if APPL == noke.node.type:

            debug('build','found APPL',noke,group)

            if not group:
                group = Group()             # Create Group
                self.groups.append( group )

            child = self.detGroups( noke['arg' ].through(),             [], group )
            return  self.detGroups( noke['func'].through(), [child]+childs, group )


        else:   # ABS or VAR
            
            if group:                       # Bubble not needed if single
                bubble = Bubble()
                bubble.childs = copy.copy( childs )
                bubble.group  = group       # Save Parent Group of Bubble ?? needed
                noke.set( bubble )
                debug('build','create Bubble',bubble,noke)

                group.rootnoke = noke       # rootnoke is overwritting (last func stays)


            if ABS == noke.node.type:
                self.detGroups( noke['expr'].through(), [] )    # Step inside

            return noke           # returns Noke

        
            
        
    def buildGroups( self ):

        # Det Groups, and Bubbles with 'childs' attribute
        self.groups = []    # Nokes
        self.detGroups( self.root().through(), [] )
        
        debug('build','buildGroups groups:',self.groups)
        
        for group in self.groups:

            # Mark upper level of Bubbles (before bubbles() Iteration)
            group.rootnoke().markUpperChilds( True )
            
            # Det parents of Bubbles
            for b in group.bubbles():
                for n in b().childs:
                    n().parent = b
    
    


    def buildGroupGeometry( self, group ):
        "Det Configuration iteratively"

        nokes = list( group.bubbles() )
        bubbles = list(map( Noke.get, nokes ))

        debug('build','buildGroupGeometry. nokes:',nokes)
        
        # Det initial Radiuses of Bubbles
        for b,n in zip( bubbles, nokes ):
            b.ring.r = self.getRadius( n )        # Recursive call
        
        
        # Iteratively det Radiuses (and angles) of Bubbles
        for retries in range( 50,0,-1 ):
        
            # Reset
            Bubble.arcs.reset()     # Reset Arcs Cache
            for b in bubbles:       # Reset Tights and Corrections
                b.tight = 0
                b.corr  = 0
                
            # Det Tights
            for b in bubbles:
                Bubble.detTights(b)
                
            # Det Corrections
            if not any( list(map( Bubble.detCorrections, bubbles )) ):
                debug( 'build', "ok" )
                break
                
            debug( 'build', "retries", retries )
            
            # Correct Radiuses of Bubbles
            for b in bubbles:
                Bubble.correct(b)
            

        # Det positions of Bubbles
        Bubble.dirs.reset()         # Reset Dirs Cache
        for b in bubbles:
            Bubble.detPosition(b)

        # Expand Radiuses for overlapping
        for b in bubbles:
            b.ring.r *= Figure.expandCoef

        # Balance Group
        group.balanceGroup()
        
        
        # Set Bounding Ring and Matrix
        group.resetBoundingRing()
        group.resetBoundingMatrix()
        


    def getRadius( self, noke ):
        """
        Calculates Radius of (Sub)Figure
        according to outside Lambdas and
        building geometry of Group inside
        """

        # Expand according to count of Lambdas
        lambdas = 0
        while ABS == noke.node.type:
            lambdas += 1
            noke = noke['expr'].through()           # There must be no old Bubbles (clean Figure before!)
        
        radius = Figure.lambdaCoef ** lambdas       # Now radius=1.0 if no Lambdas
        
        # Expand if Group inside
        if APPL == noke.node.type:
            group = noke.group()
            self.buildGroupGeometry( group )        # Recursive call
            radius *= group.boundingRing.r ** Figure.groupCoef
        
        #debug('build','radius for',noke,radius)
        
        return radius
            
            
    
    def coordinateGroup( self, noke, dir ):
        "dir is Matrix of Direction; noke is APPL-Noke"

        group = noke.group()

        # Co-ordinate inside Groups if are
        for noke in group.bubbles():

            bubble = noke()
            bubble.ring = bubble.ring.transform( dir )
            
            # Skip Lambdas
            noke = noke.skipLambdas()
            if APPL == noke.node.type:      # Inside co-ordination needed 
                
                if not bubble.parent:       # The same as parent group
                    dir1 = dir
                else:
                    parent = bubble.parent()
                    dir1 = TransformMatrix()
                    dir1.setRotate( Bubble.getDir( (parent,bubble) ) )
    
                self.coordinateGroup( noke, dir1 )

        
        # Rotate Bounding Ring
        group.boundingRing = group.boundingRing.transform( dir )
        #group.resetBoundingRing()
        group.resetBoundingMatrix()

        
    
    def buildGeometry( self ):
        
        noke = self.root().through()
        
        # Build whole inside geometry
        radius = self.getRadius( noke )
        
        self.sizeRing.r = radius
        self.refreshTransform()


        # Co-ordinate all groups

        # Skip Lambdas
        noke = noke.skipLambdas()
            
        if APPL == noke.node.type:      # Co-ordination needed
            
            dir = TransformMatrix()
            dir.setRotate( Vector2( (1,0) ) )
    
            self.coordinateGroup( noke, dir )
        


        debug( 'build', "Geometry builded", self )
        


    def clean( self ):
        "Deletes Bubbles from Nokes"
        for node in self.expression.allNodes():
            node.fission = {}

    
    def ringsToDraw( self, matrix, noke= None ):   # ?? move to Noke class
        
        noke = noke or self.root()

        #debug('draw','ringsToDraw: draw',noke)

        yielded = False
        nokes   = ()
        
        type = noke.node.type
        
        if VAR == type:
            
            if noke.node.letbound():
            
                # Check Fading Bubble
                bubble = noke()
                if bubble and bubble.fading:

                    # Do not change 'matrix'
                    matrix1 = matrix * bubble.transform()

                    yield Drawn( noke, Ring.unit.transform( matrix1 ), bubble.fading.fade )
                    yielded = True

                        
                nokes = noke['ref']['be'],      # Here must be ['ref'], not .ref()
                    
                
            else:               # Draw Bubble of Variable
                bubble = noke()
                if bubble:
                    matrix *= bubble.transform()

                yield Drawn( noke, Ring.unit.transform( matrix ) )
                return          # Nothing to draw inside

                
        elif ABS == type:       # Draw Bubble of Lambda
            
            bubble = noke()
            if bubble:
                matrix *= bubble.transform()
                
            yield Drawn( noke, Ring.unit.transform( matrix ) )
            yielded = True
            
            matrix *= Figure.lambdaMatrix.inverse()
            
            # Go inside Abstraction
            nokes = noke['expr'],

                
        elif LET == type:

            # Check Fading Bubble
            bubble = noke()
            if bubble and bubble.fading:
                # Do not change 'matrix'
                yield Drawn( noke, bubble.ring.transform( matrix * bubble.group.transformMatrix ), bubble.fading.fade )
                yielded = True
                #debug( 'draw', 'drawn LET:', noke, bubble )

            
            nokes = noke['expr'],

                
        elif APPL == type:
            
            nokes = noke['arg'], noke['func']

        
        
        
        # Feedback from Manipulator
        if yielded:
            if not Figure.drawing['done']:
                return      # Skip other Bubbles inside (too small or out of view)
        

        # Draw Bubbles inside
        for noke in nokes:
            for d in self.ringsToDraw( matrix, noke ):
                yield d



    def pick( self, matrix, cursor, noke= None ):
        
        noke = noke and noke.through()  or  self.root().through()
        
        type = noke.node.type
        
        if APPL == type:

            nokes = noke['arg'], noke['func']

        else:                   # VAR or ABS
            
            bubble = noke()
            if bubble:          # Bubble inside Group
                matrix = matrix * bubble.transform()    # create new matrix
                
            if not Ring.unit.transform( matrix ).pick( cursor ):
                return
                
            yield noke          # ABS or VAR
            
            if VAR == type:
                return

            matrix = matrix * Figure.lambdaMatrix.inversion
            nokes = noke['expr'],
                
        
        # Pick Bubbles of Group or inside Lambda
        for noke in nokes:
            for n in self.pick( matrix, cursor, noke ):
                yield n



