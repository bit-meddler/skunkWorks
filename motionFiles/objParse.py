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

    EXPECTED_KEYS - [ META_OBJ_KEY, VERTEX_KEY, TEXTURE_KEY, NORMAL_KEY, 
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
        VERTEX_KEY   : (self._parseVtx, self.ELEMENTS[VERTEX_KEY]),
        TEXTURE_KEY  : (self._parseTex, self.ELEMENTS[TEXTURE_KEY]),
        NORMAL_KEY   : (self._parseNml, self.ELEMENTS[NORMAL_KEY]),
    }

    
    def __init__( self ):
        self.DEFAULT = "__default__"
        self.obj_data = {
            "VERTS"         : [],
            "TEX_UV"        : [],
            "NORMALS"       : [],
            "REMARKS"       : [],
            "MATERIAL_LIST" : [],
            "OBJECT_LIST"   : [ self.DEFAULT ],
            "MATERIALS"     : {},
            "CONTENT"       : {
                    self.DEFAULT : {
                        "REMARKS"  : [],
                        "MATERIAL" : "",
                        "GEO"      : []
                    }
            }
        }
        self.curr_obj = self.DEFAULT
        self.curr_grp = ""
        self.curr_tgt = self.curr_obj
        self.scale = 1.
        self.tx_w_default = 1.

        
    @staticmethod    
    def _parse_3f( args ):
        toks = args.split( " " )
        x, y, z = map( float, toks )
        return x, y, z
            
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

        
    def _parseVtx( self, args ):
        self.obj_data[ "VERTS" ].append( self._parse_3f( args ) )
        
        
    def _parseTex( self, args ):
        u, v, w = 0., 0., 0.
        toks = args.split( " " )
        if( len( toks ) > 3 ):
            u, v, w =  map( float, toks )
        else
            u, v = map( float, toks )
            w = self.tx_w_default
        self.obj_data[ "TEX_UV" ].append( (u, v, w) )
        
        
    def _parseNml( self, args ):
        self.obj_data[ "NORMALS" ].append( self._parse_3f( args ) )
        
        
    def parseFile( self, file ):
        fh = open( file, "r" )
        
        last_key = ""
        parser = None # function pointer to current parser
        mode = None # Face mode
        
        for line in fh:
            line = line.strip()
            if( line == "" ):
                continue
                
            key, args = line.split( " ", 1 )
            # comments
            if( key == "#" ):
                last_key = key
                if( "centimeters" in args.lower() ):
                    print( "cm Scaled file" )
                    self.scale = 10.
                self.obj_data["CONTENT"][self.curr_tgt]["REMARKS"].append( args )
                continue
                
            # has key changed?
            if( key != last_key ):
                if( key == FACE_KEY ):
                    face_parser, face_mode = self._fingerprintFace( args )
                else:
                    if( key in EXPECTED_ORDER ):
                        parser, _parser = PARSERS[ key ]
                    else:
                        print( "Unexpected key '{}'".format( key ) )
                        exit()
                last_key = key
                
            parse( args )

#










