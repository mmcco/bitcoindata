# This script merges addresses into users, which are entities suspected of owning multiple addresses
# It uses the traditional heuristic of assuming the addresses associated with each transaction's inputs are owned by the same user
# It also uses an additional heuristic which has not yet been published
# Specifically, if a transaction has multiple outputs, exactly one of which goes to an unused address, that address is unioned with the input addresses

# union() must be called before outputUnion()

# lists with "if x not in y" checks are used instead of sets where the CPU/memory trade-off makes sense
# this is because sets are represented as dictionaries in memory and therefore take up a lot of space

import itertools

# returns an input's txID and address in a tuple
def parseInput(inputLine):
    data = inputLine.split(",", 4)
    # remember, this is only meant to parse newInputs.csv, not inputs.csv
    if len(data) != 5:
        raise Exception("bad line in inputs - cannot parse  -==-  " + inputLine + "  -==-  length of parsed input line is " + str(len(data)))
    return (data[0], data[3])

# returns an output's txID and address in a tuple
def parseOutput(line):
    data = line.split(",", 6)
    if len(data) != 7:
        raise Exception("bad line in newOutputs.csv")
    return data

# helper function for dynamic resize of two-dimensional array
def resizeTxs(count):
    for i in range(0, count):
        inputTxs.append([])

# same as above but for another 2D array
def resizeOutputTxs(count):
    for i in range(0, count):
        outputTxs.append([])

# returns the given addresses's root
def getRoot(addr):
    if type(addresses[addr]) == int:
        return addr
    else:
        root = getRoot(addresses[addr])
        addresses[addr] = root
        return root

# returns a list of all addresses, including ones that have never spent
def getAddresses():
    with open("bitcoinData/newOutputs.csv", "r") as outputs
        addressSet = set()
        for line in outputs:
            data = line.split(",", 6)
            if len(data) < 7:
                raise Exception("bad line in newOutputs.csv")
            addressSet.add(data[5])
    return addressSet


# executes union-find on a tx's inputs
def union(args):
    
    if len(args) < 2:
        raise Exception("union() passed a list of length < 2")

    for addr in args:
        if addr not in addresses:
            raise Exception(addr, "is passed to union() but does not exist in the addresses dict")

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
        raise Exception(parent[0], "was used as a parent, but its dict value is", addresses[parent[0]], "which is not of type int")
    for child in rootRanks:
        if child[1] == parent[1]:
            addresses[parent[0]] += 1
            break
        elif child[1] > parent[1]:
            raise Exception("parent selected did not have the highest rank")


# takes the addresses in a tx's outputs, conditionally unions them
def outputUnion(args, txID):

    if len(args) < 2:
        raise Exception("outputUnion was passed a set of length < 2")
    
    for addr in args:
        if addr not in addresses:
            raise Exception(addr, "is passed to outputUnion() but does not exist in the addresses dict")

    # generate a list of tuples associating each address with a boolean that describes whether it has been used yet
    boolTuples = [(addr, addr in usedAddresses) for addr in args]
    
    # if there isn't exactly one unused address in the outputs set, we're done
    # if there is exactly one, store it as address and union it with the inputs
    executeUnion = False
    for tup in boolTuples:
        # logic for first unused address encountered
        if not tup[1] and not executeUnion:
            addr = tup[0]
            executeUnion = True
        # logic for second unused address encountered
        elif not tup[1] and executeUnion:
            executeUnion = False
            break

    # add args to list of used addresses
    map (usedAddresses.add, args)

    if not executeUnion:
        return

    else:
        # if there are no inputs for this hash, its a block reward and we can't union
        if len(txs[txID][1]) == 0:
            raise Exception("outputUnion() passed a block reward")
        # otherwise, we union to the first input address
        # all the input addresses are already unioned, so we only need to use one
        else:
            union([txs[txID][1][0], addr])


inputTxs = [[]]  # index is txID, value is a list of its inputs' addresses
outputTxs = [[]]  # same as above but for outputs

# fill a dict with a key for each address
with open("bitcoinData/newInputs.csv", "r") as inputs:

    for line in inputs:

        txID, address = parseInput(line)
        txID = int(txID)
        if len(inputTxs) <= txID:
            resizeTxs(txID)
        if address not in inputTxs[txID]:
            inputTxs[txID].append(address)

print "inputTxs dict populated"

with open("bitcoinData/newOutputs.csv", "r") as outputs:  # the new heuristic uses outputs

    for line in outputs:

        data = parseOutput(line)
        txID, address = int(data[0]), data[5]
        if len(outputTxs) <= txID:
            resizeOutputTxs(txID)
        if address not in outputTxs[txID]:
            outputTxs[txID].append(address)

print "outputTxs dict populated"
    
txs = zip(itertools.count(), inputTxs, outputTxs)

print "previous dicts zipped into txs dict"

addresses = dict() # associates address with user

# populate addresses dict, making an index of value 0 for each address
for address in getAddresses():
    addresses[address] = 0

print "addresses dict populated"

# stores addresses that have already been used
usedAddresses = set()

for tx in txs:

    txID = tx[0]
    inputs = set(tx[1])
    outputs = set(tx[2])

    # if there are no inputs then it's a block reward, and can't be unioned
    if len(inputs) == 0:
        continue
    
    # if there is only one input and one output, no unions can be made
    elif len(inputs) < 2 and len(outputs) < 2:
        continue

    # if the tx gives change to an input, that is the suspected change address
    # we test this by unioning the sets and seeing if there are duplicates
    elif len(inputs.union(outputs)) < len(inputs) + len(outputs):
        continue

    # if there are multiple inputs but only one output, we can only union the inputs
    elif len(inputs) > 1 and len(outputs) < 2:
        union(inputs)

    # if there is exactly one input and multiple outputs, call outputUnion() only
    # this works because outputUnion() conditionally unions the lone output with the first input
    elif len(inputs) == 1 and len(outputs) > 1:
        outputUnion(outputs, txID)

    # if there are multiple inputs and multiple outputs, we union both
    elif len(inputs) > 1 and len(outputs) > 1:
        union(inputs)
        outputUnion(outputs, txID)

print "union completed"

usersDict = dict() # associates users' address sets with their roots

for key, value in addresses.iteritems():
    
    root = key
    while type(addresses[root]) != int:
        root = addresses[root]

    if not root in usersDict:
        usersDict[root] = set([key])

    else:
        usersDict[root].add(key)

print "usersDict populated"

# generate a list of addresses, each index being a user, from usersDict
users = []
with open("bitcoinData/heurusers.csv", "w") as userFile:

    for counter, (key, user) in enumerate(usersDict.items()):
        users.append(user)
        for address in user:
            userFile.write(address + "," + str(counter) + "\n")

print "heurusers.csv written"

# generate a CSV file associating userIDs with the number of addresses they contain
with open("bitcoinData/heurUsersCount.csv", "w") as usersCount:

    for counter, user in enumerate(users):
        usersCount.write(str(counter) + "," + str(len(user)) + "\n")

print "usersCount.csv written"
