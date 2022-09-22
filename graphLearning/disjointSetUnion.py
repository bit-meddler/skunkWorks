class WouldCycleException( Exception ):
    pass


class DSU:

    ROOT = -1

    def __init__( self, num_nodes ):
        self.num_nodes = num_nodes
        self.edge_list = []
        self.parents   = [ self.ROOT for i in range(num_nodes) ]
        self.ranks     = [ 1 for i in range(num_nodes) ]


    def addEdge( self, u, v ):
        try:
            self.make_union( u, v )
            self.edge_list.append( (u, v) )

        except WouldCycleException:
            print( "adding '{}->'{}' would cause a cycle".format( u, v ) )

    def make_union( self, left, right ):
        # add with cycle protection
        # Balence by Rank

        p_left  = self.find_leader( left  )
        p_right = self.find_leader( right )

        if( (p_right != p_left) or (p_left == self.ROOT) ):
            r_left  = self.ranks[ p_left ]
            r_right = self.ranks[ p_right ]

            if( r_left < r_right ):
                self.parents[ p_left ] = p_right
                self.ranks[ p_right ] += r_left

            else:
                self.parents[ p_right ] = p_left
                self.ranks[ p_left ] += r_right

        else:
            raise WouldCycleException

    def find_leader( self, node ):
        parent = self.parents[ node ]

        if( parent == self.ROOT ):
            return node

        grandparent = self.find_leader( parent )
        self.parents[ node ] = grandparent
        return grandparent

    def optimizePaths( self ):
        for i in range( self.num_nodes ):
            _ = self.find_leader(i)

        print( self.parents )


if( __name__ == "__main__" ):
    g = DSU( 9 )
    g.addEdge( 0, 1 )
    g.addEdge( 1, 2 )
    g.addEdge( 7, 6 )
    g.addEdge( 2, 3 )
    g.addEdge( 4, 5 )
    g.addEdge( 7, 5 )
    g.addEdge( 5, 1 )
    g.addEdge( 8, 5 )

    g.optimizePaths()