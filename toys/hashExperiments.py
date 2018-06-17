""" need to project known 3d points through a P matrix, and assign their IDs to
    some unknown 2Ds, first step is to hash both sets of 2D values, compare
    2Ds in the same bucket & their 8-neighbours before looking further afield

    Maybe brute force it for now, but a Hungarian assignment would be the way to go.
"""
import numpy as np
import math

def hash_nieve( x, y, cell_sz ):
    # round Vs floor?
    h_x = round( x / cell_sz )
    h_y = round( y / cell_sz ) * cell_sz
    return int( h_x + h_y )

# expect a 512x512 sensor, 32x32 buckets
SZ = 512. / 32
print SZ
dets = [ [0,0], [2,2], [10,10],
         [16,2], [17,2], [18,2], [30,2], [31,2], [32,2],
         [16,10], [17,10], [18,10],
         [45,45], [55,55],
         [256,256], [260,260], [270,270],
         [400,400], [500,500], [511,511], [512,512] ]

for x, y in dets:
    print x, y, hash_nieve( x, y, SZ )

if False:    
    for y in range( 4, 69, 8 ):
        for x in range( 1, 64, 4 ):
            print x, y, hash_nieve( x, y, SZ )
