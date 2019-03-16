from dhcp_packet import DhcpPacket, MessageType
from dhcp_transaction import Transaction, TransactionType

class ServerTransaction(Transaction):
    """Class for representing an ongoing session with a client.

    Various differing pieces of data are required for various transaction types.
    It is the responsibility of the server to set the apprioriate variables
    for the appropriate session type.

    This class forms a tagged union or sum type with the self.transactionType being the tag.
    """

    yourIp: int
    leaseTime: int # unsigned

    def __init__(self, packet: DhcpPacket):
        if packet.messageType is MessageType.DISCOVER:
            self.transactionType = TransactionType.RENEW
        elif packet.messageType is MessageType.RELEASE:
            self.transactionType = TransactionType.RELEASE
        else:
            raise ValueError('Unsuported transaction')
        self.transactionId = packet.transactionId
        self.yourIp = packet.yourIp
        self.clientHardwareAddr = packet.clientHardwareAddr

    # recieve a packet from client
    # returns a DhcpPacket to respond with or None to conclude the transaction
    def recv(self, packet: DhcpPacket) -> DhcpPacket:
        self._phase += 1
