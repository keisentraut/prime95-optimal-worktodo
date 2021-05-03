# Work generator for Prime95
This is a script which queries the PrimeNet server in order to get the status of exponents and then generates optimal P-1 / P+1 / ECM lines for the ```worktodo.txt``` of Prime95 / mprime. 
*Please don't run this with low sleep time on large ranges, it might create high load on the PrimeNet server.*

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

# Installation

## Windows

* Download Python3 from the official website at: https://www.python.org/downloads/windows/
* Install Python3 with default options
* Use ```pip.exe``` (usually located in ```C:\Users\{USER_NAME}\AppData\Local\Programs\Python\Python{XX}\Scripts\```) in order to install the requirement ```urllib3```: ```pip.exe install urllib3```
* Run the script with ```python.exe get_work.py 123000 124000 1```

## Linux

Please install Python 3.0 and the dependency "urllib3". This is dependent on your Linux distribution, I will list the commands below for some:

* Debian / Ubuntu: ```apt-get install python3 python3-urllib3``` (untested)
* Arch Linux: ```pacman -S python python-urllib3```
