from struct import Struct

class DhcpPacket:
    # main packet + start of first optional (not really optional)
    # uses nateive endianness
    # most of the fields will not be uses for simplicity's sake
    codec = Struct('=4BI2H4IQ64s128s' + '4B3B')
    optionHeaderDhcpMagic = [0x63, 0x82, 0x53, 0x63]

    def __init(self):
        pass

    def test(self):
        tId = 1239
        secs = 7
        yourIp = 50
        myIp = 20
        myMac = 2
        messageType = 1
        return DhcpPacket.codec.pack(2, 1, 6, 0, tId, secs, 1 << 15, 0, yourIp, myIp, 0, myMac, b'', b'', *DhcpPacket.optionHeaderDhcpMagic, 53, 1, messageType)

