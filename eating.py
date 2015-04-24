
from    debug       import  *
#import  pygame

from    events      import  *
from    figure      import  *

from    matrix      import  *

from    let         import  Application, Let
from    noke        import  *


import  config


class Morph:
    
    def __init__( self, ring0, ring1, after= None ):
        self.ring0 = ring0  # Rings for morphing    
        self.ring1 = ring1
        self.after = after  # Callback function (usually matrix refreshing)

        


class Cover( Enduring ):
    
    def __init__( self, act ):
        
        self.act    = act        # Eating act (process)
        self.morphs = []
   
   
    def start( self ):
        
        # Start time func-s
        funcs = { 'pos': Enduring.I, 'r': Enduring.I }
        Enduring.__init__( self, Act.secCover, funcs )

        
        for eating in self.act.eatings:

            # Get Eaten bubbles
            eaten = map( Noke.get, eating.eaten )
        
            # Det Bounding ring of Eaten Bubbles for Eating Bubble morphing
            eatenBounding = Group.getBounding( eaten )
            
            transform = TransformMatrix( ring= eating.abs().ring ) *  \
                        TransformMatrix( ring= eatenBounding ).inverse()
    
            for e in eaten:
                self.morphs.append( Morph( e.ring, \
                                           e.ring.transform( transform ) ) )
            
    
            # Det Bounding ring of Group excluding Eaten Bubbles
            #  for Group Bounding Ring morphing
            nokes = list( eating.group.bubbles() )
            bubbles = map( Noke.get, nokes )
            map( bubbles.remove, eaten )
            
            newBounding = Group.getBounding( bubbles )
            
            self.morphs.append( Morph( eating.group.boundingRing, \
                                       newBounding,  \
                                       eating.group.resetBoundingMatrix ) )


        return Enduring.start( self )



    def handler( self ):

        ks = self.timefuncs()
        kpos,kr = ks['pos'][1], ks['r'][1]

        #debug( 'eat', 'got eating event.', ks )

        for m in self.morphs:

            #debug( 'eat', 'morph ring' )
            
            m.ring0.mix( kpos,kr, m.ring0, m.ring1 )
            
            if m.after:
                m.after()
            

        Bubble.dirs.reset()
        
        
        if self.end:
            #self.act.figure.eating = None; return               # Stop Eating Act
            yield  Fading( self.act ).start()                   # Start Fading
            #yield  Pause( 0.5, Fading( self.act ) ).start()     # Start Fading after pause
        
        else:
            yield  self.event
            




class Pause( Enduring ):

    def __init__( self, time, after ):
        self.after = after
        Enduring.__init__( self, time, {} )
        

    def handler( self ):
        self.timefuncs()
        if self.end:
            yield self.after.start()
        else:
            yield self.event





