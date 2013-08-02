#!/usr/bin/env python

# this script simply executes all of the main component scripts in one go

import os

if __name__ == "__main__":

    if not os.path.exists("bitcoinData"):
        os.makedirs("bitcoinData")

    execfile("blocks.py")
    print "blocks written"
    execfile("txs.py")
    print "transactions written"
    execfile("inputs.py")
    print "inputs written"
    execfile("outputs.py")
    print "outputs written"

    execfile("users.py")
    print "classic user heuristic finished"
    execfile("heurusers.py")
    print "new user heuristic finished"
#    execfile("networkXGraph.py")
