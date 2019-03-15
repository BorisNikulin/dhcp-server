from dhcp_packet import DhcpPacket, MessageType
from dhcp_transaction import Transaction, TransactionType

class ServerTransaction(Transaction):
    # def __init__(self):
        # self.yourIp = None
        # self.clientHardwareAddr = None

    # recieve a packet from client
    # returns a DhcpPacket to respond with or None to conclude the transaction
    def recv(self, packet: DhcpPacket) -> DhcpPacket:
        if self._phase == 0:
            if packet.messageType is MessageType.DISCOVER:
                self.transactionType = TransactionType.RENEW
            elif packet.messageType is MessageType.RELEASE:
                self.transactionType = TransactionType.RELEASE
            else:
                raise ValueError('Unsuported transaction')
            self.transactionId = packet.transactionId
            self.yourIp = packet.yourIp
            self.clientHardwareAddr = packet.clientHardwareAddr
        self._phase += 1
