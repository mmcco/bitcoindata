'''dataStructs.py: contains functions that generate data commonly needed in Bitcoin analysis scripts'''

from operator import itemgetter


def parseCSVLine(line, expectedLen = None):
    '''returns a CSV line parsed into its values; throws error if it is not of expected length
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
    '''returns a set of all addresses'''

    with open("bitcoinData/newOutputs.csv", "r") as outputs:
        addressSet = set()
        for line in outputs:
            data = parseCSVLine(line, 7)
            addressSet.add(data[5])

    return addressSet


def inputAddresses():
    '''returns a two-dimensional list - the index is the txID, the value is a list of the addresses associated with its inputs'''

    with open("bitcoinData/newInputs.csv", "r") as inputs:
        addresses = []
        for line in inputs:
            data = parseCSVLine(line, 5)
            txID, address = int(data[0]), data[3]
            while len(addresses) <= txID:
                addresses.append([])
            addresses[txID].append(address)

    return addresses


def txOwners():
    '''returns a list, the index being the txID of the owner of each transaction
    None is used for block rewards, which have no inputs
    '''

    txAddresses = inputAddresses()
    users = addressUsers()
    owners = []
    for counter, addresses in enumerate(txAddresses):
        if len(addresses) == 0:
            owners[counter] = None
        else:
            # we can just use the first address, as they all have the same owner
            owners[counter] = addressUsers[addresses[0]]
    
    return owners


def addressUsers():
    '''returns a dictionary in which the key is the address and the value is the userID'''

    userIDs = dict()
    with open("bitcoinData/heurusers.csv", "r") as usersFile:
        for line in usersFile:
            data = parseCSVLine(line, 2)
            userIDs[data[0]] = data[1]

    return userIDs


def users():
    '''returns a list whose index is the userID and whose values is a list of that user's addresses'''

    users = [[]]
    with open("bitcoin/heurusers.csv", "r") as usersFile:
        for line in usersFile:
            data = parseCSVLine(line, 2)
            address, userID = data[0], int(data[1])
            while len(users) <= userID:
                users.append([])
            users[userID].append(address)

    return users


def usersByTx():
    '''returns a list of tuples - the index is the txID, the tuples are (fromUser, [toUsers])
    fromUser is the user that owns the inputs
    toUsers are the users that own the outputs
    '''

    users = addressUsers()
    inputUsers = txOwners()
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
    '''returns a list of all tx's Unix timestamps; the index is the tx's txID'''

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
    '''returns a list of the txIDs of all block rewards'''

    rewardTxIDs = []
    with open("bitcoinData/txs.csv", "r") as txsFile:
        for line in txsFile:
            data = parseCSVLine(line, 7)
            if int(data[5]) == 0:
                rewardTxIDs.append(int(data[0]))

    return rewardTxIDs


def addressHistory():
    ''' Returns a dict associating every address with a list of (txID, outputIndex, value, spentInTxID) tuples representing its history.
    spentInTx is the txID of the tx in which the output was used as an input; it is None by default.
    Using txIDs instead of timestamps reduces ambiguity; use txTimestamps() to replace them if necessary.
    '''
    addresses = dict()
    with open("bitcoinData/newOutputs.csv", "r") as outputs:
        for line in outputs:
            data = parseCSVLine(line, 7)
            txID, outputIndex, value, address = int(data[0]), int(data[2]), int(data[3]), data[5]
            addresses.setdefault(address, []).append([txID, outputIndex, value, None])
    
    # temporary print, DELETE
    print "finished loading outputs, len(addresses):", len(addresses)

    with open("bitcoinData/newInputs.csv", "r") as inputs:
        for line in inputs:
            data = parseCSVLine(line, 7)
            inputTxID, address, outputTxID, outputIndex = int(data[0]), data[3], int(data[5]), int(data[6])
            # put input's txID with its corresponding output
            for counter, output in enumerate(addresses[address]):
                if output[0] == outputTxID and output[1] == outputIndex:
                    addresses[address][counter][3] = inputTxID
                    break
            else:  # triggers if outputTxID does not exist in addresses[address]
                raise Exception("input's corresponding output could not be found in list")
            
    # temporary print, DELETE
    print "finished loading inputs"

    map (sort(key=itemgetter(0)), addresses)

    return addresses


def userHistory():
    '''This function is the counterpart to addressHistory(), using userIDs as the key instead of addresses.
    Like addressHistory, the return value is a list of outputs owned by the given user.
    The outputs are in the form (txID, outputIndex, value, spentInTxID)
    '''

    addressHistories = addressHistory()
    users = addressUsers()
    userHistories = dict()

    for address, history in addressHistories.items():
        userHistories.setdefault(users[address], [])
        userHistories[users[address]] += history

    return userHistories
