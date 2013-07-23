# this script is an attempted all-in-one processor of the blockparser CSV-generator's output
# it makes changes that are necessary or convenient, preparing the data for parsing by a SQL database and for a union-find algorithm to generate a list of entities
#
# the input files are:  blocks.csv
#                       transactions.csv
#                       inputs.csv
#                       outputs.csv
#
# the output files are: newBlocks.csv
#                       txs.csv
#                       newInputs.csv
#                       newOutputs.csv
#                       users.csv
#                       usersCount.csv
#                       heurUsers.csv
#                       heurUsersCount.csv
#
# all output files are stored in the data directory
#
# tx is used as an abbreviation for transaction

from dateutil.parser import parse
import calendar
import datetime

# we begin by converting each block's timestamp from ISO 8601 to a Unix timestamp
blocks = open("blocks.csv", "r")
blocks.readline()  # skip first line, which is just column names
newBlocks = open("bitcoinData/newBlocks.csv", "w")
# !!! This data type assumes that you're parsing from the genesis block; switch to dict if writing an automated updater !!!
blockTimes = []  # location is blockID, value is Unix timestamp

for line in blocks:
    data = line.split(",", 4)
    if len(data) < 5:
        raise Exception("bad line in blocks.csv")
    if int(data[0]) != len(blockTimes):
        raise Exception("mismatch between blockID (" + data[0] + ") and blockTimes list length " + str(len(blockTimes)) + ")")

    timestamp = calendar.timegm(parse(data[3][1:-1]).utctimetuple())  # convert ISO 8601 timestamp to Unix timestamp
    blockTimes.append(str(timestamp))
    data[3] = str(timestamp)
    newBlocks.write(",".join(data))

blocks.close()
newBlocks.close()


# this section selects the Unix timestamp of each tx's corresponding block and inserts it into the tx
txs = open("transactions.csv", "r")
txs.readline()  # skip first line, which is just column names
newTxs = open("bitcoinData/txs.csv", "w")
# !!! This data type assumes that you're parsing from the genesis block; switch to dict if writing an automated updater !!!
txHashes = []  # location is txID, value is txHash

for line in txs:
    data = line.split(",", 4)
    if len(data) != 5:
        raise Exception("bad line in transactions.csv")
    if len(txHashes) != int(data[0]):
        raise Exception("txIDs and txHashes do not match - len(txHashes) is " + str(len(txHashes)) + " while the txID is " + data[0])

    txHashes.append(data[1])
    data.insert(4, blockTimes[ int(data[3]) ])
    newTxs.write(",".join(data))

txs.close()
newTxs.close()


# parses a CSV line from inputs.csv or newInputs.csv
def parseInput(inputLine):
    data = inputLine.split(",")
    # allow data to be of length 5 or 7 because this function is used to parse both inputs.csv and newInputs.csv
    if len(data) != 5 and len(data) != 7:
        raise Exception("bad line in inputs - cannot parse  -==-  " + inputLine)
    return data

# parses a CSV line from outputs.csv
def parseOutput(outputLine):
    data = outputLine.split(",", 5)
    if len(data) != 6 and len(data) != 7:
        raise Exception("bad line in outputs.csv - cannot parse  -==-  " + outputLine)
    # drop the end of the line, as it's just trailing commas
    return data[:-1]

def newlineTrim(string):
    if len(string) == 0 or string[-1] != '\n':
        return string
    else:
        return string[:-1]


# we will first get the addresses from the outputs and insert them into the inputs
# we will also insert the txHash into the inputs (which initially only has the txID)
# finally, we will also replace the outputTxHash (which is not a unique identifier of a tx) with an outputTxID (which is a unique identifier of a tx)
inputs = open("inputs.csv", "r")
inputs.readline() # skip first line, which is just column names
outputs = open("outputs.csv", "r")
outputs.readline() # skip first line, which is just column names
newInputs = open("bitcoinData/newInputs.csv", "w")
outputsDict = dict()  # key is output's txHash + "," +  output's index, value is the tuple (output's txID, receiving address) for each output with this txHash and index

