'''
Diagnostic record read/write

Currently not all implemented
'''
import struct
from pymodbus.constants import ModbusStatus
from pymodbus.pdu import ModbusRequest
from pymodbus.pdu import ModbusResponse
from pymodbus.device import ModbusControlBlock
from pymodbus.exceptions import *

_MCB = ModbusControlBlock()

#---------------------------------------------------------------------------#
# TODO Make these only work on serial
#---------------------------------------------------------------------------#
class ReadExceptionStatusRequest(ModbusRequest):
    '''
    This function code is used to read the contents of eight Exception Status
    outputs in a remote device.  The function provides a simple method for
    accessing this information, because the Exception Output references are
    known (no output reference is needed in the function).
    '''
    function_code = 0x07

    def __init__(self):
        ''' Initializes a new instance
        '''
        ModbusRequest.__init__(self)

    def encode(self):
        ''' Encodes the message
        '''
        return ''

    def decode(self, data):
        ''' Decodes data part of the message.

        :param data: The incoming data
        '''
        pass

    def execute(self):
        ''' Run a read exeception status request against the store

        :returns: The populated response
        '''
        status = _MCB.Counter.summary()
        return ReadExceptionStatusResponse(status)

    def __str__(self):
        ''' Builds a representation of the request

        :returns: The string representation of the request
        '''
        return "ReadExceptionStatusRequest(%d)" % (self.function_code)

class ReadExceptionStatusResponse(ModbusResponse):
    '''
    The normal response contains the status of the eight Exception Status
    outputs. The outputs are packed into one data byte, with one bit
    per output. The status of the lowest output reference is contained
    in the least significant bit of the byte.  The contents of the eight
    Exception Status outputs are device specific.
    '''
    function_code = 0x07

    def __init__(self, status):
        ''' Initializes a new instance

        :param status: The status response to report
        '''
        ModbusRequest.__init__(self)
        self.status = status

    def encode(self):
        ''' Encodes the response

        :returns: The byte encoded message
        '''
        return struct.pack('>B', self.status)

    def decode(self, data):
        ''' Decodes a the response

        :param data: The packet data to decode
        '''
        self.status = struct.unpack('>B', data)

    def __str__(self):
        ''' Builds a representation of the response

        :returns: The string representation of the response
        '''
        arguments = (self.function_code, self.status)
        return "ReadExceptionStatusResponse(%d, %s)" % arguments


# Encapsulate interface transport 43, 14
# CANopen general reference 43, 13

#---------------------------------------------------------------------------#
# TODO Make these only work on serial
#---------------------------------------------------------------------------#
class GetCommEventCounterRequest(ModbusRequest):
    '''
    This function code is used to get a status word and an event count from the
    remote device's communication event counter. 

    By fetching the current count before and after a series of messages, a client
    can determine whether the messages were handled normally by the remote device. 

    The device's event counter is incremented once  for each successful message
    completion. It is not incremented for exception responses, poll commands,
    or fetch event counter commands. 

    The event counter can be reset by means of the Diagnostics function (code 08),
    with a subfunction of Restart Communications Option (code 00 01) or
    Clear Counters and Diagnostic Register (code 00 0A).
    '''
    function_code = 0x0b

    def __init__(self):
        ''' Initializes a new instance
        '''
        ModbusRequest.__init__(self)

    def encode(self):
        ''' Encodes the message
        '''
        return ''

    def decode(self, data):
        ''' Decodes data part of the message.

        :param data: The incoming data
        '''
        pass

    def execute(self):
        ''' Run a read exeception status request against the store

        :returns: The populated response
        '''
        status = _MCB.Counter.Event
        return GetCommEventCounterResponseResponse(status)

    def __str__(self):
        ''' Builds a representation of the request

        :returns: The string representation of the request
        '''
        return "GetCommEventCounterRequest(%d)" % (self.function_code)

class GetCommEventCounterResponse(ModbusResponse):
    '''
    The normal response contains a two-byte status word, and a two-byte
    event count. The status word will be all ones (FF FF hex) if a
    previously-issued program command is still being processed by the remote
    device (a busy condition exists). Otherwise, the status word will be 
    all zeros.
    '''
    function_code = 0x0b

    def __init__(self, count):
        ''' Initializes a new instance

        :param count: The current event counter value
        '''
        ModbusRequest.__init__(self)
        self.count = count
        self.status = True # this means we are ready, not waiting

    def encode(self):
        ''' Encodes the response

        :returns: The byte encoded message
        '''
        ready = ModbusStatus.Ready if self.status else ModbusStatus.Waiting
        return struct.pack('>HH', ready, self.count)

    def decode(self, data):
        ''' Decodes a the response

        :param data: The packet data to decode
        '''
        ready, self.count = struct.unpack('>HH', data)
        self.status = (ready == ModbusStatus.Ready)

    def __str__(self):
        ''' Builds a representation of the response

        :returns: The string representation of the response
        '''
        arguments = (self.function_code, self.count, self.status)
        return "GetCommEventCounterResponse(%d, %d, %d)" % arguments

