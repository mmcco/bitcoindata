# this script calculates the percentage of coins that fit Ron & Shamir's definition of "old coins"
# specifically, old coins have not been spent in ninety days
# the script generates a CSV file showing the percentages
# the default interval is three days

# all coins are stored in unspent outputs; we can therefore calculate the time distribution of coins simply by going through outputs and collecting unspent outputs

# a simpler way to do this would be to initially sort the outputs into "old coins" and "new coins"; each pass would be a sweep to delete all spent old outputs and move all aged new outputs into the "old" list

from dataStructs import outputsList, txTimestamps

outputs = outputsList()
timestamps = txTimestamps()

# we generate the percentage of coins that are old every three days
# therefore, we start three days after the first transaction
cutoffTime = timestamps[0] + 259200
# coins generated before this time are considered old
# we will make it ninety days before the cutoff time
oldTime = cutoffTime - 7776000
lastTxID = 0

with open("data/oldCoins.csv", "w") as oldCoinsFile:

    # stops executing when we've already processed all transactions
    while cutoffTime <= timestamps[-1]:
        
        # find the last txID in this timeframe
        while cutoffTime >= timestamps[lastTxID]:

            lastTxID += 1
            oldCoins = freshCoins = 0

        for output in outputs:

            txID, value, spentInTxID = output[0], output[2], output[3]

            if txID > lastTxID:
                break

            # if the output has already been spent, remove it and continue
            if spentInTxID is not None and spentInTxID <= lastTxID:
                outputs.remove(output)
                continue

            if timestamps[txID] < oldTime:
                oldCoins += value
            else:
                freshCoins += value

        if (oldCoins + freshCoins) != 0:
            percentOld = float(oldCoins) / (oldCoins + freshCoins)
            oldCoinsFile.write(str(cutoffTime) + "," + str(percentOld) + '\n')

            cutoffTime += 259200
            oldTime += 259200
