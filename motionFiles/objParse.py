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
    SMOOTH_G_KEY = "s"


    DEFAULT = "__default__"

    
    def __init__( self ):
        self.reset()

        
    def reset( self ):
        self.obj_data = {
            "VERTS"         : [],
            "TEX_UV"        : [],
            "NORMALS"       : [],
            "MATERIAL_LIST" : [],
            "MATERIAL_FILES": [],
            "OBJECT_LIST"   : [ self.DEFAULT ],
            "MATERIALS"     : {},
            "COMP_TOPO"     : {},
            "COMPONENTS"       : {
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


    def _fingerprintFace( self, args ):
        toks = args.split( " " )
        X = toks[0] # example face element
        parser = None
        mode   = None
        
        if( "//" in X ):
            mode = "IN"
            parser = self._parseF_i_n
        elif( "/" in X ):
            if( X.count( "/" ) == 2 ):
                mode = "ITN"
            else:
                mode = "IN"
            parser = self._parseF_in
        else:
            mode = "I"
            parser = self._parseF_i
            
        return parser, mode


    def _renameCOMPONENTS( self, old, new ):
        ren_tasks = [] # [(old, new)...]
        for COMPONENTS in self.obj_data["OBJECT_LIST"]:
            if( COMPONENTS.startswith( old ) ):
                ren_tasks.append( COMPONENTS, COMPONENTS.replace( old, new, 1 ) )
                
        for task in ren_tasks:
            source, target = task
            idx = self.obj_data["OBJECT_LIST"].index( source )
            self.obj_data["OBJECT_LIST"][ idx ] = target
            self.obj_data["COMPONENTS"][target] = self.obj_data["COMPONENTS"].pop( source )


    def _parseRem( self, args ):
        if( "centimeters" in args.lower() ):
            print( "cm Scaled file" )
            self.scale = 10.
        self.obj_data["COMPONENTS"][self.curr_tgt]["REMARKS"].append( args )


    def _parseVtx( self, args ):
        self.obj_data[ "VERTS" ].append( self._parse_3f( args ) )


    def _parseTex( self, args ):
        u, v, w = 0., 0., 0.
        toks = args.split( " " )
        if( len( toks ) > 2 ):
            u, v, w =  map( float, toks )
        else:
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
            # rename any COMPONENTS having a "default" prefix
            self._renameCOMPONENTS( self.DEFAULT, obj_name )
        else:
            # this is a new component
            self.obj_data["COMPONENTS"][self.curr_tgt] = {
                "REMARKS"  : [],
                "MATERIAL" : "",
                "GEO"      : [],
                "GEO_MODE" : ""
            }
            self.obj_data["OBJECT_LIST"].append( self.curr_tgt )


    def _parseGrp( self, args ):
        # sometimes it has hyraychy info
        # g child parent
        # Sometimes materials
        # g arms_GRP Markk_blinnSG
        # usemtl Markk_blinnSG
        # TODO
        grp_name = ""
        parent = None
        
        toks = args.split( " " )
        if( len( toks ) > 1 ):
            grp_name = toks[0]
            parent   = toks[1]
            # adapted from the HTR parser
            if parent in self.obj_data["COMP_TOPO"]:
                self.obj_data["COMP_TOPO"][ parent ].append( grp_name )
            else:
                self.obj_data["COMP_TOPO"][ parent ] = [ grp_name ]
            if grp_name not in self.obj_data["COMP_TOPO"]:
                self.obj_data["COMP_TOPO"][ grp_name ] = []
        else:
            grp_name = toks[0]
        # update tgt
        self.curr_grp = grp_name
        self.curr_tgt = ":".join( (self.curr_obj, grp_name) )
        # guard against re[eated names
        if( grp_name in self.obj_data["OBJECT_LIST"] ):
            # TODO
            return
        # new component
        self.obj_data["COMPONENTS"][self.curr_tgt] = {
            "REMARKS"  : [],
            "MATERIAL" : "",
            "GEO"      : [],
            "GEO_MODE" : ""
        }
        self.obj_data["OBJECT_LIST"].append( self.curr_tgt )
        

    def _parseMtl( self, args ):
        if( args not in self.obj_data["MATERIAL_LIST"] ):
            self.obj_data["MATERIAL_LIST"].append( args )
        self.obj_data["COMPONENTS"][self.curr_tgt]["MATERIAL"] = args


    def _parseExt( self, args ):
        # link to MTL file
        self.obj_data["MATERIAL_FILES"].append( args )


    def _parseFac( self, args ):
        self.obj_data["COMPONENTS"][self.curr_tgt]["GEO"].append(
            self.currFaceParser( args ) )


    def _parseSmg(self, args ):
        # smoothing group on/off
        # TODO:
        pass

    
    PARSERS = {
        VERTEX_KEY   : _parseVtx,
        TEXTURE_KEY  : _parseTex,
        NORMAL_KEY   : _parseNml,
        META_OBJ_KEY : _parseObj,
        META_GRP_KEY : _parseGrp,
        MTL_KEY      : _parseMtl,
        MTL_EXT_KEY  : _parseExt,
        FACE_KEY     : _parseFac,
        COMMENT_KEY  : _parseRem,
        SMOOTH_G_KEY : _parseSmg
    }

    
    def parseFile( self, file ):
        fh = open( file, "r" )
        
        last_key = ""
        parse = None # function pointer to current parser
        
        for line in fh:
            line = line.strip()
            if( line == "" ):
                continue
            
            # the cost of excepting is amortized over runtime
            # and unsplittable lines are very rare
            try:
                key, args = line.split( " ", 1 )
            except ValueError:
                # deal with common faults
                if( line.startswith( self.COMMENT_KEY ) ):
                    # comment
                    continue
                if( line.startswith( self.META_GRP_KEY ) ):
                    # blank group
                    self._parseGrp( "root" )
                print( "'{}' couldn't be split".format( line ) )
                continue
            
            # has key changed?
            if( key != last_key ):                    
                if( key in self.PARSERS.keys() ):
                    parse = self.PARSERS[ key ]
                    if( key == self.FACE_KEY ):
                        face_parser, face_mode = self._fingerprintFace( args )
                        self.currFaceParser = face_parser
                        self.obj_data["COMPONENTS"][self.curr_tgt]["GEO_MODE"] = face_mode
                elif( line.startswith( self.COMMENT_KEY ) ):
                    # Phew just a comment
                    print( "Unexpected key '{}'".format( key ) )
                    print( fh.tell() )
                    exit()
                else:
                    print( "Unexpected key '{}'".format( key ) )
                    print( fh.tell() )
                    exit()
                    
                last_key = key
                # New parser activated!
            
            parse( self, args )
        # loaded into dict
        # Tidy up Components
        del_list = []
        for obj in self.obj_data["OBJECT_LIST"]:
            if( len( self.obj_data["COMPONENTS"][obj]["GEO"] ) == 0 ):
                # No GEO in component
                if( ":" not in obj ):
                    # root
                    del_list.append( obj )
                    # TODO: Remove defunct namespace
        for victim in del_list:
            del( self.obj_data["COMPONENTS"][ victim ] )
            
        # remarshal data...
        # self.scale * vtx
        # TODO!

if( __name__ == "__main__" ):
    # test...
    reader = ObjReader()
    reader.parseFile( "cone1.obj" )
    reader.reset()
    reader.parseFile( "Pawn.obj" )
    reader.reset()
    reader.parseFile( "leftfoot.obj" )