#---------------------------------------------------------------------------#
# TODO Make these only work on serial
#---------------------------------------------------------------------------#
class GetCommEventLogRequest(ModbusRequest):
    '''
    This function code is used to get a status word, event count, message count,
    and a field of event bytes from the remote device. 

    The status word and event counts are identical  to that returned by the
    Get Communications Event Counter function (11, 0B hex). 

    The message counter contains the quantity of  messages processed by the
    remote device since its last restart, clear counters operation, or power-up.
    This count is identical to that returned by the Diagnostic function
    (code 08), sub-function Return Bus Message Count (code 11, 0B hex). 

    The event bytes field contains 0-64 bytes, with each byte corresponding to
    the status of one MODBUS send or receive operation for the remote device.
    The remote device enters the events into the field in chronological order.
    Byte 0 is the most recent event. Each new byte flushes the oldest byte
    from the field.
    '''
    function_code = 0x0c

    def __init__(self):
        ''' Initializes a new instance
        '''
        ModbusRequest.__init__(self)

    def encode(self):
        ''' Encodes the message
        '''
        return ''

    def decode(self, data):
        ''' Decodes data part of the message.

        :param data: The incoming data
        '''
        pass

    def execute(self):
        ''' Run a read exeception status request against the store

        :returns: The populated response
        '''
        results = {
            'status'        : True,
            'message_count' : _MCB.Counter.BusMessage,
            'event_count'   : _MCB.Counter.Event,
            'events'        : _MCB.getEvents(),
        }
        return GetCommEventLogResponse(**results)

    def __str__(self):
        ''' Builds a representation of the request

        :returns: The string representation of the request
        '''
        return "GetCommEventLogRequest(%d)" % self.function_code

class GetCommEventLogResponse(ModbusResponse):
    '''
    The normal response contains a two-byte status word field,
    a two-byte event count field, a two-byte message count field,
    and a field containing 0-64 bytes of events. A byte count field 
    defines the total length of the data in these four field
    '''
    function_code = 0x0c

    def __init__(self, **kwargs):
        ''' Initializes a new instance

        :param status: The status response to report
        :param message_count: The current message count
        :param event_count: The current event count
        :param events: The collection of events to send
        '''
        ModbusRequest.__init__(self)
        self.status = kwargs.get('status', True)
        self.message_count = kwargs.get('message_count', 0)
        self.event_count = kwargs.get('event_count', 0)
        self.events = kwargs.get('events', [])

    def encode(self):
        ''' Encodes the response

        :returns: The byte encoded message
        '''
        ready = ModbusStatus.Ready if self.status else ModbusStatus.Waiting
        packet  = struct.pack('>B', 6 + len(self.events))
        packet += struct.pack('>H', ready)
        packet += struct.pack('>HH', self.event_count, self.message_count)
        packet += ''.join(struct.pack('>B', e) for e in self.events)
        return packet

    def decode(self, data):
        ''' Decodes a the response

        :param data: The packet data to decode
        '''
        length = struct.unpack('>B', data[0])
        status = struct.unpack('>H', data[1:2])
        self.status = (status == ModbusStats.Ready)
        self.event_count = struct.unpack('>H', data[3:4])
        self.message_count = struct.unpack('>H', data[5:6])

        self.events = []
        for e in xrange(6, length):
            self.events.append(struct.unpack('>B', data[6 + e]))

    def __str__(self):
        ''' Builds a representation of the response

        :returns: The string representation of the response
        '''
        arguments = (self.function_code, self.status, self.message_count, self.event_count)
        return "GetCommEventLogResponse(%d, %d, %d, %d)" % arguments

#---------------------------------------------------------------------------#
# TODO Make these only work on serial
#---------------------------------------------------------------------------#
class ReportSlaveIdRequest(ModbusRequest):
    '''
    This function code is used to read the description of the type, the current
    status, and other information specific to a remote device. 
    '''
    function_code = 0x11

    def __init__(self):
        ''' Initializes a new instance
        '''
        ModbusRequest.__init__(self)

    def encode(self):
        ''' Encodes the message
        '''
        return ''

    def decode(self, data):
        ''' Decodes data part of the message.

        :param data: The incoming data
        '''
        pass

    def execute(self):
        ''' Run a read exeception status request against the store

        :returns: The populated response
        '''
        status = _MCB.getCounterSummary()
        return ReportSlaveIdResponse(status)

    def __str__(self):
        ''' Builds a representation of the request

        :returns: The string representation of the request
        '''
        return "ResportSlaveIdRequest(%d)" % self.function_code

class ReportSlaveIdResponse(ModbusResponse):
    '''
    The format of a normal response is shown in the following example. The
    data contents are specific to each type of device.
    '''
    function_code = 0x11

    def __init__(self, identifier, status=True):
        ''' Initializes a new instance

        :param identifier: The identifier of the slave
        :param status: The status response to report
        '''
        ModbusRequest.__init__(self)
        self.identifier = identifier
        self.status = status

    def encode(self):
        ''' Encodes the response

        :returns: The byte encoded message
        '''
        status = 0xFF if self.status else 0x00
        return struct.pack('>BBB', 0x03, self.identifier, self.status)

    def decode(self, data):
        ''' Decodes a the response

        :param data: The packet data to decode
        '''
        length, self.identifier, status = struct.unpack('>BBB', data)
        self.status = status == 0xFF

    def __str__(self):
        ''' Builds a representation of the response

        :returns: The string representation of the response
        '''
        arguments = (self.function_code, self.identifier, self.status)
        return "ResportSlaveIdResponse(%d, %d, %d)" % arguments

#---------------------------------------------------------------------------#
# TODO Make these only work on serial
#---------------------------------------------------------------------------#
# report device identification 43, 14

#---------------------------------------------------------------------------# 
# Exported symbols
#---------------------------------------------------------------------------# 
__all__ = [
    "ReadExceptionStatusRequest", "ReadExceptionStatusResponse",
    "ReportSlaveIdRequest", "ReportSlaveIdResponse",
]
