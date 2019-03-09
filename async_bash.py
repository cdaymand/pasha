#!/usr/bin/env python3
import json
import asyncio
import sys

from argparse import ArgumentParser
from collections import OrderedDict
from termcolor import colored


class AsyncCommand():
    def __init__(self, command_line, semaphore):
        self.commands = self.get_all_commands(command_line)
        self.semaphore = asyncio.Semaphore(semaphore)

    def run(self):
        self.result = {}
        self.tasks_finished = 0
        self.success = 0
        self.failure = 0
        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(self.execute_commands())
        except (KeyboardInterrupt):
            pass
        loop.close()
        print(" " * 50, file=sys.stderr)
        print(json.dumps(self.result, indent=4, ensure_ascii=False))
        
    def get_all_commands(self, command_line):
        commands = []
        for element in command_line:
            if element.startswith('[') and element.endswith(']'):
                index = command_line.index(element)
                for parameter in eval(element):
                    commands += self.get_all_commands(command_line[:index]+[str(parameter)]+command_line[index+1:])
                break
        else:
            commands.append(command_line)
        return commands

    def print_progress(self, returncode):
        self.tasks_finished += 1
        if returncode == 0:
            self.success += 1
        else:
            self.failure += 1
        print("Progress {}/{} {}: {} {}: {}".format(self.tasks_finished,
                                                    len(self.commands),
                                                    colored("SUCCESS", "green"),
                                                    self.success,
                                                    colored("FAILURE", "red"),
                                                    self.failure), end='\r', file=sys.stderr)

    async def execute_command(self, command):
        async with self.semaphore:
            process = await asyncio.create_subprocess_exec(*command,
                                                           stdout=asyncio.subprocess.PIPE,
                                                           stderr=asyncio.subprocess.PIPE)
            stdout, stderr = await process.communicate()
            self.print_progress(process.returncode)
            self.result[" ".join(command)] = OrderedDict([
                ("returncode", process.returncode),
                ("stdout", stdout.decode("utf8").split("\n")),
                ("stderr", stderr.decode("utf8").split("\n"))])

    async def execute_commands(self):
        tasks = []
        for command in self.commands:
            tasks.append(self.execute_command(command))
        await asyncio.gather(*tasks)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('-s', '--semaphore', nargs='?', type=int, default=100, help="Number of commands to execute at the same time")
    args, command_line = parser.parse_known_args()
    print(command_line)
    async_command = AsyncCommand(command_line, args.semaphore)
    async_command.run()