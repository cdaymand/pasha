#!/usr/bin/env python3
import os
import asyncio

from argparse import ArgumentParser
from collections import OrderedDict
from termcolor import colored

from async_bash import AsyncCommand
from socket import gethostbyname, gaierror
from pyroute2.netlink.diag import DiagSocket, AF_INET, SS_ESTABLISHED,\
    IPPROTO_TCP, NLM_F_REQUEST, SOCK_DIAG_BY_FAMILY, inet_diag_req
from pyroute2.netlink import NLM_F_DUMP


INET_DIAG_INFO = 2
HUMAN_READABLE_BYTES = (
    ("GB", 10**9),
    ("MB", 10**6),
    ("kB", 10**3),
    ("B", 1)
)


def get_tcp_sockets_infos(dport):
    with DiagSocket() as diag_socket:
        req = inet_diag_req()
        req['sdiag_family'] = AF_INET
        req['sdiag_protocol'] = IPPROTO_TCP
        req['idiag_states'] = (1 << SS_ESTABLISHED)
        req['idiag_ext'] |= (1 << (INET_DIAG_INFO - 1))
        req['idiag_dport'] = dport
        result = diag_socket.nlm_request(req, SOCK_DIAG_BY_FAMILY,
                                         NLM_F_REQUEST | NLM_F_DUMP)
    return result


class AsyncScp(AsyncCommand):
    def __init__(self, command_line, semaphore, port):
        command_line = ['scp', '-P', str(port)] + command_line
        self.port = port
        AsyncCommand.__init__(self, command_line, semaphore, None)
        # Exclude already established sockets (don't take into account ssh connections or other scp)
        self.excluded_sports = [socket['idiag_sport'] for socket in get_tcp_sockets_infos(self.port)]
        self.servers = OrderedDict()
        for command in self.commands:
            for element in command:
                if ':' in element:
                    try:
                        server = element.split(':')[0]
                        ip_address = gethostbyname(server)
                        self.servers[ip_address] = {
                            'server': server,
                            'bytes_acked': 0,
                            'bytes_received': 0
                        }
                        break
                    except gaierror:
                        continue
        self.remaining_scp = len(self.servers.keys())

    def run(self):
        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(self.execute_commands())
        except (KeyboardInterrupt):
            pass
        loop.close()

    async def display_information(self):
        while self.remaining_scp > 0:
            await asyncio.sleep(3)
            os.system('clear')
            tcp_infos = get_tcp_sockets_infos(self.port)
            for tcp_info in tcp_infos:
                if tcp_info["idiag_sport"] in self.excluded_sports:
                    continue
                dst = tcp_info["idiag_dst"]
                if dst in self.servers:
                    self.servers[dst].update({
                        'bytes_acked': tcp_info.get_attr('INET_DIAG_INFO')['tcpi_bytes_acked'],
                        'bytes_received': tcp_info.get_attr('INET_DIAG_INFO')['tcpi_bytes_received']
                    })
                    for key in ('bytes_acked', 'bytes_received'):
                        for unit in HUMAN_READABLE_BYTES:
                            if self.servers[dst][key]/unit[1] > 1:
                                self.servers[dst][key] = "{0:.2f} {unit}".format(self.servers[dst][key]/unit[1],
                                                                                 unit=unit[0])
                                break
            for information in self.servers.values():
                print("{} : Bytes acked : {} Bytes received : {}".format(colored(information['server'], 'blue'),
                                                                         colored(information['bytes_acked'], 'red'),
                                                                         colored(information['bytes_received'], 'green')))

    async def execute_command(self, command):
        async with self.semaphore:
            process = await asyncio.create_subprocess_exec(*command,
                                                           stdout=asyncio.subprocess.PIPE,
                                                           stderr=asyncio.subprocess.PIPE)
            _ = await process.communicate()
            self.remaining_scp -= 1

    async def execute_commands(self):
        tasks = []
        for command in self.commands:
            tasks.append(self.execute_command(command))
        tasks.append(self.display_information())
        await asyncio.gather(*tasks)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('-s', '--semaphore', nargs='?', type=int, default=10, help="Number of scp command to execute at the same time")
    parser.add_argument('-P', '--port', nargs='?', type=int, default=22, help="Specifies the port to connect to on the remote host")
    parser.add_argument('command_line', nargs='*', type=str, help="The same syntax as scp command")
    args = parser.parse_args()
    async_scp = AsyncScp(args.command_line, args.semaphore, args.port)
    async_scp.run()
