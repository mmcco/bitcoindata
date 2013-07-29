bitcoindata
===========
This is an extensible toolset used to analyze the output of the [blockparser](https://github.com/mcdee/blockparser) CSV call.

The tools focus on parsing the CSV output into more usable format, grouping addresses by user based on multiple heuristics, and preparing the transaction data for network analysis.

Everything is currently under heavy development and is therefore likely to be broken. Within the next month I hope to have everything in stable working order.

To run all of the main scripts at once, first ensure that all four of the blockparser CSV files (`inputs.csv`, `outputs.csv`, `transactions.csv`, `blocks.csv`) are in this repo's directory. Then run `bitcoindata.py`. The new data will be larger than the old files, and the original files will not be deleted, so make sure you have enough space in the directory.

Please contact me if you have any questions about its use, or if you want to help with its development.

We are using a machine with 22 GB of RAM, and some of these operations use all of it. Therefore, some of this code may be unrealistically slow on a typical personal computer.

This was written as part of a summer research project at Colgate University, with my advisor Vijay Ramachandran.

Everything in this repo is licensed under the GNU GPL.
