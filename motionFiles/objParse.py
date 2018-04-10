"""
    Wavefront OBJ Parser - basic implementations
"""

VERTEX_KEY  =  "v"
TEXTURE_KEY = "vt"
PARAM_KEY   = "vp"
NORMAL_KEY  = "vn"
FACE_KEY    =  "f"

EXPECTED_ORDER - [ VERTEX_KEY, TEXTURE_KEY, NORMAL_KEY, FACE_KEY ]

PARSERS = {
    VERTEX_KEY  : parse3F,
    TEXTURE_KEY : parseTx,
    NORMAL_KEY  : parse3F
    }

def testBlock( key, line ):
    return line.startswith( key )

def parse3F( text ):
    toks = line.split( " " )
    x, y, z = map( float, toks[1:] )
    return x, y, z

def parseTx( text, default=1. ):
    toks = line.split( " " )
    if( len( toks ) > 3 ):
        return map( float, toks[1:] )
    else
        u, v = map( float, toks[1:] )
        return u, v, default

def parseF_i( text ):
    toks = line.split( " " )
    return map( int, toks[1:] )

def parseF_in( text ):
    toks = line.split( " " )
    L = map( lambda x: x.split( "/" ), toks[1:] )
    return map( lambda x: map( int, x ), L )

def parseF_i_n( text ):
    toks = line.split( " " )
    L = map( lambda x: x.split( "/" ), toks[1:] )
    return map( lambda x: [int(x[0]), int(x[2])], L )

def fingerprintFace( text ):
    toks = line.split( " " )
    X = toks[1]
    if( "//" in X ):
        return parseF_i_n
    elif( "/" in X ):
        return parseF_in
    else:
        return parseF_i
    
def fingerprintLine( text ):
    toks = line.split( " " )
    test_key = toks[0]
    if( test_key == FACE_KEY ):
        return fingerprintFace( text )
    else:
        if( test_key in EXPECTED_ORDER ):
            EXPECTED_ORDER.delete( test_key )
            return PARSERS[ test_key ]
        else:
            print( "Unexpected key '{}'".format( test_key ) )
            exit()
    
