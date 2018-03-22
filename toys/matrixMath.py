""" 
    Matrix Maths, but in English
    for teaching
"""

ROTATIONS = ( "XYZ", "XZY", "YXZ", "YZX", "ZXY", "ZYX",
               "XY",  "XZ",  "YX",  "YZ",  "ZX",  "ZY",
               "X",          "Y",          "Z"          )

def _homoTest():
    A = [ [ "arxx", "aryx", "arzx", "atx" ],
          [ "arxy", "aryy", "arzy", "aty" ],
          [ "arxz", "aryz", "arzz", "atx" ],
          [    "0",    "0",    "0",   "1" ] ]

    B = [ [ "brxx", "bryx", "brzx", "btx" ],
          [ "brxy", "bryy", "brzy", "bty" ],
          [ "brxz", "bryz", "brzz", "btx" ],
          [    "0",    "0",    "0",   "1" ] ]


    return matMulEng( A, B, False )
    

def dot1dEng( A, B, optimize=True ):
    C = ""
    for i,j in zip( A, B ):
        if( ((i=="0") or (j=="0")) and optimize ):
            continue
        C += '+({}*{})'.format( i, j )
    return C

    
def _multi( A, B ):
    # Make a multiplication string
    out = "( "
    if( "*" in A ):
        out += "(" + A + ")"
    else:
        out += A
    out += "*"
    if( "*" in B ):
        out += "(" + B + ")"
    else:
        out += B
    out += " )"
    return out


def matMulEng( A, B, optimize=True ):
    A_r = len( A )
    A_c = len( A[0] )
    B_r = len( B )
    B_c = len( B[0] )
    
    C = [ [ "0" for r in range( B_c )] for c in range( A_r ) ]
    
    for i in range( A_r ):
        for j in range( B_c ):
            for k in range( A_c ):
                Av = A[i][k]
                Bv = B[k][j]

                if( Av == "0+1" ):
                    Av = "1"
                    
                if( Bv == "0+1" ):
                    Bv = "1"
                    
                if( ((Av=="0") or (Bv=="0")) and optimize ):
                    continue
                elif( (Av=="1") and (Bv=="1") ):
                    C[i][j] += "+1"
                elif( Av=="1" ):
                    if( C[i][j] == "0" ):
                        C[i][j] = ""
                    C[i][j] += Bv
                elif( Bv=="1" ):
                    if( C[i][j] == "0" ):
                        C[i][j] = ""
                    C[i][j] += Av
                else:
                    if( C[i][j] == "0" ):
                        C[i][j] = _multi( Av, Bv )
                    else:
                        C[i][j] += "+" + _multi( Av, Bv )
    return C


def _clean( M ):
    M_r = len( M )
    M_c = len( M[0] )
    new = [ [ "" for c in range( M_c ) ] for r in range( M_r ) ]
    for i in range( M_r ):
        for j in range( M_c ):
            cell = M[ i ][ j ]
            if( "(( " in cell ):
                # clean
                cell = cell.replace( "(( ", "(" )
                cell = cell.replace( " ))", ")" )
            if( "0+1" in cell ):
                cell = cell.replace( "0+1", "1" )
            cell = cell.replace( " ", "" )
            new[ i ][ j ] = cell    
    return new


def genAllRots():    
    X = [[    "1",    "0",    "0" ],
         [    "0",  "cvx", "-svx" ],
         [    "0",  "svx",  "cvx" ]]
         
    Y = [[  "cvy",    "0",  "svy" ],
         [    "0",    "1",    "0" ],
         [ "-svy",    "0",  "cvy" ]]
         
    Z = [[  "cvz", "-svz",    "0" ],
         [  "svz",  "cvz",    "0" ],
         [    "0",    "0",    "1" ]]

    ret = {}
    
    for order in ROTATIONS:
        
        M = [[    "1",    "0",    "0" ],
             [    "0",    "1",    "0" ],
             [    "0",    "0",    "1" ]]
        
        for ax in order[::-1]:
            if ax=="X":
                M = matMulEng( M, X, True )
            if ax=="Y":
                M = matMulEng( M, Y, True )
            if ax=="Z":
                M = matMulEng( M, Z, True )

        ret[ order ] = _clean( M )

    return ret


d = genAllRots()

for order in ROTATIONS:
    matrix = d[ order ]
    out = """def _rotMat{0}( rx, ry, rz ):
    # compose and simplify rotation matrix in order of {0}\n""".format( order )
    
    if( "X" in order ):
        out += "    cx, sx = np.cos( rx ), np.sin( rx )\n"
    if( "Y" in order ):
        out += "    cy, sy = np.cos( ry ), np.sin( ry )\n"
    if( "Z" in order ):
        out += "    cz, sz = np.cos( rz ), np.sin( rz )\n"
        
    out += """

    M = [ {0},
          {1},
          {2} ]
    return M

""".format( matrix[0], matrix[1], matrix[2] )

    print  out
"""
[ ['+(arxx*brxx)+(aryx*brxy)+(arzx*brxz)+(atx*0)', '+(arxx*bryx)+(aryx*bryy)+(arzx*bryz)+(atx*0)', '+(arxx*brzx)+(aryx*brzy)+(arzx*brzz)+(atx*0)', '+(arxx*btx)+(aryx*bty)+(arzx*btx)+(atx*1)'],
  ['+(arxy*brxx)+(aryy*brxy)+(arzy*brxz)+(aty*0)', '+(arxy*bryx)+(aryy*bryy)+(arzy*bryz)+(aty*0)', '+(arxy*brzx)+(aryy*brzy)+(arzy*brzz)+(aty*0)', '+(arxy*btx)+(aryy*bty)+(arzy*btx)+(aty*1)'],
  ['+(arxz*brxx)+(aryz*brxy)+(arzz*brxz)+(atx*0)', '+(arxz*bryx)+(aryz*bryy)+(arzz*bryz)+(atx*0)', '+(arxz*brzx)+(aryz*brzy)+(arzz*brzz)+(atx*0)', '+(arxz*btx)+(aryz*bty)+(arzz*btx)+(atx*1)'],
  ['+(0*brxx)+(0*brxy)+(0*brxz)+(1*0)',            '+(0*bryx)+(0*bryy)+(0*bryz)+(1*0)',            '+(0*brzx)+(0*brzy)+(0*brzz)+(1*0)',            '+(0*btx)+(0*bty)+(0*btx)+1'] ]
"""
