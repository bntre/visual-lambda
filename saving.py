
from    debug       import  * 

from    xml.dom     import  minidom


from    figure      import  Figure
from    fielditem   import  TextItem

from    vector      import  Vector

import  refnames


def save( manipulator, filename ):

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
            item.setAttribute( 'figure', `i.expression.expr` )
        
        elif isinstance( i, TextItem ):
            item.setAttribute( 'text', i.text )

        items.appendChild( item )

    try:
        f = open( filename, "w" )
        doc.writexml( f, addindent=' ', newl='\n' )
        f.close()
        debug('save', 'saved to', filename )
    except:
        print "Error. Can't write to", filename

    

    
def load( manipulator, filename ):

    try:
        dom = minidom.parse( filename )
    except IOError:
        print "Error. Can't read", filename
        return False

    manipulator.items = []
    for item in dom.getElementsByTagName('item'):
        
        i = None
        if item.hasAttribute('figure'):
            i = Figure( item.getAttribute('figure').encode() )
        elif item.hasAttribute('text'):
            i = TextItem( item.getAttribute('text').encode() )

        pos = item.getAttribute('pos').encode().split(',')
        pos = map( float, pos )
        i.position.setTranspose( pos[0],pos[1], 1 )
        i.refreshTransform()
        manipulator.items.append( i )
    
    dom.unlink()

    refnames.reset()

    debug('save', 'loaded from', filename )
    
    return True

        