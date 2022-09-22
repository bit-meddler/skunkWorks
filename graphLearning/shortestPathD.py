from collections import OrderedDict


class Graph( object ):

    INF = 1_000_000

    def __init__( self, num_nodes ):
        self.num_nodes = num_nodes
        self.adj_list  = [ [] for i in range( self.num_nodes ) ]

    def addEdge( self, source, target, weight, is_directed=False ):
        self.adj_list[source].append( [weight, target] )
        if( not is_directed ):
            self.adj_list[target].append( [weight, source] )

    def printGraph( self ):
        for i, edges in enumerate( self.adj_list ):
            print( "{} -> {}".format( i, ", ".join([ f"{t} @ {w}" for w,t in edges ]) ) )

    def dijkstra( self, source, target ):
        dists = [ self.INF for _ in range( self.num_nodes ) ]
        paths = OrderedDict()

        dists[ source ] = 0
        paths[ (0,source) ] = None # get set-like functionality

        while( len( paths ) ):
            (prior_dist, node), _ = paths.popitem( last=False )

            for nbr_dist, nbr_tgt in self.adj_list[ node ] :
                new_dist = prior_dist + nbr_dist
                old_dist = dists[ nbr_tgt ]

                if( new_dist < old_dist ):
                    # remove old edge
                    old = (old_dist, nbr_tgt)
                    if( old in paths ):
                        del paths[ old ]

                    # insert new edge
                    dists[ nbr_tgt ] = new_dist
                    paths[ (new_dist, nbr_tgt) ] = None

        for i in range( self.num_nodes ):
            print( "distance from {} to {} is {}".format(source, i, dists[ i ]) )

        return dists[ target ]


if( __name__ == '__main__' ):
    g = Graph(5)

    g.addEdge( 0, 1, 1 )
    g.addEdge( 1, 2, 1 )
    g.addEdge( 0, 2, 4 )
    g.addEdge( 0, 3, 7 )
    g.addEdge( 3, 2, 2 )
    g.addEdge( 3, 4, 3 )

    g.printGraph()

    print( g.dijkstra( 0, 4 ) )