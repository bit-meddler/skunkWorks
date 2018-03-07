"""
Toy quicksort implementation
"""

def part( array, lo_idx, hi_idx ):
    idx = lo_idx - 1
    pivot = array[ hi_idx ]
    
    print( "Pivoting {} between {} and {}".format( pivot, lo_idx, hi_idx ) )
    for i in range( lo_idx, hi_idx ):
        if( array[i] <= pivot ):
            idx += 1
            # swap
            array[ i ], array[ idx ] = array[ idx ], array[ i ]
        #twoPointPrint( array, i, idx )
    idx += 1
    array[ hi_idx ], array[ idx ] = array[ idx ], array[ hi_idx ]
    return idx
    
    
def quicksort( array, lo_idx, hi_idx ):
    if( hi_idx > lo_idx ):
        p_idx = part( array, lo_idx, hi_idx )
        
        quicksort( array, lo_idx,  p_idx-1 )
        quicksort( array, p_idx+1, hi_idx  )


def noRecurse( array ):
    q = [ [0, len( array )-1], ]
    while( len( q ) > 0 ):
        lo, hi = q.pop()
        if( lo < hi ):
            pi = part( array, lo, hi )
            q.append( [lo, pi-1] )
            q.append( [pi+1, hi] )
    
    
def twoPointPrint( array, top_i, bot_i ):
    print( " " + ("   "*top_i) + "v" )
    print( array )
    print( " " + ("   "*bot_i) + "^" )

    
if( __name__ == "__main__" ):
    l = [ 2, 4, 7, 3, 5, 9, 8, 2, 3, 5, 3 ]
    quicksort( l, 0, len(l)-1 )
    l = [ 2, 4, 7, 3, 5, 9, 8, 2, 3, 5, 3 ]
    print( "Non Recursive" )
    noRecurse( l )
