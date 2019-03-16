from dhcp_transaction import Transaction, TransactionType
from dhcp_packet import DhcpPacket

from typing import Optional
from enum import Enum

class ClientTransaction(Transaction):
    """Class for representing an onogoing transaction with the server."""

    # start a transaction
    # returns a DhcpPacket to send to the server
    def start(self, transactionType: TransactionType) -> DhcpPacket:
        """Begin a DHCP transaction of given type.

        Returns the DHCP packet to send to the server.
        """

        self.transactionType = transactionType

    # recieve a packet from server
    # returns a DhcpPacket to respond with or None to conclude the transaction
    def recv(self, packet: DhcpPacket) -> Optional[DhcpPacket]:
        """Recieve a reply from the server and returns the response packet.

        The response packet may be None to indicate conclusion of the session.
        """
        self._phase += 1
