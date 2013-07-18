# this class represents a set of bitcoin user transactions
# it also allows us to write it to the network markup language GraphML
# this allows for interfacing with network analysis and visualization programs

class Network:
    nodes = set([])
    edges = set([])

    def addNode (self, userID):
        self.nodes.add(userID)

    def addEdge (self, fromUser, toUser):
        if fromUser not in self.nodes:
            raise Exception("userID", fromUser, "passed to Network.addEdge() but does not exist in nodes")

        if toUser not in self.nodes:
            raise Exception("userID", toUser, "passed to Network.addEdge() but does not exist in nodes")

        self.edges.add((fromUser, toUser))

    def writeGraphML (self, filename):
        graphFile = open(filename, "w")

        graphFile.write('<?xml version="1.0" encoding="UTF-8"?>\n<graphml xmlns="http://graphml.graphdrawing.org/xmlns">\n<graph id="bitcoin" edgedefault="directed">\n')
        
        for node in self.nodes:
            graphFile.write('<node id="' + str(node) + '"/>\n')

        for edge in self.edges:
            graphFile.write('<edge source="' + str(edge[0]) + '" target="' + str(edge[1]) + '"/>\n')

        graphFile.write('</graph>\n</graphml>\n')
        graphFile.close()
