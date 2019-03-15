from dhcp_packet import DhcpPacket, MessageType
from dhcp_transaction import Transaction, TransactionType

class ServerTransaction(Transaction):
    """Tagged union for possible transaction types from the server's perspective
    with the transactionType being the tag.
    The extra variables must be initialized by DhcpServer after construction
    and checking transactionType (although all current transaction types use yourIp and leaseTime"""

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