class Fading( Enduring ):

    def __init__( self, act ):
        self.act   = act    # Eating act (process)

        self.faded = []         # Nokes of fading Bubbles (for removing after Fading)
        self.released = False   # Release phase started
        

    def start( self ):

        # Start time func-s
        funcs = { 'fade': Enduring.I }
        Enduring.__init__( self, Act.secFading, funcs )
        self.fade = 1.0
        
        debug( 'eat', 'init Fading. abs:', self.act.abs )
        

        # Nodes of Redex
        abs  = self.act.abs
        appl = self.act.appl

        # Replace Redex (Appl and Abs) with new created Let
        let = Let( be= None, expr= None )
        appl.subst( let )
        let.be   = appl.arg
        let.expr = appl.func
        abs.subst( abs.expr )
        # let.expr.replace( {abs: let} ) -- 
        # Do not reref to Let. Else we will go through let-bound vars at down.bubblesDraw()

        
        for eating in self.act.eatings:
            
            debug('eat', '\nFading: eating', eating.appl )
            
            # Get Noke of new Let
            letnoke = Noke( let, eating.appl.key )
            debug( 'eat', 'init Fading. let:', letnoke )
            self.act.letnoke = letnoke      # Save last Let to Act

                
            # Save Abs-Bubble to Let Noke for Fading
            absbubble = eating.abs()
            absbubble.fading = self
            letnoke.set( absbubble )
            self.faded.append( letnoke )
            
            debug( 'eat', 'Abs-Bubble saved to Let:', letnoke(), letnoke().group )
        
        
            # Prepare Eaten
            
            # Det Cover Transformation (Lambda Bubble covers Eaten Bubbles)
            absbubbleTransform = TransformMatrix( ring= absbubble.ring )
            lens = TransformMatrix()
            lens.setTranspose( 0,0, Figure.holeLens )  # Lens-effect in Hole
            cover = ( absbubbleTransform * lens ).inverse()

            # Transform all eaten Bubbles, as they are in Hole, not in Group
            for b in eating.eaten:
                bubble = b()
                bubble.ring  = bubble.ring.transform( cover )   # Redet position
                bubble.group = None
                
            debug('eat','eaten transformed and ungrouped', eating.eaten )

        
            
            # Descend
            
            def descent( noke, group, matrix ):
                # If 'noke' has Bubble, Bubble.ring already set.
                
                debug( 'eat', 'descend:', noke )
    
                if APPL == noke.node.type:      # Group inside some Lambda, 'matrix' must be None
                    
                    debug('eat','appl found',noke)
                    
                    group = noke.group()
                    for b in noke.bubblesDraw():
                        # b().ring stays on its place
                        matrix = TransformMatrix( ring= b().ring )
                        descent( b, group, matrix )    # Pass matrix, because there inside fading vars may be bubbles of this group
    
    
                elif ABS == noke.node.type:
                    noke = noke['expr'].through()   # Noke inside Abs - no position needed
                    descent( noke, None, None )
    
                
                elif VAR == noke.node.type and abs == noke.node.ref:
                
                    # Mark Bubble as fading
                    bubble = noke()
                    if not bubble:          # This Var may be inside Lambda and do not have 'bubble'
                        bubble = Bubble()   # Create Bubble without 'group'
                        noke.set( bubble )
                    bubble.fading = self
                    self.faded.append( noke )
                    
                    debug('eat','it s hole. added to faded:', self.faded )
                    
    
                    if not matrix:
                        matrix = TransformMatrix()
                        matrix.unit()
    
                    
                    # Copy eaten branch to inside of fading Var
                    
                    noke = Noke( letnoke.node.be, addkey( noke.node, noke.key ) )

                    debug('eat','ref-be:',noke)
                    debug('eat','eaten:',eating.eaten)

                    for b,h in zip( noke.bubblesDraw(), eating.eaten ):
                        
                        debug( 'eat', 'found in Hole:', b, h )
                        
                        # Copying Eaten Bubble
                        bubble = Bubble()
                        bubble.ring  = h().ring.transform( matrix )      # Redet position
                        bubble.group = group
                        b.set( bubble )
                        
                        # Copy remained Bubbles inside Eaten if are
                        if ABS == b.node.type:
                            for b,h in zip( b['expr'].bubbleNokes(),  \
                                            h['expr'].bubbleNokes() ):
                                Noke.copyBubble( b, h )
        
        
    
            # Get next Node down the fading Lambda
            group  = eating.group
            matrix = absbubbleTransform * Figure.lambdaMatrix.inverse()
    
            down = letnoke['expr'].through()   # Step inside Lambda
            
            debug('eat','down',down,down())
            
            if APPL == down.node.type:      # Appl after fading Lambda
                
                # Redet 'group' and positions of Bubbles of Group
                for b in down.bubblesDraw():
                    bubble = b()
                    matrix1 = matrix * bubble.transform()
                    bubble.ring  = Ring.unit.transform( matrix1 )   # Reset Position of Bubble
                    bubble.group = group                            # and Group
                    descent( b, group, matrix1 )    # Pass matrix, because there inside fading vars may be bubbles of this group
                
            
            else:  # VAR or ABS
                
                # Create Bubble and set 'group'
                bubble = Bubble()
                bubble.ring  = Ring.unit.transform( matrix )
                bubble.group = group
                down.set( bubble )
                descent( down, group, matrix )
                
            
            
            
            # Delete Bubbles on eaten branch
            for h in eating.eaten:
                h.remove()


        # Reref now
        let.expr.replace( {abs:let} )
            
        debug('eat', '\n' )
        
        return Enduring.start( self )



    def handler( self ):

        ks = self.timefuncs()
        self.fade = 1.0 - ks['fade'][0]


        if not self.released and self.cur > 0.5:    # Start Release at half of Fading
            yield  Release( self.act ).start()
            self.released = True


        if self.end:
            # Remove faded Bubbles from Let- and Var-Expressions
            for noke in self.faded:
                noke.remove()
        else:
            yield self.event





