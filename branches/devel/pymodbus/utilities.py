'''
Modbus Utilities
-----------------

A collection of utilities for packing data, unpacking
data computing checksums, and decode checksums.
'''

def packBitsToString(bits):
    ''' Creates a string out of an array of bits

    :param bits: A bit array

    example::

        bits = [False, True, False, True]
        result = packBitsToString(bits)
    '''
    ret = ''
    i = packed = 0
    for bit in bits:
        if bit: packed += 128
        i += 1
        if i == 8:
            ret += chr(packed)
            i = packed = 0
        else: packed >>= 1
    if i > 0 and i < 8:
        packed >>= 7-i
        ret += chr(packed)
    return ret

def unpackBitsFromString(string):
    ''' Creates bit array out of a string

    :param string: The modbus data packet to decode

    example::

        string[0]   = bytes to follow
        string[1-N] = bytes to decode
    '''
    byte_count = ord(string[0])
    bits = []
    for byte in range(1, byte_count+1):
        value = ord(string[byte])
        for bit in range(8):
            bits.append((value & 1) == 1)
            value >>= 1
    return bits, byte_count

#---------------------------------------------------------------------------#
# Error Detection Functions
#---------------------------------------------------------------------------#
def __generate_crc16_table():
    ''' Generates a crc16 lookup table

    .. note:: This will only be generated once
    '''
    result = []
    for byte in range(256):
        crc = 0x0000
        for bit in range(8):
            if (byte ^ crc) & 0x0001: crc = (crc >> 1) ^ 0xa001
            else: crc >>= 1
            byte >>= 1
        result.append(crc)
    return result

__crc16_table = __generate_crc16_table()

def computeCRC(data):
    ''' Computes a crc16 on the passed in data.

    The difference between modbus's crc16 and a normal crc16
    is that modbus starts the crc value out at 0xffff.

    example::

        return computeCRC(input) == 0x1234

    .. note:: This accepts a string or a integer list

    :param data: The data to create a crc16 of
    '''
    crc = 0xffff
    pre = lambda x: x
    if isinstance(data, str): pre = lambda x: ord(x)

    for a in data: crc = ((crc >> 8) & 0xff) ^ __crc16_table[
            (crc ^ pre(a)) & 0xff];
    return crc

def checkCRC(data, check):
    ''' Checks if the data matches the passed in CRC

    example::

        return checkCRC(input, 0x1234)

    :param data: The data to create a crc16 of
    :param check: The CRC to validate
    '''
    return computeCRC(data) == check

def computeLRC(data):
    ''' Wrapper to computer LRC of multiple types of data

    .. note:: This accepts a string or a integer list

    example::

        return computeLRC(input) == 2

    :param data: The data to apply a lrc to

    '''
    if isinstance(data, str): data = ascii2hex(data)

    lrc = sum(data)
    return 0x100 - lrc

def checkLRC(data, check):
    ''' Checks if the passed in data matches the LRC

    example::

        return checkLRC(input, 2)

    :param data: The data to calculate
    :param check: The LRC to validate
    '''
    return computeLRC(data) == check

def a2h(a):
    '''
    Converts ascii chars to hex values:

        "0" -> 0
        "1" -> 1
        "f" -> 15
        "F" -> 15

    :param a: the char to be converted
    '''
    o = ord(a)
    if 47 < o < 58:
        return ord(a) - 48
    else:
        A = a.upper()
        O = ord(A)
        if 64 < O < 71:
            return O - 55
        else:
            raise ValueError("ASCII value out of hex range.")

def ascii2hex(buffer):
    '''
    Take chars by pairs and create an hex value from them.
    Return a list with the resulting values.
    Used to decode Modbus ASCII packets.

    :param buffer: the string from an ascii modbus device
                   without ':' and '\\r\\n'
    :return a list of values.
    '''
    i = iter(buffer)
    out = []
    for x, y in zip(i, i):
        x, y = a2h(x), a2h(y)
        out.append(x << 4 | y)
    return out
#---------------------------------------------------------------------------#
# Exported symbols
#---------------------------------------------------------------------------#
__all__ = [
        'packBitsToString', 'unpackBitsFromString',
        'computeCRC', 'checkCRC', 'computeLRC', 'checkLRC', 'ascii2hex'
]
