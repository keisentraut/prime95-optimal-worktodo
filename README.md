# Work generator for Prime95
This is a script which queries the PrimeNet server in order to get the status of exponents and then generates P-1 / P+1 lines for the ```worktodo.txt``` of Prime95 / mprime. 
You should use this script if you want to contribute to the forum goal of increasing P-1 / P+1 bounds above the bounds below for all small-ish Mersenne numbers.
Please read the complete thread at [https://mersenneforum.org/showthread.php?t=26750](https://mersenneforum.org/showthread.php?t=26750), too.

*Please don't run this with low sleep time on large ranges, it might create high load on the PrimeNet server.*

From the discussions at mersenneforum.org, I have defined the following bounds as the "desired" bounds:

| Exponent range | P-1 B1 (known factor) | P-1 B1 (unfactored) |
| ------ | ------ | ----- |
| 50k < n < 100k  | 100.000.000 | 250.000.000 |
| 100k < n < 250k |  30.000.000 | 100.000.000 |
| 250k < n < 500k |  15.000.000 |  30.000.000 |
| 500k < n < 1M   |  10.000.000 |  15.000.000 |
| 1M < n < 4M     |   5.000.000 |   5.000.000 |
| 4M < n < 10M    |   2.500.000 |   2.500.000 |
| 10M < n         |   2.000.000 |   2.000.000 |

The desired target bound B1 for P+1 is to have at least one run with a value of 

* half of the desired P-1 bound; or
* half of P-1 bound which was already done for this exponent.

This script might skip the exponent if one of the following is true:

* P-1 and P+1 are already both done with bounds above the desired ones.
* There was recent activity with this exponent, i.e results reported <90 days ago.
* It also will skip the exponent, if B1 is below the desired target, but the increase would be very low: For instance, the target bound is B1=10M but there was already a B1=9M run. 
* Mersenne numbers below 50k are not considered and the script will skip all of them.  GMP-ECM is the better tool for numbers <50k compared to Prime95.

# Usage

```
# This is a script which queries the PrimeNet server in order 
# to get the status of exponents. Please don't run this with 
# large ranges, it might create high load on the server.
# 
# see https://mersenneforum.org/showthread.php?t=26750
# 
# usage:
#     python.exe get_work.py <from> <to> <print_debug>
# example:
#     python.exe get_work.py 123000 124000 1
#         generates P-1/P+1 worktodo.txt file for Mersenne numbers with exponents between
#         123000 and 124000.If all Mersenne numbers in this range have appropriate P-1/P+1,
#         then no output is generated. The last argument "1" enables debug output.
#         Set the debug output to "0", if you want to pass the output directly to Prime95.
```

# Installation

## Windows

* Download Python3 from the official website at: https://www.python.org/downloads/windows/
* Install Python3 with default options
* Use ```pip.exe``` (usually located in ```C:\Users\{USER_NAME}\AppData\Local\Programs\Python\Python{XX}\Scripts\```) in order to install the requirement ```urllib3```: ```pip.exe install urllib3```.
* Run the script with ```python.exe get_work.py 123000 124000 1```

## Linux

Please install Python 3.0 and the dependency "urllib3". This is dependent on your Linux distribution, I will list the commands below for some:

* Debian / Ubuntu: ```apt-get install python3 python3-urllib3``` (untested)
* Arch Linux: ```pacman -S python python-urllib3```
