# Parse root data
# 1) make lists of root data
# 2) swizle co-ord system: +X = +X, +Y = +Z, +Z = +Y, and scale it

import numpy as np

SWZ = np.array( [ [ 100.0,  0.0,    0.0 ],
                  [   0.0,  0.0,  100.0 ],
                  [   0.0, -1.0,    0.0 ] ], dtype=np.float )


def parseRootCSV( file_fq ):
    file_name, _ = file_fq.split( "." )
    name = file_name[4:]
    fh = open( file_fq, "r" )
    line = fh.readline() # header
    points = []
    point_splits =[0]
    line = fh.readline()
    while( line ):
        x,y,z,eol = map( float, line.split() )
        points.append( (x,y,z) ) 
        if( eol > 0.0 ):
            point_splits.append( len( points ) )
        line = fh.readline()
    fh.close()

    pts = np.array( points, dtype=np.float )
    conv = np.dot( pts, SWZ )

    return conv, point_splits


def generateMayaScript( tree_dict ):
    ret = "# Generated root data\nroot_dict = {}\n"
    for name, (points, point_splits) in tree_dict.iteritems():
        ret += "root_dict[ '{}' ] = []\n".format( name )
        for i, (s_in, s_out) in enumerate( zip( point_splits[:-1], point_splits[1:] ) ):
            ret += "root_dict[ '{}' ].append( [".format( name ) )
            for point in conv[s_in:s_out]:
                out += "[ {}, {}, {} ], ".format( point[0], point[1], point[2] )
            out += " ] )\n"
            
    return ret

    
def outputFile( tree_dict, out_file ):
    preamble = """# Convert root survey data to maya representation
import maya.cmds as mc

"""
    
    root_data = generateMayaScript( tree_dict )
    
    program = """
# Helper funcs

def makeCurve( pts, name ):
    return mc.curve( d=1, p=pts, n=name )
    
def makeLoc( pos, name ):
    return mc.spaceLocator( p=pos, n=name )
    
def mkShader( sname, matCol, specCol, ref=.5 ):
    # Make shader & Group
    shader = mc.shadingNode( "blinn", asShader=True )
    sg = mc.sets( renderable=True, noSurfaceShader=True, empty=True, name=sname )
    mc.connectAttr( '{}.outColor'.format( shader ),
                    '{}.surfaceShader'.format( sg ) )
    # setup material
    mc.setAttr( "{}.color".format( shader ),
                matCol[0], matCol[1], matCol[2], "double3" )
    mc.setAttr( "{}.specularColor".format( shader ),
                specCol[0], specCol[1], specCol[2], "double3" )
    mc.setAttr( "{}.reflectivity".format( shader ), ref )
    return sg

def extrudeAllongCurve( curr_curve, name, rad=2, taper=1, shader=None ):
    start_pos = mc.pointOnCurve( curr_curve )
    normal = mc.pointOnCurve(curr_curve, nt=True )

    curr_circle = mc.circle( c=start_pos, nr=normal, r=rad )[0]
    shape = mc.extrude( curr_circle, curr_curve, et=2, sc=taper, p=start_pos, n=name )[0]
    
    mc.delete( curr_circle )

    if( shader not None ):
        mc.sets( fe=shader, e=True )
    return shape
    
# make shaders
mkShader( "red", (0.4709, 0.0184, 0.0184), (1, 0.00599998, 0.0059999), ref=.905 )
mkShader( "blue", (0.0351, 0.0351, 0.3581), (0.0, 0.0, 1.0), ref=.905 )
mkShader( "white", (0.6, 0.6, 0.6), (1, 1.0, 1.0), ref=.905 )
mkShader( "yellow", (0.784, 0.784, 0.045472), (1.0, 1.0, 0.666), ref=.905 )


# settings
taper_val = 0.35

# do both root systems
for name, roots in root_dict:
    shapes = []
    root_shader = "red" if name=="Maple" else "blue"
    for i in range( len( roots ) ):
        pts = roots[ i ]
        curr_curve = makeCurve( pts, "{0}_{1}".format( name, i ) )[0]
        shape = extrudeAllongCurve( curr_curve, "NRB_{}_root_{}".format(name, i), rad=2, taper=taper_val, shader=root_shader )
        mc.delete( curr_curv) )
        shapes.append( shape )
    
    # Group
    mc.group( *shapes, n="{}_roots".format( name ), w=True )
"""

    survey = """# place helper locators (currently a fudge)
mc.spaceLocator( p=(0., 0., 0.), n="LOC_Maple" )
mc.spaceLocator( p=(-500., 500., 0.), n="LOC_Ash" )

# Generate sweeps

# Maple
shapes = []
pos = mc.xform( "LOC_Maple", q=1, ws=1, rp=1)
for i in range( 1, 21 ):
    rad = 50 + (30*i)
    curr_curve = mc.circle( c=pos, nr=(0.,1.,0.), r=rad, sw=180.0, s=24)[0]
    shape = extrudeAllongCurve( curr_curve, "NRB_{}_sweep_{}".format(name, i), rad=2, shader="yellow" )
    mc.delete( curr_curv) )
    shapes.append( shape )
    # keyframe
    mc.setKeyframe( shape, v=0, at='visibility', t=1 )
    mc.setKeyframe( shape, v=1, at='visibility', t=i*10 )
    
mc.group( *shapes, n="Maple_sweeps", w=True )

#Ash
shapes = []
pos = mc.xform( "LOC_Ash", q=1, ws=1, rp=1 )
for i in range( 1, 6 ):
    rad = 50 + (30*i)
    curr_curve = mc.circle( c=pos, nr=(0.,1.,0.), r=rad, sw=180.0, s=24)[0]
    shape = extrudeAllongCurve( curr_curve, "NRB_{}_sweep_{}".format(name, i), rad=2, shader="white" )
    mc.delete( curr_curv) )
    shapes.append( shape )
    # keyframe
    mc.setKeyframe( shape, v=0, at='visibility', t=1 )
    mc.setKeyframe( shape, v=1, at='visibility', t=(200 + (i*10)) )
    
mc.group( *shapes, n='Ash_sweeps', w=True )
"""

    # assemble file
    fh = open( out_file+".py", "wb" )
    
    fh.write( preamble  )
    fh.write( root_data )
    fh.write( program   )
    fh.write( survey    )
    fh.close()
    

for file in ["rootAsh.txt", "rootMaple.txt"]:
    parseRootCSV( file )

