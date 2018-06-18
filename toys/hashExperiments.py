""" need to project known 3d points through a P matrix, and assign their IDs to
    some unknown 2Ds, first step is to hash both sets of 2D values, compare
    2Ds in the same bucket & their 8-neighbours before looking further afield

    Maybe brute force it for now, but a Hungarian assignment would be the way to go.
"""
import numpy as np
import math
from random import randint
from Tkinter import *


def hash_nieve( x, y, res, num_cells ):
    # round Vs floor?
    divisor = res / num_cells
    h_x = math.floor( x / divisor )
    h_y = math.floor( y / divisor ) * num_cells
    return int( h_x + h_y )


class Hash2D( object ):
    
    def __init__( self, res, cells ):
        self.res = float( res )
        self.cells = float( cells )
        self.divisor = self.res/self.cells

        
    def hashPair( self, x, y ):
        h_x = math.floor( x / self.divisor )
        h_y = math.floor( y / self.divisor ) * self.cells
        return int( h_x + h_y )

    def hashList( self, list ):
        # assumes Nx2 np.array
        ret = np.zeros_like( list )
        ret[:,0] = np.floor( list[:,0] / self.divisor )
        ret[:,1] = np.floor( list[:,1] / self.divisor )
        ret[:,1] *= self.cells
        return np.array( np.sum( ret, axis=1 ), dtype=np.int )

    
# expect a 512x512 sensor, 32x32 buckets
RES = 512.
CELLS = 32
print( "Sensor resolution: {}, Cells: {}".format( RES, CELLS**2 ) )

if False:
    dets = [ [0,0], [2,2], [10,10],
             [16,2], [17,2], [18,2], [30,2], [31,2], [32,2],
             [16,10], [17,10], [18,10],
             [45,45], [55,55],
             [256,256], [260,260], [270,270],
             [400,400], [500,500], [511,511], [512,512] ]
    for x, y in dets:
        print x, y, hash_nieve( x, y, RES, CELLS )


if False:    
    for y in range( 4, 69, 8 ):
        for x in range( 1, 64, 4 ):
            print x, y, hash_nieve( x, y, RES, CELLS )
            
d={}
if False:
    for x in range( 0, RES, 3 ):
        for y in range( 0, RES, 3 ):
            h = hash_nieve( x, y, RES, CELLS )
            if h in d:
                d[h].append( (x,y) )
            else:
                d[h] = [ (x,y) ]

if False:
    for i in range( 800 ):
        x = randint( 0, RES )
        y = randint( 0, RES )
        h = hash_nieve( x, y, RES, CELLS )
        if h in d:
            d[h].append( (x,y) )
        else:
            d[h] = [ (x,y) ]

    # Visualize buckets & ocupancy.
    x = sorted( d.keys() )
    
    master = Tk()
    canvas = Canvas( master, width=300, height=300, bg='white' )
    canvas.pack( expand=YES, fill=BOTH )                
    cols = [ 'red', 'green', 'blue', 'black', 'yellow' ]
    extents={}
    for i, k in enumerate( x ):
        v = d[k]
        TL, BR = min( v ), max( v )
        extents[ k ] = ( TL, BR )
        canvas.create_rectangle( TL[0], TL[1], BR[0], BR[1],
                                 width=0, fill=cols[i%len(cols)],
                                 tags="k_{}".format( k )
        )
    print( "buckets used: {}".format( len( x ) ) )
    def _canvCB( e ):
        X = canvas.find_withtag( CURRENT )
        t = canvas.gettags( X )
        if( len( t ) > 0 ):
            _,val = t[0].split('_')
            k = int( val )
            c = len( d[ k ] )
            print k, c, extents[ k ]
    canvas.bind( "<Button-1>", _canvCB )
    mainloop()

# Now try matching to sets of 2D points that have been peturbed
num = 144
X  = np.random.uniform( 0, RES, (num,2) )
Z = X + np.random.uniform( -5, 5, (num,2) )
for i in range( num/10 ):
    sign = ((i % 2) * -2) + 1
    magnitude = np.random.uniform( 12, 55 ) * sign # some will be outlyers
    idx = randint(0,num-1)
    print idx, magnitude
    Z[ idx ] += magnitude
    
master = Tk()
canvas = Canvas( master, width=300, height=300, bg='white' )
canvas.pack( expand=YES, fill=BOTH )

hasher = Hash2D( RES, CELLS )
X_h = hasher.hashList( X )
Z_h = hasher.hashList( Z )

print X_h

for i in range( num ):
    x,y = X[ i ]
    canvas.create_rectangle( x-1, y-1, x+1, y+1,
                                 width=0, fill='red',
                                 tags="X_{}".format( i )
    )
    x,y = Z[ i ]
    canvas.create_rectangle( x-1, y-1, x+1, y+1,
                                 width=0, fill='blue',
                                 tags="Z_{}".format( i )
    )

def _canvCB( e ):
    X = canvas.find_withtag( CURRENT )
    t = canvas.gettags( X )
    if( len( t ) > 0 ):
        _,val = t[0].split('_')
        k = int( val )
        print k

        
canvas.bind( "<Button-1>", _canvCB )
mainloop()
# 4 neighbors = N + 1, N - 1; N-16, N+16;
# 8 neighbours = N-1, N+1; N-15, N-17, N-17; N+15, N+16, N+17
