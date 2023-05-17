

import  datetime

import  pygame
from    pygame.locals  import * 

import  cursors
import  toolbar

from    debug       import  * 
from    common      import  * 

from    vector      import  *
from    matrix      import  *

from    window      import  Window

import  let
import  lambdaparser
import  refnames

from    figure      import  Ring,Bubble,Group,Figure
from    noke        import  Noke

from    fielditem   import  TextItem

import  eating
import  construct

import  config

import  saving

from    events      import  *



def strDate():
    return datetime.datetime.now().strftime('%y%m%d_%H%M%S')



class Selection:
    "Selection. For selection, highlight, picking"
    
    def __init__( self, item, noke= None ):
        self.item = item
        self.noke = noke
        if not noke and isinstance( item, Figure ):    # Select whole Expression if noke not specified
            self.noke = item.root().through()

    def __nonzero__( self ):
        return bool( self.item )

    def __eq__( self, other ):
        return self.item == other.item and  \
               self.noke == other.noke

    def __repr__( self ):
        return '%s %s' % (repr(self.item), repr(self.noke))

    def figure( self ):
        return self.item and isinstance( self.item, Figure ) and self.item
    def text( self ):
        return self.item and isinstance( self.item, TextItem ) and self.item



# Decorators

def needSelectedItem( eventProc ):
    
    def standartEventProc( self ):
        if self.selection:
            return eventProc( self, self.selection.item )
        
    return standartEventProc
    

def needSelectedFigure( eventProc ):
    
    def standartEventProc( self ):
        figure = self.selection.figure()
        if figure:
            noke = self.selection.noke
            return eventProc( self, figure, noke )
        
    return standartEventProc


def assertNoEating( eventProc ):
    
    def standartEventProc( self, figure, noke ):
        if not figure.eating:
            return eventProc( self, figure, noke )
        
    return standartEventProc


def rebuildAfter( eventProc ):
    
    def standartEventProc( self ):
        figure = eventProc( self )          # Do eventProc
        if isinstance( figure, Figure ):
            figure.clean()                  # Rebuild after
            figure.buildGroups()
            figure.buildGeometry()
            self.invalidate()
    
    return standartEventProc


def stopNonstop( eventProc ):
    
    def standartEventProc( self ):
        if self.nonstop:
            self.nonstop = False
            debug(4, "stop nonstop!")
        else:
            return eventProc( self )        # Do eventProc
    
    return standartEventProc



