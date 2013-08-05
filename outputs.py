'''outputs.py: Writes outputs from ./outputs.csv to ./data/newOutputs.csv.
In the process, it inserts the txHash, inputTxID, and inputIndex.
The inputTxID and inputIndex will be empty if the output is unspent.
'''

from dataStructs import outputsToInputs, parseCSVLine, txHashes

inputsDict = outputsToInputs()
hashes = txHashes()

with open("outputs.csv", "r") as outputsFile, open("data/newOutputs.csv", "w") as newOutputs:

    outputsFile.readline()  # skip column names

    for line in outputsFile:
        data = parseCSVLine(line, 6)[:-1]  # drop the last item, it's just empty columns
        outputTxID, outputIndex = data[0], data[1]
        dictKey = (outputTxID, outputIndex)

        if dictKey in inputsDict:
            inputTxID, inputIndex = inputsDict[dictKey]
            # delete in order to reclaim memory
            del inputsDict[dictKey]

        else:
            inputTxID = inputIndex = ""

        # insert the txHash
        data.insert(1, hashes[int(outputTxID)])
        data.append(inputTxID)
        data.append(inputIndex)
        newOutputs.write(",".join(data) + '\n')
