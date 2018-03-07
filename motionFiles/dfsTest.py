pc = """Hips	GLOBAL
Spine	Hips
Spine1	Spine
Spine2	Spine1
Spine3	Spine2
Neck	Spine3
Head	Neck
HeadEnd	Head
RightShoulder	Spine3
RightArm	RightShoulder
RightForeArm	RightArm
RightForeArmRoll	RightForeArm
RightHand	RightForeArmRoll
RightHandEnd	RightHand
R_FingersEnd	RightHandEnd
RightHandThumb1	RightHand
RightHandThumb2	RightHandThumb1
LeftShoulder	Spine3
LeftArm	LeftShoulder
LeftForeArm	LeftArm
LeftForeArmRoll	LeftForeArm
LeftHand	LeftForeArmRoll
LeftHandEnd	LeftHand
L_FingersEnd	LeftHandEnd
LeftHandThumb1	LeftHand
LeftHandThumb2	LeftHandThumb1
RightUpLeg	Hips
RightLeg	RightUpLeg
RightFoot	RightLeg
RightToeBase	RightFoot
RightToeBaseEnd	RightToeBase
LeftUpLeg	Hips
LeftLeg	LeftUpLeg
LeftFoot	LeftLeg
LeftToeBase	LeftFoot
LeftToeBaseEnd	LeftToeBase"""


def dfs( graph, root ):
    path = []
    q = [ root ]
    while( len( q ) > 0 ):
        leaf = q.pop( 0 )
        if leaf not in path:
            path.append( leaf )
            q = graph[ leaf ] + q
    return path


pairs = pc.splitlines()
s_graph = {"GLOBAL":[]}
for line in pairs:
    child, parent = line.split()
    if parent in s_graph:
        s_graph[ parent ].append( child )
    else:
        s_graph[ parent ] = [ child ]
    if child not in s_graph:
        s_graph[ child ] = []

root = s_graph[ "GLOBAL" ][0] # assume one root
eval_order = dfs( s_graph, root )

print len( eval_order ), eval_order
