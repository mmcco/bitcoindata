'''dataStructs.py: contains functions that generate data structures commonly needed in Bitcoin analysis scripts'''

from operator import itemgetter


def parseCSVLine(line, expectedLen = None):
    '''Returns a CSV line parsed into its values; throws exception if it is not of expected length.
    It will only parse as many items as expected for efficiency's sake.
    Therefore, lines longer than expected will not be caught.
    '''
    
    if expectedLen is None:
        return line.split(",")

    else:
        data = line.split(",", expectedLen - 1)
        if len(data) != expectedLen:
            raise Exception("line passed to parseCSVLine() was not of expected length")
        return data


def getAddresses():
    '''Returns a set of all addresses.'''

    with open("bitcoinData/newOutputs.csv", "r") as outputs:
        addressSet = set()
        for line in outputs:
            data = parseCSVLine(line, 7)
            addressSet.add(data[5])

    return addressSet


def inputAddresses():
    '''Returns a two-dimensional list - the index is the txID, the value is a list of the addresses associated with its inputs.
    This function includes each address only once.
    '''

    with open("bitcoinData/newInputs.csv", "r") as inputs:
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

    with open("bitcoinData/newOutputs.csv", "r") as outputs:
        addresses = []
        for line in outputs:
            data = parseCSVLine(line, 7)
            txID, address = int(data[0]), data[5]
            while len(addresses) <= txID:
                addresses.append([])
            if address not in addresses[txID]:
                addresses[txID].append(address)

    return addresses

def txOwners(useHeur = True):
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


def addressUsers(useHeur = True):
    '''Returns a dictionary in which the key is the address and the value is the userID.
    The useHeur boolean determines whether to use the heuristic or traditional users.
    It is True by default.
    '''

    userIDs = dict()
    filename = "bitcoinData/heurusers.csv" if useHeur else "bitcoinData/users.csv"

    with open(filename, "r") as usersFile:
        for line in usersFile:
            data = parseCSVLine(line, 2)
            userIDs[data[0]] = data[1]

    return userIDs


def users(useHeur = True):
    '''Returns a list whose index is the userID and whose values is a list of that user's addresses.
    The useHeur boolean determines whether to use the heuristic or traditional users.
    It is True by default.
    '''

    users = [[]]
    filename = "bitcoinData/heurusers.csv" if useHeur else "bitcoinData/users.csv"

    with open("bitcoin/heurusers.csv", "r") as usersFile:
        for line in usersFile:
            data = parseCSVLine(line, 2)
            address, userID = data[0], int(data[1])
            while len(users) <= userID:
                users.append([])
            users[userID].append(address)

    return users


def usersByTx(useHeur = True):
    '''Returns a list of tuples - the index is the txID, the tuples are (fromUser, [toUsers]).
    fromUser is the user that owns the inputs.
    toUsers are the users that own the outputs.
    The useHeur boolean determines whether to use the heuristic or traditional users.
    It is True by default.
    '''

    users = addressUsers(useHeur)
    inputUsers = txOwners(useHeur)
    outputUsers = [ [] for x in xrange(len(inputUsers)) ]

    with open("bitcoinData/newOutputs.csv", "r") as outputs:
        for line in outputs:
            data = parseCSVLine(line, 7)
            txID, address = int(data[0]), data[5]
            outputUsers[txID].append(users[data[5]])

    if len(inputUsers) != len(outputUsers):
        raise Exception("mismatch in length between inputUsers and outputUsers")

    return zip(inputUsers, outputUsers)
    

def txTimestamps():
    '''Returns a list of all tx's Unix timestamps; the index is the tx's txID.'''

    # make a list associating txIDs with their timestamps
    txsByTime = []
    with open("bitcoinData/txs.csv", "r") as txsFile:
        for line in txsFile:
            data = parseCSVLine(line, 6)
            if len(txsByTime) != int(data[0]):
                raise Exception("mismatch between txID and length of txsByTime")
            txsByTime.append(int(data[4]))

    return txsByTime


def blockRewardIDs():
    '''Returns a list of the txIDs of all block rewards.'''

    rewardTxIDs = []
    with open("bitcoinData/txs.csv", "r") as txsFile:
        for line in txsFile:
            data = parseCSVLine(line, 7)
            if int(data[5]) == 0:
                rewardTxIDs.append(int(data[0]))

    return rewardTxIDs


def priceHistory():
    '''Returns a list of tuples: (unixTimestamp, priceUSD) that includes every past Mt. Gox transaction'''

    trades = []

    with open("bitcoinData/trades.csv", "r") as tradesFile:
        for line in tradesFile:
            price, quantity, timestamp = parseCSVLine(line, 3)
            trades.append((timestamp, price))

    trades.sort(key = lambda x: x[0])
    return trades


def addressHistory():
    ''' Returns a dict associating every address with a set of (txID, outputIndex, value, spentInTxID) tuples representing its history.
    spentInTx is the txID of the tx in which the output was used as an input; it is None by default.
    Using txIDs instead of timestamps reduces ambiguity; use txTimestamps() to replace them if necessary.
    '''

    addresses = dict()
    with open("bitcoinData/newOutputs.csv", "r") as outputs:
        for line in outputs:
            data = parseCSVLine(line, 8)
            txID, outputIndex, value, address = int(data[0]), int(data[2]), int(data[3]), data[5]
            # inputTxID is None if the output is unspent
            inputTxID = int(data[6]) if data[6] else None
            addresses.setdefault(address, set()).add((txID, outputIndex, value, None))
    
    # temporary print, DELETE
    print "finished loading outputs, len(addresses):", len(addresses)

    [address.sort(key = lambda x: x[0]) for address in addresses]
    return addresses


def userHistory(useHeur = True):
    '''This function is the counterpart to addressHistory(), using userIDs as the key instead of addresses.
    Like addressHistory, the return value is a list of outputs owned by the given user.
    The outputs are in the form (txID, outputIndex, value, spentInTxID)
    '''

    addressHistories = addressHistory()
    users = addressUsers(useHeur)
    userHistories = dict()

    for address, history in addressHistories.items():
        userHistories.setdefault(users[address], [])
        userHistories[users[address]] += history

    [userHistory.sort(key = lambda x: x[0]) for userHistory in userHistories]
    return userHistories
    

def outputsList():
    '''Returns a list of a tuple (txID, outputIndex, value, spentInTxID) for each output.'''

    outputs = [output for address in addressHistory().values() for output in address]
    outputs.sort(key = lambda x: x[0])
    return outputs
