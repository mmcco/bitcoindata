import time

lastTime = time.time()

def parseInput(inputLine):

    data = inputLine.split(",")
    # remember, this is only meant to parse newInputs.csv, not inputs.csv
    if len(data) != 7:
        raise Exception("bad line in inputs - cannot parse  -==-  " + inputLine + "  -==-  length of parsed input line is " + str(len(data)))
    return data


def resizeTxs(count):
    for i in range(0, count):
        txs.append([])


# returns the given addresses's root and rank in a tuple
def getRoot(addr):

    rank = 1
    while addresses[addr] is not None:
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

print "beginning loading addresses into dictionary by transaction"
numInputs = 0

# fill a dict with a key for each address
for line in inputs:

    data = parseInput(line)
    txID = int(data[0])
    if len(txs) <= txID:
        resizeTxs(txID)
    txs[txID].append(data[3])

    numInputs += 1
    
print "dictionary load took " + str(time.time() - lastTime) + " seconds"
print str(numInputs) + " inputs were processed"
print "creating dictionary of addresses, initializing roots"
lastTime = time.time()

addresses = dict() # associates address with user

# populate addresses dict, making an index of value None for each address
for tx in txs:
    for addr in tx:
        addresses[addr] = None

print "creating union dictionary took " + str(time.time() - lastTime) + " seconds"
print "number of addresses: " + str(len(addresses))
lastTime = time.time()
print "beginning union-find on addresses"

for tx in txs:
    if len(tx) > 1:
        union(tx)

print "union-find took " + str(time.time() - lastTime) + " seconds"
lastTime = time.time()
print "merging all uses into a dictionary"

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

print "merging users into dictionary took " + str(time.time() - lastTime) + " seconds"
lastTime = time.time()
print "number of users in dictionary: " + str(len(usersDict))
print "converting users dictionary into a list"

# generate a list of addresses, each index being a user, from usersDict
users = []

for key, value in usersDict.iteritems():
    users.append(value)

print "converting dictionary into list took " + str(time.time() - lastTime) + " seconds"
print "user generation completed"
