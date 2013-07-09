#!/usr/bin/python
import time
import MySQLdb

lastTime = time.time()

con = MySQLdb.connect(host="localhost",
                     user="root",
                     passwd="PS3SHA256",
                     db="btc")
                     #cursorclass = MySQLdb.cursors.SSCursor)

cur = con.cursor()

cur.execute("select count(*) from txs;")
# make an array with one indice for each transaction; each indice is a list of addresses combined in that transaction
txs = [[] for i in range (0, cur.fetchone()[0])]

print "txs initialized - took " + str(time.time() - lastTime) + " seconds"
lastTime = time.time()

cur.execute("select txID, address from inputs limit 1000;")
addresses = dict() # associates address with user

# fill a dict with a key for each address
for line in cur.fetchall():

    if len(line) != 3:
        raise Exception("bad response from database - length is " + str(len(line)) + " - first elem: " + str(line[0]) + " - second elem: " + str(line[1]))

    if not line[1] in addresses:
        # each address is declared with no parent and a rank of 1
        addresses[line[1]] = (line[1], 1)

    txs[line[0]].append(line[1])

print "addresses dict populated - took " + str(time.time() - lastTime) + " seconds"
lastTime = time.time()

for tx in txs:
    if len(tx) > 1:
        union(tx)

print "unions completed - took " + str(time.time() - lastTime) + " seconds"
lastTime = time.time()

users = dict() # associates users' address sets with their roots

for key, value in addresses.iteritems():
    
    if not value in users:
        users[value] = []

    users[value].append(key)

print "users generated - took " + str(time.time() - lastTime) + " seconds"
lastTime = time.time()

def union(*args):

    if len(args) == 1:
        raise Exception("union() passed a list of length 1")

    roots = map (getRoot(), args)

    # if they already have the same root, we're done
    if areAllEqual(zip(*roots)[0]):
        return

    # select the root with the highest rank as the parent, remove it
    maxRank = 0
    for root in roots:
        if root[1] > maxRank:
            parent = root
            maxRank = root[1]
    roots.remove(parent)
    
    # make everyone point to the parent
    for addr in zip(*roots)[0]:
        addresses[addr][0] = parent

    # increment the parent's rank
    addresses[parent[0]][1] += max(zip(*roots)[1])


# helper function that walks to the root and returns its key
def getRoot(addr):
    while addresses[addr][0] != addr:
        addr = addresses[addr]
    return addresses[addr]


# helper function, returns whether all items in a list are equal
def areAllEqual(*args):
    if len(args) is 0:
        return True

    elif len(args) is 3:
        return args[0] == args[1] == args[2]

    else:
        return (args[0] == args[1]) and areAllEqual(args[2:])


cur.close()
con.close()
