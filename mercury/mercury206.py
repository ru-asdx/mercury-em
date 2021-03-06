# -*- coding: utf-8 -*-

from minimalmodbus import _calculate_crc_string as modbus_crc

from struct import pack, unpack
from typing import Union, Sequence
from .utils import digitize


def read_vap(s, address_mercury, cmd=0x63):
    ''' Read Voltage (V), Amperage (A), Power (kW/h) '''

    data = send_tcp_command(s, address_mercury, cmd)

    v = digitize(data[1:3]) / 10
    a = digitize(data[3:5]) / 100
    p = digitize(data[5:8])

    return v, a, p


def read_energy(s, address_mercury, cmd=0x27, *args):
    ''' Возвращает список показаний потреблённой энергии в кВт/ч по 4 тарифам
        с момента последнего сброса '''

    data = send_tcp_command(s, address_mercury, cmd, *args)

    result = {}
    for i in range(1, 17, 4):
        result['A+_T' + str(i // 4 + 1)] = digitize(data[i:i+4]) / 100

    result['A+sum'] = round(sum(result.values()),2)
    return result


def read_freq(s, address_mercury, cmd=0x81, *args):
    ''' Чтение доп. параметров сети (частота)'''

    data = send_tcp_command(s, address_mercury, cmd, *args)
    return digitize(data[1:3]) / 100




ADDRESS_FMT = '!I'  # unsigned integer in network order

def read_data_from_socket(s):
    data = ''
    buffer = b""

    while not data:
        s.settimeout(1)
        data = s.recv(1024)
        if data:
            buffer += data

    s.settimeout(None)
    return buffer


def send_tcp_command(s, address_mercury, command, *params, **kwargs):
    message = pack_msg(address_mercury, command, *params, crc=kwargs.get('crc', True))
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
        if len(address) > 4:
            raise ValueError('address length exceeds 4 bytes')
        pad_len = 4 - len(address)
        address = b'\x00' * pad_len + address
    else:
        raise TypeError('address must be an integer or bytes')

    params = bytes(args)
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
    address = unpack(ADDRESS_FMT, message[:4])[0]
    data = list(message[4:])
    return address, data
