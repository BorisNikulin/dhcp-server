from dhcp.client_class import DhcpClient
from dhcp.transaction import TransactionType
from ipaddress import IPv4Address

class DhcpClientUI:
    """Client UI"""

    def __init__(self):

        #initialize DhcpClient, which sends DISCOVER message to server
        dhcpClient = DhcpClient()
        newIP: int(self.dhcpClient.clientIp)

        print("Client: new IP address is " + newIp)

        while True:
            print("\nClient: Choose option: \n"+
                  "_____________________________ \n"+
                  "(1) Renew lease \n"+
                  "(2) Release IP address\n"+
                  "(3) Exit\n"+
                  "_____________________________ \n")
            userInput: str = input()

            if userInput == "1":

                self.dhcpClient.renew(TransactionType.RENEW)
            elif userInput == "2":
                self.dhcpClient.release()
            else:
                if userInput == "3":
                    print("Client: Exiting.")
                
                else:
                    print("Client: Unrecognized input. Exiting")
                self.dhcpClient.disconnect
                quit()

DhcpClientUI()