class Manipulator( Window ):

    def __init__( self, caption ):

        windowSize = tuple(map(int, config.get( 'windowsize', '600x450' ).split("x")))

        Window.__init__( self, caption, windowSize )

        self.items = []
        
        
        # Load default workspace
        filename = config.get( 'workspace', 'default_workspace.xml' )
        if filename:
            if not saving.load( self, filename ):
                print("Can't open default workspace")
        

        
        self.expandMatrix = TransformMatrix()
        self.expandMatrix.setExpand( Figure.expandCoef )

        self.viewMatrix = None
        self.viewMatrix = self.defaultView( self.size, 35 )


        self.selection = Selection( None )
        self.selectionChanged = True        # Used to update statusbar text
        self.highlight = Selection( None )  # Dragging Figure over another Figure
        self.dragPos   = None               # Start drag position


        self.mode = let.Mode()              # Mode of reduction
        
        self.quick = False                  # Quick Reduction
        self.cursors = ( cursors.arrow, cursors.finger )
        self.setCursor( self.cursors[ int( self.quick ) ] )
        
        self.nonstop = False                # Nonstop reduction mode
        
        self.showInfo = True
        
        
        # Drawing 
        self.boldLambda = int( config.get( 'bold_lambda', 0 ) )

        
        
        self.eventProcs = { K_i:            self.eventInputItem,
                            K_d:            self.eventDeleteItem,
                            K_c:            self.eventCopyItem,
        
                            K_RETURN:       { KMOD_CTRL:    self.eventNonstop,
                                              None:         self.eventReduce },

                            K_BACKSPACE:    self.eventUndo,
                            K_z:            { KMOD_CTRL:    self.eventUndo },
                            K_y:            { KMOD_CTRL:    self.eventRedo },
                            K_LEFT:         { KMOD_ALT:     self.eventUndo },
                            K_RIGHT:        { KMOD_ALT:     self.eventRedo },
                            
                            K_SPACE:        self.eventExpandSelection,                            
                            K_DELETE:       self.eventDeleteNode,
                            K_INSERT:       { KMOD_ALT:     self.eventAddLambda,
                                              KMOD_CTRL:    self.eventAddApplicationAfter,
                                              None:         self.eventAddApplicationBefore },


                            K_s:            { KMOD_CTRL:    self.eventSave,
                                              KMOD_ALT:     self.eventModeBySelection },
                            K_o:            { KMOD_CTRL:    self.eventLoad },
                            
                            K_q:            self.eventModeQuick,
                            K_a:            { KMOD_ALT:     self.eventModeStrategy,
                                              KMOD_CTRL:    self.eventAddApplicationAfter,
                                              None:         self.eventAddApplicationBefore },
                            K_l:            { KMOD_ALT:     self.eventModeLazy,
                                              None:         self.eventAddLambda },
                            K_v:            self.eventAddVariable,
                            K_p:            { KMOD_ALT:     self.eventModeLazy },

                            K_e:            { KMOD_ALT:     self.eventExportMode },
                            
                            K_F1:           self.eventViewHelp,
                            K_F5:           self.eventRefreshView,
                            K_F12:          self.eventSaveScreen   }




    
        #-----------------------------------------------------
        # Prepare toolbars
        
        self.statusbar = toolbar.Statusbar()
        self.toolbars = []

        ims = toolbar.ImageSet( 'toolbar_icons.png', (48,48) )
        
        # Create font for Menus
        fontsize = int( config.get( 'fontsize' ) )  or  11
        toolbar.ToolbarItem.fontsize = fontsize
        toolbar.ToolbarItem.font     = pygame.font.SysFont( 'lucidaconsole', fontsize )
        
        left = toolbar.Toolbar( toolbar.LEFT )
        left.add( self.eventInputItem,              'Input Item from console (I)',   'Input Item' )
        left.add( None, None, '' )
        left.add( None, None, 'Reduction' )
        left.add( self.eventModeStrategy,           'Toggle reduction strategy (Alt+A)',    ' Normal order',     ' Applicative',  lambda:self.mode.applicative )
        left.add( self.eventModeLazy,               'Toggle calculus (Alt+L, Alt+P)',       ' Pure Lambda',      ' Lazy',         lambda:self.mode.lazy )
        left.add( self.eventModeBySelection,        'Reduction inside selection only or the whole expression (Alt+S)',  
                                                                           ' whole expression', ' in selection', lambda:self.mode.redex )
        left.add( None, None, '' )
        left.add( self.eventSave,                   'Save Workspace. Input file name from console. (Ctrl+S)',  'Save' )
        left.add( self.eventLoad,                   'Load Workspace. Input file name from console. (Ctrl+O)',  'Load' )
        self.toolbars.append( left )
    
        right = toolbar.Toolbar( toolbar.RIGHT )
        right.add( self.eventModeQuick,             'Quick mode: Pick for reduction. (Q)',          (ims,2,1), (ims,2,2), lambda:self.quick )
        right.add( self.eventAddVariable,           'Add a free variable to workspace (V)',         (ims,0,0) )
        right.add( self.eventAddApplicationBefore,  'Add application before selection (Insert, A)', (ims,0,1) )
        right.add( self.eventAddApplicationAfter,   'Add application after selection (Ctrl+Insert, Ctrl+A)', (ims,0,2) )
        right.add( self.eventAddLambda,             'Add lambda bubble (Alt+Insert, L)',            (ims,1,2) )
        right.add( self.eventDeleteNode,            'Delete selected bubbles (Delete)',             (ims,1,1) )
        right.add( self.eventDeleteItem,            'Delete selected item (D)',                     (ims,1,0) )
        right.add( self.eventCopyItem,              'Copy selected item (C)',                       (ims,2,0) )
        self.toolbars.append( right )

        bottom = toolbar.Toolbar( toolbar.BOTTOM )
        bottom.add( self.eventUndo,                 'Undo (Ctrl+Z, Alt+Left, Backspace)',           (ims,3,1) )
        bottom.add( self.eventReduce,               'Reduce selected figure (Enter)',               (ims,3,0) )
        bottom.add( self.eventRedo,                 'Redo (Ctrl+Y, Alt+Right)',                     (ims,3,2) )
        self.toolbars.append( bottom )

        self.invalidate()



    def drawItems( self ):

        surface = self.getSurface()     # Draw on main surface

        for item in self.items[::-1]:

            matrix = self.viewMatrix * item.transform

            # Text
            if isinstance( item, TextItem ):
                self.drawText( surface, item.text, matrix )

            # Figure
            elif isinstance( item, Figure ):
        
                for drawn in item.ringsToDraw( matrix ):

                    done = self.drawRing( surface, item, drawn, self.size )   # Pass self.size

                    # Send data into Bubble.ringsToDraw() generator
                    Figure.drawing['done'] = done




    def drawText( self, surface, text, matrix ):
       
        vector = matrix * Vector((0,0,1,1))
        x,y,s,_ = tuple(map( toInt, vector ))
       
        self.text( text, (x,y) )
    


    @staticmethod
    def checkRanges( pos,r, size ):
        return  3 < r  and  \
                -r < pos[0] < size[0]+r  and  \
                -r < pos[1] < size[1]+r
        

    def circle( self, surface, pos, r, col=None, width=1 ):

        r = toInt( r )

        if r < 1:
            debug( 1, "Error: circle radius < 1" )
            return

        pos = tuple(map( toInt, pos ))

        col = self.getColor( col )
        
        pygame.draw.circle( surface, col, pos, r, width )


    
    def drawRing( self, surface, figure, drawn, size ):
        
        # Det position
        pos = drawn.ring.pos.x, drawn.ring.pos.y
        r   = drawn.ring.r
        #r   = int( round( drawn.ring.r ) )
        

        if not self.checkRanges( pos,r, size ):
            return False
        

        # Det stroke color: Not selected, Selected, Same Node
        if not self.selection:
            sel = None
        else:
            sel = self.selected( figure, drawn.noke, self.selection )
        stroke = { None:None, True:(0xFF,0x00,0x00), False:(0xFF,0x77,0x00) }[ sel ]
        if not sel:
            if self.highlight and self.selected( figure, drawn.noke, self.highlight ):
                stroke = (0xAA,0x00,0x00)
            
            
        
        # Det fill color
        isVar =  let.VAR == drawn.noke.node.type            # expr is VAR, ABS or LET
        
        abs = None      # Get Abstraction Node for fill color
        #print('get abs', drawn.__dict__)
        if drawn.fade:
            abs = drawn.noke().fading.act.abs
        elif isVar:            
            abs = drawn.noke.ref().node
        elif let.ABS == drawn.noke.node.type:
            abs = drawn.noke.node
        else:
            raise Exception("can't get abs")
           
        debug('draw', '- draw Noke', drawn.noke, isVar, abs )
        
        fill = figure.colorspace.color( abs )
        
        
        # Draw Ring
        
        if None != drawn.fade:
        
            fading = self.drawFading( drawn.fade, fill, stroke, r )
            if fading:
                surface.blit( fading, ( toInt( pos[0]-r ), toInt( pos[1]-r ) ) )
            else:
                #fill = (0xFF,0xFF,0xFF)
                debug(2,'Error. drawFading fail.')
                self.circle( surface, pos,r, fill, 0 )
            
        
        else:
            # Fill
            if isVar and abs and 5<r:

                refNoke = drawn.noke.ref()
                debug('draw', 'refNoke', refNoke, figure.expression )
                
                if refNoke.isRedex():       # Try to draw Hole
            
                    debug('draw', 'try hole' )
                    
                    hole = self.drawHole( figure, refNoke, fill, r )
    
                    if hole:
                        surface.blit( hole, ( toInt( pos[0]-r ), toInt( pos[1]-r ) ) )
                    else:
                        #fill = (0x77,0x77,0x77)   # Hole Error
                        debug('draw', 'hole error' )
                        self.circle( surface, pos,r, fill, 0 )
                       
                else:
                     self.circle( surface, pos,r, fill, 0 )
                
            else:   # Do not draw Hole
                 self.circle( surface, pos,r, fill, 0 )
                

                
            # Stroke
            width = self.boldLambda and not isVar and 2  or  1
            self.circle( surface, pos,r, stroke, width )


        return True



    def drawHole( self, figure, noke, fill, r ):

        debug('draw', 'draw hole, noke:', noke )

        # Get Bubble of Abs
        bubble = noke()
        if not bubble:  return                  # Abs is inside Abstraction - without any application

        # Get Root of Childs for eating
        if not bubble.childs:  return           #  ?? abs must be Redex?
        #child = bubble.childs[0]()
        arg = noke.up()['arg']                  # Get Noke of argument of Redex
        
        
        # Size
        d = toInt( r*2 )
        size = d,d

        # Det Matrix
        lens = TransformMatrix()
        lens.setTranspose( 0,0, Figure.holeLens )      # Lens-effect in Hole
        cover = ( TransformMatrix( ring= bubble.ring ) * lens ).inverse()
        matrix = self.defaultView( size ) * cover
        matrix *= bubble.group.transformMatrix.inverse()        # Because of multiplying on bubble.group.transformMatrix at Figure.ringsToDraw()

        # Init Surfaces later, if needed
        surface = None
        
        # Draw Rings from first Child only
        for drawn in figure.ringsToDraw( matrix, arg ):

            if not surface:     # Init Surfaces once
                surface = pygame.Surface( size )
                surface.fill( fill )
                #surface.fill( (111,88,33), pygame.Rect(10,10,20,60) )
            
        
            done = self.drawRing( surface, figure, drawn, size )
        
            # Send data into Bubble.ringsToDraw() generator
            Figure.drawing['done'] = done

        
        if not surface:         # Nothing were drawn
            return
            
    
        # Draw Mask
        colorMask1 = 0,0xFE,0   # ?? other colors!
        colorMask2 = 0xFE,0,0
        mask = pygame.Surface( size )
        mask.fill( colorMask1 )
        r = toInt(r)
        pygame.draw.circle( mask, colorMask2, (r,r),r, 0 )
        mask.set_colorkey( colorMask2, RLEACCEL )
        surface.blit( mask, (0,0) )
        surface.set_colorkey( colorMask1, RLEACCEL )

        return surface
        
    
    def drawFading( self, fade, fill, stroke, r ):

        # Size
        d = toInt( r*2 )
        size = d,d
        
        # Mask
        colorMask1 = 0,0xFE,0

        r = toInt(r)

        surface = pygame.Surface( size )
        surface.fill( colorMask1 )
        self.circle( surface, (r,r),r, fill, 0 )
        self.circle( surface, (r,r),r, stroke, 1 )
        
        surface.set_alpha( int(round(fade * 255)) )
        surface.set_colorkey( colorMask1, RLEACCEL )

        return surface



    # View Matrix

    def centerOfView( self ):
        "Returns the center of view according to viewMatrix"

        cx = self.size[0] * 0.5
        cy = self.size[1] * 0.5
        
        return self.viewMatrix.inversion * Vector( (cx,cy,0,1) )
        

    
    def defaultView( self, size, scale= None ):
    
        cx = size[0] * 0.5
        cy = size[1] * 0.5
    
        t = TransformMatrix()
        t.setTranspose( cx,cy, scale or cy )
        
        r = TransformMatrix()
        r.setReflection()
    
        return t * r

    
    def zoomView( self, pos, button ):
        
        t = TransformMatrix()
        t.setTranspose( pos.x, pos.y, 1 )
        
        k = 1.35 ** ( 4==button and 1 or -1 )
        z = TransformMatrix()
        z.setTranspose( 0,0, k )
        
        self.viewMatrix = t * z * t.inverse() * self.viewMatrix

    def updateSelectionStatus( self ):
        # Collect selection status lines
        lines = []
        
        s = self.selection
        if s.figure():
            node = s.noke.node              # Selection
            expr = s.item.expression.expr   # Whole Figure
            if node and node != expr:
                lines.append("Selection: %s" % node)
            if expr:
                lines.append("Term: %s" % expr)
        elif s.text():
            lines.append("Text: %s" % s.item.text)
        
        # Update statusbar text
        self.statusbar.setText(*lines)
        
        # Also print the whole selection to console
        for l in lines: print(l)
        

    def paint( self ):
        "Draws and flips bg and rings"
        
        surface = self.getSurface()
        
        # Erase
        self.erase()
        
        # Draw Field Items
        self.drawItems()
        
        # Export Frame as bitmap
        if Enduring.exportMode:
            filename = 'frame_%s_%05d.bmp' % ( strDate(), Enduring.exportModeFrame )
            Enduring.exportModeFrame += 1
            
            pygame.image.save( surface, filename )
            debug(1, 'Frame saved:', filename )

        # Draw Toolbars
        for t in self.toolbars:
            t.draw( surface, self.size )
        
        # Update Statusbar
        if self.selectionChanged:
            self.selectionChanged = False
            self.updateSelectionStatus()
        self.statusbar.draw( surface, self.size )
        
        # Flip screen
        self.flip()


    def handleEvent( self, event ):

        #print('handleEvent', event)

        if event.type in ( MOUSEBUTTONDOWN, MOUSEBUTTONUP, MOUSEMOTION ):
            
            pos = Vector2( event.pos )
            
            if MOUSEBUTTONDOWN == event.type:

                #test self.addUserEvent( TEMPEVENT, pos=(2,3), ptr=self )
            
                debug( 'input', 'MOUSEBUTTONDOWN. button', event.button )
                
                modCtrl = pygame.key.get_mods() & KMOD_CTRL
                
                if event.button in (4,5):   # Wheel UP or DOWN  -  Zoom
                    if self.items:        # Don't zoom if no Figures
                        self.zoomView( pos, event.button )
                        self.invalidate()
                
                elif event.button == 1 and not modCtrl:  # Left Button (without Ctrl)

                    # Toolbars
                    item = self.pickToolbarItem( pos )
                    if item:
                        if item.callback():
                            self.invalidate()
                    
                    else:
                        if self.select( pos ):  # Select
                            if self.quick:              # Try to reduce at once
                                self.eventReduce()
                            self.invalidate()
                        
                
                elif event.button == 3 or event.button == 1 and modCtrl:   # Right Button or Left Button with Ctrl
                    if self.selection.figure(): # Try to Reref Selected Var or Abs
                        pick = self.pick( pos, figuresOnly= True )
                        if pick and pick.item == self.selection.item:
                            figure = pick.item
                            sel  = self.selection.noke.node
                            pick = pick.noke.node
                            # Try to reref
                            reref = False
                            if let.ABS == sel.type and let.VAR == pick.type:
                                reref = construct.reref( pick, sel )
                            elif let.VAR == sel.type and let.ABS == pick.type:
                                reref = construct.reref( sel, pick )
                            if reref:
                                figure.history.step( figure.expression.copy() )
                                self.invalidate()
                        
                

            if MOUSEBUTTONUP == event.type: # End Drag
                
                # Dropping
                if self.dragPos and self.selection.figure() and self.highlight.figure():
                    #debug(2,'dropped',self.selection.item.expression,'-->',self.highlight.noke)
                    dragged = self.selection.item
                    
                    construct.applicate( dragged.expression.expr, 
                                         self.highlight.noke.node )
                    
                    self.items.remove( dragged )
                    
                    new = self.highlight.item

                    new.history.step( new.expression.copy() )

                    new.detColorSpace()
                    new.clean()
                    new.buildGroups()
                    new.buildGeometry()
                    self.selection = Selection( new )
                    self.selectionChanged = True
                    self.highlight = Selection( None )
                    self.invalidate()
                    
                
                self.dragPos = None
    
    
            elif MOUSEMOTION == event.type:
                
                redraw = None
                
                # Highlight Nokes at dragging
                if self.dragPos:
                    redraw = self.mouseOver( pos )
                
                # Move dragged Bubble
                if event.buttons[0]:
                    if self.dragPos:
                        self.drag( pos )
                        redraw = True
                
                # Toolbars
                if not event.buttons[0] and not event.buttons[1]:
                    item = self.pickToolbarItem( pos )
                    if item != toolbar.ToolbarItem.highlighted:
                        toolbar.ToolbarItem.highlighted = item
                        if self.showInfo and item and item.tip:
                            print('tip:', item.tip)
                            self.statusbar.setText(item.tip)
                        else:
                            self.statusbar.setText()
                        redraw = True

                if redraw:
                    self.invalidate()
    


        elif KEYDOWN == event.type:

            try:
                proc = self.eventProcs[ event.key ]

                if callable( proc ):
                    proc()
                
                elif type( proc ) is dict:
                    mods = pygame.key.get_mods()
                    for key in proc.keys():
                        if not key  or mods & key:
                            proc[ key ]()
                            break

            except KeyError:
                pass

            
        
        elif pygame.USEREVENT <= event.type:
            
            if TIMEREVENT == event.type:
                pass
                
            elif ENDURINGEVENT == event.type:
                for e in event.data.handler():
                    self.addEvent( e )
                self.invalidate()
                
                
            elif COLOREVENT == event.type:
                for e in event.data.handler( event ):
                    self.addEvent( e )

            else:
                #print('got USEREVENT', event)
                pass



        Window.handleEvent( self, event )


    #---------------------------------------------
    # Event Procs

    def eventInputItem( self ):

        # Get Item
        expression = self.consoleInput('Input Expression >> ')
        if expression:        
            if expression[0] in ('"',"'"):
                item = TextItem( eval(expression) )
            else:
                item = Figure( expression )
    
            # Set position to center of view
            v = self.centerOfView()
            item.position.setTranspose( v[0],v[1], 1 )
            item.refreshTransform()
            
            self.items.insert( 0, item )
            self.invalidate()

    
    @needSelectedItem
    def eventCopyItem( self, item ):
        copy = item.copy()
        self.items.insert( 0, copy )
        self.selection = Selection( copy )
        self.selectionChanged = True
        self.invalidate()

    @needSelectedItem
    def eventDeleteItem( self, item ):
        if self.selection.item in self.items:
            self.items.remove( self.selection.item )
        self.selection = Selection( None )
        if self.items:
            self.selection = Selection( self.items[0] )
        self.selectionChanged = True
        self.invalidate()



    @stopNonstop
    @needSelectedFigure
    @assertNoEating
    def eventReduce( self, figure, noke ):
        if self.reduce( figure ):
            self.invalidate()
    
    @stopNonstop
    @needSelectedFigure
    @assertNoEating
    def eventNonstop( self, figure, noke ):
        self.nonstop = True
        if self.reduce( figure ):
            self.invalidate()



    @rebuildAfter
    @needSelectedFigure
    @assertNoEating
    def eventUndo( self, figure, noke ):
        expression = figure.history.undo()
        if expression:
            figure.expression = expression.copy()
            figure.detColorSpace()
            self.selection = Selection( figure )
            self.selectionChanged = True
            return figure

    @rebuildAfter
    @needSelectedFigure
    @assertNoEating
    def eventRedo( self, figure, noke ):
        expression = figure.history.redo()
        if expression:
            figure.expression = expression.copy()
            figure.detColorSpace()
            self.selection = Selection( figure )
            self.selectionChanged = True
            return figure


    # Construct

    @needSelectedFigure
    def eventExpandSelection( self, figure, noke ):
        up = noke.up()
        if up.node != self.selection.item.expression:   # Do not select Root
            self.selection.noke = up
            debug(1, 'selected:', up.node )
            self.invalidate()

    @rebuildAfter
    @needSelectedFigure
    @assertNoEating
    def eventDeleteNode( self, figure, noke ):
        construct.delete( noke.node )
        figure.history.step( figure.expression.copy() )
        self.selection = Selection( figure )
        self.selectionChanged = True
        return figure

    @rebuildAfter
    @needSelectedFigure
    @assertNoEating
    def eventAddLambda( self, figure, noke ):
        abs = construct.addLambda( noke.node )
        figure.history.step( figure.expression.copy() )
        figure.colorspace.add( None, [[abs]] )      # ??
        self.selection = Selection( figure, noke.up() )
        self.selectionChanged = True
        return figure

    @rebuildAfter
    @needSelectedFigure
    @assertNoEating
    def eventAddApplicationBefore( self, figure, noke ):
        construct.applicationBefore( noke.node )
        figure.history.step( figure.expression.copy() )
        self.selection = Selection( figure, noke.up() )
        self.selectionChanged = True
        return figure

    @rebuildAfter
    @needSelectedFigure
    @assertNoEating
    def eventAddApplicationAfter( self, figure, noke ):
        construct.applicationAfter( noke.node )
        figure.history.step( figure.expression.copy() )
        self.selection = Selection( figure, noke.up() )
        self.selectionChanged = True
        return figure


    def eventAddVariable( self ):
        fig = Figure( let.Variable() )

        # Set position to center of view
        v = self.centerOfView()
        fig.position.setTranspose( v[0],v[1], 1 )
        fig.refreshTransform()
        
        self.items.insert( 0, fig )
        self.invalidate()


    def eventLoad( self ):
        filename = self.consoleInput('Load Workspace >> ')        
        if filename and saving.load( self, filename ):
            self.invalidate()

    def eventSave( self ):
        filename = self.consoleInput('Save Workspace >> ')
        if filename:
            saving.save( self, filename )

    def eventSaveScreen( self ):
        pygame.image.save( self.getSurface(), 'screen_%s.bmp' % strDate() )


    def eventRefreshView( self ):
        if self.items:
            for item in self.items:
                if isinstance( item, Figure ) and not item.eating:
                    self.postReduce( item )  # Some garbage or rearrange
                    item.detColorSpace()
                    item.buildGroups()
                    item.buildGeometry()            
            self.invalidate()
            refnames.reset()    # Reset refnames here too
                                    

    def eventViewHelp( self ):
        self.showInfo ^= True
        if self.showInfo:
            print('Show Tips')
        else:
            print("Don't show Tips")
        #self.invalidate()

    def eventModeStrategy( self ):
        self.mode.applicative ^= True
        self.invalidate()

    def eventModeLazy( self ):
        self.mode.lazy ^= True      # Lazy or Pure
        self.invalidate()

    def eventModeBySelection( self ):
        self.mode.redex ^= True     # Redex by Selection
        self.invalidate()

    def eventModeQuick( self ):
        self.quick ^= True          # Quick Reduction Mode
        self.setCursor( self.cursors[ int( self.quick ) ] )
        self.invalidate()



    def eventExportMode( self ):
        Enduring.exportMode ^= True
        debug( 1, "Export Mode:", Enduring.exportMode )




    def pick( self, pos, figuresOnly= False ):

        for item in self.items:
            
            if isinstance( item, TextItem ):
                if not figuresOnly:
                    matrix = self.viewMatrix * item.transform
                    if item.pick( self.font, matrix, pos ):
                        return Selection( item )

            
            elif isinstance( item, Figure ):
                
                # Do not pick dragged Figure or Figure at Eating
                if item.eating  or  \
                   self.dragPos and item == self.selection.item:
                     continue
                
                matrix = self.viewMatrix * item.transform
                noke = last( item.pick( matrix, pos ) )   # Last picked (top level) Expression
                if noke:
                    return Selection( item, noke )
                    
           
        
    def selected( self, figure, noke, selection ):
        """
        Returns True | False | None:
        selected | same Node | Not selected
        """
        
        if figure == selection.figure():
            
            sel = selection.noke
            
            if let.APPL == sel.node.type:
                for n in sel.bubblesDraw():
                    if n.node == noke.node:
                        return n.key == noke.key
           
            if sel.node == noke.node:
                return sel.key == noke.key
        
        

    
    def mouseOver( self, pos ):
        
        if self.selection.figure():
        
            pick = self.pick( pos, figuresOnly= True )
            
            if pick:

                if not ( let.VAR == pick.noke.node.type and not pick.noke.node.ref ):    # if not Free Variable
                    pick.noke = last( pick.noke.withAppls() )       # With Appls!
            
                if not self.highlight or self.highlight != pick:
                     self.highlight = pick
                     return True
            else:
                if self.highlight:
                    self.highlight = Selection( None )
                    return True
        
        return False
        
    

    def select( self, pos ):
        
        pick = self.pick( pos )

        if pick:

            item = pick.item
            
            # Bring Selected Figure to top
            if item != self.items[0]:
                self.items.remove( item )
                self.items.insert( 0, item )


            if isinstance( item, Figure ):
                # Toggle Selection of Appl-s
                withAppls = list( pick.noke.withAppls() )
                if 1 < len( withAppls ):
                    if not self.quick and  \
                       self.selection.figure() and  \
                       self.selection.noke in withAppls:
                        i = withAppls.index( self.selection.noke ) - 1
                        pick.noke = withAppls[ i ]
                    else:
                        pick.noke = withAppls[ -1 ]


            elif isinstance( item, TextItem ):
                #print()
                #print('text:', pick.item.text)
                pass
                

            self.selection = pick        # {figure,noke}
            self.selectionChanged = True
                
            self.dragPos   = pos         # Save touched Ring and cursor start Position
            return True


        self.selection = Selection( None )    # Deselect
        self.selectionChanged = True
        self.dragPos   = None

        return True
        

    
    def drag( self, pos ):
    
        if not self.dragPos or not self.selection:
            return
        
        shift = pos - self.dragPos
        
        transform = TransformMatrix()
        transform.setTranspose( shift.x, shift.y, 1.0 )
        
        transform = self.viewMatrix.inverse() * transform * self.viewMatrix
        
        item = self.selection.item
        item.position = transform * item.position
        item.refreshTransform()
        
        self.dragPos += shift
        
    

    def reduce( self, figure ):
    
        self.mode.find = True
        
        if self.mode.redex or self.quick:       # Find Redex inside Selection
            sel = self.selection.noke
            
            if sel.derefable() and not sel.isRedexAppl():
                #print('derefable', sel)
                while sel.key:                  # Go outside from Be-Expressions
                    sel = sel.up()
                #print('after up. derefable?', sel)
                reduced = first( sel.node.deref() )
            
            else:
                reduced = sel.node.reduce( self.mode )

        else:                   # Find Redex in whole Expression
            expression = figure.expression.expr
            reduced = expression.reduce( self.mode )


        if reduced:
            #debug('red','reduced', reduced.__dict__, figure.expression )

            if let.BETA == reduced.result:      # Beta-redex found
                figure.eating = eating.Act( figure, reduced.data, self.afterEating )
                self.addEvent( figure.eating.start() )

            elif let.DEREF == reduced.result:   # Deref done
                figure.colorspace.add( reduced.data )
                self.selection.noke = Noke( reduced.data )   # Change Selection of Figure
                self.postReduce( figure )
                return True

        else:
            self.nonstop = False
            



    def afterEating( self, figure ):
        "Callback after Eating process."
        
        # Change Selection of Figure ??
        #self.selection = Selection( figure, figure.eating.letnoke.through() )
        #let = figure.eating.let
        self.selection = Selection( figure )
        self.selectionChanged = True
        #debug(2,'selected:',self.selection)
        
        figure.eating = None

        self.postReduce( figure )


    
    def postReduce( self, figure ):

        #debug('eat', 'after reduce:', figure.expression )

        for reduced in figure.expression.postReduce( self.mode ):
            if let.DEREF == reduced.result:
                figure.colorspace.add( reduced.data )
                self.selection = Selection( figure, Noke( reduced.data ) )
                self.selectionChanged = True
            # Else reduced.result is some garbage - do nothing
            
            debug('eat', reduced.result )
        
        #debug('eat', 'after arrange:', figure.expression )
        print()
        print('reduced:', figure.expression.expr)

        # Rebuild Figure
        figure.clean()
        figure.buildGroups()
        figure.buildGeometry()
        
        # Check Selection (it may be broken after Garbage)
        if self.selection and not self.selection.noke():
            self.selection.noke.key = ()
        
        # Step of History
        figure.history.step( figure.expression.copy() )
    
        if self.nonstop:
            self.reduce( figure )
            
    
    
    def pickToolbarItem( self, pos ):        
        for t in self.toolbars:
            item = t.pick( pos, self.size )
            if item:
                return item
        


Manipulator('Visual Lambda').run()


