'''dataStructs.py: contains functions that generate data commonly needed in Bitcoin analysis scripts'''

from operator import itemgetter

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


def inputAddresses():
    '''returns a two-dimensional list - the index is the txID, the value is a list of the addresses associated with its inputs'''

    with open("bitcoinData/newInputs.csv", "r") as inputs:
        addresses = []
        for line in inputs:
            data = line.split(",", 4)
            if len(data) != 5:
                raise Exception("bad line in newInputs.csv")
            txID, address = int(data[0]), data[3]
            while len(addresses) <= txID:
                addresses.append([])
            addresses[txID].append(address)

    return addresses


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


def addressHistory():
    ''' Returns a dict associating every address with a list of (txID, value, spentInTx) tuples representing its history.
    spentInTx is the txID of the tx in which the output was used as an input; it is None by default.
    Using txIDs instead of timestamps reduces ambiguity; use txTimestamps() to replace them if necessary.
    '''
    addresses = dict()
    with open("bitcoinData/newOutputs.csv", "r") as outputs:
        for line in outputs:
            data = line.split(",", 6)
            if len(data) != 7:
                raise Exception("bad line in newOutputs.csv")
            txID, outputIndex, value, address = int(data[0]), int(data[2]), int(data[3]), data[5]
            addresses.setdefault(address, []).append([txID, outputIndex, value, None])
    
    print "finished loading outputs"

    with open("bitcoinData/newInputs.csv", "r") as inputs:
        for line in inputs:
            data = line.split(",")
            if len(data) != 7:
                raise Exception("bad line in newInputs.csv")
            inputTxID, address, outputTxID, outputIndex = int(data[0]), data[3], int(data[5]), int(data[6])
            # put input's txID with its corresponding output
            for output in addresses[address]:
                if output[0] == outputTxID and output[1] == outputIndex:
                    output[3] = inputTxID
                    break
            else:  # triggers if outputTxID does not exist in addresses[address]
                raise Exception("input's corresponding output could not be found in list")
            
    print "finished loading inputs"

    map (sort(key=itemgetter(0)), addresses)

    return addresses
