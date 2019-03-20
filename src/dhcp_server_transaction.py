from dhcp_packet import DhcpPacket, MessageType, OpCode
from dhcp_transaction import Transaction, TransactionType

from typing import Optional, Tuple, Generator

class ServerTransaction(Transaction):
    """Class for representing an ongoing session with a client.

    Various differing pieces of data are required for various transaction types.
    It is the responsibility of the server to set the apprioriate variables
    for the appropriate session type.

    This class forms a tagged union or sum type with the self.transactionType being the tag.
    """

    __transaction: Optional[Generator[DhcpPacket, DhcpPacket, DhcpPacket]]

    yourIp: int
    serverIp: int
    leaseTime: int # unsigned

    def __init__(self):
        self.__transaction = None

    def __gen(self, packet: DhcpPacket) -> Generator[DhcpPacket, DhcpPacket, DhcpPacket]:
        self.transactionId = packet.transactionId
        self.clientHardwareAddr = packet.clientHardwareAddr

        if packet.messageType is MessageType.DISCOVER:
            self.transactionType = TransactionType.RENEW
            packet = yield DhcpPacket.fromArgs(
                OpCode.REPLY,
                self.transactionId,
                packet.secondsElapsed,
                packet.clientIp,
                self.yourIp,
                0, # TODO: figure out what to do with serverIp (nothing?)
                packet.clientHardwareAddr,
                MessageType.OFFER,
                self.leaseTime)

            if packet.messageType is MessageType.REQUEST:
                return DhcpPacket.fromArgs(
                    OpCode.REPLY,
                    self.transactionId,
                    packet.secondsElapsed,
                    packet.clientIp,
                    self.yourIp,
                    0, # TODO: server ip? see todo above
                    packet.clientHardwareAddr,
                    MessageType.ACK,
                    self.leaseTime)
            else:
                raise ValueError(f'Expected DHCP REQUEST. Got {packet.messageType.name}.')

        else:
            raise ValueError('Unsuported transaction')

    # recieve a packet from client
    # returns a DhcpPacket to respond with or None to conclude the transaction
    def recv(self, packet: DhcpPacket) -> Tuple[bool, Optional[DhcpPacket]]:
        try:
            if self.__transaction is None:
                self.__transaction = self.__gen(packet)
                return (True, next(self.__transaction))
            else:
                return (True, self.__transaction.send(packet))
        except StopIteration as ex:
            return (False, ex.value)
