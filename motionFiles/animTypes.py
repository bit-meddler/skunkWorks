""" Basic Types for containing and working with skeletal animation
"""
import numpy as np


class SkeletonData( object ):
    """
        SkeletonData - the topology and configuration of a skeleton
        
        TODO:
            # Joint Limits
            # CoM ratio
            # Expression-based solving
            
    """
    # joint Draw styles - note, enum corresponds to DoF count
    JOINT_END   = 0 # end           | Lozenge
    JOINT_HINGE = 1 # r             | Trunion
    JOINT_HARDY = 2 # r r           | Dbl Trunion
    JOINT_BALL  = 3 # r r r         | Ball
    JOINT_COMP1 = 4 # r r r t       | Spine... Ball with a Fin?
    JOINT_COMP2 = 5 # r r r t t     | Shoulder... Ball on a plate?
    JOINT_FREE  = 6 # r r r t t t   | BoxBall
    
    
    def __init__( self ):
        # Joint Data
        self.joint_names   = [] # [s]   List of Joint names, as encountered
        self.joint_count   = 0  # i     num joints encountered
        # Joint Channels
        self.joint_chans   = [] # [i]   active DoFs of each joint in order like GIANT
        self.chan_label    = [] # [s]   label of each channel (root.tx etc)
        self.joint_chanidx = [] # [i]   idx of joint's channels
        # Skel Topo
        self.joint_parents = [] # [i]   parent of joint at idx, [0]==-1 (world)
        self.joint_LUT     = {} # s:i   Dict of Name->Idx
        self.joint_topo    = {} # s:[s] Dict of parent:[ children... ]
        self.joint_root    = "" # s     name of root joint
        # The maths
        self.joint_L_mats  = [] # [np]  list of 3x4 Local Matrix - 'offset from parent'
        self.joint_G_mats  = [] # [np]  list of 3x4 Global Matrix
        # Drawing
        self.joint_styles  = [] # [i]   list of joint styles, for drawing
        
        # Animation
        self.anim = AnimData()  # obj of channel data
        
        
    @staticmethod
    def _splitchans( chans ):
        # maybe split chans to T and R parts, then compute indipendantly
        T, R = [], []
        for ch in chans:
            if( ch > 3 ):
                R.append( ch )
            elif( ch > 0 ):
                T.append( ch )
        return T, R
        
        
    def poseDirect( self, chans, origin=None ):
        """
            Based on supplied channels, pose the Skeleton's G_mats
            Direct mapping of channel data -> joint channels
            origin is an optional "Global Frame", but we shouldn't call it either global, or frame!
        """
        if( len( chans ) != len( self.joint_chans ) ):
            print( "channel data miss-match" )
        # set world Origin
        world = origin if( origin != None ) else self._eye34()
        # resulting pose
        pose = np.zeros( shape=self.joint_G_mats.shape, dtype=np.float32 )
        # walk the skel in evaluation order & pose
        # TODO:
        #       First element is always root so do root computation standalone, then ci[1:-1], ci[2:]
        for j_idx, c_in, c_out in enumerate( zip( self.joint_chanidx[:-1], self.joint_chanidx[1:] ) ):
            # compose a transformation matrix conforming to the joint's DoFs and rot-order
            transform_order = self.joint_chans[ c_in:c_out ]
            chan_data = chans[ c_in:c_out ]
            transform_order = map( lambda x: x-1, transform_order )
            M = self._eye34()
            # must be a nicer way of doing this!
            for i, op in enumerate( transform_order ):
                if( op < 3 ):
                    # tx
                    M[op,3] = chan_data[ i ]
                else:
                    # another customer for skeleton maths
                    cv, sv = np.cos( chan_data[i] ), np.sin( chan_data[i] )
                    if( op == 3 ): # X
                        M = np.matmul( np.array( [[1.,0.,0.], [0.,cv,-sv], [0.,sv,cv]],  dtype=np.float32 ), M[:,:3]
                    if( op == 4 ): # Y
                        M = np.matmul( np.array( [[cv,0.,sv], [0.,1.,-0.], [-sv,cv,1.]], dtype=np.float32 ), M[:,:3]
                    if( op == 5 ): # Z
                        M = np.matmul( np.array( [[cv,-sv,0.], [sv,cv,0.], [0.,0.,1.]],  dtype=np.float32 ), M[:,:3]
                        
            p_idx = self.joint_parents[ j_idx ]
            # Might be better...
            # dot( A, B ) -> parent . child; child's space is tx'd by parent
            # Maybe replace dot with np.matmul for the R component?
            if( p_idx >= 0 ):
                pose[ j_idx ][:,:3] = np.dot( pose[ p_idx ][:,:3],  M[:,:3] )
                pose[ j_idx ][:,3]  = np.dot( pose[ p_idx ][:,:3],  M[:,3]  )
                pose[ j_idx ][:,3] += pose[ p_idx ][:,3]
                
            else:
                pose[ j_idx ][:,:3] = np.dot( world[:,:3], M[:,:3] )
                pose[ j_idx ][:,3]  = np.dot( world[:,:3], M[:,3]  )
                pose[ j_idx ][:,3] += world[:,3]
        # return
        return pose
                
    def poseExp( self, chans, frame=None ):
        """ TODO:
            Expression based posing.
            Compute all channels based on channel data and an expression matrix.  This enables a 
            Dimentionality reduction.  Example:  Direct solution for a spine of 5 joints = 20 chans
            (5* rx, ry, rz, ty); expression bassed solution 5 chans ( ty, rx_lo, rx_hi, ry, rz, ty )
            
            This enables a 'Coarticulated' joint system, and or a rotation to be spread between joints
        """
        pass
        
        
    @staticmethod
    def _eye34():
        # This needs to be in a skeleton math lib
        return np.array( [[1.,0.,0.,0.],[0.,1.,0.,0.],[0.,0.,1.,0.]], dtype=np.float32 )
    
    
    def _remarshalTopo( self ):
        """
            In the event of a topological change, we need to retraverse the skeleton
            then update the current (invalid) ordering of Joint and Channels into the 
            new order.  The Topographic change will not alter the number of channels or
            their sequence of aplication.
            Then update the LUT as the name:id mapping has been invalidated
        """
        # sort children by weigth, decresing
        child_weights = {}
        child_weights[ self.joint_root ] = self._computeChildWeight( self.joint_root, child_weights )
        for children in self.joint_topo.values():
            children.sort( key=lambda x: child_weights[ x ], reverse=True )
        # DFS for traverse order
        traverse_order = self._traverse( self.joint_root )
        # reorder joint data
        new_joint_chans = []
        new_joint_chan_names = []
        new_joint_chan_idxs = []
        new_L_mats = []
        for j_name in traverse_order:
            j_id = self.joint_LUT[ j_name ]
            c_in, c_out = self.joint_chanidx[ j_id ], self.joint_chanidx[ j_id + 1 ]
            new_joint_chans.append( self.joint_chans[ c_in:c_out ] )
            new_joint_chan_names.append( self.chan_label[ c_in:c_out ] )
            new_joint_chan_idxs.append( len( new_joint_chans ) )
            new_L_mats.append( self.joint_L_mats[ j_id, :,: ] )
        new_joint_count = len( traverse_order )
        # Update LUT
        # Update parents
        
            
    def _traverse( self, root ):
        """
            DFS of the skeleton's topology to return a 'computation order' list.
            root can be a leaf if we are coimputing only a subset of the skel
        """
        path = []
        q = [ root ]
        while( len( q ) > 0 ):
            leaf = q.pop( 0 )
            if leaf not in path:
                path.append( leaf )
                q = self.joint_topo[ leaf ] + q
        return path
        
        
    def _computeChildWeight( self, node, collector ):
        return self._computeChildSubBranches( node, collector )
        
        
    def _computeChildSubBranches( self, node, collector ):
    acc = 0
    
    if( node in self.joint_topo ):
        children = self.joint_topo[ node ]
        if( len( children ) == 0 ):
            return 1
        for child in children:
            val = self._computeChildWeight( child, collector )
            if( child in collector ):
                collector[ child ] += val
            else:
                collector[ child ] = val
            acc += val
    else:
        assert(False)
    return acc
    
    
    def _computeChildSubJoints( self, node, collector ):
    acc = 0
    
    if( node in self.joint_topo ):
        children = self.joint_topo[ node ]
        if( len( children ) == 0 ):
            return -1
        for child in children:
            val = self._computeChildWeight( child, collector ) + 1
            if( child in collector ):
                collector[ child ] += val
            else:
                collector[ child ] = val
            acc += val
    else:
        assert(False)
    return acc
        
        
    def _updateJointConfig( self, joint_data, j_name=None, j_id=None ):
        """
            joint_data = dict of new joint setup
            joint_data[ "DoF" ] = [ 1, 2, 3, 6, 5, 4 ]
            joint_data[ "mat" ] = np.array( (3,4) )
            
            j_name / j_id = addressed by name or id (for convenience)
        """
        assert( j_name != j_id )
        if( j_id == None ):
            if( j_name in self.joint_LUT ):
                j_id = self.joint_LUT[ j_name ]
            else:
                assert( False )
        # topo hasn't changed, but what can?
        # Dof Locks
        # Rot Order
        # L_mat
        
        
    def _updateJointMat( self, joint ):
        # update joint's L_mat
        # dfs to find affected children (multi-rooted!)
        # update children's L_mat
        pass
    
    
class AnimData( object ):
    
    def __init__( self ):
        self.frame_rate  = 0  # fps
        self.frame_count = 0  # num frames
        self.frame_durr  = 0  # durration of a frame (for playback)
        self.frames      = [] # frames x channels array

    def interpolateFrames( self, l_frame, r_frame, distance ):
        """ TODO:
            interpolate all channels between l & r frames, at the position that is
            distance % between them.
            
            For now this will be a dumb linnear interpolation.
        """
        pass
        
"""
    Idea for drawing a skeleton (in the above format)
    1) Pose
    2) walk the 'evaluation order'
        a) Draw "Drawstyle" Joint at G.RT
        b) For each Child draw a Bone from G.RT to child.G.T (not Transpose!!)
        
    Now, how do we draw a bone?
        a) Start easy.  A Cylinder
        b) Blade like Trapazoid ???
"""
