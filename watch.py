#!/usr/bin/env python3
import time
import os

from subprocess import check_output
from difflib import ndiff
from termcolor import colored
from argparse import ArgumentParser, REMAINDER
from datetime import datetime


class WatchProcess():
    def __init__(self, command_line, interval):
        self.interval = interval
        self.command_line = command_line

    def run(self):
        result = {
            'stdout_list': []
        }
        try:
            while True:
                stdout = check_output(self.command_line).decode('utf8').split('\n')
                os.system('clear')
                print("Every {:.1f}s: {}\t{}\n".format(self.interval,
                                                       " ".join(self.command_line),
                                                       datetime.now().strftime("%a %b %d %H:%M:%S %Y")))
                result['stdout_list'].append(stdout)
                current_stdout = result['stdout_list'][-1]
                if len(result['stdout_list']) > 1:
                    previous_stdout = result['stdout_list'][-2]
                    for line in ndiff(previous_stdout, current_stdout):
                        color = None
                        if line.startswith('-'):
                            color = 'red'
                        elif line.startswith('+'):
                            color = 'green'
                        elif line.startswith('?'):
                            color = 'yellow'
                        if color is not None:
                            print(colored(line, color))
                        else:
                            print(line)
                else:
                    for line in current_stdout:
                        print("  "+line)
                time.sleep(self.interval)
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('-n', '--interval', nargs='?', type=int, default=2, help="Refresh interval")
    parser.add_argument('command_line', nargs=REMAINDER, type=str)
    args = parser.parse_args()
    watch_process = WatchProcess(args.command_line, args.interval)
    watch_process.run()
