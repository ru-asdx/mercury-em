# mercury-em

Receiving information from Mercury energymeters (RS485 over TCP/IP)

Official documentation on protocols used in Mercury energymeters:
* [Official site Incotex](https://www.incotexcom.ru/support/docs/protocol)
* [Protocol for single-phase Mercury energymeters 200, 201, 203 (except Mercury 203.2TD), 206. version 01.04.2018](https://www.incotexcom.ru/files/em/docs/mercury-protocol-obmena-1.pdf)
* [Protocol for three-phase Mercury energymeters 203.2TD, 204, 208, 230, 231, 234, 236, 238 version 12.12.2022](https://www.incotexcom.ru/files/em/docs/merkuriy-sistema-komand-ver-1-2022-12-12.pdf)

# Installation

Use venv

    $ git clone https://github.com/ru-asdx/mercury-em
    $ cd mercury-em
    $ python3.9 -m venv .env
    $ source .env/bin/activate

Install dependencies
```
$ pip install -r requirements.txt
```

Use it
```
$ ./mercury-em.py --proto m206 --serial 12345678 --host 192.168.1.100 --port 50 --format json
$ ./mercury-em.py --proto m236 --serial 12345678 --host 192.168.1.100 --port 50 --user admin --pass 222222 --format json
```

# Usage
```
$ ./mercury-em.py -h

Mercury energy meter data receiver

optional arguments:
   --proto [{m206,m236}]             Used protocol (M206/M236)
   --serial [SERIAL]                 Serial number of energymeter
   --host [HOST]                     RS485-TCP/IP converter ip-address
   --port [PORT]                     RS485-TCP/IP converter port
   --user [{user,admin}]             Access level (User/Admin) (only for m236 protocol)
   --pass [PASSWD]                   Access password (only for m236 protocol)
   --format [{text,json}]            Output format
```
