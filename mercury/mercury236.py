# -*- coding: utf-8 -*-

from minimalmodbus import _calculate_crc_string as modbus_crc

from struct import pack, unpack
from typing import Union, Sequence
from .utils import digitize

def read_vap(s, address_mercury, cmd=0x08):
    ''' Read Voltage (V), Amperage (A), Power (kW/h)

    0x8 - код запроса
    x11, x14, x16 - код параметра
    bwri
    '''

    data = send_tcp_command(s, address_mercury, cmd, 0x16, 0x11)
    headers = ['V_F1', 'V_F2', 'V_F3']
    result = {}

    for r in headers:
        result[r] = digitize( bytes([data[0], data[2], data[1]]), 16 ) / 100
        data = data[3:]

    data = send_tcp_command(s, address_mercury, cmd, 0x16, 0x00)
    headers = ['Psum', 'P_F1', 'P_F2', 'P_F3']

    for r in headers:
        result[r] = digitize( bytes([data[2], data[1]]), 16 )/100
        data = data[3:]

    data = send_tcp_command(s, address_mercury, cmd, 0x16, 0x21)

    headers = ['A_F1', 'A_F2', 'A_F3']
    for r in headers:
        result[r] = digitize( bytes([data[0], data[2], data[1]]), 16 )/1000
        data = data[3:]

    return result



def read_energy(s, address_mercury, cmd=0x05, param=0x00, tarif=0x00, *args):
    ''' 
    cmd      0x05 - чтение активной и реактивной энергии
    param    0x00 - от сброса (0x60 - пофазные значения учтенной активной энергии прямого направления)
    tarif    0x00 - по сумме (0x1 - тариф 1, 0х2 - тариф 2, 0x3 - тариф 3, 0x4 - тариф 4)
    '''

    data = send_tcp_command(s, address_mercury, cmd, param, tarif)

    headers = ['A+_F1', 'A+_F2', 'A+_F3'] if param == 0x60 else ['A+', 'A-', 'R+', 'R-']
    suffix = "sum" if tarif == 0x0 else '_T'+str(tarif)

    result = {}
    for r in headers:
        result[r+suffix] = digitize( bytes([data[1], data[0], data[3], data[2]]), 16 )/1000
        data = data[4:]

    if 'A-'+suffix in result:
        result['A-'+suffix] = 0

    return result


def read_energy_sum_act_react(s, address_mercury, cmd=0x05, param=0x00):
    result =  read_energy(s, address_mercury, cmd=0x05, param=0x00, tarif=0x0)
    return result


def read_energy_tarif_act_react(s, address_mercury, cmd=0x05, param=0x00):
    result = {}
    for i in range(1,5):
        r = read_energy(s, address_mercury, cmd=0x05, param=0x00, tarif=i)
        result = {**result, **r}

    return result


def read_energy_sum_by_phases(s, address_mercury, cmd=0x05, param=0x60, tarif=0x0):
    result =  read_energy(s, address_mercury, cmd=0x05, param=0x60, tarif=0x0)
    return result


def read_energy_tarif_by_phases(s, address_mercury, cmd=0x05, param=0x60, tarif=0x0):
    result = {}
    for i in range(1,5):
        r = read_energy(s, address_mercury, cmd=0x05, param=0x60, tarif=i)
        result = {**result, **r}

    return result




def read_freq(s, address_mercury, cmd=0x08):
    data = send_tcp_command(s, address_mercury, cmd, 0x16, 0x40)
    return digitize( bytes([data[0], data[2], data[1]]), 16 )/100




def check_connect(s, address_mercury, cmd=0x00, *args):
    #print (f"check_connect....")
    data = send_tcp_command(s, address_mercury, cmd, *args)
    #print (pretty_hex(data))

