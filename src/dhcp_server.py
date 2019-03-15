from dhcp_packet import DhcpPacket, MessageType
from dhcp_server_transaction import ServerTransaction, TransactionType
from singly_linked_list import DoubleEndedLinkedList

from typing import MutableMapping, Optional, Tuple
import time

Seconds = float

DEFAULT_LEASE_TIME: Seconds = 30
DEFAULT_TRANSACTION_TIMEOUT: Seconds = 30

class DhcpServer:
    def __init__(self, netId: int):
        # note time here is a float and in the packet it's an unsigned int
        self.__startTime: Seconds = time.time()
        # map from mac addresses to ip
        self.__leasedIps: MutableMapping[int, int] = {}
        # singly linked list head for mac with ip closest to expiring
        self.__closestLeaseHead: DoubleEndedLinkedList[Tuple[int, int]] = DoubleEndedLinkedList()
        # map from transaction ids to ServerTransactions
        self.__curTransactions: MutableMapping[int, ServerTransaction] = {}
        # singly linked list of transaction by closest timeout
        self.__transactionsByTimeoutHead: DoubleEndedLinkedList[Tuple[ServerTransaction, Seconds]] = DoubleEndedLinkedList()
        self.netId: int = netId
        self.__nextIp: int = 1

    # takes a packet and either retunrs a packet to send out or None to reply with no packets
    def recv(self, packet: DhcpPacket) -> DhcpPacket:
        transaction: ServerTransaction
        if packet.transactionId not in self.__curTransactions:
            if packet.messageType == MessageType.DISCOVER:
                if packet.clientHardwareAddr not in self.__leasedIps:
                    transaction = ServerTransaction(packet)
                    transaction.yourIp = self.__nextIp
                    transaction.leaseTime = int(DEFAULT_LEASE_TIME)

                    self.__curTransactions[packet.transactionId] = transaction
                    self.__freeIps()
                    self.__setNextIp()
        else:
            transaction = self.__curTransactions[packet.transactionId]

        returnPacket = transaction.recv(packet)
        if returnPacket is not None:
            self.__leaseIp(transaction.yourIp, transaction.clientHardwareAddr)
        return returnPacket

    def registerTransaction(self, transaction: ServerTransaction):
        now: Seconds = time.time()
        timeout = now + DEFAULT_TRANSACTION_TIMEOUT - self.__startTime



    def __leaseIp(self, ip: int, clientHardwareAddr: int) -> None:
        pass

    def __freeIps(self) -> None:
        pass

    def __setNextIp(self) -> None:
        pass

