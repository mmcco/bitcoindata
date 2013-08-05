'''dataStructs.py: contains functions that generate data structures commonly needed in Bitcoin analysis scripts'''

from operator import itemgetter
import os.path
from array import array


def parseCSVLine(line, expectedLen=None):
    '''Returns a CSV line parsed into its values; throws exception if it is not of expected length.
    It will only parse as many items as expected for efficiency's sake.
    Therefore, lines longer than expected will not be caught.
    '''

    if expectedLen is None:
        return line.split(",")

    else:
        data = line.split(",", expectedLen - 1)
        if len(data) != expectedLen:
            raise RuntimeError("line passed to parseCSVLine() was not of expected length")
        return data


def newlineTrim(string):
    '''Removes a newline character from the end of a string if it is present'''

    if len(string) == 0 or string[-1] != '\n':
        return string
    else:
        return string[:-1]


def txHashes():
    '''Returns a list in which the index is the txID and the value is the txHash.'''

    # allowing transactions.csv to be used allows us to use this in parser.py (before txs.cvs exists)
    hashes = []

    with open("data/txs.csv", "r") as txsFile:
        for line in txsFile:
            data = parseCSVLine(line, 3)
            txID, txHash = int(data[0]), data[1]
            if len(hashes) != txID:
                raise RuntimeError("mismatch between txID and len(hashes)")
            hashes.append(txHash)

    return hashes


def blockTimes():
    '''Returns a list in which the index is the blockID and the value is the Unix timestamp.'''

    blocktimes = []

    with open("data/newBlocks.csv", "r") as blocksFile:
        for line in blocksFile:
            data = parseCSVLine(line, 5)
            blockID, timestamp = int(data[0]), int(data[3])
            if blockID != len(blocktimes):
                raise RuntimeError("mismatch between blockID and len(blocktimes)")
            blocktimes.append(timestamp)

    return blocktimes


def spentOutputsDict():
    '''Returns a dict in which the key is (txHash + "," + outputIndex) and the value is a tuple: (outputTxID, receivingAddress, value).
    For efficiency's sake, only spent outputs are represented.
    '''

    outputs = dict()
    hashes = txHashes()

    # initialize the outputs dict with all spent outputs
    with open("inputs.csv", "r") as inputsFile:
        inputsFile.readline()
        for line in inputsFile:
            data = parseCSVLine(line, 5)
            outputTxHash, outputIndex = data[3], newlineTrim(data[4])
            outputs[outputTxHash + "," + outputIndex] = []

    with open("outputs.csv", "r") as outputsFile:
        outputsFile.readline()  # skip first line, which is just column names
        for line in outputsFile:
            data = parseCSVLine(line, 6)
            txID, index, value, address = data[0], data[1], data[2], data[4]
            if int(txID) >= len(hashes):
                raise RuntimeError("output txID " + txID + " is outside the range available in hashes  -==-  maximum available txID is " + str(len(hashes)))
            txHash = hashes[int(txID)]
            dictIndex = txHash + "," + index
            # if it isn't in the dict, it isn't spent; continue
            if dictIndex not in outputs:
                continue
            # allow for multiple values in each outputs location because txHashes are not unique identifiers of txs
            # in accordance with the Bitcoin protocol, each outputs location is a queue
            outputs[dictIndex].append((txID, address, value))

    return outputs


def outputsTxIDs():
    '''Returns a list in chronological order of output's corresponding txIDs to be zipped into a list of outputs.'''

    txIDs = []

    with open("data/txs.csv", "r") as txsFile:
        for line in txsFile:
            data = parseCSVLine(line, 8)
            txID, numOutputs = int(data[0]), int(data[6])
            for x in xrange(numOutputs):
                txIDs.append(txID)

    return txIDs


def outputsToInputs():
    '''Returns a dict in which the is (outputTxID, outputIndex) and the value is a tuple: (inputTxID, inputIndex).
    This data structure is used to relate spent outputs to their inputs, so unspent outputs are not represented.
    Because this is used for file-writing, the values are returned as strings rather than ints (this saves a lot of time).
    '''

    with open("data/newInputs.csv", "r") as newInputs:

        outputs = dict()

        for line in newInputs:
            data = parseCSVLine(line, 8)
            inputTxID, inputIndex, outputTxID, outputIndex = data[0], data[2], data[6], newlineTrim(data[7])

            dictIndex = (outputTxID, outputIndex)
            if dictIndex in outputs:
                raise RuntimeError("output already assigned input")
            outputs[dictIndex] = (inputTxID, inputIndex)

    return outputs


def getAddresses():
    '''Returns a set of all addresses.'''

    with open("data/newOutputs.csv", "r") as outputs:
        addressSet = set()
        for line in outputs:
            data = parseCSVLine(line, 7)
            addressSet.add(data[5])

    return addressSet


def inputAddresses():
    '''Returns a two-dimensional list - the index is the txID, the value is a list of the addresses associated with its inputs.
    This function includes each address only once.
    '''

    with open("data/newInputs.csv", "r") as inputs:
        addresses = []
        for line in inputs:
            data = parseCSVLine(line, 5)
            txID, address = int(data[0]), data[3]
            while len(addresses) <= txID:
                addresses.append([])
            if address not in addresses[txID]:
                addresses[txID].append(address)

    return addresses


def outputAddresses():
    '''Returns a two-dimensional list - the index is the txID, the value is a list of the addresses associated with its outputs.
    This function includes each address only once.
    '''

    with open("data/newOutputs.csv", "r") as outputs:
        addresses = []
        for line in outputs:
            data = parseCSVLine(line, 7)
            txID, address = int(data[0]), data[5]
            while len(addresses) <= txID:
                addresses.append([])
            if address not in addresses[txID]:
                addresses[txID].append(address)

    return addresses


