from dhcp.client_transaction import ClientTransaction
from dhcp.transaction import TransactionType
from dhcp.packet import DhcpPacket, MessageType, OpCode

from ipaddress import IPv4Address, IPv4Interface
from socket import *


SERVER_PORT = 4200
SERVER_INTERFACE = '255.255.255.255'

class DhcpClient:
    """Dhcp Client Logic"""

    def __init__(self):

        self.clientIp: IPv4Address = IPv4Address('0.0.0.0')
        self.transaction: ClientTransaction = ClientTransaction()
        self.clientSocket = socket(AF_INET, SOCK_DGRAM)
        self.clientSocket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        self.clientSocket.bind(('', SERVER_PORT))

        self.transaction.clientIp = IPv4Address('0.0.0.0')
        self.renew(TransactionType.DISCOVER)

    def parsePacket(self, packet: bytes) -> DhcpPacket:
        partialPacket = DhcpPacket.fromPacket(
            packet[:DhcpPacket.initialPacketSize])
        offset: int = DhcpPacket.initialPacketSize
        while partialPacket.bytesNeeded > 0:
            nextOffset = offset + partialPacket.bytesNeeded
            partialPacket.parseMore(
                packet[offset:offset + partialPacket.bytesNeeded])
            offset = nextOffset

        return partialPacket.packet

    def renew(self, transactionType: TransactionType)->None:
        """Start at Discover or request depending on transaction type"""
        if transactionType is TransactionType.DISCOVER:
            #generate start packet for discover
            startPacket = self.transaction.start(transactionType)

            #send start packet
            print("Client: Sending discover message.")
            self.clientSocket.sendto( startPacket.encode(),(SERVER_INTERFACE, SERVER_PORT))
            self.clientSocket.recv(2048)

            #receive return packet
            returnBytes = self.clientSocket.recv(2048)
            returnPacket = self.parsePacket(returnBytes)
            print(returnBytes)
            print(f'Packet: {returnPacket}')
            print("Client: Received offer message.")


        #generate request packet
        requestPacket = self.transaction.recv(returnPacket)

        if requestPacket is None:
            print ("Client: Declined by server")
        else:
            #send request packet to server
            print("Client: Sending request message.")
            self.clientSocket.sendto(requestPacket.encode(),(SERVER_INTERFACE, SERVER_PORT))
            #receive return packet
            returnBytes, serverAddress = self.clientSocket.recvfrom(2048)
            returnPacket = self.parsePacket(returnBytes)
            print("Client: Received ACK message.")

            if returnPacket.messageType == MessageType.ACK:
                self.clientIp = returnPacket.yourIp
            else:
                print("Client: Declined by server.")


    def release(self)->None:
        self.clientIp = IPv4Address('0.0.0.0')

        #generate release packet
        releasePacket = self.transaction.release()
        #send releas packet to server
        print("Client: Sending release message.")
        self.clientSocket.sendto(releasePacket.encode(),(SERVER_INTERFACE, SERVER_PORT))

    def disconnect(self)->None:
        self.clientSocket.close()


