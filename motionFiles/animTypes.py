""" Basic Types for containing and working with skeletal animation
"""
import numpy as np

class SkeletonData( object ):
    # joint Draw styles - note, enum corresponds to DoF count
    JOINT_END   = 0 # end           | Lozenge
    JOINT_HINGE = 1 # r             | Trunion
    JOINT_HARDY = 2 # r r           | Dbl Trunion
    JOINT_BALL  = 3 # r r r         | Ball
    JOINT_COMP1 = 4 # r r r t       | Spine... Ball with a Fin?
    JOINT_COMP2 = 5 # r r r t t     | Shoulder... Ball on a plate?
    JOINT_FREE  = 6 # r r r t t t   | BoxBall
    
    def __init__( self ):
        self.joint_names   = [] # s   List of Joint names, as encountered
        self.joint_count   = 0  # i   num joints encountered
        self.joint_chans   = [] # i   active DoFs of each joint in order like GIANT
        self.chan_label    = [] # s   label of each channel (root.tx etc)
        self.joint_chanidx = [] # i   idx of joint's channels
        self.joint_parents = [] # i   parent of joint at idx, [0]==-1 (world)
        self.joint_LUT     = {} # s:i Dict of Name->Idx
        self.joint_L_mats  = [] # np  list of 3x4 Local Matrix
        self.joint_G_mats  = [] # np  list of 3x4 Global Matrix
        self.joint_styles  = [] # i   list of joint styles, for drawing
        self.anim = AnimData()  # obj of channel data

    def pose( self, chans ):
        """
            Based on supplied channels, pose the Skeleton's G_mats
        """
        if( len( chans ) != len( self.joint_chans ) ):
            print( "channel data miss-match" )
        # set world Origin
        world = self._blank34()
        for j_idx, c_in, c_out in enumerate( zip( self.joint_chanidx[:-1], self.joint_chanidx[1:] ): )
            transform_order = self.joint_chans[ c_in:c_out ]
            chan_data = chans[ c_in:c_out ]
            transform_order = map( lambda x: x-1, transform_order )
            M = self._blank34()
            for i, op in enumerate( transform_order ):
                if( op < 3 ):
                    #tx
                    M[op,3] = chan_data[ i ]
                else:
                    cv, sv = np.cos( chan_data[i] ), np.sin( chan_data[i] )
                    if( op == 3 ): # X
                        M = M[:,:3] * np.array( [[1.,0.,0.], [0.,cv,-sv], [0.,sv,cv]],  dtype=np.float32 )
                    if( op == 4 ): # Y
                        M = M[:,:3] * np.array( [[cv,0.,sv], [0.,1.,-0.], [-sv,cv,1.]], dtype=np.float32 )
                    if( op == 5 ): # Z
                        M = M[:,:3] * np.array( [[cv,-sv.,0.],[sv,cv,0.], [0.,0.,1.]],  dtype=np.float32 )
                        
            p_idx = self.jpint_parents[ j_idx ]
            if( p_idx >= 0 ):
                self.joint_G_mats[ j_idx ][:,:3] = np.dot( self.joint_G_mats[ p_idx ][:,:3],  M[:,:3] )
            else:
                self.joint_G_mats[ j_idx ][:,:3] = np.dot( world[:,:3],  M[:,:3] )
            self.joint_G_mats[ j_idx ][:,3] = np.dot( M[:,:3], M[:,3] )
                
    @staticmethod
    def _blank34():
        return np.array( [[1.,0.,0.,0],[0.,1.,0.,0],[0.,0.,1.,0]], dtype=np.float32 )

    
class AnimData( object ):
    
    def __init__( self ):
        self.frame_rate  = 0  # fps
        self.frame_count = 0  # num frames
        self.frame_durr  = 0  # durration of a frame (for playback)
        self.frames      = [] # frames x channels array

