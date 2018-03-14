"""
    experiment to Parse a HTR file
"""
import numpy as np

from animTypes import SkeletonData, AnimData


MY_NAMES = [ ".tx", ".ty", ".tz", ".rx", ".ry", ".rz" ]
ROT_CONVERT = {
    "Degrees": lambda x: x,
    "Radians": np.radians,
}
   
    
def _formRot( rx, ry, rz, order="XYZ" ):
    X = np.eye( 3 )
    Y = np.eye( 3 )
    Z = np.eye( 3 )
    M = np.eye( 3 )
    
    cx, sx = np.cos( rx ), np.sin( rx )
    cy, sy = np.cos( ry ), np.sin( ry )
    cz, sz = np.cos( rz ), np.sin( rz )
    
    X[1,1], X[2,2] =  cx, cx
    X[1,2], X[2,1] = -sx, sx
    
    Y[0,0], Y[2,2] = cy,  cy
    Y[0,2], Y[2,0] = sy, -sy
    
    Z[0,0], Z[1,1] =  cy, cy
    Z[0,1], Z[1,0] = -sz, sz
    
    # Post multiplying
    for ax in order[::-1]:
        if ax=="X":
            M *= X
        if ax=="Y":
            M *= Y
        if ax=="Z":
            M *= Z
            
    return M
    
    
def readHTR( file_name ):

    fh = open( file_name, "r" )
    lines = fh.readlines()
    fh.close()
    lines.reverse() # so we can 'pop' through the lines

    skel = SkeletonData()
    
    line = lines.pop().strip()
    header_rot_order = "XYZ"
    header_rot_chans = []
    header_rot_units = "Degrees"
    header_rate = -1
    header_frames = -1
    header_joints = -1
    
    while( True ):
        
        if( line == "" ):
            continue
            
        # fps, data frames, default rot order (reversed!)
        if( "Header" in line ):
            while( True ):
                line = lines.pop().strip()
                if( "[" in line ): # New block
                    break
                if( "NumSegments" in line ):
                     _, header_joints = line.split()
                     header_joints = int( header_joints )
                if( "NumFrames" in line ):
                     _, header_frames = line.split()
                     header_frames = int( header_frames )
                if( "DataFrameRate" in line ):
                     _, header_rate = line.split()
                     header_rate = int( header_rate )
                     skel.anim.frame_rate = header_rate
                     skel.anim.frame_durr = 1.0 / header_rate
                if( "EulerRotationOrder" in line ):
                    _, header_rot_order = line.split()
                    # Assuming this is reversed!
                    header_rot_order = header_rot_order[::-1]
                    # conv to 456
                    for ax in header_rot_order:
                        val = ord( ax.lower() ) - 116 # ord(x)=120 -> 4
                        header_rot_chans.append( val )
                if( "CalibrationUnits" in line ):
                    pass #  mm
                if( "RotationUnits" in line ):
                    _, header_rot_units = line.split()
                if( "GlobalAxisofGravity" in line ):
                    pass #  Y
                if( "BoneLengthAxis" in line ):
                    pass #  Y
    
        # Topology
        if( "SegmentNames&Hierarchy" in line ):
            # Child Parent pairs
            skel.joint_topo[ "GLOBAL" ] = []
            rev_LUT = {}
            while( True ):
                line = lines.pop().strip()
                if( "[" in line ): # New block
                    break
                child, parent = line.split()
                if parent in skel.joint_topo:
                    skel.joint_topo[ parent ].append( child )
                else:
                    skel.joint_topo[ parent ] = [ child ]
                if child not in skel.joint_topo:
                    skel.joint_topo[ child ] = []
                rev_LUT[ child ] = parent
                
            root = skel.joint_topo[ "GLOBAL" ][0] # assume one root!
            del( skel.joint_topo[ "GLOBAL" ] )
            skel.joint_root = root
            skel.joint_names = skel._remarshalTopo()
            skel.joint_count = len( skel.joint_names )
            
            # make LUT
            for i, name in enumerate( skel.joint_names ):
                skel.joint_LUT[ name ] = i
            
            # make parent_list
            rev_LUT[ root ] = None
            skel.joint_parents = [ None ] * skel.joint_count
            for joint in skel.joint_names:
                p_idx = -1
                p_name = rev_LUT[ joint ]
                if( p_name != None ):
                    p_idx = skel.joint_LUT[ p_name ]
                skel.joint_parents[ skel.joint_LUT[ joint ] ] = p_idx
           
        # Basepose   
        if( "BasePosition" in line ):
            skel.joint_L_mats = np.zeros( (skel.joint_count,3,4), dtype=np.float32 )
            skel.joint_chans = []
            skel.joint_chanidx[ 0 ]
            
            while( True ):
                line = lines.pop().strip()
                if( "[" in line ): # New block
                    break
                # get base pose
                toks = line.split()
                j_name = toks[0]
                j_id = skel.joint_LUT[ j_name ]
                tx, ty, tz, rx, ry, rz, _ = map( float, toks[1:] )
                # Form L mats
                rx = ROT_CONVERT[ header_rot_units ]( rx )
                ry = ROT_CONVERT[ header_rot_units ]( ry )
                rz = ROT_CONVERT[ header_rot_units ]( rz )
                M = _formRot( rx, ry, rz, header_rot_order )
                skel.joint_L_mats[ j_id, :3, :3 ] = M
                skel.joint_L_mats[ j_id, :, 3 ] = [ tx, ty, tz ]
                # joint chans
                chans = [ 1, 2, 3 ] + header_rot_chans
                skel.joint_chans += chans
                skel.joint_chanidx.append( len( skel.joint_chans ) )
                for ch in chans:
                    skel.chan_label.append( j_name + MY_NAMES[ ch ] )
                    
            # Last Hierarchy section
            break
            
    # Channel data
    skel.anim.frames = np.zeros( ( header_frames, skel.joint_count, 6 ) )
    while( len( lines ) > 0 ):
        # [ch name]
        name = line[ 1:-1 ] # escape square brackets
        if( name == "EndOfFile" ): # End of block
            break
        # get joint's animation    
        j_id = skel.joint_LUT[ name ]
        print name
        line = lines.pop().strip()
        # populate basepose joint offset from t datas
        while( not "]" in line ):
            # accumulate ch data
            toks = line.split()
            frame = int( toks[ 0 ] ) - 1
            skel.anim.frames[ frame, j_id, : ] = map( float, toks[1:-1] )
            line = lines.pop().strip()
    
    return skel

    
if( __name__ == "__main__" ):
    s = readHTR( "171025_Guy_ROM_body_01.htr" )
    for i, (name, type) in enumerate( zip( s.joint_names, s.joint_styles ) ):
        print name, type, ":", s.joint_chans[ s.joint_chanidx[i] : s.joint_chanidx[i+1] ]
