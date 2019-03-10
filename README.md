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

* The semaphore option allow to choose the nimber of shell process running in parallel (100 by default)
* The returncode option allow to show only success "-r0" or any error code you want
* The json option can be called multiple times and allow to access data from a json file

In the command line, each python iterators should be separated with a space and placed between quotes simple or double and you can use the other type of quotes to declare string values. Lists, list comprehension and any iterators can be used.

The IPNetwork class is imported from the netaddr package as it can be used as an Iterator for IP Addresses.

When running, the script will show in stderr a summary of the progress.

### Examples
```
./async_bash.py sleep "range(1, 10)"
```
No utility except showing how it works.

```
./async_bash.py -r0 ping -c2 "IPNetwork('192.168.1.0/24')"
```
Try 2 icmp requests to each ip of the 192.168.1.0/24 network and only display success.

```
./async_bash.py grep "['error', 'warning']" "['/var/log/messages{}'.format(x) for x in ['', '.1']]"
```
Show an example using two iterators
