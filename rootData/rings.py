import maya.cmds as mc



# mayple = 20x 50cm + 30r
pos = mc.xform('Maple_base',q=1,ws=1,rp=1)

shapes = []
for i in range( 1, 21 ):
    rad = 50 + (30*i)
    curr_curve = mc.circle( c=pos, nr=(0.,1.,0.), r=rad, sw=180.0, s=24)[0]    
    mc.setAttr( "{}.overrideEnabled".format( curr_curve ), 1 )
    mc.setAttr( curr_curve + '.overrideColor', 16 )
    start  = mc.pointOnCurve( curr_curve )
    normal = mc.pointOnCurve( curr_curve, nt=True )
    #
    curr_circle = mc.circle( c=start, nr=normal, r=2 )[0]
    shape = mc.extrude( curr_circle, curr_curve, et=2, sc=1, p=start, n="sweep" )[0]
    #
    #mc.sets( fe="white", e=True )
    mc.delete( (curr_circle, curr_curve) )
    # keyframe
    mc.setKeyframe( shape, v=0, at='visibility', t=1 )
    mc.setKeyframe( shape, v=1, at='visibility', t=i*10 )
    #
    shapes.append( shape )
    
# Group
mc.group( *shapes, n='maple_sweeps', w=True )
    
    
# ash = 5 x 30xm 50r
pos = mc.xform('Ash_base',q=1,ws=1,rp=1)

shapes = []
for i in range( 1, 6 ):
    rad = 50 + (30*i)
    curr_curve = mc.circle( c=pos, nr=(0.,1.,0.), r=rad, s=24)[0]
    mc.setAttr( "{}.overrideEnabled".format( curr_curve ), 1 )
    mc.setAttr( curr_curve + '.overrideColor', 17 )
    normal = mc.pointOnCurve( curr_curve, nt=True )
    start  = mc.pointOnCurve( curr_curve )
    #
    curr_circle = mc.circle( c=start, nr=normal, r=2 )[0]
    shape = mc.extrude( curr_circle, curr_curve, et=2, sc=1, p=start, n="sweep" )[0]
    #
    #mc.sets( fe="yellow", e=True )
    mc.delete( (curr_circle, curr_curve) )
    #
    # keyframe
    mc.setKeyframe( shape, v=0, at='visibility', t=1 )
    mc.setKeyframe( shape, v=1, at='visibility', t=(200 + (i*10)) )
    shapes.append( shape )
    
# Group
mc.group( *shapes, n='ash_sweeps', w=True )