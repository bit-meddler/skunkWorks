"""
    Wavefront OBJ Parser - basic implementations
    TODOs
        optional scale factor
        groups
"""

class ObjReader( object ):
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
    FACE_M_KEY   = "_internal"

    EXPECTED_ORDER - [ META_OBJ_KEY, VERTEX_KEY, TEXTURE_KEY, NORMAL_KEY, 
                       META_GRP_KEY, MTL_KEY, MTL_EXT_KEY, FACE_KEY ]

    ELEMENTS = {
        VERTEX_KEY   : "VERTEXS",
        TEXTURE_KEY  : "TEXTURE",
        PARAM_KEY    : "PARAMETRICS",
        NORMAL_KEY   : "NORMALS",
        FACE_KEY     : "FACE_DATA",
        FACE_M_KEY   : "FACE_META",
        MTL_KEY      : "MATERIAL",
        MTL_EXT_KEY  : "EXT_MTL",
        META_OBJ_KEY : "OBJECT",
        META_GRP_KEY : "GROUP",
    }

    PARSERS = {
        VERTEX_KEY   : (_parse3F, ELEMENTS[VERTEX_KEY]),
        TEXTURE_KEY  : (_parseTx, ELEMENTS[TEXTURE_KEY]),
        NORMAL_KEY   : (_parse3F, ELEMENTS[NORMAL_KEY]),
    }

    
    def __init__( self ):
        self.DEFAULT = "__default__"
        self.obj_data = {
            "VERTS" : [],
            "TEX_UV" : [],
            "NORMALS" : [],
            "MATERIAL_LIST" : [],
            "MATERIALS" : {}
            "OBJECTS" : [ self.DEFAULT ],
            "CONTENT" : {
                "DEFAULT" : {
                    "REMARKS" : [],
                    "MATERIAL" : "",
                    "GEO" : []
                }
            },
        }
        self.curr_obj = self.DEFAULT
        self.curr_grp = ""
        self.scale = 1.
        self.tx_w_default = 1.

        
    @staticmethod    
    def _parse3F( args ):
        toks = args.split( " " )
        x, y, z = map( float, toks )
        return x, y, z
        
    def _parseTx( self, args ):
        toks = args.split( " " )
        if( len( toks ) > 3 ):
            return map( float, toks )
        else
            u, v = map( float, toks )
            return u, v, self.tx_w_default
            
    @staticmethod
    def _parseF_i( args ):
        toks = args.split( " " )
        return map( int, toks )
        
    @staticmethod
    def _parseF_in( args ):
        toks = args.split( " " )
        L = map( lambda x: x.split( "/" ), toks )
        return map( lambda x: map( int, x ), L )
        
    @staticmethod
    def _parseF_i_n( args ):
        toks = args.split( " " )
        L = map( lambda x: x.split( "/" ), toks[1:] )
        return map( lambda x: [int(x[0]), int(x[2])], L )

    @staticmethod
    def _fingerprintFace( args ):
        toks = args.split( " " )
        X = toks[0]
        parser = None
        mode = None
        if( "//" in X ):
            mode = "IN"
            parser = _parseF_i_n
        elif( "/" in X ):
            if( X.count( "/" ) == 2 ):
                mode = "ITN"
            else:
                mode = "IN"
            parser = _parseF_in
        else:
            mode = "I"
            parser = _parseF_i
        return parser, mode
        
    @staticmethod
    def _fingerprintLine( args ):
        toks = args.split( " " )
        key = toks[0]
        if( key == FACE_KEY ):
            return _fingerprintFace( text )
        else:
            if( key in EXPECTED_ORDER ):
                return PARSERS[ key ]
            else:
                print( "Unexpected key '{}'".format( key ) )
                exit()
        
    def parseFile( self, file ):
        fh = open( file, "r" )
        
        last_key = ""
        
        for line in fh:
            line = line.strip()
            if( line == "" ):
                continue
                
            key, args = line.split( " ", 1 )
            




#










