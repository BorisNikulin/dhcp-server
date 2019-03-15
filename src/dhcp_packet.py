from enum import Enum
from struct import Struct

class OpCode(Enum):
    REQUEST = 1
    REPLY = 2

class MessageType(Enum):
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

    def __init__(self):
        self.opCode = None
        self.transactionId = None
        self.secondsElapsed = None
        self.clientIp = None
        self.yourIp = None
        self.serverIp = None
        self.clientHardwareAddr = None
        self.messageType = None


    @staticmethod
    def fromPacket(packet: bytes) -> DhcpPacket:
        packetObj = DhcpPacket()
        unpacked = DhcpPacket.codec.unpack(packet)
        packetObj.opCode = unpacked[0]
        packetObj.transactionId = unpacked[4]
        packetObj.secondsElapsed = unpacked[5]
        packetObj.clientIp = unpacked[7]
        packetObj.yourIp = unpacked[8]
        packetObj.serverIp = unpacked[9]
        packetObj.clientHardwareAddr = unpacked[11]
        packetObj.messageType = MessageType(unpacked[20])
        return packetObj

    @staticmethod
    def fromArgs(
            opCode: OpCode,
            transactionId: int,
            secondsElapsed: int, # unsigned
            clientIp: int,
            yourIp: int,
            serverIp: int,
            clientHardwareAddr: int,
            messageType: MessageType) -> DhcpPacket:
        packetObj = DhcpPacket()
        packetObj.opCode = opCode
        packetObj.transactionId = transactionId
        packetObj.secondsElapsed = secondsElapsed
        packetObj.clientIp = clientIp
        packetObj.yourIp = yourIp
        packetObj.serverIp = serverIp
        packetObj.clientHardwareAddr = clientHardwareAddr
        packetObj.messageType = messageType
        return packetObj

    def encode(self) -> bytes:
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
