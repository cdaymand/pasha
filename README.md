# pasha
Python 3 Async shell Accelerated.
The aim of this repository is to share python3 scripts to increase your shell productivity.
Currently only one script is available but I have some other scripts ideas ;)

## async_bash.py
This script allow to write a shell command line integrating one to many python iterators.
The script will evaluates these iterators, collect all the commands, run them asynchronously and show the result using a json format.

### Usage
```
usage: async_bash.py [-h] [-s [SEMAPHORE]] [-r [RETURNCODE]] [-j [JSON]] ...

positional arguments:
  command_line

optional arguments:
  -h, --help            show this help message and exit
  -s [SEMAPHORE], --semaphore [SEMAPHORE]
                        Number of commands to execute at the same time
  -r [RETURNCODE], --returncode [RETURNCODE]
                        Only show output for the selected returncode
  -j [JSON], --json [JSON]
                        Access json iterators with self.json['JSON']
```
