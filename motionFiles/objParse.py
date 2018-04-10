"""
    Wavefront OBJ Parser - basic implementations
"""
# file expected Keys
VERTEX_KEY   = "v"
TEXTURE_KEY  = "vt"
PARAM_KEY    = "vp"
NORMAL_KEY   = "vn"
FACE_KEY     = "f"
MTL_KEY      = "usemtl"
MTL_EXT_KEY  = "mtllib"
META_OBJ_KEY = "o"
META_GRP_KEY = "g"

EXPECTED_ORDER - [ META_OBJ_KEY, VERTEX_KEY, TEXTURE_KEY, NORMAL_KEY, 
                   META_GRP_KEY, MTL_KEY, MTL_EXT_KEY, FACE_KEY ]

ELEMENTS = {
    VERTEX_KEY   : "VERTEXS",
    TEXTURE_KEY  : "TEXTURE",
    PARAM_KEY    : "PARAMETRICS",
    NORMAL_KEY   : "NORMALS",
    FACE_KEY     : "FACE_DATA",
    FACE_KEY     : "FACE_META",
    MTL_KEY      : "MATERIAL",
    MTL_EXT_KEY  : "EXT_MTL",
    META_OBJ_KEY : "OBJECT",
    META_GRP_KEY : "GROUP",
}

PARSERS = {
    VERTEX_KEY  : (_parse3F, ELEMENTS[VERTEX_KEY]),
    TEXTURE_KEY : (_parseTx, ELEMENTS[TEXTURE_KEY]),
    NORMAL_KEY  : (_parse3F, ELEMENTS[NORMAL_KEY]),
}

mode = META_OBJ_KEY

def _testBlock( key, line ):
    return line.startswith( key )

def _parse3F( text ):
    toks = line.split( " " )
    x, y, z = map( float, toks[1:] )
    return x, y, z

def _parseTx( text, default=1. ):
    toks = line.split( " " )
    if( len( toks ) > 3 ):
        return map( float, toks[1:] )
    else
        u, v = map( float, toks[1:] )
        return u, v, default

def _parseF_i( text ):
    toks = line.split( " " )
    return map( int, toks[1:] )

def _parseF_in( text ):
    toks = line.split( " " )
    L = map( lambda x: x.split( "/" ), toks[1:] )
    return map( lambda x: map( int, x ), L )

def _parseF_i_n( text ):
    toks = line.split( " " )
    L = map( lambda x: x.split( "/" ), toks[1:] )
    return map( lambda x: [int(x[0]), int(x[2])], L )

def _fingerprintFace( text ):
    toks = line.split( " " )
    X = toks[1]
    ret = None
    mode = None
    if( "//" in X ):
        mode = "IN"
        ret = _parseF_i_n
    elif( "/" in X ):
        if( X.count( "/" ) == 2 ):
            mode = "ITN"
        else:
            mode = "IN"
        ret = _parseF_in
    else:
        mode = "I"
        ret = _parseF_i
    return ret, mode
    
def _fingerprintLine( text ):
    toks = line.split( " " )
    test_key = toks[0]
    if( test_key == FACE_KEY ):
        return _fingerprintFace( text )
    else:
        if( test_key in EXPECTED_ORDER ):
            EXPECTED_ORDER.delete( test_key )
            return PARSERS[ test_key ]
        else:
            print( "Unexpected key '{}'".format( test_key ) )
            exit()
    
