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

from dateutil.parser import parse
import calendar
import datetime

# we begin by converting each block's timestamp from ISO 8601 to a Unix timestamp
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

    timestamp = calendar.timegm(parse(data[3][1:-1]).utctimetuple())  # convert ISO 8601 timestamp to Unix timestamp
    blockTimes.append(str(timestamp))
    data[3] = str(timestamp)
    newBlocks.write(",".join(data))

blocks.close()
newBlocks.close()


# this section selects the Unix timestamp of each tx's corresponding block and inserts it into the tx
txs = open("transactions.csv", "r")
txs.readline()  # skip first line, which is just column names
newTxs = open("txs.csv", "w")
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
    if len(data) != 6:
        raise Exception("bad line in outputs.csv - cannot parse  -==-  " + outputLine)
    # drop the end of the line, as it's just trailing commas
    return data[:5]

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
newInputs = open("newInputs.csv", "w")
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
newInputs = open("newInputs.csv", "r")
outputs = open("outputs.csv", "r")
outputs.readline() # skip first line, which is just column names
newOutputs = open("newOutputs.csv", "w")
inputsDict = dict()  # key is output txID + "," + output index, value is input's txID + "," + input index

for line in newInputs:
    data = parseInput(line)
    txID, index, outputTxHash, outputTxIndex
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
