class Graph( object ):

    INF = 1_000_000

    def __init__( self, num_nodes ):
        self.num_nodes = num_nodes+1
        self.edge_list = []

    def addEdge( self, source, target, weight ):
        self.edge_list.append( (source, target, weight) )

    def printGraph( self ):
        for edge in self.edge_list:
            print( "{}->{}@{}".format(edge[0], edge[1], edge[2]) )

    def bellamnFord( self, source=1 ):
        dist = [ self.INF for _ in range( self.num_nodes ) ]
        dist[ source ] = 0

        for i in range( 1, self.num_nodes ):
            for u, v, w in self.edge_list:
                if( dist[u]!=self.INF and dist[u] + w < dist[v] ):
                    dist[v] = dist[u] + w

        #
        for u, v, w in self.edge_list:
            if( dist[u] + w < dist[v] ):
                print("Error - Negative Weight Cycle")
                return

        for i in range( 1, self.num_nodes ):
            print( "distance from {} to {} is {}".format(source, i, dist[ i ]) )

        return

if( __name__ == '__main__' ):
    g = Graph(3)
    g.addEdge( 1, 2, 3 )
    g.addEdge( 2, 3, 4 )
    g.addEdge( 1, 3, -10 )

    g.printGraph()

    g.bellamnFord()