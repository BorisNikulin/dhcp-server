from dhcp_client_transaction import ClientTransaction
from dhcp_transaction import TransactionType
from dhcp_packet import DhcpPacket, MessageType, OpCode
from socket import *

class DhcpClient:
    """Dhcp Client Logic"""

    def __init__(self):

        clientIp: IPv4Address
        transaction: ClientTransaction = ClientTransaction()
        
        serverName = 'localhost'
        serverPort = 12000
        clientSocket = socket(AF_INET, SOCK_DGRAM)
        renew(TransactionType.DISCOVER)
        
    def renew(self, transactionType: TransactionType)->None:
        """Start at Discover or request depending on message type"""
        if transactionType == TransactionType.DISCOVER:
            #generate start packet for discover
            startPacket = self.transaction.start(transactionType)
            
            #send start packet
            print("Client: Sending discover message.")
            clientSocket.sendto( startPacket.encode(),(serverName, serverPort))
            
            #receive return packet
            returnPacket, serverAddress = clientSocket.recvfrom(2048)
            print("Client: Received offer message.")
        
        #generate request packet
        requestPacket = self.transaction.recv(returnPacket)
        #send request packet to server
        print("Client: Sending request message.")
        clientSocket.sendto(requestPacket.encode(),(serverName, serverPort))
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
        clientSocket.sendto(releasePacket.encode(),(serverName, serverPort))
        
    
