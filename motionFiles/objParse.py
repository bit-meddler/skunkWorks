"""
    Wavefront OBJ Parser - basic implementations
    TODOs
        optional scale factor
        groups
"""

class ObjReader( object ):
    # file expected Keys
    COMMENT_KEY  = "#"
    VERTEX_KEY   = "v"
    TEXTURE_KEY  = "vt"
    PARAM_KEY    = "vp"
    NORMAL_KEY   = "vn"
    FACE_KEY     = "f"
    MTL_KEY      = "usemtl"
    MTL_EXT_KEY  = "mtllib"
    META_OBJ_KEY = "o"
    META_GRP_KEY = "g"

    PARSERS = {
        VERTEX_KEY   : self._parseVtx,
        TEXTURE_KEY  : self._parseTex,
        NORMAL_KEY   : self._parseNml,
        META_OBJ_KEY : self._parseObj,
        META_GRP_KEY : self._parseGrp,
        MTL_KEY      : self._parseMtl,
        MTL_EXT_KEY  : self._parseExt,
        FACE_KEY     : self._parseFac,
        COMMENT_KEY  : self._parseRem
    }

    DEFAULT = "__default__"
    
    def __init__( self ):
        self.obj_data = {
            "VERTS"         : [],
            "TEX_UV"        : [],
            "NORMALS"       : [],
            "MATERIAL_LIST" : [],
            "MATERIAL_FILES": [],
            "OBJECT_LIST"   : [ self.DEFAULT ],
            "MATERIALS"     : {},
            "CONTENT"       : {
                    self.DEFAULT : {
                        "REMARKS"  : [],
                        "MATERIAL" : "",
                        "GEO"      : [],
                        "GEO_MODE" : ""
                    }
            }
        }
        self.curr_obj = self.DEFAULT
        self.curr_grp = ""
        self.curr_tgt = self.curr_obj
        self.currFaceParser = None
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

        
    def _renameContent( self, old, new ):
        ren_tasks = [] # [(old, new)...]
        for content in self.obj_data["OBJECT_LIST"]:
            if( content.startswith( old ) ):
                ren_tasks.append( content, content.replace( old, new, 1 ) )
                
        for task in ren_tasks:
            source, target = task
            idx = self.obj_data["OBJECT_LIST"].index( source )
            self.obj_data["OBJECT_LIST"][ idx ] = target
            self.obj_data["CONTENT"][target] = self.obj_data["CONTENT"].pop( source )
            
            
    def _parseRem( self, args ):
        if( "centimeters" in args.lower() ):
            print( "cm Scaled file" )
            self.scale = 10.
        self.obj_data["CONTENT"][self.curr_tgt]["REMARKS"].append( args )
        
        
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
        

    def _parseObj( self, args ):
        # set new name
        obj_name = args.replace( " ", "_" )
        self.curr_obj = obj_name
        self.curr_grp = ""
        self.curr_tgt = obj_name
        # rename if old
        if( self.curr_obj == self.DEFAULT ):
            # rename any content having a "default" prefix
            self._renameContent( self.DEFAULT, obj_name )
        else:
            # this is a new component
            self.obj_data["CONTENT"][self.curr_tgt] = {
                "REMARKS"  : [],
                "MATERIAL" : "",
                "GEO"      : [],
                "GEO_MODE" : ""
            }
        
        
    def _parseGrp( self, args ):
        # Update Curr_grp
        grp_name = args.replace( " ", "_" )
        self.curr_grp = grp_name
        self.curr_tgt = ":".join( (self.curr_obj, grp_name) )
        self.obj_data["CONTENT"][self.curr_tgt] = {
            "REMARKS"  : [],
            "MATERIAL" : "",
            "GEO"      : [],
            "GEO_MODE" : ""
        }

        
        
    def _parseMtl( self, args ):
        if( args not in self.obj_data["MATERIAL_LIST"] ):
            self.obj_data["MATERIAL_LIST"].append( args )
        self.obj_data["CONTENT"][self.curr_tgt]["MATERIAL"] = args
        
        
    def _parseExt( self, args ):
        # link to MTL file
        self.obj_data["MATERIAL_FILES"].append( args )
        
        
    def _parseFac( self, args ):
        self.obj_data["CONTENT"][self.curr_tgt]["GEO"].append(
            self.currFaceParser( args ) )
        
        
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

            # has key changed?
            if( key != last_key ):                    
                if( key in self.PARSERS.keys ):
                    parser = PARSERS[ key ]
                    if( key == FACE_KEY ):
                        face_parser, face_mode = self._fingerprintFace( args )
                        self.currFaceParser = face_parser
                        self.obj_data["CONTENT"][self.curr_tgt]["GEO_MOED"] = face_mode
                else:
                    print( "Unexpected key '{}'".format( key ) )
                    exit()
                    
                last_key = key
                # New parser activated!
            
            parse( args )
        # loaded into dict
        # remarshal data...
        # TODO!











