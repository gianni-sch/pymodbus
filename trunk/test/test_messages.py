'''
TODO: Split this off into a few different fixtures, it is getting
much too big
'''
import unittest
from pymodbus.bit_read_message import *
from pymodbus.bit_read_message import ReadBitsRequestBase
from pymodbus.bit_read_message import ReadBitsResponseBase
from pymodbus.bit_write_message import *
from pymodbus.register_read_message import *
from pymodbus.register_read_message import ReadRegistersRequestBase
from pymodbus.register_read_message import ReadRegistersResponseBase
from pymodbus.register_write_message import *
from pymodbus.mexceptions import *
from pymodbus.pdu import ModbusExceptions

class Context:
    def validate(self, a,b,c):
        return False

class SimpleMessageTest(unittest.TestCase):
    '''
    This is the unittest for the pymod.bit_read_message
    '''

    def setUp(self):
        '''
        Initializes the test environment and builds request/result
        encoding pairs
        '''
        self.bread = {
            ReadBitsRequestBase(12, 14)                     : '\x00\x0c\x00\x0e',
            ReadBitsResponseBase([1,0,1,1,0])               : '\x01\x0d',
        }

        self.value = 0xabcd
        self.bwrite = {
            WriteSingleCoilRequest(1, self.value)           : '\x00\x01\xff\x00',
            WriteSingleCoilResponse(1, self.value)          : '\x00\x01\xff\x00',
            WriteMultipleCoilsRequest(1, 5)                 : '\x00\x01\x00\x05\x01\x00',
            WriteMultipleCoilsResponse(1, 5)                : '\x00\x01\x00\x05',
        }

        self.values = [0xa, 0xb, 0xc]
        self.rread = {
            ReadRegistersRequestBase(1, 5)                  :'\x00\x01\x00\x05',
            ReadRegistersResponseBase(self.values)          :'\x06\x00\x0a\x00\x0b\x00\x0c',
            ReadHoldingRegistersRequest(1, 5)               :'\x00\x01\x00\x05',
            ReadHoldingRegistersResponse(self.values)       :'\x06\x00\x0a\x00\x0b\x00\x0c',
            ReadInputRegistersRequest(1,5)                  :'\x00\x01\x00\x05',
            ReadInputRegistersResponse(self.values)         :'\x06\x00\x0a\x00\x0b\x00\x0c',
            ReadWriteMultipleRegistersRequest(1,5,1,5)      :'\x00\x01\x00\x05\x00\x01\x00'
                                                             '\x05\x0a\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00',
            ReadWriteMultipleRegistersResponse(self.values) :'\x06\x00\x0a\x00\x0b\x00\x0c',
        }

        self.rwrite = {
            WriteSingleRegisterRequest(1, self.value)       : '\x00\x01\xab\xcd',
            WriteSingleRegisterResponse(1, self.value)      : '\x00\x01\xab\xcd',
            WriteMultipleRegistersRequest(1, 5)             : '\x00\x01\x00\x05\x0a\x00\x00\x00\x00\x00\x00'
                                                              '\x00\x00\x00\x00',
            WriteMultipleRegistersResponse(1, 5)            : '\x00\x01\x00\x05',
        }



    def tearDown(self):
        ''' Cleans up the test environment '''
        del self.bread
        del self.bwrite
        del self.rread
        del self.rwrite

    def testBitReadRequests(self):
        ''' Test bit read request encoding '''
        for rqst, rsp in self.bread.iteritems():
            self.assertEqual(rqst.encode(), rsp)

    def testBitWriteRequests(self):
        ''' Test bit write request encoding '''
        for rqst, rsp in self.bwrite.iteritems():
            self.assertEqual(rqst.encode(), rsp)

    def testRegisterReadRequests(self):
        ''' Test register read request encoding '''
        for rqst, rsp in self.rread.iteritems():
            self.assertEqual(rqst.encode(), rsp)

    def testRegisterReadRequestsCountErrors(self):
        '''
        This tests that the register request messages
        will break on counts that are out of range
        '''
        requests = [
            ReadHoldingRegistersRequest(1, 0x800),
            ReadInputRegistersRequest(1,0x800),
            ReadWriteMultipleRegistersRequest(1,0x800,1,5),
            ReadWriteMultipleRegistersRequest(1,5,1,0x800),
        ]
        for request in requests:
            result = request.execute(None)
            self.assertEqual(ModbusExceptions.IllegalValue,
                result.exception_code)

    def testRegisterReadRequestsValidateErrors(self):
        '''
        This tests that the register request messages
        will break on counts that are out of range
        '''
        context = Context()
        requests = [
            ReadHoldingRegistersRequest(-1, 5),
            ReadInputRegistersRequest(-1,5),
            #ReadWriteMultipleRegistersRequest(-1,5,1,5),
            #ReadWriteMultipleRegistersRequest(1,5,-1,5),
        ]
        for request in requests:
            result = request.execute(context)
            self.assertEqual(ModbusExceptions.IllegalAddress,
                result.exception_code)

    def testRegisterWriteRequests(self):
        ''' Test register write request encoding '''
        for rqst, rsp in self.rwrite.iteritems():
            self.assertEqual(rqst.encode(), rsp)

#---------------------------------------------------------------------------#
# Main
#---------------------------------------------------------------------------#
if __name__ == "__main__":
    unittest.main()
