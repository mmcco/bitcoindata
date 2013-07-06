# this script is an attempted all-in-one processor of blockparser's CSV-generator
# it makes changes that are necessary or convenient, preparing the data for parsing by a SQL database
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
#
# tx is used as an abbreviation for transaction

from sys import argv
from dateutil.parser import parse
import calendar
import datetime

blocks = open("blocks.csv", "r")
blocks.readline()  # skip first line, which is just column names
newBlocks = open("newBlocks.csv", "w")
# !!! This data type assumes that you're parsing from the genesis block; switch to dict if writing an automated updater !!!
blockTimes = []  # location is blockID, value is Unix timestamp

for line in blocks:
    data = line.split(",", 4)
    if len(data) < 5:
        raise Exception("bad line in blocks.csv")
    if int(data[0]) != len(blockTimes):
        raise Exception("mismatch between blockID (" + data[0] + ") and blockTimes list length " + str(len(blockTimes)) + ")")

    timestamp = calendar.timegm(parse(data[3][1:][:-1]).utctimetuple())  # convert ISO 8601 timestamp to Unix timestamp
    blockTimes.append(str(timestamp))
    data[3] = str(timestamp)
    newBlocks.write(",".join(data))

blocks.close()
newBlocks.close()


txs = open("transactions.csv", "r")
txs.readline()  # skip first line, which is just column names
newTxs = open("txs.csv", "w")
# !!! This data type assumes that you're parsing from the genesis block; switch to dict if writing an automated updater !!!
txHashes = []  # location is txID, value is txHash
hashDict = dict()  # key is txHash, value is corresponding txID(s) - this is used because multiples txs can have the same hashes

for line in txs:
    data = line.split(",", 4)
    if len(data) != 5:
        raise Exception("bad line in transactions.csv")
    if len(txHashes) != int(data[0]):
        raise Exception("txIDs and txHashes do not match - len(txHashes) is " + str(len(txHashes)) + " while the txID is " + data[0])

    txHashes.append(data[1])
    if data[1] not in txHashDict:
        txHashDict[data[1]] = [data[0]]
    else:
        txHashDict[data[1]].append(data[0])
    data.insert(4, blockTimes[ int(data[3]) ])
    newTxs.write(",".join(data))

txs.close()
newTxs.close()


def parseInput(inputs):
    data = line.split(",", 4)
    if len(data) != 5:
        raise Exception("bad line in inputs.csv")
    return data

def parseOutput(outputs):
    data = line.split(",", 5)
    data = data[:-1] # throw out the last item in data, it's just ",,"
    if len(data) != 5:
        raise Exception("bad line in outputs.csv")
    return data


# we will first get the addresses from the outputs and insert them into the inputs
inputs = open("inputs.csv", "r")
inputs.readline() # skip first line, which is just column names
outputs = open("outputs.csv", "r")
outputs.readline() # skip first line, which is just column names
newInputs = open("newinputs.csv", "w")
outputsDict = dict()  # key is output's txID + "," +  output's index, value is receiving address

for line in outputs:
    data = parseOutput(line)
    outputsDict[ data[0] + "," + data[1] ] = data[4]

for line in inputs:
    data = parseInput(line)
    ### !!! LOGIC ERROR !!! using a hash when a txID is expected
    outputTxHash = data[3]
    if len(txHashDict[outputTxHash]) == 1:     # if there's only one tx associated with this hash...
        outputTxID = txHashDict[outputTxHash]  # we just use that one
    else:
        outputTxID = txHashDict[outputTxHash].pop(0)  # otherwise, based on the protocol it has to be the oldest tx with this hash
    if data[3] + "," + data[4] not in outputsDict:

        raise Exception("input index " + data[1] + " from transaction " + data[0] + " does not have a corresponding item in outputsDict")
    data[3] = outputTxID  # replacing the outputTxHash with an outputTxID
    txHash = txHashes[int(data[0])]
    data.insert(1, txHash)
    address = outputsDict[ outputTxID + "," + data[4] ]
    data.insert(3, address)
    newInputs.write(",".join(data))

inputs.close()
outputs.close()
newInputs.close()


# now we're going to go through a second time, inserting inputs' information into their corresponding outputs
inputs = open("inputs.csv", "r")
inputs.readline() # skip first line, which is just column names
outputs = open("outputs.csv", "r")
outputs.readline() # skip first line, which is just column names
newOutputs = open("newoutputs.csv", "w")
inputsDict = dict()  # key is output txID + "," + output index, value is input's txID + "," + input index

for line in inputs:
    data = parseInput(line)
    inputsDict[ data[3] + "," + data[4] ] = data[0] + "," + data[1]

for line in outputs:
    data = parseOutput(line)
    # if there's a corresponding input, this output has been spent
    if data[0] + "," + data[1] in inputsDict:
        # insert the input values into inputTxID and inputTxIndex
        thisInput = inputsDict[ data[0] + data[1] ].split(",")
        inputTxID = thisInput[0]
        inputTxIndex = thisInput[1]
    else:
        # otherwise the output hasn't been spent yet, so use null values for the corresponding input
        inputTxID = ""
        inputTxIndex = ""
    txHash = txHashes[ int(data[0]) ]
    data.insert(1, txHash)
    data.append(inputTxID)
    data.append(inputTxIndex)
    newOutputs.write(",".join(data) + '\n')

inputs.close()
outputs.close()
newOutputs.close()
