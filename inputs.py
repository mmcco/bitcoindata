# new logic:
# (1) go through inputs, get evey spent output's value
# (2) go through outputs, only get info if spent (in previously populated dict)
# (3) go back thfough inputs, writing info

from dataStructs import outputsDict, txHashes, parseCSVLine

# we will first get the addresses and values from the outputs and insert them into the inputs
# we will also insert the txHash into the inputs (which initially only has the txID)
# finally, we will also replace the outputTxHash (which is not a unique identifier of a tx) with an outputTxID (which is a unique identifier of a tx)
outputs = outputsDict()  # key is output's txHash + "," +  output's index, value is the tuple (output's txID, receiving address) for each output with this txHash and index
hashes = txHashes()

with open("inputs.csv", "r") as inputs, open("bitcoinData/newInputs.csv", "w") as newInputs:
    inputs.readline()  # skip first line, which is just column names
    for line in inputs:
        data = parseCSVLine(line, 5)
        txID, index, outputTxHash, outputTxIndex = data[0], data[1], data[3], data[4]
        outputsKey = outputTxHash + "," + newlineTrim(outputTxIndex)  # used as the index for outputs
        if outputsKey not in outputs:
            raise Exception("input index " + index + " from transaction ID " + txID + " calls an output that does not exist in outputs  -==-  attempted index: " + outputTxHash + "," + outputTxIndex)
        if len(outputs[outputsKey]) == 0:
            raise Exception("the output for input index " + index + "from transaction ID " + txID + "has already been used")
        outputTxID, address, value = outputs[outputsKey].pop(0)  # the oldest output is the one that has to be used first, according to the protocol
        txHash = txHashes[int(txID)]
        data[3] = outputTxID  # replacing the outputTxHash with an outputTxID
        data.insert(1, txHash)
        data.insert(3, address)
        data.insert(4, value)
        newInputs.write(",".join(data))
