import network

btc = network.Network()

users = open("users.csv", "r")
addresses = dict()

for line in users:
    
    data = line.split(",")
    if len(data) != 2:
        raise Exception("bad line in users.csv")

    address = data[0]
    userID = data[1][:-1] # remove newline
    btc.addNode(userID)
    addresses[address] = userID

users.close()

inputs = open("newInputs.csv", "r")
txs = []

for line in inputs:
    
    data = line.split(",", 4)
    txID = int(data[0])
    address = data[3]

    while len(txs) <= txID:
        txs.append(None)

    if address not in addresses:
        raise Exception(address + " is given as an address in the addresses array, but isn't present")

    txs[txID] = addresses[address]

inputs.close()

outputs = open("newOutputs.csv", "r")

for line in outputs:
    data = line.split(",", 6)
    txID = int(data[0])

    if txs[txID] is None:
        continue
    else:
        btc.addEdge(txs[txID], addresses[data[5]])

outputs.close()

btc.writeGraphML("btc.graphml")
