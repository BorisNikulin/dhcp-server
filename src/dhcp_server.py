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
        # map from ip addresses to macs
        self.__leasedIps: MutableMapping[int, int] = {}
        # singly linked list head for time of timeout and macs sorted by ascending time of timeout
        self.__closestLeases: DoubleEndedLinkedList[Tuple[Seconds, int]] = DoubleEndedLinkedList()
        # map from transaction ids to ServerTransactions
        self.__curTransactions: MutableMapping[int, ServerTransaction] = {}
        # singly linked list of transactions by closest timeout
        self.__transactionsByTimeouts: DoubleEndedLinkedList[Tuple[Seconds, ServerTransaction]] = DoubleEndedLinkedList()
        self.netId: int = netId
        self.__nextIp: Optional[int] = 1

    def recv(self, packet: DhcpPacket) -> Optional[DhcpPacket]:
        """Recieves a DHCP packet and returns a response packet.

        The response packet may be None to indicate to not reply.
        """

        self.__timeoutTransactions()

        transaction: ServerTransaction
        if packet.transactionId not in self.__curTransactions:
            if packet.messageType is MessageType.DISCOVER:
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
        if not self.__transactionsByTimeouts.isEmpty():
            curTime = time.time()
            while self.__transactionsByTimeouts.peekFront()[0] <= curTime:
                self.__transactionsByTimeouts.popFront()

    def __leaseIp(self, ip: int, clientHardwareAddr: int) -> None:
        """Reserve an IP address on the server."""
        self.__leasedIps[ip] = clientHardwareAddr
        self.__closestLeases.pushBack((time.time() + DEFAULT_LEASE_TIME, ip))

    def __freeIps(self) -> None:
        """Unreserve IPs based on expired lease times."""
        if not self.__closestLeases.isEmpty():
            curTime = time.time()
            while self.__closestLeases.peekFront()[0] <= curTime:
                mac = self.__closestLeases.peekFront()[1]
                del self.__leasedIps[mac]
                self.__closestLeases.popFront()

    def __setNextIp(self) -> None:
        """Update self.__nextIp with the next available IP or None if no such IP exists."""
        lastIp: int
        if self.__nextIp is None:
            self.__nextIp = 1
            lastIp = self.__nextIp
        else:
            lastIp = self.__nextIp
            self.__nextIp += 1

        while self.__nextIp in self.__leasedIps and self.__nextIp != lastIp:
            if self.__nextIp == 254:
                self.__nextIp = 1
            else:
                self.__nextIp += 1

        if self.__nextIp == lastIp:
            self.__nextIp = None
