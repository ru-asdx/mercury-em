# mercury-em

Получаем показания со счетчиков Меркурий (RS485 over TCP/IP)

Официальная документация по протоколам обмена используемых в счетчиках Меркурий
* [Официальный сайт Incotex](https://www.incotexcom.ru/support/docs/protocol)
* [Протокол обмена однофазных счетчиков Меркурий 200, 201, 203 (кроме Меркурий 203.2TD), 206. версия от 01.04.2018](https://www.incotexcom.ru/files/em/docs/mercury-protocol-obmena-1.pdf)
* [Протокол обмена трёхфазных счетчиков Меркурий (Mercury) 203.2TD, 204, 208, 230, 231, 234, 236, 238 версия от 12.12.2022](https://www.incotexcom.ru/files/em/docs/merkuriy-sistema-komand-ver-1-2022-12-12.pdf)

# Installation

Use venv

    $ git clone https://github.com/ru-asdx/mercury-em
    $ cd mercury-em
    $ python3.9 -m venv .env
    $ source .env/bin/activate

Install dependencies

    $ pip install -r requirements.txt

Use it

    $ ./mercury-em.py --proto m206 --serial 12345678 --host 192.168.1.100 --port 50 --format json

# Usage
```
$ ./mercury-em.py -h
    
Mercury energy meter data receiver
  
optional arguments:
   --proto [{m206,m236}]             Используемый протокол (M206/M236)
   --serial [SERIAL]                 Серийный номер счетчика
   --host [HOST]                     IP адрес конвертора RS485-TCP/IP
   --port [PORT]                     Порт конвертора RS485-TCP/IP
   --user [{user,admin}]             Уровень доступа (User/Admin) (только для счетчиков по протоколу М236)
   --pass [PASSWD]                   Пароль доступа (только для счетчиков по протоколу М236)
   --format [{text,json}]            Формат вывода
```

