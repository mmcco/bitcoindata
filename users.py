def parseInput(inputLine):
    data = inputLine.split(",")
    # allow data to be of length 5 or 7 because this function is used to parse both inputs.csv and newInputs.csv
    if len(data) != 5 and len(data) != 7:
        raise Exception("bad line in inputs - cannot parse  -==-  " + inputLine + "  -==- length of parsed input line is " + str(len(data)))
    return data

def resizeTxs(txID):
    for i in range(0, txID):
        txs.append([])

# helper function that walks to the root and returns its key
def getRoot(addr):
    rank = 1
    while addresses[addr] != None:
        addr = addresses[addr]
        rank += 1
    return (addresses[addr], rank)


# helper function, returns whether all items in a list are equal
def areAllEqual(args):
    for i in range (0, len(args) - 1):
        if args[i] != args[i+1]:
            return False

    return True

def union(args):

    if len(args) < 2:
        raise Exception("union() passed a list of length < 2  -==-  list: " + args)

    rootInfo = map (getRoot, args)  # contains both root address and rank
    roots = [i[0] for i in rootInfo]
    ranks = [i[1] for i in rootInfo]

    # if they already have the same root, we're done
    if areAllEqual(roots):
        return

    # select the root with the highest rank as the parent
    maxRank = 0
    for root in rootInfo:
        if root[1] > maxRank:
            parent = root
            maxRank = root[1]
    
    # make everyone point to the parent
    for addr in roots:
        addresses[addr] = parent[0]


txs = [[]]  # index is txID, value is a list of its inputs' addresses
inputs = open("newInputs.csv", "r")

# fill a dict with a key for each address
for line in inputs:
    data = parseInput(line)
    txID = int(data[0])
    if len(txs) <= txID:
        resizeTxs(txID)
    txs[txID].append(data[3])
    
addresses = dict() # associates address with user

# populate addresses dict, making an index of value None for each address
for tx in txs:
    for addr in tx:
        addresses[addr] = None

for tx in txs:
    if len(tx) > 1:
        union(tx)


i = 0
for i in range(0, len(txs)):
    if txs[i] != []:
        i += 1
    else:
        break

print "len(txs): " + str(i)
print "len(addresses): " + str(len(addresses))
#users = dict() # associates users' address sets with their roots
#
#for key, value in addresses.iteritems():
#    
#    if not value in users:
#        users[value] = []
#
#    users[value].append(key)
