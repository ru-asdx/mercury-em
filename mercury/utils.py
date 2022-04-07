# -*- coding: utf-8 -*-

from typing import Union, Sequence

def digitize(byte_string, base=10) -> int:
    r"""
    >>> digitize(b'\x00\x12\x34')
    1234
    """
    str_num = ''.join(upper_hex(b) for b in byte_string)
    return int(str_num, base)


def upper_hex(byte: Union[str, bytes, int]) -> str:
    r"""
    >>> upper_hex('\x00')
    '00'
    >>> upper_hex(0x0)
    '00'
    >>> upper_hex(5)
    '05'
    >>> upper_hex(b'\x01')
    '01'
    >>> upper_hex('')
    Traceback (most recent call last):
    ...
    ValueError: expected single byte
    >>> upper_hex(b'')
    Traceback (most recent call last):
    ...
    ValueError: expected single byte
    >>> upper_hex('\x00\x01')
    Traceback (most recent call last):
    ...
    ValueError: expected single byte
    >>> upper_hex(b'\x00\x01')
    Traceback (most recent call last):
    ...
    ValueError: expected single byte
    """
    if isinstance(byte, (str, bytes)):
        if len(byte) != 1:
            raise ValueError('expected single byte')
        if isinstance(byte, str):
            byte = ord(byte)
        elif isinstance(byte, bytes):
            byte = byte[0]
    return '%02X' % byte


def pretty_hex(byte_string) -> str:
    r"""
    >>> pretty_hex('Python')
    '50 79 74 68 6F 6E'
    >>> pretty_hex('\x00\xa1\xb2')
    '00 A1 B2'
    >>> pretty_hex([1, 2, 3, 5, 8, 13])
    '01 02 03 05 08 0D'
    """
    return ' '.join(upper_hex(c) for c in byte_string)
