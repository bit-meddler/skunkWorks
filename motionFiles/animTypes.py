""" Basic Types for containing and working with skeletal animation
"""
import numpy as np

class SkeletonData( object ):
    # joint Draw styles - note, enum corresponds to DoF count
    JOINT_END   = 0 # end
    JOINT_HINGE = 1 # r
    JOINT_HARDY = 2 # r r 
    JOINT_BALL  = 3 # r r r
    JOINT_COMP1 = 4 # r r r t
    JOINT_COMP2 = 5 # r r r t t
    JOINT_FREE  = 6 # r r r t t t
    
    def __init__( self ):
        self.joint_names   = [] # s   List of Joint names, as encountered
        self.joint_count   = 0  # i   num joints encountered
        self.joint_chans   = [] # i   active DoFs of each joint in order like GIANT
        self.chan_label    = [] # s   label of each channel (root.tx etc)
        self.joint_chanidx = [] # i   idx of joint's channels
        self.joint_parents = [] # i   parent of joint at idx, [0]==-1 (world)
        self.joint_LUT     = {} # s:i Dict of Name->Idx
        self.joint_L_mats  = [] # np  list of 3x4 Local Matrix
        self.joint_styles  = [] # i   list of joint styles, for drawing
        self.anim = AnimData()  # obj of channel data
        
        
class AnimData( object ):
    
    def __init__( self ):
        self.frame_rate  = 0  # fps
        self.frame_count = 0  # num frames
        self.frame_durr  = 0  # durration of a frame (for playback)
        self.frames      = [] # frames x channels array

