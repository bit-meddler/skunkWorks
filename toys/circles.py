import numpy as np

def circleVTX( r, step, orig ):
    if( step>126 ):
        print( "Too many subdivisions for pipe" )
        step = 126
    o_x, o_y, o_z = orig
    ang = (np.pi * 2)/step
    ret = [ orig ]
    for i in xrange( step ):
        x = o_x + ( r * np.cos( ang*i ) )
        y = o_y
        z = o_z + ( r * np.sin( ang*i ) )
        ret.append( (x,y,z) )
    return ret

def genPipe( sides, radius, t_orig, b_orig=None ):
    if b_orig == None: b_orig = t_orig 
    
    # Tri fan for top
    T = np.array( circleVTX( radius, sides, t_orig ), dtype=np.float32 )
    T_end = len( T )

    # Trifan for Base
    B = np.array( circleVTX( radius, sides, b_orig ), dtype=np.float32 )
    # idx for Tri-fans
    T_idx = np.array( range( 0, T_end ), dtype=np.uint8 )
    B_idx = np.array( range( T_end, T_end + len( B ) ), dtype=np.uint8 )
    # Compute idx order for Tri strip
    S_idx = [ B_idx[1], T_idx[1] ]
    for i in range( 1, sides ):
        S_idx.append( T_idx[ i+1 ] )
        S_idx.append( B_idx[ i+1 ] )
    # close the loop
    S_idx.append( T_idx[ 1 ] )
    S_idx.append( B_idx[ 1 ] )
    # Marshal to np arrays
    S_idx = np.array( S_idx, dtype=np.uint8 )
    VBO = np.concatenate( (T, B), axis=0 )
    return [VBO, T_idx, B_idx, S_idx]

print genPipe( 20, 5, (0,10,0), (0,-10,0) )
