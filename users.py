def parseInput(inputLine):
    data = inputLine.split(",")
    # remember, this is only meant to parse newInputs.csv, not inputs.csv
    if len(data) != 7:
        raise Exception("bad line in inputs - cannot parse  -==-  " + inputLine + "  -==- length of parsed input line is " + str(len(data)))
    return data


def resizeTxs(count):
    for i in range(0, count):
        txs.append([])


# returns the given addresses's root and rank in a tuple
def getRoot(addr):
    rank = 1
    while addresses[addr] != None:
        addr = addresses[addr]
        rank += 1
    return (addr, rank)


# helper function, returns whether all items in a list are equal
def areAllEqual(args):

    for i in range (0, len(args) - 1):
        if args[i] != args[i+1]:
            return False

    return True


def union(args):

    if len(args) < 2:
        raise Exception("union() passed a list of length < 2")

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


print "len(addresses): " + str(len(addresses))


usersDict = dict() # associates users' address sets with their roots

for key, value in addresses.iteritems():
    
    if value is None:
        root = key
    else:
        root = getRoot(value)[0]

    if not root in usersDict:
        usersDict[root] = [key]

    else:
        usersDict[root].append(key)

# generate a list of addresses, each index being a user, from usersDict
users = []

for key, value in usersDict.iteritems():
    users.append(value)
