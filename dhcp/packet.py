from typing import Optional
from enum import Enum
from struct import Struct
from ipaddress import IPv4Address


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
    """Class for representing partially parsed DHCP packets.

    All parsing is based on big endian.

    Since DHCP options are variable width,
    DHCP packets must look at the options to determine how much more to parse.

    This class uses self.bytesNeeded to indicate how many more bytes
    to feed to self.parseMore().
    when self.bytesNeeded is 0, parsing is finished.
    The complete packet can be accessed at self.packet
    """

    def __init__(self, initialBytes: bytes):
        """Construct the packet with the initial fixed sized segment of the packet.

        The fixed sized of the packet is considered to be
        from the begining to the to first option,
        which must be option 53 or message type,
        and then the option type of the second option.

        This means that on top of initial non optional segment,
        the 4 byte option header magic cookie is needed,
        as well as the byte for the length of the message type, which is 1,
        The byte for the actual message type,
        and lastly the byte for next option type.
        """

        self.packet: DhcpPacket = DhcpPacket()
        self.packet.leaseTime = None

        unpacked = DhcpPacket.codec.unpack(initialBytes)
        self.packet.opCode = unpacked[0]
        self.packet.transactionId = unpacked[4]
        self.packet.secondsElapsed = unpacked[5]
        self.packet.clientIp = IPv4Address(unpacked[7])
        self.packet.yourIp = IPv4Address(unpacked[8])
        self.packet.serverIp = IPv4Address(unpacked[9])
        # mask out unneeded bits of the client hardware address
        # using the hardware address length in bytes
        self.packet.clientHardwareAddr = unpacked[11]
        self.packet.messageType = MessageType(unpacked[20])

        self.__optionType: Optional[int] = unpacked[21]
        self.__optionLen: Optional[int] = None
        self.bytesNeeded: int = 0 if self.__optionType == 255 else 1

    def parseMore(self, moreBytes: bytes) -> None:
        """Parse the moreBytes of length self.bytesNeeded.

        The number of bytes given must be exactly equal to self.bytesNeeded
        and not 0 otherwise a ValueError will be raised.
        This means when self.bytesNeeded is 0, parsing has concluded,
        and calling this method will raise a ValueError.

        The fully parsed packet is available at self.packet

        The only options suported are
            * 0: pad byte (ignored)
            * 51: Lease Time
            * 255: end of options
        All other options are ignored and skipped.

        Option 53, message type, is parsed in the constructor
        Thus is always the first option and always included.
        """
        # TODO?: move option 53, message type, parsing to this method

        if self.bytesNeeded == 0:
            raise ValueError('Parsing is complete')
        elif self.bytesNeeded != len(moreBytes):
            raise ValueError(
                'Extra bytes given does not correspond '
                'with number of bytes needed')

        if self.__optionType is None:
            self.__optionType = int.from_bytes(moreBytes, 'big', signed=False)
            if self.__optionType == 255:  # end options option
                self.bytesNeeded = 0
            else:
                if self.__optionType == 0:  # pad option
                    self.__optionType = None
                self.bytesNeeded = 1

        elif self.__optionLen is None:
            self.__optionLen = int.from_bytes(moreBytes, 'big', signed=False)
            self.bytesNeeded = self.__optionLen

        else:
            if self.__optionType == 51:
                self.packet.leaseTime = int.from_bytes(
                    moreBytes, 'big', signed=False)
            self.__optionType = None
            self.__optionLen = None
            self.bytesNeeded = 1


class DhcpPacket:
    """DHCP packet that requires option 53, message type,
    and optionally option 51, lease time"""

    opCode: OpCode
    transactionId: int
    secondsElapsed: int  # unsigned
    clientIp: IPv4Address
    yourIp: IPv4Address
    serverIp: IPv4Address
    clientHardwareAddr: int
    messageType: MessageType
    leaseTime: Optional[int]  # unsigned

    # main packet + optional header and first optional (not really opional)
    # + type of next optional
    # uses big endianness
    # most of the fields will not be used for simplicity's sake
    codec = Struct('=4BI2H4IQ64s128s' + '4B3B' + 'B')
    __optionHeaderDhcpMagic = [0x63, 0x82, 0x53, 0x63]
    initialPacketSize = codec.size

    @staticmethod
    def fromPacket(initialBytes: bytes) -> DhcpPartialPacket:
        """Begin parsing variable width DHCP packet with always required bytes.

        See DhcpPartialPacket.__init__() for detailed info
        on what constitues the initial bytes.
        """

        return DhcpPartialPacket(initialBytes)

    @staticmethod
    def fromArgs(
            opCode: OpCode,
            transactionId: int,
            secondsElapsed: int,  # unsigned
            clientIp: IPv4Address,
            yourIp: IPv4Address,
            serverIp: IPv4Address,
            clientHardwareAddr: int,
            messageType: MessageType,
            leaseTime: Optional[int] = None
            ) -> 'DhcpPacket':
        """Consturct a DhcpPacket from args."""

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
        """Construct a big endian binary DHCP packet."""

        lastType: int = 255
        extraBytes: bytes = b''
        if self.leaseTime is not None:
            lastType = 51
            extraBytes = (
                bytes([4]) +
                self.leaseTime.to_bytes(4, 'big') +
                bytes([255]))

        return DhcpPacket.codec.pack(
            self.opCode.value,
            1,  # ethernet hardware type
            6,  # 6 byte hardware addresses (mac)
            0,
            self.transactionId,
            self.secondsElapsed,
            1 << 15,  # server will reply via broadcasts
            int(self.clientIp),
            int(self.yourIp),
            int(self.serverIp),
            0,  # gateway ip
            self.clientHardwareAddr,
            b'',  # servername
            b'',  # boot filename
            *DhcpPacket.__optionHeaderDhcpMagic,
            53,
            1,
            self.messageType.value,
            lastType) + extraBytes

    def __repr__(self):
        return (
            f'{self.__class__.__name__}.fromArgs('
            f'opCode={self.opCode!s}, '
            f'transactionId={self.transactionId!r}, '
            f'secondsElapsed={self.secondsElapsed!r}, '
            f'clientIp={self.clientIp!r}, '
            f'yourIp={self.yourIp!r}, '
            f'serverIp={self.serverIp!r}, '
            f'clientHardwareAddr={self.clientHardwareAddr!r}, '
            f'messageType={self.messageType!s}, '
            f'leaseTime={self.leaseTime!r})')
