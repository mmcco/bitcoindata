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
import gc

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

    timestamp = calendar.timegm(parse(data[3][1:][:-1]).utctimetuple())  # convert ISO 8601 timestamp to Unix timestamp
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


def parseInput(inputLine):
    data = inputLine.split(",")
    # allow data to be of length 5 or 7 because this function is used to parse both inputs.csv and newInputs.csv
    if len(data) != 5 and len(data) != 7:
        raise Exception("bad line in inputs - cannot parse  -==-  " + inputLine)
    return data

def parseOutput(outputLine):
    data = outputLine.split(",", 5)
    # throw out the last item in data, it's just ",,"  !!! REMEMBER that this takes the newline off, so you have to add it manually when writing
    data = data[:-1]
    if len(data) != 5:
        raise Exception("bad line in outputs.csv - cannot parse  -==-  " + outputLine)
    return data

def newlineTrim(string):
    if string[-1] == '\n':
        return string[:-1]
    else:
        return string


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
    if int(data[0]) >= len(txHashes):
        raise Exception("output txID " + data[0] + " is outside the range available in txHashes  -==-  maximum available txID is " + str(len(txHashes)))
    txHash = txHashes[int(data[0])]
    dictIndex = txHash + "," + data[1]
    if dictIndex not in outputsDict:
        outputsDict[dictIndex] = [(data[0], data[4])]
    else:
        outputsDict[dictIndex].append( (data[0], data[4]) )

for line in inputs:
    data = parseInput(line)
    outputIDIndex = data[3] + "," + data[4][:-1]  # used as the index for outputsDict ([:-1] removes newline from data[4])
    if outputIDIndex not in outputsDict:
        raise Exception("input index " + data[1] + " from transaction ID " + data[0] + " calls an output that does not exist in outputsDict  -==-  attempted index: " + data[3] + "," + data[4]) 
    if len(outputsDict[outputIDIndex]) == 0:
        raise Exception("the output for input index " + data[1] + "from transaction ID " + data[0] + "has already been used")
    outputTxID, address = outputsDict[outputIDIndex].pop(0) # the oldest output is the one that has to be used first, according to the protocol
    data[3] = outputTxID  # replacing the outputTxHash with an outputTxID
    txHash = txHashes[int(data[0])]
    data.insert(1, txHash)
    data.insert(3, address)
    newInputs.write(",".join(data))

inputs.close()
outputs.close()
newInputs.close()

# attempting to manually clear memory, as the garbage collector doesn't seem to be doing so
outputsDict = dict()
gc.collect()


# now we're going to go through the inputs and outputs a second time, inserting each input's txID and index into its corresponding outputs
newInputs = open("newInputs.csv", "r")
newInputs.readline() # skip first line, which is just column names
outputs = open("outputs.csv", "r")
outputs.readline() # skip first line, which is just column names
newOutputs = open("newOutputs.csv", "w")
inputsDict = dict()  # key is output txID + "," + output index, value is input's txID + "," + input index

for line in newInputs:
    data = parseInput(line)
    inputsDict[ data[5] + "," + data[6][:-1] ] = data[0] + "," + data[2]  # [:-1] removes newline from data[6]

for line in outputs:
    data = parseOutput(line)
    # if there's a corresponding input, this output has been spent
    if data[0] + "," + data[1] in inputsDict:
        # insert the input values into inputTxID and inputIndex
        inputTxID, inputIndex = inputsDict[ data[0] + "," + data[1] ].split(",")
    else:
        # otherwise the output hasn't been spent yet, so use null values for the corresponding input
        inputTxID = ""
        inputIndex = ""
    txHash = txHashes[ int(data[0]) ]
    data.insert(1, txHash)
    data.append(inputTxID)
    data.append(inputIndex)
    newOutputs.write(",".join(data) + '\n')

newInputs.close()
outputs.close()
newOutputs.close()
