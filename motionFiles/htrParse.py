"""
    experiment to Parse a HTR file
"""
import numpy as np

from animTypes import SkeletonData, AnimData


MY_NAMES = [ ".tx", ".ty", ".tz", ".rx", ".ry", ".rz" ]

def _dfs( graph, root ):
    path = []
    q = [ root ]
    while( len( q ) > 0 ):
        leaf = q.pop( 0 )
        if leaf not in path:
            path.append( leaf )
            q = graph[ leaf ] + q
    return path
    
def readHTR( file_name ):

    fh = open( file_name, "r" )
    lines = fh.readlines()
    fh.close()
    lines.reverse() # so we can 'pop' through the lines

    skel = SkeletonData()
    
    line = lines.pop().strip()
    while( True ):
        
        if( line == "" ):
            continue
            
        if( "Header" in line ):
            # fps, data frames, default rot order (reversed!)
            while( True ):
                line = lines.pop().strip()
                if( "NumSegments" in line:
                    pass # 36
                if( "NumFrames" in line:
                    pass #  120
                if( "DataFrameRate" in line:
                    pass #  120
                if( "EulerRotationOrder" in line:
                    pass #  ZYX
                if( "CalibrationUnits" in line:
                    pass #  mm
                if( "RotationUnits" in line:
                    pass #  Degrees
                if( "GlobalAxisofGravity" in line:
                    pass #  Y
                if( "BoneLengthAxis" in line:
                    pass #  Y
                if( "[" in line:
                    break
    
        if( "SegmentNames&Hierarchy" in line ):
            # Child Parent pairs
            s_graph = {"GLOBAL":[]}
            rev_LUT = []
            while( True ):
                line = lines.pop().strip()
                if( "[" in line ):
                    break
                child, parent = line.split()
                if parent in s_graph:
                    s_graph[ parent ].append( child )
                else:
                    s_graph[ parent ] = [ child ]
                if child not in s_graph:
                    s_graph[ child ] = []
                rev_LUT[ child ] = parent
                
            root = s_graph[ "GLOBAL" ][0] # assume one root
            skel.joint_names = _dfs( s_graph, root )
            skel.joint_count = len( skel.joint_names )
            # make LUT
            for i, name in enumerate( skel.joint_names ):
                skel.joint_LUT[ name ] = i
            
            # make parent_list
            del( rev_LUT[ "GLOBAL" ] )
            rev_LUT[ root ] == None
            for joint in skel.joint_names:
                p_idx = -1
                p_name = rev_LUT[ joint ]
                if p_name not None:
                    p_idx = skel.joint_LUT[ p_name ]
                self.joint_parents[ skel.joint_LUT[ joint ] ] = p_idx
                
        if( "BasePosition" in line ):
            # name, 0, 0, 0, r?, r?, r?, 1
            #
            # Last Hierarchy section
            break
            
    # Tidy up skeleton? BFS to generate evaluate order
    
    line = lines.pop().strip()
    while( len( lines ) > 0 ):
        if( "[" in line ):
            # [ch name]
            line = lines.pop().strip()
            # ch data: f, tx, ty, tz, r?, r?, r?, 1.0
            # populate basepose joint offset from t datas
            if( not "]" in line ):
                # accumulate ch data
                pass
            
    # Conform to np arrays
    return skel

    
if( __name__ == "__main__" ):
    s = readBVH( "171025_Guy_ROM_body_01.htr" )
    for i, (name, type) in enumerate( zip( s.joint_names, s.joint_styles ) ):
        print name, type, ":", s.joint_chans[ s.joint_chanidx[i] : s.joint_chanidx[i+1] ]
