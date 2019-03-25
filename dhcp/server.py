from dhcp.packet import DhcpPacket, MessageType
from dhcp.server_transaction import ServerTransaction, TransactionType
from dhcp.singly_linked_list import DoubleEndedLinkedList

import logging
from typing import MutableMapping, Optional, Tuple
from ipaddress import IPv4Address, IPv4Interface
import time

log = logging.getLogger(__name__)

Seconds = float

DEFAULT_LEASE_TIME: Seconds = 30
DEFAULT_TRANSACTION_TIMEOUT: Seconds = 600


class DhcpServer:
    """Class for handling all DHCP packets and replying appropriately."""

    def __init__(self, interface: IPv4Interface):
        log.info(f'DHCP Server created on {interface}')

        # map from ip addresses to macs
        self.__leasedIps: MutableMapping[IPv4Address, int] = {}
        self.__leasedIpsByMacs: MutableMapping[int, IPv4Address] = {}
        # singly linked list for time of timeout
        # and ips sorted by ascending time of timeout
        self.__closestLeases: DoubleEndedLinkedList[
            Tuple[Seconds, IPv4Address]] = DoubleEndedLinkedList()

        # map from transaction ids to ServerTransactions
        self.__curTransactions: MutableMapping[int, ServerTransaction] = {}
        # singly linked list of transactions by closest timeout
        self.__transactionsByTimeouts: DoubleEndedLinkedList[
            Tuple[Seconds, ServerTransaction]] = DoubleEndedLinkedList()

        self.interface = interface
        self.__nextIp: Optional[IPv4Address] = \
            self.interface.network.network_address + 1

    def recv(self, packet: DhcpPacket) -> Optional[DhcpPacket]:
        """Recieves a DHCP packet and returns a response packet.

        The response packet may be None to indicate to not reply.
        """

        self.__timeoutTransactions()

        transaction: ServerTransaction
        if packet.transactionId not in self.__curTransactions:
            if packet.messageType is MessageType.DISCOVER:
                self.__freeIps()
                if packet.clientHardwareAddr not in self.__leasedIps:
                    if self.__nextIp is not None:
                        transaction = ServerTransaction()
                        transaction.yourIp = self.__nextIp
                        transaction.leaseTime = int(DEFAULT_LEASE_TIME)
                        self.__registerTransaction(transaction)

                    self.__setNextIp()
        else:
            transaction = self.__curTransactions[packet.transactionId]

        isTransactionOver, returnPacket = transaction.recv(packet)
        if isTransactionOver:
            if transaction.yourIp is not None:
                self.__leaseIp(
                    transaction.yourIp,
                    transaction.clientHardwareAddr)
            self.__freeTransaction(transaction.transactionId)

        return returnPacket

    def __registerTransaction(self, transaction: ServerTransaction):
        """Register a new transaction."""

        timeout = time.time() + DEFAULT_TRANSACTION_TIMEOUT
        self.__curTransactions[ServerTransaction.transactionId] = transaction
        self.__transactionsByTimeouts.pushBack((timeout, transaction))

    def __timeoutTransactions(self) -> None:
        """Drop any transactions whose transaction has not completed
        in a set period.
        """

        if not self.__transactionsByTimeouts.isEmpty():
            curTime = time.time()
            while self.__transactionsByTimeouts.peekFront()[0] <= curTime:
                _, transaction = self.__transactionsByTimeouts.popFront()
                del self.__curTransactions[transaction.transactionId]

    def __freeTransaction(self, transactionId: int) -> None:
        """Remove the transaction from the server by id"""
        pass

    def __leaseIp(self, ip: IPv4Address, clientHardwareAddr: int) -> None:
        """Reserve an IP address on the server."""
        self.__leasedIps[ip] = clientHardwareAddr
        self.__leasedIpsByMacs[clientHardwareAddr] = ip
        self.__closestLeases.pushBack((time.time() + DEFAULT_LEASE_TIME, ip))

    def __freeIps(self) -> None:
        """Unreserve IPs based on expired lease times."""
        if not self.__closestLeases.isEmpty():
            curTime = time.time()
            while self.__closestLeases.peekFront()[0] <= curTime:
                _, ip = self.__closestLeases.peekFront()
                mac = self.__leasedIps[ip]
                del self.__leasedIpsByMacs[mac]
                del self.__leasedIps[ip]
                self.__closestLeases.popFront()

    def __setNextIp(self) -> None:
        """Update self.__nextIp with the next available IP
        or None if no such IP exists."""
        lastIp: IPv4Address
        if self.__nextIp is None:
            self.__nextIp = self.interface.network.network_address + 1
            lastIp = self.__nextIp
        else:
            lastIp = self.__nextIp
            self.__nextIp += 1

        while self.__nextIp in self.__leasedIps and self.__nextIp != lastIp:
            if self.__nextIp == self.interface.network.broadcast_address - 1:
                self.__nextIp = self.interface.network.network_address + 1
            else:
                self.__nextIp += 1

        if self.__nextIp == lastIp:
            self.__nextIp = None
