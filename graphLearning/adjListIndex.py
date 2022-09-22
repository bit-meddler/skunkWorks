class GraphAL( object ):

    def __init__(self, num_nodes ):
        self.num_vertex = num_nodes
        self.vertex_list = [ [] for i in range( self.num_vertex ) ]

    def addEdge( self, source, dest, is_directed=False ):
        if( dest not in self.vertex_list[ source ] ):
            self.vertex_list[ source ].append( dest )

        if( not is_directed and source not in self.vertex_list[ dest ] ):
            self.vertex_list[ dest ].append( source )

    def printGraph( self ):
        for i, nodes in enumerate( self.vertex_list ):
            print( "{} -> {}".format( i, ", ".join(map(str,nodes)) ) )

    def shortestPathBFS( self, start_vtx, dest=-1 ):
        visited = [ False for i in range( self.num_vertex ) ]
        depths  = [    -1 for i in range( self.num_vertex ) ]
        parents = [    -1 for i in range( self.num_vertex ) ]


        visit_q = [ start_vtx ]
        visited[    start_vtx ] =  True
        depths[     start_vtx ] =  0
        parents[    start_vtx ] = -2

        res = []
        while( len( visit_q ) > 0 ):
            node = visit_q.pop(0)
            res.append( node )

            for neighbor in self.vertex_list[ node ]:
                if( not visited[ neighbor ] ):
                    visit_q.append( neighbor )
                    visited[ neighbor ] = True
                    parents[ neighbor ] = node
                    depths[  neighbor ] = depths[ node ] + 1

        for i in range( self.num_vertex ):
            print( "Dist from {} to {} is {}".format( start_vtx, i, depths[i] ) )

        path = []
        if( dest >= 0 ):
            tmp = dest
            while( tmp != start_vtx ):
                path.append( tmp )
                tmp = parents[ tmp ]

        return path

    def _simpleDFS( self, node, visited, path ):
        path.append( node )
        visited[ node ] = True

        for neighbor in self.vertex_list[ node ]:
            if( not visited[ neighbor ] ):
                self._simpleDFS( neighbor, visited, path )

    def simpleDFS( self, start_vtx ):
        visited = [ False for i in range( self.num_vertex ) ]
        path = []
        self._simpleDFS( start_vtx, visited, path )
        return path

    def _hasCycleUD( self, node, visited, parent ):
        # DFS
        visited[ node ] = True

        for neighbor in self.vertex_list[ node ]:
            if( not visited[ neighbor ] ):
                if( self._hasCycleUD( neighbor, visited, node ) ):
                    return True

            elif( neighbor != parent ):
                return True

        return False

    def hasCycleUD( self ):
        visited = [ False for i in range( self.num_vertex ) ]
        return self._hasCycleUD( 0, visited, -1 )

    def _hasCycleD( self, node, visited, instack ):
        # BFS?
        visited[ node ] = True
        instack[ node ] = True

        for neighbor in self.vertex_list[ node ]:

            if( instack[ neighbor ] ):
                return True

            if( not visited[ neighbor ] ):
                if( self._hasCycleD( neighbor, visited, instack ) ):
                    return True

        instack[ node ] = False
        return False

    def hasCycleD( self ):
        visited = [ False for i in range( self.num_vertex ) ]
        instack = [ False for i in range( self.num_vertex ) ]

        for i in range( self.num_vertex ):
            if( not visited[ i ] ):
                if( self._hasCycleD( i, visited, instack ) ):
                    return True
        return False

    @staticmethod
    def _flipColour( colour ):
        # 3-1 = 2, 3-2 = 1
        return 3 - colour

    def _testBiPartPaintingUD(self, node, visited, parent, colour ):
        visited[ node ] = colour
        
        for neighbor in self.vertex_list[ node ]:

            if( not visited[ neighbor ] ):
                if( not self._testBiPartPaintingUD( neighbor, visited, node, self._flipColour( colour ) ) ):
                    return False

            elif( neighbor!=parent and colour==visited[ neighbor ] ):
                return False

        return True

    def testBiPartPaintingUD( self ):
        visited = [ 0 for i in range( self.num_vertex ) ] # 0:unvisited, 1:Red, 2:Black
        res = self._testBiPartPaintingUD( 0, visited, -1, 1 )

        for i in range( self.num_vertex ):
            print( "node {} is {}".format( i, visited[i] ) )

        return res

    def topoSortBFS( self ):
        # Khan
        in_degree = [ 0 for i in range( self.num_vertex ) ]
        visit_q = []
        res = []

        for i in range( self.num_vertex ):
            for neighbor in self.vertex_list[i]:
                in_degree[ neighbor ] += 1

        for i, degree in enumerate( in_degree ):
            if( degree==0 ):
                visit_q.append( i )

        while( len( visit_q ) > 0 ):
            node = visit_q.pop( 0 )
            res.append( node )

            for neighbor in self.vertex_list[ node ]:
                in_degree[ neighbor ] -= 1

                if( in_degree[ neighbor ]==0 ):
                    visit_q.append( neighbor )

        return res

    def _topoSortDFS( self, node, visited, path,):
        visited[ node ] = True
        
        for neighbor in self.vertex_list[ node ]:
            if( not visited[ neighbor ] ):
                self._topoSortDFS( neighbor, visited, path )

        path.insert( 0, node )


    def topoSortDFS( self ):
        visited = [ False for i in range( self.num_vertex ) ]
        path = []

        for i in range( self.num_vertex ):
            if( not visited[i] ):
                self._topoSortDFS( i, visited, path )

        return path


if( __name__ =="__main__" ):

    # Undirected, shortest path, traversal, cycle

    g = GraphAL(7)

    g.addEdge( 0, 1 )
    g.addEdge( 1, 2 )
    g.addEdge( 2, 3 )
    g.addEdge( 3, 5 )
    g.addEdge( 5, 6 )
    g.addEdge( 4, 5 )
    g.addEdge( 0, 4 )
    g.addEdge( 3, 4 )

    # g.printGraph()
    # print( g.shortestPathBFS( 1, 6 ) )
    # print( g.simpleDFS( 1 ) )
    # print( g.hasCycleUD() )


    # Directed Cycle, Traversal, Bipartite detection

    g = GraphAL(3)
    g.addEdge( 0, 1, True )
    g.addEdge( 1, 2, True )
    g.addEdge( 2, 0, True )
    # g.printGraph()
    # print( g.shortestPathBFS( 0, 2 ) )
    # print( g.hasCycleD() )
    # print( g.testBiPartPaintingUD() )


    # DAG - topological Ordering

    g = GraphAL(6)
    g.addEdge( 0, 2, True )
    g.addEdge( 2, 3, True )
    g.addEdge( 3, 5, True )
    g.addEdge( 4, 5, True )
    g.addEdge( 1, 4, True )
    g.addEdge( 1, 2, True )
    g.printGraph()

    print( g.topoSortBFS() )
    print( g.topoSortDFS() )

    
    # Disjoint Set Union
