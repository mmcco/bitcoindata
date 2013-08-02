from dataStructs import outputsToInputs, parseCSVLine, txHashes

inputsDict = outputsToInputs()
hashes = txHashes()

with open("outputs.csv", "r") as outputsFile, open("bitcoinData/newOutputs.csv", "w") as newOutputs:

    outputsFile.readline()  # skip column names

    for line in outputsFile:
        data = parseCSVLine(line, 6)[:-1]  # drop the last item, it's just empty columns
        outputTxID, outputIndex = data[0], data[1]
        dictIndex = (outputTxID, outputIndex)

        if dictIndex in inputsDict:
            inputTxID, inputIndex = inputsDict[dictIndex]
            # delete in order to reclaim memory
            del inputsDict[dictIndex]

        else:
            inputTxID = inputIndex = ""

        # insert the txHash
        data.insert(1, hashes[int(outputTxID)])
        data.append(inputTxID)
        data.append(inputIndex)
        newOutputs.write(",".join(data) + '\n')
