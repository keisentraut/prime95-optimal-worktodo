# Work generator for Prime95
This is a script which queries the PrimeNet server in order to get the status of exponents and then generates optimal P-1 / P+1 / ECM lines for the ```worktodo.txt``` of Prime95 / mprime. 
Please don't run this with large ranges, it will do high load on the server.

TODO: explain what is going on here, for now this link will have do it [https://mersenneforum.org/showthread.php?t=26750](https://mersenneforum.org/showthread.php?t=26750).

# Usage

```
 usage:
     python.exe get_work.py <from> <to>
 example:
     python.exe get_work.py 123000 124000
         generates worktodos.txt for Mersenne numbers between 2^123000 and 2^124000
         if all Mersenne numbers in this range have appropriate P-1/P+1/ECM,
         then no output is generated
```

# Example run

```
$ ./get_work.py 1234000 1234200

# n:                1234001
# how_far_factored: 71
# Factors:          {45764385745049421216983}
# factors known:    True
# ECM Factoring:    {(250000, 35000000): 44, (50000, 5000000): 249}
# P-1 Factoring:    {(1325000, 33125000, 12), (20000, 395000, 12), (2500000, 62500000, 12), (1000, 1000, 0)}
# P+1 Factoring:    {(3000000, 216000000, 2, 7)}
# assigned:         False
# fully factored:   False
# 
# should not do P-1: B1=1000000 recommended but 1325000 already done with B2=25.0*B1
# should not do P-1: B1=1000000 recommended but 2500000 already done with B2=25.0*B1
# should not do PP1: B1=500000 recommended but 3000000 already done with B2=72.0*B1

# n:                1234003
# how_far_factored: 71
# Factors:          {1746327417618890599}
# factors known:    True
# ECM Factoring:    {(250000, 35000000): 44, (50000, 5000000): 281}
# P-1 Factoring:    {(20000, 395000, 12), (300000, 10000000, 12), (1000, 1000, 0)}
# P+1 Factoring:    set()
# assigned:         False
# fully factored:   False
# 
Pminus1=N/A,1,2,1234003,-1,1000000,0,71,"1746327417618890599"
Pplus1=N/A,1,2,1234003,-1,500000,0,1,71,"1746327417618890599"

# n:                1234039
# how_far_factored: 71
# Factors:          {148084681, 22212703}
# factors known:    True
# ECM Factoring:    {(250000, 35000000): 44, (50000, 5000000): 281}
# P-1 Factoring:    {(300000, 10000000, 12)}
# P+1 Factoring:    set()
# assigned:         False
# fully factored:   False
# 
Pminus1=N/A,1,2,1234039,-1,1000000,0,71,"148084681,22212703"
Pplus1=N/A,1,2,1234039,-1,500000,0,1,71,"148084681,22212703"

# n:                1234049
# how_far_factored: 71
# Factors:          set()
# factors known:    False
# ECM Factoring:    {(250000, 35000000): 44, (50000, 5000000): 281}
# P-1 Factoring:    {(1234049, 123404900, 12), (1234049, 135745390, 0), (1234049, 135745390, 12), (1325000, 33125000, 12), (20000, 395000, 12), (2500000, 62500000, 12), (1000, 1000, 0)}
# P+1 Factoring:    set()
# assigned:         False
# fully factored:   False
# 
Pminus1=N/A,1,2,1234049,-1,5000000,0,71
Pplus1=N/A,1,2,1234049,-1,2500000,0,1,71

# n:                1234063
# how_far_factored: 71
# Factors:          {80868148391}
# factors known:    True
# ECM Factoring:    {(250000, 35000000): 44, (50000, 5000000): 281}
# P-1 Factoring:    {(300000, 10000000, 12)}
# P+1 Factoring:    set()
# assigned:         False
# fully factored:   False
# 
Pminus1=N/A,1,2,1234063,-1,1000000,0,71,"80868148391"
Pplus1=N/A,1,2,1234063,-1,500000,0,1,71,"80868148391"

# n:                1234067
# how_far_factored: 67
# Factors:          {148088041, 35347055227950909167}
# factors known:    True
# ECM Factoring:    {(250000, 35000000): 44, (50000, 5000000): 226}
# P-1 Factoring:    {(300000, 10000000, 12)}
# P+1 Factoring:    set()
# assigned:         False
# fully factored:   False
# 
Pminus1=N/A,1,2,1234067,-1,1000000,0,67,"148088041,35347055227950909167"
Pplus1=N/A,1,2,1234067,-1,500000,0,1,67,"148088041,35347055227950909167"

# n:                1234099
# how_far_factored: 71
# Factors:          {347472914441}
# factors known:    True
# ECM Factoring:    {(250000, 35000000): 44, (50000, 5000000): 281}
# P-1 Factoring:    {(300000, 10000000, 12)}
# P+1 Factoring:    set()
# assigned:         False
# fully factored:   False
# 
Pminus1=N/A,1,2,1234099,-1,1000000,0,71,"347472914441"
Pplus1=N/A,1,2,1234099,-1,500000,0,1,71,"347472914441"

# n:                1234109
# how_far_factored: 71
# Factors:          {398881082211805601}
# factors known:    True
# ECM Factoring:    {(250000, 35000000): 44, (50000, 5000000): 281}
# P-1 Factoring:    {(20000, 395000, 12), (300000, 10000000, 12), (1000, 1000, 0)}
# P+1 Factoring:    set()
# assigned:         False
# fully factored:   False
# 
Pminus1=N/A,1,2,1234109,-1,1000000,0,71,"398881082211805601"
Pplus1=N/A,1,2,1234109,-1,500000,0,1,71,"398881082211805601"

# n:                1234117
# how_far_factored: 71
# Factors:          {363561172139282460272681, 364496455951}
# factors known:    True
# ECM Factoring:    {(250000, 35000000): 44, (50000, 5000000): 246}
# P-1 Factoring:    {(300000, 10000000, 12)}
# P+1 Factoring:    set()
# assigned:         False
# fully factored:   False
# 
Pminus1=N/A,1,2,1234117,-1,1000000,0,71,"363561172139282460272681,364496455951"
Pplus1=N/A,1,2,1234117,-1,500000,0,1,71,"363561172139282460272681,364496455951"

# n:                1234133
# how_far_factored: 71
# Factors:          {11961763688031202905250577}
# factors known:    True
# ECM Factoring:    {(250000, 35000000): 44, (50000, 5000000): 277}
# P-1 Factoring:    {(1325000, 33125000, 12), (20000, 395000, 12), (300000, 10000000, 12), (1000, 1000, 0)}
# P+1 Factoring:    set()
# assigned:         False
# fully factored:   False
# 
# should not do P-1: B1=1000000 recommended but 1325000 already done with B2=25.0*B1
Pplus1=N/A,1,2,1234133,-1,500000,0,1,71,"11961763688031202905250577"

# n:                1234147
# how_far_factored: 71
# Factors:          {813920475751599481, 18554165999, 52527885560407, 130819583}
# factors known:    True
# ECM Factoring:    {(250000, 35000000): 44, (50000, 5000000): 281}
# P-1 Factoring:    {(300000, 10000000, 12)}
# P+1 Factoring:    set()
# assigned:         False
# fully factored:   False
# 
Pminus1=N/A,1,2,1234147,-1,1000000,0,71,"813920475751599481,18554165999,52527885560407,130819583"
Pplus1=N/A,1,2,1234147,-1,500000,0,1,71,"813920475751599481,18554165999,52527885560407,130819583"

# n:                1234187
# how_far_factored: 71
# Factors:          {14958346441, 7208214333775539319, 22215367}
# factors known:    True
# ECM Factoring:    {(250000, 35000000): 44, (50000, 5000000): 281}
# P-1 Factoring:    {(300000, 10000000, 12)}
# P+1 Factoring:    set()
# assigned:         False
# fully factored:   False
# 
Pminus1=N/A,1,2,1234187,-1,1000000,0,71,"14958346441,7208214333775539319,22215367"
Pplus1=N/A,1,2,1234187,-1,500000,0,1,71,"14958346441,7208214333775539319,22215367"
```

