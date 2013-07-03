inputs = open("newinputs.csv", "r")
outputs = open("newoutputs.csv", "r")
neweroutputs = open("neweroutputs.csv", "w")

inputDict = dict()

for line in inputs:
    data = line.split(",", 5)
    # the dict index of each input is its outputTxHash concatenated with its outputTxIndex
    # the value of each input is its txHash concatenated with its index
    inputDict[data[4] + data[5][:-1]] = data[1] + data[2] # cut off the newline from data[5]
    #print data[4] + data[5] + "   " + data[1] + data[2]

for line in outputs:
    data = line.split(",", 6)[:-1] # remove the trailing comma, which gets parsed as the last item
    #print data[1] + data[2]
    if data[1] + data[2] in inputDict:
        inputData = inputDict[data[1] + data[2]] # contains the txHash and the txIndex of the corresponding input
        neweroutputs.write(",".join(data) + "," + inputData[:-1] + "," + inputData[-1] + '\n')
    # if there's no corresponding input, leave them blank
    else:
        neweroutputs.write(",".join(data) + ",,\n")
        
inputs.close()
outputs.close()
neweroutputs.close()
