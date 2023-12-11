# hypshell
A simple reverse shell handler and stabilizer
# Usage
`usage: ./hypshell.py [options] port`

**NOTE: To exit the program you have to enter "exit" on the shell session even if you can't read the input**
### Examples:
Start a reverse shell listener on port 4242 and start an alternative screen:

`hypshell.py 4242`

Handle `^\` to exit the program:

`hypshell.py 4242 -q`

Use connect mode and verbose

`hypshell.py 4242 -vx 127.0.0.1`

Set shell to `/bin/sh` and use python3 PTY stabilization method

`hypshell.py 4242 -s /bin/sh -m python3`

# Options
```
options:
  -h, --help            show this help message and exit
  -m method, --method method
                        Stabilize the connection using the specified method (default: script)
  -v, --verbose         Verbose mode
  -i interface, --interface interface
                        Specify the network interface to use
  -n, --normal          Use normal mode instead of alternate screen
  -c, --stabilize       Do not stabilize the connection
  -e, --echo            echo input
  -s shell, --shell shell
                        Specify the full path of the shell to use (default: /bin/bash)
  -t, --sigint          Handle SIGINT signal
  -r, --sigterm         Handle SIGTERM signal
  -q, --sigquit         Handle SIGQUIT signal
  -x address, --connect address
                        connect to specified address instead of bind
```
# Built-in Methods
Feel free to append your own methods to the code.
```
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
