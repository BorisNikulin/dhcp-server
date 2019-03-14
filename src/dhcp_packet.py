from enum import Enum
from struct import Struct

class OpCode(Enum):
    REQUEST = 1
    REPLY = 2

class DhcpMessageType(Enum):
    DISCOVER = 1
    OFFER = 2
    REQUEST = 3
    DECLINE = 4
    ACK = 5
    NAK = 6
    RELEASE = 7
    INFORM = 8

class DhcpPacket:
    # main packet + optional header and first optional (not really opional) + type of next optional
    # uses big endianness
    # most of the fields will not be uses for simplicity's sake
    codec = Struct('>4BI2H4IQ64s128s' + '4B3B' + 'B')
    optionHeaderDhcpMagic = [0x63, 0x82, 0x53, 0x63]
    # endOptionBin = bytes([255])

    def __init__(self, packet):
        unpacked = DhcpPacket.codec.unpack(packet)
        self.opCode = unpacked[0]
        self.transactionId = unpacked[4]
        self.secondsElapsed = unpacked[5]
        self.clientIp = unpacked[7]
        self.yourIp = unpacked[8]
        self.serverIp = unpacked[9]
        self.clientHardwareAddr = unpacked[11]
        self.messageType = DhcpMessageType(unpacked[20])

    def __init__(self, opCode, transactionId, secondsElapsed, clientIp, yourIp, serverIp, clientHardwareAddr, messageType):
        self.opCode = opCode
        self.transactionId = transactionId
        self.secondsElapsed = secondsElapsed
        self.clientIp = clientIp
        self.yourIp = yourIp
        self.serverIp = serverIp
        self.clientHardwareAddr = clientHardwareAddr
        self.messageType = messageType

    def encode(self):
        return DhcpPacket.codec.pack(
            self.opCode.value,
            1, # ethernet hardware type
            6, # 6 byte hardware addresses (mac)
            0,
            self.transactionId,
            self.secondsElapsed,
            1 << 15, # server will reply via broadcasts
            self.clientIp,
            self.yourIp,
            self.serverIp,
            0, # gateway ip
            self.clientHardwareAddr,
            b'', # servername
            b'', # boot filename
            *DhcpPacket.optionHeaderDhcpMagic,
            53,
            1,
            self.messageType.value,
            255)
