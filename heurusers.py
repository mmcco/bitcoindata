# This script merges addresses into users, which are entities suspected of owning multiple addresses
# It uses the traditional heuristic of assuming the addresses associated with each transaction's inputs are owned by the same user
# It also uses an additional heuristic which has not yet been published
# Specifically, if a transaction has multiple outputs, exactly one of which goes to an unused address, that address is unioned with the input addresses

# union() must be called before outputUnion()

# lists with "if x not in y" checks are used instead of sets where the CPU/memory trade-off makes sense
# this is because sets are represented as dictionaries in memory and therefore take up a lot of space

import itertools
from dataStructs import getAddresses, inputAddresses, outputAddresses
from itertools import chain


# returns the given addresses's root
# does path compression, and therefore changes state (beware)
def getRoot(addr):

    if type(addresses[addr]) == int:
        return addr

    else:
        root = getRoot(addresses[addr])
        addresses[addr] = root
        return root


# executes union-find on a tx's inputs
def union(args):

    if len(args) < 2:
        raise Exception("union() passed a list of length < 2")

    for addr in args:
        if addr not in addresses:
            raise Exception(addr, "is passed to union() but does not exist in the addresses dict")

    roots = set(map(getRoot, args))

    # if the roots are already equal, we're done
    if len(roots) == 1:
        return

    rootRanks = [(root, addresses[root]) for root in roots]
    parent = max(rootRanks, key=(lambda x: x[1]))
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
    map(usedAddresses.add, args)

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


# txs is a two-dimensional array; each item is (txID, [unique input addresses], [unique output addresses])
txs = zip(itertools.count(), inputAddresses(), outputAddresses())

print "previous dicts zipped into txs dict"

addresses = dict()  # associates address with user

# populate addresses dict, making an index of value 0 for each address
for address in getAddresses():
    addresses[address] = 0

print "addresses dict populated"

usedAddresses = set()

for tx in txs:

    # inputs and outputs are cast to sets to remove duplicates
    txID, inputs, outputs = tx[0], set(tx[1]), set(tx[2])

    # if there are no inputs then it's a block reward, and can't be unioned
    if len(inputs) == 0:
        continue

    # if there is only one input and one output, no unions can be made
    elif len(inputs) < 2 and len(outputs) < 2:
        continue

    # if the tx outputs to an address used in an input, that is the suspected change address
    # we test for duplicates by unioning the sets
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

# manual memory clearing
del txs

usersDict = dict()  # associates users' address sets with their roots

for key, value in addresses.iteritems():

    root = getRoot(key)
    usersDict.setdefault(root, set()).add(key)

print "dictionary of users indexed by root populated"

# write each user to a CSV file in the order they were first used
with open("data/heurusers.csv", "w") as userFile, open("data/heurUsersCount.csv", "w") as countFile:

    userID = 0

    # executes for each address, in the order they were created
    for address in chain(*outputAddresses()):

        if address in addresses:

            root = getRoot(address)
            user = usersDict[root]
            countFile.write(str(userID) + ',' + str(len(user)) + '\n')

            for addr in user:
                userFile.write(addr + ',' + str(userID) + '\n')
                # so that we only write each once
                del addresses[addr]

            userID += 1

print "heurusers.csv and heurUsersCount.csv written"
