from src import *
from socket import *

class DhcpClient:
    """Main client class"""

    def __init__(self):

        clientIp: IPv4Address
        serverName = 'localhost'
        serverPort = 12000
        clientSocket = socket(AF_INET, SOCK_DGRAM)

        #first connection
        connectToServer(TransactionType.REQUEST)
        
        #after ACK
        userInput: str
        while True:

                print("1. Release\n" +
                      "2. Renew \n" +
                      "3. Quit \n")
                userInput = input()

                if userInput == "1":
                    connectToServer(TransactionType.RELEASE)
                elif userInput == "2":
                    connectToServer(TransactionType.RENEW)
                else:
                    if userInput == "3":
                        print("Quitting.")
                    else:
                        print("Invalid input. Quitting.")
                    clientSocket.close()
                    quit()
                    
            
    def connectToServer(self, transactionType: TransactionType)->None:
        transaction = ClientTransaction()

        #send start packet
        clientSocket.sendto( transaction.start(transactionType),(serverName, serverPort))
        returnPacket, serverAddress = clientSocket.recvfrom(2048)

        while returnPacket is not None:
            clientSocket.sendto(transaction.recv(returnPacket),(serverName, serverPort))
            returnPacket, serverAddress = clientSocket.recvfrom(2048)
        
        
    
