from dhcp_packet import DhcpPacket, MessageType
from dhcp_server_transaction import ServerTransaction, TransactionType
from singly_linked_list import DoubleEndedLinkedList

from typing import MutableMapping, Optional, Tuple
import time

Seconds = float

DEFAULT_LEASE_TIME: Seconds = 30
DEFAULT_TRANSACTION_TIMEOUT: Seconds = 30

class DhcpServer:
    """Class for handling all DHCP packets and replying appropriately."""

    def __init__(self, netId: int):
        # map from mac addresses to ip
        self.__leasedIps: MutableMapping[int, int] = {}
        # singly linked list head for time of timeout and macs sorted by ascending time of timeout
        self.__macsByClosestLeases: DoubleEndedLinkedList[Tuple[Seconds, int]] = DoubleEndedLinkedList()
        # map from transaction ids to ServerTransactions
        self.__curTransactions: MutableMapping[int, ServerTransaction] = {}
        # singly linked list of transaction by closest timeout
        self.__transactionsByTimeouts: DoubleEndedLinkedList[Tuple[Seconds, ServerTransaction]] = DoubleEndedLinkedList()
        self.netId: int = netId
        self.__nextIp: Optional[int] = 1

    def recv(self, packet: DhcpPacket) -> Optional[DhcpPacket]:
        """Recieves a DHCP packet and returns a response packet.

        The response packet may be None to indicate to not reply."""

        self.__timeoutTransactions()

        transaction: ServerTransaction
        if packet.transactionId not in self.__curTransactions:
            if packet.messageType == MessageType.DISCOVER:
                if packet.clientHardwareAddr not in self.__leasedIps:
                    if self.__nextIp is not None:
                        transaction = ServerTransaction(packet)
                        transaction.yourIp = self.__nextIp
                        transaction.leaseTime = int(DEFAULT_LEASE_TIME)
                        self.__registerTransaction(transaction)

                    self.__freeIps()
                    self.__setNextIp()
        else:
            transaction = self.__curTransactions[packet.transactionId]

        returnPacket = transaction.recv(packet)
        if returnPacket is not None:
            self.__leaseIp(transaction.yourIp, transaction.clientHardwareAddr)
        return returnPacket

    def __registerTransaction(self, transaction: ServerTransaction):
        """Register a new transaction."""

        timeout = time.time() + DEFAULT_TRANSACTION_TIMEOUT
        self.__curTransactions[ServerTransaction.transactionId] = transaction
        self.__transactionsByTimeouts.pushBack((timeout, transaction))

    def __timeoutTransactions(self) -> None:
        """Drop any transactions whose transaction has not completed in a set period."""
        if self.__transactionByTimeouts is not isEmpty()
            if self.__transactionByTimeouts.peekFront[0] is time.time()
                
                self.__transactionByTimeouts.popFront()
                
    def __leaseIp(self, ip: int, clientHardwareAddr: int) -> None:
        """Reserve an IP address on the server."""
        self.__leasedIps.__setitem__(clientHardwareAddr, ip)

    def __freeIps(self) -> None:
        """Unreserve IPs based on expired lease times."""
        if self.__transactionByTimeouts is not isEmpty()
            if self.__macsByClosestLeases.peekFront[0] is time.time()
                mac = __macsByClosestLeases.peekFront[1]
                self.__leasedIps.__delitem__(mac)
                self.__macsByClosestLeases.popFront()

    def __setNextIp(self) -> None:
        """Update self.__nextIp with the next available IP or None if no such IP exists."""
        if self.__nextIP == 255
            self.__nextIP = 1;
        else self.__nextIP = self.__nextIP + 1;
            
            

