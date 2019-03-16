from typing import Optional
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

class DhcpPartialPacket:
    def __init__(self, initialBytes: bytes):
        self.packet: DhcpPacket = DhcpPacket()

        unpacked = DhcpPacket.codec.unpack(initialBytes)
        self.packet.opCode = unpacked[0]
        self.packet.transactionId = unpacked[4]
        self.packet.secondsElapsed = unpacked[5]
        self.packet.clientIp = unpacked[7]
        self.packet.yourIp = unpacked[8]
        self.packet.serverIp = unpacked[9]
        self.packet.clientHardwareAddr = unpacked[11]
        self.packet.messageType = MessageType(unpacked[20])

        self.__optionType: Optional[int] = unpacked[21]
        self.__optionLen: Optional[int] = None
        self.bytesNeeded: int = 0 if self.__optionType == 255 else 1

    def parseMore(self, moreBytes: bytes) -> None:
        if self.bytesNeeded == 0:
            raise ValueError('Parsing is complete')
        elif self.bytesNeeded != len(moreBytes):
            raise ValueError('Extra bytes given does not correspond with number of bytes needed')

        if self.__optionType is None:
            self.__optionType = int.from_bytes(moreBytes, 'big', signed=False)
            if self.__optionType == 255: # end options option
                self.bytesNeeded = 0
            else:
                if self.__optionType == 0: # pad option
                    self.__optionType = None
                self.bytesNeeded = 1

        elif self.__optionLen is None:
            self.__optionLen = int.from_bytes(moreBytes, 'big', signed=False)
            self.bytesNeeded = self.__optionLen

        else:
            if self.__optionType == 51:
                DhcpPacket.leaseTime = int.from_bytes(moreBytes, 'big', signed=False)
            self.__optionType = None
            self.__optionLen = None
            self.bytesNeeded = 1

class DhcpPacket:
    opCode: OpCode
    transactionId: int
    secondsElapsed: int # unsigned
    clientIp: int
    yourIp: int
    serverIp: int
    clientHardwareAddr: int
    messageType: MessageType
    leaseTime: Optional[int] # unsigned

    def __init__(self):
        leaseTime = None

    # main packet + optional header and first optional (not really opional) + type of next optional
    # uses big endianness
    # most of the fields will not be used for simplicity's sake
    codec = Struct('>4BI2H4IQ64s128s' + '4B3B' + 'B')
    __optionHeaderDhcpMagic = [0x63, 0x82, 0x53, 0x63]
    initialPacketSize = codec.size

    @staticmethod
    def fromPacket(initialBytes: bytes) -> DhcpPartialPacket:
        return DhcpPartialPacket(initialBytes)

    @staticmethod
    def fromArgs(
            opCode: OpCode,
            transactionId: int,
            secondsElapsed: int, # unsigned
            clientIp: int,
            yourIp: int,
            serverIp: int,
            clientHardwareAddr: int,
            messageType: MessageType,
            leaseTime: Optional[int] = None
        ) -> 'DhcpPacket':
        packetObj = DhcpPacket()
        packetObj.opCode = opCode
        packetObj.transactionId = transactionId
        packetObj.secondsElapsed = secondsElapsed
        packetObj.clientIp = clientIp
        packetObj.yourIp = yourIp
        packetObj.serverIp = serverIp
        packetObj.clientHardwareAddr = clientHardwareAddr
        packetObj.messageType = messageType
        packetObj.leaseTime = leaseTime
        return packetObj

    def encode(self) -> bytes:
        lastType: int = 255
        extraBytes: bytes = b''
        if self.leaseTime is not None:
            lastType = 51
            extraBytes = bytes([4]) + self.leaseTime.to_bytes(4, 'big') + bytes([255])

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
            *DhcpPacket.__optionHeaderDhcpMagic,
            53,
            1,
            self.messageType.value,
            lastType) + extraBytes