for line in outputs:
    data = parseOutput(line)
    txID, index, address = data[0], data[1], data[4]
    if int(txID) >= len(txHashes):
        raise Exception("output txID " + txID + " is outside the range available in txHashes  -==-  maximum available txID is " + str(len(txHashes)))
    txHash = txHashes[int(txID)]
    dictIndex = txHash + "," + index
    # allow for multiple values in each outputsDict location because txHashes are not unique identifiers of txs
    # in accordance with the Bitcoin protocol, each outputsDict location is a queue
    if dictIndex not in outputsDict:
        outputsDict[dictIndex] = [(txID, address)]
    else:
        outputsDict[dictIndex].append( (txID, address) )

for line in inputs:
    data = parseInput(line)
    txID, index, outputTxHash, outputTxIndex = data[0], data[1], data[3], data[4]
    outputsDictKey = outputTxHash + "," + newlineTrim(outputTxIndex)  # used as the index for outputsDict
    if outputsDictKey not in outputsDict:
        raise Exception("input index " + index + " from transaction ID " + txID + " calls an output that does not exist in outputsDict  -==-  attempted index: " + outputTxHash + "," + outputTxIndex) 
    if len(outputsDict[outputsDictKey]) == 0:
        raise Exception("the output for input index " + index + "from transaction ID " + txID + "has already been used")
    outputTxID, address = outputsDict[outputsDictKey].pop(0) # the oldest output is the one that has to be used first, according to the protocol
    txHash = txHashes[int(txID)]
    data[3] = outputTxID  # replacing the outputTxHash with an outputTxID
    data.insert(1, txHash)
    data.insert(3, address)
    newInputs.write(",".join(data))

inputs.close()
outputs.close()
newInputs.close()


# now we're going to go through the inputs and outputs a second time, inserting each input's txID and index into its corresponding outputs
newInputs = open("bitcoinData/newInputs.csv", "r")
outputs = open("outputs.csv", "r")
outputs.readline() # skip first line, which is just column names
newOutputs = open("bitcoinData/newOutputs.csv", "w")
inputsDict = dict()  # key is output txID + "," + output index, value is input's txID + "," + input index

for line in newInputs:
    data = parseInput(line)
    txID, index, outputTxHash, outputTxIndex = data[0], data[2], data[5], data[6]
    inputsDict[ outputTxHash + "," + newlineTrim(outputTxIndex) ] = txID + "," + index

for line in outputs:
    data = parseOutput(line)
    txID, index = data[0], data[1]
    # if there's a corresponding input, this output has been spent
    if txID + "," + index in inputsDict:
        # insert the input values into inputTxID and inputIndex
        inputTxID, inputIndex = inputsDict[ txID + "," + index ].split(",")
    # otherwise the output hasn't been spent yet...
    else:
        # ...so use empty values for the corresponding input
        inputTxID = ""
        inputIndex = ""
    txHash = txHashes[ int(txID) ]
    data.insert(1, txHash)
    data.append(inputTxID)
    data.append(inputIndex)
    newOutputs.write(",".join(data) + '\n')

newInputs.close()
outputs.close()
newOutputs.close()


# This script generates a CSV file associating Bitcoin addresses based on the entity that is suspected to own them
# It uses the classic heuristic of assuming all addresses owning inputs to a transaction are owned by the same entity
# This is carried out using the union-find algorithm

# note that sets are used heavily - they're somewhat slower than lists but are more bug-resistant
# if you're looking to make performance improvements, convert sets to lists where possible

def resizeTxs(count):
    for i in range(0, count):
        txs.append(set())

# returns the given addresses's root and rank in a tuple
def getRoot(addr):
    if type(addresses[addr]) == int:
        return addr
    else:
        # three-step technique used for path compression
        root = getRoot(addresses[addr])
        addresses[addr] = root
        return root