def txOwners(useHeur=True):
    '''Returns a list, the index being the txID of the owner of each transaction.
    None is used for block rewards, which have no inputs
    The useHeur boolean determines whether to use the heuristic or traditional users.
    It is True by default.
    '''

    txAddresses = inputAddresses()
    users = addressUsers(useHeur)
    owners = []
    for counter, addresses in enumerate(txAddresses):
        if len(addresses) == 0:
            owners[counter] = None
        else:
            # we can just use the first address, as they all have the same owner
            owners[counter] = addressUsers[addresses[0]]

    return owners


def addressUsers(useHeur=True):
    '''Returns a dictionary in which the key is the address and the value is the userID.
    The useHeur boolean determines whether to use the heuristic or traditional users.
    It is True by default.
    '''

    userIDs = dict()
    filename = "data/heurusers.csv" if useHeur else "data/users.csv"

    with open(filename, "r") as usersFile:
        for line in usersFile:
            data = parseCSVLine(line, 2)
            userIDs[data[0]] = data[1]

    return userIDs


def users(useHeur=True):
    '''Returns a list whose index is the userID and whose values is a list of that user's addresses.
    The useHeur boolean determines whether to use the heuristic or traditional users.
    It is True by default.
    '''

    users = [[]]
    filename = "data/heurusers.csv" if useHeur else "data/users.csv"

    with open("bitcoin/heurusers.csv", "r") as usersFile:
        for line in usersFile:
            data = parseCSVLine(line, 2)
            address, userID = data[0], int(data[1])
            while len(users) <= userID:
                users.append([])
            users[userID].append(address)

    return users


def usersByTx(useHeur=True):
    '''Returns a list of tuples - the index is the txID, the tuples are (fromUser, [toUsers]).
    fromUser is the user that owns the inputs.
    toUsers are the users that own the outputs.
    The useHeur boolean determines whether to use the heuristic or traditional users.
    It is True by default.
    '''

    users = addressUsers(useHeur)
    inputUsers = txOwners(useHeur)
    # an empty list for every tx
    outputUsers = [[] for x in xrange(len(inputUsers))]

    with open("data/newOutputs.csv", "r") as outputs:
        for line in outputs:
            data = parseCSVLine(line, 7)
            txID, address = int(data[0]), data[5]
            outputUsers[txID].append(users[data[5]])

    if len(inputUsers) != len(outputUsers):
        raise RuntimeError("mismatch in length between inputUsers and outputUsers")

    return zip(inputUsers, outputUsers)


def txTimestamps():
    '''Returns a list of all tx's Unix timestamps; the index is the tx's txID.'''

    txsByTime = []

    with open("data/txs.csv", "r") as txsFile:
        for line in txsFile:
            data = parseCSVLine(line, 6)
            txID, timestamp = int(data[0]), int(data[4])
            if len(txsByTime) != txID:
                raise RuntimeError("mismatch between txID and length of txsByTime")
            txsByTime.append(timestamp)

    return txsByTime


def blockRewardIDs():
    '''Returns a list of the txIDs of all block rewards.'''

    rewardTxIDs = []
    with open("data/txs.csv", "r") as txsFile:
        for line in txsFile:
            data = parseCSVLine(line, 7)
            if int(data[5]) == 0:
                rewardTxIDs.append(int(data[0]))

    return rewardTxIDs


def priceHistory():
    '''Returns a list of tuples: (unixTimestamp, priceUSD) that includes every past Mt. Gox transaction'''

    trades = []

    with open("data/trades.csv", "r") as tradesFile:
        for line in tradesFile:
            price, quantity, timestamp = parseCSVLine(line, 3)
            trades.append((timestamp, price))

    trades.sort(key=lambda x: x[0])
    return trades


def addressHistory():
    ''' Returns a dict associating every address with a set of (txID, outputIndex, value, spentInTxID) tuples representing its history.
    spentInTx is the txID of the tx in which the output was used as an input; it is None by default.
    Using txIDs instead of timestamps reduces ambiguity; use txTimestamps() to replace them if necessary.
    '''

    addresses = dict()
    with open("data/newOutputs.csv", "r") as outputs:
        for line in outputs:
            data = parseCSVLine(line, 8)
            txID, outputIndex, value, address = int(data[0]), int(data[2]), int(data[3]), data[5]
            # inputTxID is None if the output is unspent
            inputTxID = int(data[6]) if data[6] else None
            addresses.setdefault(address, []).append((txID, outputIndex, value, inputTxID))

            if len(addresses[address]) - 1 != outputIndex:
                raise RuntimeError("Error: mismatch with output index")

    return addresses


def userHistory(useHeur=True):
    '''This function is the counterpart to addressHistory(), using userIDs as the key instead of addresses.
    Like addressHistory, the return value is a list of outputs owned by the given user.
    The outputs are in the form (txID, outputIndex, value, spentInTxID)
    '''

    addressHistories = addressHistory()
    users = addressUsers(useHeur)
    userHistories = dict()

    for address, history in addressHistories.iteritems():
        user = users[address]
        userHistories.setdefault(user, [])
        userHistories[user] += history

    [userHistory.sort(key=lambda x: (x[0], x[1])) for userHistory in userHistories]
    return userHistories


def outputsList():
    '''Returns a list of a tuple (txID, outputIndex, value, spentInTxID) for each output.'''

    outputs = [output for address in addressHistory().values() for output in address]
    outputs.sort(key=lambda x: x[0])
    return outputs
