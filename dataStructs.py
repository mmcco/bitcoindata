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
    '''returns a list of all tx's timestamps; the index is the tx's txID'''
    # make a list associating txIDs with their timestamps
    txsByTime = []
    with open("bitcoinData/txs.csv", "r") as txsFile:
        for line in txsFile:
            data = line.split(",", 5)
            if len(txsByTime) != int(data[0]):
                raise Exception("mismatch between txID and length of txsByTime")
            txsByTime.append(int(data[4]))
    return txsByTime
