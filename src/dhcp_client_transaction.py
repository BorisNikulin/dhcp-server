from dhcp_transaction import Transaction
from dhcp_packet import DhcpPacket

from enum import Enum

class ClientTransaction(Transaction):
    # start a transaction
    # returns a DhcpPacket to send to the server
    def start(self, transactionType):
        self.transactionType = transactionType

    # recieve a packet from server
    # returns a DhcpPacket to respond with or None to conclude the transaction
    def recv(self, packet: DhcpPacket) -> DhcpPacket:
        self._phase += 1
