
import  os
from    xml.dom     import  minidom

from    debug       import  *

from    lambdaparser import parser
from    figure      import  Figure
from    fielditem   import  TextItem

from    vector      import  Vector

import  refnames



def save( manipulator, pretty = False ):

    doc = minidom.Document()
    workspace = doc.createElement("workspace")
    doc.appendChild( workspace )

    label = doc.createElement( 'label' )
    label.setAttribute( 'name', 'Visual Lambda workspace' )
    workspace.appendChild( label )
    
    items = doc.createElement('items')
    workspace.appendChild( items )
    
    for i in manipulator.items:
        item = doc.createElement('item')

        pos = i.position * Vector((0,0,1,1))
        item.setAttribute( 'pos', '%f,%f' % (pos[0],pos[1]) )
        
        if isinstance( i, Figure ):
            refnames.reset()
            item.setAttribute( 'figure', repr(i.expression.expr) )
        
        elif isinstance( i, TextItem ):
            item.setAttribute( 'text', i.text )

        items.appendChild( item )

    if pretty:
        return doc.toprettyxml(indent=' ', newl='\n')
    else:
        return doc.toxml()



def load( manipulator, xmlData ):

    try:
        dom = minidom.parseString( xmlData )
    except:
        print("Error. Can't parse workspace xml")
        return False
    
    # Reset library local defines
    parser.lib.reset_local_items()
    
    # Load items
    manipulator.items = []
    lastOrigin = Vector((0, 0))
    for item in dom.getElementsByTagName('item'):
        
        # Define
        if item.hasAttribute('define'):
            parser.lib.add_line( item.getAttribute('define'), isGlobal = False )
            continue
        
        # Figure or Text item
        i = None
        if item.hasAttribute('figure'):
            i = Figure( item.getAttribute('figure') )
        elif item.hasAttribute('text'):
            i = TextItem( item.getAttribute('text') )
        if i:
            pos = item.getAttribute('pos').split(',')
            pos = tuple(map( float, pos ))
            pos = lastOrigin + Vector(pos)
            i.position.setTranspose( pos[0],pos[1], 1 )
            i.refreshTransform()
            manipulator.items.append( i )
            
            if item.hasAttribute('origin'):
                lastOrigin = pos
    
    dom.unlink()

    refnames.reset()

    return True



def save_to_file( manipulator, filename ):
    xml = save( manipulator, pretty = True )
    if not xml:
        return False
    
    filepath = os.path.join('workspaces', filename )
    with open( filepath, "w" ) as f:
        f.write(xml)
        f.close()
        debug('save', 'Workspace saved to', filename )
        return True
    
    print("Error. Can't write to", filepath)
    return False



def load_from_file( manipulator, filename ):
    filepath = os.path.join('workspaces', filename )
    
    xmlData = None
    with open( filepath, "r" ) as f:
        xmlData = f.read()
        f.close()
    
    if not xmlData:
        print("Error. Can't read (or empty)", filepath)
        return False

    
    if load( manipulator, xmlData ):
        debug('save', 'Workspace loaded from', filename )
        return True
    
    return False

