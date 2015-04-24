


class Cache:
    

    def __init__( self, func ):
        self.dict = {}
        self.func = func


    def __setitem__( self, key, value ):
        self.dict[ key ] = value        
        
    def __getitem__( self, key ):
        try:
            return self.dict[ key ]
        except KeyError:
            value = self.func( key )
            self.dict[ key ] = value
            return value

        
    def reset( self ):
        self.dict = {}
   