class Release( Enduring ):

    def __init__( self, act ):
        self.act    = act        # Eating act (process)
        self.morphs = []

    
    def start( self ):
    
        # Start time func-s
        funcs = { 'pos': Enduring.I, 'r': Enduring.I }
        Enduring.__init__( self, Act.secRelease, funcs )
    
    
        figure = self.act.figure

        # Archive Bubbles and Groups of Figure before rebuilding
        for noke in figure.root().bubbleNokes():
            if noke():
                noke.save()     # Save to archive
                noke.remove()   # Remove original

        sizeRing = figure.sizeRing.copy()
        
        
        # Rebuild Figure
        figure.buildGroups()
        figure.buildGeometry()
        
        #debug('eat','afterbuild', figure.root().through()() )
        
        # Det Morphs
        
        modifiedGroups = {}     # dict {old group: new group}
        # ?? Here must be more smart Group marker
        # All parent groups of current must be marked (their Bounding Ring may be changed)
        
        for noke in figure.root().bubbleNokes():
            
            debug('eat','noke of figure',noke,noke())
            
            loaded = noke.load()    # Load from archive saved current Ring of Bubble
            if loaded:
                bubble = noke()
                
                if not bubble:
                    bubble = Bubble()
                    noke.set( bubble )
                
                self.morphs.append( Morph( loaded.ring, bubble.ring.copy() ) )
                debug('eat','added morph',noke,loaded.ring, loaded.group, bubble.ring)
                
                # Restore current Bubble attributes
                bubble.ring   = loaded.ring
                bubble.fading = loaded.fading
                # bubble.group = loaded.group ??
                
                # Mark group as modified (for morphing of its Bounding Ring)
                if loaded.group and  loaded.group not in modifiedGroups:
                        
                    if not bubble.group:            # This Group disappears at this Eating
                        bubble.group = Group()      # Create it for a time of Release
                        # ?? group for each bubble
                        bubble.group.boundingRing = Ring((0,0),1)
                    
                    modifiedGroups[ loaded.group ] = bubble.group
                    

                # Remove Archive
                noke.clean()
                

        # Morph Figure sizeRing
        self.morphs.append( Morph( sizeRing, \
                                   figure.sizeRing.copy(), \
                                   figure.refreshTransform ) )
        figure.sizeRing = sizeRing        # Restore current
        figure.refreshTransform()
        
            
        # Morph Bounding Rings of modified Groups
        for loaded,group in modifiedGroups.iteritems():
            
            debug('eat','group for morph', loaded.rootnoke, loaded.boundingRing )
            
            self.morphs.append( Morph( loaded.boundingRing, \
                                       group.boundingRing.copy(), \
                                       group.resetBoundingMatrix ) )
            group.boundingRing = loaded.boundingRing     # Restore current
            group.resetBoundingMatrix()
        

        return Enduring.start( self )



    def handler( self ):

        ks = self.timefuncs()
        kpos,kr = ks['pos'][1], ks['r'][1]
        
        
        for m in self.morphs:

            m.ring0.mix( kpos,kr, m.ring0, m.ring1 )
            
            if m.after:
                m.after()
        
        
        
        Bubble.dirs.reset()

        if self.end:
            # End of Eating
            self.act.end()

        else:
            yield self.event



class Eating:
    """
    Eating act. Data about Eating process.
    Phases: 1 Cover, 2 Fading, 3 Release.
    """

    def __init__( self, abs ):
    
        # Nokes
        self.abs   = abs
        self.appl  = self.abs.up()
        self.arg   = self.appl['arg']
        #self.let   = None

        # Group of Redex
        self.group = self.abs().group
        
        # Get Eaten Bubbles
        self.eaten = list( self.arg.bubblesDraw() )
        debug( 'eat', 'eaten', self.eaten )
    


class Act:
    
    # Length of phases
    secAct = float( config.get( 'eatingsec', 1.5 ) )
    secCover   = secAct / 3
    secFading  = secAct / 3
    secRelease = secAct / 3
    
    
    def __init__( self, figure, abs, callback ):
        
        self.figure   = figure
        self.abs      = abs
        self.callback = callback
        self.letnoke  = None    # for Figure.afterEating()
        self.appl     = abs.parent
        while not isinstance( self.appl, Application ):
            assert isinstance( self.appl, Let )
            self.appl = self.appl.parent

        debug( 'eat', 'init Eating. abs:', abs )
        
        # Create Eatings
        #  many if abs is inside some let-be expression
        self.eatings = []
        for key in abs.fission.iterkeys():
            noke = Noke( abs, key )
            self.eatings.append( Eating( noke ) )


        # Modified Groups
        self.modified = set()

        
        
    def start( self ):
        return Cover( self ).start()


    def end( self ):
        self.callback( self.figure )   # Call back

