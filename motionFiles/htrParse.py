"""
    experiment to Parse a HTR file
"""
import numpy as np

from animTypes import SkeletonData, AnimData


MY_NAMES = [ ".tx", ".ty", ".tz", ".rx", ".ry", ".rz" ]


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
            pass
    
        if( "SegmentNames&Hierarchy" in line ):
            # Child Parent pairs
            pass
            
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
