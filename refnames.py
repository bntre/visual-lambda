

# Representation of References as Chars


chars = map(chr,range(97,123))   # Chars
count = len(chars)

vars = []
dict = {}
cur  = 0


def reset():
    global vars,dict,cur

    vars = []
    dict = {}
    cur  = 0


def next():
    """Returns next combination of chars
    in order: a,b,..z,aa,ab,..az,ba,bb,...zz,aaa,...
    """
    
    global chars,count,cur
    
    var = ''
    
    c = cur
    while 0 <= c:
        c, i  =  c//count - 1,  c%count
        var = chars[i] + var
        
    return var
    

def repr( ref ):
    global vars,dict,cur

    if ref not in dict:
        dict[ ref ] = next()
        cur += 1
    return dict[ ref ]
