'''dataStructs.py: contains functions that generate data commonly needed in Bitcoin analysis scripts'''


def getAddresses():
    '''returns a set of all addresses'''
    with open("bitcoinData/newOutputs.csv", "r") as outputs:
        addressSet = set()
        for line in outputs:
            data = line.split(",", 6)
            if len(data) < 7:
                raise Exception("bad line in newOutputs.csv")
            addressSet.add(data[5])
    return addressSet


def addressUsers():
    '''returns a dictionary in which the key is the address and the value is the userID'''
    userIDs = dict()
    with open("bitcoinData/heurusers.csv", "r") as usersFile:
        for line in usersFile:
            data = line.split(",")
            if len(data) != 2:
                raise Exception("bad line in heurusers.csv")
            userIDs[data[0]] = data[1]
    return userIDs


def txTimestamps():
    '''returns a list of all tx's Unix timestamps; the index is the tx's txID'''
    # make a list associating txIDs with their timestamps
    txsByTime = []
    with open("bitcoinData/txs.csv", "r") as txsFile:
        for line in txsFile:
            data = line.split(",", 5)
            if len(txsByTime) != int(data[0]):
                raise Exception("mismatch between txID and length of txsByTime")
            txsByTime.append(int(data[4]))
    return txsByTime


def blockRewardIDs():
    '''returns a list of the txIDs of all block rewards'''
    rewardTxIDs = []
    with open("bitcoinData/txs.csv", "r") as txsFile:
        for line in txsFile:
            data = line.split(",", 6)
            if len(data) != 7:
                raise Exception("bad line in txs.csv")
            if int(data[5]) == 0:
                rewardTxIDs.append(int(data[0]))
    return rewardTxIDs


#def inputAddrByTx():
#    '''returns a two-dimensional list of the addresses associated with each tx's inputs; the index is the tx's txID'''
#    inputTxs = []
#    with open("bitcoinData/newInputs.csv", "r") as inputs:
#        for line in inputs:
            
# this does not currently fit the spec
def addressHistory(which="both"):
    ''' returns a dict associating every address with a list of (timestamp, value, timeSpent) tuples representing its history
    timeSpent is a Unix timestamp, and is None if the output has not yet been used as an input
    '''
    addresses = dict()
    timestamps = txTimestamps()
    with open("bitcoinData/newOutputs.csv", "r") as outputs:
        for line in outputs:
            data = line.split(",", 6)
            txID, value, address = int(data[0]), int(data[3]), data[5]
            if address not in addresses:
                addresses[address] = [(timestamps[txID], value)]
            else:
                addresses[address].append((timestamps[txID], value))
    return addresses
