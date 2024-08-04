def dijkstra(graph,start,goal):
    unvisited={n:float("inf") for n in graph.keys()}
    unvisited[start] = 0
    visited = {}
    revPath = {}
    
    while unvisited:
        minNode = min(unvisited, key=unvisited.get)
        visited[minNode]=unvisited[minNode]
        for neighbor in graph.get(minNode).keys():
            if neighbor in visited:
                continue
            tempDist=unvisited[minNode]+graph[minNode][neighbor]
            if tempDist < unvisited[neighbor]:
                unvisited[neighbor]=tempDist
                revPath[neighbor]=minNode
                
        unvisited.pop(minNode)
        
    node = goal
    strPath = node
    while node != start:
        strPath+=revPath[node]
        node=revPath[node]
        
    print(strPath[::-1])

myGraph={
    "A":{"B":2,"C":9,"F":4},
    "B":{"C":6,"E":3,"F":2},
    "F":{"E":3},
    "E":{"D":5,"C":2},
    "C":{"D":1},
    "D":{"C":2}
}

dijkstra(myGraph,"A","D")