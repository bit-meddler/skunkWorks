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

    
    fh = open( file_name+".py", "wb" )
    fh.write( "roots = {}\n" )
    for i, (s_in, s_out) in enumerate( zip( point_splits[:-1], point_splits[1:] ) ):
        out = "{0}_{1} = [ ".format( name, i )
        for point in conv[s_in:s_out]:
            out += "[ {}, {}, {} ], ".format( point[0], point[1], point[2] )
        out += " ]\n"
        out += "roots[ {1} ] = {0}_{1}\n\n".format( name, i )
        fh.write( out )
        
    out = "name = '{}'\n".format( name )
    fh.write( out )
    
    program = """
import maya.cmds as mc

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


# make shaders
mkShader( "red", (0.4709, 0.0184, 0.0184), (1, 0.00599998, 0.0059999), ref=.905 )
mkShader( "blue", (0.0351, 0.0351, 0.3581), (0.0, 0.0, 1.0), ref=.905 )

# settings
taper_val = 0.35

shapes = []
for i in range( len(roots) ):
    pts = roots[ i ]
    makeCurve( pts, "{0}_{1}".format( name, i ) )
    
    pos = pts[ 0 ]
    curr_curve = "{}_{}".format( name, i )
    normal = mc.pointOnCurve(curr_curve, nt=True )
    curr_circle = mc.circle( c=pos, nr=normal, r=2 )[0]
    shape = mc.extrude( curr_circle, curr_curve, et=2, sc=taper_val, p=pos, n="SFS_{}_{}".format( name, i ) )[0]

    # Attach Shader
    shader = "red" if name=="Maple" else "blue"
    mc.sets( fe=shader, e=True )

    # Cleanup
    mc.delete( (curr_circle, curr_curve) )
    shapes.append( shape )
    
# Group
"""
    program += "mc.group( *shapes, n='{}', w=True )\n".format( file_name )
    
    fh.write( program )
    fh.close()

for file in ["rootAsh.txt", "rootMaple.txt"]:
    parseRootCSV( file )

