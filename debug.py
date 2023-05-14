


# Int Flag (Level)
debuglevel = 3

# Str Flag (Tags)
debugtags = { 'refs':0, 'input':0, 'build':0, 'red':1, 'con':1, 'parse':1,  \
              'eat':0, 'event':0, 'hist':1, 'draw':0, 'color':0, 'save':1 }





# Level if Flag is not passed
defaultlevel = 2


def debug( *args ):
    """Prints debug information to output.
    Format:  
             Flag         Data
    debug( int level,  data,data,data,.. )   by debuglevel
    debug( str tag,    data,data,data,.. )   by debugtag
    debug(             data,data,data,.. )   simple output
    """

    if not debuglevel or not args:
        return

        
    def output( args ):
        print(" ".join(str(a) for a in args))


    if 1 == len( args ):
        return output( args )
        

    flag = args[0]                  # Int or Str Flag

    if type( flag ) is int:
        if flag < debuglevel:
            output( args[1:] )
        return 

    elif type( flag ) is str  and  flag in debugtags:
        if debugtags[ flag ]:
            output( args[1:] )
        return 

    else:                           # No Flag - Default Level
        if defaultlevel < debuglevel:
            output( args )
        return 
        
        

def debugTag( tag ):
    return  tag in debugtags  and  debugtags[ tag ]
        
        
        
        
    
    
    
    
    






