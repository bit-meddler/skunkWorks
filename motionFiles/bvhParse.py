"""
    experiment to Parse a BVH file
"""
import numpy as np


class SkeletonData( object ):
    
    def __init__( self ):
        self.joint_names   = [] # s List of Joint names, as encountered
        self.joint_count   = 0  # i num joints encountered
        self.joint_chans   = [] # i active DoFs of each joint in order like GIANT
        self.chan_label    = [] # s label of each channel (root.tx etc)
        self.joint_chanidx = [] # i idx of joint's channels
        self.joint_parents = [] # i parent of joint at idx, [0]==-1 (world)
        self.joint_LUT     = {} # s:i Dict of Name->Idx
        self.joint_L_mats  = [] # np list of 3x4 Local Matrix
        self.anim = AnimData()  # object of chanel data
        
        
class AnimData( object ):
    
    def __init__( self ):
        self.frame_rate  = 0  # fps
        self.frame_count = 0  # num frames
        self.frame_durr  = 0  # durration of a frame (for playback)
        self.frames      = [] # frames x channels array



CH_NAMES = [ "Xposition", "Yposition", "Zposition",
             "Xrotation", "Yrotation", "Zrotation" ]
MY_NAMES = [ ".tx", ".ty", ".tz", ".rx", ".ry", ".rz" ]

def _osToL( offset ):
    mat = np.zeros( (3,4), dtype=np.float32 )
    mat[:3, :3] = np.eye( 3, dtype=np.float32 )
    mat[:,3] = map( float, offset )
    return mat


def readBVH( file_name ):

    fh = open( file_name, "r" )
    lines = fh.readlines()
    fh.close()
    lines.reverse() # so we can 'pop' through the lines

    skel = SkeletonData()
    
    parent_id = -1
    depth = 0
    parent_stack = []
    
    while( len( lines ) > 0 ):
        line = lines.pop().strip()
        if( "HIERARCHY" in line ):
            # start of skeleton definition
            skel.joint_chanidx = [0]
            line = lines.pop().strip()
            while( True ):
                #print line
                if( ("ROOT" in line) or ("JOINT" in line) ):
                    # part of joint hierarchy
                    cmd, joint_name = line.split()
                    line = lines.pop()
                    if( "{" in line ):
                        depth += 1
                    skel.joint_parents.append( parent_id )
                    skel.joint_names.append( joint_name )
                    my_id = len( skel.joint_names ) - 1
                    line = lines.pop() # Offset
                    offsets = line.split()[1:]
                    skel.joint_L_mats.append( _osToL( offsets ) )
                    line = lines.pop() # Channels
                    ch_list = line.split()[2:]
                    for ch in ch_list:
                        ch_i = CH_NAMES.index( ch )
                        skel.joint_chans.append( ch_i+1 )
                        skel.chan_label.append( joint_name + MY_NAMES[ ch_i ] )
                    skel.joint_chanidx.append( len( skel.joint_chans ) )
                    skel.joint_LUT[ joint_name ] = my_id
                    parent_stack.append( parent_id )
                    parent_id = my_id
                    line = lines.pop().strip() # next element
                if( "}" in line ):
                    depth -= 1
                    parent_id = parent_stack.pop()
                    line = lines.pop().strip() # next node or end of clause
                if( "End Site" in line ):
                    line = lines.pop()
                    line = lines.pop()
                    line = lines.pop()
                    line = lines.pop().strip()
                if( depth == 0 ):
                    break
                
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

            if( len( skel.anim.frames ) != skel.anim.frame_count ):
                print( "frame range miss-match" )
            skel.anim.frames = np.array( skel.anim.frames, dtype=np.float32 )
            
    # Tidy up
    skel.joint_count = len( skel.joint_names )
    return skel

if( __name__ == "__main__" ):
    s = readBVH( "171025_Guy_ROM_body_01.bvh" )
    
