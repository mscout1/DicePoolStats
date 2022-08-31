# DicePoolStats
A script to explore probability related to oWoD dice pools.  

This is a huge monte carlo simulation I wrote for fun in 2009. It simulates
a pool of D10s being rolled and evaluated according to a modified version
of White Wolf's Old "World Of Darkness" rules.

It reports the results of getting 'S' successes, of getting at least S successes,
and of botching, given a Dice Pool of size 'p' and a Difficulty of 'd' for a
range of Ds and Ps .

The original version is in DiePoolStatsOld.py2
Since this was a personal hobby project, the code is pretty crude and the variable names
are a bit arbitrary. I included it because it is an example of performance aware code.
(My first version ran out of memory and crashed. This version crunches as it goes instead of
  trying to generate all data, then evaluate.) Running this for 1 billion trials took a couple
of days, spread over 2 computers.

The 2022 version is in DiePoolStats.py. 
I updated the code to python 3.10, and cleaned up a lot of messy code. I also
Changed it to do exact pools instead of random, generating every possible roll.
This limits it to 7-die pools, and no reroll10 rules. (An "all possible rolls" 
generator with unlimited reroll10s is an infinite loop...) Since our 2022 game
is not using roroll10s, it's a small loss.

I think the pair of these showcases a small part of my evolution as a 
programmer.