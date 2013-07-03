txs = open("txs.csv", "r")
inputs = open("inputs.csv", "r")
outputs = open("outputs.csv", "r")
newinputs = open("newinputs.csv", "w")
newoutputs = open("newoutputs.csv", "w")

txsList = []
for line in txs:
    data = line.split(",", 2)
    if len(txsList) != int(data[0]):
        raise Exception("txIDs and txsList do not match - len(txsList) is " + str(len(txsList)) + " while the txID is " + data[0])
    txsList.append(data[1])

for line in inputs:
    data = line.split(",", 1)
    newinputs.write(data[0] + "," + txsList[int(data[0])] + "," + data[1])

for line in outputs:
    data = line.split(",", 1)
    newoutputs.write(data[0] + "," + txsList[int(data[0])] + "," + data[1])

txs.close()
inputs.close()
outputs.close()
newinputs.close()
newoutputs.close()