txs = [set()]  # index is txID, value is a list of its inputs' addresses
inputs = open("bitcoinData/newInputs.csv", "r")

# fill a dict with a key for each address
for line in inputs:

    data = parseInput(line)
    txID, address = int(data[0]), data[3]
    if len(txs) <= txID:
        resizeTxs(txID)
    txs[txID].add(address)

inputs.close()
    
print "list of addresses associated by transaction filled"

addresses = dict() # associates address with user

# populate addresses dict, making an index of value 0 for each address
for address in getAddresses():
    addresses[address] = 0

print "dictionary of addresses for union-find filled"

for tx in txs:
    if len(tx) > 1:
        union(tx)

print "union-find completed"

usersDict = dict() # associates users' address sets with their roots

for key, value in addresses.iteritems():
    
    root = key
    while type(addresses[root]) != int:
        root = addresses[root]

    if not root in usersDict:
        usersDict[root] = set([key])

    else:
        usersDict[root].add(key)

print "dictionary of users indexed by root populated"

# write each user to a CSV file
userFile = open("bitcoinData/users.csv", "w")
countFile = open("bitcoinData/usersCount.csv", "w")
users = []

for counter, (key, user) in enumerate(usersDict.iteritems()):
    if len(user) == 0:
        raise Exception("trying to write a user with no addresses")
    countFile.write(str(counter) + "," + str(len(user)) + '\n')
    for address in user:
        userFile.write(address + "," + str(counter) + "\n")

userFile.close()
countFile.close()


# This script merges addresses into users, which are entities suspected of owning multiple addresses
# It uses the traditional heuristic of assuming the addresses associated with each transaction's inputs are owned by the same user
# It also uses an additional heuristic which has not yet been published
# Specifically, if a transaction has multiple outputs, exactly one of which goes to an unused address, that address is unioned with the input addresses

# union() must be called before outputUnion()

# lists with "if x not in y" checks are used instead of sets where the CPU/memory trade-off makes sense
# this is because sets are represented as dictionaries in memory and therefore take up a lot of space

import itertools

# same as above but for another 2D array
def resizeOutputTxs(count):
    for i in range(0, count):
        outputTxs.append([])

# returns a list of all addresses, including ones that have never spent
def getAddresses():
    tempOutputs = open("bitcoinData/newOutputs.csv", "r")
    addressSet = set()
    for line in tempOutputs:
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
inputs = open("bitcoinData/newInputs.csv", "r")

# fill a dict with a key for each address
for line in inputs:

    data = parseInput(line)
    txID = data[0], data[3]
    txID = int(txID)
    if len(inputTxs) <= txID:
        resizeTxs(txID)
    if address not in inputTxs[txID]:
        inputTxs[txID].append(address)

inputs.close()

print "inputTxs dict populated"

outputs = open("bitcoinData/newOutputs.csv", "r")  # the new heuristic uses outputs

for line in outputs:

    data = parseOutput(line)
    txID, address = data[0], data[5]
    txID = int(txID)
    if len(outputTxs) <= txID:
        resizeOutputTxs(txID)
    if address not in outputTxs[txID]:
        outputTxs[txID].append(address)

outputs.close()

print "outputTxs dict populated"
    
#if len(inputTxs) != len(outputTxs):
#    raise Exception("inputTxs and outputTxs are not of the same length")
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
userFile = open("bitcoinData/heurusers.csv", "w")

for counter, (key, user) in enumerate(usersDict.items()):
    users.append(user)
    for address in user:
        userFile.write(address + "," + str(counter) + "\n")

userFile.close()

# generate a CSV file associating userIDs with the number of addresses they contain
userCount = open("bitcoinData/heurUsersCount.csv", "w")

for counter, user in enumerate(users):
    userCount.write(str(counter) + "," + str(len(user)) + "\n")

userCount.close()
