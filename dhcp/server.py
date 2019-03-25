from dhcp.packet import DhcpPacket, MessageType, OpCode
from dhcp.server_transaction import ServerTransaction, TransactionType
from dhcp.singly_linked_list import DoubleEndedLinkedList

import logging
from typing import MutableMapping, Optional, Tuple, Set
from ipaddress import IPv4Address, IPv4Interface
import time

log = logging.getLogger(__name__)

Seconds = float

DEFAULT_LEASE_TIME: Seconds = 30
DEFAULT_TRANSACTION_TIMEOUT: Seconds = 600


class DhcpServer:
    """Class for handling all DHCP packets and replying appropriately."""

    def __init__(self, interface: IPv4Interface):
        log.info(f'DHCP server created on {interface}')

        # map from ip addresses to lease time (absolute) and macs
        self.__leasedIps: MutableMapping[IPv4Address, Tuple[Seconds, int]] = {}
        self.__leasedIpsByMacs: MutableMapping[int, IPv4Address] = {}
        # singly linked list for time of timeout
        # and ips sorted by ascending time of timeout
        self.__closestLeases: DoubleEndedLinkedList[
            Tuple[Seconds, IPv4Address]] = DoubleEndedLinkedList()
        # IPs preliminarily reserved (while doing a transaction)
        self.__markedIps: Set[IPv4Address] = set()

        # map from transaction ids to ServerTransactions
        self.__curTransactions: MutableMapping[int, ServerTransaction] = {}
        # singly linked list of transactions by closest timeout
        self.__transactionsByTimeouts: DoubleEndedLinkedList[
            Tuple[Seconds, ServerTransaction]] = DoubleEndedLinkedList()

        self.interface = interface
        self.__nextIp: Optional[IPv4Address] = None

    def recv(self, packet: DhcpPacket) -> Optional[DhcpPacket]:
        """Recieves a DHCP packet and returns a response packet.

        The response packet may be None to indicate to not reply.
        """

        log.info(
            f'Recieved {packet.messageType.name} '
            f'with MAC of {packet.clientHardwareAddr} and '
            f'ID of {packet.transactionId}')
        log.debug(f'Recieved packet: {packet}')

        self.__timeoutTransactions()

        transaction: Optional[ServerTransaction] = None
        returnPacket: Optional[DhcpPacket] = None

        if packet.transactionId not in self.__curTransactions:
            if packet.messageType is MessageType.DISCOVER:
                if packet.clientHardwareAddr not in self.__leasedIps:
                    self.__timeoutIps()
                    self.__setNextIp()
                    if self.__nextIp is not None:
                        self.markIp(self.__nextIp)
                        transaction = ServerTransaction()
                        transaction.transactionId = packet.transactionId
                        transaction.yourIp = self.__nextIp
                        transaction.serverIp = self.interface.ip
                        transaction.leaseTime = int(DEFAULT_LEASE_TIME)
                        self.__registerTransaction(transaction)

                else:
                    returnPacket = DhcpPacket.fromArgs(
                        OpCode.REPLY,
                        packet.transactionId,
                        packet.secondsElapsed,
                        self.__leasedIpsByMacs[packet.clientHardwareAddr],
                        self.__leasedIpsByMacs[packet.clientHardwareAddr],
                        self.interface.ip,
                        packet.clientHardwareAddr,
                        MessageType.ACK,
                        int(
                            time.time()
                            - self.__leasedIps[
                                self.__leasedIpsByMacs[
                                    packet.clientHardwareAddr]
                                ][0])
                        )

            elif packet.messageType is MessageType.REQUEST:
                if packet.yourIp not in self.__leasedIps:
                    self.markIp(packet.yourIp)
                    transaction = ServerTransaction()
                    transaction.transactionId = packet.transactionId
                    transaction.yourIp = packet.yourIp
                    transaction.serverIp = self.interface.ip
                    transaction.leaseTime = int(DEFAULT_LEASE_TIME)
                    self.__registerTransaction(transaction)
                else:
                    returnPacket = DhcpPacket.fromArgs(
                        OpCode.REPLY,
                        transaction.transactionId,
                        packet.secondsElapsed,
                        IPv4Address(0),
                        IPv4Address(0),
                        self.interface.ip,
                        transaction.clientHardwareAddr,
                        MessageType.NAK)

            elif packet.messageType is MessageType.RELEASE:
                if packet.clientHardwareAddr in self.__leasedIpsByMacs:
                    self.__freeIp(
                        self.__leasedIpsByMacs[packet.clientHardwareAddr])

        else:
            transaction = self.__curTransactions[packet.transactionId]

        if transaction is not None:
            isTransactionOver, returnPacket = transaction.recv(packet)
            if isTransactionOver:
                self.unmarkIp(transaction.yourIp)
                if transaction.transactionType is TransactionType.DISCOVER:
                    if transaction.requestIp not in self.__leasedIps:
                        self.__leaseIp(
                            transaction.yourIp,
                            transaction.clientHardwareAddr)
                    else:
                        returnPacket = DhcpPacket.fromArgs(
                            OpCode.REPLY,
                            transaction.transactionId,
                            packet.secondsElapsed,
                            packet.yourIp,
                            IPv4Address(0),
                            self.interface.ip,
                            transaction.clientHardwareAddr,
                            MessageType.NAK)
                elif transaction.transactionType is TransactionType.RENEW:
                    self.__leaseIp(
                        transaction.yourIp,
                        transaction.clientHardwareAddr)

                self.__freeTransaction(transaction.transactionId)

        log.debug(f'Return packet: {returnPacket}')
        return returnPacket

    def __registerTransaction(self, transaction: ServerTransaction):
        """Register a new transaction."""

        timeout = time.time() + DEFAULT_TRANSACTION_TIMEOUT
        self.__curTransactions[transaction.transactionId] = transaction
        self.__transactionsByTimeouts.pushBack((timeout, transaction))
        log.debug(
            f'Registered transaction with '
            f'ID {transaction.transactionId}')

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
        """Remove the transaction from the server by ID. Assumes existence."""
        del self.__curTransactions[transactionId]
        self.__transactionsByTimeouts.removeBy(lambda t: t[1] == transactionId)
        log.debug(f'Freed transaction with ID {transactionId}')

    def __leaseIp(self, ip: IPv4Address, clientHardwareAddr: int) -> None:
        """Reserve an IP address on the server."""
        leaseTime = time.time() + DEFAULT_LEASE_TIME
        self.__leasedIps[ip] = (leaseTime, clientHardwareAddr)
        self.__leasedIpsByMacs[clientHardwareAddr] = ip
        self.__closestLeases.pushBack((leaseTime, ip))
        log.debug(f'Leased {ip} to {clientHardwareAddr}')

    def __timeoutIps(self) -> None:
        """Unreserve IPs based on expired lease times."""
        if not self.__closestLeases.isEmpty():
            curTime = time.time()
            while self.__closestLeases.peekFront()[0] <= curTime:
                _, ip = self.__closestLeases.peekFront()
                _, mac = self.__leasedIps[ip]
                log.debug(f'Freed {ip} belonging to {mac}')
                del self.__leasedIpsByMacs[mac]
                del self.__leasedIps[ip]
                self.__closestLeases.popFront()

    def __freeIp(self, ip: IPv4Address) -> None:
        """Unreserve a specific IP. Assumes existence."""
        _, mac = self.__leasedIps[ip]
        del self.__leasedIpsByMacs[mac]
        del self.__leasedIps[ip]
        self.__closestLeases.removeBy(lambda l: l[1] == ip)
        log.debug(f'Freed {ip}')

    def markIp(self, ip: IPv4Address) -> None:
        """Mark an IP as taken for the purpose of reserving during a transaction."""
        self.__markedIps.add(ip)
        log.debug(f'{ip} marked')

    def unmarkIp(self, ip: IPv4Address) -> None:
        """Unmark an IP. Assumes IP is marked. See markIP()"""
        self.__markedIps.remove(ip)
        log.debug(f'{ip} unmarked')

    def __setNextIp(self) -> None:
        """Update self.__nextIp with the next available IP
        or None if no such IP exists.
        """

        lastIp: IPv4Address
        if self.__nextIp is None:
            self.__nextIp = self.interface.network.network_address + 1
            if self.__nextIp not in self.__leasedIps:
                log.debug(f'Next IP: {self.__nextIp}')
                return

        lastIp = self.__nextIp
        self.__nextIp += 1

        while (
                self.__nextIp in self.__leasedIps
                or self.__nextIp in self.__markedIps
                ) and self.__nextIp != lastIp:
            if self.__nextIp == self.interface.network.broadcast_address - 1:
                self.__nextIp = self.interface.network.network_address + 1
            else:
                self.__nextIp += 1

        if self.__nextIp == lastIp:
            self.__nextIp = None

        log.debug(f'Next IP is {self.__nextIp}')