def open_channel(s, address_mercury, user=0x1, passwd="1111111", cmd=0x01, *args):
    #print (f"open channel...")
    # 0x01 - open channel, (0x01 - user mode | 0x02 - admin mode)
    data = send_tcp_command(s, address_mercury, 0x01, user, passwd=passwd)
    #print (pretty_hex(data))

def close_channel(s, address_mercury, cmd=0x02, *args):
    #print (f"close channel...")
    # 0x02 - close channel
    data = send_tcp_command(s, address_mercury, 0x02)
    #print (pretty_hex(data))




ADDRESS_FMT = '!B'  # unsigned char (integer 1 byte in network order)

def read_data_from_socket(s):
    data = ''
    buffer = b""

    while not data:
        s.settimeout(1)
        data = s.recv(1000)
        if data:
            buffer += data

    s.settimeout(None)
    return buffer

def send_tcp_command(s, address_mercury, command, *params, **kwargs):

    message = pack_msg(address_mercury, command, *params, passwd=kwargs.get('passwd',''), crc=kwargs.get('crc', True))
    s.sendall(message)

    answer = read_data_from_socket(s)
    #answer_lines = answer.split('\r\n')
    #answer = ''.join(answer_lines)

    if len(answer) > 1:
        received_address, received_data = unpack_msg(answer)
        if received_address == address_mercury:
            return received_data

    raise ValueError(f"Error while read data from socket")


def pack_msg(address: Union[int, bytes], *args: Sequence[int], **kwargs) -> bytes:
    r"""Pack power meter address and args into string,
    add modbus CRC by default
    Keyword Arguments:
    - crc: optional bool, True by default, controls addition of CRC
    Return string with bytes
    >>> from .utils import pretty_hex
    >>> pretty_hex(pack_msg(10925856, 0x28))
    '00 A6 B7 20 28 AF 70'
    >>> pretty_hex(pack_msg(10925856, 0x28, crc=False))
    '00 A6 B7 20 28'
    >>> pretty_hex(pack_msg(10925856, 0x2b))
    '00 A6 B7 20 2B EF 71'
    >>> pretty_hex(pack_msg(b'123'))
    '00 31 32 33 04 9E'
    >>> pack_msg('123')
    Traceback (most recent call last):
        ...
    TypeError: address must be an integer or bytes
    >>> pack_msg(b'12345')
    Traceback (most recent call last):
        ...
    ValueError: address length exceeds 4 bytes
    """
    if isinstance(address, int):
        address = pack(ADDRESS_FMT, address)
    elif isinstance(address, bytes):
        if len(address) > 1:
            raise ValueError('address length exceeds 1 bytes')
    else:
        raise TypeError('address must be an integer or bytes')

    #print (f"args: {args}")
    params = bytes(args)

    #print (f"address: {address}, params: {params}")

    if kwargs.get('passwd'):
        passwd = bytes([ int(c) for c in kwargs.get('passwd') ])
        msg = (address + params + passwd).decode('latin1')
    else:
        msg = (address + params).decode('latin1')

    if kwargs.get('crc', True):
        msg += modbus_crc(msg)

    return msg.encode('latin1')


def unpack_msg(message: bytes):
    r"""Unpack message string.
    Assume the first 4 bytes carry power meter address
    Return tuple with: integer power meter address and list of bytes
    >>> unpack_msg(b'\x00\xA6\xB7\x20\x28')
    (10925856, [40])
    >>> unpack_msg(b'\x00\xA6\xB7\x20\x27\x00\x26\x56\x16\x00\x13\x70\x91\x00\x00\x00\x00\x00\x00\x00\x00\x47\x78')
    (10925856, [39, 0, 38, 86, 22, 0, 19, 112, 145, 0, 0, 0, 0, 0, 0, 0, 0, 71, 120])
    >>> unpack_msg(b'\x00\xA6\xB7\x20')
    (10925856, [])
    """
    address = unpack(ADDRESS_FMT, message[:1])[0]
    data = list(message[1:])
    return address, data
