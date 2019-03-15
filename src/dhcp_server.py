from dhcp_packet import DhcpPacket
from dhcp_server_transaction import ServerTransaction, TransactionType

import time

class Node:
    def __init__(self, nextNode, ip, leaseTimeOffset):
        self.next = nextNode
        self.ip = ip
        self.leaseTimeOffset = leaseTimeOffset

class DhcpServer:
    def __init__(self, netId: int):
        self.__startTime = time.time() # note time here is a float and in the packet it's an unsigned int
        self.__leasedIps = {} # map from ips to mac addresses
        self.__closestLeaseHead = None # a singly linked list for keeping track of the ip closest to expiring
        self.__curTransactions = {} # map from transaction ids to ServerTransactions
        self.netId = netId
        self.__nextIp = 1

    # takes a packet and either retunrs a packet to send out or None to reply with no packets
    def recv(self, packet: DhcpPacket) -> DhcpPacket:
        if packet.transactionId not in self.__curTransactions:
            self.__freeIps()
            self.__setNextIp()
            self.__curTransactions[packet.transactionId] = ServerTransaction()
        transaction = self.__curTransactions[packet.transactionId]
        returnPacket = transaction.recv(packet)
        if returnPacket is not None:
            self.__leaseIp(transaction.yourIp, transaction.clientHardwareAddr)
        return returnPacket

    def __leaseIp(self, ip: int, clientHardwareAddr: int) -> None:
        pass

    def __freeIps(self) -> None:
        pass

    def __setNextIp(self) -> None:
        pass

