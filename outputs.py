from dataStructs import outputsToInputs, parseCSVLine, txHashes

inputsDict = outputsToInputs()
hashes = txHashes()

with open("outputs.csv", "r") as outputsFile, open("bitcoinData/newOutputs.csv", "w") as newOutputs:

    outputsFile.readline()  # skip column names

    for line in outputsFile:
        data = parseCSVLine(line, 6)[:-1]  # drop the last item, it's just empty columns
        outputTxID, outputIndex = data[0], data[1]

        if (outputTxID, outputIndex) in inputsDict:
            inputTxID, inputIndex = inputsDict[(outputTxID, outputIndex)]

        else:
            inputTxID = inputIndex = ""

        # insert the txHash
        data.insert(1, hashes[int(outputTxID)])
        data.append(inputTxID)
        data.append(inputIndex)
        newOutputs.write(",".join(data) + '\n')
