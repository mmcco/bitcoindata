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
        txs.append(set())


# returns the given addresses's root and rank in a tuple
def getRoot(addr):
    if type(addresses[addr]) == int:
        return addr
    else:
        root = getRoot(addresses[addr])
        addresses[addr] = root
        return root


def union(args):
    
    if len(args) < 2:
        raise Exception("union() passed a list of length < 2")

    roots = set(map (getRoot, args))

    # if the roots are already equal, we're done
    if len(roots) == 1:
        return

    rootRanks = [(root, addresses[root]) for root in roots]
    parent = max (rootRanks, key = (lambda x: x[1]))
    rootRanks.remove(parent)
    # make everyone child root point to the parent root
    for child in rootRanks:
        addresses[child[0]] = parent[0]
    
    # increment the root's rank if we're connecting a tree of equal rank
    if type(addresses[parent[0]]) != int:
        raise Exception(parent[0] + " was used as a parent, but its dict value is " + addresses[parent[0]] + " which is not of type int")
    for child in rootRanks:
        if child[1] == parent[1]:
            addresses[parent[0]] += 1
            break
        elif child[1] > parent[1]:
            raise Exception("parent selected did not have the highest rank")


txs = [set()]  # index is txID, value is a list of its inputs' addresses
inputs = open("newInputs.csv", "r")

print "beginning loading addresses into dictionary by transaction"
numInputs = 0

# fill a dict with a key for each address
for line in inputs:

    data = parseInput(line)
    txID = int(data[0])
    if len(txs) <= txID:
        resizeTxs(txID)
    txs[txID].add(data[3])

    numInputs += 1
    
print "dictionary load took " + str(time.time() - lastTime) + " seconds"
print str(numInputs) + " inputs were processed"
print "creating dictionary of addresses, initializing roots"
lastTime = time.time()

addresses = dict() # associates address with user

# populate addresses dict, making an index of value 0 for each address
for tx in txs:
    for addr in tx:
        addresses[addr] = 0

print "creating union dictionary took " + str(time.time() - lastTime) + " seconds"
print "number of addresses: " + str(len(addresses))
lastTime = time.time()
print "beginning union-find on addresses"

for tx in txs:
    if len(tx) > 1:
        union(tx)

print "union-find took " + str(time.time() - lastTime) + " seconds"
lastTime = time.time()
print "merging all users into a dictionary"

usersDict = dict() # associates users' address sets with their roots

for key, value in addresses.iteritems():
    
    root = key
    while type(addresses[root]) != int:
        root = addresses[root]

    if not root in usersDict:
        usersDict[root] = set([key])

    else:
        usersDict[root].add(key)

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

userFile = open("users.csv", "w")

for counter, user in enumerate(users):
    for addr in user:
        userFile.write(addr + "," + str(counter) + "\n")

userFile.close()
