
OSX = (0, 1, 0, -1)
OSY = (-1, 0, 1, 0)

def map4Neighbours( x, y, mx, my, grid, visited, count ):
    size = 1
    for i in range( 4 ):
        nx = x + OSX[i]
        ny = y + OSY[i]

        if( (0 <= nx < mx) and (0 <= ny < my) and not visited[nx][ny] ):

            if( grid[nx][ny] ): # has island
                visited[nx][ny] = count
                size += map4Neighbours( nx, ny, mx, my, grid, visited, count )

            else:
                visited[nx][ny] = -1

    return size

def search( grid ):
    mx = len( grid )
    my = len( grid[0] )

    visited = [ [0 for i in range(my)] for j in range( mx ) ]

    largest, num, count = 0, 0, 0
    for i in range( mx ):
        for j in range( my ):
            
            if( not visited[i][j] ):

                if( grid[i][j] ):
                    count += 1
                    visited[i][j] = count
                    size = map4Neighbours( i, j, mx, my, grid, visited, count )

                    if( size > largest ):
                        largest = size
                        num = count

                else:
                    visited[i][j] = -1

    print( visited )
    print( num )

    return largest


grid  = [ [1, 0, 0, 1, 0],
          [1, 0, 1, 0, 0],
          [0, 0, 1, 0, 1],
          [1, 0, 1, 1, 1],
          [1, 0, 1, 1, 0] ]

print( search( grid ) )