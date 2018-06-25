# Parse root data
# 1) make lists of root data
# 2) swizle co-ord system: +X = +X, +Y = +Z, +Z = +Y, and scale it

import numpy as np

SWZ = np.array( [ [ 100.0,  0.0,    0.0 ],
                  [   0.0,  0.0,  100.0 ],
                  [   0.0, -1.0,    0.0 ] ], dtype=np.float )

def parseRootCSV( file_fq ):
    name, _ = file_fq.split( "." )
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

    
    fh = open( name+".py", "wb" )
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
    
    program = """def makeCurve( pts, name ):
    return mc.curve( d=1, p=pts, n=name )
    
def makeLoc( pos, name ):
    return mc.spaceLocator( p=pos, n=name )
    
for i in range( len(roots) ):
    pts = roots[ i ]
    makeCurve( pts, "{0}_{1}".format( name, i ) )
    
    pos = pts[ 0 ]
    curr_curve = "{}_{}".format( name, i )
    normal = mc.pointOnCurve(curr_curve, nt=True )
    curr_circle = mc.circle( c=pos, nr=normal, r=2 )[0]
    shape = mc.extrude( curr_circle, curr_curve, et=2, sc=taper_val, n="SFS_{}_{}".format( name, i ) )

"""
    fh.write( program )
    fh.close()

for file in ["rootAsh.txt", "rootMaple.txt"]:
    parseRootCSV( file )

