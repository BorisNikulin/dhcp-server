from dhcp.client_transaction import ClientTransaction
from dhcp.transaction import TransactionType
from dhcp.packet import DhcpPacket, MessageType, OpCode
from ipaddress import IPv4Address
from socket import *

class DhcpClient:
    """Dhcp Client Logic"""

    def __init__(self):

        self.clientIp: IPv4Address
        self.transaction: ClientTransaction = ClientTransaction()
        self.serverName = 'localhost'
        serverPort = 4200
        self.clientSocket = socket(AF_INET, SOCK_DGRAM)

        self.transaction.clientIp = IPv4Address('0.0.0.0')
        self.renew(TransactionType.DISCOVER)

    def renew(self, transactionType: TransactionType)->None:
        """Start at Discover or request depending on transaction type"""
        if transactionType == TransactionType.DISCOVER:
            #generate start packet for discover
            startPacket = self.transaction.start(transactionType)

            #send start packet
            print("Client: Sending discover message.")
            self.clientSocket.sendto( startPacket.encode(),(self.serverName, serverPort))

            #receive return packet
            returnPacket, serverAddress = clientSocket.recvfrom(2048)
            print("Client: Received offer message.")

        #generate request packet
        requestPacket = self.transaction.recv(returnPacket)
        #send request packet to server
        print("Client: Sending request message.")
        self.clientSocket.sendto(requestPacket.encode(),(self.serverName, serverPort))
        #receive return packet
        returnPacket, serverAddress = clientSocket.recvfrom(2048)
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
        self.clientSocket.sendto(releasePacket.encode(),(self.serverName, serverPort))

    def disconnect()->None:
        self.clientSocket.close()


