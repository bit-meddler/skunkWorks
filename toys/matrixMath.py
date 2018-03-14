""" 
    Matrix Math, but in english
    for teaching
"""

def matMulEng( A, B ):
    A_r = len( A )
    A_c = len( A[0] )
    B_r = len( B )
    B_c = len( B[0] )
    
    C = [ [ "" for r in range( B_c )] for c in range( A_r ) ]
    
    for i in range( A_r ):
        for j in range( B_c ):
            for k in range( A_c ):
                Av = A[i][k]
                Bv = B[k][j]
                if( (Av=="0") or (Bv=="0") ):
                    continue
                elif( (Av=="1") and (Bv=="1") ):
                    C[i][j] += "+1"
                else
                    C[i][j] += "+(" + Av + "*" + Bv + ")"
                
    return C
    
X = [[    "1",    "0",    "0" ],
     [    "0",  "cvx", "-svx" ],
     [    "0",  "svx",  "cvx" ]]
     
Y = [[  "cvy",    "0",  "svy" ],
     [    "0",    "1",    "0" ],
     [ "-svy",    "0",  "cvy" ]]
     
Z = [[  "cvz", "-svz",    "0" ],
     [  "svz",  "cvz",    "0" ],
     [    "0",    "0",    "1" ]]


for order in [ "XYZ", "XZY", "YXZ", "YZX", "ZXY", "ZYX" ]:
    
    M = [[    "1",    "0",    "0" ],
         [    "0",    "1",    "0" ],
         [    "0",    "0",    "1" ]]
    
    for ax in order[::-1]:
        if ax=="X":
            M = matMulEng( M, X )
        if ax=="Y":
            M = matMulEng( M, Y )
        if ax=="Z":
            M = matMulEng( M, Z )
                                    
    print( order )
    print( M )
