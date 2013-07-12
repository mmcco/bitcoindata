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
    return (data[0], data[5])

# helper function for dynamic resize of two-dimensional array
def resizeTxs(count):
    for i in range(0, count):
        inputTxs.append(set())

# same as above but for another 2D array
def resizeOutputTxs(count):
    for i in range(0, count):
        outputTxs.append(set())

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

    # add addresses to list of used addresses
    map (usedAddresses.add, args)


# takes the addresses in a tx's outputs, conditionally unions them
def outputUnion(args, txID):
    if len(args) < 2:
        raise Exception("outputUnion was passed a set of length < 2")
    # generate a list of tuples associating each address with a boolean that describes whether it has been used yet
    boolTuples = [(addr, addr in usedAddresses) for addr in args]
    
    # if there isn't exactly one unused address in the outputs set, we're done
    # if there is exactly one, store it as address and union it with the inputs
    executeUnion = False
    for tup in boolTuples:
        # logic for first unused address encountered
        if tup[1] and not executeUnion:
            addr = tup[0]
            executeUnion = True
        # logic for second unused address encountered
        if tup[1] and executeUnion:
            executeUnion = False

    if not executeUnion:
        return

    else:
        # if there are no inputs for this hash, its a block reward and we can't union
        if len(inputTxs[txID] == 0):
            return
        # otherwise, we union to the first input address
        # all the input addresses are already unioned, so we only need to use one
        else:
            union([inputTxs[0], addr])

    # add args to list of used addresses
    map (usedAddresses.add, args)


inputTxs = [set()]  # index is txID, value is a list of its inputs' addresses
outputTxs = [[]]  # same as above but for outputs
inputs = open("newInputs.csv", "r")

# fill a dict with a key for each address
for line in inputs:

    data = parseInput(line)
    txID = int(data[0])
    if len(inputTxs) <= txID:
        resizeTxs(txID)
    inputTxs[txID].add(data[3])

inputs.close()

outputs = open("newOutputs.csv", "r")  # the heuristic uses outputs

for line in outputs:
    txID, address = parseOutput(line)
    txID = int(txID)
    if len(outputTxs) <= txID:
        resizeOutputTxs(txID)
    outputTxs[txID].add(address)

outputs.close()
    
addresses = dict() # associates address with user

# populate addresses dict, making an index of value 0 for each address
for tx in inputTxs:
    for addr in tx:
        addresses[addr] = 0

if len(inputTxs) != len(outputTxs):
    raise Exception("inputTxs and outputTxs are not of the same length")
txs = zip(itertools.count(), inputTxs, outputTxs)

# stores addresses that have already been used
usedAddresses = set()

for tx in txs:

    txID = tx[0]
    inputs = tx[1]
    outputs = tx[2]

    # if there are no inputs then it's a block reward, and can't be unioned
    if len(inputs) == 0:
        continue
    
    # if there is only one input and one output, no unions can be made
    elif len(inputs) < 2 and len(outputs) < 2:
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


usersDict = dict() # associates users' address sets with their roots

for key, value in addresses.iteritems():
    
    root = key
    while type(addresses[root]) != int:
        root = addresses[root]

    if not root in usersDict:
        usersDict[root] = set([key])

    else:
        usersDict[root].add(key)

# generate a list of addresses, each index being a user, from usersDict
users = []

for key, value in usersDict.iteritems():
    users.append(value)

userFile = open("heurusers.csv", "w")

for counter, user in enumerate(users):
    for addr in user:
        userFile.write(addr + "," + str(counter) + "\n")

userFile.close()
