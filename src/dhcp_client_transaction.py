from src.dhcp_transaction import Transaction, TransactionType
from src.dhcp_packet import DhcpPacket, MessageType, OpCode

from typing import Optional
from enum import Enum
import time
import uuid

Seconds = float
DEFAULT_LEASE_TIME: Seconds = 30

class ClientTransaction(Transaction):
    """Class for representing an onogoing transaction with the server."""

    def __init__(self):
        clientHardwareAddr = uuid.getnode()
        transactionId = uuid.uuid1().int>>64
        transactionStartTime = time.time()
        clientIp: IPv4Address
        yourIp: IPv4Address
        
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
                if _phase == 1:
                    return DhcpPacket.fromArgs(
                        OpCode.REQUEST, #opCode
                        packet.transactionId,
                        time.time() - transactionStartTime,
                        packet.clientIP, #clientIP
                        packet.yourIP,
                        packet.serverIp,
                        packet.clientHardwareAddr,
                        MessageType.REQUEST,
                        DEFAULT_LEASE_TIME
                        )
                else:
                    print("Client: Error: Phase-MessageType mismatch.")
                    return None
        elif packet.messageType == MessageType.DECLINE:
            print("REQUEST DECLINED")
            return None

        elif packet.messageType == MessageType.ACK:
            if packet.clientHardwareAddr == self.clientHardwareAddr:
                if _phase == 2:
                    print("Client: IP address successfully received: " + packet.yourIP)
                    self.clientIp = packet.yourIp
                else:
                    print("Client: Error: Phase-MessageType mismatch")
            else:
                print("Client: MAC address does not match, could not ACK.")
            return None
    def release()->DhcpPacket:
        return DhcpPacket.fromArgs(
                        OpCode.REQUEST, #opCode
                        0,#ID
                        0, #elapsed time
                        IPv4Address('0.0.0.0'), #clientIP
                        IPv4Address('0.0.0.0'), #yourIP
                        IPv4Address('255.255.255.255'),
                        self.clientHardwareAddr,
                        MessageType.REQUEST,
                        DEFAULT_LEASE_TIME
                        )
        
        
