
import  os
from    xml.dom     import  minidom

from    debug       import  *

from    lambdaparser import parser
from    figure      import  Figure
from    fielditem   import  TextItem,RectItem

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
        item.setAttribute( 'pos', '%s,%s' % (format(pos[0]), format(pos[1])) )
        
        if isinstance( i, Figure ):
            refnames.reset()
            item.setAttribute( 'figure', repr(i.expression.expr) )
        
        elif isinstance( i, TextItem ):
            item.setAttribute( 'text', i.text )

        elif isinstance( i, RectItem ):
            item.setAttribute( 'rect', '%s,%s' % (format(i.size[0]), format(i.size[1])) )
            item.setAttribute( 'color', i.color )

        items.appendChild( item )

    if pretty:
        return doc.toprettyxml(indent=' ', newl='\n')
    else:
        return doc.toxml()


def format(x):
    return f"{round(x, 2):g}"

def to_tuple(attr):
    p = attr.split(',')
    return tuple(map( float, p ))


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
        elif item.hasAttribute('rect'):
            size = to_tuple(item.getAttribute('rect'))
            i = RectItem( size, item.getAttribute('color') )
        if i:
            pos = to_tuple(item.getAttribute('pos'))
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

