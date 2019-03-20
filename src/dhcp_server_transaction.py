from dhcp_packet import DhcpPacket, MessageType, OpCode
from dhcp_transaction import Transaction, TransactionType

from typing import Optional, Tuple

class ServerTransaction(Transaction):
    """Class for representing an ongoing session with a client.

    Various differing pieces of data are required for various transaction types.
    It is the responsibility of the server to set the apprioriate variables
    for the appropriate session type.

    This class forms a tagged union or sum type with the self.transactionType being the tag.
    """

    yourIp: Optional[int]
    serverIp: int
    leaseTime: int # unsigned

    # recieve a packet from client
    # returns a DhcpPacket to respond with or None to conclude the transaction
    def recv(self, packet: DhcpPacket) -> Tuple[bool, Optional[DhcpPacket]]:

        self._phase += 1
        if self._phase == 1:
            self.transactionId = packet.transactionId
            self.clientHardwareAddr = packet.clientHardwareAddr

            if packet.messageType is MessageType.DISCOVER:
                self.transactionType = TransactionType.RENEW
                return (True, DhcpPacket.fromArgs(
                    OpCode.REPLY,
                    self.transactionId,
                    packet.secondsElapsed,
                    packet.clientIp,
                    0 if self.yourIp is None else self.yourIp,
                    0, # TODO: figure out what to do with serverIp (nothing?)
                    packet.clientHardwareAddr,
                    MessageType.OFFER,
                    self.leaseTime))

            elif packet.messageType is MessageType.RELEASE:
                self.transactionType = TransactionType.RELEASE
                raise NotImplementedError

            else:
                raise ValueError('Unsuported transaction')

        elif self._phase == 2:
            if self.transactionType is TransactionType.RENEW:
                if packet.messageType is MessageType.REQUEST:
                    return (False, DhcpPacket.fromArgs(
                        OpCode.REPLY,
                        self.transactionId,
                        packet.secondsElapsed,
                        packet.clientIp,
                        0 if self.yourIp is None else self.yourIp,
                        0, # TODO: server ip? see todo above
                        packet.clientHardwareAddr,
                        MessageType.ACK,
                        self.leaseTime))

                else:
                    raise ValueError(f'Expecting DHCP request. Got {packet.messageType.name}')
            else:
                if packet.messageType is MessageType.ACK:
                    raise NotImplementedError

                else:
                    raise ValueError(f'Expecting DHCP ack. Got {packet.messageType.name}')

        else:
            raise ValueError('recieved too many packets')

