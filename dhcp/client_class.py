from dhcp.client_transaction import ClientTransaction
from dhcp.transaction import TransactionType
from dhcp.packet import DhcpPacket, MessageType, OpCode

from ipaddress import IPv4Address, IPv4Interface
from socket import *


SERVER_PORT = 4200
SERVER_INTERFACE = '144.37.118.233'

class DhcpClient:
    """Dhcp Client Logic"""

    def __init__(self):

        self.clientIp: IPv4Address = IPv4Address('0.0.0.0')
        self.lastClientIp: IPv4Address = self.clientIp
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
        
        self.transaction.yourIp = self.lastClientIp
        #generate start packet for discover
        startPacket = self.transaction.start(transactionType)
        

        #send start packet
        print(f'Packet: {startPacket}')
        self.clientSocket.sendto( startPacket.encode(),(SERVER_INTERFACE, SERVER_PORT))
             
        transactionType == TransactionType.RENEW
            
        isTransactionOver = False
        while not isTransactionOver:
            #loop until transaction is finished
            returnBytes = self.clientSocket.recv(2048)
            returnPacket = self.parsePacket(returnBytes)
            print(f'Client: Packet received from server: \n {returnPacket}')
            isTransactionOver, requestPacket = self.transaction.recv(returnPacket)

            
            print(f'Client: Response to server: \n Packet: {requestPacket}')
            
            if requestPacket is not None:
                
                self.clientSocket.sendto(requestPacket.encode(),(SERVER_INTERFACE, SERVER_PORT))
            #print(f'Test A {isTransactionOver}')
    

        if returnPacket.messageType == MessageType.ACK:
            self.clientIp = returnPacket.yourIp
            self.lastClientIp = self.clientIp
        else:
            print("Client: Declined by server.")


    def release(self)->None:
        if self.clientIp == IPv4Address('0.0.0.0'):
            print("Client: IP address has already been released")
        else:
            print("Client: Sending release message.")
        self.clientIp = IPv4Address('0.0.0.0')            
        #generate release packet
        releasePacket = self.transaction.release()
        #send releas packet to server
        
        self.clientSocket.sendto(releasePacket.encode(),(SERVER_INTERFACE, SERVER_PORT))

    def disconnect(self)->None:
        self.clientSocket.close()


