"""
    experiment to Parse a BVH file
"""
import numpy as np

from animTypes import SkeletonData, AnimData

CH_NAMES = [ "Xposition", "Yposition", "Zposition",
             "Xrotation", "Yrotation", "Zrotation" ]
MY_NAMES = [ ".tx", ".ty", ".tz", ".rx", ".ry", ".rz" ]

def _osToL( offset ):
    # BVH Joints only have a positional offset, no 'base pose' is recorded
    mat = np.zeros( (3,4),   dtype=np.float32 )
    mat[:3, :3] = np.eye( 3, dtype=np.float32 )
    mat[:,3] = map( float, offset )
    return mat


def readBVH( file_name ):

    fh = open( file_name, "r" )
    lines = fh.readlines()
    fh.close()
    lines.reverse() # so we can 'pop' through the lines

    skel = SkeletonData()
    
    while( len( lines ) > 0 ):
        line = lines.pop().strip()
        if( line.startswith( "#" ) ):
            line = lines.pop().strip()
        if( "HIERARCHY" in line ):
            # start of skeleton definition
            parent_id          = -1 # Global
            depth              =  0
            parent_stack       = []
            skel.joint_chanidx = [0]
            
            line = lines.pop().strip()
            while( True ):
                if( ("JOINT" in line) or ("ROOT" in line) ):
                    # part of joint hierarchy
                    cmd, joint_name = line.split()
                    line = lines.pop().strip()
                    if( "{" in line ):
                        depth += 1
                    skel.joint_parents.append( parent_id )
                    skel.joint_names.append(  joint_name )
                    # in BVH, joints come in 'evaluation order' - don't need Graph Traversal
                    my_id = len( skel.joint_names ) - 1  
                    skel.joint_LUT[ joint_name ] = my_id
                                        
                    line = lines.pop() # Offset
                    offsets = line.split()[1:]
                    skel.joint_L_mats.append( _osToL( offsets ) )
                    
                    line = lines.pop() # Channels
                    ch_list = line.split()[2:] # TAG Num ...
                    for ch in ch_list:
                        ch_i = CH_NAMES.index( ch )
                        skel.joint_chans.append( ch_i+1 )
                        skel.chan_label.append( joint_name + MY_NAMES[ ch_i ] )
                    skel.joint_chanidx.append( len( skel.joint_chans ) )
                    skel.joint_styles.append( len( ch_list ) )
                    
                    parent_stack.append( parent_id )
                    parent_id = my_id
                    
                    line = lines.pop().strip() # next element
                    
                if( "}" in line ):
                    depth -= 1
                    parent_id = parent_stack.pop()
                    line = lines.pop().strip() # next node or end of clause
                    
                if( "End Site" in line ):
                    line = lines.pop() # {
                    line = lines.pop() # 0 0 0
                    line = lines.pop() # }
                    skel.joint_styles[ parent_id ] = skel.JOINT_END
                    line = lines.pop().strip() # next node or end of clause
                    
                if( depth == 0 ): # End of Hierarchy 
                    break
                    
                if( line.startswith( "#" ) ):
                    line = lines.pop().strip()
                    
        # Tidy up
        skel.joint_count = len( skel.joint_names )
    
        if( "MOTION" in line ):
            # start of anim data
            frame_count = lines.pop().split()[1]
            frame_time  = lines.pop().split()[2]
            skel.anim.frame_count = int( frame_count )
            skel.anim.frame_durr  = float( frame_time )
            skel.anim.frame_rate  = 1.0 / skel.anim.frame_durr

            while( len( lines ) > 0 ):
                line = lines.pop()
                chan_data = map( float, line.split() )
                skel.anim.frames.append( chan_data )

            num_frames = len( skel.anim.frames )
            if( num_frames != skel.anim.frame_count ):
                print( "frame range miss-match" )
                skel.anim.frame_count = num_frames
            # conform to np array
            skel.anim.frames = np.array( skel.anim.frames, dtype=np.float32 )
            
    return skel

if( __name__ == "__main__" ):
    s = readBVH( "171025_Guy_ROM_body_01_mobu.bvh" )
    s = readBVH( "171025_Guy_ROM_body_01_blade.bvh" )
    for i, (name, type) in enumerate( zip( s.joint_names, s.joint_styles ) ):
        print name, type, ":", s.joint_chans[ s.joint_chanidx[i] : s.joint_chanidx[i+1] ]
