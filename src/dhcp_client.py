from dhcp_packet import DhcpPacket, MessageType
from dhcp_client_transaction import ClientTransaction, TransactionType

from typing import Optional



class DhcpClient:
    """Class for handling all DHCP packets and replying appropriately."""

    def __init__(self, netId: int):
        clientIp: IPv4Address
        transaction: ClientTransaction

    def start(self, transactionType: TransactionType) -> Optional[DhcpPacket]:
        """Returns the start packet"""
        transaction = ClientTransaction()
        startPacket = transaction.start(transactionType)

        return startPacket
    
    def recv(self, packet: DhcpPacket) -> Optional[DhcpPacket]:
        """Recieves a DHCP packet and returns a response packet.

        The response packet may be None to indicate to not request.
        """

        returnPacket = transaction.recv(packet)

    
        return returnPacket

    
