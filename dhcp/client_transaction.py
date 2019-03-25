from dhcp.transaction import Transaction, TransactionType
from dhcp.packet import DhcpPacket, MessageType, OpCode

from ipaddress import IPv4Address
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
        self.transactionId = uuid.uuid1().int>>96
        self.transactionStartTime = time.time()
        self.clientIp: IPv4Address
        self.yourIp: IPv4Address
        self._phase: int = 0;

    # start a transaction
    # returns a DhcpPacket to send to the server
    def start(self, transactionType: TransactionType) -> DhcpPacket:
        """Begin a DHCP transaction of given type.

        Returns the DHCP packet to send to the server.
        """


        self.transactionType = transactionType
        return DhcpPacket.fromArgs(
            OpCode.REQUEST, #OpCode
            self.transactionId,
            0, #secondsElapsed
            self.clientIp, #clientIp
            IPv4Address('0.0.0.0'), #yourIp
            IPv4Address('255.255.255.255'), #serverIp
            self.clientHardwareAddr,
            MessageType.DISCOVER,
            int(DEFAULT_LEASE_TIME)
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
                if self._phase == 1:
                    return DhcpPacket.fromArgs(
                        OpCode.REQUEST, #opCode
                        packet.transactionId,
                        time.time() - self.transactionStartTime,
                        packet.clientIp, #clientIP
                        packet.yourIp,
                        packet.serverIp,
                        packet.clientHardwareAddr,
                        MessageType.REQUEST,
                        int(DEFAULT_LEASE_TIME)
                        )
                else:
                    print("Client: Error: Phase-MessageType mismatch.")
                    return None
        elif packet.messageType == MessageType.DECLINE:
            print("REQUEST DECLINED")
            return None

        elif packet.messageType == MessageType.ACK:
            if packet.clientHardwareAddr == self.clientHardwareAddr:
                if self._phase == 2:
                    print("Client: IP address successfully received: " + str(packet.yourIp))
                    self.clientIp = packet.yourIp
                else:
                    print("Client: Error: Phase-MessageType mismatch")
            else:
                print("Client: MAC address does not match, could not ACK.")
            return None
        return None
    def release(self)->DhcpPacket:
        return DhcpPacket.fromArgs(
                        OpCode.REQUEST, #opCode
                        0,#ID
                        0, #elapsed time
                        IPv4Address('0.0.0.0'), #clientIP
                        IPv4Address('0.0.0.0'), #yourIP
                        IPv4Address('255.255.255.255'),
                        self.clientHardwareAddr,
                        MessageType.REQUEST,
                        int(DEFAULT_LEASE_TIME)
                        )
