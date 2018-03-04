"""
Toy quicksort implementation
"""

def part( array, lo_idx, hi_idx ):
    idx = lo_idx - 1
    cnt = (hi_idx - lo_idx) / 2
    pivot = (array[ lo_idx ] + array[ hi_idx ] + array[ cnt ]) / 3
    print( "Pivoting {}".format( pivot ) )
    for i in range( lo_idx, hi_idx+1 ):
        if( array[i] <= pivot ):
            idx += 1
            # swap
            array[ i ], array[ idx ] = array[ idx ], array[ i ]
        twoPointPrint( array, i, idx )
    return idx
    
    
def quicksort( array, lo_idx, hi_idx ):
    p_idx = part( array, lo_idx, hi_idx )
    
    quicksort( array, lo_idx,  p_idx  )
    quicksort( array, p_idx+1, hi_idx )
    
    
def twoPointPrint( array, top_i, bot_i ):
    print( " " + ("   "*top_i) + "v" )
    print( array )
    print( " " + ("   "*bot_i) + "^" )
    
if( __name__ == "__main__" ):
    l = [2, 4, 7, 3, 5, 9, 8, 2, 3, 5, 3 ]
    quicksort( l, 0, len(l)-1 )
