from dhcp_transaction import Transaction, TransactionType
from dhcp_packet import DhcpPacket

from typing import Optional
from enum import Enum
import time
import uuid

Seconds = float
DEFAULT_LEASE_TIME: Seconds = 30

class ClientTransaction(Transaction):
    """Class for representing an onogoing transaction with the server."""

    def __init__(self):
        self.clientHardwareAddr = uuid.getnode()
        self.transactionId = uuid.uuid1().int>>64
        self.transactionStartTime = time.time()
        
    # start a transaction
    # returns a DhcpPacket to send to the server
    def start(self, transactionType: TransactionType) -> DhcpPacket:
        """Begin a DHCP transaction of given type.

        Returns the DHCP packet to send to the server.
        """

        self.transactionType = transactionType
        return DhcpPacket.fromArgs(
            1, #OpCode
            self.transactionId,
            0, #secondsElapsed
            0, #clientIp
            0, #yourIp
            255, #serverIp
            self.clientHardwareAddr,
            MessageType.DISCOVER,
            DEFAULT_LEASE_TIME
            )

    # recieve a packet from server
    # returns a DhcpPacket to respond with or None to conclude the transaction
    def recv(self, packet: DhcpPacket) -> Optional[DhcpPacket]:
        """Recieve a reply from the server and returns the response packet.

        The response packet may be None to indicate conclusion of the session.
        """
        self._phase += 1

        
        if packet.messageType == MessageType.OFFER:
            if packet.clientHardwareAddr == self.clientHardwareAddr:
                return DhcpPacket.fromArgs(
                    1, #opCode
                    packet.transactionId,
                    time.time() - transactionStartTime,
                    0, #clientIP
                    packet.yourIP,
                    packet.serverIp,
                    packet.clientHardwareAddr,
                    MessageType.REQUEST,
                    DEFAULT_LEASE_TIME
                    )
        elif packet.messageType == MessageType.DECLINE:
            print("REQUEST DECLINED")
            return None

        elif packet.messageType == MessageType.ACK:
            if packet.clientHardwareAddr == self.clientHardwareAddr:
                print("IP address successfully received.")
            else:
                print("MAC address does not match, could not ACK.")
            return None

        
