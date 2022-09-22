import math


def dist_sq( A, B ):
    dx = A[0] - B[0]
    dy = A[1] - B[1]
    return int( dx*dx + dy*dy )

def dist_apx( A, B ):
    dx = A[0] - B[0]
    dy = A[1] - B[1]
    
    if( dx < 0 ): dx = -dx
    if( dy < 0 ): dy = -dy
    
    if( dy > dx ):
        return dy + (dx // 2)
    else:
        return dx + (dy // 2)

def defix( num ):
    lo =  num & 0x00FF
    hi = (num & 0xFF00) >> 8
    return (hi,lo)

X = [6,6]
locs = { "A":[3,3], "B":[3,8], "C":[8,9], "D":[5,4], "E":[9,1], "F":[6,8] }
for name, pos in locs.items():
    print( "{} exact:{} est:{}".format( name, math.sqrt( dist_sq( X, pos ) ), dist_apx( X, pos ) ) )

X = [600,600]
locs = { "A":[300,300], "B":[300,800], "C":[800,900], "D":[500,400], "E":[900,100], "F":[600,800] }
for name, pos in locs.items():
    print( "{} exact:{} est:{}".format( name, math.sqrt( dist_sq( X, pos ) ), dist_apx( X, pos ) ) )

X = [6<<8,6<<8]
locs = { "A":[3<<8,3<<8], "B":[3<<8,8<<8], "C":[8<<8,9<<8], "D":[5<<8,4<<8], "E":[9<<8,1<<8], "F":[6<<8,8<<8] }

for name, pos in locs.items():
    print( "{} fixed:{}".format( name, defix( dist_apx( X, pos ) ) ) )
