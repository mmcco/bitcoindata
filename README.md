bitcoindata
===========

*This code introduces a set union algorithm to discern which groups of Bitcoin
accounts are owned by the same entity.  This concept was [developed
concurrently](http://cseweb.ucsd.edu/~smeiklejohn/files/imc13.pdf), in a much
more formal and throughly executed form, by Dr. [Sarah
Meiklejohn](http://cseweb.ucsd.edu/~smeiklejohn/bitcoin.html) as part of her
PhD work at UC San Diego.*

*There are some interesting parts, and the set union idea was
novel. However, this code was written by a 19-year-old research intern with
no previous real-world coding experience. It's here more for historical
purposes. I'm happy to help you work with it if you're interested. However,
I've come a long way since then, and I make no promises about code quality.*

This is an extensible toolset used to analyze the output of the
[blockparser](https://github.com/mcdee/blockparser) CSV call.

The tools focus on parsing the CSV output into more usable format, grouping
addresses by user based on multiple heuristics, and preparing the transaction
data for network analysis.

Everything is currently under heavy development and is therefore likely to be
broken. Within the next month I hope to have everything in stable working
order.

To run all of the main scripts at once, first ensure that all four of the
blockparser CSV files (`inputs.csv`, `outputs.csv`, `transactions.csv`,
`blocks.csv`) are in this repo's directory. Then run `bitcoindata`. The new
data will be larger than the original files, and the original files will not be
deleted, so make sure you have enough space in the directory.

New files generated:
* `users.csv`: A CSV file that associates addresses with their user IDs.
  This uses the classic user generation heuristic described by [Reid &
  Harrigan](http://arxiv.org/abs/1107.4524).
* `heurusers.csv`: The same as above, but using the new heuristic, which
  also analyzes output data. A comprehensive description of this
  heuristic will be published soon.
* `usersCount.csv`: Associates each user ID with the number of addresses
  assigned to it, using the classic heuristic.
* `heurUsersCount.csv`: The same as above, but using the new heuristic.

Please contact me if you have any questions about its use, or if you want to
help with its development.

We are using a machine with 22 GB of RAM, and some of these operations use all
of it. Therefore, some of this code may be unrealistically slow on a typical
personal computer.

This was written as part of a summer research project at Colgate University,
with my advisor Vijay Ramachandran.
