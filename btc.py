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
#
# tx is used as an abbreviation for transaction

# add file origin to path because of symlinks
# !!! REMOVE THIS IN FINAL CODE
import sys
sys.path.append("/home/mike/bitcoindata")
from dataStructs import parseCSVLine
from dateutil.parser import parse
import calendar
import datetime


def newlineTrim(string):
    if len(string) == 0 or string[-1] != '\n':
        return string
    else:
        return string[:-1]


# we begin by converting each block's timestamp from ISO 8601 to a Unix timestamp
# !!! This data type assumes that you're parsing from the genesis block; switch to dict if writing an automated updater !!!
blockTimes = []  # location is blockID, value is Unix timestamp

with open("blocks.csv", "r") as blocks, open("bitcoinData/newBlocks.csv", "w") as newBlocks:
    blocks.readline()  # skip first line, which is just column names
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


# this section selects the Unix timestamp of each tx's corresponding block and inserts it into the tx
# !!! This data type assumes that you're parsing from the genesis block; switch to dict if writing an automated updater !!!
txHashes = []  # location is txID, value is txHash

with open("transactions.csv", "r") as txs, open("bitcoinData/txs.csv", "w") as newTxs:
    txs.readline()  # skip first line, which is just column names
    for line in txs:
        data = line.split(",", 4)
        if len(data) != 5:
            raise Exception("bad line in transactions.csv")
        if len(txHashes) != int(data[0]):
            raise Exception("txIDs and txHashes do not match - len(txHashes) is " + str(len(txHashes)) + " while the txID is " + data[0])

        txHashes.append(data[1])


# we will first get the addresses and values from the outputs and insert them into the inputs
# we will also insert the txHash into the inputs (which initially only has the txID)
# finally, we will also replace the outputTxHash (which is not a unique identifier of a tx) with an outputTxID (which is a unique identifier of a tx)
outputsDict = dict()  # key is output's txHash + "," +  output's index, value is the tuple (output's txID, receiving address) for each output with this txHash and index

with open("outputs.csv", "r") as outputs:
    outputs.readline() # skip first line, which is just column names
    for line in outputs:
        data = parseCSVLine(line, 6)
        txID, index, value, address = data[0], data[1], data[2], data[4]
        if int(txID) >= len(txHashes):
            raise Exception("output txID " + txID + " is outside the range available in txHashes  -==-  maximum available txID is " + str(len(txHashes)))
        txHash = txHashes[int(txID)]
        dictIndex = txHash + "," + index
        # allow for multiple values in each outputsDict location because txHashes are not unique identifiers of txs
        # in accordance with the Bitcoin protocol, each outputsDict location is a queue
        outputsDict.setdefault(dictIndex, []).append((txID, address, value))

with open("inputs.csv", "r") as inputs, open("bitcoinData/newInputs.csv", "w") as newInputs:
    inputs.readline() # skip first line, which is just column names
    for line in inputs:
        data = parseCSVLine(line, 5)
        txID, index, outputTxHash, outputTxIndex = data[0], data[1], data[3], data[4]
        outputsDictKey = outputTxHash + "," + newlineTrim(outputTxIndex)  # used as the index for outputsDict
        if outputsDictKey not in outputsDict:
            raise Exception("input index " + index + " from transaction ID " + txID + " calls an output that does not exist in outputsDict  -==-  attempted index: " + outputTxHash + "," + outputTxIndex) 
        if len(outputsDict[outputsDictKey]) == 0:
            raise Exception("the output for input index " + index + "from transaction ID " + txID + "has already been used")
        outputTxID, address, value = outputsDict[outputsDictKey].pop(0) # the oldest output is the one that has to be used first, according to the protocol
        txHash = txHashes[int(txID)]
        data[3] = outputTxID  # replacing the outputTxHash with an outputTxID
        data.insert(1, txHash)
        data.insert(3, address)
        data.insert(4, value)
        newInputs.write(",".join(data))


# now we're going to go through the inputs and outputs a second time, inserting each input's txID and index into its corresponding outputs
inputsDict = dict()  # key is output txID + "," + output index, value is input's txID + "," + input index

with open("bitcoinData/newInputs.csv", "r") as newInputs:
    for line in newInputs:
        data = parseCSVLine(line, 9)
        txID, index, outputTxHash, outputTxIndex = data[0], data[2], data[7], data[8]
        inputsDict[ outputTxHash + "," + newlineTrim(outputTxIndex) ] = txID + "," + index

with open("outputs.csv", "r") as outputs, open("bitcoinData/newOutputs.csv", "w") as newOutputs:
    outputs.readline() # skip first line, which is just column names
    for line in outputs:
        data = parseCSVLine(line, 3)
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
